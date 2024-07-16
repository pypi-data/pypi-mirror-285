from haversine import haversine, Unit

from shapely.ops import nearest_points
from shapely import distance
from shapely.geometry import MultiLineString, Point

from .change_crs import change_crs
from .checks import is_linestring_like

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
        sub_total = 0
        for i in range(1, len(line.coords)):
            start = Point(line.coords[i-1])
            end = Point(line.coords[i])

            sub_total += distance_geometries(start, end, crs, crs, do_haversine, units)
        total_length += sub_total
    
    return total_length