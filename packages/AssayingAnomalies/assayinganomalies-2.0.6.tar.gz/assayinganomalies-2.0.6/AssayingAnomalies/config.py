# config.py
import json
import shutil
from contextlib import ExitStack
import importlib_resources
import os


class Config:
    def __init__(self):
        self.username = None
        self.password = None
        self.sample_start = None
        self.sample_end = None
        self.domComEqFlag = None
        self.data_storage_path = None
        self.data_folder = None
        self.crspFolder = None
        self.compFolder = None
        self.daily_crsp_folder = None
        self.ff_data_folder = None
        self.num_cpus = os.cpu_count()
        self.gibbs_data_folder = None
        self.hf_effective_spreads_folder = None

    def prompt_user(self):
        self.username = str(input("Enter your WRDS username: "))
        self.password = str(input("Enter your WRDS password: "))
        self.sample_start = int(input("Enter sample start year: "))
        self.sample_end = int(input("Enter sample end year: "))

        # For Boolean input, check the string entered
        domComEqInput = input("Enter True if you would like only domestic common equity otherwise False: ")
        self.domComEqFlag = domComEqInput.strip().lower() == 'true'
        remoteInput = input("Enter True if you are using BlueHive or CIRC, otherwise False: ")
        self.remote_or_not = remoteInput.strip().lower() == 'true'

        self.data_storage_path = input("Enter the path to where you would like the downloaded data and variables"
                                       " stored. If you are using CIRC and are unsure, enter /scratch/user_id: ")

        # if self.remote_or_not:
        #     self.num_cpus = int(input("Enter the number of CPUs. If unsure, enter 1: "))

    def make_folders(self):
        paths = []
        self.data_folder = os.path.join(self.data_storage_path, 'AA_Data')
        paths.append(self.data_folder)
        self.crspFolder = os.path.join(self.data_folder, 'CRSP')
        paths.append(self.crspFolder)
        self.compFolder = os.path.join(self.data_folder, 'COMPUSTAT')
        paths.append(self.compFolder)
        self.daily_crsp_folder = os.path.join(self.crspFolder, 'Daily')
        paths.append(self.daily_crsp_folder)
        self.ff_data_folder = os.path.join(self.data_folder, 'FFData')
        paths.append(self.ff_data_folder)
        self.gibbs_data_folder = os.path.join(self.data_folder, 'Gibbs')
        paths.append(self.gibbs_data_folder)
        self.hf_effective_spreads_folder = os.path.join(self.data_folder, 'High-frequency effective spreads')
        paths.append(self.hf_effective_spreads_folder)
        for path in paths:
            os.makedirs(path, exist_ok=True)

    def save_params(self, filepath="config.json"):
        with open(filepath, 'w') as f:
            # Convert configuration parameters to a dictionary and save as JSON
            config_dict = self.__dict__
            json.dump(config_dict, f)

    def move_trading_costs_files(self):
        # Define the source folders
        with ExitStack() as stack:
            gibbs_source = stack.enter_context(importlib_resources.as_file(
                importlib_resources.files('AssayingAnomalies') / 'Gibbs')
            )
            hf_spreads_source = stack.enter_context(importlib_resources.as_file(importlib_resources.files(
                'AssayingAnomalies') / 'High-frequency effective spreads')
            )

            # Define a dictionary mapping source folders to target folders
            source_to_target = {
                gibbs_source: self.gibbs_data_folder,
                hf_spreads_source: self.hf_effective_spreads_folder
            }

            # Move files from each source folder to the respective target folder
            for source, target in source_to_target.items():
                if os.path.exists(source):
                    for filename in os.listdir(source):
                        shutil.move(os.path.join(source, filename), os.path.join(target, filename))


    @staticmethod
    def load_params(filepath="config.json"):
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                config_dict = json.load(f)
                config = Config()
                config.__dict__.update(config_dict)
                return config
        else:
            return None

    def set_up(self):
        self.prompt_user()
        self.make_folders()
        self.move_trading_costs_files()
        self.save_params()


# test = Config()
# test.prompt_user()

