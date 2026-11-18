import os
from dotenv import load_dotenv
load_dotenv()
OPENALEX_API_KEY=os.getenv("OPENALEX_API_KEY","").strip()
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY","").strip()
GEMINI_MODEL=os.getenv("GEMINI_MODEL","gemini-2.5-flash")
EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL","all-MiniLM-L6-v2")
MAX_PAPERS=int(os.getenv("MAX_PAPERS","10"))
MAX_PDF_MB=int(os.getenv("MAX_PDF_MB","20"))
