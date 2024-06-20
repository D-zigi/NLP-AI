"""
GeminiAPI chat module
for full control and customization of the chat
"""
import os
import PIL.Image
import google.generativeai as genai

#Langchain for Gemini
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')


def list_models():
    """
    Lists all available models
    """
    models = [
        m.name.replace('models/', '') 
        for m in genai.list_models() 
        if 'generateContent' in m.supported_generation_methods
    ]
    return models

def create_chat(model_name='gemini-1.5-flash'):
    """
    cretaes a chat with the specified model
    defaults to 'gemini-1.5-flash'
    """
    model = genai.GenerativeModel(model_name)
    chat = model.start_chat(history=[])
    return chat

def get_response(chat, text, image=None):
    """
    gets a response from the chat
    """
    try:
        response = chat.send_message([text], stream=True)
        response.resolve()
        return response.text
    except Exception as e:
        print(e)
        return f"<span style='color: red;'> ERROR: Unable to get response from GeminiAPI <span>"


def console_chat(chat):
    """
    console AI chat
    for test porpuses
    """
    while True:
        text = input("Me: ")
        if text == "exit~":
            break
        print("Gemini: ", get_response(chat, text))