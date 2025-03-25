import gradio as gr
import random

def random_response(message, history):
    bot_message = random.choice([
        "Yes", 
        "No", 
        "Maybe", 
        "I think so!",
        "That's an interesting question about art!",
        "Many visitors wonder about that too.",
        "Let me check the museum archives...",
        "According to our records..."
    ])
    return bot_message

# Custom CSS for full height
css = """
.gradio-container { height: 100vh !important; }
#component-0 { height: calc(100vh - 120px) !important; }
footer { visibility: hidden !important; }
h1 { text-align: center; font-family: 'Georgia', serif; }
"""

with gr.Blocks(css=css, title="Museum Learning Companion") as demo:
    gr.Markdown("# 🏛️ Museum Learning Companion")
    
    # Create the chatbot with correct parameters
    chatbot = gr.Chatbot(
        avatar_images=(None, "museo.png"),
        show_copy_button=True,
        height="80vh",
        show_label=True,
        container=True
    )
    
    # Create the chat interface with supported parameters
    chat_interface = gr.ChatInterface(
        fn=random_response,
        chatbot=chatbot,
        examples=[
            "What can you tell me about this painting?",
            "Who was the artist?",
            "What period is this from?"
        ],
        additional_inputs=None,
        submit_btn="Send",
        fill_height=True
    )

demo.launch()