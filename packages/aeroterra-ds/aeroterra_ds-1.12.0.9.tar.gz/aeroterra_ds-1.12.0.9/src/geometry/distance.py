from haversine import haversine, Unit

from math import cos

from shapely.ops import nearest_points
from shapely import distance
from shapely.geometry import MultiLineString, Point, MultiPolygon, GeometryCollection

from .change_crs import change_crs
from .checks import is_linestring_like, is_polygon_like
from .filters import filter_collection

def distance_geometries(geom_a, geom_b, crs_a=None, crs_b=None, do_haversine=True, units=Unit.KILOMETERS):
    """
    Given 2 shapely geometries, it returns the distance between them

    Parameters:
        - geom_a: First geometry to compare
        - geom_b: Seconda geometry to compare
        - crs_a: CRS of the geom_a. If not given and asked for haversine,
            epsg:4326 will be assumed.
        - crs_b: CRS of the geom_b. If not given and asked for haversine,
            epsg:4326 will be assumed.
        - do_haversine (Optional): If wanted to check the distance in haversine.
            By default in True.
        - units (Optional): If using haversine, what unit to return. Must use 
            Haversine.Units strcuture like element. By default in Kilometers
    """
    if not do_haversine and crs_a and crs_b and crs_b != crs_a:
        raise Exception("Can't Use Different CRS for non haversine distance")
    
    if do_haversine and crs_a != 4326:
        geom_a = change_crs(geom_a, crs_a, 4326)
    
    if do_haversine and crs_b != 4326:
        geom_b = change_crs(geom_b, crs_b, 4326)
    
    point_a, point_b = nearest_points(geom_a, geom_b)

    if not do_haversine:
        return distance(point_a, point_b)
    else:
        point_a = (point_a.y, point_a.x)
        point_b = (point_b.y, point_b.x)
        return haversine(point_a, point_b, unit=units)


def line_length(line, crs=None, do_haversine=True, units=Unit.KILOMETERS):
    """
    Given a shapely line, it returns the length of it

    Parameters:
        - line: Line to get the length of
        - crs: CRS of the line. If not given and asked for haversine,
            epsg:4326 will be assumed.
        - do_haversine (Optional): If wanted to check the distance in haversine.
            By default in True.
        - units (Optional): If using haversine, what unit to return. Must use 
            Haversine.Units strcuture like element. By default in Kilometers
    """
    if not is_linestring_like(line):
        raise Exception("Not Valid Line Input Type")

    if not do_haversine:
        return line.length
    
    if isinstance(line, MultiLineString):
        lines = list(line.geoms)
    else:
        lines = [line]
    
    total_length = 0
    for line in lines:
        if line.is_empty:
            continue
        sub_total = 0
        for i in range(1, len(line.coords)):
            start = Point(line.coords[i-1])
            end = Point(line.coords[i])

            sub_total += distance_geometries(start, end, crs, crs, do_haversine, units)
        total_length += sub_total
    
    return total_length


def estimate_area(polygon, pol_crs, unit=Unit.KILOMETERS):
    """
    Given a polygon estimates its area in decimal units 
    by calculating the envelope and keeping the area ratio 
    given by shapely.

    Parameters:
        - polygon: Shapely Multi(polygon) to calculate its area
        - pol_crs: CRS of the given polygon
        - units (Optional): If using haversine, what unit to return. Must use 
            Haversine.Units strcuture like element. By default in Kilometers
    """
    if not is_polygon_like(polygon) and not isinstance(polygon, GeometryCollection):
        #raise Exception(f"{polygon} Not A Valid Geometry To Get Area From")
        return 0

    if isinstance(polygon, MultiPolygon):
        polygons = polygon.geoms
    elif isinstance(polygon, GeometryCollection):
        collection = filter_collection(polygon, [is_polygon_like], False)
        polygons = []
        for geom in collection:
            if isinstance(geom, MultiPolygon):
                polygons.extend(geom.geoms)
            else:
                polygons.append(geom)
    else:
        polygons = [polygon]
    
    total_area = 0

    for sub_pol in polygons:
        try:
            if sub_pol.is_empty:
                continue

            envelope = sub_pol.envelope

            base_1 = Point(envelope.exterior.coords[0])
            base_2 = Point(envelope.exterior.coords[1])
            base = distance_geometries(base_1, base_2, pol_crs, pol_crs, True, unit)
            
            height_1 = base_2
            height_2 = Point(envelope.exterior.coords[2])
            height = distance_geometries(height_1, height_2, pol_crs, pol_crs, True, unit)

            real_area = sub_pol.area
            env_area = envelope.area
            if real_area == 0 or env_area == 0:
                continue
            ratio = real_area / env_area

            env_decimal_area = base * height
        except Exception as err:
            print(f"For {polygon} Error Getting Area Of {sub_pol} [Err: {err}]")
            env_decimal_area = 0
            ratio = 0

        total_area += env_decimal_area * ratio

    return total_area


def buffer_kilometers(geometries, radius, crs):
    """
    Create Buffered Points in the given radius, measured in KILOMETERS

    Parameters:
        - geometries: List of geometries or only geometry to buffer
        - radius: Length in Kilometers to buffer the geometry
        - crs: CRS of the given geometries
    """
    changed = change_crs(geometries, crs, 4326)
    buffered = []
    large_k = (180 * radius) / (3.14 * 6740)
    for geom in changed:
        if not isinstance(geom, Point):
            point = geom.centroid
        else:
            point = geom
        radius = large_k / cos(point.y  * 3.14 / 180.0)
        buffer = geom.buffer(radius)
        buffered.append(buffer)
    
    return change_crs(buffered, 4326, crs)