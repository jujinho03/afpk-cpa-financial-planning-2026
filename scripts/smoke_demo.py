"""Exercise the imported Rust demo's HTTP boundary with AI explicitly disabled.

Run against a loopback server using isolated/in-memory SQLite and no .env keys.
This is an API integration check, not a claim of parity with Python v4.
"""
import argparse
import json
from pathlib import Path
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse


def run(base_url, output=None):
    parsed = urlparse(base_url)
    if parsed.scheme != 'http' or parsed.hostname not in {'127.0.0.1', 'localhost', '::1'}:
        raise ValueError('Smoke checks require a local loopback HTTP server')

    def call(path, body=None):
        request = urllib.request.Request(base_url + '/api' + path,
            data=None if body is None else json.dumps(body).encode(),
            headers={'Content-Type':'application/json'}, method='GET' if body is None else 'POST')
        try:
            with urllib.request.urlopen(request, timeout=30) as r:
                return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            return e.code, json.load(e)

    for attempt in range(60):
        try:
            status, health = call('/health')
            if status == 200: break
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            pass
        if attempt == 59: raise RuntimeError('Local demo server did not become ready within 60 seconds')
        time.sleep(1)

    status, exps = call('/cpa/experiments')
    assert status == 200 and len(exps['experiments']) == 8
    assert exps['ai']['configured'] is False, 'Refusing AI endpoint test: server has an active key'
    status, defaults = call('/cpa/defaults')
    assert status == 200 and defaults['cash0'] == 14_000_000
    assert defaults['shortHorizon'] == 18 and defaults['longHorizon'] == 60
    status, analysis = call('/cpa/analyze', {})
    assert status == 200 and len(analysis['short']) == 4
    previous = {p['strategy']:p for p in analysis['short']}
    assert previous['A']['tau'] == '2027-10'
    status, changed = call('/cpa/analyze', {'living':1_500_000})
    assert status == 200
    assert previous['A']['endCash'] - changed['short'][0]['endCash'] == 300_000 * 18
    status, invalid = call('/cpa/analyze', {'cash0':-5,'pPct':300})
    assert status == 400 and invalid['error']['code'] == 'VALIDATION_ERROR'
    status, unknown = call('/cpa/analyze', {'hack':1})
    assert status == 400
    status, explored = call('/cpa/explore', {})
    assert status == 200 and len(explored['fans']) == 4
    status, checked = call('/cpa/checkin', {'strategy':'D','entries':[{'month':'2027-02','cash':7_000_000}]})
    assert status == 200 and checked['reprojection']['from'] == '2027-03'
    status, answer = call('/cpa/ask', {'questionId':'floor'})
    assert status == 200 and answer['mode'] == 'rule' and answer.get('ai') is None
    status, disabled = call('/cpa/ai/run', {'experimentId':'E1'})
    assert status == 503 and disabled['error']['code'] == 'AI_NOT_CONFIGURED'
    status, records = call('/cpa/runs')
    assert status == 200 and len(records['runs']) == 8
    summary = {
        'profile':'Rust demo expansion; distinct from Python v4',
        'monetary_unit':'KRW', 'external_ai_called':False,
        'imported_output_records':len(records['runs']),
        'checks':['health','defaults','4-strategy analysis','expense response','invalid inputs',
                  'unknown fields','sensitivity','checkin reprojection','rule answer',
                  'missing AI key returns503','imported records'],
        'defaults':defaults,
        'short':[{k:p.get(k) for k in ['strategy','tau','insolvent','minCash','endCash']} for p in analysis['short']],
        'long':analysis['long'],
    }
    if output:
        Path(output).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'PASS: {len(summary["checks"])} HTTP contract groups; 4 strategies; 8 imported records; external AI calls: 0.')
    print('Rust demo and Python v4 are separate profiles, not an equality check.')
    return summary


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',default='http://127.0.0.1:8080')
    parser.add_argument('--output')
    args=parser.parse_args()
    run(args.base_url,args.output)
