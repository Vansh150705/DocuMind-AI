from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import re
import os
import tempfile

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi

from utils.pdf_processor import extract_text_from_pdfs
from utils.ai_helpers import generate_document_dna, build_prompt, get_analytics, generate_chat_export
from utils.agents import (
    is_vague_query, get_clarification_question,
    self_reflect_and_improve, apply_confidence_adaptation, get_confidence
)

load_dotenv()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "TalkDox Backend Running Successfully"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store (one session for now)
store = {
    "vectorstore": None,
    "full_text": "",
    "pdf_names": [],
    "total_pages": 0,
    "total_chunks": 0,
    "dna": None,
    "doc_language": "English",
    "source_type": "pdf",
    "chat_history": [],
    "compare_vectorstore": None,
    "compare_name": "",
    "compare_full_text": "",
}


def index_text(text: str, source_label: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
    chunks = splitter.split_text(text)
    metas = [{"source": source_label, "page": i + 1} for i in range(len(chunks))]
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vs = FAISS.from_texts(chunks, embeddings, metadatas=metas)
    return vs, len(chunks)


@app.post("/api/upload/pdf")
async def upload_pdf(files: list[UploadFile] = File(...)):
    try:
        import io
        from pypdf import PdfReader

        all_chunks, meta = [], []
        total_pages = 0
        full_text = ""

        for f in files:
            content = await f.read()
            pdf_bytes = io.BytesIO(content)
            pdf = PdfReader(pdf_bytes)
            total_pages += len(pdf.pages)

            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                full_text += text + "\n"
                if text.strip():
                    from langchain_text_splitters import RecursiveCharacterTextSplitter
                    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
                    chunks = splitter.split_text(text)
                    for chunk in chunks:
                        all_chunks.append(chunk)
                        meta.append({"source": f.filename, "page": i + 1})

        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        vs = FAISS.from_texts(all_chunks, embeddings, metadatas=meta)

        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
        dna = generate_document_dna(full_text, llm)
        doc_language = dna.get("language", "English") if dna else "English"

        store["vectorstore"]  = vs
        store["full_text"]    = full_text
        store["pdf_names"]    = [f.filename for f in files]
        store["total_pages"]  = total_pages
        store["total_chunks"] = len(all_chunks)
        store["dna"]          = dna
        store["doc_language"] = doc_language
        store["source_type"]  = "pdf"
        store["chat_history"] = []

        return {
            "success": True,
            "pdf_names": store["pdf_names"],
            "total_pages": total_pages,
            "total_chunks": len(all_chunks),
            "dna": dna,
            "doc_language": doc_language,
            "source_type": "pdf"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/upload/web")
async def upload_web(url: str = Form(...)):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script","style","nav","footer","header","aside","form","iframe","noscript"]):
            tag.decompose()
        title = soup.title.string.strip() if soup.title else url
        texts = []
        for tag in soup.find_all(["p","h1","h2","h3","h4","li","article","section","blockquote"]):
            t = tag.get_text(" ", strip=True)
            if len(t) > 40:
                texts.append(t)
        full_text = "\n\n".join(texts)
        if len(full_text.strip()) < 200:
            return JSONResponse(status_code=400, content={"error": "Not enough text extracted. This site may block scrapers."})

        vs, chunk_count = index_text(full_text, title)
        store["vectorstore"]  = vs
        store["full_text"]    = full_text
        store["pdf_names"]    = [title]
        store["total_pages"]  = 1
        store["total_chunks"] = chunk_count
        store["dna"]          = None
        store["doc_language"] = "English"
        store["source_type"]  = "web"
        store["chat_history"] = []

        return {"success": True, "title": title, "total_chunks": chunk_count, "source_type": "web"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/upload/youtube")
async def upload_youtube(url: str = Form(...)):
    try:
        import yt_dlp
        import json as jsonlib

        m = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})", url)
        if not m:
            return JSONResponse(status_code=400, content={"error": "Invalid YouTube URL."})
        video_id = m.group(1)

        # Try yt-dlp to get subtitles/transcript
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en', 'en-US'],
            'quiet': True,
            'no_warnings': True,
        }

        full_text = ""
        title = f"YouTube: {url[:50]}"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', title)

                # Get automatic captions
                captions = info.get('automatic_captions', {})
                subtitles = info.get('subtitles', {})

                # Try subtitles first, then auto captions
                caption_data = subtitles.get('en') or subtitles.get('en-US') or \
                               captions.get('en') or captions.get('en-US') or \
                               next(iter(captions.values()), None) or \
                               next(iter(subtitles.values()), None)

                if caption_data:
                    # Get the json3 format which is easiest to parse
                    json3_url = next((c['url'] for c in caption_data if c.get('ext') == 'json3'), None)
                    if json3_url:
                        import requests as req
                        r = req.get(json3_url)
                        data = r.json()
                        events = data.get('events', [])
                        texts = []
                        for event in events:
                            segs = event.get('segs', [])
                            for seg in segs:
                                t = seg.get('utf8', '').strip()
                                if t and t != '\n':
                                    texts.append(t)
                        full_text = ' '.join(texts)

                # Fallback: use description + title if no captions
                if not full_text:
                    description = info.get('description', '')
                    full_text = f"Title: {title}\n\nDescription: {description}"

        except Exception as e:
            return JSONResponse(status_code=400, content={
                "error": f"Could not fetch video info: {str(e)}"
            })

        if len(full_text.strip()) < 100:
            return JSONResponse(status_code=400, content={
                "error": "No transcript or captions found for this video."
            })

        vs, chunk_count = index_text(full_text, f"youtube/{video_id}")

        store["vectorstore"]  = vs
        store["full_text"]    = full_text
        store["pdf_names"]    = [title]
        store["total_pages"]  = 1
        store["total_chunks"] = chunk_count
        store["dna"]          = None
        store["doc_language"] = "English"
        store["source_type"]  = "youtube"
        store["chat_history"] = []

        return {
            "success": True,
            "video_id": video_id,
            "duration": "N/A",
            "total_chunks": chunk_count,
            "source_type": "youtube",
            "title": title
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/chat")
async def chat(
    question: str = Form(...),
    mode: str = Form("qa"),
    persona: str = Form("default")
):
    try:
        if not store["vectorstore"]:
            return JSONResponse(status_code=400, content={"error": "No document loaded."})

        if is_vague_query(question):
            clarification = get_clarification_question(question)
            store["chat_history"].append({"role": "user", "content": question})
            store["chat_history"].append({"role": "assistant", "content": f"🤔 {clarification}", "sources": [], "confidence": None})
            return {"answer": f"🤔 {clarification}", "sources": [], "confidence": None, "vague": True}

        docs = store["vectorstore"].similarity_search(question, k=5)
        context = "\n\n".join([d.page_content for d in docs])
        sources = list(set([f"{d.metadata['source']} p.{d.metadata['page']}" for d in docs]))
        confidence = get_confidence(docs, question)

        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
        prompt = build_prompt(question, context, store["chat_history"], mode, persona, store["doc_language"])
        initial = llm.invoke(prompt).content
        answer = self_reflect_and_improve(question, context, initial, llm)
        answer = apply_confidence_adaptation(answer, confidence)

        store["chat_history"].append({"role": "user", "content": question})
        store["chat_history"].append({"role": "assistant", "content": answer, "sources": sources, "confidence": confidence})

        return {"answer": answer, "sources": sources, "confidence": confidence, "vague": False}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/dna")
async def get_dna():
    return {"dna": store["dna"]}


@app.post("/api/tools")
async def run_tool(tool: str = Form(...)):
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
        sample = store["full_text"][:4000]
        lang = store["doc_language"]
        lang_note = f" Respond in {lang}." if lang != "English" else ""

        prompts = {
            "summary": f"Create a structured summary: 1) Overview 2) Key Points 3) Important Details 4) Conclusion.{lang_note}\n\nDocument:\n{sample}",
            "quiz": f"Generate 5 multiple-choice quiz questions with 4 options (A-D), mark correct answer.{lang_note}\n\nDocument:\n{sample}",
            "email": f"Draft a professional email. Include subject line, greeting, body, call to action.{lang_note}\n\nDocument:\n{sample}",
            "contradictions": f"Find contradictions or inconsistencies. Be specific. If none, say so.{lang_note}\n\nDocument:\n{sample}",
            "actions": f"Extract all action items as a numbered checklist with owner and priority.{lang_note}\n\nDocument:\n{sample}"
        }

        if tool not in prompts:
            return JSONResponse(status_code=400, content={"error": "Unknown tool."})

        result = llm.invoke(prompts[tool]).content
        return {"result": result}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/timeline")
async def get_timeline():
    try:
        import json as jsonlib
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
        sample = store["full_text"][:6000]
        prompt = f"""Extract ALL dates and events. Return ONLY valid JSON array:
[{{"date":"...","sort_key":"YYYY-MM-DD","event":"...","type":"deadline/milestone/event/period/announcement/other","importance":"high/medium/low"}}]
If none found return [].
Document: {sample}"""
        response = llm.invoke(prompt).content.strip()
        response = re.sub(r"```json|```", "", response).strip()
        start = response.find("[")
        end = response.rfind("]") + 1
        data = jsonlib.loads(response[start:end])
        return {"timeline": sorted(data, key=lambda x: x.get("sort_key", "9999"))}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})



