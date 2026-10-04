"""Generate neural narration and an original stereo music/SFX bed."""
from pathlib import Path
import asyncio, json, subprocess
import edge_tts
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
DURATION = 66
SCENES = [
    (0,6,'Great ideas deserve more than a whiteboard. They deserve a working system.'),
    (6,13,'We are Team NAK. We build trading automation, blockchain products, and custom software that connects the pieces.'),
    (13,23,'From Interactive Brokers bots to MetaTrader five Expert Advisors and TradingView bridges, we turn your trading rules into automated execution.'),
    (23,32,'On Solana and Ethereum, we build smart contracts and connected applications, with the logic your product needs.'),
    (32,41,'Beyond trading, our Python tools connect data, dashboards, and messaging workflows, so repetitive work moves automatically.'),
    (41,50,'We start with your requirements. Then we design, build, test, and refine the system with you.'),
    (50,58,'You get full source code, a clear setup guide, deployment help, and support after delivery.'),
    (58,66,'Have a strategy, a workflow, or a product idea? Message Team NAK. Let us build what comes next.'),
]
SR=48000
CAPTION_CHUNKS=[]
for _,_,line in SCENES:
    words=line.split(); groups=[]; i=0
    while i<len(words):
        j=i+1
        while j<len(words) and j-i<7 and len(' '.join(words[i:j+1]))<=49: j+=1
        groups.append((i,' '.join(words[i:j]))); i=j
    CAPTION_CHUNKS.append(groups)

