#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
Script containing dictionnary of variables correspondance for waspmote, Permanent CR6, mobile CR6 stations. To go from METNO naming convention to faster scripting variable name

S. Filhol
'''

CR6_serials={'finse_stationnary':3668,
             'finse_mobile':744}

CR6_biomet_perm = {'BEC_99_99_3_1_1':               'bec',
                   'CS650PERIOD_99_99_3_1_1':       'cs650period',
                   'CS650VRATIO_99_99_3_1_1':       'cs650vratio',
                   'FC1DRIFTmax_99_99_1_1_1':       'fc1drift_max',
                   'FC1DRIFTmean_99_99_1_1_1':      'fc1drift_mean',
                   'FC1DRIFTmin_99_99_1_1_1':       'fc1drift_min',
                   'FC1DRIFTstd_99_99_1_1_1':       'fc1drift_std',
                   'FC1DRIFTsum_99_99_1_1_1':       'fc1drift_sum',
                   'FC1WSmax_16_99_1_1_1':          'fc1ws_max',
                   'FC1WSmean_16_99_1_1_1':         'fc1ws_mean',
                   'FC1WSmin_16_99_1_1_1':          'fc1ws_min',
                   'FC2DRIFTmax_99_99_1_1_1':       'fc2drift_max',
                   'FC2DRIFTmean_99_99_1_1_1':      'fc2drift_mean',
                   'FC2DRIFTmin_99_99_1_1_1':       'fc2drift_min',
                   'FC2DRIFTstd_99_99_1_1_1':       'fc2drift_std',
                   'FC2DRIFTsum_99_99_1_1_1':       'fc2drift_sum',
                   'FC2WSmax_16_99_1_1_1':          'fc2ws_max',
                   'FC2WSmean_16_99_1_1_1':         'fc2ws_mean',
                   'FC2WSmin_16_99_1_1_1':          'fc2ws_min',
                   'LWIN_6_14_1_1_1':               'lwin',
                   'LWOUT_6_15_1_1_1':              'lwout',
                   'METNORA_99_99_1_1_1':           'metno_ra',
                   'METNORR_99_99_1_1_1':           'metno_rr',
                   'METNOR_99_99_1_1_1':            'metno_r',
                   'METNOS_99_99_1_1_1':            'metno_s',
                   'PA_4_2_1_1_1':                  'pa',
                   'PERMITTIVITY_99_99_3_1_1':      'permittivty',
                   'RECORD':                        'record',
                   'RH_19_3_1_1_1':                 'rh',        # Check what is the difference between the two RH
                   'RH_19_3_1_2_1':                 'rh',
                   'SHF_6_37_1_1_1':                'SHF_6_37_1_1_1',
                   'SHF_6_37_2_1_1':                'SHF_6_37_2_1_1',
                   'SHF_99_37_1_1_1':               'SHF_99_37_1_1_1',
                   'SHF_99_37_1_1_2':               'SHF_99_37_1_1_2',
                   'SHF_99_37_2_1_1':               'SHF_99_37_2_1_1',
                   'SHF_99_37_2_1_2':               'SHF_99_37_2_1_2',
                   'SWC_12_36_3_1_1':               'SWC_12_36_3_1_1',
                   'SWIN_6_10_1_1_1':               'swin',
                   'SWOUT_6_11_1_1_1':              'swout',
                   'TA_2_1_1_1_1':                  'ta',
                   'TA_2_1_1_2_1':                  'ta',
                   'TSS_2_99_1_1_1':                'tsurf',
                   'TS_2_38_1_1_1':                 'ts_1',
                   'TS_2_38_2_1_1':                 'ts_2',
                   'TS_2_38_3_1_1':                 'ts_3',
                   'VIN_18_39_1_1_1':               'vin',
                   'WD_20_35_1_1_1':                'wd',
                   'WS_16_33_1_1_1':                'ws',
                   'model':                         'model',
                   'name':                          'name',
                   'os_version':                    'os_version',
                   'prog_name':                     'prog_name',
                   'prog_signature':                'prog_signature',
                   'serial':                        'serial',
                   'table_name':                    'table_name',
                   'time':                          'time',
                   }

CR6_biomet_perm_unit = {}

CR6_biomet_perm_description = {}

CR6_biomet_mobile = {
    'BEC 99 99 3 1 1':              '__',
    'CS650PERIOD 99 99 3 1 1':      '__',
    'CS650VRATIO 99 99 3 1 1':      '__',
    'LWIN 6 14 1 1 1':              'lwin',
    'LWOUT 6 15 1 1 1':             'lwout',
    'PA 4 2 1 1 1':                 'pa',
    'PERMITTIVITY 99 99 3 1 1':     'perm',
    'P RAIN 8 19 1 1 1':            'precip',
    'RECORD':                       'record',
    'RH 19 3 1 1 1':                'rh',
    'SHF 6 37 1 1 1':               'sh1',
    'SHF 6 37 2 1 1':               'sh2',
    'SHF 99 37 1 1 2':              'sh3',
    'SHF 99 37 2 1 2':              'sh4',
    'SR50DISTANCE 9 99 1 1 1':      's50_dist',
    'SR50QUALITY 99 99 1 1 1':      'sr50_qu',
    'SURFACETEMP 2 99 1 1 1':       'tsurf',
    'SWC 12 36 3 1 1':              'swc',
    'SWIN 6 10 1 1 1':              'swin',
    'SWOUT 6 11 1 1 1':             'swout',
    'TA 2 1 1 1 1':                 'ta',
    'TS 2 38 2 1 1':                'ts',
    'TS 2 38 3 1 1':                'ts',
    'VIN 18 39 1 1 1':              'vin',
}

