@app.post("/api/flashcards")
async def get_flashcards(count: int = Form(10)):
    try:
        import json as jsonlib
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4)
        sample = store["full_text"][:5000]
        prompt = f"""Generate exactly {count} flashcards. Return ONLY valid JSON array:
[{{"question":"...","answer":"...","difficulty":"easy/medium/hard","topic":"..."}}]
Mix difficulty levels. Do NOT number questions.
Material: {sample}"""
        response = llm.invoke(prompt).content.strip()
        response = re.sub(r"```json|```", "", response).strip()
        start = response.find("[")
        end = response.rfind("]") + 1
        cards = jsonlib.loads(response[start:end])
        return {"flashcards": cards}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/compare/upload")
async def upload_compare(files: list[UploadFile] = File(...)):
    try:
        import io
        class FileWrapper:
            def __init__(self, content, name):
                self._content = content
                self.name = name
            def read(self, *args):
                return self._content

        f = files[0]
        content = await f.read()
        wrapped = [FileWrapper(io.BytesIO(content), f.filename)]
        chunks, metas, pages, full_text = extract_text_from_pdfs(wrapped)
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        vs = FAISS.from_texts(chunks, embeddings, metadatas=metas)
        store["compare_vectorstore"] = vs
        store["compare_name"] = f.filename
        store["compare_full_text"] = full_text
        return {"success": True, "name": f.filename}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/compare/chat")
