from typing import Dict

from numpy import array, mean, median, nan, unique
from scipy.interpolate import interp1d

"""
Марочник сталей и сплавов.
2-е изд., исправл. и доп. / Зубченко А.С., Колосков М.М., Каширский Ю.В. и др. Под ред. А.С. Зубченко.
М.: Машиностроение, 2003. 784 с.
"""
data = (
    {"d10mm": 2.30, "HB": 712, "HRA": 85.1, "HRC": 66.4, "HRB": nan, "HV": 1016.0, "HSD": 98.3},
    {"d10mm": 2.31, "HB": 706, "HRA": 84.9, "HRC": 66.0, "HRB": nan, "HV": 999.0, "HSD": 97.8},
    {"d10mm": 2.32, "HB": 700, "HRA": 84.7, "HRC": 65.7, "HRB": nan, "HV": 983.0, "HSD": 97.4},
    {"d10mm": 2.33, "HB": 694, "HRA": 84.5, "HRC": 65.3, "HRB": nan, "HV": 967.0, "HSD": 96.9},
    {"d10mm": 2.34, "HB": 688, "HRA": 84.3, "HRC": 65.0, "HRB": nan, "HV": 951.0, "HSD": 96.3},
    {"d10mm": 2.35, "HB": 682, "HRA": 84.1, "HRC": 64.6, "HRB": nan, "HV": 936.0, "HSD": 95.8},
    {"d10mm": 2.36, "HB": 676, "HRA": 83.9, "HRC": 64.3, "HRB": nan, "HV": 922.0, "HSD": 95.3},
    {"d10mm": 2.37, "HB": 670, "HRA": 83.6, "HRC": 63.9, "HRB": nan, "HV": 907.0, "HSD": 94.7},
    {"d10mm": 2.38, "HB": 665, "HRA": 83.4, "HRC": 63.6, "HRB": nan, "HV": 893.0, "HSD": 94.1},
    {"d10mm": 2.39, "HB": 659, "HRA": 83.2, "HRC": 63.2, "HRB": nan, "HV": 880.0, "HSD": 93.5},
    {"d10mm": 2.40, "HB": 653, "HRA": 83.0, "HRC": 62.9, "HRB": nan, "HV": 866.0, "HSD": 92.9},
    {"d10mm": 2.41, "HB": 648, "HRA": 82.8, "HRC": 62.5, "HRB": nan, "HV": 853.0, "HSD": 92.3},
    {"d10mm": 2.42, "HB": 643, "HRA": 82.6, "HRC": 62.1, "HRB": nan, "HV": 841.0, "HSD": 91.7},
    {"d10mm": 2.43, "HB": 637, "HRA": 82.4, "HRC": 61.8, "HRB": nan, "HV": 828.0, "HSD": 91.1},
    {"d10mm": 2.44, "HB": 632, "HRA": 82.2, "HRC": 61.4, "HRB": nan, "HV": 816.0, "HSD": 90.4},
    {"d10mm": 2.45, "HB": 627, "HRA": 82.0, "HRC": 61.1, "HRB": nan, "HV": 804.0, "HSD": 89.8},
    {"d10mm": 2.46, "HB": 621, "HRA": 81.8, "HRC": 60.7, "HRB": nan, "HV": 793.0, "HSD": 89.1},
    {"d10mm": 2.47, "HB": 616, "HRA": 81.6, "HRC": 60.4, "HRB": nan, "HV": 782.0, "HSD": 88.5},
    {"d10mm": 2.48, "HB": 611, "HRA": 81.4, "HRC": 60.0, "HRB": nan, "HV": 771.0, "HSD": 87.8},
    {"d10mm": 2.49, "HB": 606, "HRA": 81.3, "HRC": 59.7, "HRB": nan, "HV": 760.0, "HSD": 87.2},
    {"d10mm": 2.50, "HB": 601, "HRA": 81.1, "HRC": 59.3, "HRB": nan, "HV": 750.0, "HSD": 86.5},
    {"d10mm": 2.51, "HB": 597, "HRA": 80.9, "HRC": 59.0, "HRB": nan, "HV": 739.0, "HSD": 85.9},
    {"d10mm": 2.52, "HB": 592, "HRA": 80.7, "HRC": 58.6, "HRB": nan, "HV": 730.0, "HSD": 85.2},
    {"d10mm": 2.53, "HB": 587, "HRA": 80.5, "HRC": 58.3, "HRB": nan, "HV": 720.0, "HSD": 84.5},
    {"d10mm": 2.54, "HB": 582, "HRA": 80.3, "HRC": 57.9, "HRB": nan, "HV": 710.0, "HSD": 83.9},
    {"d10mm": 2.55, "HB": 578, "HRA": 80.1, "HRC": 57.6, "HRB": nan, "HV": 701.0, "HSD": 83.2},
    {"d10mm": 2.56, "HB": 573, "HRA": 79.9, "HRC": 57.2, "HRB": nan, "HV": 692.0, "HSD": 82.6},
    {"d10mm": 2.57, "HB": 569, "HRA": 79.7, "HRC": 56.9, "HRB": nan, "HV": 683.0, "HSD": 81.9},
    {"d10mm": 2.58, "HB": 564, "HRA": 79.6, "HRC": 56.5, "HRB": nan, "HV": 675.0, "HSD": 81.3},
    {"d10mm": 2.59, "HB": 560, "HRA": 79.4, "HRC": 56.2, "HRB": nan, "HV": 666.0, "HSD": 80.6},
    {"d10mm": 2.60, "HB": 555, "HRA": 79.2, "HRC": 55.8, "HRB": nan, "HV": 658.0, "HSD": 80.0},
    {"d10mm": 2.61, "HB": 551, "HRA": 79.0, "HRC": 55.5, "HRB": nan, "HV": 650.0, "HSD": 79.3},
    {"d10mm": 2.62, "HB": 547, "HRA": 78.8, "HRC": 55.1, "HRB": nan, "HV": 643.0, "HSD": 78.7},
    {"d10mm": 2.63, "HB": 542, "HRA": 78.6, "HRC": 54.8, "HRB": nan, "HV": 635.0, "HSD": 78.0},
    {"d10mm": 2.64, "HB": 538, "HRA": 78.5, "HRC": 54.5, "HRB": nan, "HV": 627.0, "HSD": 77.4},
    {"d10mm": 2.65, "HB": 534, "HRA": 78.3, "HRC": 54.1, "HRB": nan, "HV": 620.0, "HSD": 76.8},
    {"d10mm": 2.66, "HB": 530, "HRA": 78.1, "HRC": 53.8, "HRB": nan, "HV": 613.0, "HSD": 76.2},
    {"d10mm": 2.67, "HB": 526, "HRA": 77.9, "HRC": 53.5, "HRB": nan, "HV": 606.0, "HSD": 75.6},
    {"d10mm": 2.68, "HB": 522, "HRA": 77.7, "HRC": 53.1, "HRB": nan, "HV": 599.0, "HSD": 74.9},
    {"d10mm": 2.69, "HB": 518, "HRA": 77.6, "HRC": 52.8, "HRB": nan, "HV": 593.0, "HSD": 74.3},
    {"d10mm": 2.70, "HB": 514, "HRA": 77.4, "HRC": 52.5, "HRB": nan, "HV": 586.0, "HSD": 73.7},
    {"d10mm": 2.71, "HB": 510, "HRA": 77.2, "HRC": 52.2, "HRB": nan, "HV": 580.0, "HSD": 73.2},
    {"d10mm": 2.72, "HB": 506, "HRA": 77.0, "HRC": 51.8, "HRB": nan, "HV": 574.0, "HSD": 72.6},
    {"d10mm": 2.73, "HB": 503, "HRA": 76.9, "HRC": 51.5, "HRB": nan, "HV": 568.0, "HSD": 72.0},
    {"d10mm": 2.74, "HB": 499, "HRA": 76.7, "HRC": 51.2, "HRB": nan, "HV": 562.0, "HSD": 71.4},
    {"d10mm": 2.75, "HB": 495, "HRA": 76.5, "HRC": 50.9, "HRB": nan, "HV": 556.0, "HSD": 70.9},
    {"d10mm": 2.76, "HB": 492, "HRA": 76.4, "HRC": 50.6, "HRB": nan, "HV": 550.0, "HSD": 70.3},
    {"d10mm": 2.77, "HB": 488, "HRA": 76.2, "HRC": 50.3, "HRB": nan, "HV": 544.0, "HSD": 69.8},
    {"d10mm": 2.78, "HB": 484, "HRA": 76.0, "HRC": 50.0, "HRB": nan, "HV": 539.0, "HSD": 69.2},
    {"d10mm": 2.79, "HB": 481, "HRA": 75.8, "HRC": 49.7, "HRB": nan, "HV": 534.0, "HSD": 68.7},
    {"d10mm": 2.80, "HB": 477, "HRA": 75.7, "HRC": 49.4, "HRB": nan, "HV": 528.0, "HSD": 68.1},
    {"d10mm": 2.81, "HB": 474, "HRA": 75.5, "HRC": 49.1, "HRB": nan, "HV": 523.0, "HSD": 67.6},
    {"d10mm": 2.82, "HB": 470, "HRA": 75.4, "HRC": 48.8, "HRB": nan, "HV": 518.0, "HSD": 67.1},
    {"d10mm": 2.83, "HB": 467, "HRA": 75.2, "HRC": 48.5, "HRB": nan, "HV": 513.0, "HSD": 66.6},
    {"d10mm": 2.84, "HB": 464, "HRA": 75.0, "HRC": 48.2, "HRB": nan, "HV": 508.0, "HSD": 66.1},
    {"d10mm": 2.85, "HB": 460, "HRA": 74.9, "HRC": 47.9, "HRB": nan, "HV": 504.0, "HSD": 65.6},
    {"d10mm": 2.86, "HB": 457, "HRA": 74.7, "HRC": 47.6, "HRB": nan, "HV": 499.0, "HSD": 65.1},
    {"d10mm": 2.87, "HB": 454, "HRA": 74.6, "HRC": 47.3, "HRB": nan, "HV": 494.0, "HSD": 64.6},
    {"d10mm": 2.88, "HB": 451, "HRA": 74.4, "HRC": 47.0, "HRB": nan, "HV": 490.0, "HSD": 64.1},
    {"d10mm": 2.89, "HB": 447, "HRA": 74.2, "HRC": 46.8, "HRB": nan, "HV": 485.0, "HSD": 63.7},
    {"d10mm": 2.90, "HB": 444, "HRA": 74.1, "HRC": 46.5, "HRB": nan, "HV": 481.0, "HSD": 63.2},
    {"d10mm": 2.91, "HB": 441, "HRA": 73.9, "HRC": 46.2, "HRB": nan, "HV": 477.0, "HSD": 62.7},
    {"d10mm": 2.92, "HB": 438, "HRA": 73.8, "HRC": 45.9, "HRB": nan, "HV": 473.0, "HSD": 62.3},
    {"d10mm": 2.93, "HB": 435, "HRA": 73.6, "HRC": 45.7, "HRB": nan, "HV": 468.0, "HSD": 61.8},
    {"d10mm": 2.94, "HB": 432, "HRA": 73.5, "HRC": 45.4, "HRB": nan, "HV": 464.0, "HSD": 61.4},
    {"d10mm": 2.95, "HB": 429, "HRA": 73.3, "HRC": 45.1, "HRB": nan, "HV": 460.0, "HSD": 61.0},
    {"d10mm": 2.96, "HB": 426, "HRA": 73.2, "HRC": 44.9, "HRB": nan, "HV": 456.0, "HSD": 60.5},
    {"d10mm": 2.97, "HB": 423, "HRA": 73.0, "HRC": 44.6, "HRB": nan, "HV": 453.0, "HSD": 60.1},
    {"d10mm": 2.98, "HB": 420, "HRA": 72.9, "HRC": 44.4, "HRB": nan, "HV": 449.0, "HSD": 59.7},
    {"d10mm": 2.99, "HB": 417, "HRA": 72.7, "HRC": 44.1, "HRB": nan, "HV": 445.0, "HSD": 59.3},
    {"d10mm": 3.00, "HB": 415, "HRA": 72.6, "HRC": 43.8, "HRB": nan, "HV": 441.0, "HSD": 58.9},
    {"d10mm": 3.01, "HB": 412, "HRA": 72.4, "HRC": 43.6, "HRB": nan, "HV": 438.0, "HSD": 58.5},
    {"d10mm": 3.02, "HB": 409, "HRA": 72.3, "HRC": 43.3, "HRB": nan, "HV": 434.0, "HSD": 58.1},
    {"d10mm": 3.03, "HB": 406, "HRA": 72.2, "HRC": 43.1, "HRB": nan, "HV": 431.0, "HSD": 57.7},
    {"d10mm": 3.04, "HB": 403, "HRA": 72.0, "HRC": 42.9, "HRB": nan, "HV": 427.0, "HSD": 57.3},
    {"d10mm": 3.05, "HB": 401, "HRA": 71.9, "HRC": 42.6, "HRB": nan, "HV": 424.0, "HSD": 56.9},
    {"d10mm": 3.06, "HB": 398, "HRA": 71.8, "HRC": 42.4, "HRB": nan, "HV": 420.0, "HSD": 56.5},
    {"d10mm": 3.07, "HB": 395, "HRA": 71.6, "HRC": 42.1, "HRB": nan, "HV": 417.0, "HSD": 56.2},
    {"d10mm": 3.08, "HB": 393, "HRA": 71.5, "HRC": 41.9, "HRB": nan, "HV": 414.0, "HSD": 56.8},
    {"d10mm": 3.09, "HB": 390, "HRA": 71.3, "HRC": 41.7, "HRB": nan, "HV": 411.0, "HSD": 55.4},
    {"d10mm": 3.10, "HB": 388, "HRA": 71.2, "HRC": 41.4, "HRB": nan, "HV": 408.0, "HSD": 55.1},
    {"d10mm": 3.11, "HB": 385, "HRA": 71.1, "HRC": 41.2, "HRB": nan, "HV": 404.0, "HSD": 54.7},
    {"d10mm": 3.12, "HB": 383, "HRA": 71.0, "HRC": 40.9, "HRB": nan, "HV": 401.0, "HSD": 54.4},
    {"d10mm": 3.13, "HB": 380, "HRA": 70.8, "HRC": 40.7, "HRB": nan, "HV": 398.0, "HSD": 54.0},
    {"d10mm": 3.14, "HB": 378, "HRA": 70.7, "HRC": 40.5, "HRB": nan, "HV": 395.0, "HSD": 53.7},
    {"d10mm": 3.15, "HB": 375, "HRA": 70.6, "HRC": 40.3, "HRB": nan, "HV": 392.0, "HSD": 53.3},
    {"d10mm": 3.16, "HB": 373, "HRA": 70.4, "HRC": 40.0, "HRB": nan, "HV": 389.0, "HSD": 53.0},
    {"d10mm": 3.17, "HB": 370, "HRA": 70.3, "HRC": 39.8, "HRB": nan, "HV": 386.0, "HSD": 52.7},
    {"d10mm": 3.18, "HB": 368, "HRA": 70.2, "HRC": 39.6, "HRB": nan, "HV": 384.0, "HSD": 52.3},
    {"d10mm": 3.19, "HB": 366, "HRA": 70.1, "HRC": 39.3, "HRB": nan, "HV": 381.0, "HSD": 52.0},
    {"d10mm": 3.20, "HB": 363, "HRA": 70.0, "HRC": 39.1, "HRB": nan, "HV": 378.0, "HSD": 51.7},
    {"d10mm": 3.21, "HB": 361, "HRA": 69.8, "HRC": 38.9, "HRB": nan, "HV": 375.0, "HSD": 51.4},
    {"d10mm": 3.22, "HB": 359, "HRA": 69.7, "HRC": 38.7, "HRB": nan, "HV": 372.0, "HSD": 51.1},
    {"d10mm": 3.23, "HB": 356, "HRA": 69.6, "HRC": 38.5, "HRB": nan, "HV": 370.0, "HSD": 50.8},
    {"d10mm": 3.24, "HB": 354, "HRA": 69.5, "HRC": 38.2, "HRB": nan, "HV": 367.0, "HSD": 50.4},
    {"d10mm": 3.25, "HB": 352, "HRA": 69.4, "HRC": 38.0, "HRB": nan, "HV": 364.0, "HSD": 50.1},
    {"d10mm": 3.26, "HB": 350, "HRA": 69.2, "HRC": 37.8, "HRB": nan, "HV": 362.0, "HSD": 49.8},
    {"d10mm": 3.27, "HB": 347, "HRA": 69.1, "HRC": 37.6, "HRB": nan, "HV": 359.0, "HSD": 49.5},
    {"d10mm": 3.28, "HB": 345, "HRA": 69.0, "HRC": 37.4, "HRB": nan, "HV": 357.0, "HSD": 49.2},
    {"d10mm": 3.29, "HB": 343, "HRA": 68.9, "HRC": 37.1, "HRB": nan, "HV": 354.0, "HSD": 48.9},
    {"d10mm": 3.30, "HB": 341, "HRA": 68.8, "HRC": 36.9, "HRB": nan, "HV": 352.0, "HSD": 48.6},
    {"d10mm": 3.31, "HB": 339, "HRA": 68.7, "HRC": 36.7, "HRB": nan, "HV": 349.0, "HSD": 48.4},
    {"d10mm": 3.32, "HB": 337, "HRA": 68.6, "HRC": 36.5, "HRB": nan, "HV": 347.0, "HSD": 48.1},
    {"d10mm": 3.33, "HB": 335, "HRA": 68.5, "HRC": 36.3, "HRB": nan, "HV": 344.0, "HSD": 47.8},
    {"d10mm": 3.34, "HB": 333, "HRA": 68.4, "HRC": 36.0, "HRB": nan, "HV": 342.0, "HSD": 47.5},
    {"d10mm": 3.35, "HB": 331, "HRA": 68.2, "HRC": 35.8, "HRB": nan, "HV": 340.0, "HSD": 47.2},
    {"d10mm": 3.36, "HB": 329, "HRA": 68.1, "HRC": 35.6, "HRB": nan, "HV": 337.0, "HSD": 46.9},
    {"d10mm": 3.37, "HB": 327, "HRA": 68.0, "HRC": 35.4, "HRB": nan, "HV": 335.0, "HSD": 46.6},
    {"d10mm": 3.38, "HB": 325, "HRA": 67.9, "HRC": 35.2, "HRB": nan, "HV": 333.0, "HSD": 46.4},
    {"d10mm": 3.39, "HB": 323, "HRA": 67.8, "HRC": 34.9, "HRB": nan, "HV": 331.0, "HSD": 46.1},
    {"d10mm": 3.40, "HB": 321, "HRA": 67.7, "HRC": 34.7, "HRB": nan, "HV": 328.0, "HSD": 45.8},
    {"d10mm": 3.41, "HB": 319, "HRA": 67.6, "HRC": 34.5, "HRB": nan, "HV": 326.0, "HSD": 45.5},
    {"d10mm": 3.42, "HB": 317, "HRA": 67.5, "HRC": 34.3, "HRB": nan, "HV": 324.0, "HSD": 45.3},
    {"d10mm": 3.43, "HB": 315, "HRA": 67.4, "HRC": 34.1, "HRB": nan, "HV": 322.0, "HSD": 45.0},
    {"d10mm": 3.44, "HB": 313, "HRA": 67.3, "HRC": 33.8, "HRB": nan, "HV": 320.0, "HSD": 44.7},
    {"d10mm": 3.45, "HB": 311, "HRA": 67.2, "HRC": 33.6, "HRB": nan, "HV": 317.0, "HSD": 44.5},
    {"d10mm": 3.46, "HB": 309, "HRA": 67.1, "HRC": 33.4, "HRB": nan, "HV": 315.0, "HSD": 44.2},
    {"d10mm": 3.47, "HB": 307, "HRA": 67.0, "HRC": 33.2, "HRB": nan, "HV": 313.0, "HSD": 44.0},
    {"d10mm": 3.48, "HB": 306, "HRA": 66.9, "HRC": 33.0, "HRB": nan, "HV": 311.0, "HSD": 43.7},
    {"d10mm": 3.49, "HB": 304, "HRA": 66.8, "HRC": 32.7, "HRB": nan, "HV": 309.0, "HSD": 43.4},
    {"d10mm": 3.50, "HB": 302, "HRA": 66.7, "HRC": 32.5, "HRB": nan, "HV": 307.0, "HSD": 43.2},
    {"d10mm": 3.51, "HB": 300, "HRA": 66.6, "HRC": 32.3, "HRB": nan, "HV": 305.0, "HSD": 42.9},
    {"d10mm": 3.52, "HB": 298, "HRA": 66.5, "HRC": 32.1, "HRB": nan, "HV": 303.0, "HSD": 42.7},
    {"d10mm": 3.53, "HB": 297, "HRA": 66.4, "HRC": 31.9, "HRB": nan, "HV": 301.0, "HSD": 42.4},
    {"d10mm": 3.54, "HB": 295, "HRA": 66.3, "HRC": 31.6, "HRB": nan, "HV": 299.0, "HSD": 42.2},
    {"d10mm": 3.55, "HB": 293, "HRA": 66.2, "HRC": 31.4, "HRB": nan, "HV": 298.0, "HSD": 41.9},
    {"d10mm": 3.56, "HB": 292, "HRA": 66.1, "HRC": 31.2, "HRB": nan, "HV": 296.0, "HSD": 41.7},
    {"d10mm": 3.57, "HB": 290, "HRA": 66.0, "HRC": 31.0, "HRB": nan, "HV": 294.0, "HSD": 41.4},
    {"d10mm": 3.58, "HB": 288, "HRA": 65.9, "HRC": 30.8, "HRB": nan, "HV": 292.0, "HSD": 41.2},
    {"d10mm": 3.59, "HB": 287, "HRA": 65.8, "HRC": 30.5, "HRB": nan, "HV": 290.0, "HSD": 40.9},
    {"d10mm": 3.60, "HB": 285, "HRA": 65.7, "HRC": 30.3, "HRB": nan, "HV": 288.0, "HSD": 40.7},
    {"d10mm": 3.61, "HB": 283, "HRA": 65.6, "HRC": 30.1, "HRB": nan, "HV": 286.0, "HSD": 40.5},
    {"d10mm": 3.62, "HB": 282, "HRA": 65.5, "HRC": 29.9, "HRB": nan, "HV": 285.0, "HSD": 40.2},
    {"d10mm": 3.63, "HB": 280, "HRA": 65.5, "HRC": 29.7, "HRB": nan, "HV": 283.0, "HSD": 40.0},
    {"d10mm": 3.64, "HB": 278, "HRA": 65.4, "HRC": 29.4, "HRB": nan, "HV": 281.0, "HSD": 39.7},
    {"d10mm": 3.65, "HB": 277, "HRA": 65.3, "HRC": 29.2, "HRB": nan, "HV": 280.0, "HSD": 39.5},
    {"d10mm": 3.66, "HB": 275, "HRA": 65.2, "HRC": 29.0, "HRB": nan, "HV": 278.0, "HSD": 39.3},
    {"d10mm": 3.67, "HB": 274, "HRA": 65.1, "HRC": 28.8, "HRB": nan, "HV": 276.0, "HSD": 39.1},
    {"d10mm": 3.68, "HB": 272, "HRA": 65.0, "HRC": 28.6, "HRB": nan, "HV": 274.0, "HSD": 38.8},
    {"d10mm": 3.69, "HB": 271, "HRA": 64.9, "HRC": 28.3, "HRB": nan, "HV": 273.0, "HSD": 38.6},
    {"d10mm": 3.70, "HB": 269, "HRA": 64.8, "HRC": 28.1, "HRB": nan, "HV": 271.0, "HSD": 38.4},
    {"d10mm": 3.71, "HB": 268, "HRA": 64.7, "HRC": 27.9, "HRB": nan, "HV": 270.0, "HSD": 38.1},
    {"d10mm": 3.72, "HB": 266, "HRA": 64.6, "HRC": 27.7, "HRB": nan, "HV": 268.0, "HSD": 37.9},
    {"d10mm": 3.73, "HB": 265, "HRA": 64.5, "HRC": 27.5, "HRB": nan, "HV": 266.0, "HSD": 37.7},
    {"d10mm": 3.74, "HB": 263, "HRA": 64.4, "HRC": 27.3, "HRB": nan, "HV": 265.0, "HSD": 37.5},
    {"d10mm": 3.75, "HB": 262, "HRA": 64.3, "HRC": 27.1, "HRB": nan, "HV": 263.0, "HSD": 37.3},
    {"d10mm": 3.76, "HB": 260, "HRA": 64.2, "HRC": 26.8, "HRB": nan, "HV": 262.0, "HSD": 37.1},
    {"d10mm": 3.77, "HB": 259, "HRA": 64.1, "HRC": 26.6, "HRB": nan, "HV": 260.0, "HSD": 36.8},
    {"d10mm": 3.78, "HB": 257, "HRA": 64.0, "HRC": 26.4, "HRB": nan, "HV": 259.0, "HSD": 36.6},
    {"d10mm": 3.79, "HB": 256, "HRA": 63.9, "HRC": 26.2, "HRB": nan, "HV": 257.0, "HSD": 36.4},
    {"d10mm": 3.80, "HB": 255, "HRA": 63.8, "HRC": 26.0, "HRB": nan, "HV": 256.0, "HSD": 36.2},
    {"d10mm": 3.81, "HB": 253, "HRA": 63.7, "HRC": 25.8, "HRB": nan, "HV": 254.0, "HSD": 36.0},
    {"d10mm": 3.82, "HB": 252, "HRA": 63.6, "HRC": 25.6, "HRB": nan, "HV": 253.0, "HSD": 35.8},
    {"d10mm": 3.83, "HB": 251, "HRA": 63.5, "HRC": 25.4, "HRB": nan, "HV": 251.0, "HSD": 35.6},
    {"d10mm": 3.84, "HB": 249, "HRA": 63.4, "HRC": 25.2, "HRB": nan, "HV": 250.0, "HSD": 35.4},
    {"d10mm": 3.85, "HB": 248, "HRA": 63.3, "HRC": 25.0, "HRB": nan, "HV": 249.0, "HSD": 35.2},
    {"d10mm": 3.86, "HB": 246, "HRA": 63.2, "HRC": 24.8, "HRB": nan, "HV": 247.0, "HSD": 35.0},
    {"d10mm": 3.87, "HB": 245, "HRA": 63.1, "HRC": 24.6, "HRB": nan, "HV": 246.0, "HSD": 34.8},
    {"d10mm": 3.88, "HB": 244, "HRA": 63.0, "HRC": 24.4, "HRB": 100.0, "HV": 244.0, "HSD": 34.6},
    {"d10mm": 3.89, "HB": 243, "HRA": 62.9, "HRC": 24.2, "HRB": 99.9, "HV": 243.0, "HSD": 34.4},
    {"d10mm": 3.90, "HB": 241, "HRA": 62.8, "HRC": 24.0, "HRB": 99.8, "HV": 242.0, "HSD": 34.2},
    {"d10mm": 3.91, "HB": 240, "HRA": 62.7, "HRC": 23.8, "HRB": 99.6, "HV": 240.0, "HSD": 34.1},
    {"d10mm": 3.92, "HB": 239, "HRA": 62.6, "HRC": 23.6, "HRB": 99.5, "HV": 239.0, "HSD": 33.9},
    {"d10mm": 3.93, "HB": 237, "HRA": 62.5, "HRC": 23.4, "HRB": 99.3, "HV": 238.0, "HSD": 33.7},
    {"d10mm": 3.94, "HB": 236, "HRA": 62.4, "HRC": 23.2, "HRB": 99.2, "HV": 237.0, "HSD": 33.5},
    {"d10mm": 3.95, "HB": 235, "HRA": 62.3, "HRC": 23.0, "HRB": 99.0, "HV": 235.0, "HSD": 33.3},
    {"d10mm": 3.96, "HB": 234, "HRA": 62.2, "HRC": 22.8, "HRB": 98.9, "HV": 234.0, "HSD": 33.1},
    {"d10mm": 3.97, "HB": 232, "HRA": 62.1, "HRC": 22.6, "HRB": 98.7, "HV": 233.0, "HSD": 33.0},
    {"d10mm": 3.98, "HB": 231, "HRA": 62.0, "HRC": 22.4, "HRB": 98.6, "HV": 231.0, "HSD": 32.8},
    {"d10mm": 3.99, "HB": 230, "HRA": 61.9, "HRC": 22.2, "HRB": 98.4, "HV": 230.0, "HSD": 32.6},
    {"d10mm": 4.00, "HB": 229, "HRA": 61.8, "HRC": 22.0, "HRB": 98.2, "HV": 229.0, "HSD": 32.5},
    {"d10mm": 4.01, "HB": 228, "HRA": 61.7, "HRC": 21.8, "HRB": 98.1, "HV": 228.0, "HSD": 32.3},
    {"d10mm": 4.02, "HB": 226, "HRA": 61.6, "HRC": 21.6, "HRB": 97.9, "HV": 227.0, "HSD": 32.1},
    {"d10mm": 4.03, "HB": 225, "HRA": 61.5, "HRC": 21.5, "HRB": 97.7, "HV": 225.0, "HSD": 32.0},
    {"d10mm": 4.04, "HB": 224, "HRA": 61.4, "HRC": 21.3, "HRB": 97.6, "HV": 224.0, "HSD": 31.8},
    {"d10mm": 4.05, "HB": 223, "HRA": 61.3, "HRC": 21.1, "HRB": 97.4, "HV": 223.0, "HSD": 31.6},
    {"d10mm": 4.06, "HB": 222, "HRA": 61.1, "HRC": 20.9, "HRB": 97.2, "HV": 222.0, "HSD": 31.5},
    {"d10mm": 4.07, "HB": 221, "HRA": 61.0, "HRC": 20.7, "HRB": 97.0, "HV": 221.0, "HSD": 31.3},
    {"d10mm": 4.08, "HB": 219, "HRA": 60.9, "HRC": 20.5, "HRB": 96.9, "HV": 219.0, "HSD": 31.2},
    {"d10mm": 4.09, "HB": 218, "HRA": 60.8, "HRC": 20.3, "HRB": 96.7, "HV": 218.0, "HSD": 31.0},
    {"d10mm": 4.10, "HB": 217, "HRA": 60.7, "HRC": 20.1, "HRB": 96.5, "HV": 217.0, "HSD": 30.9},
    {"d10mm": 4.11, "HB": 216, "HRA": 60.6, "HRC": 19.9, "HRB": 96.3, "HV": 216.0, "HSD": 30.7},
    {"d10mm": 4.12, "HB": 215, "HRA": 60.5, "HRC": 19.7, "HRB": 96.1, "HV": 215.0, "HSD": 30.6},
    {"d10mm": 4.13, "HB": 214, "HRA": 60.4, "HRC": 19.5, "HRB": 95.9, "HV": 214.0, "HSD": 30.4},
    {"d10mm": 4.14, "HB": 213, "HRA": 60.3, "HRC": 19.2, "HRB": 95.7, "HV": 213.0, "HSD": 30.3},
    {"d10mm": 4.15, "HB": 212, "HRA": 60.1, "HRC": 19.0, "HRB": 95.5, "HV": 212.0, "HSD": 30.1},
    {"d10mm": 4.16, "HB": 211, "HRA": 60.0, "HRC": 18.8, "HRB": 95.4, "HV": 211.0, "HSD": 30.0},
    {"d10mm": 4.17, "HB": 210, "HRA": 59.9, "HRC": 18.6, "HRB": 95.2, "HV": 209.0, "HSD": 29.8},
    {"d10mm": 4.18, "HB": 209, "HRA": 59.8, "HRC": 18.3, "HRB": 95.0, "HV": 208.0, "HSD": 29.7},
    {"d10mm": 4.19, "HB": 208, "HRA": 59.7, "HRC": 18.1, "HRB": 94.8, "HV": 207.0, "HSD": 29.6},
    {"d10mm": 4.20, "HB": 206, "HRA": 59.6, "HRC": 17.9, "HRB": 94.6, "HV": 206.0, "HSD": 29.4},
    {"d10mm": 4.21, "HB": 205, "HRA": 59.4, "HRC": nan, "HRB": 94.4, "HV": 205.0, "HSD": 29.3},
    {"d10mm": 4.22, "HB": 204, "HRA": 59.3, "HRC": nan, "HRB": 94.2, "HV": 204.0, "HSD": 29.2},
    {"d10mm": 4.23, "HB": 203, "HRA": 59.2, "HRC": nan, "HRB": 94.0, "HV": 203.0, "HSD": 29.0},
    {"d10mm": 4.24, "HB": 202, "HRA": 59.1, "HRC": nan, "HRB": 93.8, "HV": 202.0, "HSD": 28.9},
    {"d10mm": 4.25, "HB": 201, "HRA": 59.0, "HRC": nan, "HRB": 93.6, "HV": 201.0, "HSD": 28.8},
    {"d10mm": 4.26, "HB": 200, "HRA": 58.8, "HRC": nan, "HRB": 93.4, "HV": 200.0, "HSD": 28.6},
    {"d10mm": 4.27, "HB": 199, "HRA": 58.7, "HRC": nan, "HRB": 93.2, "HV": 199.0, "HSD": 28.5},
    {"d10mm": 4.28, "HB": 198, "HRA": 58.6, "HRC": nan, "HRB": 93.0, "HV": 198.0, "HSD": 28.4},
    {"d10mm": 4.29, "HB": 197, "HRA": 58.5, "HRC": nan, "HRB": 92.8, "HV": 197.0, "HSD": 28.3},
    {"d10mm": 4.30, "HB": 197, "HRA": 58.4, "HRC": nan, "HRB": 92.6, "HV": 196.0, "HSD": 28.1},
    {"d10mm": 4.31, "HB": 196, "HRA": 58.2, "HRC": nan, "HRB": 92.4, "HV": 195.0, "HSD": 28.0},
    {"d10mm": 4.32, "HB": 195, "HRA": 58.1, "HRC": nan, "HRB": 92.2, "HV": 194.0, "HSD": 27.9},
    {"d10mm": 4.33, "HB": 194, "HRA": 58.0, "HRC": nan, "HRB": 92.0, "HV": 193.0, "HSD": 27.8},
    {"d10mm": 4.34, "HB": 193, "HRA": 57.9, "HRC": nan, "HRB": 91.8, "HV": 192.0, "HSD": 27.6},
    {"d10mm": 4.35, "HB": 192, "HRA": 57.7, "HRC": nan, "HRB": 91.6, "HV": 191.0, "HSD": 27.5},
    {"d10mm": 4.36, "HB": 191, "HRA": 57.6, "HRC": nan, "HRB": 91.3, "HV": 190.0, "HSD": 27.4},
    {"d10mm": 4.37, "HB": 190, "HRA": 57.5, "HRC": nan, "HRB": 91.1, "HV": 189.0, "HSD": 27.3},
    {"d10mm": 4.38, "HB": 189, "HRA": 57.4, "HRC": nan, "HRB": 90.9, "HV": 188.0, "HSD": 27.2},
    {"d10mm": 4.39, "HB": 188, "HRA": 57.2, "HRC": nan, "HRB": 90.7, "HV": 187.0, "HSD": 27.0},
    {"d10mm": 4.40, "HB": 187, "HRA": 57.1, "HRC": nan, "HRB": 90.5, "HV": 186.0, "HSD": 26.9},
    {"d10mm": 4.41, "HB": 186, "HRA": 57.0, "HRC": nan, "HRB": 90.3, "HV": 185.0, "HSD": 26.8},
    {"d10mm": 4.42, "HB": 185, "HRA": 56.9, "HRC": nan, "HRB": 90.1, "HV": 184.0, "HSD": 26.7},
    {"d10mm": 4.43, "HB": 185, "HRA": 56.8, "HRC": nan, "HRB": 89.9, "HV": 183.0, "HSD": 26.6},
    {"d10mm": 4.44, "HB": 184, "HRA": 56.6, "HRC": nan, "HRB": 89.7, "HV": 183.0, "HSD": 26.4},
    {"d10mm": 4.45, "HB": 183, "HRA": 56.5, "HRC": nan, "HRB": 89.5, "HV": 182.0, "HSD": 26.3},
    {"d10mm": 4.46, "HB": 182, "HRA": 56.4, "HRC": nan, "HRB": 89.3, "HV": 181.0, "HSD": 26.2},
    {"d10mm": 4.47, "HB": 181, "HRA": 56.3, "HRC": nan, "HRB": 89.1, "HV": 180.0, "HSD": 26.1},
    {"d10mm": 4.48, "HB": 180, "HRA": 56.1, "HRC": nan, "HRB": 88.8, "HV": 179.0, "HSD": 26.0},
    {"d10mm": 4.49, "HB": 179, "HRA": 56.0, "HRC": nan, "HRB": 88.6, "HV": 178.0, "HSD": 25.8},
    {"d10mm": 4.50, "HB": 179, "HRA": 55.9, "HRC": nan, "HRB": 88.4, "HV": 177.0, "HSD": 25.7},
    {"d10mm": 4.51, "HB": 178, "HRA": 55.8, "HRC": nan, "HRB": 88.2, "HV": 176.0, "HSD": 25.6},
    {"d10mm": 4.52, "HB": 177, "HRA": 55.6, "HRC": nan, "HRB": 88.0, "HV": 175.0, "HSD": 25.5},
    {"d10mm": 4.53, "HB": 176, "HRA": 55.5, "HRC": nan, "HRB": 87.8, "HV": 175.0, "HSD": 25.3},
    {"d10mm": 4.54, "HB": 175, "HRA": 55.4, "HRC": nan, "HRB": 87.6, "HV": 174.0, "HSD": 25.2},
    {"d10mm": 4.55, "HB": 174, "HRA": 55.3, "HRC": nan, "HRB": 87.4, "HV": 173.0, "HSD": 25.1},
    {"d10mm": 4.56, "HB": 174, "HRA": 55.1, "HRC": nan, "HRB": 87.1, "HV": 172.0, "HSD": 25.0},
    {"d10mm": 4.57, "HB": 173, "HRA": 55.0, "HRC": nan, "HRB": 86.9, "HV": 171.0, "HSD": 24.9},
    {"d10mm": 4.58, "HB": 172, "HRA": 54.9, "HRC": nan, "HRB": 86.7, "HV": 171.0, "HSD": 24.7},
    {"d10mm": 4.59, "HB": 171, "HRA": 54.8, "HRC": nan, "HRB": 86.5, "HV": 170.0, "HSD": 24.6},
    {"d10mm": 4.60, "HB": 170, "HRA": 54.6, "HRC": nan, "HRB": 86.3, "HV": 169.0, "HSD": 24.5},
    {"d10mm": 4.61, "HB": 170, "HRA": 54.5, "HRC": nan, "HRB": 86.1, "HV": 168.0, "HSD": 24.4},
    {"d10mm": 4.62, "HB": 169, "HRA": 54.4, "HRC": nan, "HRB": 85.9, "HV": 167.0, "HSD": 24.2},
    {"d10mm": 4.63, "HB": 168, "HRA": 54.3, "HRC": nan, "HRB": 85.6, "HV": 167.0, "HSD": 24.1},
    {"d10mm": 4.64, "HB": 167, "HRA": 54.1, "HRC": nan, "HRB": 85.4, "HV": 166.0, "HSD": 24.0},
    {"d10mm": 4.65, "HB": 167, "HRA": 54.0, "HRC": nan, "HRB": 85.2, "HV": 165.0, "HSD": 23.9},
    {"d10mm": 4.66, "HB": 166, "HRA": 53.9, "HRC": nan, "HRB": 85.0, "HV": 164.0, "HSD": 23.7},
    {"d10mm": 4.67, "HB": 165, "HRA": 53.8, "HRC": nan, "HRB": 84.8, "HV": 164.0, "HSD": 23.6},
    {"d10mm": 4.68, "HB": 164, "HRA": 53.6, "HRC": nan, "HRB": 84.6, "HV": 163.0, "HSD": 23.5},
    {"d10mm": 4.69, "HB": 164, "HRA": 53.5, "HRC": nan, "HRB": 84.3, "HV": 162.0, "HSD": 23.4},
    {"d10mm": 4.70, "HB": 163, "HRA": 53.4, "HRC": nan, "HRB": 84.1, "HV": 162.0, "HSD": 23.2},
    {"d10mm": 4.71, "HB": 162, "HRA": 53.3, "HRC": nan, "HRB": 83.9, "HV": 161.0, "HSD": 23.1},
    {"d10mm": 4.72, "HB": 161, "HRA": 53.2, "HRC": nan, "HRB": 83.7, "HV": 160.0, "HSD": 23.0},
    {"d10mm": 4.73, "HB": 161, "HRA": 53.0, "HRC": nan, "HRB": 83.5, "HV": 160.0, "HSD": 22.9},
    {"d10mm": 4.74, "HB": 160, "HRA": 52.9, "HRC": nan, "HRB": 83.2, "HV": 159.0, "HSD": 22.7},
    {"d10mm": 4.75, "HB": 159, "HRA": 52.8, "HRC": nan, "HRB": 83.0, "HV": 158.0, "HSD": 22.6},
    {"d10mm": 4.76, "HB": 158, "HRA": 52.7, "HRC": nan, "HRB": 82.8, "HV": 158.0, "HSD": 22.5},
    {"d10mm": 4.77, "HB": 158, "HRA": 52.6, "HRC": nan, "HRB": 82.6, "HV": 157.0, "HSD": 22.4},
    {"d10mm": 4.78, "HB": 157, "HRA": 52.4, "HRC": nan, "HRB": 82.4, "HV": 156.0, "HSD": 22.3},
    {"d10mm": 4.79, "HB": 156, "HRA": 52.3, "HRC": nan, "HRB": 82.1, "HV": 156.0, "HSD": 22.1},
    {"d10mm": 4.80, "HB": 156, "HRA": 52.2, "HRC": nan, "HRB": 81.9, "HV": 155.0, "HSD": 22.0},
    {"d10mm": 4.81, "HB": 155, "HRA": 52.1, "HRC": nan, "HRB": 81.7, "HV": 154.0, "HSD": 21.9},
    {"d10mm": 4.82, "HB": 154, "HRA": 52.0, "HRC": nan, "HRB": 81.5, "HV": 154.0, "HSD": 21.8},
    {"d10mm": 4.83, "HB": 154, "HRA": 51.8, "HRC": nan, "HRB": 81.3, "HV": 153.0, "HSD": 21.7},
    {"d10mm": 4.84, "HB": 153, "HRA": 51.7, "HRC": nan, "HRB": 81.0, "HV": 153.0, "HSD": 21.6},
    {"d10mm": 4.85, "HB": 152, "HRA": 51.6, "HRC": nan, "HRB": 80.8, "HV": 152.0, "HSD": 21.5},
    {"d10mm": 4.86, "HB": 152, "HRA": 51.5, "HRC": nan, "HRB": 80.6, "HV": 151.0, "HSD": 21.4},
    {"d10mm": 4.87, "HB": 151, "HRA": 51.3, "HRC": nan, "HRB": 80.4, "HV": 151.0, "HSD": 21.3},
    {"d10mm": 4.88, "HB": 150, "HRA": 51.2, "HRC": nan, "HRB": 80.1, "HV": 150.0, "HSD": 21.2},
    {"d10mm": 4.89, "HB": 150, "HRA": 51.1, "HRC": nan, "HRB": 79.9, "HV": 150.0, "HSD": 21.1},
    {"d10mm": 4.90, "HB": 149, "HRA": 51.0, "HRC": nan, "HRB": 79.7, "HV": 149.0, "HSD": 21.0},
    {"d10mm": 4.91, "HB": 148, "HRA": 50.9, "HRC": nan, "HRB": 79.5, "HV": 148.0, "HSD": 21.0},
    {"d10mm": 4.92, "HB": 148, "HRA": 50.7, "HRC": nan, "HRB": 79.2, "HV": 148.0, "HSD": 20.9},
    {"d10mm": 4.93, "HB": 147, "HRA": 50.6, "HRC": nan, "HRB": 79.0, "HV": 147.0, "HSD": 20.8},
    {"d10mm": 4.94, "HB": 146, "HRA": 50.5, "HRC": nan, "HRB": 78.8, "HV": 146.0, "HSD": 20.8},
    {"d10mm": 4.95, "HB": 146, "HRA": 50.4, "HRC": nan, "HRB": 78.6, "HV": 146.0, "HSD": 20.7},
    {"d10mm": 4.96, "HB": 145, "HRA": 50.2, "HRC": nan, "HRB": 78.3, "HV": 145.0, "HSD": 20.7},
    {"d10mm": 4.97, "HB": 144, "HRA": 50.1, "HRC": nan, "HRB": 78.1, "HV": 144.0, "HSD": 20.7},
    {"d10mm": 4.98, "HB": 144, "HRA": 50.0, "HRC": nan, "HRB": 77.9, "HV": 144.0, "HSD": 20.6},
    {"d10mm": 4.99, "HB": 143, "HRA": 49.8, "HRC": nan, "HRB": 77.6, "HV": 143.0, "HSD": 20.6},
    {"d10mm": 5.00, "HB": 143, "HRA": nan, "HRC": nan, "HRB": 77.4, "HV": 143.0, "HSD": 20.6},
    {"d10mm": 5.01, "HB": 142, "HRA": nan, "HRC": nan, "HRB": 77.2, "HV": 142.0, "HSD": nan},
    {"d10mm": 5.02, "HB": 141, "HRA": nan, "HRC": nan, "HRB": 77.0, "HV": 141.0, "HSD": nan},
    {"d10mm": 5.03, "HB": 141, "HRA": nan, "HRC": nan, "HRB": 76.7, "HV": 141.0, "HSD": nan},
    {"d10mm": 5.04, "HB": 140, "HRA": nan, "HRC": nan, "HRB": 76.5, "HV": 140.0, "HSD": nan},
    {"d10mm": 5.05, "HB": 140, "HRA": nan, "HRC": nan, "HRB": 76.3, "HV": 140.0, "HSD": nan},
    {"d10mm": 5.06, "HB": 139, "HRA": nan, "HRC": nan, "HRB": 76.0, "HV": 139.0, "HSD": nan},
    {"d10mm": 5.07, "HB": 138, "HRA": nan, "HRC": nan, "HRB": 75.8, "HV": 138.0, "HSD": nan},
    {"d10mm": 5.08, "HB": 138, "HRA": nan, "HRC": nan, "HRB": 75.6, "HV": 138.0, "HSD": nan},
    {"d10mm": 5.09, "HB": 137, "HRA": nan, "HRC": nan, "HRB": 75.3, "HV": 137.0, "HSD": nan},
    {"d10mm": 5.10, "HB": 137, "HRA": nan, "HRC": nan, "HRB": 75.1, "HV": 137.0, "HSD": nan},
    {"d10mm": 5.11, "HB": 136, "HRA": nan, "HRC": nan, "HRB": 74.8, "HV": 136.0, "HSD": nan},
    {"d10mm": 5.12, "HB": 136, "HRA": nan, "HRC": nan, "HRB": 74.6, "HV": 136.0, "HSD": nan},
    {"d10mm": 5.13, "HB": 135, "HRA": nan, "HRC": nan, "HRB": 74.4, "HV": 135.0, "HSD": nan},
    {"d10mm": 5.14, "HB": 134, "HRA": nan, "HRC": nan, "HRB": 74.1, "HV": 134.0, "HSD": nan},
    {"d10mm": 5.15, "HB": 134, "HRA": nan, "HRC": nan, "HRB": 73.9, "HV": 134.0, "HSD": nan},
    {"d10mm": 5.16, "HB": 133, "HRA": nan, "HRC": nan, "HRB": 73.7, "HV": 133.0, "HSD": nan},
    {"d10mm": 5.17, "HB": 133, "HRA": nan, "HRC": nan, "HRB": 73.4, "HV": 133.0, "HSD": nan},
    {"d10mm": 5.18, "HB": 132, "HRA": nan, "HRC": nan, "HRB": 73.2, "HV": 132.0, "HSD": nan},
    {"d10mm": 5.19, "HB": 132, "HRA": nan, "HRC": nan, "HRB": 72.9, "HV": 132.0, "HSD": nan},
    {"d10mm": 5.20, "HB": 131, "HRA": nan, "HRC": nan, "HRB": 72.7, "HV": 131.0, "HSD": nan},
    {"d10mm": 5.21, "HB": 131, "HRA": nan, "HRC": nan, "HRB": 72.4, "HV": 131.0, "HSD": nan},
    {"d10mm": 5.22, "HB": 130, "HRA": nan, "HRC": nan, "HRB": 72.2, "HV": 130.0, "HSD": nan},
    {"d10mm": 5.23, "HB": 129, "HRA": nan, "HRC": nan, "HRB": 72.0, "HV": 129.0, "HSD": nan},
    {"d10mm": 5.24, "HB": 129, "HRA": nan, "HRC": nan, "HRB": 71.7, "HV": 129.0, "HSD": nan},
    {"d10mm": 5.25, "HB": 128, "HRA": nan, "HRC": nan, "HRB": 71.5, "HV": 128.0, "HSD": nan},
    {"d10mm": 5.26, "HB": 128, "HRA": nan, "HRC": nan, "HRB": 71.2, "HV": 128.0, "HSD": nan},
    {"d10mm": 5.27, "HB": 127, "HRA": nan, "HRC": nan, "HRB": 71.0, "HV": 127.0, "HSD": nan},
    {"d10mm": 5.28, "HB": 127, "HRA": nan, "HRC": nan, "HRB": 70.7, "HV": 127.0, "HSD": nan},
    {"d10mm": 5.29, "HB": 126, "HRA": nan, "HRC": nan, "HRB": 70.5, "HV": 126.0, "HSD": nan},
    {"d10mm": 5.30, "HB": 126, "HRA": nan, "HRC": nan, "HRB": 70.2, "HV": 126.0, "HSD": nan},
    {"d10mm": 5.31, "HB": 125, "HRA": nan, "HRC": nan, "HRB": 70.0, "HV": 125.0, "HSD": nan},
    {"d10mm": 5.32, "HB": 125, "HRA": nan, "HRC": nan, "HRB": 69.7, "HV": 125.0, "HSD": nan},
    {"d10mm": 5.33, "HB": 124, "HRA": nan, "HRC": nan, "HRB": 69.5, "HV": 124.0, "HSD": nan},
    {"d10mm": 5.34, "HB": 124, "HRA": nan, "HRC": nan, "HRB": 69.2, "HV": 124.0, "HSD": nan},
    {"d10mm": 5.35, "HB": 123, "HRA": nan, "HRC": nan, "HRB": 69.0, "HV": 123.0, "HSD": nan},
    {"d10mm": 5.36, "HB": 123, "HRA": nan, "HRC": nan, "HRB": 68.7, "HV": 123.0, "HSD": nan},
    {"d10mm": 5.37, "HB": 122, "HRA": nan, "HRC": nan, "HRB": 68.5, "HV": 122.0, "HSD": nan},
    {"d10mm": 5.38, "HB": 122, "HRA": nan, "HRC": nan, "HRB": 68.2, "HV": 122.0, "HSD": nan},
    {"d10mm": 5.39, "HB": 121, "HRA": nan, "HRC": nan, "HRB": 68.0, "HV": 121.0, "HSD": nan},
    {"d10mm": 5.40, "HB": 121, "HRA": nan, "HRC": nan, "HRB": 67.7, "HV": 121.0, "HSD": nan},
    {"d10mm": 5.41, "HB": 120, "HRA": nan, "HRC": nan, "HRB": 67.5, "HV": 120.0, "HSD": nan},
    {"d10mm": 5.42, "HB": 120, "HRA": nan, "HRC": nan, "HRB": 67.2, "HV": 120.0, "HSD": nan},
    {"d10mm": 5.43, "HB": 119, "HRA": nan, "HRC": nan, "HRB": 67.0, "HV": 119.0, "HSD": nan},
    {"d10mm": 5.44, "HB": 119, "HRA": nan, "HRC": nan, "HRB": 66.7, "HV": 119.0, "HSD": nan},
    {"d10mm": 5.45, "HB": 118, "HRA": nan, "HRC": nan, "HRB": 66.4, "HV": 118.0, "HSD": nan},
    {"d10mm": 5.46, "HB": 118, "HRA": nan, "HRC": nan, "HRB": 66.2, "HV": 118.0, "HSD": nan},
    {"d10mm": 5.47, "HB": 117, "HRA": nan, "HRC": nan, "HRB": 65.9, "HV": 117.0, "HSD": nan},
    {"d10mm": 5.48, "HB": 117, "HRA": nan, "HRC": nan, "HRB": 65.7, "HV": 117.0, "HSD": nan},
    {"d10mm": 5.49, "HB": 116, "HRA": nan, "HRC": nan, "HRB": 65.4, "HV": 116.0, "HSD": nan},
    {"d10mm": 5.50, "HB": 116, "HRA": nan, "HRC": nan, "HRB": 65.2, "HV": 116.0, "HSD": nan},
    {"d10mm": 5.51, "HB": 115, "HRA": nan, "HRC": nan, "HRB": 64.9, "HV": 115.0, "HSD": nan},
    {"d10mm": 5.52, "HB": 115, "HRA": nan, "HRC": nan, "HRB": 64.6, "HV": 115.0, "HSD": nan},
    {"d10mm": 5.53, "HB": 115, "HRA": nan, "HRC": nan, "HRB": 64.4, "HV": 115.0, "HSD": nan},
    {"d10mm": 5.54, "HB": 114, "HRA": nan, "HRC": nan, "HRB": 64.1, "HV": 114.0, "HSD": nan},
    {"d10mm": 5.55, "HB": 114, "HRA": nan, "HRC": nan, "HRB": 63.9, "HV": 114.0, "HSD": nan},
    {"d10mm": 5.56, "HB": 113, "HRA": nan, "HRC": nan, "HRB": 63.6, "HV": 113.0, "HSD": nan},
    {"d10mm": 5.57, "HB": 113, "HRA": nan, "HRC": nan, "HRB": 63.3, "HV": 113.0, "HSD": nan},
    {"d10mm": 5.58, "HB": 112, "HRA": nan, "HRC": nan, "HRB": 63.1, "HV": 112.0, "HSD": nan},
    {"d10mm": 5.59, "HB": 112, "HRA": nan, "HRC": nan, "HRB": 62.8, "HV": 112.0, "HSD": nan},
    {"d10mm": 5.60, "HB": 111, "HRA": nan, "HRC": nan, "HRB": 62.6, "HV": 111.0, "HSD": nan},
    {"d10mm": 5.61, "HB": 111, "HRA": nan, "HRC": nan, "HRB": 62.3, "HV": 111.0, "HSD": nan},
    {"d10mm": 5.62, "HB": 111, "HRA": nan, "HRC": nan, "HRB": 62.0, "HV": 111.0, "HSD": nan},
    {"d10mm": 5.63, "HB": 110, "HRA": nan, "HRC": nan, "HRB": 61.8, "HV": 110.0, "HSD": nan},
    {"d10mm": 5.64, "HB": 110, "HRA": nan, "HRC": nan, "HRB": 61.5, "HV": 110.0, "HSD": nan},
    {"d10mm": 5.65, "HB": 109, "HRA": nan, "HRC": nan, "HRB": 61.2, "HV": 109.0, "HSD": nan},
    {"d10mm": 5.66, "HB": 109, "HRA": nan, "HRC": nan, "HRB": 61.0, "HV": 109.0, "HSD": nan},
    {"d10mm": 5.67, "HB": 108, "HRA": nan, "HRC": nan, "HRB": 60.7, "HV": 108.0, "HSD": nan},
    {"d10mm": 5.68, "HB": 108, "HRA": nan, "HRC": nan, "HRB": 60.5, "HV": 108.0, "HSD": nan},
    {"d10mm": 5.69, "HB": 108, "HRA": nan, "HRC": nan, "HRB": 60.2, "HV": 108.0, "HSD": nan},
    {"d10mm": 5.70, "HB": 107, "HRA": nan, "HRC": nan, "HRB": 59.9, "HV": 107.0, "HSD": nan},
    {"d10mm": 5.71, "HB": 107, "HRA": nan, "HRC": nan, "HRB": 59.7, "HV": 107.0, "HSD": nan},
    {"d10mm": 5.72, "HB": 106, "HRA": nan, "HRC": nan, "HRB": 59.4, "HV": 106.0, "HSD": nan},
    {"d10mm": 5.73, "HB": 106, "HRA": nan, "HRC": nan, "HRB": 59.1, "HV": 106.0, "HSD": nan},
    {"d10mm": 5.74, "HB": 105, "HRA": nan, "HRC": nan, "HRB": 58.9, "HV": 105.0, "HSD": nan},
    {"d10mm": 5.75, "HB": 105, "HRA": nan, "HRC": nan, "HRB": 58.6, "HV": 105.0, "HSD": nan},
    {"d10mm": 5.76, "HB": 105, "HRA": nan, "HRC": nan, "HRB": 58.3, "HV": 105.0, "HSD": nan},
    {"d10mm": 5.77, "HB": 104, "HRA": nan, "HRC": nan, "HRB": 58.1, "HV": 104.0, "HSD": nan},
    {"d10mm": 5.78, "HB": 104, "HRA": nan, "HRC": nan, "HRB": 57.8, "HV": 104.0, "HSD": nan},
    {"d10mm": 5.79, "HB": 103, "HRA": nan, "HRC": nan, "HRB": 57.5, "HV": 103.0, "HSD": nan},
    {"d10mm": 5.80, "HB": 103, "HRA": nan, "HRC": nan, "HRB": 57.3, "HV": 103.0, "HSD": nan},
    {"d10mm": 5.81, "HB": 103, "HRA": nan, "HRC": nan, "HRB": 57.0, "HV": 103.0, "HSD": nan},
    {"d10mm": 5.82, "HB": 102, "HRA": nan, "HRC": nan, "HRB": 56.8, "HV": 102.0, "HSD": nan},
    {"d10mm": 5.83, "HB": 102, "HRA": nan, "HRC": nan, "HRB": 56.5, "HV": 102.0, "HSD": nan},
    {"d10mm": 5.84, "HB": 101, "HRA": nan, "HRC": nan, "HRB": 56.2, "HV": 101.0, "HSD": nan},
    {"d10mm": 5.85, "HB": 101, "HRA": nan, "HRC": nan, "HRB": 56.0, "HV": 101.0, "HSD": nan},
    {"d10mm": 5.86, "HB": 101, "HRA": nan, "HRC": nan, "HRB": 55.7, "HV": 101.0, "HSD": nan},
    {"d10mm": 5.87, "HB": 100, "HRA": nan, "HRC": nan, "HRB": 55.4, "HV": 100.0, "HSD": nan},
    {"d10mm": 5.88, "HB": 100, "HRA": nan, "HRC": nan, "HRB": 55.2, "HV": 100.0, "HSD": nan},
    {"d10mm": 5.89, "HB": 100, "HRA": nan, "HRC": nan, "HRB": 54.9, "HV": 100.0, "HSD": nan},
    {"d10mm": 5.90, "HB": 99, "HRA": nan, "HRC": nan, "HRB": 54.6, "HV": nan, "HSD": nan},
    {"d10mm": 5.91, "HB": 99, "HRA": nan, "HRC": nan, "HRB": 54.4, "HV": nan, "HSD": nan},
    {"d10mm": 5.92, "HB": 98, "HRA": nan, "HRC": nan, "HRB": 54.1, "HV": nan, "HSD": nan},
    {"d10mm": 5.93, "HB": 98, "HRA": nan, "HRC": nan, "HRB": 53.9, "HV": nan, "HSD": nan},
    {"d10mm": 5.94, "HB": 98, "HRA": nan, "HRC": nan, "HRB": 53.6, "HV": nan, "HSD": nan},
    {"d10mm": 5.95, "HB": 97, "HRA": nan, "HRC": nan, "HRB": 53.3, "HV": nan, "HSD": nan},
    {"d10mm": 5.96, "HB": 97, "HRA": nan, "HRC": nan, "HRB": 53.1, "HV": nan, "HSD": nan},
    {"d10mm": 5.97, "HB": 97, "HRA": nan, "HRC": nan, "HRB": 52.8, "HV": nan, "HSD": nan},
    {"d10mm": 5.98, "HB": 96, "HRA": nan, "HRC": nan, "HRB": 52.5, "HV": nan, "HSD": nan},
    {"d10mm": 5.99, "HB": 96, "HRA": nan, "HRC": nan, "HRB": 52.3, "HV": nan, "HSD": nan},
    {"d10mm": 6.00, "HB": 95, "HRA": nan, "HRC": nan, "HRB": 52.0, "HV": nan, "HSD": nan},
    {"d10mm": 6.01, "HB": 95, "HRA": nan, "HRC": nan, "HRB": 51.8, "HV": nan, "HSD": nan},
    {"d10mm": 6.02, "HB": 95, "HRA": nan, "HRC": nan, "HRB": 51.5, "HV": nan, "HSD": nan},
    {"d10mm": 6.03, "HB": 94, "HRA": nan, "HRC": nan, "HRB": 51.2, "HV": nan, "HSD": nan},
    {"d10mm": 6.04, "HB": 94, "HRA": nan, "HRC": nan, "HRB": 51.0, "HV": nan, "HSD": nan},
    {"d10mm": 6.05, "HB": 94, "HRA": nan, "HRC": nan, "HRB": 50.7, "HV": nan, "HSD": nan},
    {"d10mm": 6.06, "HB": 93, "HRA": nan, "HRC": nan, "HRB": 50.5, "HV": nan, "HSD": nan},
    {"d10mm": 6.07, "HB": 93, "HRA": nan, "HRC": nan, "HRB": 50.2, "HV": nan, "HSD": nan},
    {"d10mm": 6.08, "HB": 93, "HRA": nan, "HRC": nan, "HRB": 50.0, "HV": nan, "HSD": nan},
    {"d10mm": 6.09, "HB": 92, "HRA": nan, "HRC": nan, "HRB": 49.7, "HV": nan, "HSD": nan},
    {"d10mm": 6.10, "HB": 92, "HRA": nan, "HRC": nan, "HRB": 49.4, "HV": nan, "HSD": nan},
    {"d10mm": 6.11, "HB": 92, "HRA": nan, "HRC": nan, "HRB": 49.2, "HV": nan, "HSD": nan},
    {"d10mm": 6.12, "HB": 91, "HRA": nan, "HRC": nan, "HRB": 48.9, "HV": nan, "HSD": nan},
    {"d10mm": 6.13, "HB": 91, "HRA": nan, "HRC": nan, "HRB": 48.7, "HV": nan, "HSD": nan},
    {"d10mm": 6.14, "HB": 91, "HRA": nan, "HRC": nan, "HRB": 48.4, "HV": nan, "HSD": nan},
    {"d10mm": 6.15, "HB": 90, "HRA": nan, "HRC": nan, "HRB": 48.2, "HV": nan, "HSD": nan},
    {"d10mm": 6.16, "HB": 90, "HRA": nan, "HRC": nan, "HRB": 47.9, "HV": nan, "HSD": nan},
    {"d10mm": 6.17, "HB": 90, "HRA": nan, "HRC": nan, "HRB": 47.7, "HV": nan, "HSD": nan},
    {"d10mm": 6.18, "HB": 89, "HRA": nan, "HRC": nan, "HRB": 47.4, "HV": nan, "HSD": nan},
    {"d10mm": 6.19, "HB": 89, "HRA": nan, "HRC": nan, "HRB": 47.2, "HV": nan, "HSD": nan},
    {"d10mm": 6.20, "HB": 89, "HRA": nan, "HRC": nan, "HRB": 46.9, "HV": nan, "HSD": nan},
    {"d10mm": 6.21, "HB": 88, "HRA": nan, "HRC": nan, "HRB": 46.7, "HV": nan, "HSD": nan},
    {"d10mm": 6.22, "HB": 88, "HRA": nan, "HRC": nan, "HRB": 46.4, "HV": nan, "HSD": nan},
    {"d10mm": 6.23, "HB": 88, "HRA": nan, "HRC": nan, "HRB": 46.2, "HV": nan, "HSD": nan},
    {"d10mm": 6.24, "HB": 87, "HRA": nan, "HRC": nan, "HRB": 45.9, "HV": nan, "HSD": nan},
    {"d10mm": 6.25, "HB": 87, "HRA": nan, "HRC": nan, "HRB": 45.7, "HV": nan, "HSD": nan},
    {"d10mm": 6.26, "HB": 87, "HRA": nan, "HRC": nan, "HRB": 45.4, "HV": nan, "HSD": nan},
    {"d10mm": 6.27, "HB": 86, "HRA": nan, "HRC": nan, "HRB": 45.2, "HV": nan, "HSD": nan},
    {"d10mm": 6.28, "HB": 86, "HRA": nan, "HRC": nan, "HRB": 44.9, "HV": nan, "HSD": nan},
    {"d10mm": 6.29, "HB": 86, "HRA": nan, "HRC": nan, "HRB": 44.7, "HV": nan, "HSD": nan},
    {"d10mm": 6.30, "HB": 85, "HRA": nan, "HRC": nan, "HRB": 44.4, "HV": nan, "HSD": nan},
    {"d10mm": 6.31, "HB": 85, "HRA": nan, "HRC": nan, "HRB": 44.2, "HV": nan, "HSD": nan},
    {"d10mm": 6.32, "HB": 85, "HRA": nan, "HRC": nan, "HRB": 43.9, "HV": nan, "HSD": nan},
    {"d10mm": 6.33, "HB": 85, "HRA": nan, "HRC": nan, "HRB": 43.7, "HV": nan, "HSD": nan},
    {"d10mm": 6.34, "HB": 84, "HRA": nan, "HRC": nan, "HRB": 43.5, "HV": nan, "HSD": nan},
    {"d10mm": 6.35, "HB": 84, "HRA": nan, "HRC": nan, "HRB": 43.2, "HV": nan, "HSD": nan},
    {"d10mm": 6.36, "HB": 84, "HRA": nan, "HRC": nan, "HRB": 43.0, "HV": nan, "HSD": nan},
    {"d10mm": 6.37, "HB": 83, "HRA": nan, "HRC": nan, "HRB": 42.7, "HV": nan, "HSD": nan},
    {"d10mm": 6.38, "HB": 83, "HRA": nan, "HRC": nan, "HRB": 42.5, "HV": nan, "HSD": nan},
    {"d10mm": 6.39, "HB": 83, "HRA": nan, "HRC": nan, "HRB": 42.2, "HV": nan, "HSD": nan},
    {"d10mm": 6.40, "HB": 82, "HRA": nan, "HRC": nan, "HRB": 42.0, "HV": nan, "HSD": nan},
    {"d10mm": 6.41, "HB": 82, "HRA": nan, "HRC": nan, "HRB": 41.8, "HV": nan, "HSD": nan},
    {"d10mm": 6.42, "HB": 82, "HRA": nan, "HRC": nan, "HRB": 41.5, "HV": nan, "HSD": nan},
    {"d10mm": 6.43, "HB": 82, "HRA": nan, "HRC": nan, "HRB": 41.3, "HV": nan, "HSD": nan},
    {"d10mm": 6.44, "HB": 81, "HRA": nan, "HRC": nan, "HRB": 41.0, "HV": nan, "HSD": nan},
    {"d10mm": 6.45, "HB": 81, "HRA": nan, "HRC": nan, "HRB": 40.8, "HV": nan, "HSD": nan},
    {"d10mm": 6.46, "HB": 81, "HRA": nan, "HRC": nan, "HRB": 40.6, "HV": nan, "HSD": nan},
    {"d10mm": 6.47, "HB": 80, "HRA": nan, "HRC": nan, "HRB": 40.3, "HV": nan, "HSD": nan},
    {"d10mm": 6.48, "HB": 80, "HRA": nan, "HRC": nan, "HRB": 40.1, "HV": nan, "HSD": nan},
    {"d10mm": 6.49, "HB": 80, "HRA": nan, "HRC": nan, "HRB": 39.8, "HV": nan, "HSD": nan},
    {"d10mm": 6.50, "HB": 80, "HRA": nan, "HRC": nan, "HRB": 39.6, "HV": nan, "HSD": nan},
    {"d10mm": 6.51, "HB": 79, "HRA": nan, "HRC": nan, "HRB": 39.4, "HV": nan, "HSD": nan},
    {"d10mm": 6.52, "HB": 79, "HRA": nan, "HRC": nan, "HRB": 39.1, "HV": nan, "HSD": nan},
    {"d10mm": 6.53, "HB": 79, "HRA": nan, "HRC": nan, "HRB": 38.9, "HV": nan, "HSD": nan},
    {"d10mm": 6.54, "HB": 79, "HRA": nan, "HRC": nan, "HRB": 38.6, "HV": nan, "HSD": nan},
    {"d10mm": 6.55, "HB": 78, "HRA": nan, "HRC": nan, "HRB": 38.4, "HV": nan, "HSD": nan},
    {"d10mm": 6.56, "HB": 78, "HRA": nan, "HRC": nan, "HRB": 38.1, "HV": nan, "HSD": nan},
    {"d10mm": 6.57, "HB": 78, "HRA": nan, "HRC": nan, "HRB": 37.9, "HV": nan, "HSD": nan},
    {"d10mm": 6.58, "HB": 78, "HRA": nan, "HRC": nan, "HRB": 37.7, "HV": nan, "HSD": nan},
    {"d10mm": 6.59, "HB": 77, "HRA": nan, "HRC": nan, "HRB": 37.4, "HV": nan, "HSD": nan},
    {"d10mm": 6.60, "HB": 77, "HRA": nan, "HRC": nan, "HRB": 37.2, "HV": nan, "HSD": nan},
    {"d10mm": 6.61, "HB": 77, "HRA": nan, "HRC": nan, "HRB": 36.9, "HV": nan, "HSD": nan},
    {"d10mm": 6.62, "HB": 77, "HRA": nan, "HRC": nan, "HRB": 36.7, "HV": nan, "HSD": nan},
    {"d10mm": 6.63, "HB": 76, "HRA": nan, "HRC": nan, "HRB": 36.4, "HV": nan, "HSD": nan},
    {"d10mm": 6.64, "HB": 76, "HRA": nan, "HRC": nan, "HRB": 36.2, "HV": nan, "HSD": nan},
    {"d10mm": 6.65, "HB": 76, "HRA": nan, "HRC": nan, "HRB": 35.9, "HV": nan, "HSD": nan},
    {"d10mm": 6.66, "HB": 76, "HRA": nan, "HRC": nan, "HRB": 35.7, "HV": nan, "HSD": nan},
    {"d10mm": 6.67, "HB": 75, "HRA": nan, "HRC": nan, "HRB": 35.4, "HV": nan, "HSD": nan},
    {"d10mm": 6.68, "HB": 75, "HRA": nan, "HRC": nan, "HRB": 35.2, "HV": nan, "HSD": nan},
    {"d10mm": 6.69, "HB": 75, "HRA": nan, "HRC": nan, "HRB": 34.9, "HV": nan, "HSD": nan},
    {"d10mm": 6.70, "HB": 75, "HRA": nan, "HRC": nan, "HRB": 34.7, "HV": nan, "HSD": nan},
)


