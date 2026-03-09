"""
ELARIX — The Medieval AI Archivist
ZUCHINNI.AI · MYP Design Project

HOW TO RUN:
1. pip install flask better-profanity
2. Run this file
3. Open http://localhost:5000
"""

import os, json, random, time, hashlib
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, send_from_directory
from better_profanity import profanity

profanity.load_censor_words()
app = Flask(__name__)
app.secret_key = "elarix-medieval-2024"

# ─────────────────────────────────────────
# DATA STORAGE
# ─────────────────────────────────────────
os.makedirs("data", exist_ok=True)

def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f: json.dump(data, f, indent=2)

def get_users():   return load_json("data/users.json", {})
def save_users(u): save_json("data/users.json", u)
def get_scores():  return load_json("data/scores.json", [])
def hash_pw(pw):   return hashlib.sha256(pw.encode()).hexdigest()

def record_score(username, score, chapter_id):
    scores = get_scores()
    scores.append({"username": username, "score": score,
                   "chapter": KNOWLEDGE.get(chapter_id, {}).get("title", chapter_id),
                   "date": datetime.now().strftime("%Y-%m-%d %H:%M")})
    save_json("data/scores.json", sorted(scores, key=lambda x: x["score"], reverse=True)[:50])

def init_session():
    for k, v in [("anger",0),("dungeon",False),("dungeon_until",0),("riddle",None),
                 ("bubble_mode",False),("bubble_score",0),("quiz_score",0)]:
        session.setdefault(k, v)

# ─────────────────────────────────────────
# KNOWLEDGE BASE
# ─────────────────────────────────────────
KNOWLEDGE = {
    "chapter-1": {
        "title": "Chapter I: The Golden Age",
        "subtitle": "Dynasties & Early Kerala",
        "icon": "👑", "color": "#C9A84C",
        "key_facts": [
            "Chera Dynasty ruled 800–1102 CE",
            "Famous ancient port: Musiri (Cranganore)",
            "Black pepper — 'black gold' — traded with Rome & Arabia",
            "Sangam literature recorded Chera history",
            "Capital: Mahodayapuram (Kodungallur)"
        ],
        "quiz": [
            {"q": "What spice made Kerala famous in ancient trade?",         "a": ["pepper","black pepper","black gold"], "hint": "Called 'black gold' by the Romans"},
            {"q": "What was Kerala's most famous ancient port called?",      "a": ["musiri","muchiri","cranganore"],      "hint": "Romans wrote about it extensively"},
            {"q": "Which dynasty ruled Kerala's Golden Age 800–1102 CE?",   "a": ["chera","cheras","kulasekharas"],      "hint": "Also known as the Kulasekharas"},
        ],
        "qa": [
            {"keywords": ["chera","dynasty","kulasekharas","kings","who ruled","ancient kingdom","rulers"],
             "answer": "The **Chera Dynasty** — also called the **Kulasekharas** — ruled Kerala from approximately **800 to 1102 CE**, establishing one of the most prosperous kingdoms in ancient India. Their capital was **Mahodayapuram** (modern Kodungallur). The Cheras were known for their powerful navy, patronage of the arts, and grand temple construction.\n\n⚜ *A scroll whispers:* The last great Chera king donated the Thiruvanchikulam temple — one of Kerala's most sacred shrines."},
            {"keywords": ["trade","spice","pepper","black gold","roman","commerce","port","musiri","muchiri","cranganore","export","economy"],
             "answer": "Kerala was the world's **spice capital** in the ancient era. **Black pepper** — known as *'black gold'* — was Kerala's most prized export, traded with the **Roman Empire, Arabia, and China**. The ancient port of **Musiri** was so famous that Roman authors described it as teeming with ships from every corner of the world.\n\nRoman coins have been found in archaeological digs across Kerala, proving the vast scale of this trade.\n\n⚜ *A scroll whispers:* A Roman writer once said pepper ships arrived at Musiri so frequently that the harbour never saw a quiet day."},
            {"keywords": ["sangam","literature","poetry","tamil","culture","arts","writing","language"],
             "answer": "The **Sangam era** produced remarkable Tamil poetry documenting Chera kings in vivid detail. Works like the *Purananuru* describe Chera rulers, their battles and generosity. The famous king **Senguttuvan** (the Red Chera) is celebrated in the epic *Silappatikaram* for campaigns as far as the Himalayas.\n\n⚜ *A scroll whispers:* Sangam poets described Kerala's landscape so precisely that modern scholars use their verses to identify ancient geographical locations."},
            {"keywords": ["religion","temple","hindu","buddhism","faith","worship","god","deity"],
             "answer": "Ancient Kerala was a land of religious diversity. **Hinduism** dominated with grand temples, but **Buddhism** and **Jainism** also flourished. The **Vadakkunnathan Temple** in Thrissur and **Thiruvanchikulam Temple** were important Chera royal shrines. Kerala's famous *Theyyam* ritual performances have roots going back over 1,500 years.\n\n⚜ *A scroll whispers:* Kerala's Theyyam blends pre-Hindu tribal traditions with later Hindu practices — a living piece of ancient history."},
            {"keywords": ["decline","end","fall","collapse","chola","invasion","1102"],
             "answer": "The Chera Dynasty **collapsed around 1102 CE** after prolonged conflict with the powerful **Chola Empire** from Tamil Nadu. Repeated Chola invasions weakened central authority, causing the kingdom to fragment into smaller rival chieftaincies — the political landscape that shaped all of medieval Kerala.\n\n⚜ *A scroll whispers:* After the Chera collapse, no single ruler unified all of Kerala again until it joined independent India in 1947."},
        ]
    },
    "chapter-2": {
        "title": "Chapter II: Medieval Kingdoms",
        "subtitle": "Zamorins, Nairs & the Spice Wars",
        "icon": "⚔️", "color": "#8B4513",
        "key_facts": [
            "Zamorin of Calicut rose to power in the 13th century",
            "Vasco da Gama arrived at Calicut on 20 May 1498",
            "Kunjali Marakkars: Kerala's legendary Muslim naval commanders",
            "Kalaripayattu: world's oldest martial art, born in Kerala",
            "Portuguese captured Goa in 1510"
        ],
        "quiz": [
            {"q": "In what year did Vasco da Gama arrive at Calicut?",            "a": ["1498"],                                     "hint": "End of the 15th century"},
            {"q": "What is the world's oldest martial art from Kerala?",           "a": ["kalaripayattu","kalari"],                    "hint": "Still practiced and taught today"},
            {"q": "Who were the Zamorin's famous Muslim naval commanders?",        "a": ["kunjali marakkars","kunjali","marakkars"],   "hint": "They defended the Kerala coast from the Portuguese"},
        ],
        "qa": [
            {"keywords": ["zamorin","calicut","kozhikode","ruler","king","samoothiri"],
             "answer": "The **Zamorin** (also *Samoothiri*) was the powerful ruler of **Calicut (Kozhikode)**, dominating northern Kerala from the 13th century. The Zamorins built their kingdom through maritime trade, controlling the most important spice port on the Malabar Coast. Their court welcomed Arab, Chinese, and Jewish merchants — Calicut was one of the most cosmopolitan cities in medieval Asia.\n\n⚜ *A scroll whispers:* The Zamorin's title literally means 'Lord of the Sea' — a fitting name for a ruler whose power came entirely from maritime trade."},
            {"keywords": ["vasco da gama","portuguese","portugal","1498","arrival","explorer","europe"],
             "answer": "On **20 May 1498**, Portuguese explorer **Vasco da Gama** arrived at **Calicut**, completing the first direct sea voyage from Europe to India. This broke the Arab monopoly on the spice trade and opened the Indian Ocean to European powers.\n\nThe Zamorin initially welcomed the Portuguese, but tensions grew — da Gama's gifts were considered insultingly small, and Arab merchants warned the Zamorin that the Portuguese were a military threat.\n\n⚜ *A scroll whispers:* Da Gama's voyage took over a year. The profit from his spice cargo was 60 times the cost of the entire expedition."},
            {"keywords": ["kunjali","marakkars","naval","navy","sea","fleet","admiral","muslim","commander"],
             "answer": "The **Kunjali Marakkars** were a dynasty of brilliant Muslim naval commanders who served the Zamorin of Calicut — the most feared naval force in the Arabian Sea. **Kunjali Marakkar IV** was so successful at disrupting Portuguese shipping that the Portuguese signed treaties with his enemies just to capture him. He was eventually executed in Goa in 1600.\n\n⚜ *A scroll whispers:* Kunjali Marakkar IV is remembered as 'Admiral of the Malabar Coast' — Kerala's greatest naval hero and a symbol of resistance against colonial powers."},
            {"keywords": ["kalaripayattu","kalari","martial art","fighting","combat","warrior","nair"],
             "answer": "**Kalaripayattu** is the world's oldest surviving martial art, originating in Kerala over **3,000 years ago**. It combines strikes, kicks, grappling, weaponry (sword, spear, and the flexible sword called *Urumi*), and healing techniques. Traditionally practiced by the **Nair warrior caste**, masters were said to achieve superhuman flexibility.\n\n⚜ *A scroll whispers:* The flexible *Urumi* sword is so dangerous it is only taught to students who have already mastered every other weapon."},
            {"keywords": ["kathakali","dance","mohiniyattam","art","performance","classical","culture","music","theatre"],
             "answer": "Medieval Kerala gave birth to world-famous classical art forms. **Kathakali** — the elaborate dance-drama with iconic makeup — tells stories from the Mahabharata and Ramayana. Performers train from childhood in extraordinary physical control. **Mohiniyattam** is a graceful solo dance, and **Theyyam** is a ritual performance where the dancer embodies a deity.\n\n⚜ *A scroll whispers:* A Kathakali performer's elaborate makeup — called *chutti* — takes up to 6 hours to apply using natural pigments."},
            {"keywords": ["arab","ibn battuta","china","chinese","zheng he","merchant","traveller","visitor","trade network"],
             "answer": "Medieval Calicut was one of the most **cosmopolitan cities on Earth**. Arab, Persian, Chinese, and Jewish merchants all had permanent communities there. Moroccan traveller **Ibn Battuta** visited in the 14th century and described it as one of the greatest ports he had ever seen. Chinese admiral **Zheng He** also visited during his treasure fleet voyages. The Chinese fishing nets (*cheena vala*) still used in Kochi today were introduced in this era.\n\n⚜ *A scroll whispers:* Ibn Battuta was so impressed that he spent several months in Calicut, describing ships so large 'each had a thousand men aboard'."},
        ]
    },
    "chapter-3": {
        "title": "Chapter III: Colonial Era & Independence",
        "subtitle": "Europeans, Travancore & Freedom",
        "icon": "🏰", "color": "#2E6B4F",
        "key_facts": [
            "Battle of Colachel 1741: Travancore defeated the Dutch East India Company",
            "Marthanda Varma unified southern Kerala under Travancore",
            "Slavery abolished in Travancore in 1855",
            "Temple Entry Proclamation: 1936",
            "Kerala elected world's first democratic communist government in 1957"
        ],
        "quiz": [
            {"q": "In what year did Travancore defeat the Dutch at the Battle of Colachel?", "a": ["1741"],                                        "hint": "18th century — a famous Asian victory over Europeans"},
            {"q": "Who was the Dutch commander captured at the Battle of Colachel?",         "a": ["de lannoy","lannoy","eustachius de lannoy"],  "hint": "He later helped modernise the Travancore army"},
            {"q": "When was the Temple Entry Proclamation issued in Travancore?",            "a": ["1936"],                                        "hint": "Opening temples to all castes"},
        ],
        "qa": [
            {"keywords": ["battle of colachel","colachel","dutch","voc","1741","marthanda varma","victory","defeat"],
             "answer": "In **1741**, King **Marthanda Varma** of Travancore defeated the **Dutch East India Company (VOC)** at the **Battle of Colachel** — one of the only decisive Asian military victories over a European colonial power in the 18th century. Dutch commander **Eustachius De Lannoy** was captured and forced to serve Travancore, ironically rebuilding the army that defeated him.\n\n⚜ *A scroll whispers:* De Lannoy lived in Travancore for over 30 years, married a local woman, and became one of Marthanda Varma's most trusted advisors. His grave can still be visited in Udayagiri, Kerala."},
            {"keywords": ["marthanda varma","travancore","kingdom","unification","padmanabha","king"],
             "answer": "**Marthanda Varma** (ruled 1729–1758) unified the fragmented southern Kerala chieftaincies into a powerful Travancore kingdom. He dedicated the entire kingdom to **Lord Padmanabha** at the Padmanabhaswamy Temple, declaring himself *'Padmanabha Dasa'* — servant of Padmanabha — ruling as a steward of the deity rather than an absolute monarch.\n\n⚜ *A scroll whispers:* The Padmanabhaswamy Temple's underground vaults, opened in 2011, contained treasures estimated at over **$22 billion** — the largest temple treasure ever discovered."},
            {"keywords": ["slavery","abolish","1855","social reform","caste","lower caste","sree narayana","discrimination"],
             "answer": "Travancore **abolished slavery in 1855** — decades before it was abolished across much of the British Empire. Social reformer **Sree Narayana Guru** fought tirelessly against caste discrimination through the early 20th century, with his famous saying: *'One caste, one religion, one God for humanity.'*\n\n⚜ *A scroll whispers:* Lower-caste women in parts of Kerala were once taxed for covering their chests — a brutal injustice that reformers fought and ended."},
            {"keywords": ["temple entry","proclamation","1936","chithira thirunal","caste","untouchables","open temple"],
             "answer": "On **12 November 1936**, Maharaja **Chithira Thirunal** issued the **Temple Entry Proclamation**, opening all government temples to worshippers of all castes — including communities who had been banned for centuries. This made Travancore the first Hindu kingdom to officially end caste-based temple discrimination.\n\n⚜ *A scroll whispers:* The proclamation followed years of campaigning including the **Vaikom Satyagraha** — a 16-year civil disobedience movement inspired by Gandhi, one of the earliest in India."},
            {"keywords": ["british","east india company","colonial","empire","colonialism","british rule","malabar"],
             "answer": "The **British East India Company** gradually extended influence over Kerala through treaties and military pressure. Travancore and Cochin remained **Princely States** under British suzerainty, while Malabar in the north was directly administered as part of Madras Presidency. British rule brought railways and modern schools but deepened economic exploitation.\n\n⚜ *A scroll whispers:* The **Malabar Rebellion of 1921** — a major uprising by Muslim peasants against British rule — is one of the most debated events in Kerala's colonial history."},
            {"keywords": ["independence","1947","1957","communist","ems","namboodiripad","elections","literacy","modern","kerala model"],
             "answer": "Kerala joined independent India on **1 July 1949** and became the state of Kerala on **1 November 1956**. In **1957**, Kerala made world history by electing the **world's first democratic communist government**, led by **E.M.S. Namboodiripad**. Today Kerala is celebrated for its near **100% literacy rate**, highest Human Development Index in India, and the famous **Kerala Model** of social development.\n\n⚜ *A scroll whispers:* Kerala sends more nurses and doctors abroad than any other Indian state — the 'Kerala nurse' is a globally recognised figure working from the Gulf to the UK."},
        ]
    }
}

