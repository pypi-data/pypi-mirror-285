from g4f.client import Client


class AI:
    def __init__(self):
        self.client = Client()
        self.message_history = []

    def get_answer(self, question: str) -> str:
        user_message = {'role': 'user', "content": question}
        self.message_history.append(user_message)
        ai_response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.message_history,
        ).choices[0].message.content
        self.message_history.append({'role': 'assistant', 'content': ai_response})
        return ai_response

