from cbr_athena.athena__fastapi.routes.Fast_API_Route import Fast_API__Routes


class Routes__Auth(Fast_API__Routes):
    path_prefix: str = "auth"

    def add_routes(self):
        @self.router.get('/auth_user_id')
        def auth_user_id():
            return 'will go here'