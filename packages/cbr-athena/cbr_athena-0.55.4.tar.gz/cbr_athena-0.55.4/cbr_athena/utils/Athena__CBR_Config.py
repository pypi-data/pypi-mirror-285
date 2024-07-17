import requests

from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Env import get_env

from osbot_utils.base_classes.Type_Safe import Type_Safe
from osbot_utils.utils.Http import GET_json

PORT_LOCAL__CBR_WEBSITE = get_env('PORT', 3000)                                                            # todo: check side effect of mapping this here (vs later when the load_dotenv has happened)
URL__LOCAL__CBR_CONFIG  = f'http://localhost:{PORT_LOCAL__CBR_WEBSITE}/site_info/cbr-config-active'        # todo: refactor this to a better solution to get this data exposed to this service

class Athena__CBR_Config(Type_Safe):

    def aws_enabled(self):
        if get_env('AWS_ACCESS_KEY_ID'):
            return True
        return False

    def aws_disabled(self):
        enabled = self.aws_enabled()
        return enabled == False
    # def aws_enabled(self):
    #     return self.cbr_website().get('aws_enabled', False)
    #
    # def cbr_config(self):
    #     return self.cbr_config_active().get('cbr_config', {})
    #
    # @cache_on_self
    # def cbr_config_active(self):  # this is handling the entire server ( i think is because of the internal call to an internal endpoint)
    #     try:
    #         print(f'in cbr_config_active: {URL__LOCAL__CBR_CONFIG}')
    #         cbr_config = GET_json(URL__LOCAL__CBR_CONFIG)
    #         pprint(cbr_config)
    #         return cbr_config
    #     except:
    #         return {}
    #         # response = requests.get(URL__LOCAL__CBR_CONFIG)  # this was hanging the entire server
    #         # if response.status_code == 200:
    #         #     return response.json()
    #         # return {}
    #
    # def aws_disabled(self):
    #     print('in aws_disabled')
    #     return self.aws_enabled() == False
    #
    # def cbr_website(self):
    #     return self.cbr_config().get('cbr_website', {})


athena__cbr_config = Athena__CBR_Config()