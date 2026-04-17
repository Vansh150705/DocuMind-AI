# 🧠 DocuMind AI

**Intelligent document analysis and Q&A — powered by Google Gemini**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://docu-mind-vansh.streamlit.app/)
&nbsp;
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Latest-green)
![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-orange?logo=google)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-purple)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 🔗 Live Demo

**[https://docu-mind-vansh.streamlit.app/](https://docu-mind-vansh.streamlit.app/)**

---

## 📌 What is DocuMind AI?

DocuMind AI is a production-grade **Agentic RAG (Retrieval-Augmented Generation)** system that lets you upload PDF documents and have intelligent, multi-layered AI conversations with them.

Instead of just answering questions, DocuMind AI thinks before it responds — it detects vague queries, reviews its own answers, and adapts its response based on how confident it is. It also profiles your document the moment it's uploaded, supports multiple languages, and provides 5 one-click automation tools beyond Q&A.

---

## ✨ Features

### 💬 Intelligent Chat
- Upload single or multiple PDFs and ask anything about them
- Answers are grounded in document content — no hallucination
- Source chips show exactly which file and page each answer came from
- Colour-coded confidence bar (High / Medium / Low) per answer
- Full conversation history with smooth animations

### 🤖 3 Agentic AI Layers
| Agent | What it does |
|-------|-------------|
| **Clarification Agent** | Detects vague queries (e.g. "explain this") before retrieval and asks for clarification instead — zero API cost |
| **Self-Reflection Agent** | After generating an answer, the AI reviews its own response and improves it if incomplete |
| **Confidence Adaptation Agent** | Automatically appends warnings or disclaimers based on how well-supported the answer is |

### 🧬 Document DNA
The moment a PDF is processed, Gemini automatically generates a document fingerprint:
- Inferred title and one-line summary
- Domain (Medical / Legal / Technical / Academic / Business)
- Tone (Formal / Conversational / Persuasive / Academic)
- Complexity, Sentiment & Informativeness scores (0–100)
- Key themes and key entities
- Auto-detected language
- One unusual, non-obvious insight about the document

### 🎭 Response Modes
Switch how the AI responds to the same question:
- **🎯 Standard Q&A** — Strict, factual answers from document only
- **🧒 Explain Simply** — Like you're 10 years old, with analogies
- **💼 Executive Brief** — Bullet points, one key insight, no fluff
- **⚖️ Devil's Advocate** — Both sides of every claim, challenges assumptions

### 🛠 Smart Tools (one-click)
- 📝 Auto-Summary — 4-section structured summary
- ❓ Quiz Generator — 5 MCQs with correct answers
- 📧 Email Drafter — Professional email from document content
- 🔍 Contradiction Finder — Flags inconsistencies in the document
- 📊 Action Item Extractor — Numbered checklist with priority

### 📊 Session Analytics
- Confidence trend per answer
- Most asked-about keywords
- Session overview (questions asked, avg confidence)
- Low-confidence warnings

### 🎙 Voice Input
- Mic button inside the chat input (like ChatGPT)
- Uses browser's built-in Web Speech API — no API key needed
- Works in Chrome and Edge

### 🌐 Multilingual Support
- Auto-detects document language during DNA analysis
- All answers, summaries, and tool outputs respond in the same language
- Powered by Gemini's native 100+ language support

### 📥 Chat Export
- Download entire conversation as a `.txt` file
- Includes Q&As, source references, confidence scores, and timestamps

---

## 🏗 Architecture

```
documind/
├── app.py                    # Entry point — routing and upload flow
├── utils/
│   ├── styles.py             # CSS + voice input JavaScript
│   ├── pdf_processor.py      # PDF reading and text chunking
│   ├── ai_helpers.py         # Prompt building, DNA, export, analytics
│   └── agents.py             # 3 Agentic AI features
└── components/
    ├── tab_chat.py           # Chat tab
    ├── tab_dna.py            # Document DNA tab
    ├── tab_tools.py          # Smart Tools tab
    └── tab_analytics.py      # Analytics tab
```

---

## 🔧 How It Works

```
PDF Upload → Text Extraction (PyPDF)
          → Chunking (RecursiveCharacterTextSplitter, 600 chars, 80 overlap)
          → Embedding (Gemini Embedding 001)
          → Vector Indexing (FAISS)
          → DNA Analysis (Gemini 2.5 Flash → JSON)

User Query → Clarification Agent (vague? → ask for clarification)
           → Vector Similarity Search (top-5 chunks)
           → Confidence Scoring (keyword overlap heuristic)
           → Answer Generation (Gemini 2.5 Flash)
           → Self-Reflection Agent (review + improve)
           → Confidence Adaptation (add warning/disclaimer)
           → Display with sources + confidence bar
```

---

## 📦 Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python 3.12** | Core language |
| **Streamlit** | Frontend web framework |
| **LangChain** | AI orchestration (text splitting, model wrappers, FAISS integration) |
| **Google Gemini 2.5 Flash** | LLM for answer generation and DNA analysis |
| **Gemini Embedding 001** | Text → vector conversion |
| **FAISS** | In-memory vector similarity search |
| **PyPDF** | PDF text extraction |
| **Web Speech API** | Browser-native voice input |
| **python-dotenv** | Environment variable management |

---

## 🗂 Requirements

```txt
streamlit
langchain
langchain-community
langchain-google-genai
langchain-text-splitters
faiss-cpu
pypdf
python-dotenv
google-generativeai
```

---


## 👨‍💻 Author

**Vansh Mahajan**
- 📧 vansh150705@gmail.com
- 💼 [LinkedIn](https://www.linkedin.com/in/vansh-mahajan-napv/)
- 🐙 [GitHub](https://github.com/Vansh150705)

---

## 📄 License

This project is licensed under the MIT License.

---

<p align="center">Built with 🧠 by Vansh Mahajan</p>