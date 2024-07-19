from .config import Config


def find_tag(tags):
    for tag in tags:
        if Config.project_key() and Config.project_key() in tag:
            return tag