import gradio as gr
import openai
from openai import OpenAI
import os
import requests
from dotenv import load_dotenv
import asyncio
from openai import AsyncOpenAI

# Load environment variables from .env file
load_dotenv()
# Access the API key
openai_api_key = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Initialize OpenAI API client
client = openai.OpenAI(api_key=openai_api_key)
async_client = AsyncOpenAI(api_key=openai_api_key)

async def tts_itinerary(text, instructions, voice="nova"):
	from aiohttp import ClientSession

	output_path = "/tmp/itinerary.wav"

	url = "https://api.openai.com/v1/audio/speech"
	headers = {
		"Authorization": f"Bearer {openai_api_key}",
		"Content-Type": "application/json"
	}
	payload = {
		"model": "gpt-4o-mini-tts",
		"input": text,
		"voice": voice,
		"instructions": instructions,
		"response_format": "wav"
	}

	async with ClientSession() as session:
		async with session.post(url, headers=headers, json=payload) as resp:
			if resp.status != 200:
				error_text = await resp.text()
				raise Exception(f"TTS failed: {resp.status} - {error_text}")
			
			with open(output_path, "wb") as f:
				while True:
					chunk = await resp.content.read(1024)
					if not chunk:
						break
					f.write(chunk)

	return output_path


def sync_tts_wrapper(text):
	instructions = (
		"Voice: Friendly and enthusiastic, like a museum guide talking to kids. "
		"Tone: Excited, informative, curious. Delivery: Clear and fun."
	)
	return asyncio.run(tts_itinerary(text, instructions))



