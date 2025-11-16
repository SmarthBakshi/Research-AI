"""
Standalone UI test - runs Gradio UI with mock API responses
Use this to test the UI without running the full backend
"""

import gradio as gr
from typing import List, Dict, Tuple

# Custom CSS
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

# Mock functions for standalone testing
def mock_ask_question(question: str, k: int, temperature: float, search_type: str) -> Tuple[str, str]:
    """Mock Q&A function with sample response"""
    if not question.strip():
        return "<p style='color: red;'>Please enter a question.</p>", ""

    # Sample answer
    answer_html = f"""
    <div style='background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
        <h3 style='color: #2c3e50; margin-top: 0;'>💡 Answer</h3>
        <p style='font-size: 1.1em; line-height: 1.6;'>
            <strong>DEMO MODE:</strong> Based on your question about "{question}", here's a sample response.
            <br><br>
            Transformers are a type of neural network architecture that revolutionized natural language processing.
            They use self-attention mechanisms to process sequences in parallel, making them more efficient than
            recurrent neural networks. The key innovation is the attention mechanism, which allows the model to
            weigh the importance of different parts of the input when making predictions [1][2].
        </p>
        <hr style='margin: 20px 0; border: none; border-top: 1px solid #eee;'>
        <p style='color: #7f8c8d; font-size: 0.9em;'>
            <strong>Model:</strong> llama3.2 (mock) |
            <strong>Retrieved:</strong> {k} chunks |
            <strong>Search:</strong> {search_type}
        </p>
    </div>
    """

    # Sample citations
    citations_html = """
    <div style='margin-top: 20px;'>
        <h3>📚 Sources</h3>
        <div class='citation-box'>
            <strong>[1] attention-is-all-you-need.pdf</strong> (Chunk 12)
            <p style='margin-top: 5px; font-size: 0.9em; color: #555;'>
                The Transformer architecture eschews recurrence and instead relies entirely on an attention
                mechanism to draw global dependencies between input and output...
            </p>
        </div>
        <div class='citation-box'>
            <strong>[2] bert-pretraining.pdf</strong> (Chunk 8)
            <p style='margin-top: 5px; font-size: 0.9em; color: #555;'>
                BERT uses bidirectional transformers to pre-train deep bidirectional representations
                from unlabeled text by jointly conditioning on both left and right context...
            </p>
        </div>
    </div>
    """

    return answer_html, citations_html

def mock_search_papers(query: str, k: int, search_type: str) -> str:
    """Mock search function with sample results"""
    if not query.strip():
        return "<p style='color: red;'>Please enter a search query.</p>"

    html = f"<h3>🔍 Found {k} results for '{query}' (DEMO MODE)</h3>"

    sample_results = [
        {
            "title": "Attention Is All You Need",
            "chunk": "The Transformer architecture eschews recurrence and instead relies entirely on an attention mechanism...",
            "score": 0.95
        },
        {
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "chunk": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers...",
            "score": 0.89
        },
        {
            "title": "GPT-3: Language Models are Few-Shot Learners",
            "chunk": "We demonstrate that scaling up language models greatly improves task-agnostic, few-shot performance...",
            "score": 0.82
        }
    ]

    for i, result in enumerate(sample_results[:k], 1):
        html += f"""
        <div style='background-color: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #3498db;'>
            <h4 style='margin-top: 0; color: #2c3e50;'>[{i}] {result['title']}</h4>
            <p style='color: #7f8c8d; font-size: 0.9em;'>Chunk {i*10} | Score: {result['score']:.4f}</p>
            <p style='line-height: 1.6;'>{result['chunk']}</p>
        </div>
        """

    return html

def mock_show_stats() -> str:
    """Mock statistics display"""
    html = f"""
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;'>
        <div class='stat-card'>
            <h2 style='margin: 0;'>1,234</h2>
            <p style='margin: 10px 0 0 0; opacity: 0.9;'>Total Chunks</p>
        </div>
        <div class='stat-card'>
            <h2 style='margin: 0;'>1,234</h2>
            <p style='margin: 10px 0 0 0; opacity: 0.9;'>Indexed Chunks</p>
        </div>
        <div class='stat-card'>
            <h2 style='margin: 0;'>156</h2>
            <p style='margin: 10px 0 0 0; opacity: 0.9;'>Unique Papers</p>
        </div>
    </div>

    <div style='background-color: #ecf0f1; padding: 20px; border-radius: 8px; margin-top: 20px;'>
        <h3 style='margin-top: 0;'>🔧 Service Status (DEMO MODE)</h3>
        <ul style='list-style: none; padding: 0;'>
            <li style='margin: 10px 0;'>✅ <strong>Embedding Model</strong> (Mock)</li>
            <li style='margin: 10px 0;'>✅ <strong>OpenSearch</strong> (Mock)</li>
            <li style='margin: 10px 0;'>✅ <strong>Ollama LLM</strong> (Mock)</li>
        </ul>
        <p style='color: #7f8c8d; font-size: 0.9em; margin-top: 15px;'>
            ⚠️ Running in standalone demo mode - connect to API for real data
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
with gr.Blocks(css=custom_css, theme=gr.themes.Soft(), title="ResearchAI - Demo") as demo:
    gr.Markdown("""
    # 🚀 ResearchAI: Scientific Paper Q&A (DEMO MODE)

    ⚠️ **Running in standalone demo mode** - This is a UI preview with mock data.

    To connect to real backend: Start all services with `docker-compose up -d`
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
                fn=mock_ask_question,
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
                fn=mock_search_papers,
                inputs=[search_input, search_k_slider, search_type_dropdown],
                outputs=search_output
            )

        # Tab 3: Statistics
        with gr.Tab("📊 Statistics"):
            stats_output = gr.HTML()
            refresh_button = gr.Button("Refresh Stats")

            refresh_button.click(
                fn=mock_show_stats,
                outputs=stats_output
            )

            # Load stats on tab open
            demo.load(mock_show_stats, outputs=stats_output)

    gr.Markdown("""
    ---

    **Tips:**
    - Use **hybrid search** for best results (combines keyword + semantic matching)
    - Increase **k** to get more context (but may slow down responses)
    - Adjust **temperature** for more creative (higher) or focused (lower) answers
    - Check the **Statistics** tab to see indexed paper counts

    **Built with:** FastAPI, OpenSearch, HuggingFace Transformers, Ollama

    ---

    🚀 **To connect to real data:** Run `docker-compose up -d` from project root
    """)

if __name__ == "__main__":
    print("🚀 Starting ResearchAI UI in DEMO MODE...")
    print("📍 UI will be available at: http://localhost:7860")
    print("⚠️  Using mock data - start full stack for real backend")
    print("")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        share=False
    )
