import gradio as gr
def hello(q): return "ResearchAI UI is up ✅"
demo = gr.Interface(hello, inputs="text", outputs="text", title="ResearchAI")
demo.launch(server_name="0.0.0.0", server_port=7860, show_error=True)
