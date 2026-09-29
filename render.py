import skia, numpy as np, subprocess, sys, math, os, re
from tl import *
W,H,FPS=1920,1080,60
FD=os.environ.get('FD','/usr/share/fonts/truetype/')
HF=FD+'higgsfield/Montserrat-ExtraBold.ttf'
if not os.path.exists(HF): HF=FD+'dejavu/DejaVuSans-Bold.ttf'
TF={'h':skia.Typeface.MakeFromFile(HF),'b':skia.Typeface.MakeFromFile(FD+'dejavu/DejaVuSans.ttf'),
'bb':skia.Typeface.MakeFromFile(FD+'dejavu/DejaVuSans-Bold.ttf'),'m':skia.Typeface.MakeFromFile(FD+'dejavu/DejaVuSansMono.ttf'),
'mb':skia.Typeface.MakeFromFile(FD+'dejavu/DejaVuSansMono-Bold.ttf')}
FC={}
def F(k,s):
    s=int(s)
    if (k,s) not in FC: FC[(k,s)]=skia.Font(TF[k],s)
    return FC[(k,s)]
G='#22C55E';WH='#F2F5F3';MU='#8B9A92';RD='#EF4444';PN='#101915';LN='#22352C';DK='#062016'
def P(h,a=1.0,sw=0):
    h=h.lstrip('#'); a=max(0.0,min(1.0,a))
    p=skia.Paint(AntiAlias=True,Color=skia.Color(int(h[0:2],16),int(h[2:4],16),int(h[4:6],16),int(a*255)))
    if sw:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(sw); p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p
def GL(h,a,sw=0,sig=12):
    p=P(h,a,sw); p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle,sig)); return p
def dash(a):
    p=P(MU,a,2); p.setPathEffect(skia.DashPathEffect.Make([10,8],0)); return p
def cl(x): return 0.0 if x<0 else 1.0 if x>1 else x
def eo(x): x=cl(x); return 1-(1-x)**3
def sm(t,a,b): return eo((t-a)/(b-a))
def bo(x):
    x=cl(x); c1=1.70158; c3=c1+1; return 1+c3*(x-1)**3+c1*(x-1)**2
def tx(c,s,x,y,k,sz,col=WH,a=1.0,al='l'):
    f=F(k,sz); w=f.measureText(s)
    if al=='c': x-=w/2
    elif al=='r': x-=w
    c.drawString(s,x,y,f,P(col,a)); return w
def rr(c,l,t,r,b,rad,p): c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(l,t,r,b),rad,rad),p)
def panel(c,l,t,r,b,a=1):
    rr(c,l,t,r,b,18,P(PN,0.92*a)); rr(c,l,t,r,b,18,P(LN,a,2))
CUR=[0.0,0.0]
def head(c,s,x,y,a,sz=64):
    f=F('h',sz); sp=f.measureText(' ')
    for k,wd in enumerate(s.split()):
        g=sm(CUR[0],CUR[1]+0.05+k*0.09,CUR[1]+0.4+k*0.09)
        c.drawString(wd,x,y+(1-g)*22,f,P(WH,a*g)); x+=f.measureText(wd)+sp
def sub(c,s,x,y,a,sz=32): tx(c,s,x,y,'b',sz,MU,a)
def mkbg():
    s=skia.Surface(W,H); c=s.getCanvas(); c.clear(skia.Color(9,14,12))
    gp=P('#16241D',0.8,1)
    for x in range(0,W+1,60): c.drawLine(x,0,x,H,gp)
    for y in range(0,H+1,60): c.drawLine(0,y,W,y,gp)
    p=skia.Paint(AntiAlias=True); p.setShader(skia.GradientShader.MakeRadial(skia.Point(1150,470),950,[skia.Color(34,197,94,42),skia.Color(34,197,94,0)]))
    c.drawRect(skia.Rect.MakeWH(W,H),p)
    p2=skia.Paint(AntiAlias=True); p2.setShader(skia.GradientShader.MakeRadial(skia.Point(W/2,H/2),1250,[skia.Color(0,0,0,0),skia.Color(0,0,0,170)]))
    c.drawRect(skia.Rect.MakeWH(W,H),p2)
    return s.makeImageSnapshot()
