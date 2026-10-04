"""Compositions assembled into render.py; all marks are official source assets."""
ASSETS={name:skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(ROOT/'assets'/filename))) for name,filename in [('mascot','mascot.png'),('presenter','mascot_presenter.png'),('ibkr','ibkr.png'),('tradingview','tradingview.png'),('tv_icon','tradingview-icon.png'),('python','python.png')]}
SAMPLE=skia.SamplingOptions(skia.FilterMode.kLinear,skia.MipmapMode.kNone)
def image(c,key,x,y,w,h=None,a=1):
    im=ASSETS[key]; h=h or w*im.height()/im.width()
    c.drawImageRect(im,skia.Rect.MakeXYWH(x,y,w,h),SAMPLE,paint('#FFFFFF',a))
def platform(c,key,x,y,w=280,a=1):
    if key=='python':
        rect(c,x,y,w,72,'#FFFFFF',14,a)
        im=ASSETS[key]; rw=min(w-44,46*im.width()/im.height()); rh=rw*im.height()/im.width()
        image(c,key,x+(w-rw)/2,y+(72-rh)/2,rw,rh,a)
    else:
        rect(c,x,y,w,72,'#1B2B30',14,a)
        im=ASSETS[key]; rw=w-42; rh=rw*im.height()/im.width()
        image(c,key,x+21,y+(72-rh)/2,rw,rh,a)
def mascot(c,x,y,size,t,pose='mascot',a=1,angle=0):
    bob=math.sin(t*2.1)*9
    # Grounding shadow and soft mint halo preserve the character's 3D presence.
    p=paint('#000000',.20*a); p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle,14))
    c.drawOval(skia.Rect.MakeXYWH(x-size*.24,y+size*.44,size*.48,size*.07),p)
    c.save(); c.translate(x,y+bob); c.rotate(angle+1.6*math.sin(t*1.5))
    image(c,pose,-size/2,-size/2,size,size,a)
    c.restore()
def orbit(c,x,y,r,t,light=False):
    col='#22A978' if light else GREEN
    for k in range(3):
        circle(c,x,y,r+k*47,col,.09,1)
        theta=t*.28+k*1.8
        circle(c,x+(r+k*47)*math.cos(theta),y+(r+k*47)*math.sin(theta),4,col,.65)
def glass(c,x,y,w,h):
    rect(c,x+10,y+16,w,h,'#000000',23,.16)
    rect(c,x,y,w,h,PANEL,23,.96)
    rect(c,x,y,w,h,'#587D74',23,.32,1)
    line(c,x+23,y+1,x+w-23,y+1,'#B7E3CF',.20,1)
def ticket(c,x,y,w,title,detail,t,col=GREEN):
    c.save(); c.translate(0,math.sin(t*1.8)*5)
    glass(c,x,y,w,106)
    circle(c,x+30,y+32,5,col)
    text(c,title,x+48,y+39,22,col,'mono')
    text(c,detail,x+24,y+81,28,PAPER,'bold')
    c.restore()

def scene0(c,u):
    bg(c,u); chrome(c,0)
    tag(c,'YOUR STRATEGY DESERVES BETTER',100,205)
    headline(c,'Still trading',100,385,121,u)
    headline(c,'by hand?',100,527,121,u,GREEN,.16)
    text(c,'Turn your rules into an automated system.',107,624,32,MUTED,a=reveal(u,.55))
    a=reveal(u,.7)
    rect(c,105,705,210,63,'#263338',31,a)
    text(c,'MANUAL',210,746,23,MUTED,'mono',a,align='center')
    arrow(c,359,737,GREEN)
    rect(c,405,705,265,63,GREEN,31,.13*a)
    text(c,'AUTOMATED',537,746,23,GREEN,'mono',a,align='center')
    orbit(c,1460,523,252,u)
    # A real chart thumbnail anchors the mascot in the trading context.
    glass(c,1148,384,593,299)
    chart(c,1177,434,535,198,u)
    ticket(c,1000,190,365,'SIGNAL DETECTED','Rules matched.',u)
    mascot(c,1460,563,730,u,a=reveal(u,.10))
    ticket(c,1450,764,360,'LESS SCREEN TIME','More control.',u+2)
    text(c,'CUSTOM IBKR TRADING BOTS',105,859,23,MUTED,'mono',a=reveal(u,1))

def scene1(c,u):
    bg(c,u); chrome(c,1)
    tag(c,"I’M NADIR ALI",100,205)
    headline(c,'Custom IBKR',100,385,110,u)
    headline(c,'trading bots.',100,515,110,u,GREEN,.18)
    text(c,'Built around your strategy.',105,603,36,MUTED,a=reveal(u,.5))
    platform(c,'python',105,679,240,reveal(u,.6))
    tag(c,'TWS API + IB GATEWAY',375,693)
    orbit(c,1465,545,240,u)
    glass(c,1120,219,625,486)
    platform(c,'ibkr',1180,257,505)
    text(c,'CUSTOM EXECUTION ENGINE',1170,415,23,GREEN,'mono',a=reveal(u,.55))
    for k,label in enumerate(['STRATEGY LOGIC','RISK CHECKS','ORDER TRACKING']):
        yy=466+k*58; aa=reveal(u,.8+k*.23)
        circle(c,1188,yy-9,13,GREEN,.12*aa); check(c,1188,yy-11,GREEN,.48)
        text(c,label,1220,yy,20,MUTED,'mono',aa)
    mascot(c,1610,652,445,u,pose='presenter',a=reveal(u,.3),angle=-3)
    ticket(c,1080,764,414,'CONNECTED TO YOUR BROKER','Your strategy. Your account.',u)