RIDDLES = [
    {"q": "I have cities, but no houses. Mountains, but no trees. Water, but no fish. What am I?",     "a": ["map"],       "hint": "You use me for navigation"},
    {"q": "The more you take, the more you leave behind. What am I?",                                  "a": ["footsteps"], "hint": "Think about walking"},
    {"q": "I speak without a mouth, hear without ears. No body, yet I come alive with wind. What am I?","a": ["echo"],      "hint": "Mountains produce me"},
    {"q": "What has keys but no locks, space but no room — you can enter but not go inside?",          "a": ["keyboard"],  "hint": "You are using one right now"},
    {"q": "I am always before you, yet cannot be seen. I am behind every king and every dream.",       "a": ["future"],    "hint": "Tomorrow is my first name"},
]

# ─────────────────────────────────────────
# SMART SEARCH
# ─────────────────────────────────────────
def search(query, chapter_id):
    if chapter_id not in KNOWLEDGE: return None
    q = query.lower()
    best, best_score = None, 0
    for pair in KNOWLEDGE[chapter_id]["qa"]:
        score = sum(1 for kw in pair["keywords"] if kw in q)
        if score > best_score:
            best_score, best = score, pair["answer"]
    return best if best_score > 0 else None

# ─────────────────────────────────────────
# HTML TEMPLATES
# ─────────────────────────────────────────

