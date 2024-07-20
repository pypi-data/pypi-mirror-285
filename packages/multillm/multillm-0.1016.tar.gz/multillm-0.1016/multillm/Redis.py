# ==============================================================================
# Copyright 2023 VerifAI All Rights Reserved.
# https://www.verifai.ai
# License: 
#
# ==============================================================================

import redis
import json
import os

if os.getenv("REDIS_URI"):
    REDIS_URI = os.getenv("REDIS_URI")
else:
    REDIS_URI = "redis://localhost:6379"
    
class Redis:
    connection = None
    def __new__(cls, redis_uri=REDIS_URI):
        if cls.connection is None:
            cls.connection = redis.Redis.from_url(redis_uri)
        return cls.connection
    
    def get_connection(self):
        return Redis.connection
    
    @staticmethod
    def publish_to_redis(type="multillm", taskid=None, result=None, meta_data=None):
        redis_conn = Redis.connection
        if redis_conn == None:
            return
        res = {"type": type, "taskId": taskid, "result" : result, "meta_data": meta_data }
        payload = json.dumps(res)
        '''Payload looks like:

        For LLM payload:
        {
            "type":"multillm",
            "taskId":"4546",
            "result":"    To learn skating:\n\n1. Start..e.",
            "meta_data":{
                "type":"response",
                "model_name":"MISTRAL"
            }
        }

        For Ranking payload:
        {
            "type":"multillm",
            "taskId":"4546",
            "result":{
                "PHI3":{
                    "accuracy_score":"8",
                    "completeness_score":"7",
                    "accuracy_exp":"The response provides accurate information on learning skating through practicing balance, glides, crossovers, and seeking professional guidance.",
                    "completeness_exp":"The response covers the essential steps of learning skating, including basic glides, progress to crossovers, and seeking professional guidance for technique improvement.",
                    "avg_score":7.5
                },
                "GPT":{
                    "accuracy_score":"7",
                    "completeness_score":"6",
                    "accuracy_exp":"The response accurately mentions starting with balance training, practicing gliding, stopping, and considering lessons from a professional trainer.",
                    "completeness_exp":"The response misses some details like progressing to crossovers and lacks completeness compared to a comprehensive guide.",
                    "avg_score":6.5
                },
                "MISTRAL":{
                    "accuracy_score":"9",
                    "completeness_score":"9",
                    "accuracy_exp":"The response covers all the essential steps accurately, including starting with skates, building balance, learning basic movements, seeking professional guidance, and wearing protective gear.",
                    "completeness_exp":"The response provides a comprehensive guide, mentioning all the necessary steps clearly for learning skating.",
                    "avg_score":9.0
                }
            },
            "meta_data":{
                "type":"ranking"
            }
        }
        
        '''
        try:
            redis_conn.publish(type, payload)
        except Exception as e:
            print('(MultiLLM:publish_to_redis()) could not publish to redis: {0}' .format(str(e)))

    @staticmethod
    def stream_to_redis(type="multillmStream", taskid=None, text_chunk=None, meta_data=None):
        redis_conn = Redis.connection
        if redis_conn == None:
            return
        chunk = {"type": type, "taskId": taskid, "text_chunk" : text_chunk, "meta_data": meta_data }
        chunk_payload = json.dumps(chunk)
        try:
            redis_conn.publish(type, chunk_payload)
        except Exception as e:
            print('(MultiLLM:publish_to_redis()) could not publish to redis: {0}' .format(str(e)))          

redis_instance = Redis()
