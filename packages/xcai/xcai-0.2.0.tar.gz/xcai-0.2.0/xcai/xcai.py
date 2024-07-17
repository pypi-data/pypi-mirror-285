import json
import requests


class maas:
    def __init__(self, url):
        self.__split_mark = "\r\n" 
        self.url = url
        self.headers = {
            'Content-Type': 'application/json'
            }
        self.messages = self.init_message()
        self.answer = ""
        self.model_choice = ""
        self.content_code = 200

    def init_message(self):
        m = [{"role": "user", "content": "你好"},
             {"role": "assistant", "content":"你好,有什么可以帮到你"}]
        return m

    def add_account(self,appid,appkey):
        self.appid=appid
        self.appkey=appkey
        self.update_headers()

    def update_headers(self):
        self.headers["appid"] = self.appid
        self.headers["api-key"] = self.appkey

    def add_message(self,message):
        self.messages.append({"role": "user", "content": message})
    
    def data_response(self, kwargs):
        data = {
            "messages":self.messages,
            "file":kwargs["file"] if "file" in kwargs else "",
            "model":kwargs["model"] if "model" in kwargs else "",
            "with_search_enhance":kwargs["with_search"] if "with_search" in kwargs else False,
            "temperature":kwargs["temperature"] if "temperature" in kwargs else None,
            "top_p":kwargs["top_p"] if "top_p" in kwargs else None,
            "with_rag":kwargs["with_rag"] if "with_rag" in kwargs else False,
            "model_variant":kwargs["model_variant"] if "model_variant" in kwargs else False,
            "embedding":False
        }
        return data
    
    def predict(self, **kwargs):
        data = self.data_response(kwargs)
        response = requests.post(self.url, headers=self.headers, data=json.dumps(data), stream=True)
        self.update_model_choice(response.headers.get('model'))

        for answer in self.return_json(response):
            print(answer, end="", flush=True)
            
        print("\n")

    def predict_yield(self, **kwargs):
        data = self.data_response(kwargs)

        response = requests.post(self.url, headers=self.headers, data=json.dumps(data), stream=True)
        self.update_model_choice(response.headers.get('model'))

        for answer in self.return_json(response):
            yield answer
    
    def embedding(self, **kwargs):
        data = self.data_response(kwargs)
        data["embedding"] = True

        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
        self.update_model_choice(response.headers.get('model'))

        answer = []
        for answer_ in self.return_json_emb(response):
            answer = answer_
        
        return answer

    def update_model_choice(self, input):
        if input is None:
            pass
        else:
            self.model_choice = input

    def get_model_choice(self):
        return self.model_choice

    def get_answer(self):
        return self.answer
    
    def update_content_code(self, buffer_json):
        if "code" in buffer_json:
            self.content_code = buffer_json["code"]
        else:
            pass

    def return_json(self, response):
        partial_message = ""
        buffer = ""

        for chunk in response:
            # print(chunk)
            if chunk:
                line = chunk.decode('utf-8')
                buffer += line
                if self.is_valid_json(buffer):
                    buffer_json = json.loads(buffer)
                    decoded_line_ = buffer_json["content"]
                    self.update_content_code(buffer_json)
                    partial_message = partial_message + decoded_line_
                    yield decoded_line_
                    buffer = ""
                else:
                    try:
                        # normal
                        if self.__split_mark in buffer:
                            content_split = buffer.split(self.__split_mark)
                            # 尝试解析缓冲区中的 JSON 数据
                            starti = 0
                            endi = len(content_split)
                            for content_i in content_split:
                                starti += 1

                                if content_i == "":
                                    buffer = ""
                                    continue
                                
                                if starti < endi:
                                    buffer_json = json.loads(content_i)
                                    decoded_line_ = buffer_json["content"]
                                    self.update_content_code(buffer_json)
                                    partial_message = partial_message + decoded_line_
                                    yield decoded_line_
                                    buffer = ""
                                elif starti == endi:
                                    if self.is_valid_json(content_i):
                                        buffer_json = json.loads(content_i)
                                        decoded_line_ = buffer_json["content"]
                                        self.update_content_code(buffer_json)
                                        partial_message = partial_message + decoded_line_
                                        yield decoded_line_
                                        buffer = ""
                                    else:
                                        buffer = content_i
                        else:
                            continue
                    except:
                        # special
                        print(chunk)
                        pass

        self.messages.append({"role": "assistant", "content": partial_message})
        self.answer = partial_message
    
    def return_json_emb(self, response):
        partial_message = []
        buffer = ""

        for chunk in response:
            # print(chunk)
            if chunk:
                line = chunk.decode('utf-8')
                buffer += line
                if self.is_valid_json(buffer):
                    buffer_json = json.loads(buffer)
                    partial_message = buffer_json["content"]
                    self.update_content_code(buffer_json)
                    yield partial_message
                else:
                    continue

        self.messages.append({"role": "assistant", "content": partial_message})
        self.answer = partial_message

    def is_valid_json(self, json_string):
        try:
            json.loads(json_string)
            return True
        except json.JSONDecodeError:
            return False
        
    def reset_messages(self, history):
        self.messages = []
        for human, assistant in history:
            self.messages.append({"role": "user", "content": human })
            self.messages.append({"role": "assistant", "content":assistant})
    
    def clear_messages(self):
        self.messages = self.init_message()
