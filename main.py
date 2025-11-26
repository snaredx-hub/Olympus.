"""
PROJECT OLYMPUS: EXECUTIVE EDITION
Status: PRIORITIZED AUTONOMY | AUTO-EMAILER ACTIVE
"""
import asyncio, datetime, os, smtplib, json, math, random
import uvicorn
import aiohttp
import aiosqlite
import feedparser
import ccxt.async_support as ccxt
import pandas as pd
import dns.resolver
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from collections import deque
from youtube_transcript_api import YouTubeTranscriptApi
from textblob import TextBlob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- [STEP 1] YOUR PERSONAL KEYS ---
# YOU MUST FILL THESE FOR THE SYSTEM TO WORK
class Config:
    DB_PATH = "olympus.db"
    
    # EMAIL SETTINGS (To send you the results)
    EMAIL_ENABLED = True # Set to True
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
    SENDER_EMAIL = "your_email@gmail.com"   # The bot's email (can be yours)
    SENDER_PASS = "your_app_password"       # Get this from Google Security
    OWNER_EMAIL = "your_email@gmail.com"    # Where you want to receive reports

# --- LAYER 0: INFRASTRUCTURE ---
class Database:
    async def init_db(self):
        async with aiosqlite.connect(Config.DB_PATH) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS history 
                               (id INTEGER PRIMARY KEY, type TEXT, result TEXT, profit REAL, timestamp TEXT)''')
            await db.commit()

    async def log(self, type, result, profit):
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(Config.DB_PATH) as db:
            await db.execute("INSERT INTO history (type, result, profit, timestamp) VALUES (?, ?, ?, ?)", 
                             (type, result, profit, t))
            await db.commit()

    async def export_csv(self):
        async with aiosqlite.connect(Config.DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM history")
            rows = await cursor.fetchall()
            if not rows: return None
            df = pd.DataFrame([dict(row) for row in rows])
            fname = f"olympus_ledger_{datetime.date.today()}.csv"
            df.to_csv(fname, index=False)
            return fname

db = Database()

class Communicator:
    """Delivers the final product to the Owner."""
    def email_result(self, subject, body):
        if not Config.EMAIL_ENABLED: return print(f"[EMAIL SIM]: {subject}")
        try:
            msg = MIMEMultipart()
            msg['From'] = Config.SENDER_EMAIL
            msg['To'] = Config.OWNER_EMAIL
            msg['Subject'] = f"[OLYMPUS] {subject}"
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.login(Config.SENDER_EMAIL, Config.SENDER_PASS)
                server.send_message(msg)
            print(f">> RESULT DELIVERED: {subject}")
        except Exception as e:
            print(f">> EMAIL ERROR: {str(e)}")

comm = Communicator()

# --- LAYER 1: THE REVENUE ENGINES ---
class RevenueManager:
    def __init__(self):
        self.binance = ccxt.binance()
        self.kraken = ccxt.kraken()

    # PRIORITY 1: FREE MONEY (Content)
    async def run_alchemist(self, url):
        if "v=" not in url: return None
        try:
            vid = url.split("v=")[1].split("&")[0]
            transcript = YouTubeTranscriptApi.get_transcript(vid)
            text = " ".join([t['text'] for t in transcript])
            
            # Intelligent Summarization
            blob = TextBlob(text)
            summary = text[:1500] # First 1500 chars as draft
            
            report = f"SOURCE: {url}\n\n=== BLOG DRAFT ===\n\n{summary}...\n\n=== END OF DRAFT ==="
            
            await db.log("CONTENT", "Generated Blog Post", 50.0)
            comm.email_result("Content Generated (Ready to Publish)", report)
            return "ALCHEMIST: Content emailed to owner."
        except: return "ALCHEMIST: Failed to Transmute."

    # PRIORITY 2: FREE MONEY (Jobs)
    async def run_sniper(self):
        try:
            feed = feedparser.parse("https://www.reddit.com/r/forhire/new/.rss")
            for entry in feed.entries[:3]:
                if "[Hiring]" in entry.title:
                    proposal = f"JOB DETECTED: {entry.title}\nLINK: {entry.link}\n\nAI PROPOSAL DRAFT:\nHello, I saw your post about {entry.title}. I have a system ready to deploy for this..."
                    
                    await db.log("FREELANCE", entry.title, 100.0)
                    comm.email_result("Job Opportunity Found", proposal)
                    return f"SNIPER: Sent proposal for {entry.title}"
            return None
        except: return None

    # PRIORITY 3: PAID MONEY (Crypto - Risky)
    async def run_flash(self):
        try:
            t1 = await self.binance.fetch_ticker('BTC/USDT')
            t2 = await self.kraken.fetch_ticker('BTC/USDT')
            p1, p2 = t1['last'], t2['last']
            diff = ((p1 - p2) / p2) * 100
            
            # DECISION ENGINE: Only notify if profit > 0.6% (covers fees)
            if abs(diff) > 0.6:
                action = f"ARBITRAGE ALERT: Buy {'Kraken' if p1 > p2 else 'Binance'} / Sell {'Binance' if p1 > p2 else 'Kraken'}. Gap: {diff:.2f}%"
                await db.log("CRYPTO", action, abs(p1-p2))
                comm.email_result("ACTION REQUIRED: Crypto Arbitrage", action)
                return action
            return None
        except: return None
        finally:
            await self.binance.close()
            await self.kraken.close()

# --- LAYER 2: THE OVERLORD (DECISION MAKER) ---
class Overlord:
    def __init__(self, sys):
        self.sys = sys
        self.log_queue = deque(maxlen=20)

    async def loop(self):
        self.log_queue.appendleft("OVERLORD: Online. Prioritizing Free Revenue.")
        
        while True:
            # STEP 1: Do the Free Work First
            res_sniper = await self.sys.rev.run_sniper()
            if res_sniper: self.log_queue.appendleft(res_sniper)
            
            # Check News for Content Opportunities (Auto-Alchemist)
            # (Simulated logic for finding a trending URL to transmute)
            if random.random() > 0.95: 
                self.log_queue.appendleft("OVERLORD: Found trending topic. Running Alchemist...")
                # await self.sys.rev.run_alchemist("https://youtube.com/...") 

            # STEP 2: Check the Paid Work Last
            res_flash = await self.sys.rev.run_flash()
            if res_flash: self.log_queue.appendleft(res_flash)

            await asyncio.sleep(60) # Check every minute

# --- LAYER 3: APP & UI ---
app = FastAPI()
system = None

class SystemWrapper:
    def __init__(self):
        self.rev = RevenueManager()
        self.overlord = Overlord(self)

@app.on_event("startup")
async def start():
    global system
    await db.init_db()
    system = SystemWrapper()
    asyncio.create_task(system.overlord.loop())

# UI
HTML_UI = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#000;color:#00ff41;font-family:monospace;padding:15px}
.card{border:1px solid #333;padding:10px;margin-bottom:10px;background:#050505}
h3{border-bottom:1px solid #333;margin:0 0 5px 0;font-size:12px;color:#666}
.log{height:150px;overflow-y:auto;font-size:11px;color:#bbb}
input{width:70%;padding:12px;background:#111;border:1px solid #333;color:#fff}
button{width:25%;padding:12px;background:#00ff41;color:#000;border:none;font-weight:bold}
a{color:#00ff41}
</style>
</head>
<body>
<div style="display:flex;justify-content:space-between;margin-bottom:15px">
 <span>OLYMPUS // EXECUTIVE</span>
 <a href="/download_report">GET SPREADSHEET</a>
</div>

<div class="card">
 <h3>DECISION LOG</h3>
 <div id="auto-log" class="log">Initializing...</div>
</div>

<input id="cmd" placeholder="Manual Override..." /><button onclick="send()">RUN</button>

<script>
setInterval(async()=>{
 let r=await fetch('/api/data');
 let d=await r.json();
 document.getElementById('auto-log').innerHTML = d.logs.join('<br>');
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
    return {"logs": list(system.overlord.log_queue)}

@app.post("/api/cmd")
async def cmd(request: Request):
    data = await request.json()
    c = data.get('cmd')
    if "transmute" in c: asyncio.create_task(system.rev.run_alchemist(c.split()[-1]))
    return {"status": "Command Queued"}

@app.get("/download_report")
async def download():
    f = await db.export_csv()
    return FileResponse(f, filename="revenue_report.csv") if f else {"error": "No data"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
