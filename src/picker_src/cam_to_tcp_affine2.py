import numpy as np

# 카메라 좌표 (단위: m → mm)
camera_points = np.array([
    [-0.04, 0.01, 0.39],
    [ 0.10, 0.02, 0.39],
    [-0.01, 0.02, 0.39],
    [ 0.04, 0.01, 0.40],
    [-0.10, 0.01, 0.39],
    [ 0.03, 0.00, 0.39],
    [-0.02, 0.01, 0.39],
    [-0.07, 0.00, 0.40],
]) * 1000  # mm로 변환

# TCP 좌표 (단위: mm, 3차원만 사용)
tcp_points = np.array([
    [145.6, -36.0, 329.7],
    [139.1, -126.9, 336.8],
    [142.8, -51.5, 330.2],
    [143.5, -83.3, 338.3],
    [142.8,   1.8, 335.7],
    [141.3, -79.4, 335.0],
    [133.9, -38.2, 342.4],
    [136.0, -15.4, 336.2],
])

# 아핀 변환 계산
X = np.hstack([camera_points, np.ones((camera_points.shape[0], 1))])  # 8x4
Y = tcp_points  # 8x3

A_ext, _, _, _ = np.linalg.lstsq(X, Y, rcond=None)

A = A_ext[:3, :].T  # 3x3 행렬
b = A_ext[3, :]     # 1x3 벡터

print("=== Affine Matrix A ===")
print(A)

print("\n=== Translation Vector b ===")
print(b)