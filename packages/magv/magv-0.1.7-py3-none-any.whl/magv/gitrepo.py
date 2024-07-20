import os

def download(path, extension, ver, config):
    try:
        os.chdir(path)
        config.logger.info(f"Downloading git repository from {extension} to {path}, cloning from branch {ver}")
        if not os.system("git clone --depth=1 --branch " + ver + " " + extension + " " + path) == 0:
            raise Exception(f"Unable to clone git repository from")
    except Exception as e:
        config.logger.error(f"An error occured while downloading git repository")
        raise e