BG=mkbg()
try: MO=np.load('mouth.npy')
except Exception: MO=np.zeros(10)
rng=np.random.default_rng(0)
CAND=[];p=100.0
for k in range(16):
    o=p; c_=p+rng.normal(1.1,1.5); h=max(o,c_)+abs(rng.normal(0,0.8)); l=min(o,c_)-abs(rng.normal(0,0.8)); CAND.append((o,h,l,c_)); p=c_
PMIN=min(x[2] for x in CAND); PMAX=max(x[1] for x in CAND)
def CY(v): return 820-(v-PMIN)/(PMAX-PMIN)*430
EQ=np.cumsum(np.random.default_rng(7).normal(0.32,1.0,220)); EQ=(EQ-EQ.min())/(EQ.max()-EQ.min())
A=[(1560,560,1.0),(300,600,0.9),(300,600,0.9),(290,650,0.8),(270,700,0.7),(270,700,0.7),(270,700,0.7),(300,640,0.85),(540,560,1.1)]
def build(c,t,x,y,s):
    g=sm(t,0.2,0.5)*(1-sm(t,2.0,2.5)); bp=sm(t,0.3,1.7)
    if g>0:
        c.drawLine(x-200*s,y,x+200*s,y,dash(0.5*g)); c.drawLine(x,y-230*s,x,y+230*s,dash(0.5*g))
        for yy in (-105,105): c.drawLine(x-200*s,y+yy*s,x+200*s,y+yy*s,dash(0.25*g))
        for ex in (-25,25): c.drawCircle(x+ex*s,y-38*s,26*s,dash(0.6*g))
        c.drawArc(skia.Rect.MakeLTRB(x-160*s,y-160*s,x+160*s,y+160*s),-120,320*bp,False,P(G,0.35*g,2))
        ang=math.radians(-120+320*bp); c.drawLine(x,y,x+160*s*math.cos(ang),y+160*s*math.sin(ang),P(MU,0.5*g,2)); c.drawCircle(x,y,5,P(WH,g))
    pa=skia.Path(); pa.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x-62*s,y-105*s,x+62*s,y+105*s),24*s,24*s))
    pm=skia.PathMeasure(pa,False); L=pm.getLength(); seg=skia.Path(); pm.getSegment(0,L*bp,seg,True)
    c.drawPath(seg,GL(G,0.6*g,8)); c.drawPath(seg,P(G,1,4))
    if g>0:
        q=g*sm(bp,0.05,0.3)
        for hx,hy in ((-62,-105),(62,-105),(62,105),(-62,105)):
            px,py=x+hx*s,y+hy*s
            c.drawLine(px-34*s,py,px+34*s,py,P(G,0.7*q,2)); rr(c,px-6,py-6,px+6,py+6,1,P(WH,q))
            c.drawCircle(px-34*s,py,5,P(G,q)); c.drawCircle(px+34*s,py,5,P(G,q))
    c.drawLine(x,y-105*s,x,y-105*s-60*s*bp,P(G,1,7*s)); c.drawLine(x,y+105*s,x,y+105*s+55*s*bp,P(G,1,7*s))
    return sm(t,1.6,2.1)
