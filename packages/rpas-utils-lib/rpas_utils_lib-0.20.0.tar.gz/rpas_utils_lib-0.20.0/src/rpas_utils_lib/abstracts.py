from enum import Enum, unique
from pydantic import BaseModel
from typing import List,Union, Tuple
import numpy as np

class AnomalyType(Enum):
    pass

class Anomaly:
    def __init__(self, x, y, w, h, type: AnomalyType, score: float) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.type = type
        self.score = score

    def to_dict(self, serialize=False) -> dict:
        if serialize:
            type = self.type.value
        else:
            type = self.type
        
        return {
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "type": type,
            "score": self.score
        }

@unique
class AssetType(Enum):
    Well = 1
    Pipeline = 2
    Flowline = 3
    Powerline = 6
    Road = 8
    Pipe = 23


@unique
class FlowlineAnomalyType(AnomalyType):
    FLOWLINECONTINUOUSLEAKSIDENTIFICATOIN = 1
    """FLOWLINE CONTINUOUS LEAKS IDENTIFICATOIN"""
    SANDCOVEREDFLOWLINES = 5
    """SAND COVERED FLOWLINES"""


@unique
class PipelineAnomalyType(AnomalyType):
    AGPIPELINECOVEREDINSAND = 6
    """AG PIPELINE COVERED IN SAND"""
    LEAKAGE = 19
    """LEAKAGE"""

@unique
class RoadAnomalyType(AnomalyType):
    POTHOLES = 1
    """POTHOLES"""
    SURFACEMARKINGISSUE = 2
    """SURFACE MARKING ISSUE"""
    SANDACCUMULATIONONSURFACE = 3
    """SAND ACCUMULATION ON SURFACE"""
    SURFACEDAMAGE = 4
    """SURFACE DAMAGE"""
    OBSTRUCTION = 5
    """OBSTRUCTION"""

@unique
class WellAnomalyType(AnomalyType):
    CELLARGRATINGCONDITION = 1
    """CHECK FOR CELLAR GRATING CONDITION"""
    CHECKFORLEAKINTHESTUFFINGBOX = 2
    """CHECK FOR LEAK"""
    RUBBISHORFOD = 6
    """RUBBISH/FOD"""


class Box:
    def __init__(self, x: int, y: int, w: int, h: int, type: AssetType, confidence: float, id: str = None, attributes = {}) -> None:
        self.x = x
        """x-center"""
        self.y = y
        """y-center"""
        self.w = w  
        self.h = h
        self.type = type
        self.confidence = confidence
        self.id = id
        self.attributes = attributes
    
    def __repr__(self) -> str:
        string = f"(x, y, w, h) = ({self.x},{self.y},{self.w},{self.h})"
        return string
    
    def to_dict(self, serialize=False) -> dict:
        if serialize:
            type = self.type.value
        else:
            type = self.type
        
        return {
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "type": type,
            "confidence": self.confidence,
            "id": self.id,
            "attributes": self.attributes
        }
    @classmethod
    def from_dict(cls, d):
        return cls(
            x=d["x"],
            y=d["y"],
            w=d["w"],
            h=d["h"],
            type=AssetType(d["type"]),  # Convert string back to AssetType
            confidence=d["confidence"],
            id=d.get("id"),
            attributes=d.get("attributes", {})
        )
    
