import os,sys
import json
from multillm.BaseLLM import BaseLLM
from multillm.Prompt import Prompt
import requests

""" Google vertexai imports """
import vertexai
from vertexai.preview.language_models import TextGenerationModel
from vertexai.preview.language_models import ChatModel, InputOutputTextPair
from vertexai.preview.generative_models import GenerativeModel, ChatSession


# Google GEMINI interface
"""
The GEMINI class extends the BaseModel class and overrides the get_response() method, providing an implementation.
The get_response() method takes a response parameter and returns the content of the first response in the given response object.
"""


# TODO(developer): Update and un-comment below lines
# project_id = "PROJECT_ID"
"""
location = "us-central1"
vertexai.init(project=project_id, location=location)

model = GenerativeModel("gemini-pro")
chat = model.start_chat()

def get_chat_response(chat: ChatSession, prompt: str) -&gt; str:
    response = chat.send_message(prompt)
    return response.text

prompt = "Hello."
print(get_chat_response(chat, prompt))

prompt = "What are all the colors in a rainbow?"
print(get_chat_response(chat, prompt))

prompt = "Why does it appear when it rains?"
print(get_chat_response(chat, prompt))
""" 

class GEMINI(BaseLLM):
    

    #implement here
    def __init__ (self, **kwargs):

       
        # add values here directly or if kwargs are specified they are taken from the config file
        defaults  = {
            "class_name" : "GEMINI",
            "model" : "chat-bison@001",
            "credentials" : "key.json"
        }
        #if kwargs:
        # super().__init__(kwargs)
        #else:
        #    super().__init__(defaults)

        
    
    # Get Text
    def get_content(self, response):

        #sys.stdout = sys.__stdout__
    
        """ Get the text from the response of an LLM """
        try:
            if self.is_code(str(response)):
                #print("{0} response: {1}" .format(self.__class__.__name__,str(response)))
                return str(response), True
            else:
                #print('GEMINI is not code')
                #print("{0} response: {1}" .format(self.__class__.__name__,str(response)))
                return str(response), False
        except Exception as e:
            #print("error is_code() {0}" .format(str(e)))
            return('GEMINI response failed {}'.format(e))


    


    def get_response(self, prompt: Prompt, taskid=None, convid = None):
        
        
        """Predict using a Large Language Model."""
        project_id = "verifai-ml-training"
        location = "us-central1"
        
        
        """ Get credentials file set in the config, and set appropriate variables for your model """
        if not os.path.exists(self.credentials):
            print("({0}) error:  credential file doesn't exist" .format(self.__class__.__name__))
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials

        vertexai.init(project=project_id, location=location)
        print('model {0}' .format(self.model))

        model = GenerativeModel("gemini-pro")
        chat_model = model.start_chat()

   
        
        parameters = {
             "max_output_tokens" :  1024,
             "top_p" :  0.8,
             "top_k" :  40,
            "temperature" : 0.2
        }

        """ If context file exists, use it """
        context = ""
        if prompt.context:
            context = prompt.get_context()

        response = None
        try:
            """ Call API """
            response=chat_model.send_message( prompt.get_string())
            
        except Exception as e:
            print('error calling GEMINI: {0}' .format(str(e)))

        if not response:
            return None, None
        else: 
            response = response.text 
            content, is_code = self.get_content(response)
            if content and taskid:
                self.publish_to_redis(content, taskid)
            return(content), is_code