def scene2(c,u):
    bg(c,u); chrome(c,2)
    headline(c,'A signal. A system. An order.',100,268,77,u)
    text(c,'Your strategy becomes a connected workflow.',105,334,31,MUTED,a=reveal(u,.3))
    data=[(100,'01','YOUR SIGNAL','TradingView alerts','Or your own strategy'),(708,'02','YOUR CUSTOM BOT','Validate + size','Apply your risk rules'),(1316,'03','IBKR EXECUTION','Send the order','Monitor its status')]
    for i,(x,num,title,l1,l2) in enumerate(data):
        aa=reveal(u,.2+i*.22); yy=422+30*(1-aa)
        glass(c,x,yy,505,352)
        text(c,num,x+30,yy+50,20,GREEN,'mono',aa)
        text(c,title,x+30,yy+105,29,PAPER,'bold',aa)
        if i==0: platform(c,'tradingview',x+30,yy+137,330,aa)
        elif i==1: platform(c,'python',x+30,yy+137,280,aa)
        else: platform(c,'ibkr',x+30,yy+137,390,aa)
        text(c,l1,x+30,yy+264,28,PAPER,'bold',aa)
        text(c,l2,x+30,yy+309,24,MUTED,a=aa)
    for i,x in enumerate([656,1264]):
        arrow(c,x,599)
        phase=(u*.7-i*.3)%1
        circle(c,x-35+70*phase,599,6,GREEN,reveal(u,.6+i*.35))
    # Character follows a moving signal packet underneath the three nodes.
    progress=reveal(u,.8,4.2)
    line(c,220,838,1650,838,GREEN,.12,2)
    for k in range(12):
        xx=220+k*130; circle(c,xx,838,3,GREEN,.22)
    mascot(c,230+1420*progress,835,160,u,pose='presenter',angle=-7)
    text(c,'ILLUSTRATIVE WORKFLOW',100,910,16,MUTED,'mono')

def scene3(c,u):
    bg(c,u,True); chrome(c,3,True)
    tag(c,'YOUR RULES. BUILT IN.',100,205,INK,False)
    headline(c,'Control every',100,367,99,u,INK)
    headline(c,'step of the trade.',100,483,90,u,INK,.18)
    for i,label in enumerate(['Position sizing','Stop-loss logic','Trade monitoring']):
        aa=reveal(u,.5+i*.28); yy=610+i*74
        circle(c,120,yy-10,20,'#D0E8D9',aa); check(c,120,yy-12,'#16774B',.7)
        text(c,label,161,yy,34,INK,'bold',aa)
    glass(c,1000,210,790,526)
    text(c,'RISK & EXECUTION',1035,267,23,PAPER,'mono')
    tag(c,'PAPER MODE',1552,239)
    chart(c,1035,315,710,343,u,False,True)
    for k,(label,value) in enumerate([('SIZE','RULE BASED'),('STOP','CONFIGURED'),('STATUS','MONITORED')]):
        x=1025+k*260
        rect(c,x,773,240,99,'#DDE8DD',17)
        text(c,label,x+20,806,17,'#567263','mono')
        text(c,value,x+20,848,20,INK,'bold',reveal(u,.9+k*.2))
    mascot(c,868,709,270,u,pose='presenter',a=reveal(u,.5))
    text(c,'ILLUSTRATIVE INTERFACE',1770,911,16,'#687A6C','mono',align='right')

def scene4(c,u):
    bg(c,u); chrome(c,4)
    tag(c,'FROM BUILD TO HANDOVER',100,205)
    headline(c,'Built for you.',100,361,106,u)
    data=[('Paper tested.','Validate before going live.'),('Full source code.','Own the system I build.'),('Setup + support.','Get help getting started.')]
    for i,(title,desc) in enumerate(data):
        aa=reveal(u,.30+i*.35); x=100+30*(1-aa); y=430+i*141
        glass(c,x,y,1054,118)
        circle(c,x+51,y+59,23,GREEN,.14*aa); check(c,x+51,y+57,GREEN,.95)
        text(c,title,x+105,y+50,37,PAPER,'bold',aa)
        text(c,desc,x+105,y+92,25,MUTED,a=aa)
        text(c,f'0{i+1}',x+1015,y+68,23,GREEN,'mono',aa,align='right')
    orbit(c,1509,553,229,u)
    mascot(c,1509,584,630,u,pose='presenter',a=reveal(u,.1))
    text(c,'CLEAR PROCESS. COMPLETE HANDOVER.',100,906,22,MUTED,'mono',a=reveal(u,1.5))

def scene5(c,u):
    c.clear(skia.ColorSetRGB(81,231,160)); chrome(c,5,True)
    orbit(c,1518,535,254,u,True)
    headline(c,'Your rules.',100,363,126,u,INK)
    headline(c,'Automated.',100,509,126,u,INK,.16)
    text(c,'Let’s build your IBKR trading bot.',107,603,36,INK,a=reveal(u,.45))
    aa=reveal(u,.6)
    rect(c,104,675,830,103,INK,51,aa)
    text(c,'Message Nadir Ali on Fiverr',149,739,37,PAPER,'bold',aa)
    arrow(c,870,726,PAPER)
    text(c,'Send your strategy. I’ll take it from there.',109,840,28,'#205942',a=reveal(u,1.0))
    mascot(c,1518,552,726,u,a=reveal(u,.15),angle=3)
    rect(c,1276,840,484,66,INK,33,.95*reveal(u,.8))
    text(c,'NADIR ALI  /  BOT DEVELOPER',1518,883,21,GREEN,'mono',align='center',a=reveal(u,.8))
