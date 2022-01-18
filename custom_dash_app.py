import dash
import logger

from utils import is_debug_mode_enabled

log = logger.get_logger()

local_app_id = "ead5eb43-3ae1-4e43-8dab-1cd349942ffa"
production_app_id = "520730fb-1d3b-4218-a9c1-09d9b8342340"

local_safari_id = "web.onesignal.auto.13f7d09c-87f4-478e-9a86-b96c3b883b5b"
production_safari_id = "web.onesignal.auto.0d6d1ede-d24a-45d0-ba73-2f88839c0735"

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


def create_onesignal_js_init():
    if is_debug_mode_enabled():
        app_id = local_app_id
        safari_id = local_safari_id
        allow_local_host = "true"
    else:
        app_id = production_app_id
        safari_id = local_safari_id
        allow_local_host = "false"

    return onesignal_js_init_template.format(app_id=app_id, safari_id=safari_id, allow_local_host=allow_local_host)


class CustomDash(dash.Dash):
    def __init__(self, *args, **kwargs):
        log.info("Init Custom dash app")
        super().__init__(*args, **kwargs)

    def interpolate_index(self, **kwargs):
        onesignal_js = create_onesignal_js_init()

        return '''
<!DOCTYPE html>
<html lang="it">
    <head>
        {metas}
        <title>{title}</title>

        <link rel="apple-touch-icon" sizes="180x180" href="/assets/apple-touch-icon.png">
        <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16x16.png">
        <link rel="manifest" href="/assets/site.webmanifest">
        <link rel="mask-icon" href="/assets/safari-pinned-tab.svg" color="#5bbad5">
        <link rel="shortcut icon" href="/assets/favicon.ico">
        <!-- Android: Chrome, Firefox OS and Opera -->
        <meta name="theme-color" content="#7bc7ff">
        <!-- iOS N.B. the color bar will be the same of body background-->
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="msapplication-TileColor" content="#7bc7ff">
        <meta name="msapplication-config" content="/assets/browserconfig.xml">
        <meta name="theme-color" content="#ffffff">
        <script type='text/javascript' src='/assets/register-sw.js'></script>
        <script src="https://cdn.onesignal.com/sdks/OneSignalSDK.js" async=""></script>
        <script>{onesignal_js_init}</script>
        {css}
    </head>
    <body>
        {app_entry}
        <footer>
            {config}
            {scripts}
            {renderer}
        </footer>
    </body>
</html>
        '''.format(onesignal_js_init=onesignal_js, **kwargs)
