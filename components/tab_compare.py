"""
components/tab_compare.py
Document vs Document Comparison — upload a second PDF and compare
it against the primary document using dual vector store retrieval.
"""

import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from utils.pdf_processor import extract_text_from_pdfs


def render_compare_tab():

    st.markdown('<div class="section-label" style="margin-bottom:0.6rem;">Document Comparison</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.875rem;color:#6b7280;margin-bottom:1.2rem;line-height:1.65;">'
        'Upload a second PDF to compare against your primary document. '
        'Ask anything — differences, similarities, contradictions, or specific topics across both.'
        '</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.get("compare_processed"):
        st.markdown('<div class="section-label">Upload Second Document</div>', unsafe_allow_html=True)

        second_file = st.file_uploader(
            "Second PDF", type="pdf",
            key="compare_uploader",
            label_visibility="collapsed"
        )

        if second_file:
            st.markdown(
                f'<div class="upload-success">✅ {second_file.name} ready</div>',
                unsafe_allow_html=True
            )
            if st.button("⚡  Index Second Document"):
                with st.spinner("Indexing second document..."):
                    chunks, metas, pages, full_text = extract_text_from_pdfs([second_file])
                    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
                    vectorstore_b = FAISS.from_texts(chunks, embeddings, metadatas=metas)
                    st.session_state.compare_vectorstore  = vectorstore_b
                    st.session_state.compare_name        = second_file.name
                    st.session_state.compare_full_text   = full_text
                    st.session_state.compare_processed   = True
                    st.session_state.compare_history     = []
                st.rerun()

    else:
        doc_a = st.session_state.pdf_names[0] if st.session_state.pdf_names else "Document A"
        doc_b = st.session_state.compare_name

        st.markdown(f"""
        <div style="display:flex;gap:0.6rem;margin-bottom:1.1rem;flex-wrap:wrap;">
            <span class="doc-pill" style="background:#f0fdf4;border-color:#bbf7d0;color:#15803d;">📄 A: {doc_a}</span>
            <span style="color:#9ca3af;font-size:0.85rem;align-self:center;">vs</span>
            <span class="doc-pill" style="background:#eff6ff;border-color:#bfdbfe;color:#1d4ed8;">📄 B: {doc_b}</span>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.compare_history:
            st.markdown('<div class="section-label">Quick Comparisons</div>', unsafe_allow_html=True)
            quick = [
                "What are the key differences between these two documents?",
                "What do both documents agree on?",
                "Which document is more comprehensive?",
                "What is in Document A but missing in Document B?"
            ]
            c1, c2 = st.columns(2)
            for i, q in enumerate(quick):
                with (c1 if i % 2 == 0 else c2):
                    st.markdown('<div class="sug-pill-wrap">', unsafe_allow_html=True)
                    if st.button(q, key=f"cmp_q_{i}"):
                        st.session_state.compare_suggested = q
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div style="height:0.8rem;"></div>', unsafe_allow_html=True)

        for msg in st.session_state.compare_history:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="msg-user"><div class="msg-user-inner">{msg["content"]}</div></div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="msg-bot"><div class="msg-bot-inner">{msg["content"]}</div></div>',
                    unsafe_allow_html=True
                )
                if msg.get("sources_a") or msg.get("sources_b"):
                    chips_a = "".join([f'<span class="source-chip" style="background:#f0fdf4;border-color:#bbf7d0;color:#15803d;">A: {s}</span>' for s in msg.get("sources_a", [])])
                    chips_b = "".join([f'<span class="source-chip" style="background:#eff6ff;border-color:#bfdbfe;color:#1d4ed8;">B: {s}</span>' for s in msg.get("sources_b", [])])
                    st.markdown(f'<div style="margin-top:0.3rem;">{chips_a}{chips_b}</div>', unsafe_allow_html=True)

        st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
        col_reset, _ = st.columns([1, 3])
        with col_reset:
            st.markdown('<div class="light-btn">', unsafe_allow_html=True)
            if st.button("↺ Change Doc B"):
                for k in ["compare_vectorstore", "compare_name", "compare_full_text",
                          "compare_processed", "compare_history", "compare_suggested"]:
                    st.session_state.pop(k, None)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        question = st.chat_input("Ask anything about both documents…", key="compare_input")

        if st.session_state.get("compare_suggested"):
            question = st.session_state.compare_suggested
            del st.session_state["compare_suggested"]

        if question:
            st.session_state.compare_history.append({"role": "user", "content": question})

            skeleton_ph = st.empty()
            skeleton_ph.markdown("""
            <div style="display:flex;justify-content:flex-start;margin:1rem 0;">
                <div class="skeleton-wrap">
                    <div class="skeleton-line full"></div>
                    <div class="skeleton-line medium"></div>
                    <div class="skeleton-line short"></div>
                    <div style="margin-top:0.6rem;display:flex;align-items:center;gap:0.5rem;">
                        <div class="typing-dots"><span></span><span></span><span></span></div>
                        <span class="typing-text">Comparing both documents…</span>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            docs_a = st.session_state.vectorstore.similarity_search(question, k=4)
            docs_b = st.session_state.compare_vectorstore.similarity_search(question, k=4)

            context_a = "\n\n".join([d.page_content for d in docs_a])
            context_b = "\n\n".join([d.page_content for d in docs_b])

            sources_a = list(set([f"{d.metadata['source']} p.{d.metadata['page']}" for d in docs_a]))
            sources_b = list(set([f"{d.metadata['source']} p.{d.metadata['page']}" for d in docs_b]))

            compare_prompt = f"""You are DocuMind AI performing a side-by-side document comparison.

You have been given relevant excerpts from TWO documents.

Document A ({doc_a}):
{context_a}

Document B ({doc_b}):
{context_b}

User question: {question}

Instructions:
- Answer specifically based on both documents
- Clearly label which document you are referring to (Document A / Document B)
- Be specific and reference actual content from both
- If information only exists in one document, say so clearly
- Do not fabricate information not present in either document

Answer:"""

            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
            response = llm.invoke(compare_prompt)
            answer = response.content

            skeleton_ph.empty()

            st.session_state.compare_history.append({
                "role": "assistant",
                "content": answer,
                "sources_a": sources_a,
                "sources_b": sources_b
            })
            st.rerun()