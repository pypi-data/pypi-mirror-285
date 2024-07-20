import os
import json
import logging

name = "magv"

config_sample = '''{
    "Index-Repo" : "https://atomgit.com/zouxiangneihe/magv-index.git"
}'''

class magv_config:
    def __init__(self):
        self.logger = logging.getLogger("MANGROVE")
        self.config_json = os.path.expanduser("~/.magv/config.json")
        self.config_path = os.path.expanduser("~/.magv")
        self.repo_path = os.path.expanduser("~/.magv/magv-index")
        self.log_path = os.path.expanduser("~/.magv/magv.log")
        try:
            FIRST_RUN = False
            if not os.path.isfile(self.config_json):
                os.makedirs(self.config_path, exist_ok = True)
                with open(self.config_json, "w+") as f:
                    f.write(config_sample)
                    f.close()
                FIRST_RUN = True
            logging.basicConfig(filename=os.path.expanduser("~/.magv/magv.log"), level=logging.DEBUG, filemode="w+")
            with open(self.config_json) as f:
                self.config = json.loads(f.read())
                f.close()
                if FIRST_RUN:
                    os.system(f"git clone {self.config['Index-Repo']} {self.repo_path}")
                    print("WARNING: YOU SHOULD CHANGE YOUR CONFIGURE FILE MANUALLY AT ~/.magv/config.json TO USE MANGROVE")
                    self.logger.warning("WARNING: YOU SHOULD CHANGE YOUR CONFIGURE FILE MANUALLY AT ~/.magv/config.json TO USE MANGROVE")
                else:
                    current_working_dir = os.getcwd()
                    os.chdir(self.repo_path)
                    os.system(f"git pull")
                    os.chdir(current_working_dir)
        except:
            self.logger.fatal("An error occured while initialization")
            exit(1)