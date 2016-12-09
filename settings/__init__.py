import json
import os

def import_settings():

    SETTINGS_FOLDER = 'settings/'
    DEFAULT_SETTINGS_FILE_LOCATION = SETTINGS_FOLDER+'default.conf'

    #Import the main settings file
    settings = json.load(open(DEFAULT_SETTINGS_FILE_LOCATION))

    #Check for other settings files to override
    for overriding_settings_file in os.listdir(SETTINGS_FOLDER):

        if overriding_settings_file not in ['__init__.py','__init__.pyc','default.conf','__pycache__']:

            print(overriding_settings_file)
            for setting,value in json.load(open(SETTINGS_FOLDER+overriding_settings_file)).keys():
                settings[setting] = value

    #Make an absolute path of some paths
    for setting_name in ['static_page','template','previous_static_pages_folder']:
        settings[setting_name] = settings['root_folder'] + settings[setting_name]

    return settings

