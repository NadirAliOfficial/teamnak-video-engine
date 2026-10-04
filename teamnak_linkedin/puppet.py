"""Articulated atlas rig: independent limbs, head, live eyes and speech mouth."""
from pathlib import Path
import skia,math,json
import numpy as np
ROOT=Path(__file__).resolve().parent
ATLAS=skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(str(ROOT/'assets/mascot-rig.png')))
BOUNDS=json.load(open(ROOT/'assets/rig-bounds.json'))
SAMPLING=skia.SamplingOptions(skia.FilterMode.kLinear,skia.MipmapMode.kNone)

def p(col,a=1,stroke=0):
    col=col.lstrip('#');rgb=[int(col[i:i+2],16) for i in (0,2,4)]
    out=skia.Paint(AntiAlias=True,Color=skia.Color(*rgb,int(255*max(0,min(1,a)))))
    if stroke: out.setStyle(skia.Paint.kStroke_Style);out.setStrokeWidth(stroke);out.setStrokeCap(skia.Paint.kRound_Cap)
    return out
def part(c,key,x,y,w):
    x0,y0,x1,y1=BOUNDS[key]
    h=w*(y1-y0)/(x1-x0)
    c.drawImageRect(ATLAS,skia.Rect.MakeLTRB(x0,y0,x1,y1),skia.Rect.MakeXYWH(x,y,w,h),SAMPLING)
    return h
def arm(c,key,x,y,angle):
    c.save();c.translate(x,y);c.rotate(angle)
    part(c,key,-37,-22,74)
    c.restore()
def leg(c,key,x,y,angle):
    c.save();c.translate(x,y);c.rotate(angle)
    part(c,key,-45,-14,90)
    c.restore()
def mouth(c,viseme):
    w,h,kind=viseme
    w*=.70;h*=.70
    pa=skia.Path()
    if kind<2:
        pa.moveTo(-w/2,-2);pa.quadTo(0,9 if kind==0 else 0,w/2,-2)
    else:
        pa.addOval(skia.Rect.MakeXYWH(-w/2,-h/2,w,max(3,h)))
        c.drawPath(pa,p('#051914'))
    gl=p('#51E7A0',.34,7);gl.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle,5))
    c.drawPath(pa,gl);c.drawPath(pa,p('#82FFD0',1,5))
    if kind==4: c.drawLine(-w*.3,-h*.14,w*.3,-h*.14,p('#D7FFEA',1,2))
    if kind==5: c.drawRoundRect(skia.Rect.MakeXYWH(-w*.12,h*.03,w*.24,h*.22),3,3,p('#51E7A0',.8))

def draw(c,x,y,height,t,viseme,mode='present',gaze=-1):
    """All motion is continuous; no whole-character image switching."""
    scale=height/580
    bob=math.sin(t*1.7)*4
    shadow=p('#000000',.22);shadow.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle,12))
    c.drawOval(skia.Rect.MakeXYWH(x-height*.18,y+height*.47,height*.36,height*.045),shadow)
    c.save();c.translate(x,y+bob);c.scale(scale,scale)
    walk=mode=='walk'
    sway=1.5*math.sin(t*1.5)
    c.rotate(sway)
    # Hip joints and independently moving legs sit behind the torso.
    leg(c,'left_leg',-52,121,12*math.sin(t*7) if walk else 1.5*math.sin(t*1.2))
    leg(c,'right_leg',52,121,-12*math.sin(t*7) if walk else -1.5*math.sin(t*1.2))
    if mode=='wave':
        left=132+15*math.sin(t*6.5);right=-14+4*math.sin(t*2)
    elif mode=='point':
        left=65+6*math.sin(t*2.6);right=-18+7*math.sin(t*2.0)
    elif mode=='think':
        left=29+8*math.sin(t*1.7);right=-80+7*math.sin(t*2.2)
    elif walk:
        left=20*math.sin(t*7);right=-20*math.sin(t*7)
    else:
        left=32+15*math.sin(t*2.2);right=-25+12*math.sin(t*1.8+.6)
    arm(c,'left_arm',-106,-6,left)
    arm(c,'right_arm',106,-6,right)
    part(c,'torso',-105,-43,210)
    # Head movement is independent of torso sway and limb gestures.
    c.save();c.translate(0,-20+2.4*math.sin(t*2.0));c.rotate(2.3*math.sin(t*1.15))
    part(c,'head',-166,-266,332)
    blink_phase=t%3.65
    blink=max(.08,min(1,abs(blink_phase-.13)/.075)) if blink_phase<.26 else 1
    look=5*gaze+3*math.sin(t*.65)
    for ex in [-62,62]:
        c.save();c.translate(ex+look,-150);c.scale(1,blink)
        # Friendly LED eyes morph and blink rather than remaining baked into art.
        eye=skia.Path();eye.moveTo(-21,9);eye.cubicTo(-16,-22,16,-22,21,9)
        glow=p('#51E7A0',.45,15);glow.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle,6))
        c.drawPath(eye,glow);c.drawPath(eye,p('#6EFFC0',1,14))
        c.restore()
        eyebrow=skia.Path();eyebrow.moveTo(ex-16,-189);eyebrow.quadTo(ex,-199+3*math.sin(t*1.7),ex+16,-189)
        c.drawPath(eyebrow,p('#51E7A0',.85,4))
    c.save();c.translate(look*.5,-91);mouth(c,viseme);c.restore()
    c.restore();c.restore()
