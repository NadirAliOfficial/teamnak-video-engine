"""Team NAK / IBKR — 30 second studio motion design, 1080p30."""
from pathlib import Path
import sys, math, json, subprocess
import numpy as np
import skia

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
W,H,FPS=1920,1080,30
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
    text(c,'TEAM NAK',x+44,y,30,col,'bold')
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

def scene0(c,u):
    bg(c,u,True); chrome(c,0,True)
    tag(c,'YOUR STRATEGY. YOUR TIME.',100,205,INK,False)
    headline(c,'Your strategy.',100,380,112,u,INK)
    headline(c,'Still manual?',100,513,112,u,INK,.25)
    text(c,'Let your rules do the work.',105,604,35,'#5D6D64',a=reveal(u,.65))
    a=reveal(u,.15)
    c.save(); c.translate(35*(1-a),0)
    rect(c,1000,228,810,614,'#C4D2C5',24,.35)
    rect(c,984,210,810,614,'#FFFFFF',24,a)
    text(c,'STRATEGY MONITOR',1024,267,24,INK,'mono',a)
    tag(c,'MANUAL',1572,234,'#65736B',False)
    chart(c,1028,335,718,340,u,True)
    line(c,1024,709,1754,709,'#D8DFD6',1,1)
    text(c,'Signal detected',1024,762,27,INK,'bold',reveal(u,1.0))
    text(c,'Waiting for you...',1754,762,23,'#67776C','mono',reveal(u,1.3),align='right')
    px=1470+55*math.sin(u*1.4); py=592+20*math.cos(u)
    path=skia.Path(); path.moveTo(px,py); path.lineTo(px+2,py+48); path.lineTo(px+14,py+34); path.lineTo(px+29,py+31); path.close()
    c.drawPath(path,paint(INK)); c.drawPath(path,paint('#FFFFFF',1,2))
    if u>1.5:
        r=30+(u%1)*30; circle(c,px+7,py+12,r,'#21A972',.3*(1-u%1),2)
    c.restore()

def scene1(c,u):
    bg(c,u); chrome(c,1)
    tag(c,'BUILT FOR YOUR STRATEGY',100,205)
    headline(c,'Custom IBKR',100,385,112,u)
    headline(c,'trading bots.',100,516,112,u,GREEN,.18)
    text(c,'Interactive Brokers automation',104,603,35,MUTED,a=reveal(u,.45))
    for k,label in enumerate(['Python','TWS API','IB Gateway']):
        a=reveal(u,.7+k*.18); tag(c,label,104+k*215,677)
    cx,cy=1440,507
    # Perspective orbital paths around a broker-engine core.
    for j in range(3):
        path=skia.Path()
        for k in range(181):
            theta=k*2*math.pi/180; rx=306; ry=118
            xx=rx*math.cos(theta); yy=ry*math.sin(theta)
            angle=j*math.pi/3+.12*math.sin(u*.4)
            x=cx+xx*math.cos(angle)-yy*math.sin(angle)
            y=cy+xx*math.sin(angle)+yy*math.cos(angle)
            if k==0: path.moveTo(x,y)
            else: path.lineTo(x,y)
        c.drawPath(path,paint(GREEN,.15,2))
        theta=u*.7+j*2; xx=rx*math.cos(theta); yy=ry*math.sin(theta)
        x=cx+xx*math.cos(angle)-yy*math.sin(angle); y=cy+xx*math.sin(angle)+yy*math.cos(angle)
        circle(c,x,y,9,GREEN,.85); circle(c,x,y,19,GREEN,.08)
    a=reveal(u,.2); size=.85+.15*a
    c.save(); c.translate(cx,cy); c.scale(size,size)
    rect(c,-187,-148,380,310,'#040D0F',35,.55)
    rect(c,-200,-165,400,310,PANEL,32)
    rect(c,-200,-165,400,310,GREEN,32,.45,1)
    rect(c,-180,-145,360,270,'#1A3031',24)
    text(c,'IBKR',0,-12,88,PAPER,'bold',align='center')
    text(c,'CUSTOM ENGINE',0,50,22,GREEN,'mono',align='center')
    circle(c,-66,98,5,GREEN); text(c,'CONNECTED',-51,105,19,MUTED,'mono')
    c.restore()
    text(c,'YOUR RULES → YOUR BOT',cx,822,23,MUTED,'mono',align='center',a=reveal(u,1.0))

