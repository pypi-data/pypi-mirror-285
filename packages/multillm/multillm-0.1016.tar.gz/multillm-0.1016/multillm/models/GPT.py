import os,sys
import openai
import json
from multillm.BaseLLM import BaseLLM
from multillm.Prompt import Prompt


# Openai gpt interface
"""
The GPT class extends the BaseModel class and overrides the get_response() method, providing an implementation.
The get_response() method takes a response parameter and returns the content of the first response in the given response object.
"""
class GPT(BaseLLM):
    

    #implement here
    def __init__ (self, **kwargs):

       
        # add values here directly or if kwargs are specified they are taken from the config file
        defaults  = {
            "class_name" : "GPT",
            "model" : "gpt-3.5-turbo",
            "credentials" : "key.json"
        }
        #if kwargs:
        # super().__init__(kwargs)
        #else:
        #    super().__init__(defaults)

        
    
    # Get Text
    def get_content(self, collected_messages):
    
        """
        Get the text from the collected stream of chunks
        """  
        # Combine all messages from chunks
        full_text = ''.join(collected_messages)
        
        try:
            if self.is_code(full_text):
                print('{0} response {1}' .format(self.__class__.__name__, full_text))
                return full_text, True
            else:
                #print('GPT is not code')
                return full_text, False
        except Exception as e:
            #print("error is_code() {0}" .format(str(e)))
            return('GPT response failed as {}'.format(e))
    
    def get_response(self, prompt, taskid=None, convid = None):
        # setup prompt for API call
        messages=[]
        if convid:
            qa = super().get_conversation_history(convid,"GPT")
            for q,a in qa:
                messages.append( {"role": "user", "content" : q})
                messages.append( {"role": "assistant", "content" : a})
        
        messages.append( {"role": prompt.get_role(), "content" : prompt.get_string()})
        if prompt.context:
            messages.append({"role": prompt.get_role(), "content" : prompt.get_context()})
        
        # Setup Credentials
        
        """ or seet an Env Variable to be more secure
        self.credentials = os.getenv('OPENAI_APPLICATION_CREDENTIALS')
        """
    
        if not os.path.exists(self.credentials):
            print('error (multi_llm): could not find openai_credentials: {0}' .format(self.credentials))
            return 
        

        # Open the file for reading
        try:
            with open(self.credentials, 'r') as file:
                # Load the JSON data from the file
                data = json.load(file)
                openai.organization = data['organization']
                openai.api_key = data['api_key'] 

        except Exception as e:
            print('(multi_llm) error: could not load credentials {0} : {1}' .format(self.credentials,str(e)))
            return
                    
        # print('model {0}' .format(self.model))
        try:
            response = openai.chat.completions.create(
                model = self.model,
                messages=messages,
                stream=True
            )           
        except Exception as e:
            print("Couldn't fetch response from GPT")
            print(f"Exception caught is: {e}")
            response = None
    
        collected_messages = []
        for chunk in response:
            if chunk.choices[0].delta and chunk.choices[0].delta.content:
                    chunk_message = chunk.choices[0].delta.content
                    collected_messages.append(chunk_message)
                    self.stream_to_redis(chunk_message, taskid)
                    print(chunk_message or "", end="", flush=True)

        collected_messages = [m for m in collected_messages if m is not None]
        
        if not response:
            return None, None
        else: 
            content, is_code = self.get_content(collected_messages)
            if content and taskid:
                self.publish_to_redis(content, taskid)
            return (content), is_code