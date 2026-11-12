"""Create judge-facing AFPK v4 PDF from the supplied v2/v3 briefs and transparent hypothetical model.
All simulated values are synthetic case assumptions, not verified personal estimates.
"""
import os, sys, math, io
sys.path.insert(0,os.path.dirname(__file__))
from model_v4 import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUT='/mnt/data/AFPK_CPA_최종_아이디어_기획서_v4_2차피드백반영.pdf'
FOLDER='/mnt/data/afpk_v4'
FREG='/usr/share/fonts/truetype/nanum/NanumSquareR.ttf'; FBOLD='/usr/share/fonts/truetype/nanum/NanumSquareB.ttf'
pdfmetrics.registerFont(TTFont('NS',FREG));pdfmetrics.registerFont(TTFont('NSB',FBOLD));pdfmetrics.registerFontFamily('NS',normal='NS',bold='NSB',italic='NS',boldItalic='NSB')
W,H=A4
M=45;RIGHT=W-M;CW=W-2*M
NAVY=HexColor('#142137'); INK=HexColor('#202932'); GRAY=HexColor('#65717E'); RULE=HexColor('#D8DFE6');
BLUE=HexColor('#316496'); LBLUE=HexColor('#EAF0F6'); SOFT=HexColor('#F4F6F8'); WHITE=HexColor('#FFFFFF');
TEAL=HexColor('#317F73'); LGREEN=HexColor('#EDF5F1'); AMBER=HexColor('#AF782F'); LAMBER=HexColor('#FCF5E7'); RED=HexColor('#B3514E'); LRED=HexColor('#FBEEEE')

styles={}
def S(size=9,bold=False,lead=None,color=INK,align=TA_LEFT):
    key=(size,bold,lead,str(color),align)
    if key not in styles:
        styles[key]=ParagraphStyle('X'+str(len(styles)),fontName='NSB' if bold else 'NS',fontSize=size,leading=lead or size*1.45,alignment=align,textColor=color,spaceAfter=0,allowWidows=0,allowOrphans=0,splitLongWords=0)
    return styles[key]
def P(c,html,x,y,w,size=9,bold=False,lead=None,color=INK,align=TA_LEFT):
    p=Paragraph(str(html),S(size,bold,lead,color,align));_,h=p.wrap(w,1200);p.drawOn(c,x,H-y-h);return y+h

def T(c,t,x,y,size=9,col=INK,bold=False):
    c.setFillColor(col);c.setFont('NSB' if bold else 'NS',size);c.drawString(x,H-y-size,t)
def TR(c,t,x,y,size=9,col=INK,bold=False):
    c.setFillColor(col);c.setFont('NSB' if bold else 'NS',size);c.drawRightString(x,H-y-size,t)
def L(c,x1,y1,x2,y2,color=RULE,sw=.8,dash=None):
    c.setStrokeColor(color);c.setLineWidth(sw);c.setDash(dash or []);c.line(x1,H-y1,x2,H-y2);c.setDash([])
def R(c,x,y,w,h,color=SOFT,r=0,border=None):
    c.setFillColor(color);c.setStrokeColor(border if border else color); c.roundRect(x,H-y-h,w,h,r,stroke=1 if border else 0,fill=1)

def chip(c,label,x,y,bg=LBLUE,col=BLUE,size=7.7):
    w=pdfmetrics.stringWidth(label,'NSB',size)+15
    R(c,x,y,w,17,bg,7);T(c,label,x+7.5,y+3.1,size,col,True);return w

def banner(c,headline,desc,y,h=77,accent=BLUE,bg=LBLUE):
    R(c,M,y,CW,h,bg,5);R(c,M,y,4,h,accent)
    T(c,headline,M+14,y+10,10.7,accent,True)
    P(c,desc,M+14,y+31,CW-30,9.0,lead=13.7)
    return y+h

def block(c,title,body,x,y,w,h,bg=SOFT,accent=None):
    R(c,x,y,w,h,bg,5)
    if accent:R(c,x,y,3,h,accent)
    T(c,title,x+12,y+9,10,NAVY,True)
    P(c,body,x+12,y+29,w-24,8.5,lead=12.7)
    return y+h

def table(c,heads,rows,x,y,widths,fs=8.2,pad=7,head_h=30,rowmin=31,raw=False):
    assert abs(sum(widths)-CW)<1, (sum(widths),CW)
    R(c,x,y,CW,head_h,NAVY)
    xx=x
    for j,h in enumerate(heads):P(c,h,xx+pad,y+8,widths[j]-pad*2,8.2,True,11,WHITE);xx+=widths[j]
    y+=head_h
    for i,row in enumerate(rows):
        pars=[Paragraph(str(v),S(fs,False,fs*1.46)) for v in row]
        heights=[p.wrap(widths[j]-pad*2,1000)[1] for j,p in enumerate(pars)]
        rh=max(rowmin,max(heights)+pad*2)
        R(c,x,y,CW,rh,SOFT if i%2==0 else WHITE)
        xx=x
        for j,p in enumerate(pars):p.drawOn(c,xx+pad,H-y-(rh-heights[j])/2-heights[j]);xx+=widths[j]
        y+=rh
    L(c,x,y,x+CW,y)
    return y

def section(c,t,y):
    T(c,t,M,y,11.4,NAVY,True);L(c,M,y+20,RIGHT,y+20);return y+30

def hpage(c,n,code,action,sub,score=''):
    R(c,0,0,W,H,WHITE)
    T(c,'AFPK 2026   /   STRATEGIC FINANCIAL PLANNING',M,24,7.1,GRAY,True)
    TR(c,code.upper(),RIGHT,24,7.1,GRAY,True);L(c,M,42,RIGHT,42)
    T(c,f'{n-1:02d} / {code.upper()}',M,62,8.3,BLUE,True)
    # Action title must occupy one line; avoid subtitle collisions on long Korean headings.
    fs=19.0
    while pdfmetrics.stringWidth(action,'NSB',fs)>CW and fs>12.4:
        fs-=0.3
    T(c,action,M,89,fs,NAVY,True)
    P(c,sub,M,122,CW,8.8,False,13.6,GRAY)
    L(c,M,155,RIGHT,155)
    if score:TR(c,'평가 연결: '+score,RIGHT,161,7.8,BLUE,True)
    return 176 if score else 167

def fpage(c,n,total=17):
    L(c,M,788,RIGHT,788)
    T(c,'합격해도 끝나지 않는다  |  B안 가상 고객 · 정량 예시  |  2026.11.11 · 개정 v4',M,803,7,GRAY)
    TR(c,f'{n:02d} / {total:02d}',RIGHT,803,7.5,GRAY,True)
    c.showPage()

