import itertools
from typing import List, Tuple , Optional, Union
from shapely import geometry
import numpy as np
from joblib import Parallel, delayed
import multiprocessing as mp
from functools import partial
import cv2

from .camera_handler import Camera
from .abstracts import Polygon , AssetType ,Box

ECC_POLYGON_COLOR = {
    AssetType.Well: 255,
    AssetType.Pipe: 191,
    AssetType.Pipeline: 191,
    AssetType.Flowline: 191,
    AssetType.Road: 127,
    AssetType.Powerline: 63
}
ECC_POLYGON_COLOR.update({
    k.value: v for k, v in ECC_POLYGON_COLOR.items()
})

ECC_POLYGON_DRAW_ORDER = {
    AssetType.Well: 2,
    AssetType.Pipe: 4,
    AssetType.Pipeline: 1,
    AssetType.Flowline: 5,
    AssetType.Road: 3,
    AssetType.Powerline: 0
}  # smaller number first
ECC_POLYGON_DRAW_ORDER.update({
    k.value: v for k, v in ECC_POLYGON_DRAW_ORDER.items()
})


def densify_geometry(line_geometry: List[Tuple[float, float]], step: float) -> List[Tuple[float, float]]:
    # taken from https://gis.stackexchange.com/a/373279
    # step: add a vertice every step in whatever unit your coordinate reference system use.

    line_geometry = geometry.LineString(line_geometry)
    length_m=line_geometry.length # get the length

    xy=[] # to store new tuples of coordinates

    for distance_along_old_line in np.arange(0,length_m,step): 

        point = line_geometry.interpolate(distance_along_old_line) # interpolate a point every step along the old line
        xp,yp = point.x, point.y # extract the coordinates

        xy.append((xp,yp)) # and store them in xy list

    return xy

def to_visible_image_polygons(
        polyline: List[Tuple[float, float]],
        camera: Camera,
        asset_width: float,
        simplify_tol=0.
) -> Tuple[List[List[Tuple[int, int]]], List[List[Tuple[int, int]]], List[Tuple[int, int]]]:
    polylines = get_visible_polylines(polyline, camera)
    w, h = camera.image_width - 1 , camera.image_height - 1
    image_borders = geometry.Polygon([(0,0), (0,h), (w, h), (w, 0)])
    visible_polylines , visible_polygons = [], []
    for pline in polylines:
        if len(pline) == 1:
            polygon: geometry.Polygon = geometry.Point(pline).buffer(
                asset_width, cap_style="round")
        elif len(pline) > 1:
            polygon: geometry.Polygon = geometry.LineString(pline).buffer(
                asset_width, cap_style="flat")
        else:
            continue
        if isinstance(polygon, geometry.MultiPolygon):
            polygon = list(polygon.geoms)[0]
        polygon = polygon.intersection(image_borders)
        if simplify_tol > 0.:
            polygon = polygon.simplify(simplify_tol)
        polygon = list(polygon.exterior.coords)
        if not polygon:
            continue
        visible_polylines.append(pline)
        visible_polygons.append(polygon)
    return visible_polygons, visible_polylines, list(image_borders.exterior.coords)



