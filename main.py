"""
PROJECT OLYMPUS: REALITY EDITION
Status: LIVE DATA ONLY | AUTONOMOUS | REAL NOTIFICATIONS
"""
import asyncio, datetime, os, smtplib, json, math
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

# --- CONFIGURATION (THE OWNER'S KEYS) ---
class Config:
    DB_PATH = "olympus.db"
    # EMAIL SETUP (Fill this to get real phone notifications via Email-to-SMS or standard Email)
    EMAIL_ENABLED = False # Set True after filling details
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
    SENDER_EMAIL = "your_email@gmail.com"
    SENDER_PASS = "your_app_password"
    OWNER_EMAIL = "your_email@gmail.com"

# --- LAYER 0: REALITY DATABASE ---
class Database:
    async def init_db(self):
        async with aiosqlite.connect(Config.DB_PATH) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS opportunities 
                               (id INTEGER PRIMARY KEY, type TEXT, detail TEXT, potential_profit REAL, timestamp TEXT)''')
            await db.commit()

    async def log_opp(self, type, detail, profit):
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(Config.DB_PATH) as db:
            await db.execute("INSERT INTO opportunities (type, detail, potential_profit, timestamp) VALUES (?, ?, ?, ?)", 
                             (type, detail, profit, t))
            await db.commit()

    async def export_spreadsheet(self):
        # Generates a Real CSV Report
        async with aiosqlite.connect(Config.DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM opportunities")
            rows = await cursor.fetchall()
            
            if not rows: return None
            
            df = pd.DataFrame([dict(row) for row in rows])
            filename = f"olympus_report_{datetime.date.today()}.csv"
            df.to_csv(filename, index=False)
            return filename

db = Database()

# --- LAYER 1: THE COMMUNICATOR (NOTIFICATIONS) ---
class Communicator:
    """Sends REAL emails to the owner when money is found."""
    def notify(self, subject, body):
        if not Config.EMAIL_ENABLED:
            print(f"   [NOTIFY (Sim)]: {subject}")
            return

        try:
            msg = MIMEText(body)
            msg['Subject'] = f"[OLYMPUS] {subject}"
            msg['From'] = Config.SENDER_EMAIL
            msg['To'] = Config.OWNER_EMAIL

            with smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.login(Config.SENDER_EMAIL, Config.SENDER_PASS)
                server.send_message(msg)
            print(f"   [NOTIFY (Real)]: Email sent to owner.")
        except Exception as e:
            print(f"   [NOTIFY ERROR]: {str(e)}")

comm = Communicator()

# --- LAYER 2: THE REAL REVENUE ENGINES ---
class RevenueManager:
    def __init__(self):
        self.binance = ccxt.binance()
        self.kraken = ccxt.kraken()
        self.active = True

    async def run_flash(self):
        """REAL: Checks Binance vs Kraken for BTC/USDT Arbitrage."""
        try:
            # Fetch LIVE prices (No Simulation)
            t1 = await self.binance.fetch_ticker('BTC/USDT')
            t2 = await self.kraken.fetch_ticker('BTC/USDT')
            p1, p2 = t1['last'], t2['last']
            
            diff = p1 - p2
            percent = (diff / p2) * 100
            
            # Only alert if REAL profit exists (>0.5% to cover fees)
            if abs(percent) > 0.5:
                msg = f"REAL ARBITRAGE: Buy {'Kraken' if p1 > p2 else 'Binance'} @ ${min(p1,p2)} -> Sell {'Binance' if p1 > p2 else 'Kraken'} @ ${max(p1,p2)}. Gap: {percent:.2f}%"
                await db.log_opp("CRYPTO", msg, abs(diff))
                comm.notify("Crypto Opportunity", msg)
                return msg
            return None
        except: return None
        finally:
            await self.binance.close()
            await self.kraken.close()

    async def run_sniper(self):
        """REAL: Scans Reddit 'For Hire' for gigs."""
        try:
            # Real RSS Feed
            feed = feedparser.parse("https://www.reddit.com/r/forhire/new/.rss")
            found = []
            for entry in feed.entries[:3]:
                if "[Hiring]" in entry.title:
                    msg = f"JOB FOUND: {entry.title} ({entry.link})"
                    await db.log_opp("FREELANCE", msg, 100.0) # Est $100 value
                    comm.notify("Job Opportunity", msg)
                    found.append(msg)
            return found if found else None
        except: return None

    async def run_flipper(self, keyword="ai"):
        """REAL: Checks if high-value domains are unregistered."""
        # Generates keyword combos and checks DNS
        tlds = [".com", ".io", ".ai"]
        base = f"{keyword}{random.choice(['tech', 'sys', 'soft', 'bot'])}"
        
        results = []
        for tld in tlds:
            domain = f"{base}{tld}"
            try:
                dns.resolver.resolve(domain, 'A')
                # If resolves, it's taken. Do nothing.
            except:
                # If fails, it MIGHT be free.
                msg = f"DOMAIN POTENTIAL: {domain} appears unregistered."
                await db.log_opp("DOMAIN", msg, 500.0)
                comm.notify("Domain Found", msg)
                results.append(msg)
        return results if results else None

    async def run_alchemist(self, url):
        """REAL: Transcribes video and drafts content."""
        if "v=" not in url: return "Invalid URL"
        try:
            vid = url.split("v=")[1].split("&")[0]
            transcript = YouTubeTranscriptApi.get_transcript(vid)
            text = " ".join([t['text'] for t in transcript])
            
            # Analyze sentiment/keywords
            blob = TextBlob(text)
            keywords = blob.noun_phrases[:5]
            
            draft = f"TOPIC: {keywords}\n\nSUMMARY:\n{text[:500]}..."
            await db.log_opp("CONTENT", f"Drafted post from {vid}", 50.0)
            return draft
        except: return "No transcript available."

# --- LAYER 3: AUTONOMY (THE OVERLORD) ---
class Overlord:
    def __init__(self, sys):
        self.sys = sys
        self.log = deque(maxlen=20)

    async def loop(self):
        self.log.append("OVERLORD: Online. Watching Markets.")
        while True:
            # 1. Crypto Scan (Fast)
            res = await self.sys.rev.run_flash()
            if res: self.log.appendleft(f"[{datetime.datetime.now().strftime('%H:%M')}] {res}")
            
            # 2. Job Scan (Medium)
            res = await self.sys.rev.run_sniper()
            if res: 
                for r in res: self.log.appendleft(f"[{datetime.datetime.now().strftime('%H:%M')}] {r}")

            # 3. Domain Scan (Slow)
            if random.random() > 0.9: # Random check to avoid DNS blocking
                res = await self.sys.rev.run_flipper("crypto")
                if res:
                    for r in res: self.log.appendleft(f"[DOMAIN] {r}")

            await asyncio.sleep(60) # 1 Minute Heartbeat

# --- LAYER 4: SYSTEM & UI ---
app = FastAPI()

class OlympusSystem:
    def __init__(self):
        self.rev = RevenueManager()
        self.pilot = Overlord(self)

    async def execute(self, cmd):
        c = cmd.lower()
        if "scan" in c: return await self.rev.run_flash() or "No Arbitrage."
        if "job" in c: return await self.rev.run_sniper() or "No Jobs."
        if "domain" in c: return await self.rev.run_flipper(c.split()[-1])
        if "transmute" in c: return await self.rev.run_alchemist(c.split()[-1])
        if "report" in c: return await db.export_spreadsheet()
        return "Command Unknown."

system = OlympusSystem()

# --- DASHBOARD UI ---
HTML_UI = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#000;color:#00ff41;font-family:monospace;padding:15px;margin:0}
.card{border:1px solid #333;background:#050505;padding:10px;margin-bottom:10px}
h3{margin:0 0 5px 0;font-size:12px;color:#666;border-bottom:1px solid #333}
.log{height:150px;overflow-y:auto;font-size:11px;color:#bbb}
input{width:70%;padding:12px;background:#111;border:1px solid #333;color:#fff}
button{width:25%;padding:12px;background:#00ff41;color:#000;border:none;font-weight:bold}
.alert{color:#ff0055}
</style>
</head>
<body>
<div style="display:flex;justify-content:space-between;margin-bottom:15px">
 <span>OLYMPUS // REALITY</span>
 <a href="/download_report" style="color:#00ff41;font-size:12px">DOWNLOAD CSV</a>
</div>

<div class="card">
 <h3>OVERLORD LOGS (REAL-TIME)</h3>
 <div id="auto-log" class="log">Initializing...</div>
</div>

<div class="card">
 <h3>MANUAL TERMINAL</h3>
 <div id="sys-log" class="log">>> SYSTEM ONLINE.</div>
</div>

<input id="cmd" placeholder="Command..." /><button onclick="send()">EXECUTE</button>

<script>
setInterval(async()=>{
 let r=await fetch('/api/data');
 let d=await r.json();
 document.getElementById('auto-log').innerHTML = d.logs.join('<br>');
}, 2000);

async function send(){
 let c=document.getElementById('cmd').value;
 document.getElementById('cmd').value='';
 let l=document.getElementById('sys-log');
 l.innerHTML = '>> USER: '+c+'<br>'+l.innerHTML;
 let r=await fetch('/api/cmd',{method:'POST',body:JSON.stringify({cmd:c})});
 let d=await r.json();
 l.innerHTML = '>> GOD: '+d.reply+'<br>'+l.innerHTML;
}
</script>
</body>
</html>
"""

@app.on_event("startup")
async def startup():
    await db.init_db()
    asyncio.create_task(system.pilot.loop())

@app.get("/", response_class=HTMLResponse)
async def root(): return HTML_UI

@app.get("/api/data")
async def get_data():
    return {"logs": list(system.pilot.log)}

@app.post("/api/cmd")
async def run_cmd(request: Request):
    data = await request.json()
    res = await system.execute(data.get('cmd'))
    return {"reply": str(res)}

@app.get("/download_report")
async def download():
    file = await db.export_spreadsheet()
    if file: return FileResponse(file, filename="olympus_report.csv")
    return {"error": "No data yet"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
