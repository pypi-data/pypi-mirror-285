import unittest
from unittest.mock import patch, MagicMock
from rpas_utils_lib import get_image_meta, get_visible_assets_in_image, Camera

class TestImageProcessor(unittest.TestCase):

    @patch('exiftool.ExifToolHelper.get_metadata')
    def test_get_image_meta(self, mock_get_metadata):
        # Mock metadata
        mock_metadata = [{
            "Composite:GPSLatitude": 23.6345,
            "Composite:GPSLongitude": 58.5336,
            "Composite:GPSAltitude": 500,
            "XMP:Yaw": 30.0,
            "XMP:Pitch": 15.0,
            "XMP:Roll": 5.0,
            "Composite:FOV": 45.0,
            "File:ImageHeight": 1080,
            "File:ImageWidth": 1920,
            "EXIF:FocalLength": 35.0,
            "EXIF:FocalPlaneXResolution": 300.0
        }]
        mock_get_metadata.return_value = mock_metadata

        image_path = "/home/nuran_temp/rpas_utils_lib/Fahud_405_20230201_2.jpg"
        image_meta = get_image_meta(image_path)

        self.assertEqual(image_meta["name"], "Fahud_405_20230201_2.jpg")
        self.assertEqual(image_meta["path"], image_path)
        self.assertEqual(image_meta["lat"], 23.6345)
        self.assertEqual(image_meta["long"], 58.5336)
        self.assertEqual(image_meta["alt"], 330)  # 500 - 170
        self.assertEqual(image_meta["yaw"], 30.0)
        self.assertEqual(image_meta["pitch"], 15.0)
        self.assertEqual(image_meta["roll"], 5.0)
        self.assertEqual(image_meta["fov"], 45.0)
        self.assertEqual(image_meta["height"], 1080)
        self.assertEqual(image_meta["width"], 1920)
        self.assertEqual(image_meta["focal_length"], 35.0)
        self.assertEqual(image_meta["focal_plan_resolution"], 300.0)

    @patch('exiftool.ExifToolHelper.get_metadata')
    def test_get_image_meta_no_metadata(self, mock_get_metadata):
        mock_get_metadata.return_value = []
        image_path = "path/to/image.jpg"
        image_meta = get_image_meta(image_path)
        self.assertEqual(image_meta, {})

    @patch('rpas_utils_lib.Camera')
    def test_get_visible_assets_in_image(self, mock_camera):
        mock_camera_instance = mock_camera.return_value
        mock_camera_instance.to_image_coords.side_effect = lambda asset_lat, asset_long, return_outside: (100, 200) if asset_lat == 23.6345 and asset_long == 58.5336 else None

        image_meta = {
            "fov": 45.0,
            "width": 1920,
            "height": 1080,
            "focal_length": 35.0,
            "focal_plan_resolution": 300.0,
            "lat": 23.6345,
            "long": 58.5336,
            "roll": 5.0,
            "pitch": 15.0,
            "yaw": 30.0,
            "alt": 330
        }

        kmls = {
            "asset1": [(58.5336, 23.6345)],
            "asset2": [(58.0000, 23.0000)]
        }

        visible_assets = get_visible_assets_in_image(image_meta, kmls)
        self.assertEqual(len(visible_assets), 1)
        self.assertEqual(visible_assets[0]["id"], "asset1")
        self.assertEqual(visible_assets[0]["kml"][0]["gps"], (58.5336, 23.6345))
        self.assertEqual(visible_assets[0]["kml"][0]["pixel"], (100, 200))

if __name__ == '__main__':
    unittest.main()
