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
            

