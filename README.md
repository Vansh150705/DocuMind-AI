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

Instead of just answering questions, DocuMind AI thinks before it responds — it detects vague queries, reviews its own answers, adapts responses based on confidence, compares two documents side-by-side, and automatically extracts chronological timelines from any document.

---

## ✨ Features

### 💬 Intelligent Chat
- Upload single or multiple PDFs and ask anything about them
- Answers grounded in document content — no hallucination
- Source chips show exactly which file and page each answer came from
- Colour-coded confidence bar (High / Medium / Low) per answer
- Full conversation history with smooth animations and skeleton loader

### 🤖 3 Agentic AI Layers
| Agent | What it does |
|-------|-------------|
| **Clarification Agent** | Detects vague queries before retrieval and asks for clarification — zero API cost |
| **Self-Reflection Agent** | Reviews its own answer after generation and improves it if incomplete |
| **Confidence Adaptation Agent** | Appends warnings or disclaimers based on retrieval confidence score |

### 🔀 Document vs Document Comparison 
- Upload a second PDF and compare it against your primary document
- Queries both vector stores simultaneously — dual RAG retrieval
- Colour-coded source chips: **green = Doc A**, **blue = Doc B**
- 4 quick comparison buttons pre-loaded (differences, agreements, gaps)
- Works for contracts, reports, research papers, proposals — any two PDFs

### 🕐 Document Timeline Extractor 
- One click extracts every date, deadline, milestone, and event from the document
- Displays as a visual **vertical colour-coded timeline**
- Event types: ⏰ Deadlines, 🏁 Milestones, 📌 Events, 📆 Periods, 📢 Announcements
- High / Medium / Low priority labels
- Filter by event type
- Export timeline as `.txt` file

### 🧬 Document DNA
Auto-generated document fingerprint on upload:
- Inferred title and one-line summary
- Domain, Tone, Language detection
- Complexity, Sentiment & Informativeness scores (0–100)
- Key themes, key entities, unusual insight

### 🎭 Response Modes
- 🎯 Standard Q&A
- 🧒 Explain Simply (ELI5)
- 💼 Executive Brief
- ⚖️ Devil's Advocate

### 🛠 Smart Tools (one-click)
- 📝 Auto-Summary
- ❓ Quiz Generator
- 📧 Email Drafter
- 🔍 Contradiction Finder
- 📊 Action Item Extractor

### 📊 Session Analytics
- Confidence trend per answer
- Most asked-about keywords
- Low-confidence warnings


### 🌐 Multilingual Support
- Auto-detects document language
- Answers in the same language automatically

### 📥 Chat Export
- Download full conversation as `.txt`

---

## 🏗 Architecture

```bash
documind/
├── app.py                    # Main entry point (Streamlit app)

├── utils/
│   ├── styles.py             # UI styling + voice integration
│   ├── pdf_processor.py      # PDF parsing, cleaning & chunking
│   ├── ai_helpers.py         # Prompts, DNA generation, analytics
│   └── agents.py             # Agentic AI logic (3 agents)

├── components/
│   ├── tab_chat.py           # Chat interface (Q&A)
│   ├── tab_dna.py            # Document DNA visualization
│   ├── tab_tools.py          # Smart tools (summary, quiz, etc.)
│   ├── tab_analytics.py      # Session analytics dashboard
│   ├── tab_compare.py        # Document comparison module
│   └── tab_timeline.py       # Timeline extraction module
```
---

## ⚙️ How It Works

### 📄 Document Processing
- PDF Upload  
- Text Extraction *(PyPDF)*  
- Chunking *(600 chars, 80 overlap)*  
- Embedding *(Gemini Embedding 001)*  
- Vector Storage *(FAISS)*  
- Document DNA Analysis *(Gemini → JSON)*  

---

### 💬 Query Processing
- User Query  
- Clarification Agent *(handles vague queries)*  
- Vector Similarity Search *(Top-5 chunks)*  
- Confidence Scoring *(keyword overlap)*  

---

### 🤖 Response Generation
- Answer Generation *(Gemini 2.5 Flash)*  
- Self-Reflection Agent *(review & improve)*  
- Confidence Adaptation *(warnings if needed)*  
- Final Response with Sources + Confidence Bar  

---

### 🔀 Advanced Features

#### Document Comparison
- Dual FAISS Retrieval *(Doc A + Doc B)*  
- Combined Context → Gemini  
- Color-coded Source Attribution  

#### Timeline Extraction
- Date Extraction *(Gemini)*  
- Structured JSON  
- Chronological Sorting  
- Visual Timeline Output  

---

## 📦 Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.12 | Core language |
| Streamlit | Frontend framework |
| LangChain | AI orchestration |
| Google Gemini 2.5 Flash | LLM — answers, DNA, comparison, timeline |
| Gemini Embedding 001 | Text → vector conversion |
| FAISS | In-memory vector similarity search |
| PyPDF | PDF text extraction |
| Web Speech API | Browser-native voice input |
| python-dotenv | Environment variable management |

---

## 🛣 Roadmap

- [ ] Web page Q&A (paste a URL, chat with any website)
- [ ] YouTube video Q&A (transcript extraction)
- [ ] Persistent vector storage
- [ ] OCR for scanned PDFs
- [ ] User authentication
- [ ] Docker deployment

---

## 👨‍💻 Author

**Vansh Mahajan**
- 📧 vansh150705@gmail.com
- 💼 [LinkedIn](https://www.linkedin.com/in/vansh-mahajan-napv/)
- 🐙 [GitHub](https://github.com/Vansh150705)

---

<p align="center">Built with 🧠 by Vansh Mahajan</p>
