from cbr_athena.llms.chats.LLM__Platform_Engine import LLM__Platform_Engine
from cbr_athena.llms.providers.groq.LLM__Groq import LLM__Groq
from cbr_athena.schemas.for_fastapi.LLMs__Chat_Completion import LLMs__Chat_Completion
from osbot_utils.utils.Dev import pprint


class LLM__Platform_Engine__Groq(LLM__Platform_Engine):
    llm_platform       : str
    llm_provider       : str
    llm_model          : str
    llm_chat_completion: LLMs__Chat_Completion
    llm__groq          : LLM__Groq

    # def is_provider_available(self):
    #     return False

    def execute_request(self):
        with self.llm__groq as _:
            _.add_messages__system(self.llm_chat_completion.system_prompts)
            _.add_histories       (self.llm_chat_completion.histories     )
            _.add_message__user   (self.llm_chat_completion.user_prompt   )
            _.set_model           (self.llm_model)
            _.set_stream          (self.llm_chat_completion.stream)
            return _.chat_completion()