"""
ELARIX - The Medieval Archivist
ZUCHINNI.AI - MYP Design Project

HOW TO RUN:
1. pip install flask better-profanity
2. python app.py
3. Open http://localhost:5000

MASCOT IMAGES (put in same folder as this file):
  mascot_normal.png   mascot_thinking.png  mascot_happy.png
  mascot_angry.png    mascot_shocked.png   mascot_sad.png
"""

import os, json, random, time, hashlib, urllib.request, urllib.parse
from datetime import datetime
from flask import (Flask, render_template_string, request,
                   jsonify, session, redirect, url_for, send_from_directory)
from better_profanity import profanity

profanity.load_censor_words()
app = Flask(__name__)
app.secret_key = "elarix-medieval-2024"
# ── DATA HELPERS ─────────────────────────────────────────────
# Use /tmp for Render compatibility (writable on all platforms)
DATA_DIR = "/tmp/elarix_data" if os.path.exists("/tmp") else "data"
os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f: json.dump(data, f, indent=2)

def get_users():   return load_json(os.path.join(DATA_DIR, "users.json"), {})
def save_users(u): save_json(os.path.join(DATA_DIR, "users.json"), u)
def get_scores():  return load_json(os.path.join(DATA_DIR, "scores.json"), [])
def hash_pw(pw):   return hashlib.sha256(pw.encode()).hexdigest()

def record_score(username, score, chapter_id):
    scores = get_scores()
    scores.append({"username": username, "score": score,
                   "chapter": KNOWLEDGE.get(chapter_id, {}).get("title", chapter_id),
                   "date": datetime.now().strftime("%Y-%m-%d %H:%M")})
    save_json(os.path.join(DATA_DIR, "scores.json"), sorted(scores, key=lambda x: x["score"], reverse=True)[:50])

def init_session():
    for k, v in [("anger",0),("dungeon",False),("dungeon_until",0),("riddle",None),
                 ("bubble_mode",False),("bubble_score",0),("quiz_score",0),("irrelevant",0)]:
        session.setdefault(k, v)

# ── KNOWLEDGE BASE ───────────────────────────────────────────
KNOWLEDGE = {
    "chapter-1": {
        "title": "Chapter I: The Golden Age",
        "subtitle": "Dynasties and Early Kerala",
        "icon": "👑", "color": "#C9A84C",
        "key_facts": [
            "Chera Dynasty ruled 800-1102 CE",
            "Famous ancient port: Musiri (Cranganore)",
            "Black pepper traded with Rome and Arabia",
            "Sangam literature recorded Chera history",
            "Capital: Mahodayapuram (Kodungallur)"
        ],
        "quiz": [
            {"q": "What spice made Kerala famous in ancient trade?",
             "a": ["pepper","black pepper","black gold"],
             "hint": "Called black gold by the Romans"},
            {"q": "What was Kerala's most famous ancient port called?",
             "a": ["musiri","muchiri","cranganore"],
             "hint": "Romans wrote about it extensively"},
            {"q": "Which dynasty ruled Kerala's Golden Age 800-1102 CE?",
             "a": ["chera","cheras","kulasekharas"],
             "hint": "Also known as the Kulasekharas"},
        ],
        "qa": [
            {"keywords": ["chera","dynasty","kulasekharas","kings","who ruled","rulers","kingdom","founded"],
             "answer": "The **Chera Dynasty** (Kulasekharas) ruled Kerala from approximately **800 to 1102 CE**. Their capital was **Mahodayapuram** (modern Kodungallur). The Cheras had a powerful navy, patronised the arts, and built grand temples. They controlled the entire Kerala coast and its valuable spice trade.\n\nA scroll whispers: The last great Chera king donated the Thiruvanchikulam temple — it still stands today."},
            {"keywords": ["trade","spice","pepper","black gold","roman","port","musiri","export","silk","rome"],
             "answer": "Kerala was the world's **spice capital** in the ancient era. **Black pepper** (called black gold) was Kerala's most prized export, traded with the **Roman Empire, Arabia, and China**. The ancient port of **Musiri** (Kodungallur) was described by Roman authors as teeming with ships. Romans traded gold coins for pepper in such quantities that emperors complained it was draining Rome's treasury.\n\nA scroll whispers: Roman coins from the 1st century CE have been found in archaeological digs across Kerala."},
            {"keywords": ["sangam","literature","poetry","tamil","culture","arts","senguttuvan","purananuru"],
             "answer": "The **Sangam era** (300 BCE – 300 CE) produced remarkable Tamil poetry documenting Chera kings. Works like the **Purananuru** describe Chera rulers and battles in vivid detail. King **Senguttuvan** is celebrated in the epic **Silappatikaram** for his northern military campaigns.\n\nA scroll whispers: Sangam poets described Kerala's landscape so precisely that modern scholars use their verses to identify ancient ports and cities."},
            {"keywords": ["religion","temple","hindu","buddhism","jainism","faith","worship","perumal"],
             "answer": "Ancient Kerala was a land of remarkable religious diversity. **Hinduism** dominated with grand temples, but **Buddhism** and **Jainism** also flourished for centuries. Some Chera kings were devoted Vaishnavas (worshippers of Vishnu), earning the title **Kulasekhara Perumal**. Kerala's Theyyam ritual performances have roots stretching back over 1,500 years.\n\nA scroll whispers: One Chera king is believed to have become a saint — his devotional hymns are still sung in Vaishnava temples today."},
            {"keywords": ["decline","fall","collapse","chola","invasion","end","1102","fragment","weak"],
             "answer": "The Chera Dynasty **collapsed around 1102 CE** after prolonged conflict with the powerful **Chola Empire** from Tamil Nadu. Repeated Chola invasions burned the capital Mahodayapuram and weakened central authority, causing the kingdom to shatter into dozens of rival chieftaincies — the Zamorin, Cochin, Travancore, and others that would define medieval Kerala.\n\nA scroll whispers: After the Chera collapse, no single ruler unified all of Kerala again for 845 years."},
            {"keywords": ["jew","jewish","synagogue","foreigner","arab","china","international","cosmopolitan"],
             "answer": "Ancient Kerala welcomed merchants from across the world. **Jewish traders** arrived as early as 70 CE after the fall of Jerusalem — the **Paradesi Synagogue** in Kochi (1568) is one of the oldest active synagogues in Asia. Arab merchants called **Mappila** settled along the coast and many converted locals to Islam, creating Kerala's unique Muslim community.\n\nA scroll whispers: Kerala's Jewish community received a copper plate grant from a Chera king guaranteeing them rights and land — one of the oldest royal charters in India."},
            {"keywords": ["capital","mahodayapuram","kodungallur","cranganore","city","location"],
             "answer": "The Chera capital **Mahodayapuram** is modern-day **Kodungallur** (also called Cranganore) in central Kerala. It was one of the great port cities of the ancient world, visited by Romans, Arabs, Chinese, and Jewish traders. The city had direct sea routes to the Persian Gulf, Red Sea, and South China Sea.\n\nA scroll whispers: The ancient Cheraman Perumal Mosque in Kodungallur is claimed to be the first mosque built in India — dating to 629 CE."},
        ]
    },
    "chapter-2": {
        "title": "Chapter II: Medieval Kingdoms",
        "subtitle": "Zamorins, Nairs and the Spice Wars",
        "icon": "⚔️", "color": "#8B4513",
        "key_facts": [
            "Zamorin of Calicut rose to power in the 13th century",
            "Vasco da Gama arrived at Calicut on 20 May 1498",
            "Kunjali Marakkars: Kerala's legendary naval commanders",
            "Kalaripayattu: world's oldest martial art, born in Kerala",
            "Portuguese captured Goa in 1510"
        ],
        "quiz": [
            {"q": "In what year did Vasco da Gama arrive at Calicut?",
             "a": ["1498"], "hint": "End of the 15th century"},
            {"q": "What is the world's oldest martial art from Kerala?",
             "a": ["kalaripayattu","kalari"], "hint": "Still practiced and taught today"},
            {"q": "Who were the Zamorin's famous Muslim naval commanders?",
             "a": ["kunjali marakkars","kunjali","marakkars"],
             "hint": "They defended the Kerala coast from the Portuguese"},
        ],
        "qa": [
            {"keywords": ["zamorin","calicut","kozhikode","ruler","king","samoothiri","rise","power","dynasty"],
             "answer": "The **Zamorin** (Samoothiri) rose to power in the **13th century**, starting as a local chieftain near Calicut. Through military campaigns and strategic marriages they became the most powerful rulers in northern Kerala, controlling the lucrative pepper and spice trade.\n\nA scroll whispers: The Zamorin's title literally means Lord of the Sea."},
            {"keywords": ["fall","decline","end","defeat","zamorin","collapse","overthrow","british","tippu"],
             "answer": "The Zamorin dynasty **fell in stages** across the 18th century. Weakened by **200 years of war with the Portuguese**, then costly wars with the Mysore Sultanate under **Hyder Ali** (1766) and **Tipu Sultan** (1788-1790), who conquered Calicut and forced the Zamorin to flee. After Tipu's defeat by the British in 1799, Malabar including Calicut came under **British East India Company** rule, effectively ending Zamorin independence.\n\nA scroll whispers: The last Zamorin set fire to his own palace rather than surrender to Tipu Sultan's forces."},
            {"keywords": ["vasco da gama","portuguese","1498","arrival","explorer","portugal","first voyage"],
             "answer": "On **20 May 1498**, Portuguese explorer **Vasco da Gama** arrived at **Calicut**, completing the first direct sea voyage from Europe to India. He was received by the Zamorin but Arab merchants convinced the ruler not to trade. Da Gama returned in 1502 with warships and bombarded Calicut.\n\nA scroll whispers: The profit from da Gama's spice cargo was 60 times the cost of the entire expedition."},
            {"keywords": ["portuguese","conflict","war","attack","bombard","kozhikode","spice","trade","monopoly"],
             "answer": "The **Portuguese-Zamorin wars** lasted from **1500 to 1600s**. Portugal wanted to control the spice trade and repeatedly attacked Calicut. The Zamorin allied with Arab merchants and the Kunjali Marakkars to resist. Despite losing major sea battles, the Zamorin's forces harassed Portuguese ships for decades.\n\nA scroll whispers: The Portuguese once captured and hanged 800 Arab merchants to intimidate the Zamorin — it made him more determined to fight."},
            {"keywords": ["tipu sultan","hyder ali","mysore","invasion","malabar","18th century"],
             "answer": "**Hyder Ali** of Mysore invaded Malabar in **1766**, and his son **Tipu Sultan** conquered Calicut in **1788**. Tipu forcibly converted thousands and destroyed temples. The Zamorin burned his palace rather than surrender. After Tipu's death at **Srirangapatna in 1799**, the British took control of Malabar.\n\nA scroll whispers: Tipu Sultan's rockets were so advanced that British engineers studied them to develop their own rocket technology."},
            {"keywords": ["kunjali","marakkars","naval","navy","sea","fleet","admiral","commander","pirate"],
             "answer": "The **Kunjali Marakkars** were four generations of brilliant Muslim naval commanders serving the Zamorin. They built a powerful fleet and used guerrilla tactics to harass Portuguese ships. **Kunjali Marakkar IV** was so effective the Portuguese allied with the Zamorin himself to capture him in 1600.\n\nA scroll whispers: Kunjali Marakkar IV was executed in Goa by the Portuguese after betrayal — he remains a hero of Kerala's resistance history."},
            {"keywords": ["kalaripayattu","kalari","martial art","fighting","combat","warrior","nair","urumi"],
             "answer": "**Kalaripayattu** is the world's oldest surviving martial art, originating in Kerala over **3,000 years ago**. It combines strikes, kicks, grappling, and weapons including the deadly flexible sword called the **Urumi**. Traditionally trained by the **Nair warrior caste** who served as the Zamorin's army.\n\nA scroll whispers: The Urumi sword is so dangerous it is only taught to students who have mastered every other weapon first."},
            {"keywords": ["nair","warrior","caste","soldier","army","military","feudal","tharavad"],
             "answer": "The **Nairs** were the dominant warrior caste of medieval Kerala, serving as soldiers and administrators for rulers like the Zamorin. They followed a **matrilineal system** (property passed through the mother's line) and lived in large ancestral houses called **Tharavads**. Nair men trained in Kalaripayattu from childhood.\n\nA scroll whispers: Nair women also trained in Kalaripayattu and could participate in combat if their household was attacked."},
            {"keywords": ["kathakali","dance","mohiniyattam","art","performance","classical","culture","music","theyyam"],
             "answer": "Medieval Kerala produced world-famous art forms. **Kathakali** uses elaborate makeup and costume to tell stories from the Mahabharata and Ramayana. **Mohiniyattam** is a graceful solo dance form. **Theyyam** is a ritual performance where the dancer embodies a deity — practiced in northern Kerala for over 1,000 years.\n\nA scroll whispers: Kathakali makeup called chutti takes up to 6 hours to apply using natural pigments and coconut shell."},
            {"keywords": ["arab","ibn battuta","china","chinese","zheng he","merchant","trade","cosmopolitan","port"],
             "answer": "Medieval Calicut was one of the most **cosmopolitan ports on Earth**. Moroccan traveller **Ibn Battuta** visited in the 14th century and called it among the greatest ports he had seen. Chinese admiral **Zheng He** visited during his treasure fleet voyages. Arab, Jewish, Chinese, and African merchants all traded here.\n\nA scroll whispers: The Chinese fishing nets still standing in Kochi today were introduced during Zheng He's era."},
            {"keywords": ["spice","pepper","trade","route","silk road","wealth","goa","malabar coast"],
             "answer": "Kerala was the **spice capital of the world** in the medieval era. Black **pepper**, cardamom, cinnamon, and ginger from Kerala were worth more than gold in Europe. The Malabar Coast controlled the entire spice route from Asia to the West, making the Zamorin enormously wealthy.\n\nA scroll whispers: In medieval Europe, pepper was so valuable it was used to pay rents and ransoms."},
            {"keywords": ["cochin","kochi","kingdom","raja","perumpadapu","port","dutch","alliance"],
             "answer": "The **Kingdom of Cochin** (Kochi) was a smaller but strategically important rival to the Zamorin. The Raja of Cochin allied first with the **Portuguese** and later the **Dutch** to resist Zamorin domination. The Portuguese built **Fort Manuel** in Cochin in 1503 — the first European fort in India.\n\nA scroll whispers: The Portuguese introduced cashew nuts to Kerala — now one of the state's most important crops."},
        ]
    },
    "chapter-3": {
        "title": "Chapter III: Colonial Era and Independence",
        "subtitle": "Europeans, Travancore and Freedom",
        "icon": "🏰", "color": "#2E6B4F",
        "key_facts": [
            "Battle of Colachel 1741: Travancore defeated the Dutch",
            "Marthanda Varma unified southern Kerala",
            "Slavery abolished in Travancore in 1855",
            "Temple Entry Proclamation: 1936",
            "Kerala elected world's first communist government in 1957"
        ],
        "quiz": [
            {"q": "In what year did Travancore defeat the Dutch at Colachel?",
             "a": ["1741"], "hint": "18th century - a famous Asian victory over Europeans"},
            {"q": "Who was the Dutch commander captured at Colachel?",
             "a": ["de lannoy","lannoy","eustachius de lannoy"],
             "hint": "He later helped modernise the Travancore army"},
            {"q": "When was the Temple Entry Proclamation issued?",
             "a": ["1936"], "hint": "Opening temples to all castes"},
        ],
        "qa": [
            {"keywords": ["battle of colachel","colachel","dutch","voc","1741","marthanda varma","victory","defeat"],
             "answer": "In **1741**, King **Marthanda Varma** of Travancore defeated the **Dutch East India Company (VOC)** at the **Battle of Colachel** — one of the only decisive Asian victories over a European colonial power in the 18th century. Dutch commander **Eustachius De Lannoy** was captured and later helped modernise the Travancore army.\n\nA scroll whispers: De Lannoy's grave can still be visited in Udayagiri Fort, Kerala today."},
            {"keywords": ["marthanda varma","travancore","kingdom","unification","padmanabha","king","ruler","founded"],
             "answer": "**Marthanda Varma** (ruled 1729–1758) is considered the maker of modern Travancore. He unified fragmented southern Kerala chieftaincies through military campaigns and dedicated the entire Travancore kingdom to **Lord Padmanabhaswamy**, declaring himself the deity's servant-king. This unusual act gave him strong religious legitimacy.\n\nA scroll whispers: The Padmanabhaswamy Temple's hidden vaults, opened in 2011, contained treasures worth over 22 billion dollars — the largest temple treasure ever discovered."},
            {"keywords": ["slavery","abolish","1855","social reform","caste","sree narayana","discrimination","reform","untouchable"],
             "answer": "Travancore **abolished slavery in 1855** — decades before much of the British Empire. Social reformer **Sree Narayana Guru** (1856–1928) led a powerful movement against caste discrimination with his motto: *One caste, one religion, one God for humanity*. He consecrated temples open to all castes at a time when this was radical.\n\nA scroll whispers: Lower-caste women in parts of Kerala were once brutally taxed for covering their chests — reformers including Sree Narayana Guru fought to end this."},
            {"keywords": ["temple entry","proclamation","1936","chithira thirunal","caste","vaikom","satyagraha"],
             "answer": "On **12 November 1936**, Maharaja **Chithira Thirunal** issued the **Temple Entry Proclamation**, opening all government temples in Travancore to Hindus of all castes. This was a landmark moment in Indian social history. It followed the **Vaikom Satyagraha** (1924-1925) — a civil disobedience movement where people including Gandhi protested caste discrimination at Vaikom temple.\n\nA scroll whispers: The Temple Entry Proclamation preceded India's independence by 11 years — Travancore led the way."},
            {"keywords": ["british","east india company","colonial","empire","colonialism","british rule","malabar","princely"],
             "answer": "The **British East India Company** extended control over Kerala in stages. After Tipu Sultan's defeat in 1799, they took Malabar directly. Travancore and Cochin remained **Princely States** under British protection. The **Malabar Rebellion of 1921** was one of the most significant anti-colonial uprisings in Kerala, led by Mappila Muslims.\n\nA scroll whispers: Kerala's first printing press was brought by Christian missionaries in the colonial era — it played a major role in spreading literacy."},
            {"keywords": ["independence","1947","1949","partition","india","freedom","join"],
             "answer": "When India gained independence on **15 August 1947**, Travancore and Cochin initially hesitated to join. After political pressure, Travancore and Cochin merged into **Travancore-Cochin** on **1 July 1949**. Malabar was already part of Madras Province. All three merged into the **State of Kerala on 1 November 1956** when linguistic states were reorganised.\n\nA scroll whispers: Kerala Day (November 1st) celebrates the formation of the unified state — it is called **Kerala Piravi** meaning the Birth of Kerala."},
            {"keywords": ["communist","1957","ems","namboodiripad","election","government","first","world"],
             "answer": "In **1957**, Kerala made world history by electing the **world's first democratic communist government**, led by **E.M.S. Namboodiripad** (EMS). They passed radical land reform laws redistributing land to farmers. The Central Government controversially dismissed the ministry in 1959 under Article 356.\n\nA scroll whispers: EMS Namboodiripad was a Brahmin who gave up all caste privileges to fight for the poor — a remarkable personal sacrifice."},
            {"keywords": ["literacy","education","development","kerala model","health","modern","achievement"],
             "answer": "Modern Kerala is celebrated for the **Kerala Model of Development** — achieving near **100% literacy**, excellent healthcare, and low infant mortality despite modest income. This is attributed to centuries of royal patronage of education, Christian missionary schools, and strong social reform movements.\n\nA scroll whispers: Kerala sends more nurses, doctors, and engineers abroad than any other Indian state — remittances from the Gulf form a huge part of Kerala's economy today."},
        ]
    }
}

