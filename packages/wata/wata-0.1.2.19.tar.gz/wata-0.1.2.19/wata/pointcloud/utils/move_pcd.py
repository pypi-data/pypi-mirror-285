import numpy as np
from scipy.spatial.transform import Rotation


def xyzrpy2RTmatrix(xyz_rpy, degrees=False):
    assert len(xyz_rpy) == 6
    dx, dy, dz, roll, pitch, yaw = xyz_rpy
    
    # 创建旋转矩阵
    r = Rotation.from_euler('xyz', [roll, pitch, yaw], degrees=degrees)
    rotation_matrix = r.as_matrix()
    # 创建平移向量
    translation = np.array([dx, dy, dz])
    # 创建变换矩阵
    matrix = np.eye(4)
    matrix[:3, :3] = rotation_matrix
    matrix[:3, 3] = translation
    return matrix

def RTmatrix2xyzrpy(RTmatrix, degrees=False):
    # 提取平移向量
    translation = RTmatrix[:3, 3]
    # 提取旋转矩阵
    rotation_matrix = RTmatrix[:3, :3]
    # 使用scipy的Rotation类获取欧拉角
    r = Rotation.from_matrix(rotation_matrix)
    rpy = r.as_euler('xyz', degrees=degrees)  
    # 分别提取dx, dy, dz, roll, pitch, yaw
    dx, dy, dz = translation
    roll, pitch, yaw = rpy
    return np.array([dx, dy, dz, roll, pitch, yaw])

def move_pcd_with_RTmatrix(points, RTmatrix):
    pcd_trans = points.copy()
    pcd_hm = np.pad(points[:, :3], ((0, 0), (0, 1)), 'constant', constant_values=1)  # (N, 4)
    pcd_hm_trans = np.dot(RTmatrix, pcd_hm.T).T
    pcd_trans[:, :3] = pcd_hm_trans[:, :3]
    return pcd_trans

def move_pcd_with_xyzrpy(points, xyz_rpy, degrees):
    assert len(xyz_rpy) == 6
    RT_matrix = xyzrpy2RTmatrix(xyz_rpy, degrees=degrees)
    new_pcd = move_pcd_with_RTmatrix(points, RT_matrix)
    return new_pcd, RT_matrix