async def main():
    voice = np.zeros(SR * DURATION)
    meta = []
    captions=[]
    for i, (start, end, line) in enumerate(SCENES):
        mp3 = OUT / f'voice_{i}.mp3'
        spoken = line.replace('NAK','Nak')
        boundaries=OUT/f'voice_{i}_words.jsonl'
        if not mp3.exists() or not boundaries.exists():
            await edge_tts.Communicate(spoken, 'en-US-AndrewNeural', rate='+0%', pitch='-2Hz',boundary='WordBoundary').save(str(mp3),str(boundaries))
        raw = OUT / f'voice_{i}_raw.wav'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(mp3), '-ar', str(SR), '-ac', '1', str(raw)], check=True)
        s, _ = sf.read(raw)
        # Trim service-generated silences to get a confident, prompt delivery.
        idx = np.flatnonzero(np.abs(s) > 0.006)
        trimmed=max(0,idx[0]-2400)
        s = s[trimmed:min(len(s), idx[-1] + 5000)]
        allowed = end - start - 0.65
        dur = len(s) / SR
        speed = max(1, dur / allowed)
        clean = OUT / f'voice_{i}.wav'
        sf.write(clean, s, SR)
        if speed > 1:
            adjusted = OUT / f'voice_{i}_fit.wav'
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(clean), '-af', f'atempo={speed}', str(adjusted)], check=True)
            s, _ = sf.read(adjusted)
        s = s / max(np.max(np.abs(s)), 0.01) * 0.73
        onset = start + 0.32
        a = int(onset * SR)
        voice[a:a+len(s)] += s
        meta.append(dict(start=onset, end=onset+len(s)/SR, text=line, speed=speed))
        words=[json.loads(l) for l in boundaries.read_text().splitlines() if json.loads(l).get('type')=='WordBoundary']
        chunks=CAPTION_CHUNKS[i]
        for j,(word_index,caption) in enumerate(chunks):
            a=onset+(words[word_index]['offset']/1e7-trimmed/SR)/speed
            b=onset+(words[chunks[j+1][0]]['offset']/1e7-trimmed/SR)/speed if j+1<len(chunks) else onset+len(s)/SR+.25
            captions.append(dict(start=max(start+.3,a),end=min(end-.1,b),text=caption))
    sf.write(OUT/'narration.wav', voice, SR)
    json.dump(meta, open(OUT/'narration.json','w'), indent=2)
    json.dump(captions,open(OUT/'captions.json','w'),indent=2)
    def stamp(seconds):
        ms=round(seconds*1000); return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    (OUT/'teamnak_linkedin.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a["start"])} --> {stamp(a["end"])}\n{a["text"]}' for i,a in enumerate(captions))+'\n')
    n = len(voice)
    t = np.arange(n)/SR
    rng = np.random.default_rng(42)
    music = np.zeros((n,2))
    fx = np.zeros((n,2))
    def add(track, sig, onset, gain=1, pan=0):
        a = int(onset*SR)
        if a < 0 or a >= n: return
        sig = sig[:n-a]
        track[a:a+len(sig),0] += sig*gain*(1-pan*0.35)
        track[a:a+len(sig),1] += sig*gain*(1+pan*0.35)
    def hz(note): return 440*2**((note-69)/12)
    beat = 0.5
    chords = [[50,57,62,65],[46,53,58,62],[53,60,65,69],[48,55,60,64]]
    for bar in range((DURATION+1)//2):
        chord = chords[bar%4]
        u=np.arange(2*SR)/SR
        env = np.minimum(u/0.25,1)*np.minimum((2-u)/0.4,1)
        pad=sum(np.sin(2*np.pi*hz(note)*u)+0.3*np.sin(2*np.pi*hz(note)*1.002*u) for note in chord)*env
        add(music,pad,bar*2,0.009)
        for k in range(4):
            u=np.arange(int(0.45*SR))/SR
            pluck=(np.sin(2*np.pi*hz(chord[k]+12)*u)+0.25*np.sin(4*np.pi*hz(chord[k]+12)*u))*np.exp(-u*11)
            add(music,pluck,bar*2+k*beat,0.025,(-1)**k*0.7)
            bass=np.sin(2*np.pi*hz(chord[0]-12)*u)*np.exp(-u*7)
            add(music,bass,bar*2+k*beat,0.055)
    for k in range(int(DURATION/beat)):
        u=np.arange(int(0.22*SR))/SR
        kick=np.sin(2*np.pi*(42*u+65*(1-np.exp(-u*35))/35))*np.exp(-u*20)
        add(music,kick,k*beat,0.085)
        u=np.arange(int(0.055*SR))/SR
        hat=np.diff(rng.normal(0,1,len(u)+1))*np.exp(-u*90)
        add(music,hat,k*beat+0.25,0.006,0.5)
        if k%2:
            u=np.arange(int(0.12*SR))/SR
            clap=rng.normal(0,1,len(u))*np.exp(-u*40)
            add(music,clap,k*beat,0.010)
    for onset in [s[0] for s in SCENES[1:]]:
        u=np.arange(int(0.48*SR))/SR
        noise=rng.normal(0,1,len(u))
        whoosh=np.convolve(noise,np.ones(28)/28,'same')*np.sin(np.pi*u/0.48)**2
        add(fx,whoosh,onset-0.24,0.10)
        u=np.arange(int(0.7*SR))/SR
        impact=np.sin(2*np.pi*(38*u+32*(1-np.exp(-u*12))/12))*np.exp(-u*8)
        add(fx,impact,onset,0.085)
    for onset in [14.2,16.2,18.2,24.2,27.2,33.2,36.2,42.1,44.1,46.1,48.1,51.2,54.2,59.0]:
        u=np.arange(int(0.25*SR))/SR
        click=(np.sin(2*np.pi*960*u)+0.4*np.sin(2*np.pi*1440*u))*np.exp(-u*25)
        add(fx,click,onset,0.04)
    # Duck the bed under the narrator with a smooth envelope.
    win=int(SR*0.10)
    sums=np.cumsum(np.pad(np.abs(voice),(win//2,win-win//2)))
    env=(sums[win:]-sums[:-win])/win
    duck=1-0.60*np.clip(env/0.04,0,1)
    fade=np.clip(t/0.6,0,1)*np.clip((DURATION-t)/1.3,0,1)
    mix=voice[:,None]+music*duck[:,None]*fade[:,None]+fx
    sf.write(OUT/'mix.wav',mix,SR,subtype='PCM_24')
    print(json.dumps(meta,indent=2),flush=True)

if __name__=='__main__': asyncio.run(main())