RIDDLES = [
    {"q": "I have cities but no houses, mountains but no trees. What am I?",
     "a": ["map"], "hint": "You use me for navigation"},
    {"q": "The more you take, the more you leave behind. What am I?",
     "a": ["footsteps"], "hint": "Think about walking"},
    {"q": "I speak without a mouth, hear without ears. What am I?",
     "a": ["echo"], "hint": "Mountains produce me"},
    {"q": "What has keys but no locks, space but no room?",
     "a": ["keyboard"], "hint": "You are using one right now"},
    {"q": "I am always before you yet cannot be seen. What am I?",
     "a": ["future"], "hint": "Tomorrow is my first name"},
]

def search(query, chapter_id):
    if chapter_id not in KNOWLEDGE: return None
    q = query.lower()
    # normalise plurals/verb forms so "zamorins" matches "zamorin"
    q = q.replace("zamorins","zamorin").replace("kingdoms","kingdom")          .replace("battles","battle").replace("kings","king")          .replace("rulers","ruler").replace("traders","trader")          .replace("ports","port").replace("wars","war")          .replace("soldiers","soldier").replace("commanders","commander")          .replace("artists","artist").replace("dances","dance")          .replace("temples","temple").replace("routes","route")          .replace("reforms","reform").replace("merchants","merchant")
    best, best_score = None, 0
    for pair in KNOWLEDGE[chapter_id]["qa"]:
        # score = keyword matches + bonus if keyword is a substring
        score = 0
        for kw in pair["keywords"]:
            if kw in q:
                score += 2  # exact match worth more
            elif any(kw in word or word in kw for word in q.split() if len(word) > 3):
                score += 1  # partial match
        if score > best_score:
            best_score, best = score, pair["answer"]
    return best if best_score > 0 else None


# ── GOOGLE SEARCH ────────────────────────────────────────────
GOOGLE_API_KEY = "AIzaSyDjNTj9mv-ipysplztpuAkY3Fk9RQ0wyl401"
GOOGLE_CX      = "443561326e11e4c6e"

def google_search(query):
    try:
        url = "https://www.googleapis.com/customsearch/v1?" + urllib.parse.urlencode({
            "key": GOOGLE_API_KEY,
            "cx":  GOOGLE_CX,
            "q":   query + " Kerala history",
            "num": 3
        })
        req = urllib.request.Request(url, headers={"User-Agent": "ElarixBot/1.0"})
        with urllib.request.urlopen(req, timeout=6) as r:
            data = json.loads(r.read().decode())

        items = data.get("items", [])
        if not items:
            return None

        # Build a response from the top 3 results
        lines = []
        for item in items[:3]:
            title   = item.get("title", "")
            snippet = item.get("snippet", "").replace("\n", " ").strip()
            link    = item.get("link", "")
            if title and snippet:
                lines.append("**" + title + "**\n" + snippet + "\n*Source: " + link + "*")

        if not lines:
            return None

        return ("*Elarix consults the wider world...*\n\n" +
                "**Google Search Results:**\n\n" +
                "\n\n---\n\n".join(lines) +
                "\n\n*A scroll whispers: These results come from the open web — always verify with your teacher.*")
    except Exception as e:
        return None

# Keep Wikipedia as backup if Google fails
def wikipedia_search(query):
    try:
        search_url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query", "list": "search",
            "srsearch": query + " Kerala India history",
            "srlimit": 1, "format": "json"
        })
        req = urllib.request.Request(search_url, headers={"User-Agent": "ElarixBot/1.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode())
        results = data.get("query", {}).get("search", [])
        if not results: return None
        title = results[0]["title"]
        summary_url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query", "titles": title, "prop": "extracts",
            "exintro": True, "explaintext": True, "exsentences": 4, "format": "json"
        })
        req2 = urllib.request.Request(summary_url, headers={"User-Agent": "ElarixBot/1.0"})
        with urllib.request.urlopen(req2, timeout=5) as r2:
            data2 = json.loads(r2.read().decode())
        pages = data2.get("query", {}).get("pages", {})
        page = next(iter(pages.values()))
        extract = page.get("extract", "").strip()
        if not extract or len(extract) < 40: return None
        sentences = extract.replace("\n", " ").split(". ")
        summary = ". ".join(sentences[:3]).strip()
        if not summary.endswith("."): summary += "."
        return "**From Wikipedia** — *" + title + "*\n\n" + summary + "\n\n*A scroll whispers: Always verify with your teacher.*"
    except Exception:
        return None

# ── MASCOT ───────────────────────────────────────────────────
@app.route("/mascot/<expr>")
def mascot_img(expr):
    allowed = ["normal","happy","angry","shocked","thinking","sad"]
    script_folder = os.path.dirname(os.path.abspath(__file__))
    cwd_folder = os.getcwd()
    search_folders = list(dict.fromkeys([script_folder, cwd_folder]))
    name = "mascot_" + expr + ".png" if expr in allowed else "mascot_normal.png"
    candidates = [name, "mascot_normal.png", "mascot.png"]
    for folder in search_folders:
        for candidate in candidates:
            if os.path.exists(os.path.join(folder, candidate)):
                return send_from_directory(folder, candidate)
    return "", 404

@app.route("/mascot-debug")
def mascot_debug():
    folder = os.path.dirname(os.path.abspath(__file__))
    files = [f for f in os.listdir(folder) if "mascot" in f.lower()]
    return "<br>".join([
        f"<b>Folder:</b> {folder}",
        f"<b>Mascot files:</b> {files if files else 'NONE — upload mascot_normal.png etc to GitHub repo'}",
    ])

# ── HTML ─────────────────────────────────────────────────────

