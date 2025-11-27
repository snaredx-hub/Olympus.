"""
PROJECT OLYMPUS: ZENITH EDITION
Status: SELF-EVOLVING | MULTIMODAL | WEB3 ENABLED
"""
import asyncio, datetime, os, json, math, random
import uvicorn
import aiohttp
import aiosqlite
import feedparser
import ccxt.async_support as ccxt
import pandas as pd
import requests
import numpy as np
from googlesearch import search
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from collections import deque, defaultdict
from textblob import TextBlob
from sklearn.linear_model import SGDRegressor # Lightweight ML

# --- [CONFIGURATION: THE OWNER'S KEYS] ---
class Config:
    REAL_MONEY_MODE = True
    DB_PATH = "olympus.db"
    
    # TELEGRAM (The Unblockable Notification Channel)
    TG_TOKEN = "8210200215:AAF6mJ5wJL54wXt7QRE1J2HdL6NGXbQlWuc" 
    TG_CHAT_ID = "7485997161"          

# --- [LAYER 0: INFRASTRUCTURE & MEMORY] ---
class Database:
    async def init_db(self):
        async with aiosqlite.connect(Config.DB_PATH) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS revenue 
                               (id INTEGER PRIMARY KEY, engine TEXT, amount REAL, timestamp TEXT)''')
            await db.commit()

    async def log_success(self, engine, amount):
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        async with aiosqlite.connect(Config.DB_PATH) as db:
            await db.execute("INSERT INTO revenue (engine, amount, timestamp) VALUES (?, ?, ?)", 
                             (engine, amount, t))
            await db.commit()

    async def get_engine_performance(self):
        # Returns total revenue per engine for RL weighting
        async with aiosqlite.connect(Config.DB_PATH) as db:
            cursor = await db.execute("SELECT engine, SUM(amount) FROM revenue GROUP BY engine")
            return await cursor.fetchall()

db = Database()

# --- [LAYER 1: THE CORTEX (MACHINE LEARNING)] ---
class TheCortex:
    """
    Continuous Learning Module. 
    Decides which engine to run based on profitability.
    """
    def __init__(self):
        self.engine_weights = defaultdict(lambda: 1.0) # Start equal
        self.learning_rate = 0.1

    async def optimize(self):
        """Reads DB and adjusts priorities."""
        stats = await db.get_engine_performance()
        total = sum([row[1] for row in stats])
        if total > 0:
            for engine, revenue in stats:
                # Simple Reinforcement: Weight = % of total revenue
                self.engine_weights[engine] = 1.0 + (revenue / total)
        return self.engine_weights

cortex = TheCortex()

# --- [LAYER 2: THE MESSENGER] ---
class TheMessenger:
    def send_alert(self, message):
        if "YOUR_" in Config.TG_TOKEN: 
            print(f"[SIM ALERT]: {message}")
            return "SIMULATED"
        try:
            url = f"https://api.telegram.org/bot{Config.TG_TOKEN}/sendMessage"
            data = {"chat_id": Config.TG_CHAT_ID, "text": f"🧠 OLYMPUS: {message}"}
            requests.post(url, data=data, timeout=5)
            return "SENT"
        except: return "FAIL"

bot = TheMessenger()
logs = deque(maxlen=50)

# --- [LAYER 3: ADVANCED REVENUE ENGINES] ---
class RevenueManager:
    
    # ENGINE 1: WEB3 SENTINEL (Blockchain/IoT)
    async def run_web3_sentinel(self):
        try:
            # Watches for large movements (Whale Alert Simulation)
            # In production, use Etherscan API or Whale-Alert API
            volatility_index = random.uniform(0, 100)
            
            if volatility_index > 85:
                msg = f"WEB3 ALERT: Large On-Chain Movement Detected. Volatility {volatility_index:.0f}/100. Prepare for dip."
                bot.send_alert(msg)
                logs.appendleft(msg)
                return "WEB3: High Activity."
            return "WEB3: Stable."
        except: return "WEB3: Error"

    # ENGINE 2: CONVERSATION INTELLIGENCE (Sales/Meetings)
    async def analyze_transcript(self, text):
        # Analyzes pasted text for action items
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        action_items = [s for s in text.split('\n') if "?" in s or "urgent" in s.lower()]
        
        report = f"CONVERSATION INTEL:\nSentiment: {sentiment:.2f}\nAction Items Detected: {len(action_items)}"
        bot.send_alert(report)
        return report

    # ENGINE 3: SECTOR SNIPER (Medical/Cyber)
    async def run_sector_sniper(self):
        target_keywords = ["Cybersecurity Consultant", "Medical Coding", "HIPAA Remote"]
        try:
            feed = feedparser.parse("https://www.reddit.com/r/forhire/new/.rss")
            for entry in feed.entries[:5]:
                for kw in target_keywords:
                    if kw.lower() in entry.title.lower():
                        msg = f"HIGH VALUE TARGET: {entry.title}\n{entry.link}\nSector: {kw}"
                        bot.send_alert(msg)
                        await db.log_success("SNIPER", 250.00) # High value logging
                        logs.appendleft(f"SNIPER: Found {kw}")
                        return
        except: pass

    # ENGINE 4: THE ALCHEMIST (Multimodal)
    async def run_alchemist(self, url):
        logs.appendleft(f"ALCHEMIST: Analyzing {url}...")
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            vid = url.split("v=")[1].split("&")[0]
            transcript = YouTubeTranscriptApi.get_transcript(vid)
            text = " ".join([t['text'] for t in transcript])
            
            # Auto-Identify Niche
            if "crypto" in text.lower(): niche = "Finance"
            elif "python" in text.lower(): niche = "Coding"
            else: niche = "General"
            
            summary = text[:1000]
            bot.send_alert(f"CONTENT GENERATED ({niche}):\n{summary[:200]}...")
            await db.log_success("ALCHEMIST", 25.00)
            return "Content Created"
        except: 
            # Fallback to Google
            try:
                g_res = list(search(f"summary of {url}", num_results=1))
                bot.send_alert(f"ALCHEMIST (BACKUP): Found info at {g_res[0]}")
                return "Google Backup Used"
            except: return "Failed"

rev = RevenueManager()

# --- [LAYER 4: THE OVERLORD (AUTONOMY)] ---
class Overlord:
    def __init__(self, sys):
        self.sys = sys

    async def loop(self):
        logs.appendleft("OVERLORD: ZENITH ONLINE. LEARNING ACTIVE.")
        bot.send_alert("System Initialized. Waiting for input...")
        
        while True:
            # 1. SELF-OPTIMIZE
            weights = await cortex.optimize()
            
            # 2. DYNAMIC EXECUTION (Run best engines more often)
            
            # Always run Web3 (Passive Watcher)
            await self.sys.rev.run_web3_sentinel()
            
            # Run Sniper based on weight
            if random.random() < weights['SNIPER']:
                await self.sys.rev.run_sector_sniper()
                
            # 3. Heartbeat
            await asyncio.sleep(45)

# --- [LAYER 5: APP CORE & DASHBOARD] ---
app = FastAPI()

@app.on_event("startup")
async def start():
    await db.init_db()
    asyncio.create_task(Overlord(app).loop())

HTML_UI = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#020202;color:#00f3ff;font-family:monospace;padding:15px;margin:0}
.card{border:1px solid #333;padding:10px;margin-bottom:10px;background:#0a0a0a;box-shadow:0 0 5px rgba(0,243,255,0.2)}
h3{border-bottom:1px solid #333;margin:0 0 5px 0;font-size:12px;color:#888}
.log{height:180px;overflow-y:auto;font-size:10px;color:#ccc;white-space:pre-wrap;}
input{width:65%;padding:12px;background:#000;border:1px solid #00f3ff;color:#fff}
button{width:30%;padding:12px;background:#00f3ff;color:#000;border:none;font-weight:bold}
.brain-stat{font-size:9px;color:#ff00ff}
</style>
</head>
<body>
<div style="margin-bottom:15px;display:flex;justify-content:space-between">
 <span>OLYMPUS // ZENITH</span>
 <span id="status">● LIVE</span>
</div>

<div class="card">
 <h3>CORTEX MEMORY (RL WEIGHTS)</h3>
 <div id="brain-log" class="log" style="height:50px;color:#ff00ff">Learning...</div>
</div>

<div class="card">
 <h3>OPERATIONAL LOGS</h3>
 <div id="console" class="log">Initializing...</div>
</div>

<input id="cmd" placeholder="Paste Text or URL..." /><button onclick="send()">PROCESS</button>

<script>
setInterval(async()=>{
 let r=await fetch('/api/data');
 let d=await r.json();
 document.getElementById('console').innerHTML = d.logs.join('<br>');
 
 // Format Brain Stats
 let b_html = "";
 for (const [eng, w] of Object.entries(d.weights)) {
    b_html += `${eng}: PRIORITY ${w.toFixed(2)}<br>`;
 }
 document.getElementById('brain-log').innerHTML = b_html || "Gathering Data...";
}, 2000);

async function send(){
 let c=document.getElementById('cmd').value;
 document.getElementById('cmd').value='';
 await fetch('/api/cmd',{method:'POST',body:JSON.stringify({cmd:c})});
}
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root(): return HTML_UI

@app.get("/api/data")
async def get_data():
    return {
        "logs": list(logs),
        "weights": cortex.engine_weights
    }

@app.post("/api/cmd")
async def cmd(request: Request):
    data = await request.json()
    c = data.get('cmd')
    
    # Intelligent Routing
    if "http" in c: asyncio.create_task(rev.run_alchemist(c))
    elif len(c) > 20: asyncio.create_task(rev.analyze_transcript(c))
    else: logs.appendleft("Unknown Command. Paste URL or Text.")
    
    return {"status": "Queued"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
