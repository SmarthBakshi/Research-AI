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
"""

def check_api_health() -> Dict:
    """Check if API is available"""
    try:
        response = httpx.get(f"{API_BASE_URL}/healthz", timeout=5.0)
        if response.status_code == 200:
            return response.json()
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
        return "<p>No citations available.</p>"

    html = "<div style='margin-top: 20px;'>"
    html += "<h3>📚 Sources</h3>"

    for i, citation in enumerate(citations, 1):
        source_file = citation.get("source_file", "Unknown")
        chunk_index = citation.get("chunk_index", 0)
        excerpt = citation.get("excerpt", "")

        html += f"""
        <div class='citation-box'>
            <strong>[{i}] {source_file}</strong> (Chunk {chunk_index})
            <p style='margin-top: 5px; font-size: 0.9em; color: #555;'>{excerpt}</p>
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
        # Check API health first
        health = check_api_health()
        if health.get("status") != "ok":
            return "<p style='color: red;'>⚠️ API is not available. Please check if the backend is running.</p>", ""

        # Make request to /ask endpoint
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

            # Format answer
            answer_html = f"""
            <div style='background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <h3 style='color: #2c3e50; margin-top: 0;'>💡 Answer</h3>
                <p style='font-size: 1.1em; line-height: 1.6;'>{answer}</p>
                <hr style='margin: 20px 0; border: none; border-top: 1px solid #eee;'>
                <p style='color: #7f8c8d; font-size: 0.9em;'>
                    <strong>Model:</strong> {model} |
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
                return "<p>No results found.</p>"

            html = f"<h3>🔍 Found {len(results)} results</h3>"

            for i, result in enumerate(results, 1):
                chunk_text = result.get("chunk_text", "")
                source_file = result.get("source_file", "Unknown")
                chunk_index = result.get("chunk_index", 0)
                score = result.get("score", 0.0)

                # Truncate long text
                display_text = chunk_text[:400] + "..." if len(chunk_text) > 400 else chunk_text

                html += f"""
                <div style='background-color: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #3498db;'>
                    <h4 style='margin-top: 0; color: #2c3e50;'>[{i}] {source_file}</h4>
                    <p style='color: #7f8c8d; font-size: 0.9em;'>Chunk {chunk_index} | Score: {score:.4f}</p>
                    <p style='line-height: 1.6;'>{display_text}</p>
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
    gr.Markdown("""
    # 🚀 ResearchAI: Scientific Paper Q&A

    Ask questions about research papers from arXiv and get AI-powered answers with citations.
    """)

    with gr.Tabs():
        # Tab 1: Ask Questions
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

        # Tab 3: Statistics
        with gr.Tab("📊 Statistics"):
            stats_output = gr.HTML()
            refresh_button = gr.Button("Refresh Stats")

            refresh_button.click(
                fn=show_stats,
                outputs=stats_output
            )

            # Load stats on tab open
            demo.load(show_stats, outputs=stats_output)

    gr.Markdown("""
    ---

    **Tips:**
    - Use **hybrid search** for best results (combines keyword + semantic matching)
    - Increase **k** to get more context (but may slow down responses)
    - Adjust **temperature** for more creative (higher) or focused (lower) answers
    - Check the **Statistics** tab to see indexed paper counts

    **Built with:** FastAPI, OpenSearch, HuggingFace Transformers, Ollama
    """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        share=False
    )
