from cbr_athena.llms.providers.LLM__Chat_Completion import LLM__Chat_Completion
from osbot_utils.helpers.sqlite.cache.Sqlite__Cache__Requests__Patch import Sqlite__Cache__Requests__Patch

SQLITE_DB_NAME__Cache__Chat_Completions   =  'llm_chat_completions__cache.sqlite'
SQLITE_TABLE_NAME__Cache__Chat_Completions = 'llm_chat_completions'

class Cache__Chat_Completions(Sqlite__Cache__Requests__Patch):

    def __init__(self, db_path=None):
        self.target_class           = LLM__Chat_Completion
        self.target_function        = LLM__Chat_Completion.make_request
        self.target_function_name   = "make_request"
        self.db_name                = SQLITE_DB_NAME__Cache__Chat_Completions
        self.table_name             = SQLITE_TABLE_NAME__Cache__Chat_Completions
        self.capture_exceptions     = True
        self.print_requests         = False
        super().__init__(db_path=db_path)

    # override the method that is used to calculate the cache entry, where in the LLM__Chat_Completion.make_request
    #    the args are the self object
    def request_data(self, *args, **kwargs):
        return kwargs