import os

import cv2
import numpy as np
import pandas as pd
from itertools import product

from simba.mixins.config_reader import ConfigReader
from simba.mixins.feature_extraction_mixin import FeatureExtractionMixin
from simba.mixins.timeseries_features_mixin import TimeseriesFeatureMixin
from simba.mixins.feature_extraction_supplement_mixin import FeatureExtractionSupplemental
from simba.mixins.geometry_mixin import GeometryMixin
from simba.mixins.circular_statistics import CircularStatisticsMixin
from simba.feature_extractors.perimeter_jit import jitted_hull
from simba.utils.checks import check_if_filepath_list_is_empty, check_all_file_names_are_represented_in_video_log
from simba.utils.read_write import read_df, get_fn_ext, read_frm_of_video

NOSE = 'Nose'
LEFT_SIDE = 'Left_side'
RIGHT_SIDE = 'Right_side'
LEFT_EAR = 'Left_ear'
RIGHT_EAR = 'Right_ear'
CENTER = 'Center'
TAIL_BASE = 'Tail_base'
TAIL_CENTER = 'Tail_center'
TAIL_TIP = 'Tail_tip'

TIME_WINDOWS = np.array([0.25, 0.5, 1.0])


class MitraFeatureExtractor(ConfigReader):
    def __init__(self,
                 config_path: os.PathLike):

        ConfigReader.__init__(self, config_path=config_path, read_video_info=True, create_logger=False)
        check_if_filepath_list_is_empty(filepaths=self.outlier_corrected_paths, error_msg=f'No data files found in {self.outlier_corrected_dir} directory.')
        check_all_file_names_are_represented_in_video_log(video_info_df=self.video_info_df, data_paths=self.outlier_corrected_paths)

    def run(self):

        for file_cnt, file_path in enumerate(self.outlier_corrected_paths):
            df = read_df(file_path=file_path, file_type=self.file_type)
            results = pd.DataFrame()
            _, video_name, _ = get_fn_ext(filepath=file_path)
            _, px_per_mm, fps = self.read_video_info(video_name=video_name)
            shifted_ =  df.shift(periods=1).combine_first(df)
            nose_arr = df[[f'{NOSE}_x', f'{NOSE}_y']].values.astype(np.float32)
            p_arr = df[self.animal_bp_dict['Animal_1']['P_bps']].values.astype(np.float32)
            tailbase_arr = df[[f'{TAIL_BASE}_x', f'{TAIL_BASE}_y']].values.astype(np.float32)
            left_ear_arr = df[[f'{LEFT_EAR}_x', f'{LEFT_EAR}_y']].values.astype(np.float32)
            right_ear_arr = df[[f'{RIGHT_EAR}_x', f'{RIGHT_EAR}_y']].values.astype(np.float32)
            center_arr = df[[f'{CENTER}_x', f'{CENTER}_y']].values.astype(np.float32)
            lat_left_arr = df[[f'{LEFT_SIDE}_x', f'{LEFT_SIDE}_y']].values.astype(np.float32)
            lat_right_arr = df[[f'{RIGHT_SIDE}_x', f'{RIGHT_SIDE}_y']].values.astype(np.float32)
            tail_center_arr = df[[f'{TAIL_CENTER}_x', f'{TAIL_CENTER}_y']].values.astype(np.float32)
            tail_tip_arr = df[[f'{TAIL_TIP}_x', f'{TAIL_TIP}_y']].values.astype(np.float32)
            animal_hull_arr = df[[f'{LEFT_EAR}_x', f'{LEFT_EAR}_y', f'{RIGHT_EAR}_x', f'{RIGHT_EAR}_y', f'{NOSE}_x', f'{NOSE}_y', f'{LEFT_SIDE}_x', f'{LEFT_SIDE}_y', f'{RIGHT_SIDE}_x', f'{RIGHT_SIDE}_y', f'{TAIL_BASE}_x', f'{TAIL_BASE}_y']].values.astype(np.float32).reshape(len(df), 6, 2)
            animal_head_arr = df[[f'{LEFT_EAR}_x', f'{LEFT_EAR}_y', f'{RIGHT_EAR}_x', f'{RIGHT_EAR}_y', f'{NOSE}_x', f'{NOSE}_y']].values.astype(np.float32).reshape(len(df), 3, 2)
            direction_degrees = CircularStatisticsMixin().direction_three_bps(nose_loc=nose_arr, left_ear_loc=left_ear_arr, right_ear_loc=right_ear_arr).astype(np.float32)

            results['GEOMETRY_FRAME_ANIMAL_HULL_LENGTH'] = FeatureExtractionMixin.framewise_euclidean_distance(location_1=nose_arr, location_2=tailbase_arr, px_per_mm=px_per_mm).astype(np.int32)
            results['GEOMETRY_FRAME_ANIMAL_HULL_WIDTH'] = FeatureExtractionMixin.framewise_euclidean_distance(location_1=lat_left_arr, location_2=lat_right_arr, px_per_mm=px_per_mm).astype(np.int32)
            results['GEOMETRY_FRAME_HULL_PERIMETER_LENGTH'] = (jitted_hull(points=animal_hull_arr, target='perimeter') / px_per_mm).astype(np.int32)
            results['GEOMETRY_FRAME_HEAD_PERIMETER_LENGTH'] = (jitted_hull(points=animal_head_arr, target='perimeter') / px_per_mm).astype(np.int32)
            results['GEOMETRY_FRAME_TAIL_LENGTH'] = FeatureExtractionMixin.framewise_euclidean_distance(location_1=tailbase_arr, location_2=tail_tip_arr, px_per_mm=px_per_mm).astype(np.int32)

            results['CIRCULAR_FRAME_HULL_3POINT_ANGLE'] = FeatureExtractionMixin.angle3pt_serialized(data=np.hstack([nose_arr, center_arr, tailbase_arr])).astype(np.int32)
            results['CIRCULAR_FRAME_TAIL_3POINT_ANGLE'] = FeatureExtractionMixin.angle3pt_serialized(data=np.hstack([tailbase_arr, tail_center_arr, tail_tip_arr])).astype(np.int32)
            results['CIRCULAR_FRAME_HEAD_3POINT_ANGLE'] = FeatureExtractionMixin.angle3pt_serialized(data=np.hstack([left_ear_arr, nose_arr, right_ear_arr])).astype(np.int32)
            angular_difference = pd.DataFrame(CircularStatisticsMixin.sliding_angular_diff(data=direction_degrees, time_windows=TIME_WINDOWS, fps=int(fps)), columns=['CIRCULAR_HEAD_DIRECTION_ANGULAR_DIFFERENCE_250', 'CIRCULAR_HEAD_DIRECTION_ANGULAR_DIFFERENCE_500', 'CIRCULAR_HEAD_DIRECTION_ANGULAR_DIFFERENCE_1000'])
            rao_spacing = pd.DataFrame(CircularStatisticsMixin.sliding_rao_spacing(data=direction_degrees, time_windows=TIME_WINDOWS, fps=int(fps)), columns=['CIRCULAR_HEAD_DIRECTION_RAO_SPACING_250', 'CIRCULAR_HEAD_DIRECTION_RAO_SPACING_500', 'CIRCULAR_HEAD_DIRECTION_RAO_SPACING_1000'])
            circular_range = pd.DataFrame(CircularStatisticsMixin.sliding_circular_range(data=direction_degrees, time_windows=TIME_WINDOWS, fps=int(fps)), columns=['CIRCULAR_HEAD_DIRECTION_RANGE_250', 'CIRCULAR_HEAD_DIRECTION_RANGE_500', 'CIRCULAR_HEAD_DIRECTION_RANGE_1000'])
            circular_std = pd.DataFrame(CircularStatisticsMixin.sliding_circular_std(data=direction_degrees, time_windows=TIME_WINDOWS, fps=int(fps)), columns=['CIRCULAR_HEAD_DIRECTION_STD_250', 'CIRCULAR_HEAD_DIRECTION_STD_500', 'CIRCULAR_HEAD_DIRECTION_STD_1000'])
            results = pd.concat([results, angular_difference, rao_spacing, circular_range, circular_std], axis=1)

            results['MOVEMENT_FRAME_NOSE'] = FeatureExtractionMixin.framewise_euclidean_distance(location_1=nose_arr, location_2=shifted_[[f'{NOSE}_x', f'{NOSE}_y']].values.astype(np.float32), px_per_mm=px_per_mm).astype(np.int32)
            results['MOVEMENT_FRAME_CENTER'] = FeatureExtractionMixin.framewise_euclidean_distance(location_1=center_arr, location_2=shifted_[[f'{CENTER}_x', f'{CENTER}_y']].values.astype(np.float32), px_per_mm=px_per_mm).astype(np.int32)
            results['MOVEMENT_FRAME_TAILBASE'] = FeatureExtractionMixin.framewise_euclidean_distance(location_1=tailbase_arr, location_2=shifted_[[f'{TAIL_BASE}_x', f'{TAIL_BASE}_y']].values.astype(np.float32), px_per_mm=px_per_mm).astype(np.int32)
            results['MOVEMENT_FRAME_TAILTIP'] = FeatureExtractionMixin.framewise_euclidean_distance(location_1=tail_tip_arr, location_2=shifted_[[f'{TAIL_TIP}_x', f'{TAIL_TIP}_y']].values.astype(np.float32), px_per_mm=px_per_mm).astype(np.int32)
            results['MOVEMENT_FRAME_SUMMED'] = results['MOVEMENT_FRAME_NOSE'] + results['MOVEMENT_FRAME_CENTER'] + results['MOVEMENT_FRAME_TAILBASE'] + results['MOVEMENT_FRAME_TAILTIP']
            results['MOVEMENT_NOSE_ACCELERATION_MM_S'] = TimeseriesFeatureMixin.acceleration(data=results['MOVEMENT_FRAME_NOSE'].values.astype(np.float32), pixels_per_mm=px_per_mm, fps=fps)
            results['MOVEMENT_CENTER_ACCELERATION_MM_S'] = TimeseriesFeatureMixin.acceleration(data=results['MOVEMENT_FRAME_CENTER'].values.astype(np.float32), pixels_per_mm=px_per_mm, fps=fps)
            results['MOVEMENT_TAILBASE_ACCELERATION_MM_S'] = TimeseriesFeatureMixin.acceleration(data=results['MOVEMENT_FRAME_TAILBASE'].values.astype(np.float32), pixels_per_mm=px_per_mm, fps=fps)

            for time, bp in product(TIME_WINDOWS, [NOSE, CENTER]):
                results[f'MOVEMENT_MEAN_{time}_{bp.upper()}'] = results[f'MOVEMENT_FRAME_{bp.upper()}'].rolling(int(time * fps), min_periods=1).mean()
                results[f'MOVEMENT_VAR_{time}_{bp.upper()}'] = results[f'MOVEMENT_FRAME_{bp.upper()}'].rolling(int(time * fps), min_periods=1).var()
                results[f'MOVEMENT_SUM_{time}_{bp.upper()}'] = results[f'MOVEMENT_FRAME_{bp.upper()}'].rolling(int(time * fps), min_periods=1).sum()






            # p_df = pd.DataFrame(FeatureExtractionMixin.count_values_in_range(data=p_arr, ranges=np.array([[0.0, 0.25], [0.25, 0.50], [0.50, 0.75], [0.75, 1.0]])), columns=['PROBABILITIES_LOW_COUNT', 'PROBABILITIES_MEDIUM_LOW_COUNT', 'PROBABILITIES_MEDIUM_HIGHT', 'PROBABILITIES_HIGH_COUNT']).astype(np.int32)
            # results = pd.concat([results, p_df], axis=1)






            #results['FRAME_CENTER_MOVEMENT'] = FeatureExtractionMixin.framewise_euclidean_distance(location_1=tailbase_arr, location_2=tail_tip_arr, px_per_mm=px_per_mm).astype(np.int32)






            #results['FRAMEWISE_ANIMAL_WIDTH'] = FeatureExtractionMixin.framewise_euclidean_distance(location_1=lat_left_arr, location_2=lat_right_arr, px_per_mm=px_per_mm).astype(np.int32)







            #





feature_extractor = MitraFeatureExtractor(config_path='/Users/simon/Desktop/envs/simba/troubleshooting/mitra/project_folder/project_config.ini')
feature_extractor.run()








