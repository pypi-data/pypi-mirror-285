from shapely.geometry import Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon
from arcgis.geometry import Geometry


def create_geo_json_point(point):
    """
    Given a shapely Point, it transforms the structure into a Json for ArcGIS
    
    Parameters:
        point: Shapely point to transform.
        crs: The CRS of the point to transform.
    
    Returns a dictionary
    """
    if not isinstance(point, Point):
        raise Exception("Geometry Must Be A Point")
    
    geo_json = {}
    geo_json["x"] = point.x
    geo_json["y"] = point.y
    
    return geo_json


def create_geo_json_multipoint(multipoint):
    """
    Given a shapely MultiPoint, it transforms the structure into a Json for ArcGIS

    Parameters:
        multipoint: Shapely MultiPoint to transform.
        crs: The CRS of the point to transform.

    Returns a dictionary
    """
    if not isinstance(multipoint, MultiPoint):
        raise Exception("Geometry Must Be A MultiPoint")
        
    geo_json = {}
    points = []
    for point in multipoint.geoms:
        aux_point = (point.x, point.y)
        points.append(aux_point)
    geo_json["points"] = points
    
    return geo_json


def create_geo_json_line(linestring):
    """
    Given a shapely LineString, it transforms the structure into a Json for ArcGIS

    Parameters:
        linestring: Shapely LineString to transform.
        crs: The CRS of the point to transform.

    Returns a dictionary
    """
    if not isinstance(linestring, LineString):
        raise Exception("Geometry Must Be A LineString")
    
    geo_json = {}
    paths = []
    for point in linestring.coords:
        paths.append(point)
    geo_json["paths"] = [paths]
    
    return geo_json


def create_geo_json_multiline(multiline):
    """
    Given a shapely MultiLineString, it transforms the structure into a Json for ArcGIS

    Parameters:
        multiline: Shapely MultiLineString to transform.
        crs: The CRS of the point to transform.

    Returns a dictionary
    """
    if not isinstance(multiline, MultiLineString):
        raise Exception("Geometry Must Be A MultiLineString")
    
    geo_json = {}
    paths = []
    for line in multiline.geoms:
        aux_path = []
        for point in line.coords:
            aux_path.append(point)
        paths.append(aux_path)
    geo_json["paths"] = paths
    
    return geo_json


def create_geo_json_polygon(polygon):
    """
    Given a shapely Polygon, it transforms the structure into a Json for ArcGIS

    Parameters:
        polygon: Shapely Polygon to transform.
        crs: The CRS of the point to transform.

    Returns a dictionary
    """
    if not isinstance(polygon, Polygon):
        raise Exception("Geometry Must Be A Polygon")
    
    geo_json = {}
    external_ring = []
    for point in reversed(polygon.exterior.coords):
        external_ring.append(point)

    rings = [external_ring]
    for hole in polygon.interiors:
        aux_ring = []
        for point in reversed(hole.coords):
            aux_ring.append(point)
        rings.append(aux_ring)

    geo_json["rings"] = rings
    
    return geo_json

def create_geo_json_multipolygon(multipolygon):
    """
    Given a shapely MultiPolygon, it transforms the structure into a Json for ArcGIS

    Parameters:
        multipolygon: Shapely MultiPolygon to transform.
        crs: The CRS of the point to transform.

    Returns a dictionary
    """
    if not isinstance(multipolygon, MultiPolygon):
        raise Exception("Geometry Must Be A MultiPolygon")
    
    geo_json = {}
    rings = []
    for polygon in multipolygon.geoms:
        external_ring = []
        for point in reversed(polygon.exterior.coords):
            external_ring.append(point)
        rings.append(external_ring)

        for hole in polygon.interiors:
            aux_ring = []
            for point in reversed(hole.coords):
                aux_ring.append(point)
            rings.append(aux_ring)

    geo_json["rings"] = rings
    
    return geo_json


def create_geo_json(geometry, crs):
    """
    Given a shapely geometry, it transforms the structure into a Json for ArcGIS
    
    Parameters:
        geometry: Shapely geometry to transform.
        crs: The CRS of the geometry to transform.
    
    Returns a dictionary
    """
    if not isinstance(crs, int):
        raise Exception("CRS Must Be An Int")

    geo_json = None
    
    if isinstance(geometry, Point):
        geo_json = create_geo_json_point(geometry)
    elif isinstance(geometry, MultiPoint):
        geo_json = create_geo_json_multipoint(geometry)
    elif isinstance(geometry, LineString):
        geo_json = create_geo_json_line(geometry)
    elif isinstance(geometry, MultiLineString):
        geo_json = create_geo_json_multiline(geometry)
    elif isinstance(geometry, Polygon):
        geo_json = create_geo_json_polygon(geometry)
    elif isinstance(geometry, MultiPolygon):
        geo_json = create_geo_json_multipolygon(geometry)
    
    if geo_json is None:
        raise Exception("Couldn't Find A Valid Geometry Type")
    
    geo_json["spatialReference"] = {"wkid": crs}

    return geo_json


def get_arcgis_geometry(geometry, crs):
    """
    Given a shapely geometry, it transforms the structure into an arcgis Geometry
    
    Parameters:
        geometry: Shapely geometry to transform.
        crs: The CRS of the geometry to transform.
    
    Returns a dictionary
    """
    geo_json = create_geo_json(geometry, crs)
    return Geometry(geo_json)