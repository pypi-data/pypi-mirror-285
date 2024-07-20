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



# microsoft/Phi-3-mini-128k-instruct"
"""
The Phi-3-Mini-128K-Instruct is a 3.8B parameters, lightweight, state-of-the-art open model trained with the Phi-3 datasets that includes both synthetic data
and the filtered publicly available websites data with a focus on high-quality and reasoning dense properties. 
The model belongs to the Phi-3 family with the Mini version in two variants 4K and 128K which is the context length 
(in tokens) that it can support.

The model has underwent a post-training process that incorporates both supervised fine-tuning and direct preference optimization for the
 instruction following and safety measures. When assessed against benchmarks testing common sense, language understanding, 
math, code, long context and logical reasoning, Phi-3 Mini-4K-Instruct showcased a robust and state-of-the-art 
performance among models with less than 13 billion parameters.

Resources and Technical Documentation:

Phi-3 Microsoft Blog
Phi-3 Technical Report
Phi-3 on Azure AI Studio
Phi-3 ONNX: 128K
"""

class PHI3(BaseLLM):
    

    #implement here
    def __init__ (self, **kwargs):

       
        # add values here directly or if kwargs are specified they are taken from the config file
        defaults  = {
            "class_name" : "PHI3",
            "model" : "microsoft/Phi-3-mini-128k-instruct",
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
            return('{0} response failed as {1}'.format(self.model, str(e)))
        
    
    
    def get_response(self, prompt: Prompt, taskid=None, convid = None):
        
        
        """Predict using a Large Language Model."""
        project_id = "phi3"
        location = "us-central1"
        
        if self.url is not None:
            url = self.url
        else:
            url = "http://localhost/phi3/predict"
        
        """ Get credentials file set in the config, and set appropriate variables for your model """

        try:
            """ Call API """
            
            ## See if we can invoke importToDb
            headers = {"Content-Type" :  "application/json"}
            prmpt = prompt.get_string() + " , please return response in markdown format"
            
            
            # Chec if thread of conversation exists.. 
            messages=[]
            if convid:
                qa = super().get_conversation_history(convid,"PHI3")
                for q,a in qa:
                    messages.append( {"role": "user", "content" : q})
                    messages.append( {"role": "assistant", "content" : a})
        
            messages.append( {"role": prompt.get_role(), "content" : prmpt } )
            if prompt.context:
                messages.append({"role": prompt.get_role(), "content" : prompt.get_context()})
        
            #values = {'question':  prmpt}
            values = {'question':  messages}

      
            resp = requests.post(url, data=json.dumps(values),headers=headers)
            print("{0} Response: {1}" .format(self.model, resp.text))
            data = resp.json()
            content, is_code = self.get_content(data)
            content = content.replace(prmpt, "")
            """ 
            extras = ['<eos>','<bos>','<start_of_turn>user','<start_of_turn>','<end_of_turn>user',
            '<start_of_turn>model','<end_of_turn>model','<end_of_turn>','<s>', '</s>', '[INST]', '[/INST]' ]
            for extra in extras:          
                content = content.replace(extra, '')
            """

            if content and taskid:
                self.publish_to_redis(content, taskid)
                
            return content, is_code
            
        except Exception as e:
            print('error calling {0}: {1}' .format(self.model, str(e)))
            return None, None
