import os
from typing import Union
import pandas as pd
from copy import deepcopy
from simba.mixins.config_reader import ConfigReader
from simba.utils.checks import check_file_exist_and_readable
from simba.utils.read_write import read_df, write_df
from simba.utils.printing import SimbaTimer

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
            video_timer = SimbaTimer(start=True)
            data_path = os.path.join(self.features_dir, file_name + f'.{self.file_type}')
            data_df = read_df(file_path=data_path, file_type=self.file_type)
            out_df = deepcopy(data_df)
            save_path = os.path.join(self.targets_folder, file_name + f'.{self.file_type}')
            df = pd.DataFrame(file_df.values[1:, :3], columns=['BEHAVIOR', 'START', 'STOP'])
            df['BEHAVIOR'] = df['BEHAVIOR'].str.lower()
            for clf in self.clf_names:
                clf_df = df[df['BEHAVIOR'] == clf].sort_values(['START'])
                out_df[clf] = 0
                if len(clf_df) > 0:
                    annot_idx = list(clf_df.apply(lambda x: list(range(int(x["START"]), int(x["STOP"]) + 1)), 1))
                    annot_idx = [x for xs in annot_idx for x in xs]
                    if len(annot_idx) > 0:
                        out_df.loc[annot_idx, clf] = 1
            write_df(df=out_df, file_type=self.file_type, save_path=save_path)
            video_timer.stop_timer()
            print(f'{file_name} saved..')




            #
            # print(df)
            # print(annot_idx)
            # break
            #
            #

data_path = '/Users/simon/Desktop/envs/simba/troubleshooting/mitra/Start-Stop Annotations.xlsx'
config_path = '/Users/simon/Desktop/envs/simba/troubleshooting/mitra/project_folder/project_config.ini'
x = MitraStyleAnnotationAppender(config_path=config_path, data_path=data_path)
x.run()