# ✨ Itinerary Generator Logic
def generate_itinerary(age, interests, language, expectations, learning_goals, eta, estimated_staying_time):
    print(f"language is {language}")

    system_prompt = (
        "You are an advanced AI working for MuseoGo, a platform dedicated to enhancing museum visits using AI. "
        "You will speak in the language that the current user provides to you."
        "Your main task is to create user-friendly itineraries specifically for The Franklin Institute, "
        f"Ensure that the expected number of hours for the exhibits sums to {estimated_staying_time} and does not go over that. "
        "factoring in user profiles (age, interests, learning goals, ETA, and estimated staying time). "
        "Ensure your responses are accurate, thorough, and easy to understand."
        "Be explicit about how your recommendation matches my child's interests, age, and learning goals."
        "Provide complete, detailed recommendations for exhibits and scheduling, integrating daily show times."
        # "Clearly restate the child's age, interests, learning goals."
        "You are displaying this directly to the user, don't exclaim in response to the prompt."
        "Don't use the word I and instead use second person. Directly address your users. Don't respond to me with \"Certainly\"." 
    )
    
    user_prompt = (
        f"I am planning a trip to The Franklin Institute with my child.\n\n"
        f"Child's Age: {age}\n"
        f"Interests: {interests}\n"
        f"Learning Goals: {learning_goals}\n"
        f"Arrival Time (ETA): {eta}\n"
        f"Estimated Staying Time: {estimated_staying_time}\n\n"
        f"Keep in mind my child's conditions: {expectations}\n\n"
        "Generate a personalized museum itinerary tailored to this information. "
        "Include:\n"
        "- Recommended exhibits in order, including why you chose each exhibit.\n"
        "- Time estimates for each exhibit.\n"
        "- Integration of daily show schedules.\n"
        "- Any additional tips to maximize their visit.\n\n"
        f"Please respond to me in {language} for the rest of the conversation.\n"
        "Always format your answer as:\n"
        "\"Number. Title - explanation\"\n"
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
        "- Age-appropriate (based on my child's age)\n"
        "- Friendly and engaging\n"
        "- Factually correct\n"
        "- Easy to understand\n"
        "- Related to science, exhibits, or museum topics\n"
        "Make learning fun and inspire curiosity in my child."
    )

    user_prompt = (
        f"My child, age {age}, is visiting The Franklin Institute and asks: '{question}'\n\n"
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
def search_youtube_videos(query, CHANNEL_ID="UCpAQimPOzeu_VRWRs_S4cPw"):
	"""
	Returns a list of top 3 videos from a YouTube channel based on a query.
	Each entry includes: title, video_id
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
		results.append((title, video_id))

	return results

def format_embedded_videos(video_data):
	"""
	Accepts a list of (title, video_id) and returns Markdown with embedded iframes.
	"""
	html = ""
	for title, video_id in video_data:
		html += f"""
		### 🎥 {title}
		<iframe width="100%" height="315"
			src="https://www.youtube.com/embed/{video_id}"
			title="{title}" frameborder="0"
			allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
			allowfullscreen></iframe><br>
		"""
	return html


# # 🎨 Gradio UI with Tabs
# # Custom CSS for Helvetica font and orange theme
# css = """
# @import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue:wght@400;700&display=swap');

# body, .gradio-container {
#     font-family: 'Helvetica Neue', Arial, sans-serif !important;
# }
# button {
#     background: #FF6200
# }
# button:hover {
#     background: #FF8C42;
# }
# """


def generate_itinerary_response(age, interests, arrival_time, duration, language, expectations):
    itinerary = (
        f"Museum Itinerary for {age}-year-old:\n\n"
        f"### 👶 Kid Information\n"
        f"- **Age:** {age}\n"
        f"- **Interests:** {', '.join(interests)}\n\n"
        f"### 🕒 Visit Information\n"
        f"- **Arrival Time:** {arrival_time}:00 {'AM' if arrival_time < 12 else 'PM'}\n"
        f"- **Duration:** {duration}\n"
        f"- **Language Preference:** {language}\n"
        f"- **Other Expectations:** {expectations if expectations else 'None'}\n\n"
        f"### Agenda\n"
    )
    
    # Assuming generate_itinerary returns a string
    itineraryChat = generate_itinerary(age, interests, language, expectations, "", "", "")
    
    itinerary += itineraryChat

    return itinerary



# with gr.Blocks(title="Museum Itinerary Generator", css=css, theme=gr.themes.Default(primary_hue="orange")) as demo:
#     gr.Markdown("# 🏛️ Museum Itinerary Generator")
    
#     # Kid Information Section
#     with gr.Group():
#         gr.Markdown("## 👶 Kid Information")
#         age = gr.Textbox(label="Age", placeholder="10")
#         interests = gr.CheckboxGroup(
#             label="What are the interested topics of your kids? (Select at least one)",
#             choices=["Space exploration", "Human biology", "Technology and innovation", 
#                     "Physics and mechanics", "Environmental science", "History of science"]
#         )
    
#     # Visit Information Section
#     with gr.Group():
#         gr.Markdown("## 🕒 Visit Information")
#         arrival_time = gr.Slider(
#             label="Estimated arrive time",
#             minimum=9, maximum=17, step=1, value=12,
#             info="Drag to adjust between 9:00 and 17:00"
#         )
#         duration = gr.Radio(
#             label="Duration",
#             choices=["1 hour", "2 hours", "3 hours (recommended)", "4 hours", "> 4 hours"],
#             value="3 hours (recommended)"
#         )
#         language = gr.Radio(
#             label="Language preference",
#             choices=["English", "Spanish", "French", "Chinese", "Arabic"],
#             value="English"
#         )
#         expectations = gr.Textbox(
#             label="Other expectations (Optional)",
#             placeholder="E.g., wheelchair accessibility, quiet areas...",
#             lines=3
#         )
    
#     gr.Button("Generate Itinerary", variant="primary").click(
#         fn=generate_itinerary_response,
#         inputs=[age, interests, arrival_time, duration, language, expectations],
#         outputs=gr.Markdown()
#     )

# demo.launch()

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
    

    itinerary_output = gr.Textbox(
		label="🎟️ Your Personalized Museum Itinerary",
		lines=20
	)
    audio_output = gr.Audio(label="🔊 Listen to Itinerary", type="filepath")

    with gr.Row():
        generate_btn = gr.Button("Generate Itinerary", variant="primary")
        tts_btn = gr.Button("🔊 Play Audio", visible=False)

    generate_btn.click(
            fn=generate_itinerary_response,
            inputs=[age, interests, arrival_time, duration, language, expectations],
            outputs=itinerary_output
        ).then(
            fn=lambda: gr.update(visible=True),
            outputs=tts_btn
    )

    tts_btn.click(
        fn=sync_tts_wrapper,
        inputs=[itinerary_output],
        outputs=audio_output
    )
	
    video_markdown = gr.HTML(visible=False)

    def get_videos_and_display(query):
        videos = search_youtube_videos(query)
        return gr.update(value=format_embedded_videos(videos), visible=True)

    gr.Button("🔎 Show Recommended Videos").click(
        fn=get_videos_and_display,
        inputs=[gr.Textbox(value="space", visible=False)],
        outputs=video_markdown
    )

demo.launch()
