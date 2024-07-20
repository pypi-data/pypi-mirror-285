import os
from typing import Union
import pandas as pd
from simba.mixins.config_reader import ConfigReader
from simba.utils.checks import check_file_exist_and_readable
from simba.utils.read_write import read_df

class MitraStyleAnnotationAppender(ConfigReader):

    def __init__(self,
                 config_path: Union[str, os.PathLike],
                 data_path: Union[str, os.PathLike]):

        check_file_exist_and_readable(file_path=data_path)
        ConfigReader.__init__(self, config_path=config_path)
        self.data_path = data_path

    def run(self):
        df_dict = pd.read_excel(self.data_path, sheet_name=None)
        for file_name, file_df in df_dict.items():
            data_path = os.path.join(self.features_dir, file_name + f'.{self.file_type}')
            data_df = read_df(file_path=data_path, file_type=self.file_type)
            print(file_df)
            break








data_path = '/Users/simon/Desktop/envs/simba/troubleshooting/mitra/Start-Stop Annotations.xlsx'
config_path = '/Users/simon/Desktop/envs/simba/troubleshooting/mitra/project_folder/project_config.ini'
x = MitraStyleAnnotationAppender(config_path=config_path, data_path=data_path)
x.run()





