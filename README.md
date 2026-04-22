# 🧠 DocuMind AI

**Intelligent document analysis and Q&A — powered by Google Gemini**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://docu-mind-vansh.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python\&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Latest-green)
![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-orange?logo=google)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-purple)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 🔗 Live Demo

👉 https://docu-mind-vansh.streamlit.app/

---

## 📌 What is DocuMind AI?

DocuMind AI is a production-grade **Agentic RAG (Retrieval-Augmented Generation)** system that lets you chat with PDFs, websites, and YouTube videos using AI.

It doesn't just answer questions — it:

* Thinks before responding
* Reviews its own answers
* Adapts based on confidence
* Compares documents
* Extracts timelines
* Generates flashcards

---

## ✨ Features

### 💬 Chat with Any Content

| Source     | Input Method                |
| ---------- | --------------------------- |
| 📄 PDF     | Upload one or multiple PDFs |
| 🌐 Website | Paste any URL               |
| ▶ YouTube  | Paste video link            |

---

### 🤖 3 Agentic AI Layers

| Agent                       | Role                                |
| --------------------------- | ----------------------------------- |
| Clarification Agent         | Detects vague queries (no API cost) |
| Self-Reflection Agent       | Improves generated answers          |
| Confidence Adaptation Agent | Adds uncertainty warnings           |

---

### 🧬 Document DNA

Auto-generated document fingerprint including:

* Domain
* Tone
* Complexity
* Sentiment
* Key themes
* Entities
* Summary
* Unique insights

---

### 🔀 Doc vs Doc Comparison

* Dual FAISS retrieval
* Color-coded sources

  * 🟢 Doc A
  * 🔵 Doc B

---

### 🕐 Timeline Extractor

* Extracts dates, deadlines, milestones
* Visual structured timeline

---

### 🃏 Flashcard Generator

* Auto Q&A cards
* Difficulty filters (Easy / Medium / Hard)

---

### 🛠 Smart Tools

* Auto Summary
* Quiz Generator
* Email Drafter
* Contradiction Finder
* Action Extractor

---

### 📊 Session Analytics

* Confidence trends
* Keyword frequency
* Low-confidence detection

---

### 🌐 Multilingual Support

* Auto language detection
* Responses in same language

---

## 🏗 Project Structure

```bash
documind/
├── app.py
├── utils/
│   ├── styles.py
│   ├── pdf_processor.py
│   ├── ai_helpers.py
│   └── agents.py
└── components/
    ├── tab_chat.py
    ├── tab_dna.py
    ├── tab_tools.py
    ├── tab_analytics.py
    ├── tab_compare.py
    ├── tab_timeline.py
    └── tab_flashcards.py
```

---

## 🔧 RAG Pipeline

```
Input (PDF / URL / YouTube)
→ Text Extraction
→ Chunking (600 chars, 80 overlap)
→ Embedding (Gemini Embedding 001)
→ FAISS Index

Query
→ Clarification Agent
→ Similarity Search (Top-K)
→ Confidence Scoring
→ Answer Generation (Gemini 2.5 Flash)
→ Self-Reflection
→ Confidence Adaptation
→ Final Response + Sources
```

---

---

## 📦 Tech Stack

| Technology             | Purpose           |
| ---------------------- | ----------------- |
| Python 3.12            | Core              |
| Streamlit              | UI                |
| LangChain              | AI orchestration  |
| Gemini 2.5 Flash       | LLM               |
| Gemini Embedding       | Vector generation |
| FAISS                  | Vector search     |
| PyPDF                  | PDF parsing       |
| BeautifulSoup          | Web scraping      |
| youtube-transcript-api | Video transcripts |
| Web Speech API         | Voice input       |


---

## 👨‍💻 Author

**Vansh Mahajan**

* 📧 [vansh150705@gmail.com](mailto:vansh150705@gmail.com)
* 💼 https://www.linkedin.com/in/vansh-mahajan-napv/
* 🐙 https://github.com/Vansh150705

---

<p align="center">
Built with 🧠 by Vansh Mahajan
</p>
