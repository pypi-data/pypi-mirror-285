from cbr_athena.athena__fastapi.odin.FastApi_Header_Auth import route_with_auth
from cbr_athena.athena__fastapi.odin.api.Odin__EC2      import Odin__EC2
from cbr_athena.athena__fastapi.routes.Fast_API_Route   import Fast_API__Routes
from cbr_athena.utils.Version import Version
from osbot_utils.utils.Status import status_ok, status_error

FAST_API_ROUTES__ODIN__API__AWS =  ['/aws/ec2/instance_info'    ,
                                    '/aws/ec2/running_instances',
                                    '/aws/ec2/start_instance'   ,
                                    '/aws/ec2/stop_instance'    ]
class Routes__AWS(Fast_API__Routes):
    path_prefix: str = "aws"

    def __init__(self):
        super().__init__()
        self.odin_ec2 = Odin__EC2()

    def add_routes(self):

        @route_with_auth(self.router, 'get', '/ec2/instance_info', summary="Get information and details about an EC2 instance")
        def ec2_instance_info(instance_id):
            try:
                return status_ok(data=self.odin_ec2.instance_info(instance_id))
            except Exception as e:
                return status_error(message=f"Failed to get into about {instance_id}", error=str(e))

        @route_with_auth(self.router, 'get', '/ec2/running_instances', summary="List running EC2 instances")
        def ec2_running_instances():
            instances = self.odin_ec2.running_instances()
            return instances

        @route_with_auth(self.router, 'get','/ec2/start_instance', summary="Start an EC2 instance")
        def ec2_start_instances():
            instance_id = self.odin_ec2.start_instance()
            return {'instance_id': instance_id}

        @route_with_auth(self.router, 'get','/ec2/stop_instance', summary="Stop an EC2 instance")
        def ec2_stop_instance(instance_id):
            try:
                self.odin_ec2.stop_instance(instance_id)
                return status_ok(message= f"Instance {instance_id} is being stopped.")
            except Exception as e:
                return status_error(message=f"Failed to stop {instance_id}", error=str(e))
