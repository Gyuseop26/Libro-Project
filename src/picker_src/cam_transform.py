import numpy as np

def transform_camera_to_tcp(p_cam):
    A = np.array([
        [15.6641054,    1.3221995,   34.3771869],
        [-904.698134,   -0.5504132,  -14.3107434],
        [57.1679473,    3.1798668,   82.6765372]
    ])
    b = np.array([132.2199498, -55.0413206, 317.9866815])
    return np.dot(A, p_cam) + b
