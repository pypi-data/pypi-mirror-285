import unittest as unittest
import os
import numpy as np

from steam_sdk.builders.BuilderTFM import BuilderTFM
from steam_sdk.builders.BuilderLEDET import BuilderLEDET
from steam_sdk.builders.BuilderModel import BuilderModel
from tests.TestHelpers import assert_two_parameters
import matplotlib.pyplot as plt

# class TestBuilderTFM(unittest.TestCase):
#
#     def setUp(self) -> None:
#         """
#             This function is executed before each test in this class
#         """
#
#         self.current_path = os.getcwd()
#         os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
#         print('\nCurrent folder:          {}'.format(self.current_path))
#         print('\nTest is run from folder: {}'.format(os.getcwd()))
#
#         self.local_General_MBRD = {
#             'magnet_name': 'MBRD',
#             'magnet_length': 7.78,
#             'num_HalfTurns': 248,
#             'I_magnet': 1,
#             'bins': 1,
#             # 'lib_path' : "D:\\Code\\steam_sdk\\lib\\MB_TFM_General.lib"
#         }
#
#         self.local_HalfTurns_MBRD = {
#             'HalfTurns_to_group': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4,
#                                        4, 4, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 8, 8,
#                                        8, 8, 9, 9, 9, 9, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
#                                        11, 12, 12, 12, 12, 12, 12, 13, 13, 13, 13, 14, 14, 14, 14, 15, 15, 16, 16, 16,
#                                        16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 17, 18, 18,
#                                        18, 18, 19, 19, 19, 19, 20, 20, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21,
#                                        21, 21, 21, 22, 22, 22, 22, 22, 22, 23, 23, 23, 23, 24, 24, 24, 24, 25, 25, 26,
#                                        26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 27, 27, 27, 27, 27, 27,
#                                        28, 28, 28, 28, 29, 29, 29, 29, 30, 30, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31,
#                                        31, 31, 31, 31, 31, 32, 32, 32, 32, 32, 32, 33, 33, 33, 33, 34, 34, 34, 34, 35,
#                                        35, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 37, 37, 37, 37,
#                                        37, 37, 38, 38, 38, 38, 39, 39, 39, 39, 40, 40],
#             'HalfTurns_to_coil_sections': 248 * [1],
#             'HalfTurns_to_conductor': 248 * [1],
#             'n_strands': 248 * [36],
#             'rotation_ht': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
#                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 180.0, 180.0, 180.0, 180.0,
#                             180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0,
#                             180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0,
#                             180.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
#                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 180.0, 180.0, 180.0,
#                             180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0,
#                             180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0, 180.0,
#                             180.0, 180.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0,
#                             90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0,
#                             90.0, 90.0, 90.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0,
#                             270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0,
#                             270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0,
#                             90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0,
#                             90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 270.0, 270.0, 270.0, 270.0,
#                             270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0,
#                             270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0, 270.0,
#                             270.0],
#             'mirror_ht': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                           1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
#                           1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
#                           1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
#                           1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#             'alphaDEG_ht': [0.0, 0.8464, 1.6928, 2.5392, 3.3856, 4.232, 5.0784, 5.9248, 6.7712, 7.6176, 8.464, 9.3104,
#                             10.1568, 11.0032, 11.8496, 36.227, 37.0734, 37.9198, 38.7662, 39.6126, 40.459, 41.6,
#                             42.4464, 43.2928, 44.1392, 54.629, 55.4754, 56.3218, 57.1682, 71.053, 71.8994, 0.0, 0.8464,
#                             1.6928, 2.5392, 3.3856, 4.232, 5.0784, 5.9248, 6.7712, 7.6176, 8.464, 9.3104, 10.1568,
#                             11.0032, 11.8496, 33.537, 34.3834, 35.2298, 36.0762, 36.9226, 37.769, 45.218, 46.0644,
#                             46.9108, 47.7572, 50.549, 51.3954, 52.2418, 53.0882, 72.573, 73.4194, 0.0, 0.8464, 1.6928,
#                             2.5392, 3.3856, 4.232, 5.0784, 5.9248, 6.7712, 7.6176, 8.464, 9.3104, 10.1568, 11.0032,
#                             11.8496, 36.227, 37.0734, 37.9198, 38.7662, 39.6126, 40.459, 41.6, 42.4464, 43.2928,
#                             44.1392, 54.629, 55.4754, 56.3218, 57.1682, 71.053, 71.8994, 0.0, 0.8464, 1.6928, 2.5392,
#                             3.3856, 4.232, 5.0784, 5.9248, 6.7712, 7.6176, 8.464, 9.3104, 10.1568, 11.0032, 11.8496,
#                             33.537, 34.3834, 35.2298, 36.0762, 36.9226, 37.769, 45.218, 46.0644, 46.9108, 47.7572,
#                             50.549, 51.3954, 52.2418, 53.0882, 72.573, 73.4194, 0.0, 0.8464, 1.6928, 2.5392, 3.3856,
#                             4.232, 5.0784, 5.9248, 6.7712, 7.6176, 8.464, 9.3104, 10.1568, 11.0032, 11.8496, 36.227,
#                             37.0734, 37.9198, 38.7662, 39.6126, 40.459, 41.6, 42.4464, 43.2928, 44.1392, 54.629,
#                             55.4754, 56.3218, 57.1682, 71.053, 71.8994, 0.0, 0.8464, 1.6928, 2.5392, 3.3856, 4.232,
#                             5.0784, 5.9248, 6.7712, 7.6176, 8.464, 9.3104, 10.1568, 11.0032, 11.8496, 33.537, 34.3834,
#                             35.2298, 36.0762, 36.9226, 37.769, 45.218, 46.0644, 46.9108, 47.7572, 50.549, 51.3954,
#                             52.2418, 53.0882, 72.573, 73.4194, 0.0, 0.8464, 1.6928, 2.5392, 3.3856, 4.232, 5.0784,
#                             5.9248, 6.7712, 7.6176, 8.464, 9.3104, 10.1568, 11.0032, 11.8496, 36.227, 37.0734, 37.9198,
#                             38.7662, 39.6126, 40.459, 41.6, 42.4464, 43.2928, 44.1392, 54.629, 55.4754, 56.3218,
#                             57.1682, 71.053, 71.8994, 0.0, 0.8464, 1.6928, 2.5392, 3.3856, 4.232, 5.0784, 5.9248,
#                             6.7712, 7.6176, 8.464, 9.3104, 10.1568, 11.0032, 11.8496, 33.537, 34.3834, 35.2298, 36.0762,
#                             36.9226, 37.769, 45.218, 46.0644, 46.9108, 47.7572, 50.549, 51.3954, 52.2418, 53.0882,
#                             72.573, 73.4194],
#             'bare_cable_width': 248 * [0.0151],
#             'bare_cable_height_mean': 248 * [0.001476],
#             'strand_twist_pitch': 248 * [0.12],
#             'C_strand': 248 * [1.13125],
#             'Nc': [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,6,6,6,6,6,6,4,4,4,4,4,4,4,4,2,2,15,15,15,15,15,15,15,
#                    15,15,15,15,15,15,15,15,6,6,6,6,6,6,4,4,4,4,4,4,4,4,2,2,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,
#                    6,6,6,6,6,6,4,4,4,4,4,4,4,4,2,2,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,6,6,6,6,6,6,4,4,4,4,4,4,
#                    4,4,2,2,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,6,6,6,6,6,6,4,4,4,4,4,4,4,4,2,2,15,15,15,15,15,
#                    15,15,15,15,15,15,15,15,15,15,6,6,6,6,6,6,4,4,4,4,4,4,4,4,2,2,15,15,15,15,15,15,15,15,15,15,15,15,15,
#                    15,15,6,6,6,6,6,6,4,4,4,4,4,4,4,4,2,2,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,6,6,6,6,6,6,4,4,4,
#                    4,4,4,4,4,2,2],
#             'Rc': 248 * [0.0001],
#             'RRR': 248 * [200.0],
#             'diameter': 248 * [0.000825],
#             'fsc': 248 * [0.338983050847458],
#             'f_rho_effective': 248 * [2.0],
#         }
#
#         self.local_Strands_MBRD = {
#             'filament_diameter': 8928 * [6e-06],
#             'diameter': 8928 * [0.000825],
#             'd_core': 8928 * [0.00033],
#             'd_filamentary': 8928 * [0.00066],
#             'fsc': 8928 * [0.338983050847458],
#             'f_rho_effective': 8928 * [2.0],
#             'fil_twist_pitch': 8928 * [0.015],
#             'RRR': 8928 * [200.0],
#             'f_mag_X':[3.54439834e-05,3.98921162e-05,4.13775934e-05,5.26058091e-05,4.61908714e-05,5.89128631e-05,
#                              4.89875519e-05,6.21410788e-05,5.03153527e-05,6.36431535e-05,5.06390041e-05,6.40912863e-05,
#                              5.02489627e-05,6.38423237e-05,4.93526971e-05,6.31369295e-05,5.44066390e-05,7.18091286e-05,
#                              4.45145228e-05,7.03900415e-05,4.22572614e-05,5.72531120e-05,3.96348548e-05,5.50456432e-05,
#                              3.65477178e-05,5.24315353e-05,3.28547718e-05,4.92199170e-05,2.83153527e-05,4.51286307e-05,
#                              2.26224066e-05,3.96182573e-05,1.54854772e-05,3.16597510e-05,8.05809129e-06,1.91369295e-05,
#                              3.00663900e-05,3.45560166e-05,3.09626556e-05,3.96099585e-05,3.23651452e-05,4.25394191e-05,
#                              3.31369295e-05,4.42987552e-05,3.31867220e-05,4.50290456e-05,3.25975104e-05,4.49377593e-05,
#                              3.14605809e-05,4.41908714e-05,2.98755187e-05,4.29460581e-05,2.79004149e-05,4.98257261e-05,
#                              2.29875519e-05,3.69792531e-05,2.00331950e-05,3.43070539e-05,1.67302905e-05,3.12614108e-05,
#                              1.30290456e-05,2.77759336e-05,8.87966805e-06,2.37593361e-05,4.22406639e-06,1.90954357e-05,
#                              -9.54356846e-07,1.36680498e-05,-6.51452282e-06,7.40248963e-06],
#             'f_mag_Y': [-3.58838174e-04,-3.49842324e-04,-3.17029046e-04,-3.10705394e-04,-2.80531120e-04,-2.76763485e-04,
#                               -2.45692946e-04,-2.43576763e-04,-2.11742739e-04,-2.10680498e-04,-1.78406639e-04,-1.78058091e-04,
#                               -1.45609959e-04,-1.45759336e-04,-1.13344398e-04,-1.13867220e-04,-6.65228216e-05,-6.73609959e-05,
#                               -2.00414938e-05,-3.68879668e-05,9.87551867e-06,8.21576763e-06,3.91452282e-05,3.71120332e-05,
#                               6.77427386e-05,6.52199170e-05,9.56846473e-05,9.24813278e-05,1.23045643e-04,1.18829876e-04,
#                               1.50049793e-04,1.44307054e-04,1.77261411e-04,1.69344398e-04,2.07892116e-04,1.98531120e-04,
#                               -3.71643154e-04,-3.67601660e-04,-3.28522822e-04,-3.25394191e-04,-2.89593361e-04,-2.87145228e-04,
#                               -2.52414938e-04,-2.50713693e-04,-2.16564315e-04,-2.15543568e-04,-1.81759336e-04,-1.81302905e-04,
#                               -1.47817427e-04,-1.47817427e-04,-1.14622407e-04,-1.15012448e-04,-8.21078838e-05,-6.76016598e-05,
#                               -1.90622407e-05,-2.03983402e-05,1.16431535e-05,9.97510373e-06,4.18091286e-05,3.97676349e-05,
#                                7.14937759e-05,6.90124481e-05,1.00780083e-04,9.77759336e-05,1.29792531e-04,1.26182573e-04,
#                               1.58713693e-04,1.54464730e-04,1.87759336e-04,1.83020747e-04],
#             'f_mag': [3.60584402e-04,3.52109404e-04,3.19717877e-04,3.15127297e-04,2.84308470e-04,2.82964224e-04,2.50529048e-04,
#                            2.51378506e-04,2.17638742e-04,2.20083446e-04,1.85454139e-04,1.89241583e-04,1.54036419e-04,1.59127705e-04,
#                            1.23622981e-04,1.30199906e-04,8.59381647e-05,9.84583908e-05,4.88180726e-05,7.94699946e-05,4.33958755e-05,
#                            5.78395857e-05,5.57070068e-05,6.63876934e-05,7.69728154e-05,8.36821574e-05,1.01168116e-04,1.04763525e-04,
#                            1.26261592e-04,1.27110710e-04,1.51745555e-04,1.49646691e-04,1.77936527e-04,1.72278452e-04,2.08048227e-04,
#                            1.99451317e-04,3.72857374e-04,3.69222289e-04,3.29978682e-04,3.27796169e-04,2.91396324e-04,2.90279149e-04,
#                            2.54580747e-04,2.54597203e-04,2.19092358e-04,2.20196832e-04,1.84659292e-04,1.86789040e-04,1.51128290e-04,
#                            1.54281642e-04,1.18451858e-04,1.22768999e-04,8.67187277e-05,8.39796844e-05,2.98629630e-05,4.22321849e-05,
#                            2.31709285e-05,3.57278133e-05,4.50322757e-05,5.05839954e-05,7.26712875e-05,7.43923416e-05,1.01170518e-04,
#                            1.00621266e-04,1.29861249e-04,1.27619267e-04,1.58716562e-04,1.55068270e-04,1.87872316e-04,1.83170387e-04],
#             'strands_to_conductor': 8928 * [1],
#             'strands_to_coil_sections': 8928 * [1]
#         }
#         self.Ref_1Hz_PC_MB_2COILS = {
#             'L': np.array([1.4113534293557782e-05, 1.4113534293557782e-05]),
#             'I': np.array([0, 0]),
#             'M': np.array([0.00022649587037800982, 0.00015596861862097574]),
#             'M_IF_PC': 7.056767146778891e-06
#         }
#         self.Ref_1Hz_IFCC_MB_2COILS = {
#             'L': np.array([7.056767146778889e-06, 7.056767146778889e-06]),
#             'R': np.array([0.00029983536505049854, 0.00033126934916174143]),
#             'M': np.array([0.00027063848349049354, 4.85737433621831e-05]),
#             'tau': np.array([0.02110732323448026]*900 + [0.030394545457651582]*420),
#             'P': np.array([4.597781374333796e-07,4.5604831840894e-07,3.48475070917643e-07,3.457147511954569e-07,
#                            2.595841442459936e-07,2.577972617335797e-07,1.8509667681802683e-07,1.8359106050782325e-07,
#                            1.2415663817994998e-07,1.2269408552614626e-07,7.614021320630808e-08,7.466588678105002e-08,
#                            1.6485344781653275e-08,1.4912532079290158e-08,3.958317538290747e-09,2.348204126039845e-09,
#                            2.2222183248234847e-09,5.828706934382652e-10,1.0823378766757423e-08,9.164730667035756e-09,
#                            2.9349210210575436e-08,2.767771011362617e-08,5.7411658973482375e-08,5.5725512257629024e-08,
#                            9.46459615033757e-08,9.294207786005457e-08,1.4071454006531262e-07,1.3892629830743988e-07,
#                            1.9525898832635001e-07,1.932967826712839e-07,2.5800672899504535e-07,2.5557048852910016e-07,
#                            3.288851037279643e-07,3.2517238195936535e-07,4.161305298444791e-07,4.11105438425604e-07,
#                            4.7158985290113145e-07,4.6606268190551747e-07,3.5922243227044104e-07,3.532710005435703e-07,
#                            2.6947292054439823e-07,2.634695342248986e-07,1.9449799064925916e-07,1.8842661572540032e-07,
#                            1.3329875289114521e-07,1.27148743302134e-07,7.153426559966192e-08,7.889216498851403e-08,
#                            4.1936754294180897e-08,1.8820970212324697e-08,1.2675766105338801e-08,6.0975115705927755e-09,
#                            1.0773142071529182e-08,4.150992171071161e-09,1.9161293223583524e-08,1.2531422772599077e-08,
#                            3.743432498757492e-08,3.0819581476702224e-08,6.522518388685322e-08,5.864676954769787e-08,
#                            1.0220279422838099e-07,9.568000816731003e-08,1.4811151390219835e-07,1.4159453391667024e-07,
#                            2.026599790649796e-07,1.9612448764538618e-07,2.656888361192516e-07,2.5908855082151625e-07,
#                            3.370613964542803e-07,3.3051489305811554e-07,4.235768637222906e-07,4.191803829231203e-07,
#                            4.905593590419924e-07,4.797789122745928e-07,3.7777058684667903e-07])
#         }
#
#         self.Ref_1Hz_ISCC_MB_2COILS = {
#             'L': np.array([0.00018334, 0.00014281]),
#             'R': np.array([0.0013619, 0.00197378]),
#             'M': np.array([0.00010563, 0.00061684]),
#             'tau': np.array([0.13462149060180048]*25+[0.07235550852766245]*15),
#              'I': np.array([ 0.006045024336698462,0.005595413143078963,0.004734559057670826,0.0025011051617909873,
#                               -0.0004998634414116132,-0.0037858037761628596,-0.008628473742208579,-0.014011788180520113,
#                               -0.018349748877790117,0.01370099439060041,0.01136669178577134,0.008743132798888827,0.005589617278738937,
#                               0.0011652327866637075,-0.0038662480711846308,-0.010299842443451713,-0.017841001683696962,
#                               -0.02569929269639126,-0.032875915422238895,-0.040024339082874325,-0.04522960275211969,
#                               -0.050610315946474874,-0.05716199429299099,-0.06563462702609411,-0.07455124714515401,
#                               -0.3008715208699357,-0.3005840581758268,-0.300265196567742,-0.29977689070629765,-0.2988187925964383,
#                               -0.2708091645596204,-0.2747595639278176,-0.2773391426286654,-0.27871055469333605,
#                               -0.2788902013928421,-0.19865435479629376,-0.19189403169863384,-0.18275247528306085,
#                               -0.08200057004398213,-0.08252561064699415])
#         }
#
#         self.Ref_1Hz_EC_MB_2COILS = {
#             'L': np.array([1.2596357804059504e-05, 1.2838951726767645e-05]),
#             'R': np.array([0.12566636633360878, 0.08715760454931512]),
#             'M': np.array([0.00033894992750476685, 0.0005119439642037172]),
#             'P': np.array([6.406212411820049e-09,6.354243840496517e-09,4.855396859416668e-09,4.816936582545798e-09,
#                            3.616855677530615e-09,3.5919585630366725e-09,2.579001766020469e-09,2.558023609147444e-09,
#                            1.7299078224081363e-09,1.709529683038482e-09,1.0608820628222063e-09,1.0403398763292028e-09,
#                             2.2969474134394317e-10,2.0778031907151234e-10,5.5152302554615116e-11,3.2718159462080126e-11,
#                            3.0962765419269026e-11,8.121294091177654e-12,1.5080504649588233e-10,1.27694656553041e-10,
#                            4.089304371401243e-10,3.8564097686432694e-10,7.999320810515801e-10,7.764385454964789e-10,
#                             1.3187276295829139e-09,1.2949869606483834e-09,1.9606135213868716e-09,1.9356974681604843e-09,
#                            2.7205959846599643e-09,2.6932560456793956e-09,3.5948771267112355e-09,3.560932333254461e-09,
#                            4.582444579305587e-09,4.5307142286447105e-09,5.79805855952258e-09,5.728042609660692e-09]),
#             'tau': np.array([0.00010023650855488037]*900 + [0.00014730730374196057]*420)
#         }
#         self.Ref_1Hz_Wedges_MBRD ={
#             'I': 12.19295863,
#             'L': 2.42906275e-07,
#             'M': 1.89981215e-05,
#             'P': 1.43766246e-03,
#             'R': 9.67027297e-06,
#             'RRR_wedges': 50,
#             'tau': 0.025118864312161676
#         }
#
#         self.Ref_1Hz_ColdBore_MBRD ={
#             'I': 4.14835427e-02,
#             'L': 4.4605165e-06,
#             'M': 0.00026247,
#             'P': 6.84127150e-05,
#             'R': 0.0397544,
#             'tau': 0.00011220184543444465
#         }

    # def tearDown(self) -> None:
    #     """
    #         This function is executed after each test in this class
    #     """
    #     os.chdir(self.current_path)  # go back to initial folder
    #
    #
    # def test_plot(self):
    #

    # def test_BuilderTFM_init(self):
    #
    #     bTFM = BuilderTFM(flag_build=False)
    #     self.assertEqual(hasattr(bTFM, 'magnet_name'), True)
    #
    #     self.assertEqual(hasattr(bTFM, 'General'), True)
    #     self.assertEqual(hasattr(bTFM, 'HalfTurns'), True)
    #     self.assertEqual(hasattr(bTFM, 'Strands'), True)
    #     self.assertEqual(hasattr(bTFM, 'Options'), True)
    #     self.assertEqual(hasattr(bTFM, 'PC'), True)
    #     self.assertEqual(hasattr(bTFM, 'IFCC'), True)
    #     self.assertEqual(hasattr(bTFM, 'ISCC'), True)
    #     self.assertEqual(hasattr(bTFM, 'EC_CopperSheath'), True)
    #
    # def test_setAttribute(self):
    #     """
    #        **Test that setAttribute works**
    #     """
    #     bTFM = BuilderTFM(flag_build=False)
    #
    #     for parameter in self.local_General_MBRD:
    #         true_value = self.local_General_MBRD[parameter]
    #         setattr(bTFM.General, parameter, true_value)
    #         test_value = bTFM.getAttribute('General', parameter)
    #         assert_two_parameters(test_value, true_value)
    #
    #     for parameter in self.local_HalfTurns_MBRD:
    #         true_value = self.local_HalfTurns_MBRD[parameter]
    #         setattr(bTFM.HalfTurns, parameter, true_value)
    #         test_value = bTFM.getAttribute('HalfTurns', parameter)
    #         assert_two_parameters(test_value, true_value)
    #
    #     for parameter in self.local_Strands_MBRD:
    #         true_value = self.local_Strands_MBRD[parameter]
    #         setattr(bTFM.Strands, parameter, true_value)
    #         test_value = bTFM.getAttribute('Strands', parameter)
    #         assert_two_parameters(test_value, true_value)
    #
    # def test_getAttribute(self):
    #     """
    #        **Test that setAttribute works**
    #     """
    #     # arrange
    #     bTFM = BuilderTFM(flag_build=False)
    #
    #     for parameter in self.local_General_MBRD:
    #         true_value = self.local_General_MBRD[parameter]
    #         setattr(bTFM.General, parameter, true_value)
    #         # act
    #         test_value = bTFM.getAttribute('General', parameter)
    #         # assert
    #         assert_two_parameters(test_value, true_value)
    #
    #     for parameter in self.local_HalfTurns_MBRD:
    #         true_value = self.local_HalfTurns_MBRD[parameter]
    #         setattr(bTFM.HalfTurns, parameter, true_value)
    #         # act
    #         test_value = bTFM.getAttribute('HalfTurns', parameter)
    #         # assert
    #         assert_two_parameters(test_value, true_value)
    #
    #     for parameter in self.local_Strands_MBRD:
    #         true_value = self.local_Strands_MBRD[parameter]
    #         setattr(bTFM.Strands, parameter, true_value)
    #         # act
    #         test_value = bTFM.getAttribute('Strands', parameter)
    #         # assert
    #         assert_two_parameters(test_value, true_value)
    #
    #
    # def test_BuilderTFM(self):
    #     name = 'MBRD'
    #     file_model_data = os.path.join('model_library', 'magnets', name, 'input', f'modelData_{name}.yaml')
    #     bM = BuilderModel(file_model_data=file_model_data)
    #     builder_ledet = BuilderLEDET(path_input_file=bM.path_input_file, input_model_data=bM.model_data,
    #                                  input_map2d=bM.path_map2d, flag_build=True, input_roxie_data=bM.roxie_data,
    #                                  smic_write_path='skip')
    #
    #     bTFM = BuilderTFM(magnet_name=name, builder_LEDET=builder_ledet, flag_Roxie=True)
    #
    #     for attribute in self.local_General_MBRD:
    #         true_value = self.local_General_MBRD[attribute]
    #         test_value = bTFM.getAttribute('General', attribute)
    #         assert_two_parameters(true_value, test_value)
    #
    #     for attribute in self.local_HalfTurns_MBRD:
    #         true_value = self.local_HalfTurns_MBRD[attribute]
    #         test_value = bTFM.getAttribute('HalfTurns', attribute)
    #         assert_two_parameters(true_value, test_value)
    #
    #     for attribute in self.local_Strands_MBRD:
    #         true_value = self.local_Strands_MBRD[attribute]
    #         test_value = bTFM.getAttribute('Strands', attribute)
    #         if attribute == 'f_mag' or attribute == 'f_mag_X' or attribute == 'f_mag_Y':
    #             self.assertTrue(np.array_equal(np.round(np.array(true_value), 8), np.round(test_value[0, :70], 8)))
    #         else:
    #             assert_two_parameters(true_value, test_value)
    #
    #
    # def test_PC(self):
    #     name = 'MB_2COILS'
    #     file_model_data = os.path.join('model_library', 'magnets', name, 'input', f'modelData_{name}.yaml')
    #     bM= BuilderModel(file_model_data=file_model_data)
    #     builder_ledet = BuilderLEDET(path_input_file=bM.path_input_file, input_model_data=bM.model_data,
    #                                  input_map2d=bM.path_map2d, flag_build=True, input_roxie_data=bM.roxie_data,
    #                                  smic_write_path='skip')
    #     temperature = 1.9
    #
    #     bTFM = BuilderTFM(magnet_name=name, builder_LEDET=builder_ledet, flag_Roxie=True)
    #     frequency = bTFM.frequency
    #     bTFM.calculate_PC(frequency=frequency, T=temperature, fMag=bTFM.Strands.f_mag)
    #     for attribute in self.Ref_1Hz_PC_MB_2COILS:
    #         true_value = self.Ref_1Hz_PC_MB_2COILS[attribute]
    #         if attribute != 'I' and attribute != 'M_IF_PC':
    #             test_value = bTFM.getAttribute('PC', attribute)[0, :]
    #         else:
    #             test_value = bTFM.getAttribute('PC', attribute)
    #         if isinstance(true_value, np.ndarray):
    #             true_rounded = np.round(true_value, decimals=8)
    #             test_rounded = np.round(test_value, decimals=8)
    #             self.assertTrue(np.array_equal(true_rounded, test_rounded))
    #         else:
    #             assert_two_parameters(true_value, test_value)
    #
    # def test_IFCC(self):
    #     name = 'MB_2COILS'
    #     file_model_data = os.path.join('model_library', 'magnets', name, 'input', f'modelData_{name}.yaml')
    #     bM = BuilderModel(file_model_data=file_model_data)
    #     builder_ledet = BuilderLEDET(path_input_file=bM.path_input_file, input_model_data=bM.model_data,
    #                                  input_map2d=bM.path_map2d, flag_build=True, input_roxie_data=bM.roxie_data,
    #                                  smic_write_path='skip')
    #     bTFM = BuilderTFM(magnet_name=name, builder_LEDET=builder_ledet, flag_Roxie=True)
    #
    #     temperature = 1.9
    #     freq = bTFM.frequency
    #     bTFM.calculate_IFCC(frequency=freq, T=temperature, fMag=bTFM.Strands.f_mag)
    #
    #     for attribute in self.Ref_1Hz_IFCC_MB_2COILS:
    #         true_value = self.Ref_1Hz_IFCC_MB_2COILS[attribute]
    #         if attribute != 'tau':
    #             test_value = bTFM.getAttribute('IFCC', attribute)[0, :]
    #         else:
    #             test_value = bTFM.getAttribute('IFCC', attribute)
    #         if isinstance(true_value, np.ndarray):
    #             if attribute == 'P':
    #                 true_rounded = np.round(true_value, decimals=12)
    #                 test_rounded = np.round(test_value, decimals=12)
    #             else:
    #                 true_rounded = np.round(true_value, decimals=7)
    #                 test_rounded = np.round(test_value, decimals=7)
    #             if attribute == 'P':
    #                 self.assertTrue(np.array_equal(true_rounded, test_rounded[:75]))
    #             elif attribute == 'tau':
    #                 self.assertTrue(np.array_equal(true_rounded, test_rounded[:1320]))
    #             else:
    #                 self.assertTrue(np.array_equal(true_rounded, test_rounded))
    #         else:
    #             assert_two_parameters(true_value, test_value)
    #
    # def test_ISCC(self):
    #     name = 'MB_2COILS'
    #     file_model_data = os.path.join('model_library', 'magnets', name, 'input', f'modelData_{name}.yaml')
    #     bM = BuilderModel(file_model_data=file_model_data)
    #     builder_ledet = BuilderLEDET(path_input_file=bM.path_input_file, input_model_data=bM.model_data,
    #                                  input_map2d=bM.path_map2d, flag_build=True, input_roxie_data=bM.roxie_data,
    #                                  smic_write_path='skip')
    #     bTFM = BuilderTFM(magnet_name=name, builder_LEDET=builder_ledet, flag_Roxie=True)
    #
    #     temperature = 1.9
    #     freq = bTFM.frequency
    #     f_mag_X_test, f_mag_Y_test = bTFM.calculate_ISCC(frequency=freq, T=temperature, fMag_X=bTFM.Strands.f_mag_X, fMag_Y=bTFM.Strands.f_mag_Y)
    #     for attribute in self.Ref_1Hz_ISCC_MB_2COILS:
    #         true_value = self.Ref_1Hz_ISCC_MB_2COILS[attribute]
    #         if attribute != 'tau':
    #             test_value = bTFM.getAttribute('ISCC', attribute)[0, :]
    #         else:
    #             test_value = bTFM.getAttribute('ISCC', attribute)
    #         if isinstance(true_value, np.ndarray):
    #             true_rounded = np.round(true_value, decimals=8)
    #             test_rounded = np.round(test_value, decimals=8)
    #             if attribute == 'I':
    #                 test_rounded = test_rounded[:40]
    #                 self.assertTrue(np.allclose(true_rounded, test_rounded))
    #             elif attribute == 'tau':
    #                 self.assertTrue(np.array_equal(true_rounded, test_rounded[:40]))
    #             else:
    #                 self.assertTrue(np.array_equal(true_rounded, test_rounded))
    #         else:
    #             assert_two_parameters(true_value, test_value)
    #     f_mag_X_true = np.array([-5.797098936033723e-08, -6.307307920701971e-09, -6.431847121683985e-08, 5.58417707629028e-09,
    #                               -6.512194993285284e-08, 6.588525471306518e-09, -6.644768981427428e-08, 6.066264305898075e-09])
    #     f_mag_Y_true = np.array([-1.2771695930384483e-06, -1.2732727212657852e-06, -1.1111708903101643e-06, -1.1085997584189228e-06,
    #                               -9.58429586396095e-07, -9.57304716193677e-07, -8.084602840522705e-07, -8.078576750152607e-07])
    #     self.assertTrue(np.array_equal(np.round(f_mag_X_true, decimals=10), np.round(f_mag_X_test[0, :8], decimals=10)))
    #     self.assertTrue(np.array_equal(np.round(f_mag_Y_true, decimals=10), np.round(f_mag_Y_test[0, :8], decimals=10)))
    #
    # def test_EC_CopperSheath(self):
    #     name = 'MB_2COILS'
    #     file_model_data = os.path.join('model_library', 'magnets', name, 'input', f'modelData_{name}.yaml')
    #     bM = BuilderModel(file_model_data=file_model_data)
    #     builder_ledet = BuilderLEDET(path_input_file=bM.path_input_file, input_model_data=bM.model_data,
    #                                  input_map2d=bM.path_map2d, flag_build=True, input_roxie_data=bM.roxie_data,
    #                                  smic_write_path='skip')
    #     bTFM = BuilderTFM(magnet_name=name, builder_LEDET=builder_ledet, flag_Roxie=True)
    #
    #     temperature = 1.9
    #     freq = bTFM.frequency
    #     bTFM.calculate_EC_CopperSheath(frequency=freq, T=temperature, fMag=bTFM.Strands.f_mag)
    #
    #     for attribute in self.Ref_1Hz_EC_MB_2COILS:
    #         true_value = self.Ref_1Hz_EC_MB_2COILS[attribute]
    #         if attribute != 'tau':
    #             test_value = bTFM.getAttribute('EC_CopperSheath', attribute)[0, :]
    #         else:
    #             test_value = bTFM.getAttribute('EC_CopperSheath', attribute)
    #         if isinstance(true_value, np.ndarray):
    #             if attribute == 'R':
    #                 true_rounded = np.round(true_value, decimals=5)
    #                 test_rounded = np.round(test_value, decimals=5)
    #             elif attribute == 'P':
    #                 true_rounded = np.round(true_value, decimals=12)
    #                 test_rounded = np.round(test_value, decimals=12)
    #             else:
    #                 true_rounded = np.round(true_value, decimals=8)
    #                 test_rounded = np.round(test_value, decimals=8)
    #             if attribute == 'P':
    #                 self.assertTrue(np.array_equal(true_rounded, test_rounded[:36]))
    #             elif attribute == 'tau':
    #                 self.assertTrue(np.array_equal(true_rounded, test_rounded[:1320]))
    #             else:
    #                 self.assertTrue(np.array_equal(true_rounded, test_rounded))
    #         else:
    #             assert_two_parameters(true_value, test_value)
    #
    # def test_calculate_Wedges(self):
    #     name = 'MBRD'
    #     file_model_data = os.path.join('model_library', 'magnets', name, 'input', f'modelData_{name}.yaml')
    #     bM = BuilderModel(file_model_data=file_model_data)
    #     builder_ledet = BuilderLEDET(path_input_file=bM.path_input_file, input_model_data=bM.model_data,
    #                                  input_map2d=bM.path_map2d, flag_build=True, input_roxie_data=bM.roxie_data,
    #                                  smic_write_path='skip')
    #     bTFM = BuilderTFM(magnet_name=name, builder_LEDET=builder_ledet, path_input_file=bM.path_input_file, flag_Roxie=True)
    #
    #     temperature = 1.9
    #     bTFM.calculate_Wedges(T=temperature)
    #
    #     for attribute in self.Ref_1Hz_Wedges_MBRD:
    #         true_value = self.Ref_1Hz_Wedges_MBRD[attribute]
    #         test_value = bTFM.getAttribute('Wedges', attribute)
    #         if attribute != 'tau':
    #             assert_two_parameters(round(true_value, 8), round(test_value[0], 8))
    #         else:
    #             assert_two_parameters(round(true_value, 8), round(test_value, 8))
    #
    # def test_calculate_ColdBore(self):
    #     name = 'MBRD'
    #     file_model_data = os.path.join('model_library', 'magnets', name, 'input', f'modelData_{name}.yaml')
    #     bM = BuilderModel(file_model_data=file_model_data)
    #     builder_ledet = BuilderLEDET(path_input_file=bM.path_input_file, input_model_data=bM.model_data,
    #                                  input_map2d=bM.path_map2d, flag_build=True, input_roxie_data=bM.roxie_data,
    #                                  smic_write_path='skip')
    #     bTFM = BuilderTFM(magnet_name=name, builder_LEDET=builder_ledet, path_input_file=bM.path_input_file, flag_Roxie=True)
    #
    #     temperature = 1.9
    #     bTFM.calculate_ColdBore(T=temperature)
    #
    #     for attribute in self.Ref_1Hz_ColdBore_MBRD:
    #         true_value = self.Ref_1Hz_ColdBore_MBRD[attribute]
    #         test_value = bTFM.getAttribute('ColdBore', attribute)
    #         if attribute != 'tau':
    #             assert_two_parameters(round(true_value, 8), round(test_value[0], 8))
    #         else:
    #             assert_two_parameters(round(true_value, 8), round(test_value, 8))
    #
    #
    # def test_calculate_Mutual_Coupling_Wedges_CB(self):
    #     name = 'MBRD'
    #     file_model_data = os.path.join('model_library', 'magnets', name, 'input', f'modelData_{name}.yaml')
    #     bM = BuilderModel(file_model_data=file_model_data)
    #     builder_ledet = BuilderLEDET(path_input_file=bM.path_input_file, input_model_data=bM.model_data,
    #                                  input_map2d=bM.path_map2d, flag_build=True, input_roxie_data=bM.roxie_data,
    #                                  smic_write_path='skip')
    #     bTFM = BuilderTFM(magnet_name=name, builder_LEDET=builder_ledet, path_input_file=bM.path_input_file)
    #
    #     temperature = 1.9
    #     bTFM.calculate_Wedges(T=temperature)
    #     bTFM.calculate_ColdBore(T=temperature)
    #     M_Wedges_ColdBore = bTFM.calculate_MutualCoupling_ColdBore_Wedges()
    #
    #     K = M_Wedges_ColdBore/(np.sqrt(bTFM.Wedges.L*bTFM.ColdBore.L))
    #
    #     fig, ax = plt.subplots(1,1, figsize=(18,10))
    #     ax.semilogx(bTFM.frequency, K)
    #     plt.xlabel('Frequency [Hz]')
    #     plt.ylabel('Coupling Coefficient Wedges and ColdBore')
    #     plt.title('Coupling Coefficient Wedges and ColdBore in function of the frequency', fontweight='bold')
    #     plt.legend()
    #     plt.show()
    #
    #
    #     print('ciao')



