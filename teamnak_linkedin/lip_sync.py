"""Speech-timed robot visemes, modulated by the actual narration signal.

Word boundaries come from the speech engine. Phonemes come from CMUdict;
within-word timings are weighted estimates, not forced phoneme alignment.
"""
from pathlib import Path
import json,re
import numpy as np
import soundfile as sf
import cmudict

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
FPS=60
DICT=cmudict.dict()
SHAPES={
    'rest':(78,0,0), 'closed':(77,0,1),
    'a':(89,49,2), 'e':(101,24,2),
    'o':(57,48,3), 'u':(43,34,3),
    'fv':(83,13,4), 'tongue':(77,25,5),
    'consonant':(88,18,2),
}
def group(phone):
    if phone in ['M','B','P']: return 'closed'
    if phone in ['AA','AE','AH','AO','AW','AY']: return 'a'
    if phone in ['EH','EY','IH','IY']: return 'e'
    if phone in ['OW','OY']: return 'o'
    if phone in ['UW','UH','W']: return 'u'
    if phone in ['F','V']: return 'fv'
    if phone in ['L','TH','DH']: return 'tongue'
    return 'consonant'
def phones(word):
    key=re.sub(r'[^a-z\']','',word.lower())
    special={'ibkr':['AY','B','IY','K','EY','AA','R'],'tradingview':['T','R','EY','D','IH','NG','V','Y','UW'],'fiverr':['F','AY','V','ER']}
    result=DICT.get(key,[special.get(key,['AH','T'])])[0]
    return [re.sub(r'\d','',p) for p in result]
def main():
    speech,sr=sf.read(OUT/'narration.wav')
    count=66*FPS
    hop=sr//FPS
    rms=np.array([np.sqrt(np.mean(speech[i*hop:(i+1)*hop]**2)) for i in range(count)])
    active=rms[rms>.006]
    reference=np.percentile(active,80)
    energy=np.clip(rms/reference,0,1)
    targets=np.tile(np.array(SHAPES['rest'],float),(count,1))
    events=[]
    narration=json.load(open(OUT/'narration.json'))
    for i,meta in enumerate(narration):
        raw,_=sf.read(OUT/f'voice_{i}_raw.wav')
        audible=np.flatnonzero(np.abs(raw)>.006)
        trimmed=max(0,audible[0]-2400)/sr
        words=[json.loads(l) for l in (OUT/f'voice_{i}_words.jsonl').read_text().splitlines() if json.loads(l).get('type')=='WordBoundary']
        for word in words:
            start=meta['start']+(word['offset']/1e7-trimmed)/meta['speed']
            duration=word['duration']/1e7/meta['speed']
            pp=phones(word['text'])
            weights=[1.40 if group(p) in ['a','e','o','u'] else .64 if p in ['B','P','T','K','D','G'] else .90 for p in pp]
            onset=start
            for p,weight in zip(pp,weights):
                end=onset+duration*weight/sum(weights)
                g=group(p)
                a=max(0,round(onset*FPS)); b=min(count,max(a+1,round(end*FPS)))
                targets[a:b]=SHAPES[g]
                events.append(dict(start=onset,end=end,word=word['text'],phoneme=p,viseme=g))
                onset=end
    result=targets.copy()
    # Actual waveform energy controls openness, preventing speech motion in pauses.
    for i in range(count):
        if energy[i]<.055:
            result[i]=SHAPES['rest']
        elif result[i,2] not in [0,1]:
            result[i,1]*=(.58+.42*energy[i])
    # Coarticulation: smooth shape changes while keeping bilabial closures crisp.
    for i in range(1,count):
        if result[i,2] not in [0,1]:
            result[i,:2]=result[i-1,:2]*.25+result[i,:2]*.75
    np.save(OUT/'mouth_visemes.npy',result)
    np.save(OUT/'speech_energy.npy',energy)
    json.dump(dict(method='Speech-engine word timestamps + CMU phonemes + waveform energy; weighted within-word timing',fps=FPS,events=events),open(OUT/'lip_sync.json','w'),indent=2)
    assert len(result)==3960 and np.isfinite(result).all()
    assert sum(result[:,1]>10)>250, 'Insufficient speech articulation'
    silent=rms<.001
    assert not np.any(result[silent,1]>0), 'Mouth moved in silence'
    print(f'Lip sync: {len(events)} phoneme events, {sum(result[:,1]>10)} speaking frames; pause checks passed.',flush=True)

if __name__=='__main__': main()
