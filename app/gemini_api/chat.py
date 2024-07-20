"""
GeminiAPI chat module
for full control and customization of the chat
"""
import io
import base64
import PIL.Image
import google.generativeai as genai
from google.api_core import exceptions
from google.generativeai.types.generation_types import (
    BrokenResponseError,
    BlockedPromptException,
    StopCandidateException,
    IncompleteIterationError
)

error_code_map = {
    "IncompleteIterationError": 500,
    "BrokenResponseError": 500,
    "ResourceExhausted": 429,
    "TooManyRequests" : 429,
    "StopCandidateException": 422,
    "BlockedPromptException": 403
}


def list_model_names(name_filters=None):
    """
    Lists all available models names
    """
    model_names = [
        model.name.replace('models/', '')
        for model in genai.list_models()
            if 'generateContent' in model.supported_generation_methods
    ]

    def by_name(model_name):
        if name_filters:
            for name_filter in name_filters:
                if not (('-' not in name_filter and name_filter in model_name)
                    or ('-' in name_filter and name_filter.replace('-', '') not in model_name)):
                    return False
        return True

    model_names = [model_name for model_name in filter(by_name, model_names)]

    return model_names


DEFAULT_MODEL = list_model_names(['latest']).pop()


def create_chat(model_name=DEFAULT_MODEL, history=None, system_instruction=None):
    """
    cretaes a chat with the specified model
    defaults to DEFAULT_MODEL
    """
    model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
    chat = model.start_chat(history=history)
    return chat

def change_model(chat, model_name):
    """
    changes the model used by the chat
    defaults to DEFAULT_MODEL
    """
    old_model_name = chat.model.model_name.replace('models/', '')

    if model_name != old_model_name and model_name in list_model_names():
        history = chat.history
        return create_chat(model_name, history)
    return chat


def get_response(chat, text, images=None, stream=False):
    """
    gets a response from the chat
    """
    try:
        if images and len(images) > 0:
            message = [text]

            for image in images:
                image_bytes = base64.b64decode(image)
                image = PIL.Image.open(io.BytesIO(image_bytes))
                message.append(image)
        else:
            message = [text]

        response = chat.send_message(message, stream=stream)

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

        return error, chat

    except (BrokenResponseError, BlockedPromptException, StopCandidateException, IncompleteIterationError, IndexError) as e:
        print(f"Error: {e}")
        if len(chat.history) > 0:
            last_send, last_received = chat.rewind()
            print(last_send, last_received)
        error_message = "Request is unacceptable or Response was broken. Please try again."
        error_code = error_code_map[type(e).__name__]

        error = {"message": error_message, "code": error_code}

        return error, chat

    except exceptions.ServerError as e:
        print(f"Error: {e}")
        error_message = "Server error. Please try again later."
        error = {"message": error_message, "code": 500}

        return error, chat

    except exceptions.ClientError as e:
        print(f"Error: {e}")
        error_message = "Request/Response error. Please try again."
        error = {"message": error_message, "code": 400}

        return error, chat

    else:
        return response.text

def get_chat_name(chat):
    """
    invents the name of the chat
    """
    history = chat.history
    if len(history) != 0:
        message = """\
            This chat needs a name! 
            Analyze our conversation and give me your best shot of short, 
            simple but informative name. 
            In your response you should provide me with just the name of the chat without any other text.
            """

        chat_copy = create_chat(history=history)
        response = get_response(chat_copy, message)
        chat_name = response

        return chat_name
    return "blank"


# custom chats
def create_webuilder(model_name=DEFAULT_MODEL, history=None):
    """
    creates a webuilder chat
    """
    webuilder_instructions = """\
        1. In your responses include HTML code only.
        2. The code block must contain HTML, CSS, JS structure of user's request.
        3. Make the structure as complex and accurate as you can.
        4. Instead of images use emojis.
        5. No example or external links should be on the website.
        6. Must add your prefered colors for the website: body background and text colors.

        Remember: Your goal is to be as accurate and complex as possible while adhering to these instructions.  Focus on providing complete and functional HTML code blocks for the user's requests.
        IMPORTANT: If user's request will seem impossible or unfamiliar for a website, return 'EMPTY'.

        expected html message:
        <html>
            <head>
                <title>...</title>
                <style>...</style>
                <script>...</script>
            </head>
            <body>
                ...
            </body>
        </html>
    """

    webuilder_instructions = """\
    if request seems like a website:
        return From request build HTML5 website;
    else:
        return 'EMPTY'
    """

    chat = create_chat(
        model_name=model_name,
        history=history,
        system_instruction=webuilder_instructions
    )
    return chat



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
