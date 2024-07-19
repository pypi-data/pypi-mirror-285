import numpy as np

from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, Point, MultiPoint, LinearRing

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
    
    if isinstance(possible_line, LinearRing):
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


def is_thin(polygon, filter_aspect=21):
    """
    Returns a boolean indicating if the polygon is thin.

    Parameters:
        - polygon: Shapely Polygon to check
        - filter_aspect: Ratio of the Perimeter vs Area. 
            The bigger the value the more thinner polygons
            will be accepted. By default at 21, value from 
            an average equilateral polygon
    """
    if not isinstance(polygon, Polygon):
        raise Exception(f"{polygon} Not a valid Polygon")

    perimeter = polygon.length
    area = polygon.area
    aspect = area / perimeter

    return aspect < perimeter / filter_aspect