LANDING_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ZUCHINNI.AI — Elarix</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;600&family=IM+Fell+English:ital@0;1&display=swap" rel="stylesheet">
<style>
:root{--maroon:#6B1E2E;--deep:#100308;--gold:#C9A84C;--parchment:#F5E6C8;}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--deep);font-family:'IM Fell English',serif;color:var(--parchment);min-height:100vh;overflow-x:hidden;}
.bg{position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse 80% 60% at 15% 55%,rgba(107,30,46,.38),transparent 60%),radial-gradient(ellipse 60% 50% at 85% 20%,rgba(55,15,8,.45),transparent 60%),linear-gradient(175deg,#060102,#100308,#09020C);}
.bg-grid{position:fixed;inset:0;z-index:0;opacity:.05;background-image:linear-gradient(rgba(201,168,76,.8) 1px,transparent 1px),linear-gradient(90deg,rgba(201,168,76,.8) 1px,transparent 1px);background-size:80px 80px;}
.particle{position:fixed;border-radius:50%;pointer-events:none;z-index:1;animation:rise linear infinite;}
@keyframes rise{0%{transform:translateY(105vh) scale(0);opacity:0}10%{opacity:1}90%{opacity:.6}100%{transform:translateY(-5vh) scale(.5);opacity:0}}
nav{position:fixed;top:0;left:0;right:0;z-index:200;display:flex;justify-content:space-between;align-items:center;padding:1.2rem 3rem;background:rgba(8,1,2,.7);border-bottom:1px solid rgba(201,168,76,.12);backdrop-filter:blur(16px);}
.logo{font-family:'Cinzel Decorative',cursive;font-size:1.05rem;color:var(--gold);text-decoration:none;letter-spacing:3px;}
nav a:not(.logo){font-family:'Cinzel',serif;font-size:.72rem;color:rgba(245,230,200,.55);text-decoration:none;letter-spacing:2.5px;text-transform:uppercase;margin-left:2rem;transition:color .3s;}
nav a:not(.logo):hover{color:var(--gold);}
.hero{position:relative;z-index:10;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:2rem;}
.eyebrow{font-family:'Cinzel',serif;font-size:.68rem;letter-spacing:6px;color:var(--gold);opacity:.75;text-transform:uppercase;border:1px solid rgba(201,168,76,.28);padding:.45rem 1.8rem;border-radius:30px;margin-bottom:2.2rem;animation:fadeUp 1s ease both;}
.title{font-family:'Cinzel Decorative',cursive;font-size:clamp(3.5rem,11vw,8rem);color:var(--gold);line-height:.95;text-shadow:0 0 80px rgba(201,168,76,.35);animation:fadeUp 1s ease .15s both;margin-bottom:.6rem;}
.rule{width:120px;height:2px;background:linear-gradient(90deg,transparent,var(--gold),transparent);margin:.8rem auto 1.6rem;animation:fadeUp 1s ease .25s both;}
.sub{font-family:'Cinzel',serif;font-size:clamp(.9rem,2.5vw,1.3rem);color:rgba(245,230,200,.45);letter-spacing:5px;text-transform:uppercase;animation:fadeUp 1s ease .3s both;margin-bottom:2.5rem;}
.desc{font-size:1.1rem;max-width:580px;line-height:2;color:rgba(245,230,200,.72);font-style:italic;animation:fadeUp 1s ease .45s both;margin-bottom:3.5rem;}
.btns{display:flex;gap:1.4rem;flex-wrap:wrap;justify-content:center;animation:fadeUp 1s ease .6s both;}
.btn-g{font-family:'Cinzel',serif;font-size:.8rem;letter-spacing:3px;padding:1rem 2.8rem;text-decoration:none;text-transform:uppercase;border-radius:4px;transition:all .35s;background:linear-gradient(135deg,var(--maroon),#3D0D1A);border:1.5px solid var(--gold);color:var(--gold);}
.btn-g:hover{transform:translateY(-3px);box-shadow:0 0 35px rgba(201,168,76,.25);}
.btn-ghost{font-family:'Cinzel',serif;font-size:.8rem;letter-spacing:3px;padding:1rem 2.8rem;text-decoration:none;text-transform:uppercase;border-radius:4px;transition:all .35s;background:transparent;border:1.5px solid rgba(245,230,200,.22);color:rgba(245,230,200,.55);}
.btn-ghost:hover{border-color:var(--gold);color:var(--gold);}
.features{position:relative;z-index:10;max-width:1080px;margin:0 auto;padding:5rem 2rem 7rem;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.6rem;}
.fc{background:rgba(40,12,20,.88);border:1px solid rgba(201,168,76,.18);border-radius:10px;padding:2rem 1.8rem;text-align:center;transition:all .4s;animation:fadeUp .8s ease both;}
.fc:hover{border-color:var(--gold);transform:translateY(-5px);box-shadow:0 25px 60px rgba(0,0,0,.55);}
.fi{font-size:2.4rem;margin-bottom:1rem;}
.ft{font-family:'Cinzel',serif;font-size:.85rem;color:var(--gold);letter-spacing:2.5px;text-transform:uppercase;margin-bottom:.7rem;}
.fd{font-size:.9rem;line-height:1.85;color:rgba(245,230,200,.62);font-style:italic;}
footer{position:relative;z-index:10;text-align:center;padding:2.5rem;border-top:1px solid rgba(201,168,76,.1);font-family:'Cinzel',serif;font-size:.68rem;letter-spacing:2px;color:rgba(245,230,200,.25);}
@keyframes fadeUp{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:translateY(0)}}
</style></head><body>
<div class="bg"></div><div class="bg-grid"></div>
<nav><a href="/" class="logo">⚔ ZUCHINNI.AI</a><div><a href="/login">Login</a><a href="/signup">Join</a><a href="/leaderboard">Hall of Fame</a></div></nav>
<section class="hero">
  <div class="eyebrow">✦ MYP Design Project · Kerala History · ZUCHINNI.AI ✦</div>
  <h1 class="title">ELARIX</h1><div class="rule"></div>
  <p class="sub">The Ancient Archivist of Kerala</p>
  <p class="desc">"Enter these halls, seeker. I am Elarix — keeper of Kerala's chronicles spanning three thousand years of dynasties, spice routes, martial arts, and the courage of kings. Ask, and the ancient scrolls shall answer."</p>
  <div class="btns"><a href="/signup" class="btn-g">⚔ Begin Your Journey</a><a href="/login" class="btn-ghost">Return to Archives</a></div>
</section>
<div class="features">
  <div class="fc" style="animation-delay:.05s"><div class="fi">📜</div><div class="ft">Three Chronicles</div><div class="fd">Journey through Kerala's Golden Age, medieval Zamorin kingdoms, and the colonial era — packed with rich historical detail.</div></div>
  <div class="fc" style="animation-delay:.12s"><div class="fi">🔍</div><div class="ft">Smart Search</div><div class="fd">Ask any question in plain English. Elarix searches the scrolls and responds in the voice of a medieval archivist.</div></div>
  <div class="fc" style="animation-delay:.19s"><div class="fi">⚔️</div><div class="ft">Dungeon & Riddles</div><div class="fd">Speak with respect or face the dungeon! Solve ancient riddles and pop enchanted bubbles to earn freedom.</div></div>
  <div class="fc" style="animation-delay:.26s"><div class="fi">📝</div><div class="ft">Chapter Quizzes</div><div class="fd">Test your knowledge with 3 questions per chapter and climb the Scrolls of Fame leaderboard.</div></div>
  <div class="fc" style="animation-delay:.33s"><div class="fi">🔐</div><div class="ft">Your Own Account</div><div class="fd">Sign up and log in — quiz scores and your leaderboard rank are saved across sessions.</div></div>
  <div class="fc" style="animation-delay:.40s"><div class="fi">🏆</div><div class="ft">Hall of Fame</div><div class="fd">Top 50 quiz scores from all scholars displayed on the Scrolls of Fame — compete for the crown.</div></div>
</div>
<footer>⚜ ZUCHINNI.AI · Elarix the Archivist · MYP Design Project ⚜</footer>
<script>for(let i=0;i<18;i++){const p=document.createElement('div');p.className='particle';const s=Math.random()*5+2;p.style.cssText=`width:${s}px;height:${s}px;left:${Math.random()*100}%;background:rgba(201,168,76,${Math.random()*.35+.08});animation-duration:${Math.random()*18+12}s;animation-delay:-${Math.random()*18}s;box-shadow:0 0 ${s*3}px rgba(201,168,76,.4);`;document.body.appendChild(p);};</script>
</body></html>"""

AUTH_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{% if mode=='login' %}Enter{% else %}Join{% endif %} — Elarix</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Cinzel:wght@400;600&family=IM+Fell+English:ital@0;1&display=swap" rel="stylesheet">
<style>
:root{--maroon:#6B1E2E;--deep:#100308;--gold:#C9A84C;--parchment:#F5E6C8;}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--deep);font-family:'IM Fell English',serif;color:var(--parchment);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:1.5rem;}
.bg{position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse 70% 70% at 25% 55%,rgba(107,30,46,.3),transparent 65%),linear-gradient(170deg,#060102,#100308);}
.card{position:relative;z-index:10;background:rgba(42,12,22,.94);border:1px solid rgba(201,168,76,.3);border-radius:14px;padding:3rem 2.8rem;width:100%;max-width:430px;backdrop-filter:blur(22px);box-shadow:0 50px 100px rgba(0,0,0,.65);}
.top{text-align:center;margin-bottom:2rem;}
.logo-link{font-family:'Cinzel Decorative',cursive;font-size:.95rem;color:var(--gold);text-decoration:none;letter-spacing:3px;display:block;margin-bottom:1.8rem;}
.orn{color:rgba(201,168,76,.35);font-size:1.1rem;margin-bottom:1rem;}
h1{font-family:'Cinzel Decorative',cursive;font-size:1.75rem;color:var(--gold);text-shadow:0 0 30px rgba(201,168,76,.25);margin-bottom:.4rem;}
.csub{font-style:italic;color:rgba(245,230,200,.45);font-size:.88rem;}
.divider{height:1px;background:linear-gradient(90deg,transparent,rgba(201,168,76,.35),transparent);margin:1.6rem 0;}
label{font-family:'Cinzel',serif;font-size:.65rem;letter-spacing:2.5px;text-transform:uppercase;color:rgba(245,230,200,.55);display:block;margin-bottom:.45rem;}
input{width:100%;padding:.9rem 1.1rem;margin-bottom:1.3rem;background:rgba(8,2,5,.7);border:1px solid rgba(201,168,76,.22);border-radius:7px;color:var(--parchment);font-family:'IM Fell English',serif;font-size:1rem;outline:none;transition:all .3s;}
input:focus{border-color:var(--gold);box-shadow:0 0 20px rgba(201,168,76,.12);}
input::placeholder{color:rgba(245,230,200,.2);font-style:italic;}
.btn{width:100%;padding:1rem;font-family:'Cinzel',serif;font-size:.8rem;letter-spacing:3px;text-transform:uppercase;background:linear-gradient(135deg,var(--maroon),#3D0D1A);border:1.5px solid var(--gold);border-radius:7px;color:var(--gold);cursor:pointer;transition:all .35s;margin-top:.3rem;}
.btn:hover{box-shadow:0 0 30px rgba(201,168,76,.28);transform:translateY(-1px);}
.btn:disabled{opacity:.45;cursor:not-allowed;transform:none;}
.err{background:rgba(110,30,30,.35);border:1px solid rgba(200,60,60,.3);border-radius:7px;padding:.8rem 1rem;font-size:.85rem;color:#ffaaaa;text-align:center;margin-bottom:1.1rem;display:none;}
.sw{text-align:center;margin-top:1.6rem;font-size:.88rem;color:rgba(245,230,200,.45);}
.sw a{color:var(--gold);text-decoration:none;font-family:'Cinzel',serif;}
.sw a:hover{text-decoration:underline;}
</style></head><body><div class="bg"></div>
<div class="card">
  <div class="top">
    <a href="/" class="logo-link">⚔ ZUCHINNI.AI</a>
    <div class="orn">⚜ ✦ ⚜</div>
    <h1>{% if mode=='login' %}The Gates Open{% else %}Join the Order{% endif %}</h1>
    <p class="csub">{% if mode=='login' %}Return to the chronicles, scholar.{% else %}Begin your medieval journey, seeker.{% endif %}</p>
  </div>
  <div class="divider"></div>
  <div class="err" id="err"></div>
  <label>Chosen Name</label>
  <input type="text" id="username" placeholder="Enter your name, traveller..." autocomplete="off">
  <label>Secret Passphrase</label>
  <input type="password" id="password" placeholder="Your passphrase...">
  {% if mode=='signup' %}
  <label>Confirm Passphrase</label>
  <input type="password" id="confirm" placeholder="Repeat your passphrase...">
  {% endif %}
  <button class="btn" id="btn" onclick="go()">{% if mode=='login' %}⚔ Enter the Archives{% else %}📜 Begin the Journey{% endif %}</button>
  <div class="sw">{% if mode=='login' %}New here? <a href="/signup">Create your chronicle</a>{% else %}Already a scholar? <a href="/login">Enter the archives</a>{% endif %}</div>
</div>
<script>
const mode="{{mode}}";
document.addEventListener('keydown',e=>{if(e.key==='Enter')go();});
async function go(){
  const u=document.getElementById('username').value.trim(),p=document.getElementById('password').value;
  document.getElementById('err').style.display='none';
  if(!u||!p){show('Both fields are required.');return;}
  if(mode==='signup'){
    const c=document.getElementById('confirm').value;
    if(p!==c){show('Passphrases do not match!');return;}
    if(p.length<4){show('Passphrase must be 4+ characters.');return;}
  }
  const btn=document.getElementById('btn');btn.disabled=true;btn.textContent='⏳ Consulting scrolls...';
  const r=await fetch('/'+mode,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
  const d=await r.json();
  if(d.success){btn.textContent='✓ Granted!';setTimeout(()=>window.location='/chapters',700);}
  else{show(d.error||'The scrolls reject your entry.');btn.disabled=false;btn.textContent=mode==='login'?'⚔ Enter the Archives':'📜 Begin the Journey';}
}
function show(m){const e=document.getElementById('err');e.textContent=m;e.style.display='block';}
</script></body></html>"""

CHAPTERS_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Choose Your Chronicle — Elarix</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Cinzel:wght@400;600&family=IM+Fell+English:ital@0;1&display=swap" rel="stylesheet">
<style>
:root{--maroon:#6B1E2E;--deep:#100308;--gold:#C9A84C;--parchment:#F5E6C8;}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--deep);font-family:'IM Fell English',serif;color:var(--parchment);min-height:100vh;}
.bg{position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse 65% 55% at 20% 55%,rgba(107,30,46,.28),transparent 60%),linear-gradient(165deg,#060102,#100308);}
nav{position:fixed;top:0;left:0;right:0;z-index:100;display:flex;justify-content:space-between;align-items:center;padding:1rem 2.5rem;background:rgba(6,1,2,.92);border-bottom:1px solid rgba(201,168,76,.13);backdrop-filter:blur(14px);}
.logo{font-family:'Cinzel Decorative',cursive;font-size:.95rem;color:var(--gold);text-decoration:none;letter-spacing:2.5px;}
.nr{display:flex;align-items:center;gap:1.8rem;}
.nr a{font-family:'Cinzel',serif;font-size:.65rem;color:rgba(245,230,200,.55);text-decoration:none;letter-spacing:2.5px;text-transform:uppercase;transition:color .3s;}
.nr a:hover{color:var(--gold);}
.nu{font-family:'Cinzel',serif;font-size:.65rem;color:var(--gold);letter-spacing:2px;padding:.3rem .9rem;border:1px solid rgba(201,168,76,.25);border-radius:20px;}
.hdr{position:relative;z-index:10;text-align:center;padding:7.5rem 2rem 3rem;}
.hdr h1{font-family:'Cinzel Decorative',cursive;font-size:clamp(1.8rem,5vw,3.5rem);color:var(--gold);text-shadow:0 0 40px rgba(201,168,76,.28);margin-bottom:.7rem;}
.hdr p{font-style:italic;color:rgba(245,230,200,.52);font-size:1rem;max-width:520px;margin:0 auto;line-height:1.9;}
.rule{width:160px;height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent);margin:1.8rem auto;}
.grid{position:relative;z-index:10;display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:2rem;max-width:1060px;margin:0 auto;padding:1.5rem 2rem 5rem;}
.card{background:rgba(40,12,20,.88);border:1px solid rgba(201,168,76,.18);border-radius:11px;overflow:hidden;text-decoration:none;color:inherit;transition:all .4s cubic-bezier(.25,.8,.25,1);animation:rise .7s ease both;display:flex;flex-direction:column;}
.card:nth-child(1){animation-delay:.08s;}.card:nth-child(2){animation-delay:.18s;}.card:nth-child(3){animation-delay:.28s;}
.card:hover{transform:translateY(-8px);border-color:var(--gold);box-shadow:0 30px 70px rgba(0,0,0,.7),0 0 45px rgba(201,168,76,.12);}
.banner{height:150px;display:flex;align-items:center;justify-content:center;font-size:4.5rem;position:relative;}
.bicon{position:relative;z-index:1;transition:transform .4s;filter:drop-shadow(0 0 18px rgba(201,168,76,.45));}
.card:hover .bicon{transform:scale(1.18);}
.body{padding:1.8rem;}
.cnum{font-family:'Cinzel',serif;font-size:.6rem;letter-spacing:4px;color:var(--gold);opacity:.65;text-transform:uppercase;margin-bottom:.45rem;}
.ctitle{font-family:'Cinzel',serif;font-size:1.25rem;color:var(--gold);margin-bottom:.4rem;line-height:1.35;}
.csub{font-style:italic;color:rgba(245,230,200,.45);font-size:.82rem;margin-bottom:1.4rem;}
.facts{list-style:none;}
.facts li{font-size:.82rem;color:rgba(245,230,200,.62);padding:.3rem 0;border-bottom:1px solid rgba(201,168,76,.07);display:flex;gap:.5rem;align-items:flex-start;line-height:1.5;}
.facts li::before{content:'⚜';font-size:.6rem;color:var(--gold);opacity:.5;flex-shrink:0;margin-top:3px;}
.foot{margin-top:auto;padding:1.1rem 1.8rem;border-top:1px solid rgba(201,168,76,.12);display:flex;justify-content:space-between;align-items:center;}
.cta{font-family:'Cinzel',serif;font-size:.65rem;letter-spacing:2px;color:var(--gold);text-transform:uppercase;}
.arr{color:var(--gold);font-size:1.1rem;transition:transform .3s;}
.card:hover .arr{transform:translateX(6px);}
@keyframes rise{from{opacity:0;transform:translateY(28px)}to{opacity:1;transform:translateY(0)}}
</style></head><body><div class="bg"></div>
<nav><a href="/" class="logo">⚔ ZUCHINNI.AI</a>
<div class="nr"><span class="nu">{{ username }}</span><a href="/leaderboard">🏆 Hall of Fame</a><a href="/logout">Depart</a></div></nav>
<div class="hdr"><h1>The Chronicles of Kerala</h1><div class="rule"></div>
<p>"Choose your chapter, seeker. Each scroll holds the wisdom of a different age — from ancient spice empires to the dawn of modern Kerala."</p></div>
<div class="grid">
{% for id, ch in chapters.items() %}
<a href="/chat/{{ id }}" class="card">
  <div class="banner" style="background:linear-gradient(135deg,{{ ch.color }}25,{{ ch.color }}45);">
    <span class="bicon">{{ ch.icon }}</span></div>
  <div class="body">
    <div class="cnum">Chronicle {{ loop.index }}</div>
    <div class="ctitle">{{ ch.title.split(':')[1].strip() if ':' in ch.title else ch.title }}</div>
    <div class="csub">{{ ch.subtitle }}</div>
    <ul class="facts">{% for f in ch.key_facts[:4] %}<li>{{ f }}</li>{% endfor %}</ul>
  </div>
  <div class="foot"><span class="cta">Consult the Scrolls</span><span class="arr">→</span></div>
</a>{% endfor %}
</div></body></html>"""

CHAT_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ chapter.icon }} {{ chapter.title }} — Elarix</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Cinzel:wght@400;600&family=IM+Fell+English:ital@0;1&display=swap" rel="stylesheet">
<style>
:root{--maroon:#6B1E2E;--deep:#100308;--gold:#C9A84C;--gold2:#E8C97A;--parchment:#F5E6C8;--ch:{{ chapter.color }};}
*{margin:0;padding:0;box-sizing:border-box;}html,body{height:100%;overflow:hidden;}
body{background:var(--deep);font-family:'IM Fell English',serif;color:var(--parchment);display:flex;flex-direction:column;}
.bg{position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse 50% 60% at 8% 50%,rgba(107,30,46,.18),transparent 55%),radial-gradient(ellipse 40% 40% at 92% 15%,color-mix(in srgb,var(--ch) 12%,transparent),transparent 55%),linear-gradient(165deg,#060102,#100308);}
.topbar{position:relative;z-index:100;flex-shrink:0;display:flex;justify-content:space-between;align-items:center;padding:.75rem 1.5rem;background:rgba(5,1,2,.97);border-bottom:1px solid rgba(201,168,76,.16);}
.tbl{display:flex;align-items:center;gap:.9rem;}
.back{font-family:'Cinzel',serif;font-size:.62rem;color:rgba(245,230,200,.45);text-decoration:none;letter-spacing:2px;text-transform:uppercase;transition:color .3s;}
.back:hover{color:var(--gold);}
.badge{font-family:'Cinzel',serif;font-size:.62rem;letter-spacing:2px;text-transform:uppercase;color:var(--gold);background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.28);padding:.28rem .85rem;border-radius:20px;}
.tbc{font-family:'Cinzel Decorative',cursive;font-size:.9rem;color:var(--gold);letter-spacing:3px;}
.tbr{display:flex;align-items:center;gap:.7rem;}
.tbb{font-family:'Cinzel',serif;font-size:.62rem;letter-spacing:1.5px;text-transform:uppercase;padding:.38rem .95rem;border-radius:5px;cursor:pointer;transition:all .3s;border:1px solid;}
.gold-btn{background:rgba(201,168,76,.08);border-color:rgba(201,168,76,.35);color:var(--gold);}
.gold-btn:hover{background:rgba(201,168,76,.18);}
.dim-btn{background:rgba(107,30,46,.2);border-color:rgba(107,30,46,.5);color:rgba(245,230,200,.5);}
.dim-btn:hover{border-color:var(--maroon);color:var(--parchment);}
.tu{font-family:'Cinzel',serif;font-size:.6rem;color:rgba(245,230,200,.35);letter-spacing:1px;}
.main{display:flex;flex:1;overflow:hidden;position:relative;z-index:10;}
.sidebar{width:255px;flex-shrink:0;background:rgba(10,3,6,.95);border-right:1px solid rgba(201,168,76,.12);display:flex;flex-direction:column;overflow-y:auto;}
.sidebar::-webkit-scrollbar{width:3px;}.sidebar::-webkit-scrollbar-thumb{background:rgba(201,168,76,.18);}
.sb{padding:1.2rem;border-bottom:1px solid rgba(201,168,76,.08);}
.sbh{font-family:'Cinzel',serif;font-size:.58rem;letter-spacing:3px;text-transform:uppercase;color:rgba(201,168,76,.55);margin-bottom:.9rem;}
.fl{list-style:none;}
.fl li{font-size:.8rem;color:rgba(245,230,200,.6);padding:.4rem 0;border-bottom:1px solid rgba(201,168,76,.05);display:flex;gap:.45rem;align-items:flex-start;line-height:1.55;}
.fl li::before{content:'⚜';font-size:.55rem;color:var(--gold);opacity:.45;flex-shrink:0;margin-top:3px;}
.sug{font-size:.78rem;color:rgba(245,230,200,.55);padding:.48rem .75rem;border-radius:5px;border:1px solid rgba(201,168,76,.1);margin-bottom:.35rem;cursor:pointer;transition:all .3s;font-style:italic;}
.sug:hover{background:rgba(201,168,76,.07);border-color:rgba(201,168,76,.3);color:var(--parchment);}
.chat-area{flex:1;display:flex;flex-direction:column;overflow:hidden;}
.messages{flex:1;overflow-y:auto;padding:1.4rem;display:flex;flex-direction:column;gap:1.1rem;}
.messages::-webkit-scrollbar{width:3px;}.messages::-webkit-scrollbar-thumb{background:rgba(201,168,76,.18);}
.msg{display:flex;gap:.75rem;animation:msgIn .3s ease both;}
.msg.user{flex-direction:row-reverse;}
@keyframes msgIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.av{width:34px;height:34px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:.95rem;border:1px solid rgba(201,168,76,.28);}
.msg.elarix .av{background:linear-gradient(135deg,#3D0D1A,var(--maroon));}
.msg.user .av{background:rgba(201,168,76,.1);}
.bub{max-width:73%;padding:.9rem 1.1rem;border-radius:8px;font-size:.93rem;line-height:1.85;}
.msg.elarix .bub{background:rgba(22,6,12,.95);border:1px solid rgba(201,168,76,.13);border-top-left-radius:2px;}
.msg.user .bub{background:rgba(107,30,46,.35);border:1px solid rgba(107,30,46,.55);border-top-right-radius:2px;text-align:right;}
.mn{font-family:'Cinzel',serif;font-size:.58rem;letter-spacing:2px;text-transform:uppercase;color:var(--gold);opacity:.65;margin-bottom:.35rem;}
.msg.user .mn{text-align:right;}
.mt{color:rgba(245,230,200,.87);}
.mt strong{color:var(--gold2);}.mt em{color:rgba(245,230,200,.6);}
.typing{display:flex;align-items:center;gap:5px;padding:.5rem .8rem;}
.typing span{width:6px;height:6px;border-radius:50%;background:var(--gold);opacity:.35;animation:pulse 1.1s ease infinite;}
.typing span:nth-child(2){animation-delay:.18s;}.typing span:nth-child(3){animation-delay:.36s;}
@keyframes pulse{0%,100%{opacity:.2;transform:scale(.8)}50%{opacity:.85;transform:scale(1.15)}}
.ibar{padding:.9rem 1.4rem;background:rgba(6,1,3,.97);border-top:1px solid rgba(201,168,76,.13);display:flex;gap:.75rem;align-items:flex-end;flex-shrink:0;}
#mi{flex:1;background:rgba(18,5,10,.85);border:1px solid rgba(201,168,76,.2);border-radius:8px;color:var(--parchment);font-family:'IM Fell English',serif;font-size:.93rem;padding:.75rem 1rem;resize:none;outline:none;transition:border .3s;min-height:42px;max-height:110px;line-height:1.6;}
#mi:focus{border-color:rgba(201,168,76,.48);}
#mi::placeholder{color:rgba(245,230,200,.18);font-style:italic;}
.sbtn{padding:.75rem 1.4rem;font-family:'Cinzel',serif;font-size:.72rem;letter-spacing:2px;text-transform:uppercase;background:linear-gradient(135deg,var(--maroon),#3D0D1A);border:1px solid rgba(201,168,76,.38);border-radius:8px;color:var(--gold);cursor:pointer;transition:all .3s;flex-shrink:0;}
.sbtn:hover{box-shadow:0 0 22px rgba(201,168,76,.2);border-color:var(--gold);}
.sbtn:disabled{opacity:.38;cursor:not-allowed;}
/* bubble overlay */
.ov{position:fixed;inset:0;z-index:500;background:rgba(4,1,2,.93);backdrop-filter:blur(14px);display:none;flex-direction:column;align-items:center;justify-content:center;gap:1.8rem;}
.ov.on{display:flex;}
.ovt{font-family:'Cinzel Decorative',cursive;font-size:2rem;color:var(--gold);text-align:center;}
.ovd{font-style:italic;color:rgba(245,230,200,.55);text-align:center;max-width:420px;line-height:1.9;font-size:.95rem;}
.bgrid{display:grid;grid-template-columns:repeat(5,1fr);gap:1rem;}
.bb{width:68px;height:68px;border-radius:50%;background:radial-gradient(circle at 35% 35%,rgba(201,168,76,.55),rgba(107,30,46,.25));border:2px solid rgba(201,168,76,.45);font-size:1.9rem;cursor:pointer;transition:all .25s;display:flex;align-items:center;justify-content:center;animation:fl 2.2s ease-in-out infinite;}
.bb:nth-child(2){animation-delay:.35s;}.bb:nth-child(3){animation-delay:.7s;}.bb:nth-child(4){animation-delay:1.05s;}.bb:nth-child(5){animation-delay:1.4s;}
.bb:hover{transform:scale(1.15);}
.bb.popped{background:rgba(201,168,76,.06);border-style:dashed;opacity:.3;cursor:default;animation:none;}
@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
.bp{font-family:'Cinzel',serif;font-size:.75rem;letter-spacing:2px;color:rgba(245,230,200,.45);}
/* quiz modal */
.mo{position:fixed;inset:0;z-index:500;background:rgba(4,1,2,.93);backdrop-filter:blur(14px);display:none;align-items:center;justify-content:center;padding:1rem;}
.mo.on{display:flex;}
.md{background:rgba(22,6,12,.98);border:1px solid rgba(201,168,76,.28);border-radius:13px;padding:2.5rem;max-width:500px;width:100%;box-shadow:0 50px 100px rgba(0,0,0,.75);}
.mdt{font-family:'Cinzel Decorative',cursive;font-size:1.45rem;color:var(--gold);text-align:center;margin-bottom:.4rem;}
.mds{text-align:center;font-style:italic;color:rgba(245,230,200,.42);margin-bottom:1.6rem;font-size:.85rem;}
.pb{height:3px;background:rgba(201,168,76,.1);border-radius:2px;margin-bottom:1.6rem;overflow:hidden;}
.pf{height:100%;background:var(--gold);border-radius:2px;transition:width .5s ease;}
.mq{font-size:1.05rem;line-height:1.75;color:var(--parchment);margin-bottom:.4rem;}
.mh{font-size:.78rem;color:rgba(201,168,76,.45);font-style:italic;margin-bottom:1.4rem;}
.mi{width:100%;padding:.8rem 1rem;background:rgba(8,2,5,.75);border:1px solid rgba(201,168,76,.22);border-radius:7px;color:var(--parchment);font-family:'IM Fell English',serif;font-size:.98rem;outline:none;margin-bottom:1rem;transition:border .3s;}
.mi:focus{border-color:rgba(201,168,76,.5);}
.mbs{display:flex;gap:.9rem;}
.mb{flex:1;padding:.8rem;font-family:'Cinzel',serif;font-size:.72rem;letter-spacing:2px;text-transform:uppercase;border-radius:7px;cursor:pointer;transition:all .3s;}
.mbp{background:linear-gradient(135deg,var(--maroon),#3D0D1A);border:1px solid var(--gold);color:var(--gold);}
.mbp:hover{box-shadow:0 0 22px rgba(201,168,76,.22);}
.mbg{background:transparent;border:1px solid rgba(245,230,200,.18);color:rgba(245,230,200,.45);}
.mr{text-align:center;padding:1.3rem;border-radius:8px;margin-bottom:1rem;font-size:.95rem;}
.ok{background:rgba(40,120,40,.15);border:1px solid rgba(80,180,80,.25);color:#90ee90;}
.bad{background:rgba(130,40,40,.15);border:1px solid rgba(180,80,80,.25);color:#ffaaaa;}
.mf{text-align:center;padding:1.5rem 0;}
.mfi{font-size:3rem;margin-bottom:1rem;}
.mft{font-size:1rem;line-height:1.75;color:rgba(245,230,200,.82);}
</style></head><body><div class="bg"></div>
<div class="topbar">
  <div class="tbl"><a href="/chapters" class="back">← Chronicles</a><span class="badge">{{ chapter.icon }} {{ chapter.title.split(':')[0] }}</span></div>
  <div class="tbc">ELARIX</div>
  <div class="tbr">
    <button class="tbb gold-btn" onclick="openQuiz()">📜 Quiz</button>
    <a href="/leaderboard" style="text-decoration:none"><button class="tbb gold-btn">🏆</button></a>
    <button class="tbb dim-btn" onclick="clearChat()">✕ Clear</button>
    <span class="tu">{{ username }}</span>
    <a href="/logout" style="text-decoration:none"><button class="tbb dim-btn">Leave</button></a>
  </div>
</div>
<div class="main">
  <div class="sidebar">
    <div class="sb"><div class="sbh">Key Facts</div>
      <ul class="fl">{% for f in chapter.key_facts %}<li>{{ f }}</li>{% endfor %}</ul>
    </div>
    <div style="padding:1.2rem;text-align:center;border-bottom:1px solid rgba(201,168,76,.08);">
      <img id="mascot-img" src="/mascot/normal" alt="Elarix"
        style="width:170px;border-radius:8px;transition:opacity 0.2s ease,transform 0.2s ease;filter:drop-shadow(0 0 12px rgba(201,168,76,.3));">
      <div id="mascot-caption" style="font-family:'Cinzel',serif;font-size:.6rem;letter-spacing:2px;color:rgba(201,168,76,.5);margin-top:.6rem;text-transform:uppercase;">Awaiting your question...</div>
    </div>
    <div class="sb"><div class="sbh">Try asking…</div>
      {% set sugs = ["Who were the Chera kings?","Tell me about the spice trade","What is Kalaripayattu?","Who was Vasco da Gama?","Tell me about the Battle of Colachel","What was the Temple Entry Proclamation?","Tell me about Kathakali","Who were the Kunjali Marakkars?","Tell me about slavery reform","When did Kerala gain independence?"] %}
      {% for s in sugs[:6] %}<div class="sug" onclick="fillSend('{{ s }}')">{{ s }}</div>{% endfor %}
    </div>
  </div>
  <div class="chat-area">
    <div class="messages" id="msgs">
      <div class="msg elarix"><div class="av">⚔</div>
        <div><div class="mn">Elarix · The Archivist</div>
          <div class="bub"><div class="mt">
            <em>*The great iron-bound tome opens with a resonant thud. Candlelight flickers across ancient parchment...*</em><br><br>
            Greetings, <strong>{{ username }}</strong>. You have entered the scrolls of <strong>{{ chapter.title }}</strong>.<br><br>
            I am Elarix — keeper of Kerala's chronicles. Ask me anything about the people, rulers, events, trade, culture, or battles of this era.<br><br>
            <strong>⚠ Remember:</strong> Three transgressions of tongue shall cast you into the dungeon!
          </div></div></div>
      </div>
    </div>
    <div class="ibar">
      <textarea id="mi" placeholder="Ask Elarix about {{ chapter.title }}…" onkeydown="hk(event)" oninput="rs(this)" rows="1"></textarea>
      <button class="sbtn" id="sb" onclick="send()">Ask ⚔</button>
    </div>
  </div>
</div>
<!-- Bubble overlay -->
<div class="ov" id="bov">
  <div class="ovt">🫧 The Bubble Challenge</div>
  <div class="ovd">Pop all 5 enchanted bubbles to lift the dungeon's curse!</div>
  <div class="bgrid">
    <div class="bb" onclick="pop(this)">🫧</div><div class="bb" onclick="pop(this)">🫧</div>
    <div class="bb" onclick="pop(this)">🫧</div><div class="bb" onclick="pop(this)">🫧</div>
    <div class="bb" onclick="pop(this)">🫧</div>
  </div>
  <div class="bp" id="bp">0 / 5 bubbles popped</div>
</div>
<!-- Quiz modal -->
<div class="mo" id="qm">
  <div class="md">
    <div class="mdt">📜 The Scholar's Trial</div>
    <div class="mds" id="qpt">Question 1 of 3</div>
    <div class="pb"><div class="pf" id="qpb" style="width:0%"></div></div>
    <div id="qbody">
      <div class="mq" id="qq"></div><div class="mh" id="qh"></div>
      <input class="mi" id="qa" placeholder="Your answer, scholar…" onkeydown="e=>{if(e.key==='Enter')sa();}">
      <div class="mbs"><button class="mb mbp" onclick="sa()">⚔ Submit</button><button class="mb mbg" onclick="cq()">← Close</button></div>
    </div>
    <div id="qres" style="display:none">
      <div class="mr" id="rb"></div>
      <div class="mbs"><button class="mb mbp" id="nb">Next →</button></div>
    </div>
    <div id="qfin" style="display:none" class="mf">
      <div class="mfi" id="fi"></div><div class="mft" id="ft"></div>
      <div class="mbs" style="margin-top:1.5rem"><button class="mb mbp" onclick="cq()">Return to Archives</button></div>
    </div>
  </div>
</div>
<script>
const CH="{{chapter_id}}",UN="{{username}}";
let loading=false,qi=0,qt=0;

// ── MASCOT ──
function setMascot(expr, caption){
  var img=document.getElementById('mascot-img');
  var cap=document.getElementById('mascot-caption');
  if(!img) return;
  img.style.opacity='0';
  img.style.transform='scale(0.92)';
  setTimeout(function(){
    img.src='/mascot/'+expr+'?t='+Date.now();
    if(cap) cap.textContent=caption;
    img.style.opacity='1';
    img.style.transform='scale(1)';
  },200);
}

// ── INPUT HELPERS ──
function hk(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}}
function rs(el){el.style.height='auto';el.style.height=Math.min(el.scrollHeight,110)+'px';}
function fillSend(t){document.getElementById('mi').value=t;send();}

// ── SEND MESSAGE ──
async function send(){
  var inp=document.getElementById('mi');
  var txt=inp.value.trim();
  if(!txt||loading) return;
  addMsg('user',txt);
  inp.value='';
  inp.style.height='auto';
  loading=true;
  document.getElementById('sb').disabled=true;
  setMascot('thinking','Consulting the scrolls...');
  var tid=addTyping();
  try{
    var r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:txt,chapter:CH})});
    var d=await r.json();
    removeTyping(tid);
    if(d.type==='bubble'){
      showBubbles();
      setMascot('happy','Pop the bubbles!');
    } else if(d.type==='warning'){
      setMascot('angry','Watch your tongue!');
      addMsg('elarix',d.message);
    } else if(d.type==='dungeon_start'){
      setMascot('shocked','To the dungeon!');
      addMsg('elarix',d.message);
    } else if(d.type==='riddle_correct'){
      setMascot('happy','Well done, scholar!');
      addMsg('elarix',d.message);
    } else if(d.type==='dungeon'){
      setMascot('shocked','Solve the riddle!');
      addMsg('elarix',d.message);
    } else {
      setMascot('normal','Ask me anything...');
      addMsg('elarix',d.message);
    }
  } catch(err){
    removeTyping(tid);
    setMascot('sad','Something went wrong...');
    addMsg('elarix','The scrolls are unreachable. Try again.');
  }
  loading=false;
  document.getElementById('sb').disabled=false;
}

// ── MESSAGES ──
function addMsg(role,text){
  var c=document.getElementById('msgs');
  var d=document.createElement('div');
  d.className='msg '+role;
  var isE=(role==='elarix');
  d.innerHTML='<div class="av">'+(isE?'⚔':UN[0].toUpperCase())+'</div><div><div class="mn">'+(isE?'Elarix · The Archivist':UN)+'</div><div class="bub"><div class="mt">'+fmt(text)+'</div></div></div>';
  c.appendChild(d);
  c.scrollTop=c.scrollHeight;
}
function fmt(t){
  t = t.replace(/[*][*]([^*]+)[*][*]/g,'<strong>$1</strong>');
  t = t.replace(/[*]([^*]+)[*]/g,'<em>$1</em>');
  t = t.replace(/\n/g,'<br>');
  return t;
}
function addTyping(){
  var id='t'+Date.now();
  var c=document.getElementById('msgs');
  var d=document.createElement('div');
  d.className='msg elarix';
  d.id=id;
  d.innerHTML='<div class="av">⚔</div><div class="bub"><div class="typing"><span></span><span></span><span></span></div></div>';
  c.appendChild(d);
  c.scrollTop=c.scrollHeight;
  return id;
}
function removeTyping(id){var e=document.getElementById(id);if(e)e.remove();}
function clearChat(){document.getElementById('msgs').innerHTML='';addMsg('elarix','The scrolls are cleared. A fresh chapter begins. What would you ask, seeker?');}

// ── BUBBLES ──
function showBubbles(){
  document.querySelectorAll('.bb').forEach(function(b){b.classList.remove('popped');b.textContent='🫧';});
  document.getElementById('bp').textContent='0 / 5 bubbles popped';
  document.getElementById('bov').classList.add('on');
}
async function pop(btn){
  if(btn.classList.contains('popped')) return;
  btn.classList.add('popped');
  btn.textContent='💨';
  var r=await fetch('/api/bubble',{method:'POST',headers:{'Content-Type':'application/json'}});
  var d=await r.json();
  document.getElementById('bp').textContent=d.score+' / 5 bubbles popped';
  if(d.done){
    setTimeout(function(){
      document.getElementById('bov').classList.remove('on');
      setMascot('happy','Freedom at last!');
      addMsg('elarix',d.message);
    },700);
  }
}

// ── QUIZ ──
async function openQuiz(){
  var r=await fetch('/api/quiz/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({chapter:CH})});
  var d=await r.json();
  if(d.error){alert(d.error);return;}
  qi=0; qt=d.total;
  setQ(d.question,d.hint,0,d.total);
  document.getElementById('qbody').style.display='block';
  document.getElementById('qres').style.display='none';
  document.getElementById('qfin').style.display='none';
  document.getElementById('qm').classList.add('on');
}
function setQ(q,hint,idx,total){
  document.getElementById('qq').textContent=q;
  document.getElementById('qh').textContent='Hint: '+hint;
  document.getElementById('qpt').textContent='Question '+(idx+1)+' of '+total;
  document.getElementById('qpb').style.width=((idx/total)*100)+'%';
  document.getElementById('qa').value='';
  setTimeout(function(){document.getElementById('qa').focus();},100);
}
async function sa(){
  var ans=document.getElementById('qa').value.trim();
  if(!ans) return;
  var r=await fetch('/api/quiz',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({chapter:CH,answer:ans,q_index:qi})});
  var d=await r.json();
  document.getElementById('qbody').style.display='none';
  document.getElementById('qres').style.display='block';
  var rb=document.getElementById('rb');
  rb.className=d.correct?'mr ok':'mr bad';
  rb.textContent=d.correct?'Correct! The ancient scrolls confirm your wisdom.':'Not quite, scholar. The scrolls tell a different story.';
  document.getElementById('qpb').style.width=(((qi+1)/qt)*100)+'%';
  var nb=document.getElementById('nb');
  if(d.done){
    nb.textContent='See Results';
    nb.onclick=function(){showFin(d.final_score,d.total);};
  } else {
    qi++;
    nb.textContent='Next Question';
    nb.onclick=function(){
      setQ(d.next_q.q,d.next_q.hint,qi,qt);
      document.getElementById('qbody').style.display='block';
      document.getElementById('qres').style.display='none';
    };
  }
}
function showFin(score,total){
  document.getElementById('qres').style.display='none';
  document.getElementById('qfin').style.display='block';
  document.getElementById('qpb').style.width='100%';
  var p=score/total;
  if(p===1){ setMascot('happy','Perfect score!'); }
  else if(p>=0.6){ setMascot('happy','Well done!'); }
  else { setMascot('sad','Study more, seeker...'); }
  document.getElementById('fi').textContent=p===1?'🏆':p>=0.6?'📜':'📚';
  document.getElementById('ft').textContent=p===1?'Perfect — '+score+'/'+total+'! You are a true Master of the Chronicles!':p>=0.6?'Well done — '+score+'/'+total+'. A fine scholar of Kerala\'s history.':score+'/'+total+'. Return to the scrolls and study further, seeker.';
}
function cq(){document.getElementById('qm').classList.remove('on');}
document.getElementById('mi').focus();
</script></body></html>"""

LEADERBOARD_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scrolls of Fame — Elarix</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Cinzel:wght@400;600&family=IM+Fell+English:ital@0;1&display=swap" rel="stylesheet">
<style>
:root{--maroon:#6B1E2E;--deep:#100308;--gold:#C9A84C;--parchment:#F5E6C8;}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--deep);font-family:'IM Fell English',serif;color:var(--parchment);min-height:100vh;}
.bg{position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse 60% 50% at 50% 0%,rgba(107,30,46,.22),transparent 60%),linear-gradient(170deg,#060102,#100308);}
nav{position:fixed;top:0;left:0;right:0;z-index:100;display:flex;justify-content:space-between;align-items:center;padding:1rem 2.5rem;background:rgba(5,1,2,.94);border-bottom:1px solid rgba(201,168,76,.12);backdrop-filter:blur(14px);}
.logo{font-family:'Cinzel Decorative',cursive;font-size:.95rem;color:var(--gold);text-decoration:none;letter-spacing:2.5px;}
nav a:not(.logo){font-family:'Cinzel',serif;font-size:.65rem;color:rgba(245,230,200,.5);text-decoration:none;letter-spacing:2.5px;text-transform:uppercase;margin-left:1.8rem;transition:color .3s;}
nav a:not(.logo):hover{color:var(--gold);}
.page{position:relative;z-index:10;max-width:780px;margin:0 auto;padding:7rem 1.5rem 4rem;}
h1{font-family:'Cinzel Decorative',cursive;font-size:clamp(1.8rem,5vw,3.2rem);color:var(--gold);text-align:center;text-shadow:0 0 40px rgba(201,168,76,.28);margin-bottom:.5rem;}
.sub{text-align:center;font-style:italic;color:rgba(245,230,200,.45);margin-bottom:2.8rem;line-height:1.85;}
.rule{width:150px;height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent);margin:0 auto 2.5rem;}
.tw{background:rgba(38,10,18,.9);border:1px solid rgba(201,168,76,.18);border-radius:11px;overflow:hidden;box-shadow:0 35px 70px rgba(0,0,0,.55);}
.th{display:grid;grid-template-columns:55px 1fr 1fr 65px 130px;gap:1rem;padding:.75rem 1.5rem;background:rgba(201,168,76,.07);border-bottom:1px solid rgba(201,168,76,.14);}
.th span{font-family:'Cinzel',serif;font-size:.58rem;letter-spacing:3px;text-transform:uppercase;color:rgba(201,168,76,.55);}
.tr{display:grid;grid-template-columns:55px 1fr 1fr 65px 130px;gap:1rem;padding:.95rem 1.5rem;border-bottom:1px solid rgba(201,168,76,.06);align-items:center;transition:background .25s;animation:ri .4s ease both;}
.tr:last-child{border-bottom:none;}.tr:hover{background:rgba(201,168,76,.04);}
@keyframes ri{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}
.rk{font-family:'Cinzel Decorative',cursive;font-size:1.05rem;text-align:center;}
.r1{color:#FFD700;text-shadow:0 0 14px rgba(255,215,0,.45);}.r2{color:#C0C0C0;}.r3{color:#CD7F32;}.rn{color:rgba(245,230,200,.28);}
.un{font-family:'Cinzel',serif;font-size:.82rem;color:var(--parchment);}
.un.me{color:var(--gold);}
.cn{font-size:.78rem;color:rgba(245,230,200,.45);font-style:italic;}
.sc{font-family:'Cinzel Decorative',cursive;font-size:1.1rem;color:var(--gold);text-align:center;}
.dt{font-size:.72rem;color:rgba(245,230,200,.3);font-family:'Cinzel',serif;}
.empty{text-align:center;padding:3rem;font-style:italic;color:rgba(245,230,200,.38);line-height:2;}
.cta{text-align:center;margin-top:2.5rem;}
.cta a{font-family:'Cinzel',serif;font-size:.72rem;letter-spacing:3px;text-transform:uppercase;color:var(--gold);text-decoration:none;padding:.8rem 2rem;border:1px solid rgba(201,168,76,.28);border-radius:6px;transition:all .3s;}
.cta a:hover{background:rgba(201,168,76,.07);border-color:var(--gold);}
</style></head><body><div class="bg"></div>
<nav><a href="/chapters" class="logo">⚔ ZUCHINNI.AI</a><div><a href="/chapters">Chronicles</a><a href="/logout">Depart</a></div></nav>
<div class="page">
  <h1>🏆 Scrolls of Fame</h1><div class="rule"></div>
  <p class="sub">"The scholars who have proven their mastery of Kerala's ancient chronicles — ranked for all eternity."</p>
  <div class="tw">
    {% if scores %}
    <div class="th"><span>Rank</span><span>Scholar</span><span>Chronicle</span><span>Score</span><span>Date</span></div>
    {% for e in scores %}
    <div class="tr" style="animation-delay:{{ loop.index0 * 0.04 }}s">
      <div class="rk {% if loop.index==1 %}r1{% elif loop.index==2 %}r2{% elif loop.index==3 %}r3{% else %}rn{% endif %}">
        {% if loop.index==1 %}👑{% elif loop.index==2 %}⚔{% elif loop.index==3 %}📜{% else %}{{ loop.index }}{% endif %}
      </div>
      <div class="un {% if e.username==username %}me{% endif %}">{{ e.username }}{% if e.username==username %} ✦{% endif %}</div>
      <div class="cn">{{ e.chapter[:32] }}{% if e.chapter|length > 32 %}…{% endif %}</div>
      <div class="sc">{{ e.score }}/3</div>
      <div class="dt">{{ e.date }}</div>
    </div>{% endfor %}
    {% else %}<div class="empty">⚜ The Scrolls of Fame await their first scholar…<br>Complete a chapter quiz to claim your immortal place!</div>
    {% endif %}
  </div>
  <div class="cta"><a href="/chapters">← Return to the Chronicles</a></div>
</div></body></html>"""

# ─────────────────────────────────────────
# ROUTES — AUTH
# ─────────────────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("chapters")) if "username" in session else render_template_string(LANDING_HTML)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        d = request.get_json()
        users = get_users()
        u, pw = d.get("username","").strip(), hash_pw(d.get("password",""))
        if u in users and users[u]["password"] == pw:
            session["username"] = u; init_session()
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Invalid name or passphrase"})
    return render_template_string(AUTH_HTML, mode="login")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        d = request.get_json()
        users = get_users()
        u, pw = d.get("username","").strip(), d.get("password","")
        if not u or len(pw) < 4:
            return jsonify({"success": False, "error": "Name required & passphrase min 4 chars"})
        if u in users:
            return jsonify({"success": False, "error": "That name is already taken"})
        users[u] = {"password": hash_pw(pw), "joined": datetime.now().isoformat()}
        save_users(users)
        session["username"] = u; init_session()
        return jsonify({"success": True})
    return render_template_string(AUTH_HTML, mode="signup")

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("index"))

# ─────────────────────────────────────────
# ROUTES — PAGES
# ─────────────────────────────────────────
@app.route("/chapters")
def chapters():
    if "username" not in session: return redirect(url_for("index"))
    return render_template_string(CHAPTERS_HTML, chapters=KNOWLEDGE, username=session["username"])

@app.route("/chat/<chapter_id>")
def chat(chapter_id):
    if "username" not in session: return redirect(url_for("index"))
    if chapter_id not in KNOWLEDGE: return redirect(url_for("chapters"))
    return render_template_string(CHAT_HTML, chapter_id=chapter_id,
        chapter=KNOWLEDGE[chapter_id], username=session["username"])

@app.route("/leaderboard")
def leaderboard():
    if "username" not in session: return redirect(url_for("index"))
    return render_template_string(LEADERBOARD_HTML, scores=get_scores(), username=session["username"])

# ─────────────────────────────────────────
# API — CHAT
# ─────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def api_chat():
    if "username" not in session: return jsonify({"error":"Not logged in"}), 401
    init_session()
    d = request.get_json()
    message = d.get("message","").strip()
    chapter = d.get("chapter","")
    now, name = time.time(), session["username"]

    if session["bubble_mode"]:
        return jsonify({"type":"bubble","message":"🫧 Pop all the bubbles first using the button overlay!"})

    if session["dungeon"]:
        if now < session["dungeon_until"]:
            rem = int(session["dungeon_until"] - now)
            return jsonify({"type":"dungeon","message":f"⛓️ *The chains hold firm...* Imprisoned for **{rem}** more seconds.\n\n🕯️ **{session['riddle']['q']}**\n\n*Hint: {session['riddle']['hint']}*"})
        riddle = session["riddle"]
        if riddle and any(a in message.lower() for a in riddle["a"]):
            session["dungeon"] = False; session["bubble_mode"] = True; session["bubble_score"] = 0; session.modified = True
            return jsonify({"type":"riddle_correct","message":"🧩 **The answer rings true!** The dungeon doors groan open...\n\nNow pop **5 enchanted bubbles** to lift the curse completely! 🫧"})
        return jsonify({"type":"dungeon","message":f"⛓️ *Elarix shakes his head...*\n\nThat is not the answer the dungeon demands.\n\n🕯️ **{riddle['q']}**\n\n*Hint: {riddle['hint']}*"})

    if profanity.contains_profanity(message):
        session["anger"] += 1; session.modified = True
        if session["anger"] >= 3:
            riddle = random.choice(RIDDLES)
            session["dungeon"] = True; session["dungeon_until"] = now + 20
            session["riddle"] = riddle; session.modified = True
            return jsonify({"type":"dungeon_start","message":f"⚔️ **ENOUGH!** Three times you have brought foulness into the sacred archives!\n\n*Elarix slams his tome shut with a thunderous crash...*\n\n🏰 **You are cast into the DUNGEON for 20 seconds!**\n\n🕯️ Ponder this riddle:\n\n**{riddle['q']}**\n\n*Hint: {riddle['hint']}*"})
        w = 3 - session["anger"]
        return jsonify({"type":"warning","message":f"⚠️ *Elarix's eye twitches with displeasure...*\n\nMind your tongue in these sacred halls. **{w}** warning(s) remain."})

    lo = message.lower()
    if lo in ["hi","hello","hey","greetings","namaste","good day"]:
        return jsonify({"type":"answer","message":random.choice([
            f"*The great iron-bound tome opens with a resonant thud...*\n\nAh, **{name}**. I am **Elarix**, keeper of Kerala's chronicles. Ask me anything about this chapter — the scrolls hold many secrets!",
            f"*Elarix looks up from a crumbling parchment...*\n\nWell met, **{name}**. The archives await your questions. What would you know about this era of Kerala's glorious history?"
        ])})

    answer = search(message, chapter)
    if answer:
        return jsonify({"type":"answer","message":answer})

    return jsonify({"type":"answer","message":random.choice([
        "*Elarix frowns and runs a finger along several shelves...*\n\nHmm. The scrolls do not speak clearly on that. Try asking about the **rulers, trade, culture, battles, or key events** of this chapter.",
        "*The archivist shakes his head slowly...*\n\nI cannot find that in today's scrolls, seeker. Ask about a specific **person, event, date, or practice** from this era.",
    ])})

# ─────────────────────────────────────────
# API — BUBBLE
# ─────────────────────────────────────────
@app.route("/api/bubble", methods=["POST"])
def api_bubble():
    if "username" not in session: return jsonify({"error":"Not logged in"}), 401
    if not session.get("bubble_mode"): return jsonify({"message":"No challenge active.","done":False,"score":0})
    session["bubble_score"] += 1; session.modified = True
    score = session["bubble_score"]
    if score >= 5:
        session["bubble_mode"] = False; session["bubble_score"] = 0; session["anger"] = 0; session.modified = True
        return jsonify({"message":"🎉 **All bubbles vanquished!** You are FREE! The dungeon's curse is lifted. Speak wisely henceforth, traveller.","done":True,"score":5})
    return jsonify({"message":f"🫧 Bubble {score}/5 popped! {5-score} more to freedom!","done":False,"score":score})

# ─────────────────────────────────────────
# API — QUIZ
# ─────────────────────────────────────────
@app.route("/api/quiz/start", methods=["POST"])
def quiz_start():
    if "username" not in session: return jsonify({"error":"Not logged in"}), 401
    d = request.get_json(); cid = d.get("chapter","")
    if cid not in KNOWLEDGE: return jsonify({"error":"Chapter not found"}), 404
    session["quiz_score"] = 0; session.modified = True
    q = KNOWLEDGE[cid]["quiz"][0]
    return jsonify({"question":q["q"],"hint":q["hint"],"q_index":0,"total":len(KNOWLEDGE[cid]["quiz"])})

@app.route("/api/quiz", methods=["POST"])
def quiz_answer():
    if "username" not in session: return jsonify({"error":"Not logged in"}), 401
    d = request.get_json()
    cid, answer, qi = d.get("chapter",""), d.get("answer","").lower().strip(), d.get("q_index",0)
    if cid not in KNOWLEDGE: return jsonify({"error":"Not found"}), 404
    qs = KNOWLEDGE[cid]["quiz"]
    correct = any(a in answer or answer in a for a in qs[qi]["a"])
    if correct: session["quiz_score"] = session.get("quiz_score",0) + 1; session.modified = True
    if qi == len(qs) - 1:
        record_score(session["username"], session["quiz_score"], cid)
        return jsonify({"correct":correct,"done":True,"final_score":session["quiz_score"],"total":len(qs)})
    nq = qs[qi+1]
    return jsonify({"correct":correct,"done":False,"next_q":{"q":nq["q"],"hint":nq["hint"]}})

# ─────────────────────────────────────────
# MASCOT ROUTE
# ─────────────────────────────────────────
@app.route("/mascot/<expression>")
def mascot(expression):
    allowed = ["normal","happy","angry","shocked","thinking","sad"]
    name = f"mascot_{expression}.png" if expression in allowed else "mascot_normal.png"
    folder = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(folder, name)):
        # fallback: try mascot.png, then return 404
        if os.path.exists(os.path.join(folder, "mascot.png")):
            return send_from_directory(folder, "mascot.png")
        return "", 404
    return send_from_directory(folder, name)

# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n⚔ ELARIX — The Medieval Archivist")
    print("📜 Run: pip install flask better-profanity")
    print("🌐 Then open: http://localhost:5000\n")
    app.run(debug=True, port=5000)