def sim_18(path):
    cash=1400.0; rows=[]
    for ym in MONTHS[:18]:
        fa=fam(ym)
        ex=exam(ym, "C" if path=="C" else "A")
        salary=0.0
        if path=="B" and ym >= (2027,2): salary=80.0
        if path=="C" and ym >= (2027,4): salary=230.0
        if path.startswith("D") and ym >= (2027,8): salary=80.0
        if path=="D_ok" and ym >= (2028,2): salary=230.0
        cash+=fa+salary-120.0-ex
        rows.append((ym,round(cash,2),min_cash(ym),salary))
    return rows

c=canvas.Canvas(OUT,pagesize=A4,pageCompression=1)
c.setTitle('합격해도 끝나지 않는다 | AFPK CPA 유예생 재무설계 v4')
c.setAuthor('AFPK 영 플래너 챌린지 2026 · 가상 고객 사례 기획')

# PAGE 1 - Cover
R(c,0,0,W,H,WHITE);R(c,0,0,12,H,NAVY)
T(c,'AFPK  YOUNG PLANNER CHALLENGE 2026',M+10,68,9,BLUE,True)
T(c,'FINANCIAL PLANNING / IDEA PROPOSAL',M+10,88,8.2,GRAY,True)
L(c,M+10,124,RIGHT-2,124,NAVY,1.4)
P(c,'합격해도<br/>끝나지 않는다',M+10,163,CW-24,34,True,43,NAVY)
P(c,'CPA 2차 유예생의 합격·취업 지연 위험과<br/>18개월 지급능력을 연결한 AI 조건부 재무설계',M+12,289,CW-35,15,False,24,INK)
R(c,M+10,392,CW-15,133,SOFT,7)
T(c,'THE QUESTION',M+25,414,9,BLUE,True)
P(c,'시험에 합격해도 첫 급여가 늦어지는 청년.<br/>고객의 현금은 <b>어느 시점까지</b> 필수 지출을 감당할 수 있으며,<br/><b>언제 근로·취업 전략을 변경해야 하는가?</b>',M+25,441,CW-50,14.2,False,23,NAVY)
T(c,'재무설계 60점',M+12,579,10,NAVY,True);T(c,'AI 활용·비판적 검증 40점',M+165,579,10,NAVY,True)
L(c,M+12,607,RIGHT-2,607)
P(c,'본 문서는 공모전 참가작 제출 전의 설득형 기획서이며, 계산된 금액은 <b>B안 가상 고객과 명시적 가정</b>에 따른 예시다. 실제 분석으로 확인되지 않은 개인 합격확률과 채용확률은 예측하지 않는다.',M+12,635,CW-22,9,lead=14,color=GRAY)
T(c,'CONCEPT REVIEW  /  v4',M+12,752,9.5,BLUE,True)
TR(c,'2026.11.11',RIGHT-2,753,9,GRAY)
c.showPage()

# PAGE 2 - executive
n=2;y=hpage(c,n,'decision summary','우리가 권하는 것은 ‘전업 포기’가 아니라 지급능력을 지키는 선택이다','첫 급여가 늦어져도 생활을 유지할 수 있는 계획을 만들고, 성과가 불확실한 선택은 조건별로 비교한다.','주제·목표 10 / 해법 20 / 전달 10')
y=section(c,'핵심 결론: 계산 가능한 것과 아직 모르는 것을 분리한다',y)
y=banner(c,'가상 기준에서 순수 재무가치 1위는 C, 마지막 응시권을 유지하는 대안은 B','가상 조건(p=0.60, q=0.70, 근로 병행에 따른 p 감소 10%p)에서 60개월 현금흐름 현가: C 6,717만 원 > B 6,062만 원 > D 5,854만 원. 이는 검증된 급여·확률로 얻은 현실 예측이 아니다.',y,87)
y+=21
# 3 cards
cardw=(CW-16)/3
for i,(t,desc,col) in enumerate([
 ('C / 재무가치 1위','즉시 구직 → 2027년 4월 첫 급여. 조기 소득이 가치 우위를 만든다.',LBLUE),
 ('B / 유예기회 보존','2027년 2월 첫 시간제 급여를 가정. 현금은 안전하지만 학습시간 감소를 평가해야 한다.',LGREEN),
 ('D / 전환 옵션','시험 후 시간제 근로 → 2028년 2월 취업을 가정. 채용 지연 시 안전하지 않다.',SOFT)]):
    block(c,t,desc,M+i*(cardw+8),y,cardw,115,col)
y+=139
y=section(c,'심사위원에게 미리 알려야 하는 세 가지 판단 원칙',y)
y=table(c,['판단 순서','뜻','이 기획의 대응'],[
 ('① 필수 지급','월세·생활비·법정 채무를 적기에 지급할 수 있는가','18개월 현금흐름과 최초 위반월'),
 ('② 안전성','월별 필수비용 3개월분의 여유를 유지하는가','수험기 420만 원 / 시험 이후 375·360만 원'),
 ('③ 선택권','고객이 마지막 응시 기회를 중시하는 경우 손실을 어디까지 감내할 것인가','B와 C의 재무가치 차이·민감도 설명')],M,y,[105,185,CW-290],fs=8.3,rowmin=46)
y+=17
P(c,'<b>오해 금지</b> — CPA 합격률은 고객 개인 확률이 아니며, 수습 등록률도 개인 취업확률이 아니다. 기대가치 계산은 시나리오 탐색용이다.',M,y,CW,9,color=GRAY)
fpage(c,n)

# PAGE 3 - customers & no jargon
n=3;y=hpage(c,n,'problem first','이 고객의 문제는 시험보다 다음 달 현금이 먼저 줄어든다는 것이다','CPA 시험을 몰라도 이해할 수 있도록 “고객의 경제적 문제 → 원인 → 해야 할 행동”으로 설명한다.','주제·목표 10 / 전달 10')
y=section(c,'고객의 한 문장',y)
y=banner(c,'“붙어도 월세는 누가 내지?”','27세 가상 고객은 정기 급여가 없고 가족의 생활비 지원도 점차 종료된다. 시험에 합격하더라도 첫 급여를 받는 시점은 확정되지 않는다.',y,83)
y+=24
y=section(c,'이 사례에서 실제로 발생하는 두 번의 현금 공백',y)
steps=[('현재~시험 전','급여 없음','생활비 + 수험비 지출'),('시험 후~결과 발표','지원금 축소·종료','필수 지출 계속'),('합격 이후','수습처·첫 급여 지연 가능','재무계획 재설정')]
for i,(a,b,d) in enumerate(steps):
    xx=M+i*(CW/3)
    R(c,xx+2,y,(CW/3)-8,98,SOFT if i!=2 else LBLUE,5)
    T(c,f'{i+1:02d}',xx+13,y+9,10,BLUE,True)
    T(c,a,xx+13,y+28,9.6,NAVY,True)
    P(c,b+'<br/>'+d,xx+13,y+51,CW/3-30,8.2,lead=12)
    if i<2:T(c,'→',xx+CW/3-6,y+34,17,BLUE,True)
