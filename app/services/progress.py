import asyncio
from collections import defaultdict

RUNS = {}
EVENTS = defaultdict(list)

def init(run_id):
    RUNS[run_id] = {"status": "queued", "result": None, "error": None}
    EVENTS[run_id] = []

def emit(run_id, step, message, progress):
    event = {"step": step, "message": message, "progress": progress}
    EVENTS[run_id].append(event)
    RUNS[run_id]["status"] = "running"

def complete(run_id, result):
    RUNS[run_id]["status"] = "completed"
    RUNS[run_id]["result"] = result

def fail(run_id, error):
    RUNS[run_id]["status"] = "failed"
    RUNS[run_id]["error"] = str(error)

async def stream_events(run_id):
    sent = 0
    while True:
        events = EVENTS.get(run_id, [])
        while sent < len(events):
            yield f"data: {__import__('json').dumps(events[sent])}\n\n"
            sent += 1
        status = RUNS.get(run_id, {}).get("status")
        if status in ("completed", "failed"):
            final = {"step": "done", "message": status, "progress": 100}
            yield f"data: {__import__('json').dumps(final)}\n\n"
            break
        await asyncio.sleep(0.25)
