"""AFPK v4 transparent synthetic-case model, no predictions of CPA outcomes.
All monetary amounts are 10,000 KRW; dates are (year, month).
"""
import numpy as np
from collections import OrderedDict
from datetime import date

INITIAL_CASH=1400.0
SECURITY_DEPOSIT=1000.0
ICL_BALANCE=1600.0
LIVING=120.0
PARTTIME=80.0
REGULAR_START=230.0
CPA_START=290.0
DISCOUNT=0.05
# Fictional fixed voluntary ICL repayment: 20 per month from Jan 2029; never an asserted legal obligation.
ICL_VOLUNTARY=20.0
P_BASE=0.60
Q_BASE=0.70
DELTA_BASE=0.10

MONTHS=[(2026+(11+i)//12, (11+i)%12+1) for i in range(60)]

def fam(ym):
    return 60.0 if ym<=(2027,2) else (30.0 if ym<=(2027,8) else 0.0)

def exam(ym, plan):
    if plan=='C': return 0.0
    return 20.0 if ym<=(2027,6) else (5.0 if ym<=(2027,9) else 0.0)

def min_cash(ym):
    return 420.0 if ym<=(2027,6) else (375.0 if ym<=(2027,9) else 360.0)

def wage(start, amount, ym, annual=0.03):
    if ym<start: return 0.0
    n=(ym[0]-start[0])*12+(ym[1]-start[1]); return round(amount * ((1+annual)**(n//12)), 6)

def income(plan, outcome, ym, job_delay=0, cpa_wage=CPA_START, regular_wage=REGULAR_START):
    # Outcome P=pass & secured; U=pass unassigned; F=fail.
    if plan=='C':
        return wage((2027,4+job_delay),regular_wage,ym)
    if plan=='A':
        if outcome=='P': return wage((2028,1+job_delay),cpa_wage,ym,0.05)
        if outcome=='F': return wage((2028,2+job_delay),regular_wage,ym)
        return wage((2028,6+job_delay),regular_wage,ym)
    if plan=='B':
        # first part-time paycheck Feb 2027, preceded by Dec-Jan search.
        if outcome=='P' and ym>=(2028,1+job_delay):return wage((2028,1+job_delay),cpa_wage,ym,0.05)
        if outcome=='F' and ym>=(2028,2+job_delay):return wage((2028,2+job_delay),regular_wage,ym)
        if outcome=='U' and ym>=(2028,4+job_delay):return wage((2028,4+job_delay),regular_wage,ym)
        return PARTTIME if ym>=(2027,2) else 0.0
    if plan=='D':
        # leads: apply in May, first part-time paycheck Aug; job search Nov, first salary Feb.
        if outcome=='P' and ym>=(2028,1+job_delay):return wage((2028,1+job_delay),cpa_wage,ym,0.05)
        if outcome in ['U','F'] and ym>=(2028,2+job_delay):return wage((2028,2+job_delay),regular_wage,ym)
        return PARTTIME if ym>=(2027,8) else 0.0
    raise ValueError(plan)

def simulate(plan, outcome, job_delay=0,cpa_wage=CPA_START, regular_wage=REGULAR_START):
    cash=INITIAL_CASH
    rows=[]
    for i,ym in enumerate(MONTHS):
        inflow=income(plan,outcome,ym,job_delay=job_delay,cpa_wage=cpa_wage,regular_wage=regular_wage)
        f=fam(ym); x=exam(ym,plan)
        debt_cash = ICL_VOLUNTARY if ym >= (2029,1) else 0.0
        net=inflow+f-LIVING-x-debt_cash
        cash+=net
        rows.append({'ym':ym,'month_index':i+1,'income':inflow,'family':f,'living':LIVING,'exam':x,
                     'debt_cash':debt_cash,'net':net,'raw_cash':cash,'cash_floor':max(0,cash),'unfunded':max(0,-cash),'cmin':min_cash(ym),'ok':cash>=min_cash(ym)})
    return rows

def pv(rows, r=DISCOUNT):
    rm=(1+r)**(1/12)-1
    return sum(row['net']/(1+rm)**(row['month_index']) for row in rows) + INITIAL_CASH

def metrics(plan,outcome,**kwargs):
    rows=simulate(plan,outcome,**kwargs)
    first=next((row['ym'] for row in rows[:18] if not row['ok']), None)
    return {'c18':round(rows[17]['raw_cash'],1), 'min18':round(min(r['raw_cash']-r['cmin'] for r in rows[:18]),1),
            'first_violation':first, 'pv60':round(pv(rows),1), 'c60':round(rows[-1]['raw_cash'],1), 'rows':rows}

def expected_pv(plan,p=P_BASE,q=Q_BASE,delta=DELTA_BASE,**kwargs):
    if plan=='C': return metrics('C','F',**kwargs)['pv60']
    if plan=='B':p=max(0,p-delta)
    return (p*q*metrics(plan,'P',**kwargs)['pv60']+
            p*(1-q)*metrics(plan,'U',**kwargs)['pv60']+
            (1-p)*metrics(plan,'F',**kwargs)['pv60'])

def expectation_break_even(p=.6,q=.7):
    """Find delta where expected PV(B, delta) = expected PV(D, 0), if possible."""
    vP=metrics('B','P')['pv60'];vU=metrics('B','U')['pv60'];vF=metrics('B','F')['pv60']
    diff=q*vP+(1-q)*vU-vF
    D=expected_pv('D',p=p,q=q)
    if not diff:return None
    return p-(D-vF)/diff

if __name__=='__main__':
    for plan in 'ABCD':
        print(plan, 'PV=',round(expected_pv(plan),1), 'all outcomes:')
        for s in 'PUF':
            a=metrics(plan,s)
            print('  ',s,'C18',a['c18'],'C60',a['c60'],'PV',a['pv60'],'violation',a['first_violation'])
    print('break-even δ(B vs D)=', expectation_break_even())
    for d in [0,.05,.1,.15]:
        print('delta',d,'B PV',expected_pv('B',delta=d))
    for q in [.5,.7,.9]:
        print('q',q,'D PV',expected_pv('D',q=q),'B PV',expected_pv('B',q=q))