def interpolate(x_hardness: str, y_hardness: str, strategy="mean", kind: int = 1):
    # Извлекаем данные в numpy массивы
    x_data = array([d[x_hardness] for d in data])
    y_data = array([d[y_hardness] for d in data])

    x_unique = unique(x_data)
    # Вычисляем y для каждого уникального x
    if strategy == "mean":
        y_unique = array([mean(y_data[x_data == x]) for x in x_unique])
    elif strategy == "median":
        y_unique = array([median(y_data[x_data == x]) for x in x_unique])

    return interp1d(x_unique, y_unique, kind=kind, bounds_error=False, fill_value=nan)


class Hardness:
    """Твердость"""

    __slots__ = ("HB", "HRA", "HRC", "HRB", "HV", "HSD")

    HB_HRA = interpolate("HB", "HRA", kind=1)
    HB_HRC = interpolate("HB", "HRC", kind=1)
    HB_HRB = interpolate("HB", "HRB", kind=1)
    HB_HV = interpolate("HB", "HV", kind=1)
    HB_HSD = interpolate("HB", "HSD", kind=1)

    HRA_HB = interpolate("HRA", "HB", kind=1)
    HRA_HRC = interpolate("HRA", "HRC", kind=1)
    HRA_HRB = interpolate("HRA", "HRB", kind=1)
    HRA_HV = interpolate("HRA", "HV", kind=1)
    HRA_HSD = interpolate("HRA", "HSD", kind=1)

    HRC_HB = interpolate("HRC", "HB", kind=1)
    HRC_HRA = interpolate("HRC", "HRA", kind=1)
    HRC_HRB = interpolate("HRC", "HRB", kind=1)
    HRC_HV = interpolate("HRC", "HV", kind=1)
    HRC_HSD = interpolate("HRC", "HSD", kind=1)

    HRB_HB = interpolate("HRB", "HB", kind=1)
    HRB_HRA = interpolate("HRB", "HRA", kind=1)
    HRB_HRC = interpolate("HRB", "HRC", kind=1)
    HRB_HV = interpolate("HRB", "HV", kind=1)
    HRB_HSD = interpolate("HRB", "HSD", kind=1)

    HV_HB = interpolate("HV", "HB", kind=1)
    HV_HRA = interpolate("HV", "HRA", kind=1)
    HV_HRC = interpolate("HV", "HRC", kind=1)
    HV_HRB = interpolate("HV", "HRB", kind=1)
    HV_HSD = interpolate("HV", "HSD", kind=1)

    HSD_HB = interpolate("HSD", "HB", kind=1)
    HSD_HRA = interpolate("HSD", "HRA", kind=1)
    HSD_HRC = interpolate("HSD", "HRC", kind=1)
    HSD_HRB = interpolate("HSD", "HRB", kind=1)
    HSD_HV = interpolate("HSD", "HV", kind=1)

    @classmethod
    def validate(cls, **hardness: Dict[str, float]):
        """Валидирование твердости"""
        assert len(hardness) == 1, ValueError(f"{len(hardness)=} must be 1")
        for k, v in hardness.items():
            assert k in cls.__slots__, KeyError(f"{hardness=} not in {cls.__slots__}")
            assert isinstance(v, (float, int)), TypeError(f"{type(v)=} must be float")

    def __init__(self, **hardness: Dict[str, float]):
        Hardness.validate(**hardness)
        converted = Hardness.convert(**hardness)
        for k, v in converted.items():
            setattr(self, k, v)

    @property
    def values(self) -> Dict[str, float]:
        return {k: getattr(self, k, nan) for k in self.__slots__}

    @classmethod
    def convert(cls, **hardness: Dict[str, float]) -> Dict[str, float]:
        cls.validate(**hardness)
        for k, v in hardness.items():
            assert k in cls.__slots__, KeyError(f"{hardness=} not in {cls.__slots__}")

            match k:
                case "HB":
                    return {"HB": v, "HRA": float(cls.HB_HRA(v)), "HRC": float(cls.HB_HRC(v)), "HRB": float(cls.HB_HRB(v)), "HV": float(cls.HB_HV(v)), "HSD": float(cls.HB_HSD(v))}
                case "HRA":
                    return {"HB": float(cls.HRA_HB(v)), "HRA": v, "HRC": float(cls.HRA_HRC(v)), "HRB": float(cls.HRA_HRB(v)), "HV": float(cls.HRA_HV(v)), "HSD": float(cls.HRA_HSD(v))}
                case "HRC":
                    return {"HB": float(cls.HRC_HB(v)), "HRA": float(cls.HRC_HRA(v)), "HRC": v, "HRB": float(cls.HRC_HRB(v)), "HV": float(cls.HRC_HV(v)), "HSD": float(cls.HRC_HSD(v))}
                case "HRB":
                    return {"HB": float(cls.HRB_HB(v)), "HRA": float(cls.HRB_HRA(v)), "HRC": float(cls.HRB_HRC(v)), "HRB": v, "HV": float(cls.HRB_HV(v)), "HSD": float(cls.HRB_HSD(v))}
                case "HV":
                    return {"HB": float(cls.HV_HB(v)), "HRA": float(cls.HV_HRA(v)), "HRC": float(cls.HV_HRC(v)), "HRB": float(cls.HV_HRB(v)), "HV": v, "HSD": float(cls.HV_HSD(v))}
                case "HSD":
                    return {"HB": float(cls.HSD_HB(v)), "HRA": float(cls.HSD_HRA(v)), "HRC": float(cls.HSD_HRC(v)), "HRB": float(cls.HSD_HRB(v)), "HV": float(cls.HSD_HV(v)), "HSD": v}
                case _:
                    return {}


if __name__ == "__main__":
    h = Hardness(HB=229)
    print(h.values)
    print(Hardness.convert(HB=229))
