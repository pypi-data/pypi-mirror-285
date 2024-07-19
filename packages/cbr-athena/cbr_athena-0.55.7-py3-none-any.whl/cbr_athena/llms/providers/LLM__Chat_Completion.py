import requests
from osbot_utils.base_classes.Type_Safe import Type_Safe
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Json import from_json_str
from osbot_utils.utils.Status           import status_error


MAX_ANSWER_SIZE = 512

class LLM__Chat_Completion(Type_Safe):
    base_url : str
    api_key  : str
    model    : str
    messages : list
    stream   : bool = True

    def add_histories(self, histories):
        if type(histories) is list:
            for item in histories:
                question = item.question
                answer   = item.answer
                if answer and len(answer) > MAX_ANSWER_SIZE:                        # todo: move this to a separate method and make this more scientific (for example using an LLM to create a summary)
                    answer = answer[:MAX_ANSWER_SIZE] + "..."               # do this so that we don't have an exponential growth in the size of the content sent to the LLMs
                self.add_message('user'     , question)
                self.add_message('assistant', answer)

    def add_message__system(self, system_prompt):
        self.add_message('system', system_prompt)
        return self

    def add_message__user(self, user_prompt):
        self.add_message('user', user_prompt)
        return self

    def add_messages__system(self, system_prompts):
        if type(system_prompts) is list:
            for system_prompt in system_prompts:
                self.add_message__system(system_prompt)
        return self

    def add_messages__user(self, user_prompts):
        for user_prompt in user_prompts:
            self.add_message__user(user_prompt)
        return self

    def add_message(self, role, content):
        message = {'role': role, 'content': content}
        self.messages.append(message)
        return self

    def chat_completion(self):
        if self.stream:
            return self.chat_completion__streamed()
        else:
            return self.chat_completion__not_streamed()

    def chat_completion__not_streamed(self):
        if self.is_provider_not_available():
            return f"Provider not available"
        messages = self.messages
        headers  =  { 'Authorization': f'Bearer {self.api_key}',
                      'Content-Type' : 'application/json'      }
        json_data = { 'messages': messages   ,
                      'model'   : self.model ,
                      'stream'  : False      }
        post_data = { 'headers': headers     ,
                      'json'   : json_data    ,
                      'url'    : self.base_url}

        response  = self.requests_post__not_streamed(**post_data)
        return response

    def chat_completion__streamed(self):
        if self.is_provider_not_available():
            yield f"Provider not available"
        messages = self.messages
        headers  =  { 'Authorization': f'Bearer {self.api_key}',
                      'Content-Type' : 'application/json'      }
        json_data = { 'messages': messages   ,
                      'model'   : self.model ,
                      'stream'  : True       }
        post_data = { 'headers': headers     ,
                      'json'   : json_data    ,
                      'url'    : self.base_url}

        response  = self.requests_post__streamed(**post_data)
        for item in response:
            yield item

    def is_provider_available(self):
        if self.api_key:
            return True
        return False

    def is_provider_not_available(self):
        return self.is_provider_available() is False

    def json_data(self):
        payload = { "messages": self.messages,
                    "model"   : self.model  }
        return payload

    def make_request(self, post_data):
        response  = requests.post(**post_data)
        if response.status_code == 200:
            if response.headers['Content-Type'] == 'application/x-ndjson':
                return response
            else:
                return response.json()
        else:
            return status_error(error=response.text, message=f'request failed with status code: {response.status_code}')

    def requests_post__not_streamed(self, url, json, headers=None):  # todo refactor the other methods to use this naming convention
        try:
            response = requests.post(url, headers=headers, json=json)
            if response.status_code != 200:
                return  f"Error fetching Open Router data, status_code was {response.status_code}, text was : {response.text}"
            json_data = response.json()
            choice  = json_data.get('choices')[0]
            content = choice.get('message').get('content')
            return content
        except Exception as error:
            return f"Error fetching Open Router data : {error}"

    def requests_post__streamed(self, url, json, headers=None):  # todo refactor the other methods to use this naming convention
        try:
            response = requests.post(url, headers=headers, json=json, stream=True)
            for line in response.iter_lines():
                if line:
                    raw_data = line.decode('utf-8')
                    if raw_data.startswith('data: {'):
                        json_line = raw_data[5:]
                        json_data = from_json_str(json_line)
                        choice = json_data.get('choices')[0]
                        yield choice.get('delta').get('content')
                    elif raw_data.startswith('{'):
                        yield raw_data
                        # json_data = from_json_str(raw_data)
                        # if json_data:
                        #     yield json_data
        except Exception as error:
            yield f"Error fetching Open Router data : {error}"

    def post_data(self):
        url     = self.base_url
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"
        json    = self.json_data()
        return dict(url=url, headers=headers, json=json)


    def send_post_data(self):
        post_data = self.post_data()
        return self.make_request(post_data=post_data)

    def send_user_prompt(self, user_prompt):                # todo: see if we need this
        self.add_message__user(user_prompt)
        post_data = self.post_data()
        #pprint(post_data)
        return self.make_request(post_data=post_data)

    def set_model(self, value):
        self.model = value
        return self

    def set_stream(self, value):
        self.stream = value
        return self