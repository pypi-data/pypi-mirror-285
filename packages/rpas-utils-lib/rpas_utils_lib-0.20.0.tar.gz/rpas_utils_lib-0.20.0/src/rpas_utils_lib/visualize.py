
import os

import cv2

from .abstracts import Batch

def visualize_batch_point_assets(batch: Batch, save_dir: str):
    for counter, item in enumerate(batch.items):
        # Load Image
        path = item.path
        image = cv2.imread(path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get annotations and Draw the Bounding Boxes
        for asset in item.point_assets.assets:
            cv2.rectangle(
                image,
                pt1=(asset.box.xmin, asset.box.ymax),
                pt2=(asset.box.xmax, asset.box.ymin),
                color=(0,0,255),
                thickness=3)

        # Save the Image
        cv2.imwrite(
            filename=os.path.join(save_dir, f"{counter}.jpg"),
            img=image
        )

def render_pixels_on_image(image_path, points: list, output_path, color=(0,0,255)):
    image = cv2.imread(image_path)
    image_name = os.path.basename(image_path)
    for point in points:
        id = point["id"]
        coords = point["kml"]
        for cord in coords:
            pixel = cord["pixel"]
            cv2.circle(image, (pixel[0], pixel[1]), 100, color, 100)
            cv2.putText(image, id, (pixel[0] + 50, pixel[1] + 50) , cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 5)
    cv2.imwrite(f"{output_path}/{image_name}", image)


def render_assets_on_image(image_path, output_path, point_assets = None, linear_assets = None):
    image = cv2.imread(image_path)
    image_name = os.path.basename(image_path)
    for point in point_assets:
        id = point["id"]
        coords = point["kml"]
        for cord in coords:
            pixel = cord["pixel"]
            cv2.circle(image, (pixel[0], pixel[1]), 50, (0,0,255), 50)
            cv2.putText(image, id, (pixel[0] + 50, pixel[1] + 50) , cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 5)
    
    for line in linear_assets:
        id = line["id"]
        coords = line["kml"]
        for i in range(len(coords)-1):
            current_pixel = coords[i]["pixel"]
            next_pixel = coords[i + 1]["pixel"]
            cv2.line(image, (current_pixel[0], current_pixel[1]), (next_pixel[0], next_pixel[1]), (0,0,255), 20)
            cv2.putText(image, id, (current_pixel[0] + 50, current_pixel[1] + 50) , cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 5)

    cv2.imwrite(f"{output_path}/{image_name}", image)