import json, re
from app.config import GEMINI_API_KEY, GEMINI_MODEL

def _client():
    if not GEMINI_API_KEY:
        return None
    try:
        from google import genai
        return genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        return None

def ask(prompt: str):
    client=_client()
    if not client:return None
    try:
        if hasattr(client,"interactions"):
            r=client.interactions.create(model=GEMINI_MODEL,input=prompt)
            return getattr(r,"output_text",None)
    except Exception:
        pass
    try:
        r=client.models.generate_content(model=GEMINI_MODEL,contents=prompt)
        return getattr(r,"text",None)
    except Exception:
        return None

def json_ask(prompt: str, schema=None):
    client=_client()
    if not client:return None
    try:
        if hasattr(client,"interactions"):
            fmt={"type":"text","mime_type":"application/json"}
            if schema:
                fmt["schema"]=schema
            r=client.interactions.create(model=GEMINI_MODEL,input=prompt,response_format=fmt)
            text=getattr(r,"output_text","") or ""
            return json.loads(text)
    except Exception:
        pass
    try:
        from google.genai import types
        kwargs={"response_mime_type":"application/json","temperature":0.2}
        if schema: kwargs["response_schema"]=schema
        r=client.models.generate_content(model=GEMINI_MODEL,contents=prompt,
                                         config=types.GenerateContentConfig(**kwargs))
        text=getattr(r,"text","") or ""
        return json.loads(text)
    except Exception:
        raw=ask(prompt)
        if not raw:return None
        try:
            m=re.search(r"\{.*\}",raw,re.S)
            return json.loads(m.group(0)) if m else None
        except Exception:return None
