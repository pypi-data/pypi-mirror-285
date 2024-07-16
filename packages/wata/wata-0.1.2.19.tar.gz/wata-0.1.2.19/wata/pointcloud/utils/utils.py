import numpy as np
from pathlib import Path
import os
import tqdm
import glob
import struct
from wata.file.utils import utils as file
from wata.pointcloud.utils.load_pcd import get_points_from_pcd_file
from wata.pointcloud.utils.o3d_visualize_utils import open3d_draw_scenes, show_pcd_from_points_by_open3d
from wata.pointcloud.utils.qtopengl_visualize_utils import show_pcd_from_points_by_qtopengl
from wata.pointcloud.utils.plot_visualize_utils import plot_draw_scenes, show_pcd_from_points_by_matplotlib
from wata.file.utils.type_mapping import numpy_type_to_pcd_type, np_type_to_numpy_type, numpy_type_to_struct_type

def cut_pcd(points, pcd_range):
    x_range = [pcd_range[0], pcd_range[3]]
    y_range = [pcd_range[1], pcd_range[4]]
    z_range = [pcd_range[2], pcd_range[5]]
    mask = (x_range[0] <= points[:, 0]) & (points[:, 0] <= x_range[1]) & (y_range[0] < points[:, 1]) & (
            points[:, 1] <= y_range[1]) & (z_range[0] < points[:, 2]) & (points[:, 2] <= z_range[1])
    points = points[mask]
    return points


def filter_points(points, del_points):
    pcd1_set = set(map(tuple, points))
    pcd2_set = set(map(tuple, del_points))
    result_set = pcd1_set - pcd2_set
    result = np.array(list(result_set))
    return result


def get_points(path, num_features):
    pcd_ext = Path(path).suffix
    if pcd_ext == '.bin':
        num_features = 4 if num_features is None else num_features
        points = np.fromfile(path, dtype=np.float32).reshape(-1, num_features)
    elif pcd_ext == ".npy":
        points = np.load(path)
        points = points[:, 0:num_features]
    elif pcd_ext == ".pcd":
        points = get_points_from_pcd_file(path, num_features=num_features)
    else:
        raise NameError("Unable to handle {} formatted files".format(pcd_ext))
    return points


def pcd2bin(pcd_dir, bin_dir, num_features=4):
    file.mkdir_if_not_exist(bin_dir)
    pcd_list = glob.glob(pcd_dir + "./*.pcd")
    for pcd_path in tqdm.tqdm(pcd_list):
        filename, _ = os.path.splitext(pcd_path)
        filename = filename.split("\\")[-1]
        points = get_points_from_pcd_file(pcd_path, num_features=num_features)
        points = points[:, 0:num_features].astype(np.float32)
        bin_file = os.path.join(bin_dir, filename) + '.bin'
        points.tofile(bin_file)
    print("==> The bin file has been saved in \"{}\"".format(bin_dir))


def show_pcd(path, point_size=1, background_color=None, pcd_range=None, bin_num_features=None, create_coordinate=True,
             create_plane=True, type='open3d'):
    points = get_points(path, num_features=bin_num_features)
    if pcd_range:
        points = cut_pcd(points, pcd_range)
    show_pcd_from_points(points=points, point_size=point_size, background_color=background_color,
                         create_coordinate=create_coordinate, create_plane=create_plane,
                         type=type)


def show_pcd_from_points(points, point_size=1, background_color=None, colors=None, create_coordinate=True,
                         create_plane=True, type='open3d', savepath=None, plot_range=None, o3d_cam_param=None,
                         o3d_window_size=[1200, 800]):
    if type == 'open3d':
        show_pcd_from_points_by_open3d(
            points=points, point_size=point_size,
            background_color=background_color,
            create_coordinate=create_coordinate,
            create_plane=create_plane,
            colors=colors,
            cam_param=o3d_cam_param,
            window_size=o3d_window_size
        )
    elif type == 'qtopengl':
        show_pcd_from_points_by_qtopengl(
            points=points,
            point_size=point_size,
            background_color=background_color,
            create_coordinate=create_coordinate,
            create_plane=create_plane
        )
    elif type == 'matplotlib':
        show_pcd_from_points_by_matplotlib(
            points=points,
            point_size=point_size,
            background_color=background_color,
            colors=colors,
            create_coordinate=create_coordinate,
            savepath=savepath, plot_range=plot_range
        )
    elif type == 'mayavi':
        pass
    elif type == 'vispy':
        pass


def add_boxes(points, gt_boxes=None, gt_labels=None, pred_boxes=None, pred_labels=None, pred_scores=None, point_size=1,
              background_color=None, create_plane=True, point_colors=None, create_coordinate=True, type='open3d',
              savepath=None, plot_range=None, o3d_cam_param=None, o3d_window_size=[1200, 800]):
    if type == 'open3d':
        open3d_draw_scenes(points=points, gt_boxes=gt_boxes, gt_labels=gt_labels,
                           pred_boxes=pred_boxes, pred_labels=pred_labels, pred_scores=pred_scores,
                           point_size=point_size, background_color=background_color, create_plane=create_plane,
                           create_coordinate=create_coordinate, cam_param=o3d_cam_param,
                           window_size=o3d_window_size)
    elif type == 'qtopengl':
        pass
    elif type == 'matplotlib':
        plot_draw_scenes(points=points, gt_boxes=gt_boxes, gt_labels=gt_labels,
                         pred_boxes=pred_boxes, pred_labels=pred_labels, pred_scores=pred_scores,
                         point_size=point_size, background_color=background_color,
                         point_colors=point_colors,
                         create_coordinate=create_coordinate, savepath=savepath, plot_range=plot_range)
    elif type == 'mayavi':
        pass
    elif type == 'vispy':
        pass


