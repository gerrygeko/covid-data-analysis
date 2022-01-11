import dash
import logger

log = logger.get_logger()


class CustomDash(dash.Dash):
    def __init__(self, *args, **kwargs):
        log.info("Init Custom dash app")
        super().__init__(*args, **kwargs)

    def interpolate_index(self, **kwargs):
        return '''
<!DOCTYPE html>
<html>
    <head>
        {metas}
        <title>{title}</title>

        <link rel="apple-touch-icon" sizes="180x180" href="/assets/apple-touch-icon.png">
        <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16x16.png">
        <link rel="manifest" href="/assets/site.webmanifest">
        <link rel="mask-icon" href="/assets/safari-pinned-tab.svg" color="#5bbad5">
        <link rel="shortcut icon" href="/assets/favicon.ico">
        <meta name="msapplication-TileColor" content="#da532c">
        <meta name="msapplication-config" content="/assets/browserconfig.xml">
        <meta name="theme-color" content="#ffffff">

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
        '''.format(**kwargs)