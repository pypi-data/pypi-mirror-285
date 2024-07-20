import os,sys
import json
from multillm.BaseLLM import BaseLLM
from multillm.Prompt import Prompt
import requests
from anthropic import Anthropic



# Google ANTHROPIC interface
"""
The CLAUDE class extends the BaseModel class and overrides the get_response() method, providing an implementation.
The get_response() method takes a response parameter and returns the content of the first response in the given response object.
"""
class CLAUDE(BaseLLM):
    

    #implement here
    def __init__ (self, **kwargs):

       
        # add values here directly or if kwargs are specified they are taken from the config file
        defaults  = {
            "class_name" : "CLAUDE",
            "model" : "chat-bison@001",
            "credentials" : "key.json",
           
        }
        #if kwargs:
        # super().__init__(kwargs)
        #else:
        #    super().__init__(defaults)

        
   
    # Get Text
    def get_content(self, collected_messages):
        # Combine all messages from chunks
        full_text = ''.join(collected_messages)
        #sys.stdout = sys.__stdout__
    
        """ Get the text from the response of an LLM """
        try:
            if self.is_code(full_text):
                print("{0} response: {1}" .format(self.__class__.__name__,full_text))
                return full_text, True
            else:
                #print('CLAUDE is not code')
                print("{0} response: {1}" .format(self.__class__.__name__,full_text))
                return full_text, False
        except Exception as e:
            #print("error is_code() {0}" .format(str(e)))
            return('CLAUDE response failed {}'.format(e))

    def get_response(self, prompt, taskid=None, convid=None):
        """Predict using a Large Language Model."""
        project_id = "verifai-ml-training"
        location = "us-central1"

        """ Get credentials file set in the config, and set appropriate variables for your model """
        if not os.path.exists(self.credentials):
            try:
                api_key = os.environ["ANTHROPIC_API_KEY"]
            except Exception as e:
                print('the env variable ANTHROPIC_API_KEY is not set')
                return None, False
        else:
            with open(self.credentials, "r") as f:
                api_key = f.readline().strip()

        """
         curl -X POST https://api.anthropic.com/v1/messages \
         --header "x-api-key: $ANTHROPIC_API_KEY" \
         --header "anthropic-version: 2023-06-01" \
         --header "content-type: application/json" \
        """
                
        if self.url is not None:
            url = self.url
        else:
            url = "https://api.anthropic.com/v1/messages"

        prmpt = prompt.get_string() + " , please return response in markdown format"
        if convid:
            qa = super().get_conversation_history(convid,"CLAUDE")
            for q,a in qa:
                messages.append( {"role": "user", "content" : q})
                messages.append( {"role": "assistant", "content" : a})

        messages = [] 
        messages.append( {"role": prompt.get_role(), "content" : prmpt } )
        if prompt.context:
            messages.append({"role": "assistant", "content" : prompt.get_context()})

            
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": messages,
            "stream": True
        }

        try:
            """ Call API """
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }

            #print('calling {0} with Headers {1} , payload {2}' .format(url, headers, payload))
            response = requests.post(url, data=json.dumps(payload), headers=headers, stream=True)
            
            '''
            Without streaming, the result of response.json() is like:
                {
                "id":"msg_015qTPXnkqpsEs3RVyfJZ4j7",
                "type":"message",
                "role":"assistant",
                "model":"claude-3-sonnet-20240229",
                "content":[
                    {
                        "type":"text",
                        "text":"Dig a hole, place the plant, cover with soil, water generously, and provide sunlight."
                    }
                ],
                "stop_reason":"end_turn",
                "stop_sequence":"None",
                "usage":{
                    "input_tokens":21,
                    "output_tokens":25
                }
                }
            '''
            collected_messages = []
            for chunk in response.iter_lines():
                if chunk:
                    cur = chunk.decode('utf-8')
                    '''
                    chunk.decode('utf-8') looks like:
                        event: content_block_delta
                        data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hello"}}
                    '''
                    lines = cur.strip().split("\n")
                    for line in lines:
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                if data.get("type") == "content_block_delta" and "delta" in data:
                                    chunk_message = data["delta"]["text"]
                                    self.stream_to_redis(chunk_message, taskid)
                                    print("{}" .format(chunk_message))
                                    collected_messages.append(chunk_message)
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            print(f'error calling claude: {str(e)}')


        if len(collected_messages) == 0:
            return None, None
        else: 
            content, is_code = self.get_content(collected_messages)
        if content and taskid:
            self.publish_to_redis(content, taskid)
        
        return(content), is_code
            



    def get_response_via_sdk(self, prompt: Prompt, taskid=None, convid = None):
        
        """Predict using a Large Language Model."""
        project_id = "verifai-ml-training"
        location = "us-central1"

        """ Get credentials file set in the config, and set appropriate variables for your model """
        if not os.path.exists(self.credentials):
            try:
                api_key = os.environ["ANTHROPIC_API_KEY"]
            except Exception as e:
                print('the env variable ANTHROPIC_API_KEY is not set')

        else:
            f = open(self.credentials, "r")
            api_key = f.readline()

        
        client = Anthropic(
        # This is the default and can be omitted
        #api_key=os.environ.get("ANTHROPIC_API_KEY"),
        api_key=api_key
        )

        collected_messages = []
        try:
            with client.messages.stream(
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt.get_string()
                    }
                ],
                model="claude-3-opus-20240229",
            ) as stream:
                for chunk_message in stream.text_stream:
                    collected_messages.append(chunk_message)
                    self.stream_to_redis(chunk_message, taskid)
                    print(chunk_message, end="", flush=True)
            print("\n")
        except Exception as e:
            print(f'Error calling Claude: {str(e)}')
        collected_messages = [m for m in collected_messages if m is not None]

        ''' non-streaming version:
        response = client.messages.create(
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt.get_string(),
                }
                ],
                model="claude-2.1",
        )



        resp = response.model_dump_json()
        #  {"id": "msg_01WT3NWeLfgrAY7XQTVPHLPp", "content": [{"text":
        res = json.loads(resp)
        #print('claude reponse: {0}' .format(resp))
        resp = res["content"]
        r = resp[0]
        response = r["text"]
        '''
        
        if len(collected_messages) == 0:
            return None, None
        else: 
            content, is_code = self.get_content(collected_messages)
        if content and taskid:
            self.publish_to_redis(content, taskid)
        
        return(content), is_code

