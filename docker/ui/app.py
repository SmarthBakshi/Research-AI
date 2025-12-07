"""
ResearchAI Gradio UI

Interactive chat interface for querying scientific papers using RAG.

Author: ResearchAI Team
"""

import os
import gradio as gr
import httpx
from typing import List, Dict, Tuple

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")

# Custom CSS for better UI
custom_css = """
.citation-box {
    background-color: #f0f0f0;
    border-left: 4px solid #4CAF50;
    padding: 10px;
    margin: 10px 0;
    border-radius: 4px;
}
.stat-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}
footer {
    display: none !important;
}
.gradio-container .footer {
    display: none !important;
}
"""

def check_api_health() -> Dict:
    """Check if API is available"""
    try:
        response = httpx.get(f"{API_BASE_URL}/", timeout=5.0)
        if response.status_code == 200:
            return {"status": "ok", "services": {}}
        return {"status": "error", "services": {}}
    except Exception as e:
        return {"status": "error", "message": str(e), "services": {}}

def get_stats() -> Dict:
    """Get system statistics"""
    try:
        response = httpx.get(f"{API_BASE_URL}/stats", timeout=5.0)
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception:
        return {}

def format_citations(citations: List[Dict]) -> str:
    """Format citations as HTML"""
    if not citations:
        return "<p style='color: var(--body-text-color);'>No citations available.</p>"

    html = "<div style='margin-top: 20px;'>"
    html += "<h3 style='color: var(--body-text-color);'>📚 Sources</h3>"

    for i, citation in enumerate(citations, 1):
        source_file = citation.get("source_file", "Unknown")
        chunk_index = citation.get("chunk_index", 0)
        excerpt = citation.get("excerpt", "")

        html += f"""
        <div style='background-color: var(--block-background-fill); border-left: 4px solid #4CAF50; padding: 15px; margin: 10px 0; border-radius: 8px;'>
            <strong style='color: var(--body-text-color);'>[{i}] {source_file}</strong> <span style='color: var(--body-text-color-subdued);'>(Chunk {chunk_index})</span>
            <p style='margin-top: 8px; font-size: 0.95em; color: var(--body-text-color); line-height: 1.6;'>{excerpt}</p>
        </div>
        """

    html += "</div>"
    return html

def ask_question(question: str, k: int, temperature: float, search_type: str) -> Tuple[str, str]:
    """
    Ask a question to the RAG system

    Returns:
        Tuple of (answer_html, citations_html)
    """
    if not question.strip():
        return "<p style='color: red;'>Please enter a question.</p>", ""

    try:
        # Make request to /ask endpoint directly (no health check needed)
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{API_BASE_URL}/ask",
                json={
                    "question": question,
                    "k": k,
                    "temperature": temperature,
                    "search_type": search_type
                }
            )

        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer generated.")
            citations = data.get("citations", [])
            model = data.get("model", "unknown")
            retrieved = data.get("retrieved_chunks", 0)

            # Format answer (without model name)
            answer_html = f"""
            <div style='background-color: var(--block-background-fill); padding: 20px; border-radius: 8px; border: 1px solid var(--border-color-primary);'>
                <h3 style='color: var(--body-text-color); margin-top: 0;'>💡 Answer</h3>
                <p style='font-size: 1.1em; line-height: 1.6; color: var(--body-text-color);'>{answer}</p>
                <hr style='margin: 20px 0; border: none; border-top: 1px solid var(--border-color-primary);'>
                <p style='color: var(--body-text-color-subdued); font-size: 0.9em;'>
                    <strong>Retrieved:</strong> {retrieved} chunks |
                    <strong>Search:</strong> {search_type}
                </p>
            </div>
            """

            citations_html = format_citations(citations)

            return answer_html, citations_html

        elif response.status_code == 503:
            return "<p style='color: orange;'>⚠️ Service unavailable. Some components may not be initialized yet.</p>", ""
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return f"<p style='color: red;'>Error: {error_detail}</p>", ""

    except httpx.TimeoutException:
        return "<p style='color: red;'>⏱️ Request timed out. The question may be too complex or the LLM is slow.</p>", ""
    except httpx.ConnectError:
        return "<p style='color: red;'>⚠️ Cannot connect to API. Please check if the backend container is running.</p>", ""
    except Exception as e:
        return f"<p style='color: red;'>Error: {str(e)}</p>", ""

