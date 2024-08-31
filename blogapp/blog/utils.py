import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def get_chatgpt_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

def get_chatgpt_summary(content):
    summary_prompt = f"Summarize the following content in  one SHORT sentence MAX 25 WORDS: {content}.Let it be an interesting and intriguing sentence.Write down what the reader will gain from reading this content and what the content promises."
    return get_chatgpt_response(summary_prompt)