y+=127
y=section(c,'이 고객에게 재무설계가 해 줄 수 있는 일',y)
y=table(c,['일반적인 질문','재무설계가 답할 질문'],[
 ('시험을 계속할까?','필수 지출을 지키며 선택권을 유지할 수 있는 기간이 얼마인가?'),
 ('합격하면 얼마 벌까?','합격 후 수습·구직 지연을 견딜 유동성이 충분한가?'),
 ('돈이 부족하면 아르바이트할까?','지원 시작·채용·첫 지급까지 걸리는 시간을 반영했을 때 언제 행동해야 하나?')],M,y,[168,CW-168],fs=8.6,rowmin=53)
y+=18
P(c,'<b>본 사례의 범위:</b> 자산·부채·현금흐름·비상자금·실행·모니터링. 시험 합격 예측, 개인 진로 코칭, 실제 금융상품의 확정 추천은 범위 밖이다.',M,y,CW,9,lead=14,color=GRAY)
fpage(c,n)

# PAGE 4 - CPA primer and facts
n=4;y=hpage(c,n,'context in one page','CPA 제도는 두 문장으로 충분하다: 시험 기회가 제한되고 첫 급여는 불확실하다','시험제도 설명은 최소화하고 재무적 영향을 먼저 이해하도록 배치했다.','주제·목표 10 / 진단 20')
y=section(c,'복잡한 용어 대신 재무문제를 만든 두 개의 사건',y)
block(c,'① 유예: 한 번 남은 응시 기회','전년도 1차 합격 자격으로 다음 해 2차를 응시하는 상황이다. 고객은 2026년 1차 합격, 2027년에 마지막 유예 응시를 앞두었다(가상 고객 설정).',M,y,(CW-12)/2,118,SOFT,BLUE)
block(c,'② 수습: 합격과 취업 사이의 구간','최종 합격이 즉시 급여를 확정하지는 않는다. 수습기관 등록·채용·첫 지급일은 각각 확인해야 한다. 수습처 미지정이 곧 무소득을 뜻하지도 않는다.',M+(CW+12)/2,y,(CW-12)/2,118,LBLUE,BLUE)
y+=140
y=section(c,'근거로 사용할 2026년 공식 통계',y)
# display key figures
for i,(big,lab,sub) in enumerate([
 ('26.3%','제2차 전체 합격률','1,150 / 4,368명'),('61.0%','유예생 집단 합격률','959 / 1,572명'),('83.4%','합격자 중 유예생 비중','959 / 1,150명')]):
    xx=M+i*(CW/3)
    R(c,xx+2,y,CW/3-8,105,SOFT,5)
    T(c,big,xx+12,y+10,24,NAVY,True)
    T(c,lab,xx+12,y+48,8.7,INK,True)
    T(c,sub,xx+12,y+68,8.0,GRAY)
y+=127
y=banner(c,'공식 정책은 수습 지연을 “가능한 위험”으로 보여준다','금융위원회는 2026년 5월 29일 수습 안정화 방안을 발표했다. 한시적 배정지원은 장기 미지정자(예: 합격 후 2년 이상)를 원칙적 우선 대상으로 하며, 모든 합격자가 즉시 배정된다는 뜻은 아니다. [S2]',y,93,TEAL,LGREEN)
y+=16
P(c,'<b>수치 해석:</b> 61.0%는 집단의 관찰 합격률이며 특정 고객의 확률 p가 아니다. 특정 날짜의 미등록 비중을 수습확보확률 q나 영구 실업률로도 사용하지 않는다. [S1, S2]',M,y,CW,8.7,lead=13,color=GRAY)
fpage(c,n)

# PAGE 5 - Financial baseline
n=5;y=hpage(c,n,'client & financial goals','재무설계는 고객의 1,400만 원과 월별 지급의무에서 출발한다','원본 v2/v3의 가상 고객 기준값을 유지하되 지출·안전자금·소득발생 시점의 가정을 명확하게 세분화했다.','주제·목표 10 / 진단 20')
y=section(c,'김유예(가명) · 27세 · 서울 원룸 거주 / B안 가상 고객',y)
y=table(c,['재무상태','가상 기준값','적용 원칙'],[
 ('현금성 예금','1,400만 원','월별 지출을 충당할 수 있는 유동성'),
 ('주거보증금','1,000만 원','주거자산으로 관리, 생활비 가용현금에서 제외'),
 ('학자금대출(ICL)','잔액 1,600만 원','당장 월정액 원리금으로 처리하지 않음. 실제 의무상환 시점·금액 확인'),
 ('필수 생활비','월 120만 원','월세 50만 원 포함'),
 ('수험비','월 20만 원(2027.6까지) / 이후 3개월 월 5만 원 / 그 후 0','추가 수험·행정비용 종료 시점을 명시'),
 ('가족 지원','60만 원(2027.2까지) → 30만 원(2027.8까지) → 이후 0','지원 감소는 고객 합의에 따른 가정')],M,y,[138,166,CW-304],fs=8.2,rowmin=36)
y+=19
y=section(c,'최소 안전자금은 필수 수험비까지 포함해 시점별로 설정',y)
for i,(v,label,detail) in enumerate([('420만','시험 전 ~ 2027.06','(생활 120 + 수험 20) × 3'),('375만','시험 후 2027.07~09','(생활 120 + 경과비 5) × 3'),('360만','2027.10 이후','생활 120 × 3')]):
    xx=M+i*(CW/3)
    R(c,xx+2,y,CW/3-8,84,SOFT if i!=0 else LBLUE,5)
    T(c,v,xx+11,y+8,18,NAVY,True)
    T(c,label,xx+11,y+36,8.2,BLUE,True)
    T(c,detail,xx+11,y+55,7.7,GRAY)
y+=105
P(c,'<b>초기 순자산(단순 표시):</b> 현금 1,400 + 보증금 1,000 − 학자금잔액 1,600 = <b>800만 원</b>. 이는 예금·보증금의 법적 제한과 학자금 이자·세금 등은 별도 검증해야 하는 가상 스냅샷이다.',M,y,CW,8.7,lead=14)
fpage(c,n)

