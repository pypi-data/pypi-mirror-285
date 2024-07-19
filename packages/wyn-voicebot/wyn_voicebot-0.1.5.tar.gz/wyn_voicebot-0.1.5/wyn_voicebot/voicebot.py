import time
from base64 import b64decode
from IPython.display import Javascript, Audio, display
from google.colab import output

import openai

class ChatBot:
    """
    A class to interact with OpenAI's GPT models for generating responses based on user input.

    Attributes:
    -----------
    client : OpenAI
        An instance of OpenAI initialized with the provided API key.
    history : list
        A list to maintain the conversation history.

    Methods:
    --------
    generate_response(prompt: str) -> str:
        Generates a response from the chatbot based on the user prompt.
    get_history() -> list:
        Returns the conversation history.
    """
    def __init__(self, api_key: str):
        """
        Initializes the ChatBot with the provided OpenAI API key.

        Parameters:
        -----------
        api_key : str
            The API key to authenticate with OpenAI.
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.history = [{"role": "system", "content": "You are a helpful assistant."}]

    def generate_response(self, prompt: str) -> str:
        """
        Generates a response from the chatbot based on the user prompt.

        Parameters:
        -----------
        prompt : str
            The user's prompt to which the chatbot responds.

        Returns:
        --------
        str
            The chatbot's response.
        """
        self.history.append({"role": "user", "content": prompt})

        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",  # NOTE: feel free to change it to gpt-4, or gpt-4o
            messages=self.history
        )

        response = completion.choices[0].message.content
        self.history.append({"role": "assistant", "content": response})

        return response

    def get_history(self) -> list:
        """
        Returns the conversation history.

        Returns:
        --------
        list
            The conversation history.
        """
        return self.history



RECORD = """
const sleep  = time => new Promise(resolve => setTimeout(resolve, time))
const b2text = blob => new Promise(resolve => {
    const reader = new FileReader()
    reader.onloadend = e => resolve(e.srcElement.result)
    reader.readAsDataURL(blob)
})

var record = time => new Promise(async resolve => {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    recorder = new MediaRecorder(stream)
    chunks = []
    recorder.ondataavailable = e => chunks.push(e.data)
    recorder.start()
    await sleep(time)
    recorder.onstop = async ()=>{
        blob = new Blob(chunks)
        text = await b2text(blob)
        resolve(text)
    }
    recorder.stop()
})
"""

class AudioProcessor:
    """
    A class to record audio, save it, interact with ChatBot, and play the response.

    Attributes:
    -----------
    chatbot : ChatBot
        An instance of the ChatBot class to generate responses.
    
    Methods:
    --------
    record_audio(sec: int = 3) -> str:
        Records audio for the specified duration and saves it as 'audio.wav'.
    process_audio_and_generate_response() -> None:
        Records audio, gets the transcript, generates a response, and saves the response as an mp3 file.
    play_audio(file_path: str) -> None:
        Plays the audio file specified by the file path.
    """
    def __init__(self, api_key: str):
        """
        Initializes the AudioProcessor with the provided OpenAI API key.

        Parameters:
        -----------
        api_key : str
            The API key to authenticate with OpenAI.
        """
        self.chatbot = ChatBot(api_key=api_key)

    def record_audio(self, sec: int = 3) -> str:
        """
        Records audio for the specified duration and saves it as 'audio.wav'.

        Parameters:
        -----------
        sec : int, optional
            The duration in seconds for which to record audio (default is 3).

        Returns:
        --------
        str
            The file name of the saved audio.
        """
        print("Recording audio...")
        display(Javascript(RECORD))
        s = output.eval_js('record(%d)' % (sec * 1000))
        b = b64decode(s.split(',')[1])
        with open('audio.wav', 'wb') as f:
            f.write(b)
        print("Audio saved!")
        return 'audio.wav'

    def process_audio_and_generate_response(self) -> None:
        """
        Records audio, gets the transcript, generates a response, and saves the response as an mp3 file.
        """
        audio_file = self.record_audio()

        # Transcribe audio
        print(f"Transcribing audio from: {audio_file}")
        audio_file = open(audio_file, "rb")
        transcript = self.chatbot.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

        print(transcript.text)

        # Generate response
        bot_answer = self.chatbot.generate_response(transcript.text)
        print(bot_answer)

        # Generate speech response
        response = self.chatbot.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=bot_answer
        )

        speech_file_path = "output.mp3"
        response.write_to_file(speech_file_path)

        # Play response audio
        self.play_audio(speech_file_path)

    def play_audio(self, file_path: str) -> None:
        """
        Plays the audio file specified by the file path.

        Parameters:
        -----------
        file_path : str
            The path to the audio file to be played.
        """
        audio = Audio(file_path, autoplay=True)
        display(audio)