def cartesian_to_spherical(points):
    points_cloud = points.copy()
    x = points_cloud[:, 0]
    y = points_cloud[:, 1]
    z = points_cloud[:, 2]
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    dis = np.sqrt(x ** 2 + y ** 2)
    theta = np.arctan2(z, dis)  # 极角
    phi = np.arctan2(y, x)  # 方位角
    spherical_points = np.column_stack((r, theta, phi))
    points[:, 0:3] = spherical_points[:, 0:3]
    return points


def get_pcd_channel_dimension(points, vfov, channel_nums, offset=0.01):
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]
    theta = np.rad2deg(np.arctan2(z, np.sqrt(x ** 2 + y ** 2)))  # 极角
    v_angle = vfov[1] - vfov[0] + 2 * offset
    v_resolution = v_angle / channel_nums
    v_channel = ((vfov[1] + offset - theta) / v_resolution + 1).astype(int)
    return v_channel

def points_in_boxes(points, boxes, type="gpu"):
    import torch
    from wata.pointcloud.ops.roiaware_pool3d import roiaware_pool3d_utils
    
    if isinstance(points, np.ndarray):
        if type == "gpu":
            points = torch.from_numpy(points[:,:3]).unsqueeze(dim=0).float().cuda()
        else:
            points = torch.from_numpy(points[:,:3]).unsqueeze(dim=0).float().cpu()
    if isinstance(boxes, np.ndarray):
        if type == "gpu":
            boxes = torch.from_numpy(boxes).unsqueeze(dim=0).float().cuda()
        else:
            boxes = torch.from_numpy(boxes).unsqueeze(dim=0).float().cpu()

    if type == "gpu":
        box_idxs_of_pts = roiaware_pool3d_utils.points_in_boxes_gpu(points, boxes).cpu().numpy()
    else:
        box_idxs_of_pts = roiaware_pool3d_utils.points_in_boxes_cpu(points, boxes).numpy()
    return box_idxs_of_pts

def save_pcd(points, save_path, fields=None, npdtype=None, type='binary'):
    npdtype_is_exist = True
    point_num, fields_num = points.shape[0], points.shape[1]
    if npdtype is None:
        npdtype_is_exist = False
        points = points.astype(np.float32)
        npdtype = [np.dtype('float32') for _ in range(fields_num)]
    else:
        assert (npdtype) == fields_num, "The length of <npdtype> should be consistent with the number of columns in the pcd."

    if isinstance(npdtype[0], str):
        npdtype = [np_type_to_numpy_type(npdtype[i]) for i in range(fields_num)]


    one_point = points[0,:]
    TYPE, SIZE = [],[]
    struct_formats = ""
    for i in range(len(one_point)):
        struct_formats += numpy_type_to_struct_type(npdtype[i])
        type_size = numpy_type_to_pcd_type(npdtype[i])
        TYPE.append(type_size[0])
        SIZE.append(str(type_size[1]))
    TYPE = " ".join(TYPE)
    SIZE = " ".join(SIZE)
    COUNT = " ".join(map(str, np.ones(int(fields_num), dtype=np.int8)))

    if fields is None:
        fields = " ".join(map(str,np.arange(4, fields_num+1)))  # 生成从4到n的数组
        fields = "x y z " + fields
    else:
        assert (fields) == fields_num, "The length of <fields> should be consistent with the number of columns in the pcd."

    pcd_file = open(save_path, 'wb')

    pcd_file.write('# .PCD v0.7 - Point Cloud Data file format\n'.encode('utf-8'))
    pcd_file.write('VERSION 0.7\n'.encode('utf-8'))

    pcd_file.write(f'FIELDS {fields}\n'.encode('utf-8'))
    pcd_file.write(f'SIZE {SIZE}\n'.encode('utf-8'))
    pcd_file.write(f'TYPE {TYPE}\n'.encode('utf-8'))
    pcd_file.write(f'COUNT {COUNT}\n'.encode('utf-8'))
    pcd_file.write(f'WIDTH {str(point_num)}\n'.encode('utf-8'))
    pcd_file.write('HEIGHT 1\n'.encode('utf-8'))
    pcd_file.write('VIEWPOINT 0 0 0 1 0 0 0\n'.encode('utf-8'))
    pcd_file.write(f'POINTS {str(point_num)}\n'.encode('utf-8'))
    pcd_file.write(f'DATA {type}\n'.encode('utf-8'))

    for i in range(point_num):
        point = points[i,:]
        if type == 'ascii':
            string = ' '.join(map(str, point)) + "\n"
            pcd_file.write(string.encode('utf-8'))
        elif type == 'binary':
            if npdtype_is_exist:
                point = [vlue.astype(npdtype[i]) for i, vlue in enumerate(point)]
            string = struct.pack(struct_formats, *point)
            pcd_file.write(string)
        else:
            raise ValueError("Only 'ascii' and 'binary' can be selected for type")
    pcd_file.close()