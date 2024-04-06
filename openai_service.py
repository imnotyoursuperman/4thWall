import openai

class OpenAIService:
    def __init__(self, api_key):
        openai.api_key = api_key

    def correct_text(self, text):
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=text,
            max_tokens=50
        )
        corrected_text = response['choices'][0]['text'].strip()
        return corrected_text

