import combinations

import geopandas as gpd

from math import cos

from rtree import index

from shapely import unary_union

from shapely.geometry import Polygon, MultiPolygon, Point, GeometryCollection

from .dataframes import create_gdf_geometries
from .change_crs import change_crs
from .checks import is_polygon_like, split_collection

def get_intersections(polygons, precise=True):
    """
    Given a list of polygons it returns the positions of those that intersect each other

    Parameters:
        - polygons: List of polygons to check
        - precise: If intersection must be secured or if it could use rtree one
    
    Returns a dictionary with List positions as key and a list of other positions intersecting
    as value
    """
    idx = index.Index()
    intersected_polygons = {}

    for i, polygon in enumerate(polygons):
        idx.insert(i, polygon.bounds)
        intersected_polygons[i] = []

    for i, polygon1 in enumerate(polygons):
        intersections = []
        for j in idx.intersection(polygon1.bounds):
            if j <= i:
                continue
            if precise or polygon1.intersects(polygons[j]):
                intersections.append(j)
                intersected_polygons[j].append(i)
        intersected_polygons[i].extend(intersections)
    
    return intersected_polygons


def create_unique_lists(intersections):
    """
    Given a dictionary of intersections it returns the unique list of joined elements

    Parameters:
        - intersections: Dict of intersections. Key: Position of element, Value: List of intersections
    """
    visited = set()
    unique_links = []

    def dfs(node, current_link):
        visited.add(node)
        current_link.append(node)

        for neighbor in intersections.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, current_link)

    for key in intersections.keys():
        if key not in visited:
            current_link = []
            dfs(key, current_link)
            unique_links.append(current_link)
    
    return unique_links


def join_by_intersections(polygons, values_column={}, precise=True):
    """
    Given a GeoDataFrame with polygons, it returns new GeoDataFrame with the set
    of intersected polygons joined.

    Parameters:
        - polygons: GeoDataFrame to join
        - values_column: Dictionary indicating new columns to create with operations
            to do with the combination.
                {new_key: [operation_type, operation_column]}
                operation_types:
                    - sum
                    - count
                    - unique
                    - max
                    - min
            By default, an empty dic meaning no new column will be created
        - precise: If intersection must be secured or if it could use rtree one
    """
    geometry_column = polygons.geometry.name
    crs = polygons.crs
    pols_list = polygons[geometry_column].to_list()
    intersections = get_intersections(pols_list, precise=precise)
    links = create_unique_lists(intersections)
    
    polygons_final = []
    
    for link in links:
        if len(link) == 0:
            continue
        polygons_current = [pols_list[i] for i in link]
        polygon = unary_union(polygons_current)
        if isinstance(polygon, Polygon):
            polygon = MultiPolygon([polygon])
        
        values = {geometry_column: polygon}
        polygons_current = polygons.iloc[link]
        for new_key, operation in values_column.items():
            metric = None
            operation_key = operation[0]
            operation_action = operation[1]
            if operation_action == "sum":
                metric = polygons_current[operation_key].sum()
            elif operation_action == "count":
                metric = polygons_current[operation_key].count()
            elif operation_action == "unique":
                metric = len(polygons_current[operation_key].unique())
            elif operation_action == "max":
                metric = polygons_current[operation_key].max()
            elif operation_action == "min":
                metric = polygons_current[operation_key].min()
            values[new_key] = metric

        polygons_final.append(values)

    return gpd.GeoDataFrame(polygons_final, geometry=geometry_column, crs=crs)


