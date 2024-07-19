from cbr_athena.aws.ec2.CBR__EC2_Instance       import CBR__EC2_Instance
from osbot_aws.AWS_Config                       import AWS_Config
from osbot_aws.aws.ec2.EC2                      import EC2
from osbot_utils.base_classes.Kwargs_To_Self    import Kwargs_To_Self
from osbot_utils.utils.Status                   import status_error

AMIS_PER_REGION = {'eu-west-1': 'ami-0136026a91d5f4151',
                   'eu-west-2': 'ami-008ea0202116dbc56'}

class Odin__EC2(Kwargs_To_Self):
    ec2        : EC2
    aws_config : AWS_Config

    def instance_info(self, instance_id):
        return self.ec2.instance_details(instance_id)

    def start_instance(self):
        try:
            ec2_instance = CBR__EC2_Instance()
            region_name  = self.aws_config.region_name()
            image_id     = AMIS_PER_REGION.get(region_name)
            ec2_instance.create_kwargs['image_id'] = image_id       # todo: add this AMI detection to the CBR__EC2_Instance class
            return ec2_instance.create()
        except Exception as e:
            return status_error(message='failed to create EC2 instance',
                                error=str(e))

    def stop_instance(self, instance_id):
        return self.ec2.instance_terminate(instance_id)

    def running_instances(self):
        return self.ec2.instances_details()