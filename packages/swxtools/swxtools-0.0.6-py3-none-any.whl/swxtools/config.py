import yaml
import os


ISO_TIMEFMT = '%Y-%m-%dT%H:%M:%S.%fZ'


def loadConfig():
    config = {}
    config_file = 'swxtools.cfg'
    if not os.path.isfile(config_file):
        config_file = os.path.expanduser('~/.swxtools.cfg')
    if os.path.isfile(config_file):
        config = yaml.safe_load(open(config_file))
        return config, config_file
    else:
        raise FileNotFoundError('No configuration file found')


config, config_file = loadConfig()