class Polygon:
    def __init__(self, id:str = None, type: AssetType = None, coords: List[Tuple[int, int]] = [], linestring: List[Tuple[int, int]] = [], attributes = {}) -> None:
        self.id = id
        self.type = type 
        self.coords = coords
        self.linestring = linestring
        self.attributes = attributes

    def __repr__(self) -> str:
        string = f"<Polygon id={self.id}, type={self.type}, size={len(self.coords)}>"
        return string

    def to_dict(self, serialize=False) -> dict:
        if serialize:
            type = self.type.value
        else:
            type = self.type
        
        return {
            "id": self.id,
            "type": type,
            "coords": self.coords,
            "linestring": self.linestring,
            "attributes": self.attributes
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        # Deserialize 'type' if needed (assuming it's an Enum or similar)
        type = data.get("type")
        if type and isinstance(type, str):
            # Add necessary deserialization logic for 'type'
            type = AssetType[type]  # Example if AssetType is an Enum
        
        return cls(
            id=data.get("id"),
            type=type,
            coords=data.get("coords", []),
            linestring=data.get("linestring", []),
            attributes=data.get("attributes", {})
        )


class LinearAsset:
    def __init__(self, polygon: Polygon = None, type: int = None, asset_id: int = None, db_key: int = None, anomalies: List[Anomaly] = []) -> None:
        self.polygon: Polygon = polygon
        self.type = type
        self.asset_id = asset_id
        self.db_key = db_key  # Asset ID in the Database.
        self.anomalies = anomalies

    def __repr__(self) -> str:
        return f"Linear Asset -> Type: {self.type}, ID: {self.asset_id}"



class PointAsset:
    def __init__(self, box: Box = None, type: int = None, asset_id: int = None, db_key: int = None, anomalies: List[Anomaly] = []) -> None:
        self.box: Box = box
        self.type = type
        self.asset_id = asset_id
        self.db_key = db_key  # Asset ID in the Database
        self.anomalies = anomalies

    def __repr__(self) -> str:
        return f"Point Asset -> Type: {self.type}, ID: {self.asset_id}"

class KML:
    def __init__(self, id, pixel_location, ground_location = None) -> None:
        self.id = id
        self.ground_location = ground_location
        self.pixel_location = pixel_location




def asset_label_to_asset_type(asset_label: int):
    asset_label += 1
    # if asset_label == 2:
    #     return AssetType(3)
    return AssetType(asset_label)

def asset_name_to_asset_type(asset_name: str): 
    return AssetType[asset_name.capitalize()]

class PointAssetsResults:
    def __init__(self) -> None:
        self.assets: List[PointAsset] = []
    
    def serialize(self) -> List[dict]:
        output = []
        for asset in self.assets:
            output.append({
                "box": asset.box.to_dict(serialize=True),
                "anomalies": [anomaly.to_dict(serialize=True) for anomaly in asset.anomalies],
                "asset_id": asset.asset_id,
                "type": asset.type.value,
                "db_key": asset.db_key
            })
        return output
    
    def deserialize(self, dump: List[dict]):
        for item in dump:
            b = Box(item["box"]["x"], item["box"]["y"], item["box"]["w"], item["box"]["h"], item["box"]["type"], item["box"]["confidence"])
            anomalies = [Anomaly(x=anomaly["x"], y=anomaly["y"], w=anomaly["w"], h=anomaly["h"], type=anomaly["type"], score=anomaly["score"]) for anomaly in item.get("anomalies", [])]
            pa = PointAsset(box=b, type=AssetType(item["type"]), asset_id=item["asset_id"], db_key=item["db_key"], anomalies=anomalies)
            self.assets.append(pa)


class LinearAssetsResults:
    def __init__(self) -> None:
        self.assets: List[LinearAsset] = []
    
    def serialize(self) -> List[dict]:
        output = []
        for asset in self.assets:
            output.append({
                "polygon": asset.polygon.to_dict(serialize=True),
                "anomalies": [anomaly.to_dict(serialize=True) for anomaly in asset.anomalies],
                "asset_id": asset.asset_id,
                "type": asset.type.value,
                "db_key": asset.db_key
            })
        return output
    
    def deserialize(self, dump: List[dict]):
        for item in dump:
            p = Polygon(id=item["asset_id"], type=item["type"], coords=item["polygon"]["coords"], linestring=item["polygon"]["linestring"], attributes=item["polygon"]["attributes"])
            anomalies = [Anomaly(x=anomaly["x"], y=anomaly["y"], w=anomaly["w"], h=anomaly["h"], type=anomaly["type"], score=anomaly["score"]) for anomaly in item["anomalies"]]
            la = LinearAsset(polygon=p, type=AssetType(item["type"]), asset_id=item["asset_id"], db_key=item["db_key"], anomalies=anomalies)
            self.assets.append(la)

class ImageMirror(BaseModel):
    name: str = None
    description: str = None
    image_id: int
    path: str = None
    metadata: dict = None
    image:np.ndarray = None
    class Config:
        arbitrary_types_allowed = True
    point_assets: Union[PointAssetsResults, list] = PointAssetsResults()
    linear_assets: Union[LinearAssetsResults, list] = LinearAssetsResults()
    exists: bool = None



class Batch(BaseModel):
    items: List[ImageMirror]
    batch_id: str = None


class DetectionResults:
    def __init__(self, path: str, boxes: List[Box] = None) -> None:
        self.path = path
        self.boxes = boxes