def get_polygons_hit(input_gdf, intersect_geoms, intersect_crs=None, area_perc=None):
    """
    Returns a GDF filter from the input_gdf based on those that
    intersect with intersect_geoms

    Parameters:
        - input_gdf: GDF to get the base from
        - intersect_geoms: GeoDataframe/(Multi)Polygon/(Multi)Polygons List 
            where to get the geometries from
        - intersect_crs: CRS of the given intersect_geoms. In case the geoms are 
            a GDF the crs assigned to it will be used. If set to None, it'll be
            assumed the geometries are in the same crs as input_gdf. By default,
            in None.
        - area_perc: Percentage of the original polygon needed to be
            considered a valid intersection. If None, any intersection
            will be counted.
    """
    if input_gdf.crs is None:
        raise Exception("Must Provide a CRS for the input_gdf")
    if intersect_crs is None:
        intersect_crs = input_gdf.crs

    intersect_gdf = create_gdf_geometries(intersect_geoms, intersect_crs)
    intersect_gdf = intersect_gdf.to_crs(input_gdf.crs)

    original_geoms = input_gdf.geometry.to_list()
    intersect_geoms = intersect_gdf.geometry.to_list()

    idx = index.Index()
    for i, polygon in enumerate(intersect_geoms):
        idx.insert(i, polygon.bounds)
    
    pols_keep = []
    for i, polygon in enumerate(original_geoms):
        area_needed = 0
        if area_perc is not None:
            area_needed = polygon.area * area_perc
        matches = False
        for j in idx.intersection(polygon.bounds):
            pol_intersection = polygon.intersection(intersect_geoms[j])
            if pol_intersection.is_empty or not is_polygon_like(pol_intersection):
                continue

            if pol_intersection.area >= area_needed:
                matches = True
                break
        
        if matches:
            pols_keep.append(i)
    
    return input_gdf.iloc[pols_keep]


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


def filter_thin_polygons(polygons, split_multi=False, filter_aspect=21):
    """
    Given a list of (multi)polygons it returns a 
    new list with only the non thin polygons remaining.

    Parameters:
        - polygons: List of polygons-like figures to filter
        - split_multi (Optional): If multipolygons like geometries
            should be split into polygons or if the unification should
            remain. By default at False.
        - filter_aspect: Ratio of the Perimeter vs Area. 
            The bigger the value the more thinner polygons
            will be accepted. By default at 21, value from 
            an average equilateral polygon
    """
    final_polygons = []
    for geom in polygons:
        if isinstance(geom, Polygon):
            if not is_thin(geom, filter_aspect) and geom.area > 0:
                final_polygons.append(geom)
        elif isinstance(geom, MultiPolygon):
            new_geoms = []
            for sub_pol in geom.geoms:
                if isinstance(geom, Polygon) and not is_thin(sub_pol, filter_aspect) and geom.area > 0:
                    new_geoms.append(sub_pol)
            if split_multi:
                final_polygons.extend(new_geoms)
            else:
                final_polygons.append(MultiPolygon(new_geoms))

    return final_polygons


def generate_triangles(polygon):
    """
    Generate a list of all the triangles (shapely 
    polygons) that can be formed from the vertices
    of a given polygon that area also fully contained in it.

    Note: Doesn't work for holed polygons for now. The code
    won't break but hole(s) will be ignored

    Parameters:
        - polygon: Polygon to triangularize
    """
    vertices = list(polygon.exterior.coords)
    
    triangle_vertices = combinations(vertices, 3)
    
    triangles = []
    for vertices in triangle_vertices:
        try:
            triangle = Polygon(vertices)
            if polygon.contains(triangle):
                triangles.append(triangle)
        except:
            continue
    
    return triangles


def detect_and_cut_thin_parts(polygon, filter_aspect = 100):
    """
    Detects and cuts thin parts from a Shapely polygon, 
    returning the new geometry. In case the geometry
    is not a polygon like one, an expection will be raised.

    Note: Doesn't work for holed polygons for now. The code
    won't break but hole(s) will be ignored

    Parameters:
        - polygon: Shapely Polygon object to split.
        - filter_aspect: Ratio of the Perimeter vs Area. 
            The bigger the value the more thinner polygons
            will be accepted. By default at 10, five times the value 
            of an average equilateral polygon
    """
    triangles = generate_triangles(polygon)
    if len(triangles) == 0:
        return polygon
    
    not_thin_triangles = []
    total_area = polygon.area
    same_area = total_area * 0.01
    
    for j, triangle in enumerate(triangles):
        intersection = triangle.difference(polygon)
        if intersection.area > same_area:
            continue

        if not is_thin(triangle, filter_aspect):
            not_thin_triangles.append(triangle)
    
    response = unary_union(not_thin_triangles)

    if is_polygon_like(response):
        return response
    elif isinstance(response, GeometryCollection):
        return split_collection(response, is_polygon_like)
    else:
        return None