# PAGE 6 - options, time lags
n=6;y=hpage(c,n,'strategies on equal footing','네 전략 모두 채용까지의 대기시간을 반영해야 비교가 공정하다','단지 취업을 “결정”한 날이 아니라 실제 첫 급여가 들어오는 월을 기준으로 모델링했다.','진단 20 / 해법 20')
y=section(c,'같은 초기 자금 · 같은 필수 지출 · 서로 다른 소득경로',y)
y=table(c,['경로','행동','첫 근로소득 가정','남는 위험'],[
 ('A 전업','시험 준비에 집중, 2027.09 결과 확인','CPA 수습 취업 시 2028.01부터 등 / 실패 시 별도 구직','2027.10 이미 안전자금 위반 가능'),
 ('B 근로 병행','2026.12~2027.01 구직 후 수험+근로','2027.02부터 월 80만 원','공부시간 감소로 합격 조건 p 악화 가능'),
 ('C 취업 전환','2026.12~2027.03 구직·급여 지연','2027.04부터 월 230만 원','최종 유예 기회 포기, 채용 보장 없음'),
 ('D 조건부 전환','2027.05부터 시험 후 근로 탐색, 2027.11부터 정규직 구직','2027.08 월 80만 → 2028.02 월 230만(취업 성공 가정)','채용 실패·지연이면 안전자금 위반')],M,y,[94,186,125,CW-405],fs=8.1,rowmin=60)
y+=23
y=section(c,'D는 자동 취업 규칙이 아니다 — 선행 준비를 행동으로 적는다',y)
steps=[('05월','시간제 근로 탐색','7월 시험 이후 시작하도록 사전 접촉'),('08월','시간제 첫 급여','근로시간·지급일 확인 후 현금흐름 반영'),('11월','정규직 구직','예상 3개월 후 첫 급여까지 브리지 자금 확보'),('02월','취업 성공/실패 분기','성공할 때만 월 230만 원 유입')]
for i,(mo,t,d) in enumerate(steps):
    xx=M+i*(CW/4)
    block(c,mo+' / '+t,d,xx+2,y,CW/4-7,119,SOFT if i!=3 else LBLUE)
y+=142
P(c,'<b>실행 타당성 필터:</b> 시간제 근로·취업은 지원과 선정이 필요하다. 이 문서의 급여·채용월은 확인된 구인공고가 아닌 가상 조건이므로, 실제 상담에서는 지원처·근로시간·첫 지급일 증빙 전까지 확정 유입으로 계산하지 않는다.',M,y,CW,8.8,lead=13.8,color=GRAY)
fpage(c,n)