def scene2(c,u):
    bg(c,u); chrome(c,2)
    headline(c,'From signal to execution.',100,270,86,u)
    text(c,'One connected workflow. Built around your logic.',104,334,32,MUTED,a=reveal(u,.3))
    cards=[(100,'01','YOUR SIGNAL','Strategy rules','TradingView alerts'),(705,'02','YOUR BOT','Validate the signal','Apply risk rules'),(1310,'03','IBKR ORDER','Send the order','Track its status')]
    for i,(x,num,title,l1,l2) in enumerate(cards):
        a=reveal(u,.3+i*.28)
        yy=423+35*(1-a)
        rect(c,x,yy,510,410,PANEL,22,a)
        rect(c,x,yy,510,410,GREEN if i==1 else LINE,22,.55*a,1)
        text(c,num,x+35,yy+62,23,GREEN,'mono',a)
        text(c,title,x+35,yy+130,33,PAPER,'bold',a)
        if i==0:
            points=[(x+40+k*35, yy+215+math.sin(k*.9)*22-k*2) for k in range(12)]
            p=skia.Path(); p.moveTo(*points[0])
            for pt in points[1:]: p.lineTo(*pt)
            c.drawPath(p,paint(CYAN,a,3))
            circle(c,*points[-1],6,CYAN,a)
        elif i==1:
            for k in range(5):
                rect(c,x+40+k*85,yy+215,60,6,GREEN,3,.25+a*.5)
                rect(c,x+40+k*85,yy+239,40+15*math.sin(u+k),4,MUTED,2,.45)
        else:
            rect(c,x+35,yy+184,440,85,'#203934',12,a)
            check(c,x+71,yy+225,GREEN,1.2)
            text(c,'ORDER ACKNOWLEDGED',x+103,yy+233,20,GREEN,'mono',a*reveal(u,2.6))
        text(c,l1,x+35,yy+333,28,PAPER,a=a)
        text(c,l2,x+35,yy+375,25,MUTED,a=a)
    for i,x in enumerate([657,1262]):
        arrow(c,x,627)
        for j in range(3):
            phase=(u*.55-j*.2-i*.35)%1
            circle(c,x-32+phase*64,627,5,GREEN,reveal(u,.8+i*.4)*(1-abs(phase-.5)))
    tag(c,'ILLUSTRATIVE WORKFLOW',100,864,MUTED)

def scene3(c,u):
    bg(c,u,True); chrome(c,3,True)
    tag(c,'CONTROL COMES FIRST',100,205,INK,False)
    headline(c,'Built around',100,367,97,u,INK)
    headline(c,'your risk rules.',100,483,97,u,INK,.18)
    for i,label in enumerate(['Position sizing','Stop-loss logic','Trade monitoring']):
        a=reveal(u,.65+i*.3); yy=608+i*75
        circle(c,120,yy-10,20,'#D0E8D9',a); check(c,120,yy-12,'#16774B',.7)
        text(c,label,161,yy,35,INK,'bold',a)
    rect(c,1004,220,790,630,'#BFCEC3',24,.4)
    rect(c,985,201,790,630,INK,24)
    text(c,'RISK & EXECUTION',1025,258,24,PAPER,'mono')
    tag(c,'PAPER MODE',1545,228)
    chart(c,1025,316,706,330,u,False,True)
    line(c,1025,690,1730,690,LINE,1,1)
    for i,(label,value) in enumerate([('SIZE','RULE BASED'),('STOP','CONFIGURED'),('STATUS','MONITORED')]):
        x=1025+i*240
        text(c,label,x,737,18,MUTED,'mono')
        text(c,value,x,779,22,GREEN,'bold',reveal(u,.8+i*.25))
    text(c,'ILLUSTRATIVE INTERFACE',1750,879,17,'#687A6C','mono',align='right')

