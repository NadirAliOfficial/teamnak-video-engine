from pathlib import Path
import subprocess,sys,json
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
def run(*args): subprocess.run(args,check=True)
run(sys.executable,str(ROOT/'voice.py'))
run(sys.executable,str(ROOT/'render.py'),'stills')
workers=[subprocess.Popen([sys.executable,str(ROOT/'render.py'),str(i),'3']) for i in range(3)]
codes=[p.wait() for p in workers]
if any(codes): raise RuntimeError(f'Render failed: {codes}')
listing=OUT/'segments.txt'
listing.write_text('\n'.join(f"file '{OUT/f'part_{i}.mp4'}'" for i in range(3)))
run('ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-i',str(OUT/'mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-c:a','aac','-b:a','192k','-ar','48000','-t','30','-movflags','+faststart',str(OUT/'nadir_ali_ibkr_fiverr_v2.mp4'))
run('ffmpeg','-y','-loglevel','error','-i',str(OUT/'nadir_ali_ibkr_fiverr_v2.mp4'),'-vf','scale=1280:720','-r','30','-c:v','libx264','-preset','fast','-crf','22','-c:a','aac','-b:a','160k','-movflags','+faststart',str(OUT/'nadir_ali_ibkr_preview.mp4'))
print('Finished:',OUT/'nadir_ali_ibkr_fiverr_v2.mp4',flush=True)
