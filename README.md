# About Project
This project consists of two separate parts: Gemini API apps, and own NLP model.
The first part of this project was created for the Gemini API competition. The idea of this part was to create Gemini API based on chatbot and other custom usable advanced and concentrated apps on specific tasks like web builder. The whole project uses Flask.

# Gemini API apps

This part of the project contains the client-side JavaScript code for interacting with the Gemini API via a Socket.IO connection. This code powers the front-end of applications built on top of the Gemini API, enabling real-time communication and dynamic content updates.

## Features

* **Real-time Chat:** Enables interactive chat experiences with the Gemini API, allowing users to send messages and receive responses in real-time.
* **Model Selection:** Provides the ability to switch between different Gemini models, allowing users to tailor their interactions to specific tasks.
* **File Uploads:** Supports uploading images and other files to the Gemini API, enabling the use of multimedia content in chat interactions.
* **Chat History Management:** Allows users to load and save chat histories, preserving their interactions for future reference.
* **Error Handling:** Implements robust error handling mechanisms to gracefully manage potential issues during communication with the Gemini API.

## Apps

### Gemini chatbot
    This app provides a basic chat interface for interacting with the Gemini API. Users can type messages and receive responses from the Gemini model.

### Gemini web builder
    This app allows users to build simple websites using the Gemini API. Users can provide text descriptions of their desired website, and the Gemini API will generate the HTML code.

# own NLP model:

Not implemented yet.


## Usage

This project part is designed to be run as a full project that is out of the box. To use it, follow these steps:

1. **Add Gemini API key:** You need an API key to use the Gemini API. You can create a key with one click in Google AI Studio. [Get an API key](https://makersuite.google.com/app/apikey).
Once gotten one add the key into your dot env file.
```dotenv
GOOGLE_API_KEY=YOUR_API_KEY
FIREBASE_CREDENTIALS='firebase.json'
TMP_PATH='app/static/tmp'
```
2. **Add Firebase:** You need a Firebase database and storage for auto-saving chats for users. Create Firebase for your project and download its secret key. [Firebase](https://firebase.google.com/).
Your Firebase secret key json keys should look like firebase firebase template.json:
```json
{
  "type": "",
  "project_id": "",
  "private_key_id": "",
  "private_key": "",
  "client_email": "",
  "client_id": "",
  "auth_uri": "",
  "token_uri": "",
  "auth_provider_x509_cert_url": "",
  "client_x509_cert_url": "",
  "universe_domain": ""
}
```
rename your secret key to firebase.json and upload it to your root project folder.

3. **Create virtual environment:** 
```bash
python3 -m venv env
```
4. **Install dependencies:** Install the required dependencies using pip.
```bash
pip install -r requirements.txt
```
5. **Run the server:** Start the Flask server to run the Gemini API applications.
```bash
flask run
```

## License
This project is licensed under the [Apache License](LICENSE).

## Contact

D-zigi - [yusufovdzigi@gmail.com](mailto:yusufovdzigi@gmail.com)