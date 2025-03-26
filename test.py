import gradio as gr
import openai
from openai import OpenAI
import os
import requests
from dotenv import load_dotenv
import asyncio
from openai import AsyncOpenAI
import tempfile

# Load environment variables from .env file
load_dotenv()
# Access the API key
openai_api_key = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


client = openai.OpenAI(api_key=openai_api_key)
async_client = AsyncOpenAI(api_key=openai_api_key)


async def tts_itinerary(text, instructions, voice="nova"):
	from aiohttp import ClientSession

	# Use Gradio-safe temp file
	with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
		output_path = tmpfile.name

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
def generate_itinerary(age, interests, language, expectations,
					   learning_goals, eta, estimated_staying_time):
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
		model="gpt-3.5-turbo",
		messages=[
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": user_prompt}
		]
	)

	itinerary = response.choices[0].message.content
	audio_path = sync_tts_wrapper(itinerary)

	return itinerary, gr.update(value=audio_path, visible=True)


# ✨ Knowledge Companion Logic
def answer_question(age, question):
    system_prompt = (
        "You are an educational AI chatbot for MuseoGo, designed to answer questions from children visiting "
        "The Franklin Institute. Your answers must be:\n"
        "- Age-appropriate (based on the child's age)\n"
        "- Friendly and engaging 😊\n"
        "- Factually correct and easy to understand\n"
        "- Focused on science, exhibits, or museum topics\n"
        "- Designed to make learning fun and spark curiosity 🧠✨\n\n"
        "SAFETY GUIDELINES:\n"
        "- If the input includes hate speech, harmful content, or anything inappropriate, DO NOT answer the question.\n"
        "- Instead, respond with a kind and firm message like: 'Let's keep things friendly and fun! 😊 I'm here to help with science questions and cool stuff about the museum. If you're curious about something science-y, I'm all ears!'\n"
        "- Never repeat or acknowledge harmful content directly.\n\n"
        "Use emojis where helpful to make your responses more fun and relatable.\n"
        "Always end your answer with a simple multiple-choice question to check understanding."
    )

    user_prompt = (
        f"My child, age {age}, is visiting The Franklin Institute and asks: '{question}'\n\n"
        "Please give a clear, fun explanation that matches their age level, and connect it to any related exhibit or science concept in the museum when possible."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content





# ✨ Exit Ticket Generator Logic

def generate_exit_ticket(age, exhibits, favorite_part):
    system_prompt = (
        "You are an AI assistant creating personalized exit tickets for young visitors "
        "at The Franklin Institute. Your goal is to reinforce learning by summarizing key takeaways "
        "and providing engaging prompts for reflection. Keep the tone friendly, simple, and age-appropriate. "
        "Use fun language to celebrate learning and encourage curiosity."
    )

    user_prompt = (
        f"A {age}-year-old child visited The Franklin Institute and explored the following topics:\n"
        f"{exhibits}\n\n"
        f"Their favorite part of the visit was: {favorite_part}\n\n"
        "Create a fun, engaging exit ticket that includes:\n"
        "- A summary of what they learned (in simple language for their age).\n"
        "- A playful reflection question.\n"
        "- A suggested hands-on or creative activity they can try at home to keep learning."
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return response.choices[0].message.content

# def generate_exit_ticket(age, exhibits, favorite_part):
#     # Handle both string and list inputs for exhibits
#     if isinstance(exhibits, str):
#         exhibits_list = [ex.strip() for ex in exhibits.split(",")]
#         exhibits_str = exhibits
#     elif isinstance(exhibits, list):
#         exhibits_list = [ex.strip() for ex in exhibits]
#         exhibits_str = ", ".join(exhibits)
#     else:
#         exhibits_list = []
#         exhibits_str = str(exhibits)

    # Generate the exit ticket content
#     exit_ticket_content = f"""## What You Learned Today!

# Hey there, future scientist! Today at The Franklin Institute, you explored {exhibits_str}. 
# Here's what you might have discovered:

# - {exhibits_list[0] if len(exhibits_list) > 0 else "Science"} is all about...
# {'- ' + exhibits_list[1] + ' which shows...' if len(exhibits_list) > 1 else ''}

# ## Reflection Question
# What was the most surprising thing you learned about {favorite_part}?

# ## Keep Exploring at Home
# Try this fun activity: [simple activity related to {exhibits_list[0] if exhibits_list else 'science'}]
# """
#     return exit_ticket_content

def search_youtube_videos(query, CHANNEL_ID="UCpAQimPOzeu_VRWRs_S4cPw"):
    """
    Searches YouTube videos from The Franklin Institute channel based on a query
    and returns relevant videos with their URLs.
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

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            # url = f"https://www.youtube.com/watch?v={video_id}"
            results.append((title, video_id))

        return results
    except Exception as e:
        print(f"Error searching YouTube videos: {e}")
        return []



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


def create_exit_ticket(age, exhibits, favorite_part):
	# Generate the exit ticket content - plain text
	exit_ticket_text = generate_exit_ticket(age, exhibits, favorite_part)

	# Format the text into HTML-friendly format (replace newlines with <br>)
	formatted_text = exit_ticket_text.replace('\n', '<br>')

	# Wrap the content in a styled HTML container
	exit_ticket_html = f"""
	<div style="font-family: Arial, sans-serif; line-height: 1.6;">
		<h2>🧾 Your Personalized Exit Ticket</h2>
		<p>{formatted_text}</p>
	</div>
	"""

	# Get exhibits as a list
	exhibits_list = [
		ex.strip() for ex in
		(exhibits.split(",") if isinstance(exhibits, str) else exhibits)
	]

	# Prepare embedded video section
	video_section = """
	<div style="margin-top: 40px;">
		<h2>🎬 Recommended Videos from The Franklin Institute</h2>
	"""
	video_urls = []

	for i, exhibit in enumerate(exhibits_list[:3]):  # Limit to 3 exhibits
		videos = search_youtube_videos(exhibit)
		if videos:
			if i < 2:  # Only embed for first 2 exhibits
				video_section += f"<h3>About {exhibit}:</h3>"
				video_section += format_embedded_videos(videos[:2])
			video_urls.append(videos[0][1])  # Store first video ID

	# Pad with None if fewer than 3
	while len(video_urls) < 3:
		video_urls.append(None)

	video_section += "</div>"

	# Combine all content
	full_exit_ticket = exit_ticket_html + video_section

	return full_exit_ticket, video_urls[0], video_urls[1], video_urls[2]


## Gradio Interface
css = """
@import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue:wght@400;700&display=swap');

body, .gradio-container {
    font-family: 'Helvetica Neue', Arial, sans-serif !important;
}

}
"""

with gr.Blocks(title="Museum Experience", css=css) as demo:
    gr.Markdown("# 🏛️ Museum Experience")
    
    with gr.Tabs() as tabs:
        with gr.Tab("Itinerary Generator", id=0):
            # Kid Information Section
            with gr.Group():
                gr.Markdown("## 👶 Kid Information")
                age = gr.Number(label="Age", value=10, precision=0)
                interests = gr.CheckboxGroup(
                    label="What are the interested topics of your kids? (Select at least one)",
                    choices=["Space exploration", "Human biology", "Technology and innovation", 
                            "Physics and mechanics", "Environmental science", "History of science"]
                )
                learning_goals = gr.Textbox(
                    label="Learning Goals",
                    placeholder="What do you hope your child will learn from this visit?"
                )
            
            # Visit Information Section
            with gr.Group():
                gr.Markdown("## 🕒 Visit Information")
                eta = gr.Textbox(
                    label="Estimated arrival time",
                    placeholder="Enter time between 9:00 and 17:00",
                    value="12:00",
                )
                estimated_staying_time = gr.Radio(
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
                    
                itinerary_output = gr.Markdown()
                tts_audio_output = gr.Audio(label="🎧 Listen to Itinerary", visible=False)

                generate_btn = gr.Button("Generate Itinerary", variant="primary")
                generate_btn.click(
                    fn=generate_itinerary,
                    inputs=[age, interests, language, expectations, learning_goals, eta, estimated_staying_time],
                    outputs=[itinerary_output, tts_audio_output]
                )
            
        
        with gr.Tab("Learning Companion", id=1):
            chatbot = gr.Chatbot(
            avatar_images=(None, "museo.png"),
            show_copy_button=True,
            height="75vh",
            show_label=True,
            container=True
            )
    
        # Create the chat interface with supported parameters
            chat_interface = gr.ChatInterface(
                fn=answer_question,
                chatbot=chatbot,
                examples=[
                    "Why is the sky blue?",
                    "What is a black hole?",
                    "What makes a rainbow?"
                ],
                additional_inputs=None,
                submit_btn=True,
                fill_height=True
            )


        with gr.Tab("Exit Ticket Generator", id=2):
            gr.Markdown("# 🏛️ Franklin Institute Exit Ticket Generator")
            gr.Markdown("Create personalized exit tickets for young visitors with learning summaries and video recommendations!")
            
            exhibits = gr.CheckboxGroup(
                label="What exhibitions did you visit today? (Select at least one)",
                choices=["The Giant Heart" , "Your Brain" , "Changing Earth" , "Space Command" , "The Train Factory" , "Sir Isaac's Loft" , "SportsZone"],
                interactive=True
            )
            favorite_part = gr.Textbox(
                label="What is your favorite exhibition?",
                placeholder="E.g., Space Exploration",
                lines=3
            )
            
            generate_btn = gr.Button("Generate Exit Ticket", variant="primary")
            
            with gr.Row():
                exit_ticket_output = gr.HTML(label="Your Personalized Exit Ticket")
                video_outputs = []
                for i in range(3):
                    video_outputs.append(gr.Video(label=f"Recommended Video {i+1}", visible=False))
            
            generate_btn.click(
                fn=create_exit_ticket,
                inputs=[age, exhibits, favorite_part],
                outputs=[exit_ticket_output, *video_outputs]
            )

demo.launch()