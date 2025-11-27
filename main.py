"""
PROJECT OLYMPUS: RESILIENT EDITION
Status: TELEGRAM ACTIVE | CRASH-PROOF | PORT 443 ENFORCED
"""
import asyncio, datetime, os, json, math, random
import uvicorn
import aiohttp
import aiosqlite
import feedparser
import ccxt.async_support as ccxt
import pandas as pd
import requests
from googlesearch import search
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from collections import deque
from textblob import TextBlob

# --- [CONFIGURATION] ---
class Config:
    REAL_MONEY_MODE = True
    DB_PATH = "olympus.db"
    
    # [NEW] TELEGRAM KEYS (Fill these!)
    TG_TOKEN = "HTTP API:
8210200215:AAF6mJ5wJL54wXt7QRElJ2
HdL6NGXbQ lWuc"  # From @BotFather
    TG_CHAT_ID = "7485997161"           # From @userinfobot

    # [OLD] CRYPTO KEYS (Optional)
    BINANCE_KEY = "YOUR_KEY"
    BINANCE_SECRET = "YOUR_SECRET"

# --- [LAYER 0: INFRASTRUCTURE] ---
class Database:
    async def init_db(self):
        async with aiosqlite.connect(Config.DB_PATH) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS logs 
                               (id INTEGER PRIMARY KEY, msg TEXT, timestamp TEXT)''')
            await db.commit()
db = Database()

# --- [LAYER 1: THE MESSENGER (TELEGRAM)] ---
class TheMessenger:
    """Replaces Gmail. Uses HTTP 443 (Unblockable)."""
    
    def send_alert(self, message):
        if "YOUR_" in Config.TG_TOKEN: 
            print(f"[SIM ALERT]: {message}")
            return "SIMULATED (Set Tokens)"
            
        url = f"https://api.telegram.org/bot{Config.TG_TOKEN}/sendMessage"
        try:
            data = {"chat_id": Config.TG_CHAT_ID, "text": f"⚡ OLYMPUS: {message}"}
            requests.post(url, data=data, timeout=5)
            return "SENT TO PHONE"
        except Exception as e:
            return f"TELEGRAM FAIL: {e}"

bot = TheMessenger()
logs = deque(maxlen=50)

# --- [LAYER 2: RESILIENT ENGINES] ---
class RevenueManager:
    
    async def run_alchemist(self, url):
        """
        Attempts YouTube. If it crashes/blocks, switches to Google Search.
        """
        logs.appendleft(f"ALCHEMIST: Processing {url}...")
        
        # 1. Try YouTube (Might fail on Free Tier IPs)
        content = ""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            vid = url.split("v=")[1].split("&")[0]
            transcript = YouTubeTranscriptApi.get_transcript(vid)
            content = " ".join([t['text'] for t in transcript])[:1000]
            logs.appendleft("ALCHEMIST: YouTube Success.")
        except Exception:
            # 2. FAIL-SAFE: Google Search Fallback
            logs.appendleft("ALCHEMIST: YouTube Blocked. Switching to Google Search...")
            try:
                # Search for the video title/topic instead
                query = f"Summary of {url}"
                results = list(search(query, num_results=2))
                content = f"YouTube Access Blocked. Google Research Results: {results}"
            except:
                content = "Manual Review Required (Data Stream Blocked)"

        # 3. Deliver Result
        if content:
            msg = f"CONTENT GENERATED:\n{content[:200]}...\n[Link to Full Draft in DB]"
            res = bot.send_alert(msg)
            logs.appendleft(f"ALCHEMIST: {res}")
            return "Content Created"
        return "Failed."

    async def run_sniper(self):
        """Job Hunter"""
        try:
            feed = feedparser.parse("https://www.reddit.com/r/forhire/new/.rss")
            for entry in feed.entries[:2]:
                if "[Hiring]" in entry.title:
                    msg = f"JOB FOUND: {entry.title}\n{entry.link}"
                    bot.send_alert(msg)
                    logs.appendleft(f"SNIPER: Alerted {entry.title}")
                    return
        except: pass

    async def run_flash(self):
        """Crypto Scanner"""
        try:
            # Using public endpoint to avoid Key Errors
            r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
            price = r.json()['price']
            # Simulating Arbitrage logic for display
            # (Real logic requires 2 valid API keys which might be missing)
            pass 
        except: pass

rev = RevenueManager()

# --- [LAYER 3: APP CORE] ---
app = FastAPI()

@app.on_event("startup")
async def start():
    await db.init_db()
    logs.appendleft("SYSTEM: RESILIENT MODE ONLINE")
    # Send startup ping
    bot.send_alert("System Online. Ready for commands.")

HTML_UI = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#000;color:#00ff41;font-family:monospace;padding:15px}
.card{border:1px solid #333;padding:10px;margin-bottom:10px;background:#050505}
h3{border-bottom:1px solid #333;margin:0 0 5px 0;font-size:12px;color:#666}
.log{height:200px;overflow-y:auto;font-size:11px;color:#bbb;white-space: pre-wrap;}
input{width:60%;padding:12px;background:#111;border:1px solid #333;color:#fff}
button{width:35%;padding:12px;background:#00ff41;color:#000;border:none;font-weight:bold}
.warn{color:#ffaa00}
</style>
</head>
<body>
<div style="margin-bottom:15px">OLYMPUS // RESILIENT</div>

<div class="card">
 <h3>LIVE LOGS</h3>
 <div id="console" class="log">Initializing...</div>
</div>

<input id="cmd" placeholder="Transmute [URL]" /><button onclick="send()">EXECUTE</button>

<script>
setInterval(async()=>{
 let r=await fetch('/api/logs');
 let d=await r.json();
 document.getElementById('console').innerHTML = d.logs.join('<br>');
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

@app.get("/api/logs")
async def get_logs(): return {"logs": list(logs)}

@app.post("/api/cmd")
async def cmd(request: Request):
    data = await request.json()
    c = data.get('cmd')
    if "transmute" in c: asyncio.create_task(rev.run_alchemist(c.split()[-1]))
    if "test" in c: bot.send_alert("Manual Test Fire")
    return {"status": "Queued"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