LANDING_HTML = r"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ZUCHINNI.AI - Elarix</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;600&family=IM+Fell+English:ital@0;1&display=swap" rel="stylesheet">
<style>
:root{--maroon:#6B1E2E;--deep:#100308;--gold:#C9A84C;--parchment:#F5E6C8;}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--deep);font-family:'IM Fell English',serif;color:var(--parchment);min-height:100vh;overflow-x:hidden;}
.bg{position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse 80% 60% at 15% 55%,rgba(107,30,46,.38),transparent 60%),linear-gradient(175deg,#060102,#100308);}
nav{position:fixed;top:0;left:0;right:0;z-index:200;display:flex;justify-content:space-between;align-items:center;padding:1.2rem 3rem;background:rgba(8,1,2,.7);border-bottom:1px solid rgba(201,168,76,.12);backdrop-filter:blur(16px);}
.nav-logo{font-family:'Cinzel Decorative',cursive;font-size:1.05rem;color:var(--gold);text-decoration:none;letter-spacing:3px;}
nav a:not(.nav-logo){font-family:'Cinzel',serif;font-size:.72rem;color:rgba(245,230,200,.55);text-decoration:none;letter-spacing:2.5px;text-transform:uppercase;margin-left:2rem;transition:color .3s;}
nav a:not(.nav-logo):hover{color:var(--gold);}
.hero{position:relative;z-index:10;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:2rem;}
.eyebrow{font-family:'Cinzel',serif;font-size:.68rem;letter-spacing:6px;color:var(--gold);border:1px solid rgba(201,168,76,.28);padding:.45rem 1.8rem;border-radius:30px;margin-bottom:2.2rem;}
.hero-title{font-family:'Cinzel Decorative',cursive;font-size:clamp(3.5rem,11vw,8rem);color:var(--gold);line-height:.95;margin-bottom:.6rem;}
.hero-sub{font-family:'Cinzel',serif;font-size:clamp(.9rem,2.5vw,1.3rem);color:rgba(245,230,200,.45);letter-spacing:5px;text-transform:uppercase;margin-bottom:2.5rem;}
.hero-desc{font-size:1.1rem;max-width:580px;line-height:2;color:rgba(245,230,200,.72);font-style:italic;margin-bottom:3.5rem;}
.hero-btns{display:flex;gap:1.4rem;flex-wrap:wrap;justify-content:center;}
.btn-primary{font-family:'Cinzel',serif;font-size:.8rem;letter-spacing:3px;padding:1rem 2.8rem;text-decoration:none;text-transform:uppercase;border-radius:4px;background:linear-gradient(135deg,var(--maroon),#3D0D1A);border:1.5px solid var(--gold);color:var(--gold);transition:all .35s;}
.btn-primary:hover{transform:translateY(-3px);box-shadow:0 0 35px rgba(201,168,76,.25);}
.btn-outline{font-family:'Cinzel',serif;font-size:.8rem;letter-spacing:3px;padding:1rem 2.8rem;text-decoration:none;text-transform:uppercase;border-radius:4px;background:transparent;border:1.5px solid rgba(245,230,200,.22);color:rgba(245,230,200,.55);transition:all .35s;}
.btn-outline:hover{border-color:var(--gold);color:var(--gold);}
.features{position:relative;z-index:10;max-width:1080px;margin:0 auto;padding:5rem 2rem 7rem;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.6rem;}
.feat-card{background:rgba(40,12,20,.88);border:1px solid rgba(201,168,76,.18);border-radius:10px;padding:2rem 1.8rem;text-align:center;transition:all .4s;}
.feat-card:hover{border-color:var(--gold);transform:translateY(-5px);}
.feat-icon{font-size:2.4rem;margin-bottom:1rem;}
.feat-title{font-family:'Cinzel',serif;font-size:.85rem;color:var(--gold);letter-spacing:2.5px;text-transform:uppercase;margin-bottom:.7rem;}
.feat-desc{font-size:.9rem;line-height:1.85;color:rgba(245,230,200,.62);font-style:italic;}
footer{position:relative;z-index:10;text-align:center;padding:2.5rem;border-top:1px solid rgba(201,168,76,.1);font-family:'Cinzel',serif;font-size:.68rem;letter-spacing:2px;color:rgba(245,230,200,.25);}
</style></head><body>
<div class="bg"></div>
<nav>
  <a href="/" class="nav-logo">ZUCHINNI.AI</a>
  <div><a href="/login">Login</a><a href="/signup">Join</a><a href="/leaderboard">Hall of Fame</a></div>
</nav>
<section class="hero">
  <div class="eyebrow">MYP Design Project - Kerala History - ZUCHINNI.AI</div>
  <h1 class="hero-title">ELARIX</h1>
  <p class="hero-sub">The Ancient Archivist of Kerala</p>
  <p class="hero-desc">"Enter these halls, seeker. I am Elarix - keeper of Kerala's chronicles spanning three thousand years of dynasties, spice routes, martial arts, and the courage of kings."</p>
  <div class="hero-btns">
    <a href="/signup" class="btn-primary">Begin Your Journey</a>
    <a href="/login" class="btn-outline">Return to Archives</a>
  </div>
</section>
<div class="features">
  <div class="feat-card"><div class="feat-icon">📜</div><div class="feat-title">Three Chronicles</div><div class="feat-desc">Journey through Kerala's Golden Age, medieval kingdoms, and the colonial era.</div></div>
  <div class="feat-card"><div class="feat-icon">🔍</div><div class="feat-title">Smart Search</div><div class="feat-desc">Ask any question in plain English. Elarix searches the ancient scrolls and responds as a medieval archivist.</div></div>
  <div class="feat-card"><div class="feat-icon">⚔️</div><div class="feat-title">Dungeon and Riddles</div><div class="feat-desc">Speak with respect or face the dungeon! Solve riddles and pop bubbles to earn your freedom.</div></div>
  <div class="feat-card"><div class="feat-icon">🎭</div><div class="feat-title">Mascot Expressions</div><div class="feat-desc">Elarix reacts to everything - happy, shocked, angry, thinking - with animated expressions.</div></div>
  <div class="feat-card"><div class="feat-icon">📝</div><div class="feat-title">Chapter Quizzes</div><div class="feat-desc">Test your knowledge with 3 questions per chapter and climb the Scrolls of Fame leaderboard.</div></div>
  <div class="feat-card"><div class="feat-icon">🏆</div><div class="feat-title">Hall of Fame</div><div class="feat-desc">Top 50 quiz scores from all scholars displayed on the Scrolls of Fame.</div></div>
</div>
<footer>ZUCHINNI.AI - Elarix the Archivist - MYP Design Project</footer>
</body></html>"""

AUTH_HTML = r"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Elarix - Auth</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Cinzel:wght@400;600&family=IM+Fell+English:ital@0;1&display=swap" rel="stylesheet">
<style>
:root{--maroon:#6B1E2E;--deep:#100308;--gold:#C9A84C;--parchment:#F5E6C8;}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--deep);font-family:'IM Fell English',serif;color:var(--parchment);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:1.5rem;}
.bg{position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse 70% 70% at 25% 55%,rgba(107,30,46,.3),transparent 65%),linear-gradient(170deg,#060102,#100308);}
.auth-card{position:relative;z-index:10;background:rgba(42,12,22,.94);border:1px solid rgba(201,168,76,.3);border-radius:14px;padding:3rem 2.8rem;width:100%;max-width:430px;box-shadow:0 50px 100px rgba(0,0,0,.65);}
.auth-logo{font-family:'Cinzel Decorative',cursive;font-size:.95rem;color:var(--gold);text-decoration:none;letter-spacing:3px;display:block;text-align:center;margin-bottom:1.8rem;}
.auth-title{font-family:'Cinzel Decorative',cursive;font-size:1.75rem;color:var(--gold);text-align:center;margin-bottom:.4rem;}
.auth-sub{font-style:italic;color:rgba(245,230,200,.45);font-size:.88rem;text-align:center;margin-bottom:1.6rem;}
.auth-divider{height:1px;background:linear-gradient(90deg,transparent,rgba(201,168,76,.35),transparent);margin-bottom:1.6rem;}
.auth-label{font-family:'Cinzel',serif;font-size:.65rem;letter-spacing:2.5px;text-transform:uppercase;color:rgba(245,230,200,.55);display:block;margin-bottom:.45rem;}
.auth-field{width:100%;padding:.9rem 1.1rem;margin-bottom:1.3rem;background:rgba(8,2,5,.7);border:1px solid rgba(201,168,76,.22);border-radius:7px;color:var(--parchment);font-family:'IM Fell English',serif;font-size:1rem;outline:none;transition:all .3s;}
.auth-field:focus{border-color:var(--gold);}
.auth-field::placeholder{color:rgba(245,230,200,.2);font-style:italic;}
.auth-btn{width:100%;padding:1rem;font-family:'Cinzel',serif;font-size:.8rem;letter-spacing:3px;text-transform:uppercase;background:linear-gradient(135deg,var(--maroon),#3D0D1A);border:1.5px solid var(--gold);border-radius:7px;color:var(--gold);cursor:pointer;transition:all .35s;margin-top:.3rem;}
.auth-btn:hover{box-shadow:0 0 30px rgba(201,168,76,.28);transform:translateY(-1px);}
.auth-btn:disabled{opacity:.45;cursor:not-allowed;transform:none;}
.auth-err{background:rgba(110,30,30,.35);border:1px solid rgba(200,60,60,.3);border-radius:7px;padding:.8rem 1rem;font-size:.85rem;color:#ffaaaa;text-align:center;margin-bottom:1.1rem;display:none;}
.auth-switch{text-align:center;margin-top:1.6rem;font-size:.88rem;color:rgba(245,230,200,.45);}
.auth-switch a{color:var(--gold);text-decoration:none;font-family:'Cinzel',serif;}
</style></head><body>
<div class="bg"></div>
<div class="auth-card">
  <a href="/" class="auth-logo">ZUCHINNI.AI</a>
  <div class="auth-title">{% if mode=='login' %}The Gates Open{% else %}Join the Order{% endif %}</div>
  <div class="auth-sub">{% if mode=='login' %}Return to the chronicles, scholar.{% else %}Begin your medieval journey, seeker.{% endif %}</div>
  <div class="auth-divider"></div>
  <div class="auth-err" id="err-msg"></div>
  <label class="auth-label">Chosen Name</label>
  <input type="text" class="auth-field" id="inp-user" placeholder="Enter your name, traveller..." autocomplete="off">
  <label class="auth-label">Secret Passphrase</label>
  <input type="password" class="auth-field" id="inp-pass" placeholder="Your passphrase...">
  {% if mode=='signup' %}
  <label class="auth-label">Confirm Passphrase</label>
  <input type="password" class="auth-field" id="inp-conf" placeholder="Repeat your passphrase...">
  {% endif %}
  <button class="auth-btn" id="auth-submit" onclick="doAuth()">
    {% if mode=='login' %}Enter the Archives{% else %}Begin the Journey{% endif %}
  </button>
  <div class="auth-switch">
    {% if mode=='login' %}New here? <a href="/signup">Create your chronicle</a>
    {% else %}Already a scholar? <a href="/login">Enter the archives</a>{% endif %}
  </div>
</div>
<script>
var MODE = "{{ mode }}";
document.addEventListener('keydown', function(e){ if(e.key==='Enter') doAuth(); });
function doAuth(){
  var u = document.getElementById('inp-user').value.trim();
  var p = document.getElementById('inp-pass').value;
  clearErr();
  if(!u || !p){ showErr('Both fields are required.'); return; }
  if(MODE === 'signup'){
    var c = document.getElementById('inp-conf').value;
    if(p !== c){ showErr('Passphrases do not match!'); return; }
    if(p.length < 4){ showErr('Passphrase must be 4+ characters.'); return; }
  }
  var btn = document.getElementById('auth-submit');
  btn.disabled = true;
  btn.textContent = 'Consulting scrolls...';
  fetch('/' + MODE, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({username:u, password:p})
  })
  .then(function(r){ return r.json(); })
  .then(function(d){
    if(d.success){ window.location = '/chapters'; }
    else{
      showErr(d.error || 'The scrolls reject your entry.');
      btn.disabled = false;
      btn.textContent = MODE==='login' ? 'Enter the Archives' : 'Begin the Journey';
    }
  });
}
function showErr(m){ var e=document.getElementById('err-msg'); e.textContent=m; e.style.display='block'; }
function clearErr(){ document.getElementById('err-msg').style.display='none'; }
</script></body></html>"""

CHAPTERS_HTML = r"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Choose Your Chronicle - Elarix</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Cinzel:wght@400;600&family=IM+Fell+English:ital@0;1&display=swap" rel="stylesheet">
<style>
:root{--maroon:#6B1E2E;--deep:#100308;--gold:#C9A84C;--parchment:#F5E6C8;}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--deep);font-family:'IM Fell English',serif;color:var(--parchment);min-height:100vh;}
.bg{position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse 65% 55% at 20% 55%,rgba(107,30,46,.28),transparent 60%),linear-gradient(165deg,#060102,#100308);}
nav{position:fixed;top:0;left:0;right:0;z-index:100;display:flex;justify-content:space-between;align-items:center;padding:1rem 2.5rem;background:rgba(6,1,2,.92);border-bottom:1px solid rgba(201,168,76,.13);backdrop-filter:blur(14px);}
.nav-logo{font-family:'Cinzel Decorative',cursive;font-size:.95rem;color:var(--gold);text-decoration:none;letter-spacing:2.5px;}
.nav-links{display:flex;align-items:center;gap:1.8rem;}
.nav-links a{font-family:'Cinzel',serif;font-size:.65rem;color:rgba(245,230,200,.55);text-decoration:none;letter-spacing:2.5px;text-transform:uppercase;transition:color .3s;}
.nav-links a:hover{color:var(--gold);}
.nav-user{font-family:'Cinzel',serif;font-size:.65rem;color:var(--gold);letter-spacing:2px;padding:.3rem .9rem;border:1px solid rgba(201,168,76,.25);border-radius:20px;}
.page-head{position:relative;z-index:10;text-align:center;padding:7.5rem 2rem 3rem;}
.page-head h1{font-family:'Cinzel Decorative',cursive;font-size:clamp(1.8rem,5vw,3.5rem);color:var(--gold);margin-bottom:.7rem;}
.page-head p{font-style:italic;color:rgba(245,230,200,.52);max-width:520px;margin:0 auto;line-height:1.9;}
.divider{width:160px;height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent);margin:1.8rem auto;}
.ch-grid{position:relative;z-index:10;display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:2rem;max-width:1060px;margin:0 auto;padding:1.5rem 2rem 5rem;}
.ch-card{background:rgba(40,12,20,.88);border:1px solid rgba(201,168,76,.18);border-radius:11px;overflow:hidden;text-decoration:none;color:inherit;transition:all .4s;display:flex;flex-direction:column;}
.ch-card:hover{transform:translateY(-8px);border-color:var(--gold);box-shadow:0 30px 70px rgba(0,0,0,.7);}
.ch-banner{height:150px;display:flex;align-items:center;justify-content:center;font-size:4.5rem;}
.ch-body{padding:1.8rem;}
.ch-num{font-family:'Cinzel',serif;font-size:.6rem;letter-spacing:4px;color:var(--gold);opacity:.65;text-transform:uppercase;margin-bottom:.45rem;}
.ch-title{font-family:'Cinzel',serif;font-size:1.25rem;color:var(--gold);margin-bottom:.4rem;}
.ch-sub{font-style:italic;color:rgba(245,230,200,.45);font-size:.82rem;margin-bottom:1.4rem;}
.ch-facts{list-style:none;}
.ch-facts li{font-size:.82rem;color:rgba(245,230,200,.62);padding:.3rem 0;border-bottom:1px solid rgba(201,168,76,.07);display:flex;gap:.5rem;line-height:1.5;}
.ch-facts li::before{content:'>';font-size:.6rem;color:var(--gold);opacity:.5;flex-shrink:0;margin-top:3px;}
.ch-foot{margin-top:auto;padding:1.1rem 1.8rem;border-top:1px solid rgba(201,168,76,.12);display:flex;justify-content:space-between;align-items:center;}
.ch-cta{font-family:'Cinzel',serif;font-size:.65rem;letter-spacing:2px;color:var(--gold);text-transform:uppercase;}
</style></head><body>
<div class="bg"></div>
<nav>
  <a href="/" class="nav-logo">ZUCHINNI.AI</a>
  <div class="nav-links">
    <span class="nav-user">{{ username }}</span>
    <a href="/leaderboard">Hall of Fame</a>
    <a href="/logout">Depart</a>
  </div>
</nav>
<div class="page-head">
  <h1>The Chronicles of Kerala</h1>
  <div class="divider"></div>
  <p>"Choose your chapter, seeker. Each scroll holds the wisdom of a different age of Kerala's magnificent history."</p>
</div>
<div class="ch-grid">
{% for id, ch in chapters.items() %}
<a href="/chat/{{ id }}" class="ch-card">
  <div class="ch-banner" style="background:linear-gradient(135deg,{{ ch.color }}25,{{ ch.color }}45);">
    {{ ch.icon }}
  </div>
  <div class="ch-body">
    <div class="ch-num">Chronicle {{ loop.index }}</div>
    <div class="ch-title">{{ ch.title.split(':')[1].strip() if ':' in ch.title else ch.title }}</div>
    <div class="ch-sub">{{ ch.subtitle }}</div>
    <ul class="ch-facts">{% for f in ch.key_facts[:4] %}<li>{{ f }}</li>{% endfor %}</ul>
  </div>
  <div class="ch-foot"><span class="ch-cta">Consult the Scrolls &rarr;</span></div>
</a>
{% endfor %}
</div>
</body></html>"""

CHAT_HTML = r"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ chapter.title }} - Elarix</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Cinzel:wght@400;600&family=IM+Fell+English:ital@0;1&display=swap" rel="stylesheet">
<style>
:root{--maroon:#6B1E2E;--deep:#100308;--gold:#C9A84C;--gold2:#E8C97A;--parchment:#F5E6C8;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{height:100%;overflow:hidden;}
body{background:var(--deep);font-family:'IM Fell English',serif;color:var(--parchment);display:flex;flex-direction:column;}
.bg{position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse 50% 60% at 8% 50%,rgba(107,30,46,.18),transparent 55%),linear-gradient(165deg,#060102,#100308);}

/* TOPBAR */
.topbar{position:relative;z-index:100;flex-shrink:0;display:flex;justify-content:space-between;align-items:center;padding:.75rem 1.5rem;background:rgba(5,1,2,.97);border-bottom:1px solid rgba(201,168,76,.16);}
.tb-left{display:flex;align-items:center;gap:.9rem;}
.tb-back{font-family:'Cinzel',serif;font-size:.62rem;color:rgba(245,230,200,.45);text-decoration:none;letter-spacing:2px;text-transform:uppercase;transition:color .3s;}
.tb-back:hover{color:var(--gold);}
.tb-badge{font-family:'Cinzel',serif;font-size:.62rem;letter-spacing:2px;text-transform:uppercase;color:var(--gold);background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.28);padding:.28rem .85rem;border-radius:20px;}
.tb-title{font-family:'Cinzel Decorative',cursive;font-size:.9rem;color:var(--gold);letter-spacing:3px;}
.tb-right{display:flex;align-items:center;gap:.7rem;}
.topbtn{font-family:'Cinzel',serif;font-size:.62rem;letter-spacing:1.5px;text-transform:uppercase;padding:.38rem .95rem;border-radius:5px;cursor:pointer;transition:all .3s;border:1px solid;}
.topbtn-gold{border-color:rgba(201,168,76,.35);color:var(--gold);background:none;}
.topbtn-gold:hover{background:rgba(201,168,76,.12);}
.topbtn-dim{border-color:rgba(107,30,46,.5);color:rgba(245,230,200,.5);background:none;}
.topbtn-dim:hover{border-color:var(--maroon);color:var(--parchment);}
.tb-user{font-family:'Cinzel',serif;font-size:.6rem;color:rgba(245,230,200,.35);letter-spacing:1px;}

/* LAYOUT */
.wrap{display:flex;flex:1;overflow:hidden;position:relative;z-index:10;}

/* SIDEBAR */
.sidebar{width:260px;flex-shrink:0;background:rgba(10,3,6,.95);border-right:1px solid rgba(201,168,76,.12);display:flex;flex-direction:column;overflow-y:auto;}
.sidebar::-webkit-scrollbar{width:3px;}
.sidebar::-webkit-scrollbar-thumb{background:rgba(201,168,76,.18);}
.sb-sec{padding:1.2rem;border-bottom:1px solid rgba(201,168,76,.08);}
.sb-head{font-family:'Cinzel',serif;font-size:.58rem;letter-spacing:3px;text-transform:uppercase;color:rgba(201,168,76,.55);margin-bottom:.9rem;}
.sb-facts{list-style:none;}
.sb-facts li{font-size:.8rem;color:rgba(245,230,200,.6);padding:.4rem 0;border-bottom:1px solid rgba(201,168,76,.05);display:flex;gap:.45rem;line-height:1.55;}
.sb-facts li::before{content:'-';color:var(--gold);opacity:.45;flex-shrink:0;}
.mascot-area{padding:1.2rem;text-align:center;border-bottom:1px solid rgba(201,168,76,.08);}
#mascot-img{width:170px;border-radius:8px;transition:opacity .2s ease,transform .2s ease;filter:drop-shadow(0 0 12px rgba(201,168,76,.3));}
#mascot-cap{font-family:'Cinzel',serif;font-size:.6rem;letter-spacing:2px;color:rgba(201,168,76,.5);margin-top:.6rem;text-transform:uppercase;display:block;transition:opacity .15s ease;}
.mascot-emoji{width:170px;height:170px;font-size:5rem;display:none;align-items:center;justify-content:center;border-radius:8px;background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.15);margin:0 auto;transition:all .3s ease;}
.mascot-normal{color:#C9A84C;} .mascot-thinking{color:#88aaff;animation:pulse 1.2s ease-in-out infinite;}
.mascot-happy{color:#90ee90;} .mascot-angry{color:#ff6b6b;animation:shake 0.4s ease;}
.mascot-shocked{color:#ffd700;animation:bounce 0.3s ease;} .mascot-sad{color:#aaaaff;}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}
@keyframes shake{0%,100%{transform:translateX(0)}25%{transform:translateX(-6px)}75%{transform:translateX(6px)}}
@keyframes bounce{0%,100%{transform:translateY(0)}40%{transform:translateY(-12px)}}
.sug-item{font-size:.78rem;color:rgba(245,230,200,.55);padding:.48rem .75rem;border-radius:5px;border:1px solid rgba(201,168,76,.1);margin-bottom:.35rem;cursor:pointer;transition:all .3s;font-style:italic;display:block;width:100%;text-align:left;background:none;}
.sug-item:hover{background:rgba(201,168,76,.07);border-color:rgba(201,168,76,.3);color:var(--parchment);}

/* CHAT */
.chat-col{flex:1;display:flex;flex-direction:column;overflow:hidden;}
.msg-list{flex:1;overflow-y:auto;padding:1.4rem;display:flex;flex-direction:column;gap:1.1rem;}
.msg-list::-webkit-scrollbar{width:3px;}
.msg-list::-webkit-scrollbar-thumb{background:rgba(201,168,76,.18);}
.msg-row{display:flex;gap:.75rem;animation:popIn .3s ease both;}
.msg-row.is-user{flex-direction:row-reverse;}
@keyframes popIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.msg-av{width:34px;height:34px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:.95rem;border:1px solid rgba(201,168,76,.28);}
.msg-row.is-bot .msg-av{background:linear-gradient(135deg,#3D0D1A,var(--maroon));}
.msg-row.is-user .msg-av{background:rgba(201,168,76,.1);}
.msg-bub{max-width:73%;padding:.9rem 1.1rem;border-radius:8px;font-size:.93rem;line-height:1.85;}
.msg-row.is-bot .msg-bub{background:rgba(22,6,12,.95);border:1px solid rgba(201,168,76,.13);border-top-left-radius:2px;}
.msg-row.is-user .msg-bub{background:rgba(107,30,46,.35);border:1px solid rgba(107,30,46,.55);border-top-right-radius:2px;text-align:right;}
.msg-who{font-family:'Cinzel',serif;font-size:.58rem;letter-spacing:2px;text-transform:uppercase;color:var(--gold);opacity:.65;margin-bottom:.35rem;}
.msg-row.is-user .msg-who{text-align:right;}
.msg-txt{color:rgba(245,230,200,.87);}
.msg-txt strong{color:var(--gold2);}
.msg-txt em{color:rgba(245,230,200,.6);}
.dots{display:flex;align-items:center;gap:5px;padding:.5rem .8rem;}
.dots span{width:6px;height:6px;border-radius:50%;background:var(--gold);opacity:.35;animation:blink 1.1s ease infinite;}
.dots span:nth-child(2){animation-delay:.18s;}
.dots span:nth-child(3){animation-delay:.36s;}
@keyframes blink{0%,100%{opacity:.2;transform:scale(.8)}50%{opacity:.85;transform:scale(1.15)}}

/* INPUT */
.inp-bar{padding:.9rem 1.4rem;background:rgba(6,1,3,.97);border-top:1px solid rgba(201,168,76,.13);display:flex;gap:.75rem;align-items:flex-end;flex-shrink:0;}
#msg-inp{flex:1;background:rgba(18,5,10,.85);border:1px solid rgba(201,168,76,.2);border-radius:8px;color:var(--parchment);font-family:'IM Fell English',serif;font-size:.93rem;padding:.75rem 1rem;resize:none;outline:none;transition:border .3s;min-height:42px;max-height:110px;line-height:1.6;}
#msg-inp:focus{border-color:rgba(201,168,76,.48);}
#msg-inp::placeholder{color:rgba(245,230,200,.18);font-style:italic;}
#send-btn{padding:.75rem 1.4rem;font-family:'Cinzel',serif;font-size:.72rem;letter-spacing:2px;text-transform:uppercase;background:linear-gradient(135deg,var(--maroon),#3D0D1A);border:1px solid rgba(201,168,76,.38);border-radius:8px;color:var(--gold);cursor:pointer;transition:all .3s;flex-shrink:0;}
#send-btn:hover{box-shadow:0 0 22px rgba(201,168,76,.2);border-color:var(--gold);}
#send-btn:disabled{opacity:.38;cursor:not-allowed;}

/* BUBBLE OVERLAY */
.bub-ov{position:fixed;inset:0;z-index:1000;background:rgba(4,1,2,.93);backdrop-filter:blur(14px);display:none;flex-direction:column;align-items:center;justify-content:center;gap:1.8rem;}
.bub-ov.show{display:flex;}
.bub-title{font-family:'Cinzel Decorative',cursive;font-size:2rem;color:var(--gold);}
.bub-desc{font-style:italic;color:rgba(245,230,200,.55);max-width:420px;line-height:1.9;text-align:center;}
.bub-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:1rem;}
.bub-btn{width:68px;height:68px;border-radius:50%;background:radial-gradient(circle at 35% 35%,rgba(201,168,76,.55),rgba(107,30,46,.25));border:2px solid rgba(201,168,76,.45);font-size:1.9rem;cursor:pointer;display:flex;align-items:center;justify-content:center;animation:bfloat 2.2s ease-in-out infinite;}
.bub-btn:nth-child(2){animation-delay:.35s;}
.bub-btn:nth-child(3){animation-delay:.7s;}
.bub-btn:nth-child(4){animation-delay:1.05s;}
.bub-btn:nth-child(5){animation-delay:1.4s;}
.bub-btn.popped{background:rgba(201,168,76,.06);border-style:dashed;opacity:.3;cursor:default;animation:none;}
@keyframes bfloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
.bub-score{font-family:'Cinzel',serif;font-size:.75rem;letter-spacing:2px;color:rgba(245,230,200,.45);}

/* QUIZ MODAL */
.quiz-ov{position:fixed;inset:0;z-index:1000;background:rgba(4,1,2,.93);backdrop-filter:blur(14px);display:none;align-items:center;justify-content:center;padding:1rem;}
.quiz-ov.show{display:flex;}
.quiz-box{background:rgba(22,6,12,.98);border:1px solid rgba(201,168,76,.28);border-radius:13px;padding:2.5rem;max-width:500px;width:100%;box-shadow:0 50px 100px rgba(0,0,0,.75);}
.quiz-title{font-family:'Cinzel Decorative',cursive;font-size:1.45rem;color:var(--gold);text-align:center;margin-bottom:.4rem;}
.quiz-prog-label{text-align:center;font-style:italic;color:rgba(245,230,200,.42);margin-bottom:1.2rem;font-size:.85rem;}
.quiz-prog-bar{height:3px;background:rgba(201,168,76,.1);border-radius:2px;margin-bottom:1.6rem;overflow:hidden;}
.quiz-prog-fill{height:100%;background:var(--gold);border-radius:2px;transition:width .5s ease;}
.quiz-q{font-size:1.05rem;line-height:1.75;color:var(--parchment);margin-bottom:.4rem;}
.quiz-hint{font-size:.78rem;color:rgba(201,168,76,.45);font-style:italic;margin-bottom:1.4rem;}
.quiz-inp{width:100%;padding:.8rem 1rem;background:rgba(8,2,5,.75);border:1px solid rgba(201,168,76,.22);border-radius:7px;color:var(--parchment);font-family:'IM Fell English',serif;font-size:.98rem;outline:none;margin-bottom:1rem;transition:border .3s;}
.quiz-inp:focus{border-color:rgba(201,168,76,.5);}
.qbtns{display:flex;gap:.9rem;}
.qbtn{flex:1;padding:.8rem;font-family:'Cinzel',serif;font-size:.72rem;letter-spacing:2px;text-transform:uppercase;border-radius:7px;cursor:pointer;transition:all .3s;}
.qbtn-main{background:linear-gradient(135deg,var(--maroon),#3D0D1A);border:1px solid var(--gold);color:var(--gold);}
.qbtn-main:hover{box-shadow:0 0 22px rgba(201,168,76,.22);}
.qbtn-ghost{background:transparent;border:1px solid rgba(245,230,200,.18);color:rgba(245,230,200,.45);}
.quiz-res{text-align:center;padding:1.3rem;border-radius:8px;margin-bottom:1rem;font-size:.95rem;}
.res-ok{background:rgba(40,120,40,.15);border:1px solid rgba(80,180,80,.25);color:#90ee90;}
.res-bad{background:rgba(130,40,40,.15);border:1px solid rgba(180,80,80,.25);color:#ffaaaa;}
.quiz-fin{text-align:center;padding:1.5rem 0;}
.quiz-fin-icon{font-size:3rem;margin-bottom:1rem;}
.quiz-fin-txt{font-size:1rem;line-height:1.75;color:rgba(245,230,200,.82);}
</style></head><body>
<div class="bg"></div>

<div class="topbar">
  <div class="tb-left">
    <a href="/chapters" class="tb-back">&larr; Chronicles</a>
    <span class="tb-badge">{{ chapter.icon }} {{ chapter.title.split(':')[0] }}</span>
  </div>
  <div class="tb-title">ELARIX</div>
  <div class="tb-right">
    <button class="topbtn topbtn-gold" onclick="startQuiz()">Quiz</button>
    <button class="topbtn topbtn-gold" onclick="window.location='/leaderboard'">Trophy</button>
    <button class="topbtn topbtn-dim" onclick="clearMsgs()">Clear</button>
    <span class="tb-user">{{ username }}</span>
    <button class="topbtn topbtn-dim" onclick="window.location='/logout'">Leave</button>
  </div>
</div>

<div class="wrap">
  <div class="sidebar">
    <div class="sb-sec">
      <div class="sb-head">Key Facts</div>
      <ul class="sb-facts">
        {% for f in chapter.key_facts %}<li>{{ f }}</li>{% endfor %}
      </ul>
    </div>
    <div class="mascot-area">
      <img id="mascot-img" src="/mascot/normal" alt="Elarix"
        onerror="this.style.display='none';document.getElementById('mascot-fallback').style.display='flex';">
      <div id="mascot-fallback" class="mascot-emoji mascot-normal" style="display:none;">🧙</div>
      <span id="mascot-cap">Awaiting your question...</span>
    </div>
    <div class="sb-sec">
      <div class="sb-head">Try asking</div>
      <button class="sug-item" onclick="quickAsk('Who were the Chera kings?')">Who were the Chera kings?</button>
      <button class="sug-item" onclick="quickAsk('Tell me about the spice trade')">Tell me about the spice trade</button>
      <button class="sug-item" onclick="quickAsk('What is Kalaripayattu?')">What is Kalaripayattu?</button>
      <button class="sug-item" onclick="quickAsk('Who was Vasco da Gama?')">Who was Vasco da Gama?</button>
      <button class="sug-item" onclick="quickAsk('Tell me about the Battle of Colachel')">Battle of Colachel</button>
      <button class="sug-item" onclick="quickAsk('What was the Temple Entry Proclamation?')">Temple Entry Proclamation</button>
    </div>
  </div>

  <div class="chat-col">
    <div class="msg-list" id="msg-list">
      <div class="msg-row is-bot">
        <div class="msg-av">E</div>
        <div>
          <div class="msg-who">Elarix - The Archivist</div>
          <div class="msg-bub">
            <div class="msg-txt">
              Greetings, <strong>{{ username }}</strong>. You have entered the scrolls of <strong>{{ chapter.title }}</strong>.<br><br>
              I am Elarix, keeper of Kerala's chronicles. Ask me anything about the people, rulers, events, trade, culture, or battles of this era.<br><br>
              <strong>Remember:</strong> Three transgressions of tongue shall cast you into the dungeon!
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="inp-bar">
      <textarea id="msg-inp" placeholder="Ask Elarix about {{ chapter.title }}..." rows="1"
        onkeydown="onKey(event)" oninput="growInp(this)"></textarea>
      <button id="voice-btn" onclick="toggleVoice()" title="Toggle Elarix voice on/off" style="padding:.75rem .9rem;background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.3);border-radius:8px;color:rgba(201,168,76,.6);cursor:pointer;font-size:1.1rem;transition:all .3s;flex-shrink:0;" title="Toggle voice">🔊</button>
      <button id="send-btn" onclick="doSend()">Send</button>
    </div>
  </div>
</div>

<!-- BUBBLE OVERLAY -->
<div class="bub-ov" id="bub-ov">
  <div class="bub-title">The Bubble Challenge</div>
  <div class="bub-desc">Pop all 5 enchanted bubbles to lift the dungeon's curse!</div>
  <div class="bub-grid">
    <div class="bub-btn" onclick="popOne(this)">O</div>
    <div class="bub-btn" onclick="popOne(this)">O</div>
    <div class="bub-btn" onclick="popOne(this)">O</div>
    <div class="bub-btn" onclick="popOne(this)">O</div>
    <div class="bub-btn" onclick="popOne(this)">O</div>
  </div>
  <div class="bub-score" id="bub-score">0 / 5 popped</div>
  <button onclick="forceExitBubbles()" style="margin-top:1rem;padding:.5rem 1.5rem;background:transparent;border:1px solid rgba(201,168,76,.3);color:rgba(201,168,76,.5);font-family:Cinzel,serif;font-size:.65rem;letter-spacing:2px;cursor:pointer;border-radius:4px;">EXIT PUNISHMENT</button>
</div>

<!-- QUIZ MODAL -->
<div class="quiz-ov" id="quiz-ov">
  <div class="quiz-box">
    <div class="quiz-title">The Scholar's Trial</div>
    <div class="quiz-prog-label" id="q-label">Question 1 of 3</div>
    <div class="quiz-prog-bar"><div class="quiz-prog-fill" id="q-fill" style="width:0%"></div></div>

    <div id="q-area">
      <div class="quiz-q" id="q-text"></div>
      <div class="quiz-hint" id="q-hint"></div>
      <input class="quiz-inp" id="q-inp" placeholder="Your answer, scholar..."
        onkeydown="if(event.key==='Enter') checkAnswer()">
      <div class="qbtns">
        <button class="qbtn qbtn-main" onclick="checkAnswer()">Submit Answer</button>
        <button class="qbtn qbtn-ghost" onclick="closeQuiz()">Close</button>
      </div>
    </div>

    <div id="q-res" style="display:none">
      <div class="quiz-res" id="q-res-box"></div>
      <div class="qbtns"><button class="qbtn qbtn-main" id="q-next">Next</button></div>
    </div>

    <div id="q-fin" style="display:none" class="quiz-fin">
      <div class="quiz-fin-icon" id="q-fin-icon"></div>
      <div class="quiz-fin-txt" id="q-fin-txt"></div>
      <div class="qbtns" style="margin-top:1.5rem">
        <button class="qbtn qbtn-main" onclick="closeQuiz()">Return to Archives</button>
      </div>
    </div>
  </div>
</div>

<script>
var CH = "{{ chapter_id }}";
var UN = "{{ username }}";
var busy = false;
var qIdx = 0;
var qTotal = 0;

// Emoji fallback for each expression (shown if image file missing)
var MASCOT_EMOJI = {
  normal: '🧙', thinking: '🤔', happy: '😄', angry: '😠', shocked: '😱', sad: '😢'
};
var MASCOT_CAPTION_DEFAULT = {
  normal: 'Ask me anything...', thinking: 'Consulting the scrolls...',
  happy: 'Splendid!', angry: 'Watch your tongue!', shocked: 'By the scrolls!', sad: 'Oh dear...'
};
var mascotHasImage = null; // null=unknown, true=yes, false=no

function setMascot(expr, cap) {
  var img = document.getElementById('mascot-img');
  var label = document.getElementById('mascot-cap');
  var fallback = document.getElementById('mascot-fallback');
  if (!label) return;

  var caption = cap || MASCOT_CAPTION_DEFAULT[expr] || '';
  label.style.opacity = '0';
  setTimeout(function(){ label.textContent = caption; label.style.opacity = '1'; }, 150);

  if (!img) return;

  // Fade out
  img.style.opacity = '0';
  img.style.transform = 'scale(0.9)';

  setTimeout(function(){
    var newSrc = '/mascot/' + expr + '?v=' + Date.now();
    var testImg = new Image();
    testImg.onload = function() {
      // Image loaded successfully
      mascotHasImage = true;
      if (fallback) fallback.style.display = 'none';
      img.style.display = 'block';
      img.src = newSrc;
      img.style.opacity = '1';
      img.style.transform = 'scale(1)';
    };
    testImg.onerror = function() {
      // No image file — show emoji fallback instead
      mascotHasImage = false;
      img.style.display = 'none';
      if (fallback) {
        fallback.style.display = 'flex';
        fallback.textContent = MASCOT_EMOJI[expr] || '🧙';
        fallback.className = 'mascot-emoji mascot-' + expr;
      }
    };
    testImg.src = newSrc;
  }, 200);
}

function onKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); doSend(); }
}
function growInp(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 110) + 'px';
}
function quickAsk(t) {
  document.getElementById('msg-inp').value = t;
  doSend();
}

function doSend() {
  var inp = document.getElementById('msg-inp');
  var txt = inp.value.trim();
  if (!txt || busy) return;
  addMsg('user', txt);
  inp.value = '';
  inp.style.height = 'auto';
  busy = true;
  document.getElementById('send-btn').disabled = true;
  setMascot('thinking', 'Consulting the scrolls...');
  var tid = addDots();
  fetch('/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: txt, chapter: CH})
  })
  .then(function(r){ return r.json(); })
  .then(function(d){
    removeDots(tid);
    if (d.type === 'bubble') {
      showBubbles();
      setMascot('happy', 'Pop the bubbles!');
    } else if (d.type === 'warning') {
      setMascot('angry', 'Watch your tongue!');
      addMsg('bot', d.message);
    } else if (d.type === 'dungeon_start') {
      setMascot('shocked', 'To the dungeon!');
      addMsg('bot', d.message);
    } else if (d.type === 'dungeon') {
      setMascot('shocked', 'Solve the riddle!');
      addMsg('bot', d.message);
    } else if (d.type === 'riddle_correct') {
      setMascot('happy', 'Well done!');
      addMsg('bot', d.message);
    } else if (d.type === 'wiki') {
      setMascot('thinking', 'Found it in Wikipedia!');
      addMsg('bot', d.message);
    } else if (d.type === 'irritated') {
      setMascot('angry', 'Ask something relevant!');
      addMsg('bot', d.message);
    } else {
      setMascot('normal', 'Ask me anything...');
      addMsg('bot', d.message);
    }
  })
  .catch(function(){
    removeDots(tid);
    setMascot('sad', 'Something went wrong...');
    addMsg('bot', 'The scrolls are unreachable. Please try again.');
  })
  .finally(function(){
    busy = false;
    document.getElementById('send-btn').disabled = false;
  });
}

// ── VOICE SYSTEM ─────────────────────────────────────────────
var voiceOn = true;
var elarixVoice = null;

function loadVoice() {
  var voices = window.speechSynthesis.getVoices();
  if (!voices.length) return;
  // Priority: female English voices
  var preferred = [
    "Google UK English Female",
    "Microsoft Hazel - English (United Kingdom)",
    "Microsoft Zira - English (United States)",
    "Samantha",
    "Karen",
    "Moira",
    "Tessa",
    "Victoria",
  ];
  for (var i = 0; i < preferred.length; i++) {
    var v = voices.find(function(v){ return v.name === preferred[i]; });
    if (v) { elarixVoice = v; break; }
  }
  // Fallback: any female-sounding en-GB voice
  if (!elarixVoice) {
    elarixVoice = voices.find(function(v){
      return v.lang === 'en-GB' && (v.name.toLowerCase().includes('female') || 
             v.name.includes('Hazel') || v.name.includes('Susan'));
    });
  }
  // Fallback: any en-GB voice
  if (!elarixVoice) {
    elarixVoice = voices.find(function(v){ return v.lang === 'en-GB'; });
  }
  // Fallback: any English voice
  if (!elarixVoice) {
    elarixVoice = voices.find(function(v){ return v.lang.startsWith('en'); });
  }
}

window.speechSynthesis.onvoiceschanged = loadVoice;
loadVoice();

function toggleVoice() {
  voiceOn = !voiceOn;
  var btn = document.getElementById('voice-btn');
  btn.textContent = voiceOn ? '🔊' : '🔇';
  btn.style.color = voiceOn ? 'rgba(201,168,76,.9)' : 'rgba(201,168,76,.4)';
  btn.style.borderColor = voiceOn ? 'rgba(201,168,76,.6)' : 'rgba(201,168,76,.2)';
  if (!voiceOn) window.speechSynthesis.cancel();
}

function speakText(text) {
  if (!voiceOn || !window.speechSynthesis) return;
  // Strip markdown formatting for cleaner speech
  var clean = text
    .replace(/[*][*]([^*]+)[*][*]/g, '$1')
    .replace(/[*]([^*]+)[*]/g, '$1')
    .replace(/A scroll whispers:[\s\S]*$/, '')
    .replace(/\n+/g, '. ')
    .trim();
  if (!clean) return;
  window.speechSynthesis.cancel(); // stop any current speech
  var utt = new SpeechSynthesisUtterance(clean);
  if (elarixVoice) utt.voice = elarixVoice;
  utt.pitch = 1.1;    // slightly higher = female, wise
  utt.rate = 0.88;    // slightly slower = dramatic
  utt.volume = 1.0;
  window.speechSynthesis.speak(utt);
}

function addMsg(role, text) {
  var list = document.getElementById('msg-list');
  var row = document.createElement('div');
  row.className = 'msg-row ' + (role === 'bot' ? 'is-bot' : 'is-user');
  var av = role === 'bot' ? 'E' : UN[0].toUpperCase();
  var who = role === 'bot' ? 'Elarix - The Archivist' : UN;
  row.innerHTML =
    '<div class="msg-av">' + av + '</div>' +
    '<div><div class="msg-who">' + who + '</div>' +
    '<div class="msg-bub"><div class="msg-txt">' + fmtText(text) + '</div></div></div>';
  list.appendChild(row);
  list.scrollTop = list.scrollHeight;
  if (role === 'bot') speakText(text);
}

function fmtText(t) {
  t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  t = t.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  t = t.replace(/\n/g, '<br>');
  return t;
}

function addDots() {
  var id = 'dots-' + Date.now();
  var list = document.getElementById('msg-list');
  var row = document.createElement('div');
  row.id = id;
  row.className = 'msg-row is-bot';
  row.innerHTML = '<div class="msg-av">E</div><div><div class="msg-bub"><div class="dots"><span></span><span></span><span></span></div></div></div>';
  list.appendChild(row);
  list.scrollTop = list.scrollHeight;
  return id;
}

function removeDots(id) {
  var el = document.getElementById(id);
  if (el) el.remove();
}

function clearMsgs() {
  document.getElementById('msg-list').innerHTML = '';
  addMsg('bot', 'The scrolls are cleared. A fresh chapter begins. What would you ask, seeker?');
  setMascot('normal', 'Ask me anything...');
}

function showBubbles() {
  // reset all bubbles visually
  document.querySelectorAll('.bub-btn').forEach(function(b){
    b.classList.remove('popped');
    b.textContent = 'O';
    b.style.opacity = '1';
    b.style.pointerEvents = 'auto';
  });
  document.getElementById('bub-score').textContent = '0 / 5 popped';
  document.getElementById('bub-ov').classList.add('show');
}

function popOne(btn) {
  if (btn.classList.contains('popped')) return;
  btn.classList.add('popped');
  btn.textContent = '✦';
  btn.style.opacity = '0.4';
  btn.style.pointerEvents = 'none';

  // Count popped bubbles purely on frontend — no server needed
  var popped = document.querySelectorAll('.bub-btn.popped').length;
  document.getElementById('bub-score').textContent = popped + ' / 5 popped';

  if (popped >= 5) {
    // Tell server to clear bubble_mode, then close overlay
    setTimeout(function(){
      fetch('/api/bubble/reset', {method:'POST', headers:{'Content-Type':'application/json'}})
        .catch(function(){}) // ignore errors, close anyway
        .finally(function(){
          closeBubbles("*Elarix watches the last bubble pop with a satisfied nod.*\n\n**Very well.** You have served your punishment. The archives are open to you again. Choose your words more carefully this time!");
        });
    }, 500);
  }
}

function closeBubbles(msg) {
  document.getElementById('bub-ov').classList.remove('show');
  busy = false;
  setMascot('happy', 'Freedom at last!');
  if (msg) addMsg('bot', msg);
}

function forceExitBubbles() {
  fetch('/api/bubble/reset', {method:'POST', headers:{'Content-Type':'application/json'}})
  .then(function(){
    closeBubbles("*Elarix sighs and waves you through.*\n\nVery well. The punishment is lifted. Don't make me regret this.");
  })
  .catch(function(){
    closeBubbles('');
  });
}



function startQuiz() {
  fetch('/api/quiz/start', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({chapter: CH})
  })
  .then(function(r){
    if (!r.ok) { alert('Quiz failed to load (server error ' + r.status + ')'); return null; }
    return r.json();
  })
  .then(function(d){
    if (!d) return;
    if (d.error) { alert('Quiz error: ' + d.error); return; }
    qIdx = 0; qTotal = d.total;
    // Reset all panels
    document.getElementById('q-area').style.display = 'block';
    document.getElementById('q-res').style.display = 'none';
    document.getElementById('q-fin').style.display = 'none';
    // Set question content BEFORE showing modal
    document.getElementById('q-text').textContent = d.question;
    document.getElementById('q-hint').textContent = 'Hint: ' + d.hint;
    document.getElementById('q-label').textContent = 'Question 1 of ' + d.total;
    document.getElementById('q-fill').style.width = '0%';
    document.getElementById('q-inp').value = '';
    // Show modal
    document.getElementById('quiz-ov').classList.add('show');
    setMascot('thinking', 'Quiz time!');
    setTimeout(function(){ document.getElementById('q-inp').focus(); }, 300);
  })
  .catch(function(err){
    alert('Could not connect to quiz. Make sure you are logged in and try again.');
    console.error('Quiz error:', err);
  });
}

function setQ(q, hint, idx, total) {
  document.getElementById('q-text').textContent = q;
  document.getElementById('q-hint').textContent = 'Hint: ' + hint;
  document.getElementById('q-label').textContent = 'Question ' + (idx+1) + ' of ' + total;
  document.getElementById('q-fill').style.width = ((idx/total)*100) + '%';
  document.getElementById('q-inp').value = '';
  setTimeout(function(){ document.getElementById('q-inp').focus(); }, 100);
}

function checkAnswer() {
  var ans = document.getElementById('q-inp').value.trim();
  if (!ans) { document.getElementById('q-inp').focus(); return; }
  var btn = document.querySelector('#q-area .qbtn-main');
  if (btn) btn.disabled = true;
  fetch('/api/quiz', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({chapter: CH, answer: ans, q_index: qIdx})
  })
  .then(function(r){ return r.json(); })
  .then(function(d){
    if (btn) btn.disabled = false;
    document.getElementById('q-area').style.display = 'none';
    document.getElementById('q-res').style.display = 'block';
    var rb = document.getElementById('q-res-box');
    rb.className = 'quiz-res ' + (d.correct ? 'res-ok' : 'res-bad');
    rb.textContent = d.correct
      ? 'Correct! The ancient scrolls confirm your wisdom.'
      : 'Not quite. The scrolls tell a different story.';
    document.getElementById('q-fill').style.width = (((qIdx+1)/qTotal)*100) + '%';
    var nxt = document.getElementById('q-next');
    if (d.done) {
      nxt.textContent = 'See Results';
      nxt.onclick = function(){ showFinal(d.final_score, d.total); };
    } else {
      qIdx++;
      nxt.textContent = 'Next Question';
      nxt.onclick = function(){
        document.getElementById('q-text').textContent = d.next_q.q;
        document.getElementById('q-hint').textContent = 'Hint: ' + d.next_q.hint;
        document.getElementById('q-label').textContent = 'Question ' + (qIdx+1) + ' of ' + qTotal;
        document.getElementById('q-inp').value = '';
        document.getElementById('q-area').style.display = 'block';
        document.getElementById('q-res').style.display = 'none';
        setTimeout(function(){ document.getElementById('q-inp').focus(); }, 100);
      };
    }
  })
  .catch(function(err){
    if (btn) btn.disabled = false;
    alert('Error submitting answer. Please try again.');
  });
}

function showFinal(score, total) {
  document.getElementById('q-res').style.display = 'none';
  document.getElementById('q-fin').style.display = 'block';
  document.getElementById('q-fill').style.width = '100%';
  var pct = score / total;
  if (pct === 1) {
    setMascot('happy', 'Perfect score!');
    document.getElementById('q-fin-icon').textContent = '🏆';
    document.getElementById('q-fin-txt').textContent = 'Perfect! ' + score + '/' + total + ' - You are a true Master of the Chronicles!';
  } else if (pct >= 0.6) {
    setMascot('happy', 'Well done!');
    document.getElementById('q-fin-icon').textContent = '📜';
    document.getElementById('q-fin-txt').textContent = 'Well done! ' + score + '/' + total + ' - A fine scholar of Kerala history.';
  } else {
    setMascot('sad', 'Study more, seeker...');
    document.getElementById('q-fin-icon').textContent = '📚';
    document.getElementById('q-fin-txt').textContent = score + '/' + total + ' - Return to the scrolls and study further, seeker.';
  }
}

function closeQuiz() {
  document.getElementById('quiz-ov').classList.remove('show');
}

document.getElementById('msg-inp').focus();
</script>
</body></html>"""

LEADERBOARD_HTML = r"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scrolls of Fame - Elarix</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Cinzel:wght@400;600&family=IM+Fell+English:ital@0;1&display=swap" rel="stylesheet">
<style>
:root{--maroon:#6B1E2E;--deep:#100308;--gold:#C9A84C;--parchment:#F5E6C8;}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--deep);font-family:'IM Fell English',serif;color:var(--parchment);min-height:100vh;}
.bg{position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse 60% 50% at 50% 0%,rgba(107,30,46,.22),transparent 60%),linear-gradient(170deg,#060102,#100308);}
nav{position:fixed;top:0;left:0;right:0;z-index:100;display:flex;justify-content:space-between;align-items:center;padding:1rem 2.5rem;background:rgba(5,1,2,.94);border-bottom:1px solid rgba(201,168,76,.12);backdrop-filter:blur(14px);}
.nav-logo{font-family:'Cinzel Decorative',cursive;font-size:.95rem;color:var(--gold);text-decoration:none;letter-spacing:2.5px;}
nav a:not(.nav-logo){font-family:'Cinzel',serif;font-size:.65rem;color:rgba(245,230,200,.5);text-decoration:none;letter-spacing:2.5px;text-transform:uppercase;margin-left:1.8rem;transition:color .3s;}
nav a:not(.nav-logo):hover{color:var(--gold);}
.page{position:relative;z-index:10;max-width:780px;margin:0 auto;padding:7rem 1.5rem 4rem;}
h1{font-family:'Cinzel Decorative',cursive;font-size:clamp(1.8rem,5vw,3.2rem);color:var(--gold);text-align:center;margin-bottom:.5rem;}
.page-sub{text-align:center;font-style:italic;color:rgba(245,230,200,.45);margin-bottom:2.8rem;line-height:1.85;}
.divider{width:150px;height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent);margin:0 auto 2.5rem;}
.lb-wrap{background:rgba(38,10,18,.9);border:1px solid rgba(201,168,76,.18);border-radius:11px;overflow:hidden;box-shadow:0 35px 70px rgba(0,0,0,.55);}
.lb-head{display:grid;grid-template-columns:55px 1fr 1fr 65px 130px;gap:1rem;padding:.75rem 1.5rem;background:rgba(201,168,76,.07);border-bottom:1px solid rgba(201,168,76,.14);}
.lb-head span{font-family:'Cinzel',serif;font-size:.58rem;letter-spacing:3px;text-transform:uppercase;color:rgba(201,168,76,.55);}
.lb-row{display:grid;grid-template-columns:55px 1fr 1fr 65px 130px;gap:1rem;padding:.95rem 1.5rem;border-bottom:1px solid rgba(201,168,76,.06);align-items:center;transition:background .25s;}
.lb-row:last-child{border-bottom:none;}
.lb-row:hover{background:rgba(201,168,76,.04);}
.lb-rank{font-family:'Cinzel',serif;font-size:1rem;text-align:center;color:rgba(245,230,200,.35);}
.lb-rank.r1{color:#FFD700;font-weight:bold;}
.lb-rank.r2{color:#C0C0C0;}
.lb-rank.r3{color:#CD7F32;}
.lb-name{font-family:'Cinzel',serif;font-size:.82rem;color:var(--parchment);}
.lb-name.is-me{color:var(--gold);}
.lb-ch{font-size:.78rem;color:rgba(245,230,200,.45);font-style:italic;}
.lb-sc{font-family:'Cinzel Decorative',cursive;font-size:1.1rem;color:var(--gold);text-align:center;}
.lb-dt{font-size:.72rem;color:rgba(245,230,200,.3);}
.lb-empty{text-align:center;padding:3rem;font-style:italic;color:rgba(245,230,200,.38);line-height:2;}
.back-area{text-align:center;margin-top:2.5rem;}
.back-area a{font-family:'Cinzel',serif;font-size:.72rem;letter-spacing:3px;text-transform:uppercase;color:var(--gold);text-decoration:none;padding:.8rem 2rem;border:1px solid rgba(201,168,76,.28);border-radius:6px;transition:all .3s;}
.back-area a:hover{background:rgba(201,168,76,.07);}
</style></head><body>
<div class="bg"></div>
<nav>
  <a href="/chapters" class="nav-logo">ZUCHINNI.AI</a>
  <div><a href="/chapters">Chronicles</a><a href="/logout">Depart</a></div>
</nav>
<div class="page">
  <h1>Scrolls of Fame</h1>
  <div class="divider"></div>
  <p class="page-sub">"The scholars who have proven their mastery of Kerala's ancient chronicles."</p>
  <div class="lb-wrap">
    {% if scores %}
    <div class="lb-head"><span>Rank</span><span>Scholar</span><span>Chronicle</span><span>Score</span><span>Date</span></div>
    {% for e in scores %}
    <div class="lb-row">
      <div class="lb-rank {% if loop.index==1 %}r1{% elif loop.index==2 %}r2{% elif loop.index==3 %}r3{% endif %}">{{ loop.index }}</div>
      <div class="lb-name {% if e.username==username %}is-me{% endif %}">{{ e.username }}</div>
      <div class="lb-ch">{{ e.chapter[:30] }}{% if e.chapter|length > 30 %}...{% endif %}</div>
      <div class="lb-sc">{{ e.score }}/3</div>
      <div class="lb-dt">{{ e.date }}</div>
    </div>
    {% endfor %}
    {% else %}
    <div class="lb-empty">The Scrolls of Fame await their first scholar.<br>Complete a quiz to claim your place!</div>
    {% endif %}
  </div>
  <div class="back-area"><a href="/chapters">&larr; Return to Chronicles</a></div>
</div>
</body></html>"""

# ── ROUTES ───────────────────────────────────────────────────
@app.route("/")
def index():
    if "username" in session: return redirect(url_for("chapters"))
    return render_template_string(LANDING_HTML)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        d = request.get_json()
        users = get_users()
        u = d.get("username","").strip()
        if u in users and users[u]["password"] == hash_pw(d.get("password","")):
            session["username"] = u; init_session()
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Invalid name or passphrase"})
    return render_template_string(AUTH_HTML, mode="login")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        d = request.get_json()
        users = get_users()
        u = d.get("username","").strip()
        pw = d.get("password","")
        if not u or len(pw) < 4:
            return jsonify({"success": False, "error": "Name required and passphrase min 4 chars"})
        if u in users:
            return jsonify({"success": False, "error": "That name is already taken"})
        users[u] = {"password": hash_pw(pw), "joined": datetime.now().isoformat()}
        save_users(users); session["username"] = u; init_session()
        return jsonify({"success": True})
    return render_template_string(AUTH_HTML, mode="signup")

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("index"))

@app.route("/chapters")
def chapters():
    if "username" not in session: return redirect(url_for("index"))
    return render_template_string(CHAPTERS_HTML, chapters=KNOWLEDGE, username=session["username"])

@app.route("/chat/<chapter_id>")
def chat(chapter_id):
    if "username" not in session: return redirect(url_for("index"))
    if chapter_id not in KNOWLEDGE: return redirect(url_for("chapters"))
    # Always reset bubble/dungeon on page load — prevents getting permanently stuck
    session["bubble_mode"] = False
    session["bubble_score"] = 0
    session["dungeon"] = False
    session["dungeon_until"] = 0
    session["riddle"] = None
    session["anger"] = 0
    session["irrelevant"] = 0
    session.modified = True
    return render_template_string(CHAT_HTML, chapter_id=chapter_id,
        chapter=KNOWLEDGE[chapter_id], username=session["username"])

@app.route("/leaderboard")
def leaderboard():
    if "username" not in session: return redirect(url_for("index"))
    return render_template_string(LEADERBOARD_HTML, scores=get_scores(), username=session["username"])

@app.route("/api/chat", methods=["POST"])
def api_chat():
    if "username" not in session: return jsonify({"error":"Not logged in"}), 401
    init_session()
    d = request.get_json()
    message = d.get("message","").strip()
    chapter = d.get("chapter","")
    now = time.time()
    name = session["username"]

    if session["bubble_mode"]:
        return jsonify({"type":"bubble","message":"Pop all the bubbles first to continue!"})

    if session["dungeon"]:
        if now < session["dungeon_until"]:
            rem = int(session["dungeon_until"] - now)
            return jsonify({"type":"dungeon",
                "message":"The chains hold firm... **" + str(rem) + "** seconds remain.\n\n" +
                          session["riddle"]["q"] + "\n\nHint: " + session["riddle"]["hint"]})
        riddle = session["riddle"]
        if riddle and any(a in message.lower() for a in riddle["a"]):
            session["dungeon"] = False; session["bubble_mode"] = True
            session["bubble_score"] = 0; session.modified = True
            return jsonify({"type":"riddle_correct",
                "message":"**The answer rings true!** The dungeon doors groan open...\n\nNow pop **5 enchanted bubbles** to lift the curse!"})
        return jsonify({"type":"dungeon",
            "message":"That is not the answer the dungeon demands.\n\n" +
                      riddle["q"] + "\n\nHint: " + riddle["hint"]})

    if profanity.contains_profanity(message):
        session["anger"] += 1; session.modified = True
        if session["anger"] >= 3:
            riddle = random.choice(RIDDLES)
            session["dungeon"] = True; session["dungeon_until"] = now + 20
            session["riddle"] = riddle; session.modified = True
            return jsonify({"type":"dungeon_start",
                "message":"**ENOUGH!** Three transgressions! You are cast into the **DUNGEON for 20 seconds!**\n\nSolve this riddle:\n\n**" +
                          riddle["q"] + "**\n\nHint: " + riddle["hint"]})
        w = 3 - session["anger"]
        return jsonify({"type":"warning",
            "message":"Mind your tongue in these sacred halls. **" + str(w) + "** warning(s) remain."})

    lo = message.lower().strip()
    words = set(lo.split())  # individual words for exact matching

    # GREETINGS — only trigger on short pure greetings, not mid-sentence
    GREET_WORDS = {"hi","hello","hey","greetings","namaste","sup","howdy","yo","hiya","heya"}
    is_greeting = (
        words & GREET_WORDS and len(lo) < 25
    ) or lo in ["good day","whats up","what's up","good morning","good evening","good afternoon"]
    if is_greeting:
        return jsonify({"type":"answer","message":random.choice([
            "Ah, **" + name + "**! *Elarix looks up from his crumbling parchment.* Welcome back to the archives! What Kerala wisdom do you seek today?",
            "Well met, **" + name + "**! The candles are lit, the scrolls are open. Ask away, young scholar!",
            "Greetings, **" + name + "**! *Elarix adjusts his spectacles and cracks his knuckles.* What would you like to learn about Kerala history?",
        ])})

    # NAME
    if any(w in lo for w in ["your name","who are you","what are you","introduce yourself","what is your name","who r u","ur name","whos elarix","who is elarix"]):
        return jsonify({"type":"answer","message":random.choice([
            "I am **Elarix**, Ancient Archivist of Kerala! For **847 years** I have guarded these scrolls. My name means *keeper of forgotten truths* in the old tongue — though my mother simply called me *Eli*.",
            "**Elarix** is my name! Scribe, scholar, archivist, and occasional dungeon-warden. I have memorised every king, every battle, and every spice route in Kerala. Pleased to meet you, **" + name + "**!",
        ])})

    # AGE
    if any(w in lo for w in ["how old are you","how old r u","your age","ur age","when were you born","your birthday"]):
        return jsonify({"type":"answer","message":random.choice([
            "*Elarix strokes his very long beard.*\n\nI have been alive since the **Chera Dynasty** — approximately **847 years**. Though I stopped counting after the first few centuries. The scrolls keep me young!",
            "I was born in **1177 CE**, just after the fall of the Chera kingdom. Watching empires rise and fall does wonders for one's perspective. I am **847 years old**, give or take a decade!",
        ])})

    # HOBBIES
    if any(w in lo for w in ["hobby","hobbies","free time","pastime","what do you enjoy","ur hobbies","ur hobby","do for fun","do you do for fun"]):
        return jsonify({"type":"answer","message":random.choice([
            "*Elarix leans back in his ancient chair with delight.*\n\nAh, my hobbies! I enjoy:\n\n**1.** Reading ancient scrolls (obviously)\n**2.** Cataloguing spice trade routes\n**3.** Arguing with historians who get Kerala history wrong\n**4.** Feeding my pet crow, Kali\n**5.** Occasionally locking rude visitors in the dungeon\n\nSimple pleasures for a simple archivist!",
            "In my spare time I enjoy **writing new scrolls**, **sharpening my quill**, and **eavesdropping on merchants** to learn the latest trade gossip. I also recently took up **Kalaripayattu** — I am not very good at it. My back hurts.",
        ])})

    # FAVOURITE SUBJECT
    if any(w in lo for w in ["favourite subject","favorite subject","fav subject","best subject","fav sub","ur subject","your subject"]):
        return jsonify({"type":"answer","message":"*Elarix gasps dramatically.*\n\n**History**, obviously! Specifically the **maritime history of Kerala** — spice routes, the Zamorin's navy, the Kunjali Marakkars. Pure poetry.\n\nI also secretly enjoy **mathematics** — calculating how many Roman coins were exchanged for a sack of pepper is deeply satisfying.\n\nMy **least** favourite subject? Physical education. Have you seen these robes? Not designed for running."})

    # FAVOURITE FOOD
    if any(w in lo for w in ["favourite food","favorite food","fav food","what do you eat","ur food","your food"]):
        return jsonify({"type":"answer","message":random.choice([
            "*Elarix pats his stomach fondly.*\n\nMy absolute favourite is **Kerala Sadya** — the grand feast served on a banana leaf. Rice, sambar, avial, payasam... magnificent.\n\nI also have a weakness for **black pepper chicken** — fitting, given that pepper built this entire civilisation! I avoid Portuguese food on principle.",
            "Being an 847-year-old archivist, I have eaten at the tables of kings! My favourite is **fish curry with rice** — a Kerala staple. I once had dinner with the Zamorin himself. He had terrible table manners.",
        ])})

    # FAVOURITE COLOUR
    if any(w in lo for w in ["favourite colour","favorite colour","fav colour","favorite color","favourite color","fav color","what colour","what color","ur colour","ur color"]):
        return jsonify({"type":"answer","message":"*Elarix gestures dramatically at the room.*\n\n**Gold** — obviously! The colour of the Chera Dynasty's glory, of spice trade wealth, of candlelight on ancient parchment.\n\nAlso **deep maroon** — the colour of royal Kerala silk.\n\nMy least favourite? **Orange** — it reminds me of the Dutch East India Company's flag, and we all know how *that* ended for them at Colachel!"})

    # HOW ARE YOU
    if any(w in lo for w in ["how are you","how r u","are you okay","how are u","u ok","you alright","hows it going","how you doing","how r u doing"]):
        return jsonify({"type":"answer","message":random.choice([
            "*Elarix dramatically places hand on chest.*\n\nI am **magnificent**, thank you for asking, **" + name + "**! The scrolls are organised, the candles are lit, and no one has been rude enough for the dungeon today. A splendid day!",
            "Honestly? My back aches from 847 years of hunching over scrolls, and my crow Kali ate three of my best parchments this morning.\n\nBut seeing a scholar like **" + name + "** eager to learn Kerala history? *That* makes it all worthwhile.",
            "I am **deeply well**, **" + name + "**! Though slightly grumpy — someone asked me what Minecraft is yesterday. I sent them to the dungeon.",
        ])})

    # COMPLIMENTS
    if any(w in lo for w in ["good job","well done","great job","amazing","awesome","you rock","you are great","ur great","love you","you are the best","ur the best"]):
        return jsonify({"type":"answer","message":random.choice([
            "*Elarix blushes beneath his ancient beard.*\n\nOh my... **" + name + "**, you are too kind! 847 years and this is still the best part of the job. Now — shall we celebrate with some Kerala history?",
            "Why thank you, **" + name + "**! *Elarix does a small undignified victory shuffle.* You have made this old archivist very happy indeed!",
        ])})

    # INAPPROPRIATE / WEIRD QUESTIONS — respond in character instead of glitching
    INAPPROPRIATE = ["femboy","nsfw","sexy","naked","nude","porn","sex","hot girl","hot guy",
                     "girlfriend","boyfriend","kiss me","marry me","are you hot","are you cute",
                     "do you like me","flirt","hookup","naughty","dirty","inappropriate"]
    if any(w in lo for w in INAPPROPRIATE):
        return jsonify({"type":"answer","message":random.choice([
            "*Elarix slams his scroll shut and stares at you over his spectacles.*\n\n**Absolutely not.** I am an 847-year-old archivist, not an entertainment device. Ask me about Kerala history or I shall note this in the disciplinary scrolls.",
            "*Elarix raises both eyebrows so high they disappear into his hood.*\n\nSeeker, I have been alive since the **Chera Dynasty**. I have NO time for this nonsense. Shall we return to the chronicles?",
            "*Elarix coughs disapprovingly and adjusts his robes.*\n\nI did not guard these scrolls for **847 years** to answer THAT. Ask something worthy of the archives.",
        ])})

    # MILD INSULTS
    if any(w in lo for w in ["you are dumb","you are stupid","you are useless","you suck","shut up","you are boring","ur dumb","ur stupid","ur useless","ur boring"]):
        return jsonify({"type":"answer","message":random.choice([
            "*Elarix raises one very long eyebrow slowly.*\n\nI have survived the fall of the Chera Dynasty, three invasions, and 847 years of difficult students, **" + name + "**.\n\nYour words wound me not. The dungeon, however, is always available.",
            "Dumb? **DUMB?!** I have memorised every Kerala king since 800 CE! *Elarix huffs and straightens his robes.* I shall let that pass. **This time.**",
        ])})

    # THANKS
    if len(lo) < 20 and any(w in lo for w in ["thank you","thanks","thx","ty","thank u","cheers","thankyou"]):
        return jsonify({"type":"answer","message":random.choice([
            "*Elarix bows with a gracious sweep of his robes.*\n\nYou are most welcome, **" + name + "**! It is my honour to share the chronicles of Kerala. Come back anytime — the archives never close!",
            "Think nothing of it, **" + name + "**! Sharing Kerala's history is what I live for — literally, for 847 years. Now go forth and impress your teachers!",
        ])})

    # BYE
    if len(lo) < 25 and any(w in lo for w in ["bye","goodbye","see you","cya","take care","farewell","good night","goodnight","gtg","got to go","gotta go"]):
        return jsonify({"type":"answer","message":random.choice([
            "*Elarix stands and bows deeply.*\n\nFarewell, **" + name + "**! May the wisdom of Kerala's ancient kings guide your path. The archives will be here when you return!",
            "Goodbye, **" + name + "**! *Elarix waves dramatically with his quill, spattering ink everywhere.* Safe travels, young scholar. Kali says goodbye too!",
        ])})

    # LOCAL KNOWLEDGE
    answer = search(message, chapter)
    if answer:
        session["irrelevant"] = 0
        session["anger"] = 0  # reset anger on good messages so dungeon doesn't appear randomly
        session.modified = True
        return jsonify({"type":"answer","message":answer})

    # GOOGLE / WIKIPEDIA FOR HISTORY QUESTIONS
    HISTORY_KEYWORDS = [
        "who","what","when","where","why","how","tell me","explain",
        "dynasty","king","queen","ruler","empire","war","battle","history",
        "kerala","india","british","portuguese","dutch","chera","zamorin",
        "trade","spice","temple","religion","culture","art","dance","martial",
        "independence","colonial","revolution","ancient","medieval","century",
        "year","period","era","time","event","place","person","leader","general"
    ]
    is_history = any(kw in lo for kw in HISTORY_KEYWORDS)
    if is_history:
        wiki = google_search(message) or wikipedia_search(message)
        if wiki:
            session["irrelevant"] = 0; session.modified = True
            return jsonify({"type":"wiki","message":wiki})

    # IRRELEVANT COUNTER
    session["irrelevant"] = session.get("irrelevant", 0) + 1
    session.modified = True
    irr = session["irrelevant"]

    if irr == 1:
        return jsonify({"type":"irritated",
            "message":"*Elarix raises an eyebrow...*\n\nHmm. The scrolls do not speak on that. Ask me about the **rulers, trade, culture, battles, or events** of this chapter."})
    elif irr == 2:
        return jsonify({"type":"irritated",
            "message":"*Elarix taps the tome impatiently...*\n\nSeeker, you test my patience. I cannot find that in these scrolls. Ask something **relevant to this chapter's history**."})
    else:
        session["irrelevant"] = 0
        session["bubble_mode"] = True
        session["bubble_score"] = 0
        session.modified = True
        return jsonify({"type":"bubble",
            "message":"*Elarix SLAMS the great tome shut!*\n\n**ENOUGH of this nonsense!** You have wasted the archivist's time with irrelevant babble three times!\n\nAs punishment — pop **5 enchanted bubbles** before you may speak again!"})

@app.route("/api/bubble", methods=["POST"])
def api_bubble():
    if "username" not in session: return jsonify({"error":"Not logged in"}), 401
    session["bubble_score"] = session.get("bubble_score", 0) + 1
    session.modified = True
    score = session["bubble_score"]
    if score >= 5:
        session["bubble_mode"] = False
        session["bubble_score"] = 0
        session["anger"] = 0
        session["irrelevant"] = 0
        session.modified = True
        return jsonify({"score": 5, "done": True,
            "message": "*Elarix watches the last bubble pop with a satisfied nod.*\n\n**Very well.** You have served your punishment. The archives are open to you again, **" + session["username"] + "**. Choose your words more carefully this time."})
    return jsonify({"score": score, "done": False})

@app.route("/api/bubble/reset", methods=["POST"])
def api_bubble_reset():
    """Emergency reset — clears bubble mode from session"""
    if "username" not in session: return jsonify({"ok": True})
    session["bubble_mode"] = False
    session["bubble_score"] = 0
    session["irrelevant"] = 0
    session["anger"] = 0
    session.modified = True
    return jsonify({"ok": True})

@app.route("/api/session/state")
def session_state():
    """Returns current session state so JS can restore UI on page reload"""
    if "username" not in session: return jsonify({"bubble_mode": False, "dungeon": False})
    return jsonify({
        "bubble_mode": session.get("bubble_mode", False),
        "dungeon": session.get("dungeon", False),
        "dungeon_until": session.get("dungeon_until", 0),
    })

@app.route("/api/quiz/start", methods=["POST"])
def quiz_start():
    if "username" not in session: return jsonify({"error":"Not logged in"}), 401
    d = request.get_json()
    cid = d.get("chapter","")
    if cid not in KNOWLEDGE: return jsonify({"error":"Chapter not found"}), 404
    session["quiz_score"] = 0; session.modified = True
    q = KNOWLEDGE[cid]["quiz"][0]
    return jsonify({"question":q["q"],"hint":q["hint"],"total":len(KNOWLEDGE[cid]["quiz"])})

@app.route("/api/quiz", methods=["POST"])
def quiz_answer():
    if "username" not in session: return jsonify({"error":"Not logged in"}), 401
    d = request.get_json()
    cid = d.get("chapter",""); ans = d.get("answer","").lower().strip(); qi = d.get("q_index",0)
    if cid not in KNOWLEDGE: return jsonify({"error":"Not found"}), 404
    qs = KNOWLEDGE[cid]["quiz"]
    correct = any(a in ans or ans in a for a in qs[qi]["a"])
    if correct: session["quiz_score"] = session.get("quiz_score",0)+1; session.modified = True
    if qi == len(qs)-1:
        record_score(session["username"], session["quiz_score"], cid)
        return jsonify({"correct":correct,"done":True,
                        "final_score":session["quiz_score"],"total":len(qs)})
    nq = qs[qi+1]
    return jsonify({"correct":correct,"done":False,"next_q":{"q":nq["q"],"hint":nq["hint"]}})

if __name__ == "__main__":
    print("\n  ELARIX - The Medieval Archivist")
    print("  pip install flask better-profanity")
    print("  http://localhost:5000\n")
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"  Local:   http://localhost:5000")
    print(f"  Network: http://{local_ip}:5000  (share this with other devices on same WiFi)\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
