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
with gr.Blocks() as demo:
    with gr.Tabs():  # ✅ Wrap all tabs inside gr.Tabs()
        with gr.Tab("🗺️ Personalized Itinerary"):
            gr.Markdown("## 🧭 Museum Itinerary Generator")
            gr.Markdown("Fill in the details below to generate a custom visit plan for The Franklin Institute!")

            with gr.Row():
                age = gr.Number(label="Child's Age")
                eta = gr.Textbox(label="Arrival Time (e.g. 10:00 AM)")
                duration = gr.Textbox(label="Estimated Stay (e.g. 3 hours)")

            interests = gr.Textbox(lines=3, label="Interests")
            goals = gr.Textbox(lines=3, label="Learning Goals")

            generate_btn = gr.Button("Generate Itinerary")
            output = gr.Textbox(label="Suggested Itinerary", lines=10)

            generate_btn.click(fn=generate_itinerary,
                               inputs=[age, interests, goals, eta, duration],
                               outputs=output)

        with gr.Tab("🤖 Interactive Knowledge Companion"):
            gr.Markdown("## 🤖 Real-Time Q&A")

            child_age = gr.Number(label="Child's Age", value=8)
            question = gr.Textbox(label="Your Question", placeholder="Why is the sky blue?")
            ask_btn = gr.Button("Ask")
            answer_output = gr.Textbox(label="AI Answer", lines=5)

            ask_btn.click(fn=answer_question,
                          inputs=[child_age, question],
                          outputs=answer_output)
            
        with gr.Tab("🎟️ Exit Ticket Generator"):
            gr.Markdown("## 🎟️ Get Your Exit Ticket!")
            gr.Markdown("Summarize your visit and take home fun learning prompts!")

            child_age = gr.Number(label="Child's Age", value=8)
            exhibits_visited = gr.Textbox(label="Exhibits & Topics Explored", lines=3, placeholder="Space, Dinosaurs, Physics...")
            favorite_part = gr.Textbox(label="Favorite Part of the Visit", placeholder="I loved the planetarium show!")

            generate_ticket_btn = gr.Button("Generate Exit Ticket")
            exit_ticket_output = gr.Textbox(label="Your Exit Ticket", lines=10)

            gr.Markdown("### 📺 Suggested Learning Videos:")
            video_output = gr.Textbox(label="Video Recommendations", lines=8)

            generate_ticket_btn.click(fn=generate_exit_ticket,
                                    inputs=[child_age, exhibits_visited, favorite_part],
                                    outputs=[exit_ticket_output, video_output])

demo.launch(share=False)