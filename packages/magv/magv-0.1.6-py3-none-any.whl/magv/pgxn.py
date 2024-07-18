import os
import requests
import shutil
import json

PGXN_API = "https://api.pgxn.org"

def get_latest_ver(extension, config):
    obj = requests.get(PGXN_API + f"/extension/{extension}.json")
    config.logger.info(f"Get {extension} status from PGXN, HTTP status code {obj.status_code}")
    if not obj.status_code == 200:
        raise Exception(obj.status_code)
    ext_json = json.loads(obj.content)
    return ext_json[ext_json["latest"]]["version"]

def download(path, extension, version, config):
    if version == "master":
        version = get_latest_ver(extension, config)
    obj = requests.get(PGXN_API + f"/dist/{extension}/{version}/{extension}-{version}.zip")
    config.logger.info(f"Downloaded {extension} from PGXN, HTTP status code {obj.status_code}")
    if not obj.status_code == 200:
        raise Exception(obj.status_code)
    try:
        with open(os.path.join(path, f"{extension}-{version}.zip"), "wb+") as f:
            f.write(obj.content)
        f.close()
    except Exception as e:
        config.logger.error(f"Cannot write into {os.path.join(path, f'{extension}-{version}.zip')}")
        raise e
    try:
        unzip_path = os.path.join(path, f'{extension}-{version}')
        shutil.unpack_archive(os.path.join(path, f"{extension}-{version}.zip"), path)
        os.system(f"mv {unzip_path}/* {path}")
        os.system(f"mv {unzip_path}/.[!.]* {path}")
        os.system(f"rm -rf {unzip_path}")
        os.remove(os.path.join(path, f.name))
    except Exception as e:
        config.logger.error(f"An error occured while performing file operations")
        config.logger.error(e)
        raise e

def search(ext, config):
    try:
        res = json.loads(requests.get(f"https://api.pgxn.org/search/extensions?q={ext}").content)["hits"]
        ext_list = list()
        for item in res:
            ext_list.append([item["extension"], "PGXN", item["abstract"]])
        return ext_list
    except Exception as e:
        config.logger.error("An error occured while searching extension in PGXN")
        raise e