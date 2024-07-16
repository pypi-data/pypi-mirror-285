import unittest
import json
from unittest.mock import patch, MagicMock
import numpy as np
import rpas_utils_lib
from rpas_utils_lib import DetectionHandler, DetectionResults, Box, asset_name_to_asset_type, AssetType, PointAsset, PointAssetsResults, LinearAssetsResults

class TestDetectionHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Sample JSON data to mimic input file
        cls.sample_json_data = {
            "image1.jpg": [
                {
                    "box": [100, 150, 50, 60],
                    "labels": [{"name": "Well", "score": 0.96}]
                },
                {
                    "box": [200, 250, 80, 90],
                    "labels": [{"name": "Well", "score": 0.97}]
                }
            ],
            "image2.jpg": [
                {
                    "box": [300, 350, 70, 80],
                    "labels": [{"name": "Well", "score": 0.94}]
                },
                {
                    "box": [400, 450, 60, 70],
                    "labels": [{"name": "Well", "score": 0.98}]
                }
            ]
        }

        # Save sample JSON data to a file for testing
        with open("sample_data.json", "w") as f:
            json.dump(cls.sample_json_data, f)

        # Initialize DetectionHandler
        cls.detection_handler = DetectionHandler(focus_on=[AssetType.Well])

    def test_parse_from_json_file(self):
        parsed_results = self.detection_handler.parse_from_json_file("sample_data.json")
        self.assertEqual(len(parsed_results), 2)
        self.assertEqual(parsed_results[0].path, "image1.jpg")
        self.assertEqual(len(parsed_results[0].boxes), 2)
        self.assertEqual(parsed_results[0].boxes[0].x, 100)

    def test_IOU(self):
        boxA = Box(100, 150, 50, 60, AssetType.Well, 0.96)
        boxB = Box(110, 160, 50, 60, AssetType.Well, 0.95)
        iou = self.detection_handler.IOU(boxA, boxB)
        self.assertGreater(iou, 0)

    def test_group_boxes(self):
        boxA = Box(100, 150, 50, 60, AssetType.Well, 0.96)
        boxB = Box(110, 160, 50, 60, AssetType.Well, 0.95)
        boxes = [boxA, boxB]
        grouped_boxes = self.detection_handler.group_boxes(boxes)
        self.assertEqual(len(grouped_boxes), 1)

    def test_supress_overlap(self):
        boxA = Box(100, 150, 50, 60, AssetType.Well, 0.96)
        boxB = Box(110, 160, 50, 60, AssetType.Well, 0.95)
        boxes = [boxA, boxB]
        suppressed_boxes = self.detection_handler.supress_overlap(boxes)
        self.assertEqual(len(suppressed_boxes), 1)

    @patch('cv2.imread')
    @patch('cv2.imshow')
    @patch('cv2.waitKey')
    @patch('cv2.destroyAllWindows')
    def test_annotate(self, mock_destroy, mock_waitkey, mock_imshow, mock_imread):
        # Mock the imread method to return a dummy image
        mock_imread.return_value = 255 * np.ones((1000, 1000, 3), dtype=np.uint8)

        parsed_results = self.detection_handler.parse_from_json_file("sample_data.json")

        try:
            self.detection_handler.annotate(parsed_results[0])
        except Exception as e:
            self.fail(f"annotate method failed: {e}")

if __name__ == '__main__':
    unittest.main()