import pickle
import httpx
import os
from lxml import etree


from pykml.factory import KML_ElementMaker as KML


def read_pickle(path: str):
    with open(path, "rb") as f:
        return pickle.load(f)


def write_pickle(object, path: str):
    with open(path, "wb") as f:
        pickle.dump(object, f)


def create_linear_assets_folder(kmls, path):
    name = os.path.basename(path)
    name = os.path.splitext(name)[0]

    folder = KML.Folder(KML.name(name + " linear assets"))
    folder.append(KML.visibility(1))

    for kml in kmls:
        id = kml["id"]
        coords = kml["kml"]

        linestring = [c["gps"] for c in coords]
        linestring = [f"{c[0]},{c[1]},0,0" for c in linestring]
        linestring = " ".join(linestring)

        pixels = [c["pixel"] for c in coords]
        pixels = [f"{p[0]},{p[1]}" for p in pixels]
        pixels = " ".join(pixels)

        pm = KML.Placemark(KML.name(id))
        
        p = etree.Element('pixel')
        p.text = pixels
        pm.append(p)

        pm.append(KML.LineString(KML.coordinates(linestring)))
        folder.append(pm)
    return folder


def create_point_assets_folder(kmls, path):
    name = os.path.basename(path)
    name = os.path.splitext(name)[0]

    folder = KML.Folder(KML.name(name + " point assets"))
    folder.append(KML.visibility(1))
    for kml in kmls:
        id = kml["id"]
        cord = kml["kml"][0]["gps"]
        pixel = kml["kml"][0]["pixel"]
        pm = KML.Placemark(KML.name(id))
        p = etree.Element('pixel')
        p.text = f"{pixel[0]},{pixel[1]}"
        pm.append(p)
        pm.append(KML.Point(KML.coordinates(f"{cord[0]},{cord[1]},{0.0}")))
        folder.append(pm)
    return folder


def create_folder(kmls, path):
    linear_assets = []
    point_assets = []
    for kml in kmls:
        if len(kml["kml"]) == 1:
            point_assets.append(kml)
        else:
            linear_assets.append(kml)
    
    point_folder = create_point_assets_folder(point_assets, path)
    linear_folder = create_linear_assets_folder(linear_assets, path)

    return point_folder, linear_folder

################### NOT SURE IF NEEDED ###################

# async def GET(endpoint: str):
#     async with httpx.AsyncClient() as client:
#         r = await client.get(endpoint)
#         r = r.json()
#         return r


# async def POST(endpoint: str, json_data: dict):
#     async with httpx.AsyncClient() as client:
#         r = await client.post(endpoint, data=json_data)
#         r = r.json()
#         return r

