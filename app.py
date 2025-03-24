import gradio as gr
import openai
from openai import OpenAI
import os
import requests
import urllib.parse

client = openai.OpenAI(api_key="YOUR_API_KEY")
YOUTUBE_API_KEY = "YOUR_YT_API_KEY"


# ✨ Itinerary Generator Logic
def generate_itinerary(age, interests, learning_goals, eta, estimated_staying_time):
    system_prompt = (
        "You are an advanced AI working for MuseoGo, a platform dedicated to enhancing museum visits using AI. "
        "Your main task is to create user-friendly itineraries specifically for The Franklin Institute, "
        "factoring in user profiles (age, interests, learning goals, ETA, and estimated staying time). "
        "Ensure your responses are accurate, thorough, and easy to understand. "
        "Provide complete, detailed recommendations for exhibits and scheduling, integrating daily show times."
    )
    
    user_prompt = (
        f"A visitor is planning a trip to The Franklin Institute with a child.\n\n"
        f"Child's Age: {age}\n"
        f"Interests: {interests}\n"
        f"Learning Goals: {learning_goals}\n"
        f"Arrival Time (ETA): {eta}\n"
        f"Estimated Staying Time: {estimated_staying_time}\n\n"
        "Generate a personalized museum itinerary tailored to this information. "
        "Include:\n"
        "- Recommended exhibits in order\n"
        "- Time estimates for each\n"
        "- Integration of daily show schedules\n"
        "- Any additional tips to maximize their visit."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if you're on free tier
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return response.choices[0].message.content

# ✨ Knowledge Companion Logic
def answer_question(age, question):
    system_prompt = (
        "You are an educational AI chatbot for MuseoGo, designed to answer questions from children visiting "
        "The Franklin Institute. Your answers must be:\n"
        "- Age-appropriate (based on the child's age)\n"
        "- Friendly and engaging\n"
        "- Factually correct\n"
        "- Easy to understand\n"
        "- Related to science, exhibits, or museum topics\n"
        "Make learning fun and inspire curiosity in the child."
    )

    user_prompt = (
        f"A child, age {age}, is visiting The Franklin Institute and asks: '{question}'\n\n"
        "Please respond with a clear, fun explanation suitable for their age, and reference any relevant exhibit or concept."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Or use "gpt-4" if available
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content

# ✨ Exit Ticket Generator
def generate_exit_ticket(age, exhibits, favorite_part):
    system_prompt = (
        "You are an AI assistant creating personalized exit tickets for young visitors "
        "at The Franklin Institute. Your goal is to reinforce learning by summarizing key takeaways, "
        "providing engaging prompts for reflection, and recommending follow-up educational videos "
        "ONLY from The Franklin Institute’s official YouTube channel: https://www.youtube.com/@TheFranklinInstitutePHL/videos.\n\n"
        "All video recommendations MUST be from this channel."
    )

    user_prompt = (
        f"A {age}-year-old child visited The Franklin Institute and explored the following topics:\n"
        f"{exhibits}\n\n"
        f"Their favorite part of the visit was: {favorite_part}\n\n"
        "Create a fun, engaging exit ticket that includes:\n"
        "- A summary of what they learned (simple language).\n"
        "- A fun reflection question.\n"
        "- A suggested activity to continue learning at home."
    )

    # Generate the Exit Ticket
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    )
    
    exit_ticket_text = response.choices[0].message.content
    
# ✨ Video recommendations
    # 📺 Get 3 video recommendations from The Franklin Institute's YouTube channel based on the exhibits visited
    # https://www.youtube.com/@TheFranklinInstitutePHL/videos
    # search_youtube_videos() function to be defined: YOUTUBE_API_KEY
def search_youtube_videos(query, CHANNEL_ID = "UCpAQimPOzeu_VRWRs_S4cPw"):
	"""
	Searches YouTube videos from a specific channel based on a query
	and returns the top 3 relevant videos.
	"""
	base_url = "https://www.googleapis.com/youtube/v3/search"
	params = {
		"key": YOUTUBE_API_KEY,
		"channelId": CHANNEL_ID,
		"part": "snippet",
		"q": query,
		"maxResults": 3,
		"order": "relevance",
		"type": "video"
	}

	response = requests.get(base_url, params=params)
	data = response.json()

	results = []
	for item in data.get("items", []):
		video_id = item["id"]["videoId"]
		title = item["snippet"]["title"]
		url = f"https://www.youtube.com/watch?v={video_id}"
		results.append((title, url))

	return results 


# 🎨 Gradio UI with Tabs
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