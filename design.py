import gradio as gr

# Custom CSS for Helvetica font and orange theme
css = """
@import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue:wght@400;700&display=swap');

body, .gradio-container {
    font-family: 'Helvetica Neue', Arial, sans-serif !important;
}
button {
    background: #FF6200
}
button:hover {
    background: #FF8C42;
}
"""


def generate_itinerary(age, interests, arrival_time, duration, language, expectations):
    itinerary = f"""
    **Museum Itinerary for {age}-year-old:**

    ### 👶 Kid Information
    - **Age:** {age}
    - **Interests:** {", ".join(interests)}

    ### 🕒 Visit Information
    - **Arrival Time:** {arrival_time}:00 {'AM' if arrival_time < 12 else 'PM'}
    - **Duration:** {duration}
    - **Language Preference:** {language}
    - **Other Expectations:** {expectations if expectations else "None"}
    """
    return itinerary


with gr.Blocks(title="Museum Itinerary Generator", css=css, theme=gr.themes.Default(primary_hue="orange")) as demo:
    gr.Markdown("# 🏛️ Museum Itinerary Generator")
    
    # Kid Information Section
    with gr.Group():
        gr.Markdown("## 👶 Kid Information")
        age = gr.Textbox(label="Age", placeholder="10")
        interests = gr.CheckboxGroup(
            label="What are the interested topics of your kids? (Select at least one)",
            choices=["Space exploration", "Human biology", "Technology and innovation", 
                    "Physics and mechanics", "Environmental science", "History of science"]
        )
    
    # Visit Information Section
    with gr.Group():
        gr.Markdown("## 🕒 Visit Information")
        arrival_time = gr.Slider(
            label="Estimated arrive time",
            minimum=9, maximum=17, step=1, value=12,
            info="Drag to adjust between 9:00 and 17:00"
        )
        duration = gr.Radio(
            label="Duration",
            choices=["1 hour", "2 hours", "3 hours (recommended)", "4 hours", "> 4 hours"],
            value="3 hours (recommended)"
        )
        language = gr.Radio(
            label="Language preference",
            choices=["English", "Spanish", "French", "Chinese", "Arabic"],
            value="English"
        )
        expectations = gr.Textbox(
            label="Other expectations (Optional)",
            placeholder="E.g., wheelchair accessibility, quiet areas...",
            lines=3
        )
    
    gr.Button("Generate Itinerary", variant="primary").click(
        fn=generate_itinerary,
        inputs=[age, interests, arrival_time, duration, language, expectations],
        outputs=gr.Markdown()
    )

demo.launch()




