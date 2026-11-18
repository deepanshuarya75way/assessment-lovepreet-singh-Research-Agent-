from pathlib import Path
import hashlib
try:
    import chromadb
except Exception:chromadb=None

class Store:
    def __init__(self):
        self.client=None;self.col=None
        if chromadb:
            try:
                self.client=chromadb.PersistentClient(path="data/vector")
                self.col=self.client.get_or_create_collection("research_evidence")
            except Exception:pass
    def add(self,run_id,documents,metadatas,ids):
        if self.col and documents:
            self.col.add(documents=documents,metadatas=metadatas,ids=ids)
    def query(self,text,n=8):
        if not self.col:return []
        try:
            x=self.col.query(query_texts=[text],n_results=n)
            return [{"text":d,"meta":m} for d,m in zip(x["documents"][0],x["metadatas"][0])]
        except Exception:return []
STORE=Store()
