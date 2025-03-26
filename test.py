import gradio as gr
import openai
from openai import OpenAI
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Access the API key
openai_api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=openai_api_key)
YOUTUBE_API_KEY = "YOUR_YT_API_KEY"




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
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content





# ✨ Exit Ticket Generator Logic
def generate_exit_ticket(age, exhibits, favorite_part):
    # Handle both string and list inputs for exhibits
    if isinstance(exhibits, str):
        exhibits_list = [ex.strip() for ex in exhibits.split(",")]
        exhibits_str = exhibits
    elif isinstance(exhibits, list):
        exhibits_list = [ex.strip() for ex in exhibits]
        exhibits_str = ", ".join(exhibits)
    else:
        exhibits_list = []
        exhibits_str = str(exhibits)

    # Generate the exit ticket content
    exit_ticket_content = f"""## What You Learned Today!

Hey there, future scientist! Today at The Franklin Institute, you explored {exhibits_str}. 
Here's what you might have discovered:

- {exhibits_list[0] if len(exhibits_list) > 0 else "Science"} is all about...
{'- ' + exhibits_list[1] + ' which shows...' if len(exhibits_list) > 1 else ''}

## Reflection Question
What was the most surprising thing you learned about {favorite_part}?

## Keep Exploring at Home
Try this fun activity: [simple activity related to {exhibits_list[0] if exhibits_list else 'science'}]
"""
    return exit_ticket_content

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
            url = f"https://www.youtube.com/watch?v={video_id}"
            results.append((title, url))

        return results
    except Exception as e:
        print(f"Error searching YouTube videos: {e}")
        return []

def create_exit_ticket(age, exhibits, favorite_part):
    # Generate the exit ticket content - pass exhibits as-is
    exit_ticket = generate_exit_ticket(age, exhibits, favorite_part)
    
    # Get exhibits as a list (handles both string and list inputs)
    exhibits_list = [ex.strip() for ex in (exhibits.split(",") if isinstance(exhibits, str) else exhibits)]
    
    # Video recommendations
    video_recommendations = "\n\n## Recommended Videos from The Franklin Institute\n"
    video_urls = []
    
    for i, exhibit in enumerate(exhibits_list[:3]):  # Limit to 3 exhibits
        videos = search_youtube_videos(exhibit)
        if videos:
            if i < 2:  # Only include in markdown for first 2 exhibits
                video_recommendations += f"\n### About {exhibit}:\n"
                for j, (title, url) in enumerate(videos[:2], 1):  # Limit to 2 videos per exhibit
                    video_recommendations += f"{j}. [{title}]({url})\n"
            video_urls.append(videos[0][1])  # Take first video URL
    
    # Pad with None if we don't have enough videos
    while len(video_urls) < 3:
        video_urls.append(None)
    
    # Combine the content
    full_exit_ticket = exit_ticket + video_recommendations
    
    return full_exit_ticket, video_urls[0], video_urls[1], video_urls[2]


### Gradio Interface
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
                generate_btn = gr.Button("Generate Itinerary", variant="primary")
                generate_btn.click(
                    fn=generate_itinerary,
                    inputs=[age, interests, language, expectations, learning_goals, eta, estimated_staying_time],
                    outputs=itinerary_output
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
                    "What can you tell me about this painting?",
                    "Who was the artist?",
                    "What period is this from?"
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
                exit_ticket_output = gr.Markdown(label="Your Personalized Exit Ticket")
                video_outputs = []
                for i in range(3):
                    video_outputs.append(gr.Video(label=f"Recommended Video {i+1}", visible=False))
            
            generate_btn.click(
                fn=create_exit_ticket,
                inputs=[age, exhibits, favorite_part],
                outputs=[exit_ticket_output, *video_outputs]
            )

demo.launch()