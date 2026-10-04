"""Nadir Ali / IBKR — premium 30-second mascot explainer, 1080p60."""
from pathlib import Path
import sys, math, json, subprocess
import numpy as np
import skia

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
W,H,FPS=1920,1080,60
INK='#10191C'; PAPER='#F1F4ED'; GREEN='#51E7A0'; MUTED='#92A6A0'; LINE='#2B3A3D'; PANEL='#172529'; CYAN='#83CEED'
base=skia.Typeface.MakeFromFile(str(ROOT/'fonts/Inter.ttf'))
args=skia.FontArguments()
coords=skia.FontArguments.VariationPosition.Coordinates([skia.FontArguments.VariationPosition.Coordinate(int.from_bytes(b'wght','big'),780)])
args.setVariationDesignPosition(skia.FontArguments.VariationPosition(coords))
bold=base.makeClone(args)
mono=skia.Typeface.MakeFromFile(str(ROOT/'fonts/Mono.ttf'))
fonts={}
def font(sz,weight='regular'):
    key=(sz,weight)
    if key not in fonts: fonts[key]=skia.Font({'regular':base,'bold':bold,'mono':mono}[weight],sz)
    return fonts[key]
def paint(col,a=1,stroke=0):
    col=col.lstrip('#'); r,g,b=[int(col[i:i+2],16) for i in (0,2,4)]
    p=skia.Paint(AntiAlias=True,Color=skia.Color(r,g,b,int(255*max(0,min(1,a)))))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke); p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p
def rect(c,x,y,w,h,color,r=0,a=1,stroke=0):
    c.drawRoundRect(skia.Rect.MakeXYWH(x,y,w,h),r,r,paint(color,a,stroke))
def text(c,s,x,y,sz=30,col=PAPER,weight='regular',a=1,align='left'):
    f=font(sz,weight); tw=f.measureText(s)
    if align=='center': x-=tw/2
    if align=='right': x-=tw
    c.drawString(s,x,y,f,paint(col,a)); return tw
def line(c,x1,y1,x2,y2,col,a=1,width=2): c.drawLine(x1,y1,x2,y2,paint(col,a,width))
def circle(c,x,y,r,col,a=1,stroke=0): c.drawCircle(x,y,r,paint(col,a,stroke))
def clamp(v): return max(0,min(1,v))
def ease(v): return 1-(1-clamp(v))**4
def reveal(t,delay=0,duration=0.7): return ease((t-delay)/duration)
def headline(c,s,x,y,sz,t,col=PAPER,delay=0):
    a=reveal(t,delay); text(c,s,x,y+35*(1-a),sz,col,'bold',a)
def tag(c,label,x,y,col=GREEN,dark=True):
    width=font(22,'mono').measureText(label)+36
    rect(c,x,y,width,43,col,21,0.10 if dark else 0.22)
    text(c,label,x+18,y+29,22,col,'mono')
def logo(c,x=100,y=89,col=PAPER):
    circle(c,x+15,y-13,15,GREEN if col==PAPER else INK)
    line(c,x+8,y-14,x+14,y-8,INK if col==PAPER else GREEN,1,3)
    line(c,x+14,y-8,x+23,y-20,INK if col==PAPER else GREEN,1,3)
    text(c,'NADIR ALI',x+44,y,30,col,'bold')
def check(c,x,y,col=GREEN,s=1):
    line(c,x-10*s,y,x-2*s,y+8*s,col,1,3*s); line(c,x-2*s,y+8*s,x+14*s,y-11*s,col,1,3*s)
def arrow(c,x,y,col=GREEN):
    line(c,x-22,y,x+22,y,col,1,3); line(c,x+9,y-12,x+22,y,col,1,3); line(c,x+9,y+12,x+22,y,col,1,3)

rng=np.random.default_rng(14)
prices=100+np.cumsum(rng.normal(.10,1.0,55))
def chart(c,x,y,w,h,t,light=False,levels=False):
    grid='#D8DFD6' if light else '#293A3E'
    for i in range(5): line(c,x,y+i*h/4,x+w,y+i*h/4,grid,.65,1)
    for i in range(9): line(c,x+i*w/8,y,x+i*w/8,y+h,grid,.5,1)
    n=max(2,min(len(prices),int(2+reveal(t,0,2.5)*(len(prices)-2))))
    def yy(v): return y+h*.88-(v-prices.min())/(prices.max()-prices.min())*h*.72
    step=w/(len(prices)+1)
    for i in range(n):
        a=prices[i-1] if i else prices[0]-0.7; b=prices[i]
        col='#21A972' if light else GREEN
        if b<a: col='#91A19A' if light else '#718885'
        xx=x+(i+1)*step; y1,y2=yy(a),yy(b)
        line(c,xx,min(y1,y2)-h*.023,xx,max(y1,y2)+h*.023,col,.8,2)
        rect(c,xx-step*.28,min(y1,y2),step*.56,max(3,abs(y2-y1)),col,1)
    if levels:
        for frac,label,col in [(0.23,'TAKE PROFIT',GREEN),(0.56,'ENTRY',CYAN),(0.83,'STOP LOSS','#EAA49B')]:
            yy_=y+h*frac
            p=paint(col,.8,2); p.setPathEffect(skia.DashPathEffect.Make([8,8],0))
            c.drawLine(x,yy_,x+w,yy_,p)
            rect(c,x+w-175,yy_-17,175,34,PANEL,5)
            text(c,label,x+w-163,yy_+7,18,col,'mono')

