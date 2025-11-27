"""
PROJECT OLYMPUS: DIAGNOSTIC EDITION
Status: DEBUGGING MODE | VERBOSE LOGGING
"""
import asyncio, datetime, os, smtplib, json, math, random
import uvicorn
import aiohttp
import aiosqlite
import feedparser
import ccxt.async_support as ccxt
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from collections import deque
from youtube_transcript_api import YouTubeTranscriptApi
from textblob import TextBlob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- [CONFIGURATION] ---
class Config:
    # 1. MAKE SURE THIS IS TRUE
    REAL_MONEY_MODE = True 
    
    DB_PATH = "olympus.db"
    
    # 2. YOUR KEYS (CHECK THESE CAREFULLY)
    SMTP_USER = "your_email@gmail.com"      # <-- RE-ENTER THIS
    SMTP_PASS = "your_app_password"         # <-- RE-ENTER THIS (16 chars, no spaces)
    OWNER_EMAIL = "your_email@gmail.com"    

# --- [LAYER 0: DATABASE] ---
class Database:
    async def init_db(self):
        async with aiosqlite.connect(Config.DB_PATH) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS logs 
                               (id INTEGER PRIMARY KEY, msg TEXT, timestamp TEXT)''')
            await db.commit()
db = Database()

# --- [LAYER 1: THE DIAGNOSTIC ENGINE] ---
class TheDoctor:
    """Finds out why the system is broken."""
    
    async def test_gmail(self):
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
            server.login(Config.SMTP_USER, Config.SMTP_PASS)
            server.quit()
            return "✅ GMAIL: CONNECTED (Credentials Valid)"
        except Exception as e:
            return f"❌ GMAIL ERROR: {str(e)}"

    async def test_youtube(self):
        try:
            # Test with a known video (Me at the zoo)
            YouTubeTranscriptApi.get_transcript("jNQXAC9IVRw")
            return "✅ YOUTUBE: CONNECTED (API Working)"
        except Exception as e:
            return f"❌ YOUTUBE ERROR: {str(e)}"

    async def test_config(self):
        if Config.REAL_MONEY_MODE:
            return "✅ CONFIG: REAL MONEY MODE IS ON"
        else:
            return "⚠️ CONFIG: REAL MONEY MODE IS OFF (Emails will not send)"

doctor = TheDoctor()

# --- [LAYER 2: THE WORKER] ---
class TheHand:
    async def send_email(self, to, subj, body):
        if not Config.REAL_MONEY_MODE: return "SIMULATION (Check Config)"
        try:
            msg = MIMEMultipart()
            msg['From'] = Config.SMTP_USER
            msg['To'] = to
            msg['Subject'] = subj
            msg.attach(MIMEText(body, 'plain'))
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
                s.login(Config.SMTP_USER, Config.SMTP_PASS)
                s.send_message(msg)
            return "SUCCESS: Email Sent"
        except Exception as e: return f"EMAIL FAILED: {str(e)}"

hand = TheHand()
logs = deque(maxlen=50)

# --- [LAYER 3: REVENUE] ---
class RevenueManager:
    async def run_alchemist(self, url):
        logs.appendleft(f"ALCHEMIST: Processing {url}...")
        if "v=" not in url: 
            logs.appendleft("ALCHEMIST: Invalid URL Format")
            return
        try:
            vid = url.split("v=")[1].split("&")[0]
            transcript = YouTubeTranscriptApi.get_transcript(vid)
            text = " ".join([t['text'] for t in transcript])[:1000]
            
            # SEND
            res = await hand.send_email(Config.OWNER_EMAIL, "ALCHEMIST CONTENT", text)
            logs.appendleft(f"ALCHEMIST: {res}")
        except Exception as e:
            logs.appendleft(f"ALCHEMIST CRASH: {str(e)}")

rev = RevenueManager()

# --- [LAYER 4: APP] ---
app = FastAPI()

@app.on_event("startup")
async def start():
    await db.init_db()
    logs.appendleft("SYSTEM: DIAGNOSTIC MODE ONLINE")

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
.test-btn{width:100%;background:#ff0055;color:white;margin-bottom:15px}
</style>
</head>
<body>
<div style="margin-bottom:15px">OLYMPUS // DIAGNOSTIC</div>

<button class="test-btn" onclick="runTest()">RUN SYSTEM SELF-TEST</button>

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
}, 1000);

async function runTest(){
 await fetch('/api/test');
}

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

@app.get("/api/test")
async def test_sys():
    logs.appendleft("--- STARTING SELF-TEST ---")
    logs.appendleft(await doctor.test_config())
    logs.appendleft(await doctor.test_gmail())
    logs.appendleft(await doctor.test_youtube())
    logs.appendleft("--- END SELF-TEST ---")
    return {"status": "ok"}

@app.post("/api/cmd")
async def cmd(request: Request):
    data = await request.json()
    c = data.get('cmd')
    if "transmute" in c: asyncio.create_task(rev.run_alchemist(c.split()[-1]))
    return {"status": "Queued"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