def get_visible_polylines(
        polyline_wc: List[Tuple[int, int]], camera: Camera) -> List[List[Tuple[int, int]]]:
    """Convert polyline from world coordinates into image coordinates,
    then check if such coordinate is in the image.
    This process may break a polyline into multiple segment of polylines,
    and only coordinates that are in the image are returned."""
    if not len(polyline_wc):
        return []
    w, h = camera.image_width - 1 , camera.image_height - 1
    image_border_lines = [
        [(0, 0), (0, h)],
        [(0, h), (w, h)],
        [(w, h), (w, 0)],
        [(w, 0), (0, 0)]]
    polyline_wc = np.array(polyline_wc, dtype=np.float64)
    polyline_ics = camera.world_coords_to_image_coords(
        asset_lats=polyline_wc[:, 1], asset_longs=polyline_wc[:, 0], return_outside=True)
    total_ics = len(polyline_ics)
    def is_inside(p):
        x, y = p
        return not (x < 0 or y < 0 or x >= camera.image_width or y >= camera.image_height)
    if total_ics == 1:
        return [[polyline_ics[0]]] if is_inside(polyline_ics[0]) else []
    polyline_vis_rle = rle(list(map(is_inside, polyline_ics)))
    visible_polylines = []
    for n, s, vis in zip(*polyline_vis_rle):
        if not vis:
            continue
        pline = []
        # add start point that extends to the edge of the image
        if s > 0:
            for bline in image_border_lines:
                isct_p = intersect(polyline_ics[s-1], polyline_ics[s], *bline)
                if isct_p is None:
                    continue
                pline.append((round(isct_p[0]), round(isct_p[1])))
        # add the points
        pline.extend(polyline_ics[s:s+n])
        # add end point that extends to the edge of the image
        if s+n < total_ics:
            for bline in image_border_lines:
                isct_p = intersect(pline[-1], polyline_ics[s+n], *bline)
                if isct_p is None:
                    continue
                pline.append((round(isct_p[0]), round(isct_p[1])))
        visible_polylines.append(pline)
    return visible_polylines

def rle(inarray):
    """ run length encoding. Partial credit to R rle function. 
        Multi datatype arrays catered for including non Numpy
        returns: tuple (runlengths, startpositions, values).
        Taken from: <https://stackoverflow.com/a/32681075>"""
    ia = np.asarray(inarray)                # force numpy
    n = len(ia)
    if n == 0: 
        return (None, None, None)
    else:
        y = ia[1:] != ia[:-1]               # pairwise unequal (string safe)
        i = np.append(np.where(y), n - 1)   # must include last element posi
        z = np.diff(np.append(-1, i))       # run lengths
        p = np.cumsum(np.append(0, z))[:-1] # positions
        return(z, p, ia[i])
    

def intersect(p1, p2, p3, p4):
    """Intersection between line(p1, p2) and line(p3, p4).
    Taken from <https://gist.github.com/kylemcdonald/6132fc1c29fd3767691442ba4bc84018>."""
    x1,y1 = p1
    x2,y2 = p2
    x3,y3 = p3
    x4,y4 = p4
    denom = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
    if denom == 0: # parallel
        return None
    ua = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / denom
    if ua < 0 or ua > 1: # out of range
        return None
    ub = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / denom
    if ub < 0 or ub > 1: # out of range
        return None
    x = x1 + ua * (x2-x1)
    y = y1 + ua * (y2-y1)
    return (x,y)

def calculate_intersection(polygons_mask, boxes_mask):
    combined_mask = cv2.bitwise_and(polygons_mask, boxes_mask)
    cv2.imwrite("samples/refine_camera/dummy_polygons.jpg", polygons_mask)
    cv2.imwrite("samples/refine_camera/dummy_boxes.jpg", boxes_mask)
    cv2.imwrite("samples/refine_camera/dummy.jpg", combined_mask)
    intersected_pixels = np.sum(combined_mask == 255)
    total_intersected_pixels = np.sum(boxes_mask == 255)
    intersection_percentage = intersected_pixels / total_intersected_pixels * 100
    return intersection_percentage

def get_polygons(
        asset: dict, asset_width: float,
        camera, densify_assets, simplify_tol) -> List[Polygon]:
    if not len(asset["coords"]):
        return []
    if len(asset["coords"]) > 1:
        line = asset["coords"]
        if densify_assets:
            line = densify_geometry(line, step=0.00001)
        polygons, segments, image_borders = to_visible_image_polygons(
            polyline=line, camera=camera, asset_width=asset_width, simplify_tol=simplify_tol)
    elif len(asset["coords"]) == 1:
        if densify_assets:
            polygons, segments, image_borders = to_visible_image_polygons(
                polyline=asset["coords"], camera=camera, asset_width=asset_width, simplify_tol=simplify_tol)
        else:
            polylines = get_visible_polylines(asset["coords"], camera)
            polygons = polylines
            segments = polylines
    ps = [
        Polygon(
            id=asset["id"], coords=polygon, linestring=segment,
            attributes=asset["attributes"], type=asset["type"])
        for polygon, segment in zip(polygons, segments)]
    return ps

