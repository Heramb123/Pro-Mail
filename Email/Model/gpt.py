import os
import openai

openai.api_key="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"


def api(content):

    while True:
        completion=openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"system","content":content}]
    )

        chat_response=str(completion.choices[0].message.content)
        chat_response=chat_response.replace('\n','')
        
        
        #chat_response = completion.choices[0].message.replace('\n', ' ')
        #chat_response = completion.choices[0].text.replace('\n', ' ')
        return chat_response
            

