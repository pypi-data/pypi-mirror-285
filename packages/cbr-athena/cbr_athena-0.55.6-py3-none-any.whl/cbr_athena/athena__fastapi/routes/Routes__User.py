from pydantic import BaseModel

from cbr_athena.athena__fastapi.routes.Fast_API_Route           import Fast_API__Routes
from cbr_athena.odin.Data__User_Session                 import Data__User_Session
from cbr_athena.schemas.for_fastapi.Create_User_Session import Create_User_Session


class Routes__User(Fast_API__Routes):
    path_prefix: str = "user"

    def __init__(self):
        super().__init__()
        self.Data__User_Session = Data__User_Session()

    def add_routes(self):

        @self.router.post('/create_user_session')
        async def post__create_user_session(create_user_session: Create_User_Session):
            kwargs = dict(user_name      = create_user_session.user_name                     ,
                          session_id     = create_user_session.session_id                    ,
                          source         = create_user_session.source         or 'Athena_API',
                          cognito_tokens = create_user_session.cognito_tokens or {}          )
            session_id = self.Data__User_Session.dydb__create_session(**kwargs)
            if session_id:
                return {"session_id": session_id}
            return {"status":"error","message":"user session not found"}