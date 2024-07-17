import numpy as np

from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, Point, MultiPoint, GeometryCollection

def is_number(value):
    """
    Returns true if the value is a number-like structure

    Parameters:
        - value: Parameter to check if a number like structure
    """
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, np.number):
        return True

    if isinstance(value, complex):
        return True

    return False


def is_box_polygon(possible_box_pol):
    """
    Returns true if the value is a box polygon

    Parameters:
        - possible_box_pol: Parameter to check if a box polygon
    """
    if not isinstance(possible_box_pol, Polygon):
        return False
    
    if len(possible_box_pol.exterior.coords) != 5:
        return False
    
    pol_box = possible_box_pol.envelope

    return pol_box.difference(possible_box_pol).area == 0


def is_bbox(possible_bbox):
    """
    Returns true if the value is a bbox-like structure

    Parameters:
        - possible_bbox: Parameter to check if a bbox like structure
    """
    if is_box_polygon(possible_bbox):
        return True

    if not isinstance(possible_bbox, tuple) and not isinstance(possible_bbox, list):
        return False
    
    if len(possible_bbox) != 4:
        return False
    
    if not is_number(possible_bbox[0]):
        return False

    if possible_bbox[2] <= possible_bbox[0]:
        return False
    
    if possible_bbox[3] <= possible_bbox[1]:
        return False
    
    return True    


def is_polygon_like(possible_polygon):
    """
    Returns true if the value is a polygon-like structure

    Parameters:
        - possible_polygon: Parameter to check if a polygon like structure
    """
    if isinstance(possible_polygon, Polygon):
        return True
    
    if isinstance(possible_polygon, MultiPolygon):
        return True
    
    return False


def is_linestring_like(possible_line):
    """
    Returns true if the value is a linestring-like structure

    Parameters:
        - possible_line: Parameter to check if a linestring like structure
    """
    if isinstance(possible_line, LineString):
        return True
    
    if isinstance(possible_line, MultiLineString):
        return True
    
    return False


def is_point(possible_point):
    """
    Returns true if the value is a point-like structure

    Parameters:
        - possible_point: Parameter to check if a point like structure
    """
    if isinstance(possible_point, Point):
        return True
    
    if not isinstance(possible_point, tuple) and not isinstance(possible_point, list):
        return False
    
    if len(possible_point) != 2:
        return False
    
    return True


def point_in_bbox(point, bbox):
    """
    Returns true if the point (x, y) is iniside the bbox (min_x, min_y, max_x, max_y)

    Parameters:
        - point: Point to check if inside box
        - bbox: Bounding Box to check for
    """
    if not is_bbox(bbox):
        raise Exception("Invalid bbox")
    
    if not is_point(point):
        raise Exception("Invalid point")
    
    if isinstance(bbox, Polygon):
        bbox = bbox.bounds
    
    if isinstance(point, Point):
        point = (point.x, point.y)
    

    if point[0] < bbox[0]:
        return False
    if point[1] < bbox[1]:
        return False
    if point[0] > bbox[2]:
        return False
    if point[1] > bbox[3]:
        return False
    
    return True
    

def is_multi_geometry(possible_multi):
    """
    Returns true if the value is a multigeometry structure

    Parameters:
        - possible_multi: Parameter to check if a multigeometry structure
    """
    if isinstance(possible_multi, MultiPolygon):
        return True

    if isinstance(possible_multi, MultiLineString):
        return True

    if isinstance(possible_multi, MultiPoint):
        return True
    
    return False

def is_single_geometry(possible_single):
    """
    Returns true if the value is a single geometry structure

    Parameters:
        - possible_single: Parameter to check if a single geometry structure
    """
    if isinstance(possible_single, Polygon):
        return True

    if isinstance(possible_single, LineString):
        return True

    if isinstance(possible_single, Point):
        return True
    
    return False


def is_geometry(possible_geom):
    """
    Returns true if the value is a geometry structure

    Parameters:
        - possible_geom: Parameter to check if a geometry structure
    """
    return is_multi_geometry(possible_geom) or is_single_geometry(possible_geom)


def filter_collection(collection, check_functions, join_geoms=True):
    """
    Given a Geometry Collection filter out keeping all the 
    geometries that passes the given function.

    Parameters:
        - collection: GeometryCollection to split
        - check_function: List of functions to check the type of the 
            geometry. The function expect only 1 parameter, being 
            that the geometry to check.
        - join_geoms (Optional): If the filtered geometries should be joined
            to a only one. If not, a list of geometries will be returned
    """

    if not isinstance(collection, GeometryCollection):
        raise Exception(f"Not A Valid Collection [{collection}]")

    response_geometries = []
    for geom in collection.geoms:
        for check in check_functions:
            if check(geom):
                response_geometries.append(geom)
    
    if len(response_geometries) == 0:
        return None
    elif join_geoms:
        return unary_union(response_geometries)
    else:
        return response_geometries
