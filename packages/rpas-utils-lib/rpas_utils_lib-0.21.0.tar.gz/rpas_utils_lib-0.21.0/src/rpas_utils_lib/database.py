from argparse import ArgumentParser
from urllib.parse import quote_plus
import logging
import json

from sqlalchemy import create_engine, MetaData, select, insert, update
from typing import List
from shapely.wkb import loads

from .abstracts import Batch ,Box, PointAsset, LinearAsset, Polygon , PointAssetsResults, LinearAssetsResults
from .tables import RPASTables

LOGGER = logging.getLogger("rpas")


class DatabaseInterface:
    def __init__(self, args) -> None:
        LOGGER.debug("Creating a database interface instance...")
        self.host = args.host
        self.port = args.port
        self.username = args.username
        self.password = args.password
        self.db_name = args.db_name
        # Helpers.write_pickle(args, Constants.Database.configuration_file_path)  # save arguments in filesystem 
        
        self.engine = create_engine(f"postgresql://{self.username}:{quote_plus(self.password)}@{self.host}:{self.port}/{self.db_name}")
        self.metadata = MetaData()

        self.tables = RPASTables(self.metadata)
        self.missions_image_table = self.tables.build_missions_image()
        self.ai_annotations_table = self.tables.build_ai_annotation_table()
        self.assets_table = self.tables.build_assets_table()

        self.connection = self.engine.connect()
        LOGGER.debug("A database interface instance was created!")

    def table_names(self) -> List[str]:
        return self.engine.table_names()

    def load_batch_path(self, batch: Batch) -> Batch:
        """This function will take a batch of images of type Batch, get the image ids and load the images paths and return the batch with the paths

        Args:
            batch (Batch): Batch that will be processed

        Returns:
            Batch: Processed batch
        """
        with self.engine.connect() as connection:  # since this is read-only, we do not use .begin()
            images_ids = [item.image_id for item in batch.items]
            stmt = select(
                self.missions_image_table.c.link,
                self.missions_image_table.c.id
            ).where(self.missions_image_table.c.id.in_(images_ids))
            result = connection.execute(stmt).fetchall()
            id_path_map = {r[1]: r[0] for r in result}

            for item in batch.items:
                image_id = item.image_id
                if image_id not in id_path_map.keys():
                    item.exists = False
                else:
                    item.path = id_path_map[image_id]
                    item.exists = True

            return batch

    def load_batch_meta(self, batch: Batch) -> Batch:
        """This function will take a batch of images of type Batch, get the image ids and load the images metadata and return the batch with the metadata

        Args:
            batch (Batch): Batch that will be processed

        Returns:
            Batch: Processed batch
        """
        with self.engine.connect() as connection:  # since this is read-only, we do not use .begin()
            images_ids = [item.image_id for item in batch.items]
            stmt = select(
                self.missions_image_table.c.metadata,
                self.missions_image_table.c.id
            ).where(self.missions_image_table.c.id.in_(images_ids))
            result = connection.execute(stmt).fetchall()
            id_path_map = {r[1]:json.loads(r[0]) for r in result}

            for item in batch.items:
                image_id = item.image_id
                if image_id not in id_path_map.keys():
                    item.exists = False
                else:
                    item.metadata = id_path_map[image_id]
                    item.exists = True
            
            return batch        

    def load_batch_detections(self, batch: Batch) -> Batch:
        """This function will take a batch of images of type Batch, get the image ids and load the images annotation (point and linear assets) and return the batch with the annotation

        Args:
            batch (Batch): Batch that will be processed

        Returns:
            Batch: Processed batch
        """
        with self.engine.connect() as connection:  # since this is read-only, we do not use .begin()
            for item in batch.items:
                image_id = item.image_id
                point_assets = PointAssetsResults()
                linear_assets = LinearAssetsResults()
                stmt = select(
                    self.ai_annotations_table.c.id,
                    self.ai_annotations_table.c.annotation_type,
                    self.ai_annotations_table.c.detection_result
                ).where(self.ai_annotations_table.c.image_id == image_id)
                # Do something to edit this line
                results = connection.execute(stmt).fetchall()
                for result in results:
                    db_key, annotation_type, detections = result[0], result[1], json.loads(result[2])
                    if annotation_type == 0:  # Point Asset
                        det = detections["box"][0]
                        box = Box(
                            x = det["x"],
                            y = det["y"],
                            w = det["w"],
                            h = det["h"],
                            type=det["type"],
                            confidence=det["confidence"]
                        )
                        point_assets.assets.append(PointAsset(box=box, type=box.type, db_key=db_key))
                    else:  # Linear Asset
                        det = detections["polygons"][0]
                        polygon = Polygon(
                            id=det["id"],
                            type=det["type"],
                            coords=det["coords"])
                        la = LinearAsset(polygon=polygon, type=polygon.type, asset_id=polygon.id, db_key=db_key)
                        linear_assets.assets.append(la)
            
                item.point_assets = point_assets
                item.linear_assets = linear_assets

            return batch         

    def write_batch_detections(self, batch: Batch) -> None:
        """This function takes the batch and extracts the point asets [BOXES] and insert them in the database

        Args:
            batch (Batch): The annotated batch with the detections
        """
        with self.engine.begin() as connection:
            for item in batch.items:
                image_id = item.image_id
                # Do something to write the (meta.point_assets) in the database
                for asset in item.point_assets.assets:
                    payload = {
                        "boxes":[
                            {
                                "x": asset.box.x,
                                "y": asset.box.y,
                                "w": asset.box.w,
                                "h": asset.box.h,
                                "type": asset.type.value,
                                "confidence": asset.box.confidence}]}
                    anomalies = [
                        anomaly.to_dict(serialize=True)
                        for anomaly in asset.anomalies]
                    anomalies = {"boxes": anomalies}
                    stmt = insert(self.ai_annotations_table).values(
                        detection_result=payload,
                        image_id=image_id,
                        annotation_type=0,
                        detected_asset_type=asset.type.value,
                        detected_anomaly_id=0
                    ).returning(self.ai_annotations_table.c.id)
                    result = connection.execute(stmt)
                    asset.db_key = result.fetchall()[0][0]

    def write_point_assets_boxes(self, batch: Batch) -> None:
        """This function writes the point assets results after the whole batch being processed (detections, ids, anomalies)

        Args:
            batch (Batch): The annotated batch with the detections
        """
        with self.engine.begin() as connection:
            for item in batch.items:
                image_id = item.image_id
                # Do something to write the (meta.point_assets) in the database
                for asset in item.point_assets.assets:
                    detection_results = {
                        "box":[{
                            "x": asset.box.x,
                            "y": asset.box.y,
                            "w": asset.box.w,
                            "h": asset.box.h,
                            "type": asset.type.value,
                            "confidence": asset.box.confidence}]}

                    identification_results = {"asset": asset.asset_id}
                    detected_asset_id=str(asset.asset_id)

                    anomalies = [
                        anomaly.to_dict(serialize=True)
                        for anomaly in asset.anomalies]
                    anomalies = {"boxes": anomalies}
                    
                    stmt = insert(self.ai_annotations_table).values(
                        detection_result=detection_results,
                        detected_asset_type=asset.type.value,
                        image_id=image_id,
                        annotation_type=0,
                        identification_result=identification_results,
                        detected_asset_id=detected_asset_id,
                        anomaly_detection_result=anomalies,
                        detected_anomaly_id=0
                    ).returning(self.ai_annotations_table.c.id)
                    result = connection.execute(stmt.execution_options(autocommit=True))
                    asset.db_key = result.fetchall()[0][0]
                LOGGER.debug(
                    "%s: %d point assets were written to DB",
                    image_id, len(item.point_assets.assets))
                LOGGER.debug(
                    "%s: db_keys: %s",
                    image_id, str([asset.db_key for asset in item.point_assets.assets]))

    def write_linear_assets_polygons(self, batch: Batch) -> None:
        """This function writes the linear assets results after the whole batch being processed (detections, ids, anomalies)

        Args:
            batch (Batch): The annotated batch with the detections
        """
        with self.engine.begin() as connection:
            for item in batch.items:
                image_id = item.image_id
                
                for asset in item.linear_assets.assets:
                    detection_results = {
                        "polygons": [{
                            "type": asset.polygon.type,
                            "coords": asset.polygon.coords,
                            "id": asset.polygon.id}]}

                    identification_results = {"asset": asset.asset_id}
                    detected_asset_id=str(asset.asset_id)

                    anomalies = [
                        anomaly.to_dict(serialize=True)
                        for anomaly in asset.anomalies]
                    anomalies = {"boxes": anomalies}
                    
                    stmt = insert(self.ai_annotations_table).values(
                        detection_result=detection_results,
                        detected_asset_type=asset.type.value,
                        image_id=image_id,
                        annotation_type=1,
                        identification_result=identification_results,
                        detected_asset_id=detected_asset_id,
                        anomaly_detection_result=anomalies,
                        detected_anomaly_id=0
                    ).returning(self.ai_annotations_table.c.id)
                    result = connection.execute(stmt.execution_options(autocommit=True))
                    asset.db_key = result.fetchall()[0][0]
                LOGGER.debug(
                    "%s: %d linear assets were written to DB",
                    image_id, len(item.linear_assets.assets))
                LOGGER.debug(
                    "%s: db_keys: %s",
                    image_id, str([asset.db_key for asset in item.linear_assets.assets]))

    def write_batch_identifications(self, batch: Batch) -> None:
        """This function takes the batch with point assets [Identified boxes] and update the DB and linear assets [Identified polygons] and insert them into the DB 

        Args:
            batch (Batch): The annotated batch with the assets identifications
        """
        with self.engine.begin() as connection:
            for item in batch.items:
                all_assets = item.point_assets.assets
                for asset in all_assets:
                    stmt = update(self.ai_annotations_table).where(
                        self.ai_annotations_table.c.id == asset.db_key
                    ).values(
                        identification_result={"asset": asset.asset_id},
                        detected_asset_id=str(asset.asset_id))
                    connection.execute(stmt)
        
        self.write_linear_assets_polygons(batch)

    def write_batch_anomalies(self, batch: Batch) -> None:
        """This function should take the annotated only with the assets anomalies classification and write it to the Database

        Args:
            batch (Batch): The annotated batch with the assets anomalies classification
        """
        with self.engine.begin() as connection:
            for item in batch.items:
                all_assets = item.point_assets.assets + item.linear_assets.assets
                for asset in all_assets:
                    stmt = update(self.ai_annotations_table).where(
                        self.ai_annotations_table.c.id == asset.db_key
                    ).values(
                        anomaly_detection_result={"anomaly": asset.anomalies},
                        detected_anomaly_id=str(asset.anomalies)
                    )
                    connection.execute(stmt)

    def write_batch(self, batch: Batch) -> None:
        self.write_point_assets_boxes(batch)
        self.write_linear_assets_polygons(batch)

    def load_kmls(self, kmls: List[str]) -> dict:
        output_kmls = []
        with self.engine.connect() as connection:  # since this is read-only, we do not use .begin()
            stmt = select(
                self.assets_table.c.asset_type,
                self.assets_table.c.asset_id,
                self.assets_table.c.loc
            ).where(self.assets_table.c.asset_id.in_(kmls))
            result = connection.execute(stmt).fetchall()
            LOGGER.debug(result)
            for row in result:
                LOGGER.debug(row.loc.data)
                geometry = loads(row.loc.data)
                kml = {
                    "asset_id": row.asset_id,
                    "asset_type": row.asset_type,
                    "coords": list(geometry.coords)
                    }
                output_kmls.append(kml)
            LOGGER.debug(kmls)



if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--host", default="172.16.0.203", help="Database host ip")
    parser.add_argument("--port", default="5432", help="Database host port")
    parser.add_argument("--username", default="esbaar", help="Database username")
    parser.add_argument("--password", default="password", help="Database password")
    parser.add_argument("--db_name", default="rpas", help="Database name")


    arguments = parser.parse_args()
    
    db = DatabaseInterface(arguments)
    LOGGER.info(db.table_names())