def bg(c,t,light=False):
    c.clear(skia.ColorSetRGB(241,244,237) if light else skia.ColorSetRGB(16,25,28))
    if not light:
        p=paint(GREEN); p.setShader(skia.GradientShader.MakeRadial(skia.Point(1500,430),850,[skia.Color(42,111,84,55),skia.Color(16,25,28,0)]))
        c.drawRect(skia.Rect.MakeWH(W,H),p)
    # Editorial edge markers, subtle depth, and a restrained moving field.
    for i in range(15):
        x=980+i*67; y=180+math.sin(t*.6+i*.4)*22
        circle(c,x,y,1.5,'#A2B8AA' if light else '#517068',.35)
    line(c,100,119,1820,119,'#CBD5C9' if light else LINE,.7,1)

def chrome(c,idx,light=False):
    col=INK if light else PAPER
    logo(c,col=col)
    text(c,'IBKR AUTOMATION',1820,85,23,'#52635C' if light else MUTED,'mono',align='right')
    text(c,f'0{idx+1} / 06',100,1008,18,'#66776E' if light else MUTED,'mono')
    for i in range(6): rect(c,1610+i*35,998,25,4,GREEN if not light else '#20A673',2,1 if i<=idx else .20)

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

SCENE_FUNCS=[scene0,scene1,scene2,scene3,scene4,scene5]
BOUNDS=[0,4,9,15,20,25,30]
CAPTIONS=[
    [(0.32,3.6,'Still placing every trade by hand?')],
    [(4.32,6.7,'I’m Nadir Ali. I build custom bots'),(6.7,8.8,'for Interactive Brokers.')],
    [(9.32,12.1,'Turn your strategy, or TradingView alerts,'),(12.1,14.8,'into automated orders.')],
    [(15.32,17.8,'With position sizing, stop losses,'),(17.8,19.8,'and trade monitoring built in.')],
    [(20.32,22.7,'Paper tested. Your source code.'),(22.7,24.8,'Setup and support.')],
    [(25.32,27.1,'Ready to automate?'),(27.1,29.9,'Message Nadir Ali on Fiverr.')]
]
if (OUT/'captions.json').exists():
    synced=json.load(open(OUT/'captions.json'))
    CAPTIONS=[[(v['start'],v['end'],v['text']) for v in synced if BOUNDS[i]<=v['start']<BOUNDS[i+1]] for i in range(6)]
def frame(t):
    s=skia.Surface(W,H); c=s.getCanvas()
    idx=min(5,next((i for i in range(6) if BOUNDS[i]<=t<BOUNDS[i+1]),5))
    u=t-BOUNDS[idx]
    c.save()
    push=1+.010*clamp(u/(BOUNDS[idx+1]-BOUNDS[idx]))
    c.translate(W/2,H/2); c.scale(push,push); c.translate(-W/2,-H/2)
    SCENE_FUNCS[idx](c,u)
    c.restore()
    for a,b,caption in CAPTIONS[idx]:
        if a<=t<b:
            f=font(29); tw=f.measureText(caption)
            rect(c,(W-tw)/2-26,936,tw+52,57,INK,12,.90)
            text(c,caption,W/2,975,29,PAPER,align='center')
    # A fast diagonal ink/green wipe covers cuts, preserving readable holds.
    if idx>0 and u<.34:
        p=1-ease(u/.34); x=-300+(W+600)*p
        path=skia.Path(); path.moveTo(-500,0); path.lineTo(x+280,0); path.lineTo(x,H); path.lineTo(-500,H); path.close()
        c.drawPath(path,paint(GREEN if idx!=5 else INK))
    return s.makeImageSnapshot()

def stills():
    from PIL import Image,ImageOps,ImageDraw
    times=[2.7,7.3,13.2,18.3,23.6,28.5]
    thumbs=[]
    for i,t in enumerate(times):
        img=frame(t); path=OUT/f'scene_{i+1}.png'
        img.save(str(path),skia.kPNG)
        pil=Image.open(path).convert('RGB').resize((640,360))
        thumbs.append(pil)
    sheet=Image.new('RGB',(1280,1080),'#10191c')
    for i,pil in enumerate(thumbs): sheet.paste(pil,((i%2)*640,(i//2)*360))
    sheet.save(OUT/'storyboard.jpg',quality=95)
    cover=skia.Surface(W,H)
    scene1(cover.getCanvas(),3.3)
    text(cover.getCanvas(),'CUSTOM STRATEGIES / EXECUTION / RISK CONTROLS',100,934,23,GREEN,'mono')
    cover.makeImageSnapshot().save(str(OUT/'thumbnail.png'),skia.kPNG)
    print('Stills ready',flush=True)

def render(part=0,parts=1):
    start=int(30*FPS*part/parts); end=int(30*FPS*(part+1)/parts)
    dest=OUT/f'part_{part}.mp4'
    proc=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgba','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','2',str(dest)],stdin=subprocess.PIPE)
    for n in range(start,end):
        img=frame(n/FPS)
        data=img.tobytes()
        proc.stdin.write(data)
        if n%90==0: print(f'Part {part}: frame {n}/{end}',flush=True)
    proc.stdin.close()
    if proc.wait(): raise RuntimeError('Frame encoding failed')

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='stills': stills()
    else: render(int(sys.argv[1]) if len(sys.argv)>1 else 0,int(sys.argv[2]) if len(sys.argv)>2 else 1)
