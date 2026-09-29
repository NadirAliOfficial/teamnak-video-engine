import numpy as np, soundfile as sf
from tl import *
SR=48000; N=int((END+0.5)*SR); tt=np.arange(N)/SR
V=np.zeros(N)
for i,s0 in enumerate(ST):
    s,r=sf.read(f'v{i}.wav')
    if s.ndim>1: s=s.mean(1)
    n2=int(len(s)*SR/r); s=np.interp(np.arange(n2)*r/SR,np.arange(len(s)),s)
    a=int(s0*SR); V[a:a+n2]+=s[:N-a]
V=V/(np.abs(V).max()+1e-9)*0.9
def f(m): return 440*2**((m-69)/12)
def add(arr,sig,t0,g=1.0):
    i=int(t0*SR)
    if 0<=i<N: j=min(N,i+len(sig)); arr[i:j]+=g*sig[:j-i]
rng=np.random.default_rng(3)
M=np.zeros(N); bt=60/100; bar=4*bt
CH=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]
for b in range(int(END/bar)+2):
    a=int(b*bar*SR); e=min(N,int((b+1)*bar*SR))
    if a>=N: break
    u=tt[a:e]-b*bar; env=np.clip(u/0.5,0,1)*np.clip((bar-u)/0.5,0,1); ch=CH[b%4]
    for m in ch:
        for d in (0.997,1.003): M[a:e]+=0.04*env*np.sin(2*np.pi*f(m)*d*tt[a:e])
    M[a:e]+=0.08*env*np.sin(2*np.pi*f(ch[0]-24)*tt[a:e])
    for k in range(8):
        L=int(0.45*SR); u2=np.arange(L)/SR; note=ch[k%3]+12+(12 if k%4==3 else 0)
        add(M,np.sin(2*np.pi*f(note)*u2)*np.exp(-u2*8),b*bar+k*bt/2,0.035)
u=np.arange(int(0.35*SR))/SR
kick=np.sin(2*np.pi*(45*u+110*(1-np.exp(-25*u))/25))*np.exp(-u*9)
uh=np.arange(int(0.06*SR))/SR; hat=np.diff(rng.normal(0,1,len(uh)+1))*np.exp(-uh*70)
uc=np.arange(int(0.2*SR))/SR; clap=rng.normal(0,1,len(uc))*np.exp(-uc*28)
k=0; t0=SS[2]+0.15
while t0<END-2.0:
    add(M,kick,t0,0.22); add(M,hat,t0+bt/2,0.025)
    if k%2==1: add(M,clap,t0,0.035)
    t0+=bt; k+=1
X=np.zeros(N)
for ev in events():
    t0,kd,fr=ev
    if kd=='whoosh':
        L=int(0.7*SR); n=np.convolve(rng.normal(0,1,L),np.ones(10)/10,'same'); w=np.sin(np.pi*np.arange(L)/L)**2; add(X,n*w,t0-0.35,0.35)
    elif kd=='tick':
        u2=np.arange(int(0.04*SR))/SR; add(X,np.sin(2*np.pi*2400*u2)*np.exp(-u2*120),t0,0.06)
    elif kd=='pop':
        u2=np.arange(int(0.2*SR))/SR; add(X,np.sin(2*np.pi*fr*u2*(1+0.5*np.exp(-u2*30)))*np.exp(-u2*20),t0,0.16)
    elif kd=='ding':
        u2=np.arange(int(1.0*SR))/SR; add(X,(np.sin(2*np.pi*fr*u2)+0.4*np.sin(4*np.pi*fr*u2)+0.15*np.sin(6*np.pi*fr*u2))*np.exp(-u2*6),t0,0.1)
    elif kd=='boom':
        u2=np.arange(int(1.6*SR))/SR; add(X,np.sin(2*np.pi*(40*u2+60*(1-np.exp(-8*u2))/8))*np.exp(-u2*2.5)+0.3*rng.normal(0,1,len(u2))*np.exp(-u2*14),t0,0.4)
def ma(x,w):
    c=np.cumsum(np.insert(x,0,0)); y=(c[w:]-c[:-w])/w; return np.concatenate([np.full(w//2,y[0]),y,np.full(len(x)-len(y)-w//2,y[-1])])
env=ma(np.abs(V),int(0.12*SR)); g=1-0.6*np.clip(env/(0.25*env.max()),0,1); g=ma(g,int(0.25*SR))
fade=np.clip(tt/0.4,0,1)*np.clip((END+0.3-tt)/1.8,0,1)
out=V+M*g*0.55*fade+X*0.8*fade
out=out/np.abs(out).max()*0.95
sf.write('mix.wav',np.stack([out,out],1),SR,subtype='PCM_16')
FPS=60; NF=int(END*FPS)+2; hop=SR//FPS
rms=np.array([np.sqrt(np.mean(V[i*hop:(i+1)*hop]**2)) if i*hop<N else 0 for i in range(NF)])
ref=np.percentile(rms[rms>0.01],90) if (rms>0.01).any() else 1
m=np.clip((rms/ref-0.08)/0.92,0,1); o=np.zeros(NF)
for i in range(1,NF): o[i]=o[i-1]+(m[i]-o[i-1])*(0.6 if m[i]>o[i-1] else 0.3)
np.save('mouth.npy',o); print('MIXDONE',round(END,2))
