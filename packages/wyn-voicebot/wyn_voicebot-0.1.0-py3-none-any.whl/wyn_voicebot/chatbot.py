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
