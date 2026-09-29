import json
T=json.load(open('tts.json')); D=T['d']
GAP=0.55; ST=[]; _t=2.0
for x in D: ST.append(_t); _t+=x+GAP
END=_t+2.4
SS=[0.0]+[s-0.3 for s in ST[1:]]; SE=SS[1:]+[END]
CHAR_T=2.0
def cand_t(k): return 0.9+k*0.1
def card_t(k): return SS[3]+0.4+k*0.35
def node_t(k): return SS[4]+0.3+k*(SE[4]-SS[4]-0.6)/5
def alert_t(k): return SS[5]+1.3+k*1.2
def check_t(k): return SS[6]+1.2+k*0.55

LINES=["You have a trading strategy that works.",
"But you can't watch the charts all day. You miss entries, and emotions get in the way.",
"We're Team NAK. We turn trading strategies into automated systems.",
"MT4 and MT5 Expert Advisors. Interactive Brokers bots. And crypto trading bots.",
"Your rules become code. The code is backtested on real data. Then it connects to your broker, and executes exactly as written. Every time.",
"Risk limits, position sizing, and instant alerts to Telegram or Discord. All built in.",
"No black box. You get clean code, full documentation, and support after delivery.",
"Over 300 solutions delivered, with a 4.9 star rating.",
"Send us your strategy. We'll show you exactly how we'd build it."]
NS=len(LINES)
BTN_T=SS[-1]+0.9
def events():
    E=[(SS[i],'whoosh',0) for i in range(1,NS)]
    E+=[(cand_t(k),'tick',0) for k in range(16)]
    E+=[(CHAR_T,'pop',440),(SS[2]+0.15,'boom',0)]
    E+=[(card_t(k),'pop',560+k*110) for k in range(3)]
    E+=[(node_t(k),'pop',480+k*90) for k in range(5)]
    E+=[(alert_t(k),'ding',880+k*220) for k in range(2)]
    E+=[(check_t(k),'pop',620+k*110) for k in range(3)]
    E+=[(SS[7]+0.35,'pop',700),(SS[7]+0.75,'pop',820),(BTN_T,'ding',990)]
    return E
