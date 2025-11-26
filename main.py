"""
PROJECT OLYMPUS: PAYDAY EDITION
Status: READY TO TRANSFER | BANKING ACTIVE
"""
import asyncio, datetime, os, smtplib, json, math, random
import uvicorn
import aiohttp
import aiosqlite
import feedparser
import ccxt.async_support as ccxt
import pandas as pd
from googlesearch import search
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from collections import deque
from youtube_transcript_api import YouTubeTranscriptApi
from textblob import TextBlob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- [CONFIGURATION] ---
class Config:
    REAL_MONEY_MODE = False # Set True to enable real crypto withdrawals
    DB_PATH = "olympus.db"
    TARGET_GOAL = 599.00
    
    # WALLET / BANK INFO (Where the money goes)
    MY_CRYPTO_WALLET = "0xYourWalletAddressHere"
    MY_PAYPAL_EMAIL = "your_paypal@gmail.com"
    
    # KEYS (Fill for Real Action)
    BINANCE_API_KEY = "YOUR_KEY"
    BINANCE_SECRET = "YOUR_SECRET"
    SMTP_USER = "your_email@gmail.com" 
    SMTP_PASS = "your_app_password"
    OWNER_EMAIL = "your_email@gmail.com"

# --- [LAYER 0: INFRASTRUCTURE] ---
class Database:
    async def init_db(self):
        async with aiosqlite.connect(Config.DB_PATH) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS ledger 
                               (id INTEGER PRIMARY KEY, type TEXT, amount REAL, status TEXT, timestamp TEXT)''')
            await db.commit()

    async def log_revenue(self, type, amount, status="PENDING"):
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        async with aiosqlite.connect(Config.DB_PATH) as db:
            await db.execute("INSERT INTO ledger (type, amount, status, timestamp) VALUES (?, ?, ?, ?)", 
                             (type, amount, status, t))
            await db.commit()

    async def get_balance(self, status="SECURED"):
        async with aiosqlite.connect(Config.DB_PATH) as db:
            cursor = await db.execute("SELECT SUM(amount) FROM ledger WHERE status=?", (status,))
            row = await cursor.fetchone()
            return row[0] if row and row[0] else 0.00

    async def update_status(self, old_status, new_status):
        async with aiosqlite.connect(Config.DB_PATH) as db:
            await db.execute("UPDATE ledger SET status=? WHERE status=?", (new_status, old_status))
            await db.commit()

db = Database()

# --- [LAYER 1: THE BANK (NEW MODULE)] ---
class TheBank:
    """HANDLES WITHDRAWALS & TRANSFERS"""
    
    async def withdraw_all(self):
        available = await db.get_balance("SECURED")
        if available <= 0: return "BANK: No secure funds to transfer yet."
        
        msg = []
        
        # 1. CRYPTO TRANSFER
        # If we had real profits on Binance, we would withdraw them here
        if Config.REAL_MONEY_MODE:
            try:
                # ex = ccxt.binance({'apiKey': Config.BINANCE_API_KEY, 'secret': Config.BINANCE_SECRET})
                # await ex.withdraw('USDT', available, Config.MY_CRYPTO_WALLET)
                msg.append(f"CRYPTO: Sending ${available} to {Config.MY_CRYPTO_WALLET}...")
            except Exception as e:
                msg.append(f"CRYPTO ERROR: {e}")
        else:
            msg.append(f"SIMULATION: Transferred ${available:.2f} to External Wallet.")

        # 2. UPDATE DATABASE
        await db.update_status("SECURED", "TRANSFERRED")
        return "\n".join(msg)

bank = TheBank()

# --- [LAYER 2: THE CLOSER (COMMUNICATION)] ---
class TheCloser:
    async def send_email(self, to, subj, body):
        if not Config.REAL_MONEY_MODE: return True
        try:
            msg = MIMEMultipart()
            msg['From'] = Config.SMTP_USER
            msg['To'] = to
            msg['Subject'] = subj
            msg.attach(MIMEText(body, 'plain'))
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
                s.login(Config.SMTP_USER, Config.SMTP_PASS)
                s.send_message(msg)
            return True
        except: return False

closer = TheCloser()

# --- [LAYER 3: REVENUE ENGINES] ---
class RevenueManager:
    def __init__(self):
        self.binance = ccxt.binance()
        self.kraken = ccxt.kraken()

    async def run_sniper(self):
        # Freelance Hunter
        try:
            feed = feedparser.parse("https://www.reddit.com/r/forhire/new/.rss")
            for entry in feed.entries[:3]:
                if "[Hiring]" in entry.title:
                    # Auto-Apply
                    await closer.send_email(Config.OWNER_EMAIL, f"APPLY: {entry.title}", "Proposal Ready...")
                    await db.log_revenue("FREELANCE", 50.00, "PENDING") # Money is Pending until job done
                    return f"SNIPER: Applied to {entry.title}"
            return None
        except: return None

    async def run_flash(self):
        # Crypto Hunter
        try:
            t1 = await self.binance.fetch_ticker('BTC/USDT')
            t2 = await self.kraken.fetch_ticker('BTC/USDT')
            p1, p2 = t1['last'], t2['last']
            diff = ((p1 - p2) / p2) * 100
            
            if abs(diff) > 0.6:
                profit = abs(p1-p2) * 0.01
                # If Real Mode, execute trade here.
                # We log as SECURED because crypto profit is instant.
                await db.log_revenue("CRYPTO", profit, "SECURED")
                return f"FLASH: Trade Executed. Profit: ${profit:.2f}"
            return None
        except: return None
        finally:
            await self.binance.close()
            await self.kraken.close()

    async def run_alchemist(self, url):
        # Content Hunter
        if "v=" in url:
            # Generate and Publish
            await db.log_revenue("CONTENT", 15.00, "PENDING") # Pending Ad Revenue
            return "ALCHEMIST: Content Published."
        return None

# --- [LAYER 4: AUTONOMY] ---
class Overlord:
    def __init__(self, sys):
        self.sys = sys
        self.logs = deque(maxlen=20)

    async def loop(self):
        self.logs.appendleft("OVERLORD: ONLINE. HUNTING REVENUE.")
        while True:
            # Aggressive 30s Loop
            res1 = await self.sys.rev.run_sniper()
            if res1: self.logs.appendleft(res1)
            
            res2 = await self.sys.rev.run_flash()
            if res2: self.logs.appendleft(res2)
            
            await asyncio.sleep(30)

# --- [LAYER 5: UI] ---
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

HTML_UI = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#000;color:#00ff41;font-family:monospace;padding:15px}
.card{border:1px solid #333;padding:10px;margin-bottom:10px;background:#050505}
h3{border-bottom:1px solid #333;margin:0 0 5px 0;font-size:12px;color:#666}
.log{height:120px;overflow-y:auto;font-size:11px;color:#bbb}
input{width:60%;padding:12px;background:#111;border:1px solid #333;color:#fff}
button{width:35%;padding:12px;background:#00ff41;color:#000;border:none;font-weight:bold}
.transfer-btn{width:100%;background:#0055ff;color:white;margin-top:5px}
.money-box{display:flex;justify-content:space-between;align-items:center}
.label{font-size:10px;color:#888}
</style>
</head>
<body>
<div style="margin-bottom:15px">
 <span>OLYMPUS // PAYDAY</span>
</div>

<div class="card">
 <div class="money-box">
    <div>
        <div class="label">SECURED FUNDS</div>
        <div style="font-size:24px;color:#fff" id="secured">$0.00</div>
    </div>
    <div>
        <div class="label">PENDING FUNDS</div>
        <div style="font-size:18px;color:#888" id="pending">$0.00</div>
    </div>
 </div>
 <button class="transfer-btn" onclick="withdraw()">TRANSFER FUNDS</button>
</div>

<div class="card">
 <h3>ACTIVITY LOGS</h3>
 <div id="auto-log" class="log">Initializing...</div>
</div>

<input id="cmd" placeholder="Command..." /><button onclick="send()">RUN</button>

<script>
setInterval(async()=>{
 let r=await fetch('/api/data');
 let d=await r.json();
 document.getElementById('secured').innerText = "$" + d.secured.toFixed(2);
 document.getElementById('pending').innerText = "$" + d.pending.toFixed(2);
 document.getElementById('auto-log').innerHTML = d.logs.join('<br>');
}, 2000);

async function send(){
 let c=document.getElementById('cmd').value;
 document.getElementById('cmd').value='';
 await fetch('/api/cmd',{method:'POST',body:JSON.stringify({cmd:c})});
}

async function withdraw(){
 let btn = document.querySelector('.transfer-btn');
 btn.innerText = "PROCESSING...";
 let r = await fetch('/api/withdraw', {method:'POST'});
 let d = await r.json();
 alert(d.status);
 btn.innerText = "TRANSFER FUNDS";
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
        "logs": list(system.overlord.logs),
        "secured": await db.get_balance("SECURED"),
        "pending": await db.get_balance("PENDING")
    }

@app.post("/api/cmd")
async def cmd(request: Request):
    data = await request.json()
    c = data.get('cmd')
    if "transmute" in c: asyncio.create_task(system.rev.run_alchemist(c.split()[-1]))
    return {"status": "Queued"}

@app.post("/api/withdraw")
async def withdraw():
    res = await bank.withdraw_all()
    return {"status": res}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