async def compare_chat(question: str = Form(...)):
    try:
        if not store["vectorstore"] or not store["compare_vectorstore"]:
            return JSONResponse(status_code=400, content={"error": "Both documents required."})

        docs_a = store["vectorstore"].similarity_search(question, k=4)
        docs_b = store["compare_vectorstore"].similarity_search(question, k=4)
        context_a = "\n\n".join([d.page_content for d in docs_a])
        context_b = "\n\n".join([d.page_content for d in docs_b])
        sources_a = list(set([f"{d.metadata['source']} p.{d.metadata['page']}" for d in docs_a]))
        sources_b = list(set([f"{d.metadata['source']} p.{d.metadata['page']}" for d in docs_b]))

        doc_a = store["pdf_names"][0] if store["pdf_names"] else "Document A"
        doc_b = store["compare_name"]

        prompt = f"""You are performing a side-by-side document comparison.

Document A ({doc_a}): {context_a}
Document B ({doc_b}): {context_b}

Question: {question}
Answer specifically, label Document A / Document B clearly."""

        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
        answer = llm.invoke(prompt).content

        return {"answer": answer, "sources_a": sources_a, "sources_b": sources_b}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/analytics")
async def analytics():
    return get_analytics(store["chat_history"])


@app.get("/api/state")
async def get_state():
    return {
        "processed": store["vectorstore"] is not None,
        "source_type": store["source_type"],
        "pdf_names": store["pdf_names"],
        "total_pages": store["total_pages"],
        "total_chunks": store["total_chunks"],
        "doc_language": store["doc_language"],
        "dna": store["dna"],
        "chat_history": store["chat_history"],
        "compare_loaded": store["compare_vectorstore"] is not None,
        "compare_name": store["compare_name"],
    }


@app.post("/api/reset")
async def reset():
    for k in store:
        if k in ["vectorstore", "compare_vectorstore"]:
            store[k] = None
        elif k in ["chat_history"]:
            store[k] = []
        elif k in ["total_pages", "total_chunks"]:
            store[k] = 0
        else:
            store[k] = ""
    store["source_type"] = "pdf"
    return {"success": True}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)