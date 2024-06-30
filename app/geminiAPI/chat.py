"""
GeminiAPI chat module
for full control and customization of the chat
"""
import os
import io
import base64
import PIL.Image
import google.generativeai as genai
from google.api_core import exceptions
from google.generativeai.types.generation_types import BrokenResponseError, BlockedPromptException, StopCandidateException, IncompleteIterationError

from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

error_code_map = {
    "BrokenResponseError": 500,
    "BlockedPromptException": 403,
    "StopCandidateException": 422,
    "IncompleteIterationError": 500,
    "ResourceExhausted": 429,
    "TooManyRequests" : 429
}


def list_model_names(name_filter=''):
    """
    Lists all available models names
    """
    model_names = [
        m.name.replace('models/', '')
        for m in genai.list_models()
        if 'generateContent' in m.supported_generation_methods
        and name_filter in m.name
    ]
    return model_names

DEFAULT_MODEL = list_model_names('latest').pop()

def create_chat(model_name=DEFAULT_MODEL, history=None):
    """
    cretaes a chat with the specified model
    defaults to DEFAULT_MODEL
    """
    model = genai.GenerativeModel(model_name)
    chat = model.start_chat(history=history)
    return chat

def change_model(chat, model_name):
    """
    changes the model used by the chat
    defaults to DEFAULT_MODEL
    """
    if model_name in list_model_names() and model_name != DEFAULT_MODEL:
        history = chat.history
        return create_chat(model_name, history)
    return chat


def get_response(chat, text, image=None, stream=False):
    """
    gets a response from the chat
    """
    try:
        if image:
            image_bytes = base64.b64decode(image)
            image_ready = io.BytesIO(image_bytes)
            image = PIL.Image.open(image_ready)
            message = [text, image]
        else:
            message = [text]

        response = chat.send_message(message, stream=stream)
        response.resolve()
    except exceptions.InvalidArgument as e:
        print(f"Error: {e}")
        error_message = str(e)[3:]
        error = {"message": error_message, "code": 400}
        return error, chat

    except (exceptions.ResourceExhausted, exceptions.TooManyRequests) as e:
        print(f"Error: {e}")
        error_message = "Too many or too fast requests. Please slow down and try again later"
        error_code = error_code_map[type(e).__name__]
        error = {"message": error_message, "code": error_code}
        print(error)

        return error, chat

    except (BrokenResponseError, BlockedPromptException, StopCandidateException, IncompleteIterationError) as e:
        print(f"Error: {e}")
        last_send, last_received = chat.rewind()
        print(last_send, last_received)
        error_message = "Request is unacceptable or Response was broken. Please try again."
        error_code = error_code_map[type(e).__name__]

        error = {"message": error_message, "code": error_code}
        print(error)

        return error, chat

    except exceptions.ServerError as e:
        print(f"Error: {e}")
        error_message = "Server error. Please try again later."
        error = {"message": error_message, "code": 500}
        return error, chat

    except exceptions.ClientError as e:
        print(f"Error: {e}")
        print(type(e).__name__)
        error_message = "Request/Response error. Please try again."
        error = {"message": error_message, "code": 400}
        return error, chat

    else:
        return response.text

def get_chat_name(chat):
    """
    invents the name of the chat
    """
    if len(chat.history) != 0:
        message = """\
            This chat needs a name! 
            Analyze our conversation and give me your best shot of short, 
            simple but informative name. 
            In your response you should provide me with just the name of the chat without any other text.
            """

        chat_name = get_response(chat, message)
        chat.rewind()
        return chat_name
    return "blank"



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
