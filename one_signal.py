import json
import requests

from resources import create_resource_dict_for_languages

onesignal_js_init_template = '''
            var OneSignal = window.OneSignal || [];
            var initConfig = {{
               appId: "{app_id}",
               safari_web_id: "{safari_id}",
               notifyButton: {{
                   enable: true,
               }},
               // This is needed for now for localtesting
               allowLocalhostAsSecureOrigin: {allow_local_host},
               subdomainName: 'http://127.0.0.1:5000'
            }};
            OneSignal.push(function () {{
                OneSignal.SERVICE_WORKER_PARAM = {{ scope: '/assets/' }};
                OneSignal.SERVICE_WORKER_PATH = 'assets/OneSignalSDKWorker.js'
                OneSignal.SERVICE_WORKER_UPDATER_PATH = 'assets/OneSignalSDKUpdaterWorker.js'
                OneSignal.init(initConfig);
            }});
        '''


class OneSignal:

    def __init__(self, app_id, safari_id, allow_local_host, api_key, is_debug):
        """Inits OneSignal with connection details"""
        self.app_id = app_id
        self.safari_id = safari_id
        self.allow_local_host = allow_local_host
        self.rest_api_key = api_key
        self.is_debug = is_debug

    def send(self, resource_key):
        auth_header = f"Basic {self.rest_api_key}"
        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": auth_header}

        message_content = create_resource_dict_for_languages(resource_key, self.is_debug)
        payload = {"app_id": self.app_id,
                   "included_segments": ["Subscribed Users"],
                   "contents": message_content}

        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
        return req

    def create_onesignal_js_init(self):
        return onesignal_js_init_template.format(app_id=self.app_id,
                                                 safari_id=self.safari_id,
                                                 allow_local_host=self.allow_local_host)