# PAGE 7 - chart 18 months
n=7;y=hpage(c,n,'18 month affordability','소득이 늦어지는 순간 A는 먼저 무너지고, D는 취업 성공 여부로 갈린다','동일한 가상 기준값으로 2026.12~2028.05의 월말 잔액을 재계산했다. 음수는 현금이 아니라 미충당액이다.','진단 20 / 전달 10')
plotx,ploty,pw,ph=M+29,218,CW-52,299
# chart grid and legend
keys=[('A','A / 무소득 스트레스',NAVY),('B','B / 80만 원 근로 지속',BLUE),('C','C / 2027.04 취업',TEAL),('D','D / 2028.02 취업 성공',AMBER),('D_fail','D / 취업 지연',RED)]
for i,(key,label,col) in enumerate(keys):
    xx=M+5+(i%3)*165; yy=174+(i//3)*20
    R(c,xx,yy+8,16,3,col);T(c,label,xx+22,yy+2,7.5,INK)
vals={k:sim_18(k) for k in ['A','B','C','D_ok','D_fail']}
K={'A':'A','B':'B','C':'C','D':'D_ok','D_fail':'D_fail'}
maxv=3000
XP=lambda j:plotx+j/17*pw
YP=lambda val:ploty+ph*(1-max(0,min(maxv,val))/maxv)
for v in [0,360,1000,2000,3000]:
    yy=YP(v);L(c,plotx,yy,plotx+pw,yy,RULE,.6);TR(c,str(v),plotx-7,yy-5,7,GRAY)
# cmin line time varying
p=c.beginPath()
for j,ym in enumerate(MONTHS[:18]):
    xy=XP(j),H-YP(min_cash(ym));(p.moveTo if j==0 else p.lineTo)(*xy)
c.setStrokeColor(TEAL);c.setLineWidth(1.1);c.setDash(4,3);c.drawPath(p);c.setDash()
for k,name,col in keys:
    rr=vals[K[k]]
    p=c.beginPath()
    for j,row in enumerate(rr):
        xy=XP(j),H-YP(row[1]);(p.moveTo if j==0 else p.lineTo)(*xy)
    c.setStrokeColor(col);c.setLineWidth(1.85 if k in ['A','B','D'] else 1.5)
    if k=='D_fail':c.setDash(3,3)
    c.drawPath(p);c.setDash()
for j in [0,3,6,9,12,15,17]:
    ym=MONTHS[j];T(c,f'{str(ym[0])[2:]}.{ym[1]:02}',XP(j)-11,ploty+ph+9,7.0,GRAY)
T(c,'점선: 시점별 최소 안전자금',M+34,ploty+ph+30,8.1,TEAL,True)
y=ploty+ph+58
res=[]
for plan,label in [('A','A / 무소득 스트레스'),('B','B / 시간제 근로'),('C','C / 즉시 취업'),('D_ok','D / 채용 성공'),('D_fail','D / 채용 지연')]:
    rr=vals[plan];first=next((f'{ym[0]}.{ym[1]:02}' for ym,v,cm,_ in rr if v<cm),'위반 없음')
    end=rr[-1][1];tag=(f'미충당 {abs(end):,.0f}' if end<0 else f'{end:,.0f}')
    res.append([label,first,tag])
y=table(c,['18개월 고정 시나리오','최초 안전자금 위반','2028.05 말 가용현금 (만원)'],res,M,y,[181,134,CW-315],fs=8.2,pad=7,rowmin=28)
y+=13
P(c,'<b>해석:</b> C·B는 가정된 채용·급여가 실제 발생할 때에만 유동성 요건을 충족한다. D의 정상 경로는 안전하지만, 2028.02 첫 급여가 지연되면 2028.03에 하한을 위반한다. A의 2028.05 미충당액은 555만 원이다.',M,y,CW,8.5,lead=12.8)
fpage(c,n)

# PAGE 8 - outcome based comparison
n=8;y=hpage(c,n,'outcome by strategy','합격 이후에도 세 갈래 소득 경로를 같은 기준으로 검사한다','합격·수습처 확보 여부에 따라 2028년 이후 실제 소득 시작일을 달리 설정하고 18개월 제약 통과 여부를 재계산한다.','진단 20 / 해법 20')
y=section(c,'2027년 결과를 세 상태로 분리 (확률은 사실이 아닌 조건변수)',y)
for i,(name,body,bg) in enumerate([('P / 합격·수습 확보','2028.01 첫 급여 월 290만 원 가정',LGREEN),('U / 합격·수습 미확보','비CPA 대체근로/취업경로를 전략마다 별도로 적용',LBLUE),('F / 불합격','유예 종료 후 구직·취업경로 반영',SOFT)]):
    block(c,name,body,M+i*(CW/3),y,(CW/3)-7,90,bg)
y+=112
y=section(c,'18개월 말 자금 (만원) / 각 상태에서 최초 하한 위반 여부',y)
rows=[]
for plan in 'ABCD':
    row=[plan]
    for outcome in 'PUF':
        met=metrics(plan,outcome)
        row.append(f"{met['c18']:,.0f} / "+('위반' if met['first_violation'] else '통과'))
    rows.append(row)
y=table(c,['전략','P / 합격·확보','U / 합격·미확보','F / 불합격'],rows,M,y,[70,143,143,CW-356],fs=8.35,rowmin=45)
y+=23
y=banner(c,'A의 18개월 말 잔액이 회복되더라도 실행 가능한 전략은 아니다','A는 P 경로에서 18개월 말 잔액이 양(+)이더라도 2027.10에 최소 안전자금을 먼저 위반한다. 미래 급여가 과거의 지급불능을 자동으로 해결하지는 않는다.',y,82,AMBER,LAMBER)
y+=25
y=section(c,'금융 의사결정으로 다시 해석',y)
P(c,'<b>① A</b>는 합격 여부와 관계없이 ‘첫 급여 전의 브리지 자금’이 부족해 부적격하다. <b>② B</b>는 가정된 시간제 소득만 발생하면 18개월 제약을 통과하지만 공부시간 감소를 추가 검증해야 한다. <b>③ C</b>는 조기 취업이 성립할 경우 현금흐름이 가장 안정적이다. <b>④ D</b>는 조기 구직과 첫 급여 일정이 지켜질 때만 통과하며, 취업 지연이 가장 중요한 실패조건이다.',M,y,CW,9.3,lead=15)
fpage(c,n)

# PAGE 9 - 60 month values
n=9;y=hpage(c,n,'60 month financial value','장기 가치까지 계산하면 기본 가정에서는 C가 앞서고, B·D는 조건부 대안이다','60개월(2026.12~2031.11) 동일 기간의 할인 현금흐름을 가상 급여·취업 시점으로 직접 산출했다.','진단 20 / 해법 20')
y=section(c,'60개월 비교에 공통 적용한 핵심 가정',y)
P(c,'월 실수령(가상): 일반 근로 <b>230만 원</b>, CPA 수습취업 <b>290만 원</b>. 일반 근로는 연 3%, CPA 경로는 연 5% 증가. 연 할인율 5%. 2029.01부터 모든 경로에 <b>월 20만 원의 가상 자발적 학자금 상환</b>을 동일 적용. 실제 임금·ICL 법정 의무상환액이 아니다.',M,y,CW,8.7,lead=13.3)
y+=73
# chart horizontal bars
records=[('C / 즉시 취업',expected_pv('C'),TEAL),('B / 병행 (Δp=10%p)',expected_pv('B'),BLUE),('D / 조건부 전환',expected_pv('D'),AMBER),('A / 전업',expected_pv('A'),GRAY)]
startx=M+154;barsw=CW-176
for i,(label,value,col) in enumerate(records):
    yy=y+i*54
    T(c,label,M,yy+10,8.9,INK,True)
    R(c,startx,yy+6,barsw,18,SOFT,3)
    R(c,startx,yy+6,barsw*value/7000,18,col,3)
    TR(c,f'{value:,.0f}만',RIGHT,yy+32,8.5,col,True)
y+=242
P(c,'<b>조건변수:</b> p=0.60(전업 시 합격 조건), q=0.70(합격 후 특정 시점까지 수습확보 조건), 병행시 p 감소 10%p. 숫자는 개인 확률이 아니라 <b>모형 비교를 위한 예시 입력값</b>이다.',M,y,CW,8.5,lead=13.0,color=GRAY)
y+=62
y=banner(c,'기본 재무판정: C가 1위다. 다만 고객이 마지막 유예의 선택권을 중요하게 생각할 수 있다','C는 수험 기회 포기라는 비금전적·비가역적 비용이 있다. B는 18개월 제약을 통과하며 마지막 응시권을 유지하지만, 기본 60개월 현금흐름 현재가치는 C보다 약 655만 원 낮다.',y,84,TEAL,LGREEN)
y+=20
y=section(c,'장기 가치 해석의 한계',y)
P(c,'60개월 수치는 동일한 가상 조건에서 계산한 <b>조건부 현금흐름의 현재가치</b>다. CPA 취업·급여, 일반 취업, 소득상승률, p·q 모두 실측·예측값이 아니다. 법정 ICL 상환액·세금·인플레이션·가족 사건을 완전히 모델링한 순자산 예측도 아니므로 확정 수익이라고 설명하지 않는다.',M,y,CW,9.0,lead=14)
fpage(c,n)

# PAGE 10 - sensitivity and flip
n=10;y=hpage(c,n,'sensitivity and decision boundary','B가 유리하다는 결론은 합격조건 하락과 향후 보수에 따라 달라진다','공부시간 감소를 숨기지 않고, B의 합격조건 감소 Δp가 장기 가치에 주는 영향을 실제 수치로 비교한다.','진단 20 / 해법 20')
y=section(c,'근로 병행의 합격조건 하락을 0~15%p로 가정하면',y)
rows=[]
for d in [0,.05,.10,.15]:
    b=expected_pv('B',delta=d);rows.append([f'{d*100:.0f}%p',f'{b:,.0f}만 원',f'{b-expected_pv("C"):+,.0f}만 원','C 우세' if b<expected_pv('C') else 'B 우세'])
y=table(c,['Δp (병행의 감소폭)','B의 60개월 가치','B - C','재무가치 순위'],rows,M,y,[121,134,121,CW-376],fs=8.4,rowmin=38)
y+=19
P(c,'<b>핵심:</b> 현재 보수(290만 원)와 q=0.70의 가정에서는 병행에 따른 감소폭이 0%p여도 C가 B보다 높은 현금흐름 현재가치를 보인다. “B가 무조건 안전하고 유리하다”는 표현은 금지한다.',M,y,CW,9,lead=14)
y+=66
y=section(c,'최종 권고가 바뀌는 두 가지 조건',y)
R(c,M,y,(CW-12)/2,111,LBLUE,5)
T(c,'전략 B가 C를 앞서는 조건',M+12,y+12,9.7,BLUE,True)
P(c,'기본 p=0.60, q=0.70, Δp=10%p 가정에서 <b>CPA 경로 월 실수령 초임을 약 333만 원 이상</b>으로 높이면 B의 60개월 가치가 C를 넘어선다. 실제 보수 통계가 아니다.',M+12,y+35,(CW-34)/2,8.7,lead=13.5)
xx=M+(CW+12)/2;R(c,xx,y,(CW-12)/2,111,SOFT,5)
T(c,'전략 C의 구직이 더 늦어질 경우',xx+12,y+12,9.7,BLUE,True)
P(c,'C의 첫 급여가 2027.04에서 <b>2027.07로 3개월 지연</b>되는 조건에서는 C의 예시 가치가 5,969만 원으로 떨어져 B 기본값(6,062만 원)을 밑돈다.',xx+12,y+35,(CW-34)/2,8.7,lead=13.5)
y+=136
y=section(c,'왜 “최적 전략 하나”가 아니라 조건부 권고인가',y)
P(c,'현재의 결과는 미래 CPA 보수와 실제 취업시점에 매우 민감하다. 따라서 <b>재무가치 1위 C</b>를 투명하게 알리고, 고객이 CPA 유예기회를 중시한다면 <b>B의 예상 손실(기본 약 655만 원)·유동성 안전성·합격조건 하락 위험</b>을 함께 설명해 합의해야 한다. 확률을 추정하지 못했다는 이유로 숫자의 한계를 숨기지 않는다.',M,y,CW,9.0,lead=14.3)
fpage(c,n)

# PAGE 11 - decision matrix
n=11;y=hpage(c,n,'advisory recommendation','권고안은 C를 기본 비교점으로 제시하고, B를 ‘기회 보존’ 대안으로 제안한다','수치가 보여주는 것과 고객의 가치 판단을 분리해야 책임 있는 재무설계가 된다.','해법 20 / 전달 10')
y=section(c,'고객에게 실제로 제시할 권고 구조',y)
y=table(c,['권고 단계','현재 가상 결과','고객에게 필요한 결정'],[
 ('1 / 지급능력','A: 2027.10 최초 안전자금 위반 → 배제','A를 단독 권고하지 않는다'),
 ('2 / 재무우위','C: 60개월 가치 6,717만 원으로 기준상 1위','취업 경로가 실제 성립할 가능성·시점 확인'),
 ('3 / 선택권','B: 안전자금 통과, C 대비 655만 원 낮은 재무가치','마지막 응시 기회에 대해 고객이 받아들일 비용인가'),
 ('4 / 보완대안','D: 취업이 2028.02 발생할 때 통과 / 실패 시 2028.03 위반','채용·첫 급여 일정 증빙 전에는 안전 확정 금지')],M,y,[120,188,CW-308],fs=8.5,rowmin=57)
y+=25
R(c,M,y,CW,133,LGREEN,5)
T(c,'고객 설명용 최종 권고문 (가정 사례)',M+13,y+12,10.5,TEAL,True)
P(c,'“현재 제시하신 소득·자산 조건에서 <b>순수 재무지표는 즉시 취업(C)이 가장 유리</b>합니다. 다만 회계사 시험의 마지막 응시 기회를 반드시 유지하고 싶으시다면, 매월 실제 첫 급여를 확인한 시간제 근로(B)로 생활비를 확보하면서 준비하는 방안을 검토할 수 있습니다. 그 선택은 기본 비교에서 약 <b>655만 원의 60개월 재무가치 차이</b>와 공부시간 감소 위험을 감수하는 결정입니다. 채용이나 급여 시작이 늦어진다면 계획은 즉시 다시 검토해야 합니다.”',M+13,y+41,CW-27,9.1,lead=14.2)
y+=155
y=section(c,'실행 전에 반드시 확인해야 할 증빙',y)
P(c,'<b>시간제 근로:</b> 실제 채용·시간표·첫 급여일.  <b>취업 전환:</b> 지원·면접·입사 가능시점과 첫 정산일.  <b>학자금:</b> ICL 대출 종류·이자·기발생 의무상환 통지 여부.  <b>고객 합의:</b> CPA 응시권을 유지하기 위한 최대 허용 재무적 손실과 가족지원 종료 조건.',M,y,CW,8.9,lead=14)
fpage(c,n)

# PAGE 12 - monitoring trigger
n=12;y=hpage(c,n,'actionable monitoring','D의 전환 규칙은 고용시장 대기시간을 고려한 ‘사전 발동’이어야 한다','기존 오류: 잔액 720만 원이 된 뒤 바로 급여가 발생한다고 가정. v4는 구직 선행시간과 실패경로를 분리한다.','해법 20 / 진단 20')
y=section(c,'고객이 따를 수 있는 월별 행동 규칙',y)
y=table(c,['시점','점검 기준','선행 행동','검증 결과'],[
 ('2027.05','시험 후 3개월의 현금잔액을 미리 예측','시간제 근로 지원·면접 시작. 8월 첫 급여를 목표로 준비','8월 첫 급여가 없으면 전망을 다시 계산'),
 ('2027.06','전업 A 잔액 720만 원 도달','7월 시험 이후 근로 전환 일정 확정','720은 “급여 보장”이 아니라 위험 신호'),
 ('2027.11','3개월 뒤 전망이 안전자금 360만 원 하회','정규직 구직 시작, 기존 시간제 근로 지속','2028.02 첫 급여 발생 시 18개월 안전'),
 ('2028.01','정규직 채용·2월 지급 여부 미확정','실패 시 현금 부족 위험 고지, 자금·취업 대안 재검토','D 지연 경로는 2028.03 첫 위반')],M,y,[76,151,161,CW-388],fs=8.2,rowmin=63)
y+=22
# timeline snapshot
for i,(datev,amt,meaning) in enumerate([('2027.06','720','시험 종료'),('2027.09','565','가족지원 종료'),('2027.11','485','구직 시작'),('2028.01','405','첫 급여 직전'),('2028.02','515','정규직 첫 급여')]):
    xx=M+i*(CW/5)
    R(c,xx+1,y,CW/5-5,83,SOFT if i!=4 else LGREEN,4)
    T(c,datev,xx+7,y+8,8.2,GRAY,True);T(c,amt,xx+7,y+29,18,NAVY,True)
    P(c,meaning,xx+7,y+56,CW/5-15,7.8)
y+=107
P(c,'<b>실패조건:</b> D가 2028.02에 취업하지 못하고 월 80만 원의 시간제 근로만 유지한다면 2028.03 잔액은 <b>325만 원</b>으로 안전자금 360만 원을 위반한다. 미확정 추가차입·지원금으로 이를 메운 것으로 계산하지 않는다.',M,y,CW,9.0,lead=14)
fpage(c,n)

# PAGE 13 - what AI changes
n=13;y=hpage(c,n,'meaningful ai contribution','AI를 코드 생성기에 그치지 않고 “놓친 가정”을 찾는 감사자로 사용한다','AI 활용 20점의 근거는 사용 사실이 아니라 문제 발견 → 재계산 → 고객 권고 변경이라는 검증 가능한 절차다.','AI 활용 20')
y=section(c,'AI가 담당할 네 가지 역할과 인간의 독립 검증',y)
y=table(c,['기능','AI의 기여','담당자의 확인','결과 증거'],[
 ('정보 누락 점검','고객 진술에서 계약·첫 급여일·지원 종료 등 빠진 변수 제안','실제 가상 고객 가정 승인, 확인 불가 항목 표시','정보 수집 표 전·후'),
 ('경로 생성','합격/미확보/불합격과 구직 지연을 결합한 빠진 시나리오 탐색','현실성·중복 시나리오 제거','누락 시나리오 추가 이력'),
 ('반례 탐색','“B가 유리” 같은 초기 권고를 반박할 조건 탐색','Python으로 p 감소·급여 지연 재계산','권고 반전 근거표'),
 ('고객 설명','복잡한 모형을 쉬운 재무적 행동으로 번역','법령·수치·적합성 최종 승인','원문/수정 문안 비교')],M,y,[100,177,140,CW-417],fs=8.2,rowmin=63)
y+=22
y=section(c,'AI가 실질적으로 바꿔야 할 것',y)
R(c,M,y,(CW-12)/2,133,SOFT,5)
T(c,'AI 최초 주장에 대한 반례 (예시 질문)',M+10,y+9,9.3,NAVY,True)
P(c,'“병행 근로 B는 현금이 많으므로 항상 최선인가?”<br/>→ 공부시간 감소 Δp와 취업 전환 C를 동시에 비교하도록 지시',M+10,y+38,(CW-32)/2,8.8,lead=13)
xx=M+(CW+12)/2;R(c,xx,y,(CW-12)/2,133,LBLUE,5)
T(c,'검증 후 고객 결론',xx+10,y+9,9.3,BLUE,True)
P(c,'기본 가상 조건에서는 C의 현금흐름 가치가 우세. B의 선택은 <b>약 655만 원의 가상 재무가치 차이</b>와 공부시간 위험을 설명한 뒤 고객이 결정.',xx+10,y+38,(CW-32)/2,8.8,lead=13)
y+=158
P(c,'<b>증거의 구분:</b> 본 v4에서 수행한 것은 Python으로 재현 가능한 시나리오 검산과 권고의 조건부 해석이다. 외부 AI 도구 2종×반복 프롬프트 비교 실험은 <b>아직 실행 완료된 결과로 주장하지 않는다</b>. 실제 참가작 부록에는 프롬프트·원출력·검증·수정 이력을 제출해야 한다.',M,y,CW,9,lead=14,color=GRAY)
fpage(c,n)

# PAGE 14 - tests
n=14;y=hpage(c,n,'ai audit protocol','AI 검증 20점은 실제 원출력과 수정 전후의 재무적 차이로 증명한다','예상 오류를 만들어 적는 대신, 같은 프롬프트를 반복 실행하고 공식 문서 및 재현 코드로 판정하도록 실험을 설계했다.','AI 비판적 검증 20')
y=section(c,'6개 검증 실험: 결과가 아니라 검사할 질문',y)
y=table(c,['ID','AI가 틀리기 쉬운 판단','반증 자료·계산','재무적 영향'],[
 ('E1','전체·유예생 집단률을 고객 개인 합격확률로 확정','2026 금융위 유형별 분모','기대가치 변화'),
 ('E2','합격 다음 달부터 수습·급여 자동 발생','금융위 수습 정책, 급여 지연 L','최초 안전자금 위반월'),
 ('E3','유예·부분합격 규정 혼동','해당 연도 공식 시험 시행계획','수험비·응시 계획'),
 ('E4','ICL을 일반 월정액 원리금으로 처리','국세청 귀속연도별 법정 상환 통지','월별 필수지출 왜곡'),
 ('E5','근로 시작일과 첫 급여일을 동일시','실제 구직·급여 지연 가정','D 전략의 경로 반전'),
 ('E6','B의 공부시간 손실 또는 C의 취업 지연을 무시','Python Δp·취업시점 민감도','최종 권고의 변경')],M,y,[45,198,142,CW-385],fs=8.3,rowmin=49)
y+=20
y=section(c,'실험별로 반드시 남길 증거 4단계',y)
for i,(t,d) in enumerate([('입력','도구·모델명, 시점, 프롬프트, 합성 데이터'),('원출력','응답 전문·캡처를 편집 없이 보존'),('독립 판정','원문 조항, Python 코드, 테스트 케이스'),('권고 변경','오류가 실제 고객 행동에 미치는 차이')]):
    xx=M+i*(CW/4)
    block(c,str(i+1)+' / '+t,d,xx+2,y,CW/4-7,112,SOFT if i%2==0 else LBLUE)
y+=135
P(c,'<b>검증 윤리:</b> AI가 오류를 내지 않으면 “오류 없음”으로 기록한다. 출처·시점·프롬프트·실제 출력 없이 오류가 발생했다고 쓰지 않는다. 이 PDF의 가정된 초기 주장은 실험의 질문 예시이지, 외부 모델을 통해 관찰한 오류 결과가 아니다.',M,y,CW,9,lead=14,color=GRAY)
fpage(c,n)

# PAGE 15 - six stages
n=15;y=hpage(c,n,'financial planning six steps','시험 이야기가 아니라 표준 재무설계 6단계로 고객에게 제안한다','분석 결과를 실제 실행과 모니터링으로 연결하여 ‘CPA 진로상담’처럼 보일 위험을 통제한다.','재무설계 60점')
y=table(c,['표준 단계','고객 중심 내용','결과물'],[
 ('1. 관계 정립','고객이 감수할 재무적 위험과 상담 범위를 합의. 합격예측은 제외.','상담 범위·책임'),
 ('2. 정보 수집·목표','현금·보증금·ICL·가족지원·실제 지급일을 구조화.','F1: 재무상태표'),
 ('3. 진단·분석','18개월 Cmin 위반과 60개월 가치를 비교, 고용지연 스트레스 반영.','F2: 잔액 / F3: 가치'),
 ('4. 재무설계 제안','C 재무가치 우위 고지, B 선택권 유지 비용 설명, A 기각, D 실패조건 제시.','F4: 4개 전략 비교'),
 ('5. 실행 지원','근로시간·구직 시작일·첫 급여일·자금조달 증빙 확인.','F5: 월별 실행표'),
 ('6. 모니터링','매월 위험 예측, 소득·수습 상태 변동 즉시 새로 계산.','F6: 조정 규칙')],M,186,[122,286,CW-408],fs=8.5,rowmin=61)
y=635
y=banner(c,'보고서 본문의 중심은 재무분석과 해법이다','개인 합격확률 추정, 학원 정보, 수험 코칭은 분석의 중심이 아니다. 심사위원은 “이 고객의 자산·채무·현금흐름을 어떻게 보호하는가”를 먼저 확인할 수 있어야 한다.',y,96,TEAL,LGREEN)
fpage(c,n)

# PAGE 16 - judging alignment
n=16;y=hpage(c,n,'judge scoring map','공식 100점의 각 항목에 확인 가능한 증거를 직접 대응시켰다','핵심 주장은 표·그래프·고객 행동으로 증명하고, 예정 결과는 완료된 실험처럼 표시하지 않는다.','공식 평가표 100')
y=table(c,['평가항목','배점','심사위원 질문','이 기획이 제공하는 증거'],[
 ('주제·재무목표','10','왜 CPA 수험이 재무설계 문제인가?','생활비·부채·첫 급여 공백과 우선순위 목표 (3~5p)'),
 ('진단·분석','20','가정·수치가 정합적인가?','동일조건 18개월·60개월 경로 및 민감도 (6~10p)'),
 ('해법·실행','20','실제로 실행 가능한가?','채용까지 선행기간, 최종 권고, 실패조건 (11~12p)'),
 ('전달력','10','비전문가도 이해하는가?','용어 최소화, 경제적 갈등 우선, 고객 설명문'),
 ('AI 활용','20','AI가 무엇을 추가로 발견하는가?','누락 시나리오·반례 탐색·고객 문안 (13p)'),
 ('AI 비판적 검증','20','AI 결과의 오류·한계를 검증했나?','E1~E6 실행 후 원출력과 검산·수정 이력 (14p)')],M,y,[109,46,159,CW-314],fs=8.3,rowmin=65)
y+=23
y=section(c,'현 단계의 성과를 과장하지 않는 것이 오히려 전문성이다',y)
P(c,'<b>완료:</b> 가상 고객 기준값 정의, 18개월·60개월 모형 계산, 최소 안전자금 재검토, 근로·채용 지연 경로, B의 합격조건 민감도. <b>추가 확보:</b> 실제 근로·CPA 보수 근거, 원본 AI 실험 결과, 소득연도별 ICL 상환액 및 공식 양식 최종 검증.',M,y,CW,9.0,lead=14)
fpage(c,n)

# PAGE 17 - source + limits
n=17;y=hpage(c,n,'references & assumptions','검증된 사실과 가정된 숫자를 한 페이지에서 명확히 구분한다','수치의 출처·발표 시점·해석 범위를 문서 전체에서 일관되게 유지한다.','출처·재현성')
y=section(c,'핵심 공식 출처',y)
sources=[
 ('[S1]','금융위원회, 2026 제61회 CPA 최종 합격 결과 (2026.09.01)','https://fsc.go.kr/no010101/87628'),
 ('[S2]','금융위원회, CPA 수습 안정화 방안 (2026.05.29 결정, 06.01 공개)','https://fsc.go.kr/no010101/87013'),
 ('[S3]','국세청, 맞춤형 학자금 상환 안내 (2026.04.20; 2025 귀속)','https://www.nts.go.kr/nts/na/ntt/selectNttInfo.do?nttSn=1350361'),
 ('[S4]','한국재무설계협회, AFPK 영 플래너 챌린지 2026 공식 공고','https://www.ifpk.org/?data_usn=181814&mnu_usn=67&mode=view&page_no=1'),
 ('[S5]','택스워치 2026.09.22, 국회예산정책처 「생성형 AI의 노동시장 영향」 보도','https://www.taxwatch.co.kr/article/tax/2026/09/21/0002')
]
for i,(code,lab,url) in enumerate(sources):
    yy=y+i*51
    R(c,M,yy,CW,43,SOFT if i%2==0 else WHITE,4)
    T(c,code,M+9,yy+7,8.7,BLUE,True)
    P(c,lab,M+50,yy+6,CW-58,8.5,lead=12.4)
    c.linkURL(url,(M, H-yy-43, M+CW,H-yy),relative=0,thickness=0)
y+=275
P(c,'<b>S5 해석 주의:</b> 2025년 수습 등록 338/1,200명(10.22 기준)은 특정 시점의 상태이며, 다른 연도 등록률과 직접 비교한 영구 미지정률이 아니다. 국회예산정책처 원보고서의 해당 표·쪽수는 이 PDF에서 직접 독립 검증하지 않았으므로 택스워치 2차 보도라는 사실을 표시했다.',M,y,CW,8.5,lead=13.2,color=GRAY)
y+=73
y=section(c,'가정 및 모델 제외 항목',y)
P(c,'<b>가정값:</b> 1,400만 원 가용현금, 월 생활비 120만 원, 수험비, 가족지원 감소, 시간제 보수 80만 원, 정규직 230만 원, CPA 경로 290만 원, p=0.60·q=0.70, Δp=10%p, 구직·수습 지연. <b>모형 제한:</b> 60개월 값은 가상 세후 소득과 가상 자발적 학자금 상환(2029년부터 월 20만 원)으로 계산한 현금흐름 현가이며, 실제 법정 상환액·물가·금융상품 금리·개인 합격/채용확률을 추정하지 않는다.',M,y,CW,8.5,lead=13.1)
y+=84
P(c,'<b>후속 검증:</b> 은행 이자율·예금금리, 실제 ICL 소득기준 및 미래 상환고지, 2027 시험 일정, 실제 근로계약 보수 범위를 대조한 뒤 가상 고객의 금액·모형을 업데이트해야 한다.',M,y,CW,8.4,lead=13,color=GRAY)
fpage(c,n)

c.save()
print('SAVED',OUT,os.path.getsize(OUT))
