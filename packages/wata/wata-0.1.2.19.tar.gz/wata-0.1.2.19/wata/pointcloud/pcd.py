from wata.pointcloud.utils import utils
from wata.pointcloud.utils import move_pcd
from wata.pointcloud.utils import o3d_visualize_utils


class PointCloudProcess:

    @staticmethod
    def cut_pcd(points, pcd_range):
        return utils.cut_pcd(points, pcd_range)

    @staticmethod
    def filter_points(points, del_points):
        return utils.filter_points(points, del_points)

    @staticmethod
    def show_pcd(path, point_size=1, background_color=None, pcd_range=None, bin_num_features=None,
                 create_coordinate=True, create_plane=False, type='open3d'):
        utils.show_pcd(path, point_size, background_color, pcd_range, bin_num_features, create_coordinate, create_plane,
                       type)

    @staticmethod
    def points_to_o3d_model(points, point_colors=None):
        return o3d_visualize_utils.points_to_o3d_model(points=points, point_colors=point_colors)

    @staticmethod
    def save_o3d_camera_parameters(points, save_file_path='camera_parameters.json', window_size=[1200, 800]):
        return o3d_visualize_utils.save_o3d_camera_parameters(points, save_file_path, window_size)

    @staticmethod
    def show_pcd_from_points(points, point_size=1, background_color=None, colors=None, create_coordinate=True,
                             create_plane=False, type='open3d'):
        utils.show_pcd_from_points(points, point_size, background_color, colors, create_coordinate, create_plane, type)

    @staticmethod
    def get_points(path, num_features=None):
        return utils.get_points(path, num_features)

    @staticmethod
    def add_boxes(points, gt_boxes=None, gt_labels=None, pred_boxes=None, pred_labels=None, pred_scores=None,
                  point_size=1,
                  background_color=None, create_plane=False, point_colors=None, create_coordinate=True, type='open3d',
                  savepath=None, plot_range=None):
        utils.add_boxes(points, gt_boxes=gt_boxes, gt_labels=gt_labels, pred_boxes=pred_boxes, pred_labels=pred_labels,
                        pred_scores=pred_scores, point_size=point_size,
                        background_color=background_color, create_plane=create_plane, point_colors=point_colors,
                        create_coordinate=create_coordinate, type=type, savepath=savepath, plot_range=plot_range)

    @staticmethod
    def pcd2bin(pcd_dir, bin_dir, num_features=4):
        utils.pcd2bin(pcd_dir, bin_dir, num_features)

    @staticmethod
    def xyzrpy2RTmatrix(xyz_rpy, degrees):
        return move_pcd.xyzrpy2RTmatrix(xyz_rpy=xyz_rpy, degrees=degrees)

    @staticmethod
    def RTmatrix2xyzrpy(RTmatrix):
        return move_pcd.RTmatrix2xyzrpy(RTmatrix)

    @staticmethod
    def move_pcd_with_RTmatrix(points, RTmatrix):
        return move_pcd.move_pcd_with_RTmatrix(points, RTmatrix)

    @staticmethod
    def move_pcd_with_xyzrpy(points, xyz_rpy, degrees):
        return move_pcd.move_pcd_with_xyzrpy(points, xyz_rpy, degrees=degrees)
    
    @staticmethod
    def cartesian_to_spherical(points):
        return utils.cartesian_to_spherical(points=points)
    
    @staticmethod
    def get_pcd_channel_dimension(points, vfov, channel_nums, offset=0.01):
        return utils.get_pcd_channel_dimension(points, vfov, channel_nums, offset)
    
    @staticmethod
    def points_in_boxes(points, boxes, type="gpu"):
        return utils.points_in_boxes(points, boxes, type)

    @staticmethod
    def save_pcd(points,save_path, fields=None, npdtype=None ,type='binary'):
        return utils.save_pcd(points, save_path,fields,npdtype,type)