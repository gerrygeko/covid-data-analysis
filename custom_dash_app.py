import dash
import logger
import utils

log = logger.get_logger()


class CustomDash(dash.Dash):
    def __init__(self, *args, **kwargs):
        log.info("Init Custom dash app")
        super().__init__(*args, **kwargs)

    def interpolate_index(self, **kwargs):
        onesignal_js = utils.get_one_signal_init_javascript()

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
