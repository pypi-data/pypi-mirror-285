from dotenv import load_dotenv

#from cbr_athena.dbs.DB__CBR__Content import DB__CBR__Content
from cbr_athena.athena__fastapi.routes.Fast_API_Route import Fast_API__Routes
from cbr_athena.utils.Version import Version

class Routes__Dev(Fast_API__Routes):
    path_prefix: str = "dev"

    def __init__(self):
        super().__init__()
        load_dotenv()
        #self.db_cbr_content = DB__CBR__Content()

    def add_routes(self):

        pass
        # @self.router.get('/first_question')
        # def first_question():
        #     return {"question": "Hi, this is my first question"}
        #
        # @self.router.get('/files_in_db')
        # def files_in_db():
        #     file_paths = []
        #     for file in self.db_cbr_content.files():
        #         file_paths.append(file.get('path'))
        #     return file_paths