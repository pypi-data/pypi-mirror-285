from typing import Optional
from geopy import distance

import utm 
import math
import numpy as np



class Camera:

    def __init__(self, width_fov_degrees, image_width, image_height, focal_length_mm, focal_plan_resolution):
        """
            This camera model assumes that it's a square camera so Fx = Fy and Sx = Sy
        """
        self.image_width = image_width
        self.image_height = image_height
        self.x_fov_rad = ((math.pi/180.0) * width_fov_degrees) / 2
        """The horizontal alpha / 2 in rad"""
        self.y_fov_rad = math.atan(
            (self.image_height / self.image_width) * math.tan(((math.pi/180.0) * width_fov_degrees) / 2))
        # """The vertical alpha / 2 in rad, calculated with the correct AoV formula"""
        self.focal_length = focal_length_mm / 10 ## from mm to cm
        self.focal_plan_resolution = focal_plan_resolution
        self.Sx = 1 # 1.4
        """No shear on the sensor"""
        self.Sy = 1 # 1.15
        """No shear on the sensor"""
        self.W = np.array([[1, 0, 0], [0, 1, 0]]) # [[1 0 0] [0 1 0]]

    def __repr__(self) -> str:
        print(f"Image Width: {self.image_width}")
        print(f"Image Height: {self.image_height}")
        print(f"Focal Length: {self.focal_length}")
        print(f"Longitude: {self.long}")
        print(f"Latitude: {self.lat}")
        print(f"Height: {self.height_above_ground}")
        print(f"Yaw: {self.yaw}")
        print(f"Pitch: {self.pitch}")
        print(f"Roll: {self.roll}")
        return "---------"

    def to_utm(self, lat, long):
        easting, northing, _, _ = utm.from_latlon(lat, long, force_zone_number=40, force_zone_letter="Q")
        return easting, northing

    def to_lat_long(self, easting, northing):
        lat, long = utm.to_latlon(easting, northing, zone_number=40, zone_letter="Q", strict=False)
        return lat, long

    def set_position(self, lat, long, height_above_ground = 285.0, roll=0, pitch=0, yaw=0):

        self.lat = lat
        self.long = long

        self.lat_utm, self.long_utm = self.to_utm(self.lat, self.long)

        self.height_above_ground = height_above_ground
        
        self.roll = -roll
        self.yaw = yaw
        self.pitch = pitch

        # self.roll = 180 - roll
        # self.pitch = 180 - pitch
        self.yaw = yaw - 90
        # It has been rotated over the yaw's axis !!

        self.roll *= (np.pi / 180)
        self.pitch *= (np.pi / 180)
        self.yaw *= (np.pi / 180)

        self.Rx = np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, np.cos(self.pitch), -np.sin(self.pitch)],
                [0.0, np.sin(self.pitch), np.cos(self.pitch)]
            ]
        )

        self.Ry = np.array(
            [
                [np.cos(self.roll), 0.0, np.sin(self.roll)],
                [0.0, 1.0, 0.0],
                [-np.sin(self.roll), 0.0, np.cos(self.roll)]
            ]
        )

        self.Rz = np.array(
            [
                [np.cos(self.yaw), -np.sin(self.yaw), 0.0],
                [np.sin(self.yaw), np.cos(self.yaw), 0.0],
                [0.0, 0.0, 1.0]
            ]
        )

        self.rotation_matrix = self.Rz @ self.Ry @ self.Rx
        self.translation_vector = np.expand_dims(np.array([self.long_utm, self.lat_utm, self.height_above_ground]), axis=1)
        
        self.translation_vector = -1 * self.rotation_matrix.T @ self.translation_vector
        
        self.extrinsic_matrix = np.concatenate((self.rotation_matrix.T, self.translation_vector), axis=1)
        # self.extrinsic_matrix = np.concatenate((self.extrinsic_matrix, np.expand_dims(np.array([0,0,0,1]), axis=0)), axis=0)


        aspect_ratio = self.image_height/self.image_width


        self.intrinsic_matrix = np.array([
            [self.focal_length * self.focal_plan_resolution, 0, self.image_width/2],
            [0, self.focal_length * self.focal_plan_resolution, self.image_height/2],
            [0, 0, 1]]
        ) # square-shaped pixel

        self.transformation_matrix = self.intrinsic_matrix @ self.extrinsic_matrix

    def is_visible_point(self, asset_lat, asset_long, ground_height = 0):
        lat_distance = distance.distance((asset_lat,0), (self.lat, 0))
        long_distance = distance.distance((0, asset_long), (0, self.long))

        if asset_lat<self.lat:
            lat_distance *= -1

        if asset_long<self.long:
            long_distance *= -1

        lat_metres = lat_distance.meters
        long_metres = long_distance.meters

        cam_x_metres = (
                    long_metres * math.cos(self.yaw) 
                    + lat_metres * math.sin(self.yaw)
                )
        cam_y_metres = (
                    lat_metres * math.cos(self.yaw) 
                    - long_metres * math.sin(self.yaw)
                )

        cam_x_rad = math.atan(cam_x_metres/self.height_above_ground)
        cam_y_rad = math.atan(cam_y_metres/self.height_above_ground)

        if abs(cam_x_rad) > self.x_fov_rad:
            return False
        if abs(cam_y_rad) > self.y_fov_rad:
            return False
        else:
            return True

    def to_image_coords(
            self, asset_lat: float, asset_long: float,
            ground_height: float=0.,
            return_outside: bool=False, debug: bool=False):
        # if not self.is_visible_point(asset_lat=asset_lat, asset_long=asset_long, ground_height=ground_height):
        #     return False
        # NOTE: above lines are disabled, since it is easier to check the image coordinates against image boundaries instead

        asset_lat_utm, asset_long_utm = self.to_utm(asset_lat, asset_long)

        homo_asset_ground_point = [asset_long_utm, asset_lat_utm, ground_height, 1]
        
        logits = self.extrinsic_matrix @ homo_asset_ground_point
        transformed_asset_point = self.intrinsic_matrix @ logits
               
        x, y = transformed_asset_point[0] // transformed_asset_point[-1], transformed_asset_point[1] // transformed_asset_point[-1]


        x *= self.Sx
        y *= self.Sy

        rot, trans = np.split(self.W, [2], axis=1)
        if self.W.shape == (3, 3):
            raise NotImplementedError
        x_y = np.array([x, y]).reshape(-1, 1)
        x_y_ = np.dot(rot, x_y)
        x_y_ = np.add(x_y_, trans)
        x, y = int(x_y_[0]), int(x_y_[1])

        if debug: 
            print(homo_asset_ground_point)
            print(self.extrinsic_matrix)
            print(logits)
            print(self.intrinsic_matrix)
            print(transformed_asset_point)
            print(x, y)
            print(f"focal_length: {self.focal_length}, {self.focal_plan_resolution}")
            print("------------------------------------------------------------")
        


        if x < 0 or y < 0 or x > self.image_width or y > self.image_height:
            if return_outside:
                return int(x) , int(y)
            else:
                return False 
        else:
            return int(x), int(y)

    def world_coords_to_image_coords(
            self, asset_lats: np.ndarray, asset_longs: np.ndarray,
            ground_heights: Optional[np.ndarray]=None,
            return_outside: bool=False, debug: bool=False):
        utm_lats, utm_longs = self.to_utm(asset_lats, asset_longs)
        if ground_heights is None:
            ground_heights = np.zeros_like(asset_lats)
        homo_asset_ground_points = np.stack([
            utm_longs, utm_lats, ground_heights, np.ones_like(asset_lats)],
            axis=0)
        # no sensor shear is assumed
        res = np.linalg.multi_dot((
            self.intrinsic_matrix, self.extrinsic_matrix, homo_asset_ground_points))

        res = res / res[2, :][np.newaxis, :]
        if self.W.shape == (2, 3):
            W_h = np.vstack((self.W, [[0, 0, 1]]))
            res = (W_h @ res).T
        else:
            W_h = self.W
            res = (W_h @ res).T
            res = res / res[:, 2][:, np.newaxis]

        if debug: 
            print(homo_asset_ground_points)
            print(self.extrinsic_matrix)
            print(self.intrinsic_matrix)
            print(res)
            print(f"focal_length: {self.focal_length}, {self.focal_plan_resolution}")
            print("------------------------------------------------------------")
        
        xy_list = res[:, :2].astype(int).tolist()
        if return_outside:
            return xy_list
        outside = (
            res[:, 0] < 0) | (res[:, 1] < 0) | \
                (res[:, 0] > self.image_width) | (res[:, 1] > self.image_height)
        xy_list = [
            False if o else xy_list[i]
            for i, o in enumerate(outside)]
        return xy_list

    def rotate_points(self, x, y):
        homogenous_point = [x, y, 1]
        homogenous_pixel = self.Rz @ self.Rx @ self.Ry @ homogenous_point 
        image_x, image_y = [int(abs(p)) for p in homogenous_pixel][:-1]
        return (image_x, image_y)

    def to_gps_coords(self, pixel: tuple):
        """this method transforms from pixel to ground coordinates

        Args:
            pixel (tuple): (x, y)

        """

        U_V_1 = np.array([pixel[0], pixel[1], 1])
        U_V_W = - U_V_1 * self.height_above_ground
        logits = np.linalg.inv(self.intrinsic_matrix) @ U_V_W
        logits = np.append(logits, 1)
        ext_mtx = np.concatenate((self.extrinsic_matrix, [[0, 0, 0, 1]]))
        homo_asset_ground_point = np.linalg.inv(ext_mtx) @ logits
        asset_long_utm, asset_lat_utm, ground_height = homo_asset_ground_point[:3]
        lat, long = self.to_lat_long(asset_lat_utm, asset_long_utm)
        return long, lat
    
    def to_dict(self):
        return {
            "image_width": self.image_width,
            "image_height": self.image_height,
            "x_fov_rad": self.x_fov_rad,
            "y_fov_rad": self.y_fov_rad,
            "focal_length": self.focal_length,
            "focal_plan_resolution": self.focal_plan_resolution,
            "Sx": self.Sx,
            "Sy": self.Sy,
            "W": self.W.tolist(),
            "extrinsic_matrix": self.extrinsic_matrix.tolist(),
            "intrinsic_matrix": self.intrinsic_matrix.tolist(),
            "transformation_matrix": self.transformation_matrix.tolist()
        }
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            image_width=data["image_width"],
            image_height=data["image_height"],
            x_fov_rad=data["x_fov_rad"],
            y_fov_rad=data["y_fov_rad"],
            focal_length=data["focal_length"],
            focal_plan_resolution=data["focal_plan_resolution"],
            Sx=data["Sx"],
            Sy=data["Sy"],
            W=np.array(data["W"]),
            extrinsic_matrix=np.array(data["extrinsic_matrix"]),
            intrinsic_matrix=np.array(data["intrinsic_matrix"]),
            transformation_matrix=np.array(data["transformation_matrix"])
        )


def build_camera(image_meta):
    camera = Camera(
        width_fov_degrees=image_meta['fov'],
        image_width=image_meta['width'], 
        image_height=image_meta['height'], 
        focal_length_mm=image_meta['focal_length'],
        focal_plan_resolution=image_meta['focal_plan_resolution']
        )
    camera.set_position(image_meta['lat'], image_meta['long'], roll=image_meta['roll'], pitch=image_meta['pitch'], yaw=image_meta['yaw'], height_above_ground=image_meta["alt"])
    return camera
