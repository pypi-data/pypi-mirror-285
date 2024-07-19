import asyncio

from fastapi                                                        import Request
from starlette.responses                                            import StreamingResponse
from cbr_athena.athena__fastapi.routes.Routes__OpenAI               import Routes__OpenAI
from cbr_athena.aws.dynamo_db.DyDB__CBR_Chat_Threads                import log_llm_chat
from cbr_athena.llms.chats.LLM__Chat_Completion__Resolve_Engine     import LLM__Chat_Completion__Resolve_Engine
from cbr_athena.llms.storage.CBR__Chats_Storage__Local              import CBR__Chats_Storage__Local
from cbr_athena.schemas.for_fastapi.LLMs__Chat_Completion           import LLMs__Chat_Completion
from osbot_fast_api.api.Fast_API_Routes                             import Fast_API_Routes

ROUTES_PATHS__CONFIG = ['/config/status', '/config/version']

class Routes__Chat(Fast_API_Routes):
    tag                     : str = 'chat'
    cbr_chats_storage_local: CBR__Chats_Storage__Local

    def execute_llm_request(self, llm_chat_completion):
        llm_platform_engine = LLM__Chat_Completion__Resolve_Engine().map_provider(llm_chat_completion)
        if llm_platform_engine:
            return llm_platform_engine.execute_request()
        return 'no engine'

    async def handle_other_llms(self, llm_chat_completion: LLMs__Chat_Completion, request: Request):
        stream = llm_chat_completion.stream
        if stream:
            return StreamingResponse(self.handle_other_llms__streamer(llm_chat_completion, request), media_type='text/event-stream"; charset=utf-8')
        else:
            return await self.handle_other_llms__no_stream(llm_chat_completion, request)

    async def handle_other_llms__no_stream(self, llm_chat_completion: LLMs__Chat_Completion, request: Request):
        complete_answer =  self.execute_llm_request(llm_chat_completion)
        try:
            request_headers = {key: value for key, value in request.headers.items()}
            log_llm_chat(llm_chat_completion, complete_answer, request_headers)
            llm_chat_completion.llm_answer = complete_answer
            self.cbr_chats_storage_local.chat_save(llm_chat_completion)
        except:
            pass
        return complete_answer

    async def handle_other_llms__streamer(self, llm_chat_completion: LLMs__Chat_Completion, request: Request):
        complete_answer = ''
        async def simulated_api_call():                         # Simulating the response of the async API call
            #user_data = llm_chat_completion.user_data or {}

            response =  self.execute_llm_request(llm_chat_completion)
            for chunk in response:
                await asyncio.sleep(0)                           # this is needed to trigger sending the data back (without it, we don't get streaming)
                yield chunk

        generator = simulated_api_call()
        async for answer in generator:
            if answer:
                complete_answer += answer
                yield f"{answer}\n"

        try:
            request_headers = {key: value for key, value in request.headers.items()}
            log_llm_chat(llm_chat_completion, complete_answer, request_headers)
            llm_chat_completion.llm_answer = complete_answer
            self.cbr_chats_storage_local.chat_save(llm_chat_completion)
        except:
            pass


    async def completion(self, llm_chat_completion: LLMs__Chat_Completion, request: Request):
        routes_open_ai = Routes__OpenAI()
        user_data      = llm_chat_completion.user_data

        # for now use the code in routes_open_ai.prompt_with_system__stream which is already working for OpenAI
        if 'selected_platform' in user_data and user_data.get('selected_platform') != 'OpenAI (Paid)':
            return await self.handle_other_llms(llm_chat_completion, request)
        else:
            stream = llm_chat_completion.stream
            if stream:
                return await routes_open_ai.prompt_with_system__stream(llm_chat_completion, request)
            else:
                return await routes_open_ai.prompt_with_system__not_stream(llm_chat_completion, request)

    async def view(self, chat_id: str):
        chat_cache = self.cbr_chats_storage_local.chat(chat_id)
        if chat_cache.cache_exists():
            return chat_cache.data().get('latest')
        return {}

    async def poc_save(self):
        llm_chat_completion = LLMs__Chat_Completion()
        cache_key = self.cbr_chats_storage_local.chat_save(llm_chat_completion)
        return dict(chat_id = llm_chat_completion.chat_thread_id, cache_key = cache_key)

    def setup_routes(self):
        self.router.post("/completion"     )(self.completion )
        self.router.get("/view"            )(self.view       )
        self.router.get("/poc-save"        )(self.poc_save   )



