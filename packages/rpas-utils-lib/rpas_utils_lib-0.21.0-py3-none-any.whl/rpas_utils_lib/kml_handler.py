import requests
from xml.dom import minidom

from pykml.factory import KML_ElementMaker as KML
from lxml import etree

from .abstracts import AssetType


def parse_assets_dict(d: dict):
    filtered_kmls = []
    for asset in d:
        asset_id = asset["asset_id"]
        asset_attributes = asset["asset_attributes"]
        coords = asset["asset_geom"]["coordinates"]
        asset_type = asset["asset_type"]
        if asset_type == "flowline":
            asset_type = AssetType.Flowline
        elif asset_type == "pipeline":
            asset_type = AssetType.Pipeline
        elif asset_type == "well":
            asset_type = AssetType.Well
        elif asset_type == "road":
            asset_type = AssetType.Road
        elif asset_type == "powerline":
            asset_type = AssetType.Powerline

        if asset_type in [AssetType.Flowline, AssetType.Pipeline, AssetType.Well, AssetType.Road, AssetType.Powerline]:
            try:
                coords = [(float(cord[0]), float(cord[1])) for cord in coords]
            except:
                coords = [(float(coords[0]), float(coords[1]))]
            kml = {
                "id": asset_id,
                "type": asset_type,
                "coords": coords,
                "attributes": asset_attributes
            }
            filtered_kmls.append(kml)

    return filtered_kmls


def load_filtered_kmls(longitude, latitude, host: str, port: int):
    print("[INFO] Calling spatial filter")
    payload = {
    "latitude":latitude,
    "longitude":longitude,
    "radius":300
    }

    filtered_assets = requests.post(f"http://{host}:{port}/assets/spatial_filter/", json=payload).json()["assets_geom.geos"]
    return parse_assets_dict(filtered_assets)


def load_kmls(kmls_path):
    file = minidom.parse(kmls_path)
    pms = file.getElementsByTagName('Placemark')
    kmls = {}
    for pm in pms:
        id = id = pm.getAttribute("id")
        coordinates = pm.getElementsByTagName("coordinates")[0].firstChild.data
        coordinates = coordinates.strip()
        coordinates = coordinates.split(" ")
        coordinates = [(float(cord.split(",")[0]), float(cord.split(",")[1])) for cord in coordinates]
        kmls[id] = coordinates
    return kmls

def write_image_kmls(path, point_assets_folder, linear_assets_folder):
    doc = KML.Document()
    if point_assets_folder is not None:
        doc.append(point_assets_folder)    
    if linear_assets_folder is not None:
        doc.append(linear_assets_folder)
    with open(path, "w") as f:
        kml = KML.kml(doc)
        f.write(etree.tostring(kml, pretty_print=True, encoding='utf8', method='xml').decode())

