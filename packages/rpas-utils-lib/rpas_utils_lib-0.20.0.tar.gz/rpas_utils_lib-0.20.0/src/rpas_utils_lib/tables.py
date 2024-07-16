from sqlalchemy import MetaData, Column, Integer, String, Float, Date, Boolean, JSON, Table, DateTime
from geoalchemy2 import Geometry

class RPASTables:
    def __init__(self, metadata: MetaData) -> None:
        self.metadata = metadata

    def build_missions_image(self) -> Table:
        missions_image = Table(
            "missions_image", self.metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(100)),
            Column("lat_wgs84", Float),
            Column("long_wgs84", Float),
            Column("func_loc", String(100)),
            Column("date_taken", Date),
            Column("link", String(1000)),
            Column("link_export", String(1000)),
            Column("flight_id", Integer),
            Column("job_id", Integer),
            ## location  # Geometry ????
            Column("easting_wgs84", Float),
            Column("northing_wgs84", Float),
            Column("sensor", String(250)),
            Column("metadata", JSON),
            Column("image_annotated", Boolean)
            ## image_footprint = Column()  # Geometry ????
        )
        return missions_image
    
    def build_ai_annotation_table(self) -> Table:
        ai_annotation = Table(
            "annotation_ai", self.metadata,
            Column("id", Integer, primary_key=True),
            Column("image_id", Integer),
            Column("annotation_type", Boolean),         # 0/1 for Point/Linear
            Column("detection_result", JSON),           # Detection results
            Column("detected_asset_type", String(50)),  # Highest confidence asset type
            Column("identification_result", JSON),      # Identification results
            Column("detected_asset_id", String(50)),    # Highest confidence asset id (KML)
            Column("anomaly_detection_result", JSON),   # Anomaly classification results
            Column("detected_anomaly_id", Integer)      # Highest confidence anomoly id
        )
        return ai_annotation

    def build_assets_table(self) -> Table:
        assets_table = Table(
            "assets_asset", self.metadata,
            Column("id", Integer, primary_key=True),
            Column("asset_id", String(300), nullable=False),
            Column("asset_type", String(30), nullable=False),
            Column("loc", Geometry(geometry_type=None)),
            Column("type", String(50)),
            Column("loc_psd93", Geometry(geometry_type=None)),
            Column("altitude_mode", String(300)),
            Column("asset_area", String(300)),
            Column("begin", DateTime(timezone=True)),
            Column("description", String(3000)),
            Column("draw_order", Integer),
            Column("end", DateTime(timezone=True)),
            Column("extrude", Integer),
            Column("from_loc", String(300)),
            Column("from_type", String(300)),
            Column("func_loc", String(300)),
            Column("icon", String(300)),
            Column("length_m", String(300)),
            Column("medium", String(300)),
            Column("global_id", String(300)),
            Column("owner", String(300)),
            Column("snippet", String(300)),
            Column("status", String(300)),
            Column("tessellate", Integer),
            Column("timestamp", DateTime(timezone=True)),
            Column("to_loc", String(300)),
            Column("to_type", String(300)),
            Column("util_category", String(300)),
            Column("util_name", String(300)),
            Column("util_type", String(300)),
            Column("visibility", Integer),
            Column("provisional_id", String(300))
        )
        return assets_table