def search_papers(query: str, k: int, search_type: str) -> str:
    """Search for relevant paper chunks"""
    if not query.strip():
        return "<p style='color: red;'>Please enter a search query.</p>"

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_BASE_URL}/search",
                json={
                    "query": query,
                    "k": k,
                    "search_type": search_type
                }
            )

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            if not results:
                return "<p style='color: var(--body-text-color);'>No results found.</p>"

            html = f"<h3 style='color: var(--body-text-color);'>🔍 Found {len(results)} results</h3>"

            for i, result in enumerate(results, 1):
                chunk_text = result.get("chunk_text", "")
                source_file = result.get("source_file", "Unknown")
                chunk_index = result.get("chunk_index", 0)
                score = result.get("score", 0.0)

                # Truncate long text
                display_text = chunk_text[:400] + "..." if len(chunk_text) > 400 else chunk_text

                html += f"""
                <div style='background-color: var(--block-background-fill); padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #3498db; border: 1px solid var(--border-color-primary);'>
                    <h4 style='margin-top: 0; color: var(--body-text-color);'>[{i}] {source_file}</h4>
                    <p style='color: var(--body-text-color-subdued); font-size: 0.9em;'>Chunk {chunk_index} | Score: {score:.4f}</p>
                    <p style='line-height: 1.6; color: var(--body-text-color);'>{display_text}</p>
                </div>
                """

            return html
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return f"<p style='color: red;'>Error: {error_detail}</p>"

    except Exception as e:
        return f"<p style='color: red;'>Error: {str(e)}</p>"

def show_stats() -> str:
    """Display system statistics"""
    health = check_api_health()
    stats = get_stats()

    services = health.get("services", {})
    embedder_status = "✅" if services.get("embedder") else "❌"
    opensearch_status = "✅" if services.get("opensearch") else "❌"
    ollama_status = "✅" if services.get("ollama") else "❌"

    total_chunks = stats.get("total_chunks", 0)
    indexed_chunks = stats.get("indexed_chunks", 0)
    unique_papers = stats.get("unique_papers", 0)

    html = f"""
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;'>
        <div class='stat-card'>
            <h2 style='margin: 0;'>{total_chunks:,}</h2>
            <p style='margin: 10px 0 0 0; opacity: 0.9;'>Total Chunks</p>
        </div>
        <div class='stat-card'>
            <h2 style='margin: 0;'>{indexed_chunks:,}</h2>
            <p style='margin: 10px 0 0 0; opacity: 0.9;'>Indexed Chunks</p>
        </div>
        <div class='stat-card'>
            <h2 style='margin: 0;'>{unique_papers:,}</h2>
            <p style='margin: 10px 0 0 0; opacity: 0.9;'>Unique Papers</p>
        </div>
    </div>

    <div style='background-color: #ecf0f1; padding: 20px; border-radius: 8px; margin-top: 20px;'>
        <h3 style='margin-top: 0;'>🔧 Service Status</h3>
        <ul style='list-style: none; padding: 0;'>
            <li style='margin: 10px 0;'>{embedder_status} <strong>Embedding Model</strong></li>
            <li style='margin: 10px 0;'>{opensearch_status} <strong>OpenSearch</strong></li>
            <li style='margin: 10px 0;'>{ollama_status} <strong>Ollama LLM</strong></li>
        </ul>
        <p style='color: #7f8c8d; font-size: 0.9em; margin-top: 15px;'>
            Last checked: {health.get("timestamp", "Unknown")}
        </p>
    </div>
    """

    return html

# Example questions
example_questions = [
    "What are the latest advances in transformer architectures?",
    "Explain attention mechanisms in neural networks",
    "What is the difference between BERT and GPT models?",
    "How do diffusion models work?",
    "What are the applications of reinforcement learning?"
]

