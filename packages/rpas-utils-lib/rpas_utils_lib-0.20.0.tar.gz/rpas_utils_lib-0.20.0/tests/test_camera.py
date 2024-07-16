import rpas_utils_lib
import numpy as np

from rpas_utils_lib import build_camera


def test_camera():
    # Test data
    image_meta = {
        'fov': 90,
        'width': 1920,
        'height': 1080,
        'focal_length': 35,
        'focal_plan_resolution': 1.0,
        'lat': 40.748817,
        'long': -73.985428,
        'alt': 285.0,
        'roll': 0,
        'pitch': 0,
        'yaw': 0
    }

    # Instantiate the Camera
    camera = build_camera(image_meta)

    # Test UTM conversion
    lat, long = 40.748817, -73.985428
    easting, northing = camera.to_utm(lat, long)
    assert isinstance(easting, float) and isinstance(northing, float), "UTM conversion failed."

    # Test visibility
    visible = camera.is_visible_point(40.748817, -73.985428)
    assert visible is True, "Point visibility check failed."

    # Test coordinate transformation
    image_coords = camera.to_image_coords(40.748817, -73.985428)
    assert image_coords is not False, "Coordinate transformation to image failed."

    # Test coordinate transformation with debug
    image_coords_debug = camera.to_image_coords(40.748817, -73.985428, debug=True)
    assert image_coords_debug is not False, "Coordinate transformation to image with debug failed."

    # Test world coordinates to image coordinates
    asset_lats = np.array([40.748817, 40.7489])
    asset_longs = np.array([-73.985428, -73.9855])
    image_coords_list = camera.world_coords_to_image_coords(asset_lats, asset_longs)
    assert all(isinstance(coords, list) or coords is False for coords in image_coords_list), "World coordinates to image coordinates transformation failed."

    # Test reverse transformation to GPS coordinates
    pixel_coords = (960, 540)  # Center of the image
    gps_coords = camera.to_gps_coords(pixel_coords)
    assert isinstance(gps_coords, tuple) and len(gps_coords) == 2, "Reverse transformation to GPS coordinates failed."

    print("All tests passed!")

if __name__ == "__main__":
    test_camera()


    