def body(c,t,m,x,y,s,i):
    wave=i in (2,NS-1); happy=i in (2,7,NS-1) and not any(ST[j]-0.05<=t<=ST[j]+D[j]+0.1 for j in range(NS)); worried=i==1; lk=-4 if x>W/2 else 4
    c.drawCircle(x,y,150*s,GL(G,0.10,0,40))
    c.drawLine(x,y-165*s,x,y+160*s,P(G,1,7*s))
    al=3.35 if i==0 else 2.25-0.9*m
    c.drawLine(x-60*s,y+25*s,x-60*s+70*s*math.cos(al),y+25*s+70*s*math.sin(al),P(G,1,9*s))
    an=(-1.0+0.4*math.sin(t*9)) if wave else (-0.35+0.08*math.sin(t*3)) if 3<=i<=7 else 0.95
    c.drawLine(x+60*s,y+25*s,x+60*s+60*s*math.cos(an),y+25*s+60*s*math.sin(an),P(G,1,9*s))
    rr(c,x-62*s,y-105*s,x+62*s,y+105*s,24*s,P(G))
    rr(c,x-48*s,y-92*s,x-32*s,y+20*s,8*s,P('#FFFFFF',0.22))
    eh=0.12 if (t%3.7)<0.13 else 1.0
    for ex in (-25,25):
        cx=x+ex*s; cy=y-38*s
        if happy:
            c.drawArc(skia.Rect.MakeLTRB(cx-14*s,cy-10*s,cx+14*s,cy+16*s),200,140,False,P('#FFFFFF',1,6*s)); continue
        c.drawOval(skia.Rect.MakeLTRB(cx-15*s,cy-18*s*eh,cx+15*s,cy+18*s*eh),P('#FFFFFF'))
        if eh>0.5: c.drawCircle(cx+lk*s,cy+3*s,7.5*s,P(DK))
        if worried: c.drawLine(cx-12*s,cy-28*s-(ex>0)*7*s,cx+12*s,cy-28*s-(ex<0)*7*s,P(DK,1,5*s))
    if worried:
        dy=(t*40)%30; c.drawCircle(x+70*s,y-80*s+dy*s,8*s,P('#7DD3FC',0.9))
    mh=(5+32*m)*s; mw=(36-8*m)*s; r=min(mw,mh)/2
    if happy: c.drawArc(skia.Rect.MakeLTRB(x-20*s,y+2*s,x+20*s,y+34*s),20,140,False,P(DK,1,6*s))
    else: rr(c,x-mw/2,y+16*s,x+mw/2,y+16*s+mh,r,P(DK))
def char(c,t,m):
    if t<0.25: return
    i=max(k for k in range(NS) if t>=SS[k])
    if i==0: x,y,s=A[0]
    else:
        g=sm(t,SS[i],SS[i]+0.7); a,b=A[i-1],A[i]; x,y,s=[a[j]+(b[j]-a[j])*g for j in range(3)]
    y+=math.sin(t*2.4)*6*s*sm(t,2.3,2.8)
    if i==0 and t<2.5:
        f=build(c,t,x,y,s)
        if f<=0.01: return
        c.saveLayerAlpha(None,int(f*255)); body(c,t,m,x,y,s,i); c.restore(); return
    body(c,t,m,x,y,s,i)
def s0(c,t):
    for k,(o,h,l,cc) in enumerate(CAND):
        g=sm(t,cand_t(k),cand_t(k)+0.25)
        if g<=0: continue
        x=200+k*64; col=G if cc>=o else RD
        c.drawLine(x,CY(h),x,CY(l),P(col,g,3))
        yo=CY(o); yc=yo+(CY(cc)-yo)*g
        rr(c,x-17,min(yo,yc),x+17,max(yo,yc)+2,4,P(col))
    g=sm(t,2.4,3.2); n=int(16*g)
    if n>1:
        pa=skia.Path(); pa.moveTo(200,CY(CAND[0][3]))
        for k in range(1,n): pa.lineTo(200+k*64,CY(CAND[k][3]))
        c.drawPath(pa,GL('#A7F3C9',0.5,8)); c.drawPath(pa,P('#A7F3C9',0.8,3))
    head(c,"You have a strategy.",140,200,1,70)
    sub(c,"It works when you trade it by hand.",140,258,sm(t,2.6,3.1))