# Build Gradio Interface
with gr.Blocks(css=custom_css, theme=gr.themes.Soft(), title="ResearchAI") as demo:
    gr.HTML("""
    <div style="text-align: center; padding: 30px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 20px;">
        <h1 style="color: white; font-size: 42px; margin: 0 0 10px 0; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">
            🚀 ResearchAI: Scientific Paper Q&A
        </h1>
        <p style="color: rgba(255,255,255,0.95); font-size: 18px; margin: 10px 0 5px 0; font-weight: 500;">
            Powered by <strong>Retrieval-Augmented Generation (RAG)</strong>
        </p>
        <p style="color: rgba(255,255,255,0.85); font-size: 16px; margin: 0;">
            Ask questions about research papers from arXiv and get AI-powered answers with citations
        </p>
    </div>
    """)

    with gr.Tabs():
        # Tab 1: About
        with gr.Tab("ℹ️ About"):
            gr.Markdown("""
            # 🚀 Welcome to ResearchAI!

            ResearchAI is an **AI-powered research paper Q&A system** that helps you explore and understand scientific papers from arXiv using advanced Retrieval-Augmented Generation (RAG).
            """)

            with gr.Row():
                with gr.Column():
                    gr.Markdown("""
                    ### 📖 How to Use

                    #### **💬 Ask Questions Tab**
                    1. **Type your question** about research topics
                       - Example: *"What is attention in neural networks?"*
                       - Example: *"How do transformers differ from RNNs?"*

                    2. **Adjust settings:**
                       - **Number of sources (k)**: How many relevant excerpts to retrieve (1-10)
                       - **Temperature**: Controls answer creativity (0 = focused, 1.5 = creative)
                       - **Search type**: Hybrid combines keyword + semantic search

                    3. **Click "Ask Question"** to get AI-generated answers with citations

                    #### **🔍 Search Papers Tab**
                    - Search for specific topics or keywords in indexed papers
                    - Get direct excerpts from relevant papers
                    - Useful for exploring what papers are available
                    """)

                with gr.Column():
                    gr.Markdown("""
                    ### 💡 Tips for Best Results

                    ✅ **Be specific** in your questions
                    - Good: *"How does self-attention work in transformers?"*
                    - Avoid: *"What is AI?"*

                    ✅ **Use hybrid search** for most accurate results

                    ✅ **Check citations** to verify information

                    ✅ **Adjust temperature** based on your needs:
                    - **Low (0-0.3)**: Precise, factual answers
                    - **Medium (0.4-0.7)**: Balanced responses
                    - **High (0.8-1.5)**: Creative, exploratory answers

                    ✅ **Review multiple sources** for comprehensive understanding
                    """)

            gr.Markdown("---")

            with gr.Row():
                with gr.Column():
                    gr.Markdown("""
                    ### 📚 Current Knowledge Base

                    This system is indexed with research papers on:
                    - 🤖 Transformer architectures
                    - 🧠 Attention mechanisms
                    - 📝 Large language models (LLMs)
                    - 👁️ Computer vision models
                    - 🔬 Deep learning techniques

                    *More papers are continuously being added!*
                    """)

                with gr.Column():
                    gr.Markdown("""
                    ### 🔧 Technical Stack

                    - **Frontend**: Gradio
                    - **Backend**: FastAPI
                    - **Vector Search**: OpenSearch with kNN
                    - **Embeddings**: HuggingFace Transformers (e5-base-v2)
                    - **LLM**: OpenAI GPT-4o-mini / Ollama (local GPU)
                    - **Database**: PostgreSQL on Google Cloud SQL
                    - **Orchestration**: Apache Airflow
                    - **Hosting**: Google Cloud Platform
                    """)

            gr.Markdown("---")

            gr.Markdown("""
            ### 🎯 What Makes ResearchAI Different?

            - **📄 Citation-Backed Answers**: Every answer includes source excerpts from papers
            - **🔍 Hybrid Search**: Combines BM25 keyword search with semantic vector search
            - **⚡ Fast & Scalable**: Optimized for sub-second query latency
            - **🎓 Academic Focus**: Specifically designed for scientific literature
            - **🔓 Open Architecture**: Built with open-source tools and transparent methods

            ### 🐛 Issues or Questions?

            Feel free to reach out via the social links at the bottom of the page!
            """)

            gr.HTML("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; margin-top: 20px; text-align: center;">
                <h3 style="margin-top: 0; color: white;">🎓 Perfect for Researchers, Students, and AI Enthusiasts!</h3>
                <p style="margin-bottom: 0; font-size: 16px; opacity: 0.95;">
                    Explore cutting-edge research papers with the power of AI-assisted understanding.
                </p>
            </div>
            """)

        # Tab 2: Search Papers
        with gr.Tab("🔍 Search Papers"):
            with gr.Row():
                with gr.Column(scale=1):
                    search_input = gr.Textbox(
                        label="Search Query",
                        placeholder="Enter keywords or semantic query...",
                        lines=2
                    )

                    search_k_slider = gr.Slider(
                        minimum=1,
                        maximum=20,
                        value=5,
                        step=1,
                        label="Number of results"
                    )

                    search_type_dropdown = gr.Radio(
                        choices=["hybrid", "dense"],
                        value="hybrid",
                        label="Search Type"
                    )

                    search_button = gr.Button("Search", variant="primary")

                with gr.Column(scale=2):
                    search_output = gr.HTML(label="Search Results")

            search_button.click(
                fn=search_papers,
                inputs=[search_input, search_k_slider, search_type_dropdown],
                outputs=search_output
            )

        # Tab 3: Ask Questions
        with gr.Tab("💬 Ask Questions"):
            with gr.Row():
                with gr.Column(scale=2):
                    question_input = gr.Textbox(
                        label="Your Question",
                        placeholder="Ask anything about the research papers...",
                        lines=3
                    )

                    with gr.Row():
                        k_slider = gr.Slider(
                            minimum=1,
                            maximum=10,
                            value=5,
                            step=1,
                            label="Number of sources to retrieve"
                        )
                        temp_slider = gr.Slider(
                            minimum=0.0,
                            maximum=1.5,
                            value=0.7,
                            step=0.1,
                            label="Temperature (creativity)"
                        )

                    search_type_radio = gr.Radio(
                        choices=["hybrid", "dense"],
                        value="hybrid",
                        label="Search Type",
                        info="Hybrid uses both keyword and semantic search"
                    )

                    ask_button = gr.Button("Ask Question", variant="primary", size="lg")

                    gr.Examples(
                        examples=example_questions,
                        inputs=question_input,
                        label="Example Questions"
                    )

                with gr.Column(scale=3):
                    answer_output = gr.HTML(label="Answer")
                    citations_output = gr.HTML(label="Citations")

            ask_button.click(
                fn=ask_question,
                inputs=[question_input, k_slider, temp_slider, search_type_radio],
                outputs=[answer_output, citations_output]
            )

    gr.Markdown("""
    ---

    **Quick Tips:**
    - Use **hybrid search** for best results (combines keyword + semantic matching)
    - Increase **k** to get more context (but may slow down responses)
    - Adjust **temperature** for more creative (higher) or focused (lower) answers
    - Check the **About** tab for detailed usage instructions

    **Built with:** FastAPI, OpenSearch, HuggingFace Transformers, OpenAI
    """)

    gr.HTML("""
    <div style="text-align: center; margin-top: 40px; padding: 30px 20px; border-top: 1px solid var(--border-color-primary); background-color: var(--background-fill-secondary);">
        <div style="margin-bottom: 15px; font-size: 16px; color: var(--body-text-color);">
            Built with ❤️ by <a href="https://github.com/smarthbakshi" target="_blank" style="color: #667eea; text-decoration: none; font-weight: 600;">Smarth Bakshi</a>
        </div>
        <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
            <a href="https://github.com/smarthbakshi" target="_blank"
               style="background: #333; color: white; padding: 12px; border-radius: 50%; text-decoration: none; transition: all 0.3s; display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px;"
               onmouseover="this.style.transform='scale(1.1)'; this.style.opacity='0.8'" onmouseout="this.style.transform='scale(1)'; this.style.opacity='1'">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.762-1.605-2.665-.3-5.466-1.332-5.466-5.91 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.59-2.805 5.61-5.475 5.91.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                </svg>
            </a>
            <a href="https://linkedin.com/in/smarthbakshi" target="_blank"
               style="background: #0077b5; color: white; padding: 12px; border-radius: 50%; text-decoration: none; transition: all 0.3s; display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px;"
               onmouseover="this.style.transform='scale(1.1)'; this.style.opacity='0.8'" onmouseout="this.style.transform='scale(1)'; this.style.opacity='1'">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
            </a>
            <a href="mailto:bakshismarth.20@gmail.com"
               style="background: #667eea; color: white; padding: 12px; border-radius: 50%; text-decoration: none; transition: all 0.3s; display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px;"
               onmouseover="this.style.transform='scale(1.1)'; this.style.opacity='0.8'" onmouseout="this.style.transform='scale(1)'; this.style.opacity='1'">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                </svg>
            </a>
        </div>
    </div>
    """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        share=False
    )
