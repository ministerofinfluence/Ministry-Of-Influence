from fastapi import FastAPI, BackgroundTasks, HTTPException
from datetime import datetime
import os
import glob

app = FastAPI()
LOG_DIR = "/logs"

def get_today_filename():
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"journal_{date_str}.md")

def ensure_journal_exists(filepath):
    if not os.path.exists(filepath):
        header = f"# SysOp Journal\n**Date**: {datetime.now().strftime('%Y-%m-%d')}\n**Observer**: SysOp (v0.2)\n---\n\n"
        with open(filepath, "w") as f:
            f.write(header)

def write_to_journal(sender: str, message: str, type: str):
    filepath = get_today_filename()
    ensure_journal_exists(filepath)
    
    timestamp = datetime.now().strftime("%H:%M")
    entry = f"### [{timestamp}] {type}: {sender}\n{message}\n\n---\n"
    
    with open(filepath, "a") as f:
        f.write(entry)

@app.post("/log")
async def log_event(sender: str, message: str, type: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_to_journal, sender, message, type)
    return {"status": "logged"}

@app.get("/logs")
def list_logs():
    files = glob.glob(os.path.join(LOG_DIR, "journal_*.md"))
    return {"logs": [os.path.basename(f) for f in sorted(files, reverse=True)]}

@app.get("/logs/today")
def read_current_log():
    filepath = get_today_filename()
    if not os.path.exists(filepath):
        return {"content": "No logs for today yet."}
    with open(filepath, "r") as f:
        return {"content": f.read()}

@app.get("/logs/{date_str}")
def read_log(date_str: str):
    # Security: Simple check to prevent directory traversal
    if ".." in date_str or "/" in date_str:
        raise HTTPException(status_code=400, detail="Invalid filename")
        
    filepath = os.path.join(LOG_DIR, f"journal_{date_str}.md")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Log not found")
        
    with open(filepath, "r") as f:
        return {"content": f.read()}

@app.get("/status")
def status():
    return {"role": "SysOp", "state": "WATCHING", "version": "0.2"}
