from logging import INFO
from os import environ
from dotenv import load_dotenv

from osbot_aws.aws.ec2.EC2_Instance import EC2_Instance
from osbot_utils.testing.Logging import Logging
from osbot_utils.utils.Http import wait_for_ssh

CBR__AMIS = {'test-image-creation':'ami-0136026a91d5f4151'}

class CBR__EC2_Instance(EC2_Instance):
    logging : Logging

    def __init__(self):
        super().__init__()
        self.create_kwargs = self.cbr_create_kwargs()
        self.logging.log_to_sys_stdout()
        self.logging.set_logger_level(INFO)

    def cbr_create_kwargs(self):
        load_dotenv()
        instance_type     = 't3.nano'
        spot_instance     = True
        security_group_id = environ.get('EC2_TESTS__SECURITY_GROUP_ID')
        ssh_key_name      = environ.get('EC2_TESTS__PATH_SSH_KEY_FILE_NAME')
        return  dict(image_id          = 'ami-0136026a91d5f4151', # AMI created with python installed
                     key_name          = ssh_key_name  ,
                     security_group_id = security_group_id,
                     instance_type     = instance_type      ,
                     spot_instance     = spot_instance      )
    def log(self, message):
        self.logging.info(message)

    def ssh(self):
        ssh_key_file = environ.get('EC2_TESTS__PATH_SSH_KEY_FILE')
        ssh_key_user = environ.get('EC2_TESTS__PATH_SSH_KEY_USER')
        return super().ssh(ssh_key_file=ssh_key_file, ssh_key_user=ssh_key_user)


    def wait_for_instance_running(self):
        self.ec2.wait_for_instance_running(self.instance_id)

    def wait_for_ssh(self):
        return wait_for_ssh(self.ip_address())