def pf(w): return 600-(80*math.sin(w*.006)+45*math.sin(w*.017+1)+18*math.sin(w*.05))
def s1(c,t):
    u=t-SS[1]; head(c,"Markets never sleep.",520,190,1); sub(c,"You miss entries. Emotions take over.",520,245,1)
    panel(c,520,300,1800,900)
    sc=u*260; pa=skia.Path()
    for j,sx in enumerate(range(540,1781,6)):
        (pa.moveTo if j==0 else pa.lineTo)(sx,pf(sx+sc))
    c.drawPath(pa,GL(G,0.5,10)); c.drawPath(pa,P(G,1,3))
    for k in range(int(sc/380)-1,int((sc+1300)/380)+2):
        wx=k*380+190; sx=wx-sc
        if not 570<sx<1760: continue
        py=pf(wx)
        if sx<1250:
            c.drawCircle(sx,py,9,P(RD)); rr(c,sx-62,py-66,sx+62,py-24,10,P(RD,0.9)); tx(c,"MISSED",sx,py-36,'bb',22,'#FFFFFF',1,'c')
        else:
            c.drawCircle(sx,py,9,P(G)); tx(c,"ENTRY",sx,py-30,'bb',20,G,1,'c')
    cx,cy=1735,200; c.drawCircle(cx,cy,40,P(WH,0.8,4))
    for ang,ln in ((u*7,30),(u*0.6,20)): c.drawLine(cx,cy,cx+ln*math.sin(ang),cy-ln*math.cos(ang),P(WH,0.9,4))
def s2(c,t):
    u=t-SS[2]; cx,cy=1160,430; g=sm(u,0.1,0.9)
    c.drawCircle(cx,cy,175,P(G,0.10*g))
    c.drawArc(skia.Rect.MakeLTRB(cx-150,cy-150,cx+150,cy+150),-90,360*g,False,GL(G,0.7,16,14))
    c.drawArc(skia.Rect.MakeLTRB(cx-150,cy-150,cx+150,cy+150),-90,360*g,False,P(G,1,9))
    for j in range(3):
        q=cl((u-0.9-j*0.18)/1.0)
        if 0<q<1: c.drawCircle(cx,cy,150+q*260,P(G,(1-q)*0.5,3))
    tx(c,"TN",cx,cy+44,'h',128,WH,sm(u,0.5,0.9),'c')
    a=sm(u,0.8,1.3); f=F('h',92); s="TEAM NAK"; sp=14; w=sum(f.measureText(ch) for ch in s)+sp*(len(s)-1); x=cx-w/2
    for ch in s: c.drawString(ch,x,cy+280,f,P(WH,a)); x+=f.measureText(ch)+sp
    tx(c,"Trading strategies  \u2192  automated systems",cx,cy+345,'b',36,MU,sm(u,1.4,1.9),'c')
CARDS=[("MT4 / MT5","Expert Advisors"),("IBKR API","Interactive Brokers bots"),("Crypto Bots","Exchange API automation")]
def s3(c,t):
    head(c,"Built for your platform.",540,215,1)
    for k,(ti,su) in enumerate(CARDS):
        g=sm(t,card_t(k),card_t(k)+0.5)
        if g<=0: continue
        x=540+k*420; y=310+(1-g)*60
        panel(c,x,y,x+380,y+400,g); rr(c,x,y,x+380,y+6,3,P(G,g))
        ix,iy=x+190,y+140
        if k==0:
            for dx,h,col in ((-50,70,G),(0,46,RD),(50,96,G)):
                c.drawLine(ix+dx,iy-h/2-18,ix+dx,iy+h/2+18,P(col,g,3)); rr(c,ix+dx-15,iy-h/2,ix+dx+15,iy+h/2,4,P(col,g))
        elif k==1: tx(c,"</>",ix,iy+26,'mb',84,G,g,'c')
        else:
            for dx in (-44,0,44): c.drawCircle(ix+dx,iy,38,P(PN,g)); c.drawCircle(ix+dx,iy,38,P(G,g,5))
            tx(c,"$",ix+44,iy+14,'bb',40,G,g,'c')
        tx(c,ti,ix,y+280,'h',40,WH,g,'c'); tx(c,su,ix,y+330,'b',24,MU,g,'c')