def scene4(c,u):
    bg(c,u); chrome(c,4)
    tag(c,'FROM BUILD TO HANDOVER',100,205)
    headline(c,'Built to be yours.',100,361,106,u)
    data=[('01','Paper tested.','Validate before going live.'),('02','Your source code.','Own the system we build.'),('03','Setup + support.','Get help getting started.')]
    for i,(num,title,desc) in enumerate(data):
        x=100+i*584; a=reveal(u,.35+i*.35); y=459+40*(1-a)
        rect(c,x,y,552,362,PANEL,22,a)
        text(c,num,x+34,y+59,23,MUTED,'mono',a)
        circle(c,x+472,y+51,22,GREEN,.13*a); check(c,x+472,y+49,GREEN,.9)
        if i==0:
            for k in range(3):
                line(c,x+38,y+105+k*24,x+48,y+115+k*24,GREEN,a,3)
                line(c,x+48,y+115+k*24,x+66,y+97+k*24,GREEN,a,3)
                rect(c,x+91,y+105+k*24,210-k*35,7,MUTED,3,.35*a)
        elif i==1:
            text(c,'< / >',x+34,y+168,64,GREEN,'mono',a)
        else:
            rect(c,x+35,y+106,96,64,GREEN,16,.12*a)
            for k in range(3): circle(c,x+60+k*22,y+138,4,GREEN,a)
            line(c,x+52,y+170,x+42,y+184,GREEN,a,2)
        text(c,title,x+34,y+250,38,PAPER,'bold',a)
        text(c,desc,x+34,y+306,25,MUTED,a=a)
    text(c,'Custom development. Clear ownership.',100,877,28,MUTED,a=reveal(u,1.5))

def scene5(c,u):
    c.clear(skia.ColorSetRGB(81,231,160)); chrome(c,5,True)
    # Oversized moving brand rings give the final shot its own visual identity.
    for k in range(5): circle(c,1630,520,180+k*80+u*8,INK,.10,2)
    a=reveal(u,.1)
    headline(c,'Your rules.',100,378,138,u,INK)
    headline(c,'Automated.',100,538,138,u,INK,.20)
    text(c,'Custom bots for Interactive Brokers.',109,629,37,INK,a=reveal(u,.5))
    rect(c,105,706,814,106,INK,53,reveal(u,.8))
    text(c,'Message Team NAK on Fiverr',149,773,36,PAPER,'bold',reveal(u,.8))
    arrow(c,856,758,PAPER)
    text(c,'Send your strategy. Let’s build it.',110,868,29,'#205942',a=reveal(u,1.3))
    cx,cy=1515,514
    circle(c,cx,cy,173,INK)
    check(c,cx,cy,GREEN,7)
    text(c,'STRATEGY → SYSTEM',cx,776,23,INK,'mono',align='center',a=a)

SCENE_FUNCS=[scene0,scene1,scene2,scene3,scene4,scene5]
BOUNDS=[0,4,9,15,20,25,30]
CAPTIONS=[
    [(0.32,3.6,'Still placing every trade by hand?')],
    [(4.32,6.7,'Team NAK builds custom trading bots'),(6.7,8.8,'for Interactive Brokers.')],
    [(9.32,12.1,'Turn your strategy, or TradingView alerts,'),(12.1,14.8,'into automated orders.')],
    [(15.32,17.8,'With position sizing, stop losses,'),(17.8,19.8,'and trade monitoring built in.')],
    [(20.32,22.7,'Paper tested. Your source code.'),(22.7,24.8,'Setup and support.')],
    [(25.32,27.1,'Ready to automate?'),(27.1,29.9,'Message Team NAK on Fiverr.')]
]
if (OUT/'captions.json').exists():
    synced=json.load(open(OUT/'captions.json'))
    CAPTIONS=[[(v['start'],v['end'],v['text']) for v in synced if BOUNDS[i]<=v['start']<BOUNDS[i+1]] for i in range(6)]
def frame(t):
    s=skia.Surface(W,H); c=s.getCanvas()
    idx=min(5,next((i for i in range(6) if BOUNDS[i]<=t<BOUNDS[i+1]),5))
    u=t-BOUNDS[idx]
    SCENE_FUNCS[idx](c,u)
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
    text(cover.getCanvas(),'CUSTOM STRATEGIES / EXECUTION / RISK CONTROLS',100,934,26,GREEN,'mono')
    cover.makeImageSnapshot().save(str(OUT/'thumbnail.png'),skia.kPNG)
    print('Stills ready',flush=True)

def render(part=0,parts=1):
    start=int(900*part/parts); end=int(900*(part+1)/parts)
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
