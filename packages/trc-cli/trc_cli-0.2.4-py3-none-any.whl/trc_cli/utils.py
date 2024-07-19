from pathlib import Path
import random
import glob
import json
from trc_cli.constants import *


def get_random_sbom(location: Path = SBOMS_PATH):
    # Define the path where .json files are located
    search = location / '*.json'

    # Get a list of all .json files in the specified path
    files = glob.glob(str(search))

    # If files list is not empty, pick and return a random file path
    if files:
        return Path(random.choice(files))
    # If no json files are found, notify the user
    else:
        return "No .json files found in the specified path."


def load_microservices(location: Path = MICROSERVICES_PATH):
    with location.open("r") as fs:
        data = json.load(fs)

    return data


def load_factsheet_ids(location: Path = TEMP_STORAGE):
    with location.open("r") as fs:
        data = json.load(fs)

    temp = list()

    for item in data:
        temp.append(item['factSheetId'])

    return temp