KW={'def','if','and'}
def colmap(l):
    cols=[WH]*len(l)
    for mm in re.finditer(r"[A-Za-z_][A-Za-z_0-9]*|\d+(\.\d+)?",l):
        w=mm.group(0); col=None
        if w in KW: col=G
        elif w[0].isdigit(): col='#FBBF24'
        elif mm.end()<len(l) and l[mm.end()]=='(': col='#7DD3FC'
        if col: cols[mm.start():mm.end()]=[col]*(mm.end()-mm.start())
    return cols
NL=["RULES","CODE","BACKTEST","BROKER API","LIVE"]
CODE=["def on_bar(bar):","    if rsi(bar, 14) < 30 and bar.close > ema(bar, 200):","        size = risk.position_size(pct=1.0)","        broker.buy(bar.symbol, size, sl=stop, tp=target)"]
CMAP=[colmap(l) for l in CODE]
LOG=[("09:31:02","BUY","SPY","100","FILLED"),("10:47:15","SELL","SPY","100","FILLED"),("11:02:40","BUY","QQQ","50","FILLED")]
def s4(c,t):
    head(c,"From rules to live execution.",520,200,1)
    NX=[620+k*280 for k in range(5)]; NY=320
    for k in range(4):
        c.drawLine(NX[k]+38,NY,NX[k+1]-38,NY,P(LN,1,4)); g=sm(t,node_t(k)+0.2,node_t(k+1))
        if g>0: c.drawLine(NX[k]+38,NY,NX[k]+38+(NX[k+1]-NX[k]-76)*g,NY,GL(G,0.6,8)); c.drawLine(NX[k]+38,NY,NX[k]+38+(NX[k+1]-NX[k]-76)*g,NY,P(G,1,4))
    st=-1
    for k in range(5):
        c.drawCircle(NX[k],NY,34,P(PN)); c.drawCircle(NX[k],NY,34,P(LN,1,3))
        a=cl((t-node_t(k))/0.35)
        if a>0: st=k; c.drawCircle(NX[k],NY,44*bo(a),GL(G,0.45,0,16)); c.drawCircle(NX[k],NY,34*bo(a),P(G))
        tx(c,str(k+1),NX[k],NY+11,'bb',30,DK if a>0.5 else MU,1,'c')
        tx(c,NL[k],NX[k],NY+82,'bb',22,WH if a>0.5 else MU,1,'c')
    panel(c,520,450,1800,920)
    if st<0: return
    u=t-node_t(st); a=sm(u,0,0.3); X=575; Y=530
    if st==0:
        for j,(kw,rest) in enumerate((("IF  ","RSI(14) < 30  AND  close > EMA(200)"),("THEN","BUY  \u00b7  risk 1% of account"),("EXIT","at 2R  or  trailing stop"))):
            b=a*sm(u,j*0.25,j*0.25+0.3); tx(c,kw,X,Y+60+j*90,'mb',38,G,b); tx(c,rest,X+140,Y+60+j*90,'m',38,WH,b)
    elif st==1:
        n=int(u*60)
        for j,l in enumerate(CODE):
            s=l[:max(0,n)]; n-=len(l)
            tx(c,str(j+1),X,Y+40+j*62,'m',28,MU,a); cw=F('m',28).measureText('M'); q=0
            while q<len(s):
                e=q
                while e<len(s) and CMAP[j][e]==CMAP[j][q]: e+=1
                tx(c,s[q:e],X+50+q*cw,Y+40+j*62,'m',28,CMAP[j][q],a); q=e
            if 0<len(s)<len(l) and int(t*4)%2==0: rr(c,X+50+F('m',28).measureText(s)+4,Y+14+j*62,X+50+F('m',28).measureText(s)+20,Y+46+j*62,2,P(G))
    elif st==2:
        tx(c,"Backtest \u00b7 equity curve",X,Y+5,'bb',24,MU,a)
        L,R,T_,B=600,1740,560,880; c.drawLine(L,B,R,B,P(LN,a,2)); c.drawLine(L,T_,L,B,P(LN,a,2))
        n=max(2,int(len(EQ)*sm(u,0,1.6))); pa=skia.Path(); fa=skia.Path(); fa.moveTo(L,B)
        for j in range(n):
            x=L+(R-L)*j/(len(EQ)-1); y=B-10-EQ[j]*(B-T_-30)
            (pa.moveTo if j==0 else pa.lineTo)(x,y); fa.lineTo(x,y)
        fa.lineTo(L+(R-L)*(n-1)/(len(EQ)-1),B); fa.close(); c.drawPath(fa,P(G,0.12*a)); c.drawPath(pa,GL(G,0.5*a,10)); c.drawPath(pa,P(G,a,4))
    elif st==3:
        for j,l in enumerate(("> connecting to broker API ...","> authenticated","> market data stream      OK","> order routing           OK")):
            tx(c,l,X,Y+50+j*70,'m',32,WH if j else MU,a*sm(u,j*0.3,j*0.3+0.2))
        pu=0.6+0.4*math.sin(t*6); c.drawCircle(1560,Y+40,11,P(G,a*pu)); tx(c,"CONNECTED",1585,Y+50,'bb',28,G,a)
    else:
        cols=[X,X+230,X+400,X+580,X+730]
        for j,h in enumerate(("TIME","SIDE","SYMBOL","QTY","STATUS")): tx(c,h,cols[j],Y+20,'bb',24,MU,a)
        for r,row in enumerate(LOG):
            b=a*sm(u,0.2+r*0.4,0.4+r*0.4)
            for j,v in enumerate(row): tx(c,v,cols[j],Y+90+r*80,'m',32,(G if v=="BUY" else RD if v=="SELL" else G if v=="FILLED" else WH),b)
        pu=0.6+0.4*math.sin(t*6); c.drawCircle(1600,Y+10,11,P(G,a*pu)); tx(c,"LIVE",1625,Y+20,'bb',28,G,a)