def construct_polygons(
            self,
            assets: List[dict],
            asset_width: float,
            camera,
            focused_types: Optional[List[AssetType]] = None,
            densify_assets=False,
            simplify_tol=0.) -> List[Polygon]:
            
        func_get_polygons = partial(
            get_polygons,
            asset_width=asset_width, camera=camera,
            densify_assets=densify_assets, simplify_tol=simplify_tol)
        if focused_types is None:
            _iterator = assets
        else:
            _iterator = filter(lambda a: a["type"] in focused_types, assets)
        # final_polygons = list(itertools.chain(*[
        #     func_get_polygons(asset)
        #     for asset in _iterator]))
        final_polygons = list(itertools.chain(*Parallel(n_jobs=mp.cpu_count())(
            delayed(func_get_polygons)(asset)
            for asset in _iterator)))
        return final_polygons

def draw_boxes(detections, boxes_mask, method):
    for box in sorted(detections, key=lambda o: ECC_POLYGON_DRAW_ORDER[o.type]):
        pt1 = (box.x + box.w // 2, box.y + box.h // 2)
        pt2 = (box.x - box.w // 2, box.y - box.h // 2)
        
        if method == 'ls_ecc' and box.type is AssetType.Well:
            continue
        
        if method == 'ls_ecc':
            color = 255
            cv2.rectangle(boxes_mask, pt1, pt2, color, thickness=-1)
        else:
            color = ECC_POLYGON_COLOR[box.type]
            cv2.circle(boxes_mask, (box.x, box.y), box.w // 2, color, thickness=-1)

def draw_polygons(kml_polygons, polygons_mask, method):
    for polygon in sorted(kml_polygons, key=lambda o: ECC_POLYGON_DRAW_ORDER[o.type]):
        points = np.array(polygon.coords, dtype=np.int32)
        
        if method == 'ls_ecc':
            color = 255
        else:
            color = ECC_POLYGON_COLOR[polygon.type]
            
        cv2.fillPoly(polygons_mask, [points], color)

def resize_masks(mask, rescale):
    new_size = (int(rescale * mask.shape[1]), int(rescale * mask.shape[0]))
    return cv2.resize(mask, new_size, interpolation=cv2.INTER_CUBIC)

def save_debug_images(boxes_mask, polygons_mask, method):
    cv2.imwrite(f"samples/refine_camera/boxes_mask_{method}.jpg", boxes_mask)
    cv2.imwrite(f"samples/refine_camera/polygons_mask_{method}.jpg", polygons_mask)

def calculate_transformation_matrix(
        detections: List[Box],
        kml_polygons: List[Polygon],
        camera,
        method: str,
        motionType=cv2.MOTION_AFFINE,
        rescale=0.1,
        debug=False):
    
    # Initialize masks
    boxes_mask = np.zeros((camera.image_height, camera.image_width), dtype=np.uint8)
    polygons_mask = np.zeros((camera.image_height, camera.image_width), dtype=np.uint8)

    # Draw boxes and polygons on masks
    draw_boxes(detections, boxes_mask, method)
    draw_polygons(kml_polygons, polygons_mask, method)

    # Resize masks
    boxes_mask = resize_masks(boxes_mask, rescale)
    polygons_mask = resize_masks(polygons_mask, rescale)

    # Save debug images if required
    if debug:
        save_debug_images(boxes_mask, polygons_mask, method)

    # Calculate transformation matrix
    try:
        _, W = cv2.findTransformECC(
            polygons_mask, boxes_mask,
            warpMatrix=None, motionType=motionType,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10000, 1e-5))
        
        W2 = W.copy()
        W2[:, 2] *= 10
        print("OK!")
    except Exception as e:
        W2 = np.array([[1, 0, 0], [0, 1, 0]])
        print((
            "Failed to do findTransformECC. "
            "len(detections)=%d len(kml_polygons)=%d. "
            "Fall back to identity transformation matrix. "
            "Reason: %s") % (len(detections), len(kml_polygons), str(e)))
    
    return W2


