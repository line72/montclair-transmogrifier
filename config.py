
class Config:
    def __init__(self,
                 build_dir = './build', # base location of the builds
                 repo = 'whitelabel', # The repo suffix
                 package_name = 'montclair-whitelabel', # App package name
                 name = 'Montclair Whitelabel', # Project name, this shows up in multiple places
                 description = 'Real time Bus Tracker',
                 url = 'https://whitelabel.montclair.line72.net',
                 logo_svg = '', # Path to the logo.svg (used to generate favicon.ico and app-icon.png)
                 montclair_config = None,
                 ios_config = None,
                 android_config = None
                 ):
        self.build_dir = build_dir
        self.repo = repo
        self.package_name = package_name
        self.name = name
        self.description = description
        self.url = url
        self.logo_svg = logo_svg
        self.montclair_config = montclair_config
        self.ios_config = ios_config
        self.android_config = android_config

class MontclairConfig:
    def __init__(self,
                 version = '1.0.0', # version of montclair to build from
                 revision = 1, # output revision of whitelabel build,
                 title = None, # optional title
                 first_run_text = '', # text to show the first time the app is run
                 configuration_js_file = '' # path to the Configuration.js
    ):
        self.version = version
        self.revision = revision
        self.title = title
        self.first_run_text = first_run_text
        self.configuration_js_file = configuration_js_file

class MontclairiOSConfig:
    def __init__(self,
                 version = '1.0.0', # version of montclair-pwa-ios to build from
                 revision = 1, # output revision of whitelabel build
                 app_id = 'net.line72.montclair.whitelabel',
                 app_store_id = '',
                 app_store_url = '' # URL to the app store
    ):
        self.version = version
        self.revision = revision
        self.app_id = app_id
        self.app_store_id = app_store_id
        self.app_store_url = app_store_url

class MontclairAndroidConfig:
    def __init__(self,
                 version = '1.0.0', # version of montclair-pwa-android to build from
                 revision = 1, # output revision of whitelabel build
                 app_id = 'net.line72.montclair.whitelabel',
                 play_store_url = '' # URL to the play store
    ):
        self.version = version
        self.revision = revision
        self.app_id = app_id
        self.play_store_url = play_store_url