def s5(c,t):
    u=t-SS[5]; head(c,"Risk management, built in.",520,200,1)
    panel(c,520,290,1120,900)
    for k,(lb,v,fr) in enumerate((("Max daily loss","2%",0.4),("Risk per trade","1%",0.25),("Max open trades","3",0.6))):
        y=380+k*180; tx(c,lb,570,y,'bb',30,WH); tx(c,v,1070,y,'mb',32,G,1,'r')
        rr(c,570,y+40,1070,y+54,7,P(LN)); g=sm(u,0.3+k*0.25,1.2+k*0.25)
        if g>0: rr(c,570,y+40,570+500*fr*g,y+54,7,P(G))
    X0,Y0,X1,Y1=1250,280,1690,925; mx=(X0+X1)/2
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(X0,Y0,X1,Y1),50,50),GL(G,0.18,0,30))
    rr(c,X0,Y0,X1,Y1,50,P('#05080A')); rr(c,X0,Y0,X1,Y1,50,P('#2E4038',1,5)); rr(c,mx-65,Y0+18,mx+65,Y0+46,14,P('#000000'))
    tx(c,"9:41",X0+45,Y0+42,'bb',20,WH); tx(c,"Alerts",X0+40,Y0+110,'h',34,WH)
    for k,(app,col,l1,l2) in enumerate((("Telegram","#2AABEE","BUY  EURUSD  @ 1.0842","SL 1.0820  \u00b7  TP 1.0890"),("Discord","#5865F2","SPY position closed","Take profit reached"))):
        g=sm(t,alert_t(k),alert_t(k)+0.45)
        if g<=0: continue
        x=X0+22; y=Y0+145+k*200-(1-g)*50
        panel(c,x,y,X1-22,y+180,g); c.drawCircle(x+38,y+42,14,P(col,g))
        tx(c,app,x+62,y+51,'bb',24,WH,g); tx(c,"now",X1-45,y+51,'b',20,MU,g,'r')
        tx(c,l1,x+26,y+108,'bb',24,WH,g); tx(c,l2,x+26,y+146,'b',21,MU,g)
