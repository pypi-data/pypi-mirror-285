import json
import cv2
from typing import List, Tuple
from .abstracts import DetectionResults, Box, asset_name_to_asset_type, AssetType, PointAsset ,PointAssetsResults, LinearAssetsResults

class DetectionHandler:
    def __init__(self, focus_on: List[AssetType] = None) -> None:
        self.score_threshold = 0.95
        self.IOU_threshold = 0
        if focus_on is None:
            self.focus_on = list(AssetType)
        else:
            self.focus_on = focus_on

    def annotate(self, image: DetectionResults) -> None:
        img = cv2.imread(image.path)
        for box in image.boxes:
            if box.type is AssetType.Well:
                pt1 = (box.x, box.y)
                pt2 = (box.x + box.w, box.y + box.h)
                cv2.rectangle(img, pt1, pt2, color=(0,0,255), thickness=15)
                if box.id is None:
                    box.id = "Unknown"
                cv2.putText(img, box.id, (box.x + 50, box.y + 50) , cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 15)
        
        cv2.namedWindow("Test", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Test", 1500, 900)
        cv2.imshow("Test", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def IOU(self, boxA: Box, boxB: Box):
        xA = max(boxA.x - boxA.w//2, boxB.x - boxB.w//2)
        yA = max(boxA.y - boxA.h//2, boxB.y - boxB.h//2)
        xB = min(boxA.x + boxA.w//2, boxB.x + boxB.w//2)
        yB = min(boxA.y + boxA.h//2, boxB.y + boxB.h//2)

        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

        boxAArea = (boxA.w + 1) * (boxA.h + 1)
        boxBArea = (boxB.w + 1) * (boxB.h + 1)  

        iou = interArea / float(boxAArea + boxBArea - interArea)
        return iou

    def group_boxes(self, boxes: List[Box]) -> List[List[Box]]:
        discarded_indexes = []
        grouped_boxes = []
        for i in range(len(boxes)):
            if i in discarded_indexes:
                continue
            group = [boxes[i]]
            discarded_indexes.append(i)
            for j in range(i, len(boxes)):
                if i == j or j in discarded_indexes:
                    continue
                iou = self.IOU(boxes[i], boxes[j])
                if iou > self.IOU_threshold:
                    group.append(boxes[j])
                    discarded_indexes.append(j)
            grouped_boxes.append(group)
        return grouped_boxes          

    def supress_overlap(self, boxes: List[Box]) -> List[Box]:
        grouped_boxes = self.group_boxes(boxes)
        maximized_boxes = []
        for group in grouped_boxes:
            type = group[0].type
            confidence = group[0].confidence
            xmin = min([box.x - box.w//2 for box in group])
            ymin = min([box.y - box.h//2 for box in group])
            xmax = max([box.x + box.w//2 for box in group])
            ymax = max([box.y + box.h//2 for box in group])
            w = xmax-xmin
            h = ymax-ymin
            maximized_box = Box(
                x=xmin + w//2,
                y=ymin + h//2,
                w=w,
                h=h,
                type=type,
                confidence=confidence
            )
            maximized_boxes.append(maximized_box)
        return maximized_boxes

    def parse_from_json_file(self, json_path: str) -> List[DetectionResults]:
        """
        This Function is used to parse the detection results saved in the JSON file into a list of images each image will be an instance of the 
        abstract class "Image" wich will contain a list of boxes with the highst confidence.
        """

        f = open(json_path, "r")
        raw = json.load(f)
        images = []
        for image_path, data in raw.items():
            boxes = []
            for d in data:
                labels = d["labels"]
                for label in labels:
                    type = asset_name_to_asset_type(label["name"])
                    if type not in self.focus_on:
                        continue
                    score = label["score"]
                    if score >= self.score_threshold:
                        box = Box(
                            x = d["box"][0],
                            y = d["box"][1],
                            w = d["box"][2],
                            h = d["box"][3],
                            type = type,
                            confidence = score
                            )
                        boxes.append(box)
            
            image = DetectionResults(image_path, boxes)
            images.append(image)
        return images   

    def parse(self, raw_data: List[dict]) -> Tuple[PointAssetsResults, LinearAssetsResults]:
        point_asset_results = PointAssetsResults()
        linear_asset_results = PointAssetsResults()
        for box in raw_data:
            if box["type"] in [AssetType.Flowline, AssetType.Powerline, AssetType.Pipe, AssetType.Road]:
                pass
            elif box["type"] in [AssetType.Well]:
                b = Box(box["x"], box["y"], box["w"], box["h"], box["type"], box["confidence"])
                pa = PointAsset(box=b, type=box["type"])
                point_asset_results.assets.append(pa)
            else:
                raise Exception(f"Not Supported Asset Type {box['type']}")
        return point_asset_results, linear_asset_results


