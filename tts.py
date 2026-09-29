from kokoro_onnx import Kokoro
import soundfile as sf, json
from tl import LINES as L
k=Kokoro("kokoro-v1.0.onnx","voices-v1.0.bin")
d=[]
for i,l in enumerate(L):
    s,sr=k.create(l.replace("300","three hundred").replace("4.9","four point nine"),voice="am_michael",speed=1.0,lang="en-us")
    sf.write(f"v{i}.wav",s,sr); d.append(len(s)/sr)
json.dump({"sr":sr,"d":d},open("tts.json","w")); print("TTSDONE",d)