FILES=["strategy.py","risk.py","broker_api.py","backtest.py","README.md"]
CHK=["Clean, readable code","Full documentation","Support after delivery"]
def s6(c,t):
    u=t-SS[6]; head(c,"No black box.",520,200,1,76); sub(c,"You own everything we build.",520,258,1)
    panel(c,520,310,1080,880); tx(c,"project/",565,370,'mb',28,MU)
    for k,fn in enumerate(FILES):
        a=sm(u,0.3+k*0.15,0.6+k*0.15); y=430+k*85
        rr(c,570,y-30,598,y+4,4,P(G,a,3)); tx(c,fn,620,y,'m',32,WH,a)
    for k,s in enumerate(CHK):
        y=440+k*160; g=cl((t-check_t(k))/0.4)
        c.drawCircle(1200,y,32,P(LN,1,3))
        if g>0:
            c.drawCircle(1200,y,32*bo(g),P(G)); pa=skia.Path(); pa.moveTo(1186,y); pa.lineTo(1197,y+11); pa.lineTo(1216,y-11); c.drawPath(pa,P(DK,g,6))
        tx(c,s,1260,y+13,'bb',38,WH,0.35+0.65*g)
def star(c,cx,cy,R,p):
    pa=skia.Path()
    for j in range(10):
        rad=R if j%2==0 else R*0.45; an=-math.pi/2+j*math.pi/5
        (pa.moveTo if j==0 else pa.lineTo)(cx+rad*math.cos(an),cy+rad*math.sin(an))
    pa.close(); c.drawPath(pa,p)
def s7(c,t):
    u=t-SS[7]; head(c,"Proven in production.",520,200,1)
    for k in range(2):
        g=sm(u,0.35+k*0.4,0.85+k*0.4)
        if g<=0: continue
        x=540+k*640; y=310+(1-g)*50; cx=x+280
        panel(c,x,y,x+560,y+440,g); rr(c,x,y,x+560,y+6,3,P(G,g))
        v=sm(u,0.4+k*0.4,1.8+k*0.4)
        if k==0:
            tx(c,f"{int(round(300*v))}+",cx,y+230,'h',140,G,g,'c'); tx(c,"solutions delivered",cx,y+330,'b',34,MU,g,'c')
        else:
            tx(c,f"{4.9*v:.1f}",cx,y+210,'h',130,G,g,'c')
            for j in range(5):
                q=sm(u,1.0+j*0.12,1.3+j*0.12); star(c,cx-120+j*60,y+270,24,P(G,g*(0.25+0.75*q)))
            tx(c,"client rating",cx,y+350,'b',34,MU,g,'c')
def s8(c,t):
    u=t-SS[8]; a=sm(u,0.1,0.5)
    c.drawCircle(860,330,40,P(G,a,5)); tx(c,"TN",860,343,'h',34,WH,a,'c')
    head(c,"Send us your strategy.",800,470,sm(u,0.2,0.7),68)
    sub(c,"We'll show you exactly how we'd build it.",800,535,sm(u,0.5,1.0),36)
    g=bo((t-BTN_T)/0.5)
    if g>0.01:
        w=460; cx,cy=800+w/2,640; hw,hh=w/2*g,45*g
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(cx-hw,cy-hh,cx+hw,cy+hh),hh,hh),GL(G,0.55,0,22)); rr(c,cx-hw,cy-hh,cx+hw,cy+hh,hh,P(G))
        lab="Message us today" if os.environ.get('CTA')=='fiverr' else "theteamnak.com"
        tx(c,lab,cx,cy+13,'bb',int(38*g)+1,DK,1,'c')
