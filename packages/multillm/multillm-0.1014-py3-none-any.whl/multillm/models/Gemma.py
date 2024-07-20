# ==============================================================================
# Copyright 2023 VerifAI All Rights Reserved.
# https://www.verifai.ai
# License: 
#
# ==============================================================================
import os,sys
import json
import requests
from multillm.BaseLLM import BaseLLM
from multillm.Prompt import Prompt



# Gemma Recurrent interface
"""
This model card corresponds to the 2B instruction version of the RecurrentGemma model. You can also visit the model card of the 2B base model.

Resources and technical documentation:

Responsible Generative AI Toolkit
RecurrentGemma on Kaggle
Terms of Use: Terms

Authors: Google

"""

class GEMMA(BaseLLM):
    

    #implement here
    def __init__ (self, **kwargs):

       
        # add values here directly or if kwargs are specified they are taken from the config file
        defaults  = {
            "class_name" : "GEMMA",
            "model" : "google/recurrentgemma-2b-it",
            "credentials" : "key.json"
        }
       
        
    
    # Get Text
    def get_content(self, response):
    
        """ Get the text from the response of an LLM """
        try:
            resp = response
        except Exception as e:
            #print("error is_code() {0}" .format(str(e)))
            return('your prompt returned no response  as {}'.format(e))

        try:
            if self.is_code(resp):
                print("{0} response: {1}" .format(self.__class__.__name__,str(resp)))
                return str(resp), True
            else:
                return str(resp), False
        except Exception as e:
            #print("error is_code() {0}" .format(str(e)))
            return('{0} response failed as {1}'.format(self.model,str(e)))
        
    
    
    def get_response(self, prompt: Prompt, taskid=None, convid = None):
        
        
        """Predict using a Large Language Model."""
        project_id = "Gemma"
        location = "us-central1"
        
        if self.url is not None:
            url = self.url
        else:
            url = "http://localhost/gemma/predict"
        
        """ Get credentials file set in the config, and set appropriate variables for your model """

        try:
            """ Call API """
            
            ## See if we can invoke importToDb
            headers = {"Content-Type" :  "application/json"}
            prmpt = prompt.get_string() + " , please return response in markdown format"
            
            
            # Chec if thread of conversation exists.. 
            messages=[]
            if convid:
                qa = super().get_conversation_history(convid,"GEMMA")
                for q,a in qa:
                    messages.append( {"role": "user", "content" : q})
                    messages.append( {"role": "assistant", "content" : a})
        
            messages.append( {"role": prompt.get_role(), "content" : prmpt } )
            if prompt.context:
                messages.append({"role": "assistant", "content" : prompt.get_context()})
        
            #values = {'question':  prmpt}
            values = {'question':  messages}

      
            resp = requests.post(url, data=json.dumps(values),headers=headers)
            print("{0} Response: {1}" .format(self.model, resp.text))
            data = resp.json()
            content, is_code = self.get_content(data)
            content = content.replace(prmpt, "")
            extras = ['<eos>','<bos>','<start_of_turn>user','<start_of_turn>','<start_of_turn>model',
                      '<end_of_turn>model','<end_of_turn>','<s>', '</s>', '[INST]', '[/INST]' ]
            for extra in extras:          
                content = content.replace(extra, '')

            if content and taskid:
                self.publish_to_redis(content, taskid)
                
            return content, is_code
            
        except Exception as e:
            print('error calling {0}: {1}' .format(self.model, str(e)))
            return None, None
