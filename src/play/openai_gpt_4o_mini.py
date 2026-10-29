from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def talk_to_student(prompt : list, role):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages = prompt
    )
    text = response.choices[0].message.content
    usage = response.usage
    finish_reason = response.choices[0].finish_reason
    print(f"{role}:", end=" ")
    print(text)
    return text, usage, finish_reason