SC=[s0,s1,s2,s3,s4,s5,s6,s7,s8]
def wrap(s,n):
    out=[];cur=""
    for w in s.split():
        if len(cur)+len(w)+1>n and cur: out.append(cur); cur=w
        else: cur=(cur+" "+w).strip()
    out.append(cur); return out
def subs(c,t):
    for i,s0_ in enumerate(ST):
        e=s0_+D[i]
        if s0_-0.1<=t<=e+0.3:
            a=min(sm(t,s0_-0.1,s0_+0.15),1-sm(t,e+0.05,e+0.3))
            ls=wrap(LINES[i],72); f=F('b',30); mw=max(f.measureText(l) for l in ls)
            y0=1045-(len(ls)-1)*40
            rr(c,960-mw/2-24,y0-38,960+mw/2+24,1045+16,12,P('#000000',0.55*a))
            for j,l in enumerate(ls): tx(c,l,960,y0+j*40,'b',30,WH,a,'c')
def wm(c,t):
    a=sm(t,SS[2]+1.5,SS[2]+2.2)*(1-sm(t,SS[NS-1],SS[NS-1]+0.4))
    if a<=0: return
    c.drawCircle(78,66,24,P(G,a,4)); tx(c,"TN",78,74,'h',20,WH,a,'c'); tx(c,"TEAM NAK",116,75,'h',24,WH,a)
_pr=np.random.default_rng(11); PT=list(zip(_pr.uniform(0,W,70),_pr.uniform(0,H,70),_pr.uniform(8,30,70),_pr.uniform(1.2,3.2,70),_pr.uniform(0,6.28,70)))
def parts(c,t):
    for x0,y0,sp,sz,ph in PT:
        y=(y0-t*sp)%H; x=x0+math.sin(t*0.5+ph)*18
        c.drawCircle(x,y,sz,P(G,0.10+0.18*(0.5+0.5*math.sin(t*2+ph))))
def sweep(c,t):
    for i in range(1,NS):
        u=(t-(SS[i]-0.15))/0.55
        if 0<u<1:
            x=-100+u*(W+200); c.drawRect(skia.Rect.MakeLTRB(x-40,0,x+40,H),GL(G,0.18,0,30)); c.drawRect(skia.Rect.MakeLTRB(x-1.5,0,x+1.5,H),P('#A7F3C9',0.7))
SURF=skia.Surface(W,H)
def frame(fi):
    t=fi/FPS; c=SURF.getCanvas(); c.drawImage(BG,0,0); parts(c,t)
    CUR[0]=t
    for i in range(NS):
        if not (SS[i]-0.01<=t<=SE[i]+0.06): continue
        a=1.0 if i==0 else sm(t,SS[i],SS[i]+0.35)
        CUR[1]=SS[i]+(2.0 if i==0 else 0)
        if i<NS-1: a*=1-sm(t,SE[i]-0.3,SE[i]+0.05)
        if a<=0.002: continue
        c.saveLayerAlpha(None,int(a*255)); z=1+0.035*cl((t-SS[i])/(SE[i]-SS[i])); c.translate(W/2,H/2+(1-a)*18); c.scale(z,z); c.translate(-W/2,-H/2); SC[i](c,t); c.restore()
    sweep(c,t); wm(c,t); char(c,t,float(MO[min(fi,len(MO)-1)])); subs(c,t)
    return SURF
if __name__=='__main__':
    if sys.argv[1]=='still':
        for ts in sys.argv[2:]:
            frame(int(float(ts)*FPS)).makeImageSnapshot().save(f'still_{ts}.png',skia.kPNG)
    else:
        w,n=int(sys.argv[2]),int(sys.argv[3]); NF=int(END*FPS); a,b=NF*w//n,NF*(w+1)//n
        p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgba','-s','1920x1080','-r','60','-i','-','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-g','120',f'seg{w}.mp4'],stdin=subprocess.PIPE)
        for fi in range(a,b): p.stdin.write(frame(fi).makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
        p.stdin.close(); p.wait(); print('seg',w,'done',flush=True)
