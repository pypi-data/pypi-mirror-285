from wata.mathematics.utils import utils
from wata.mathematics.utils import trans_coordinate
import numpy as np

class Maths:

    @staticmethod
    def point_in_polygon(point, polygon):
        return utils.point_in_polygon(point, polygon)

    @staticmethod
    def xy2rt(x,y):
        return trans_coordinate.xy2rt(x,y)

    @staticmethod
    def rt2xy(r, theta):
        return trans_coordinate.rt2xy(r, theta)

    @staticmethod
    def xyz2rtp(x, y, z):
        return trans_coordinate.xyz2rtp(x, y, z)

    @staticmethod
    def rtp2xyz(r,theta,phi):
        return trans_coordinate.rtp2xyz(r,theta,phi)