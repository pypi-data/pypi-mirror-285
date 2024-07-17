import pyproj
from shapely.geometry import Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon
from shapely.ops import unary_union

from pandas import DataFrame
import geopandas as gpd

def change_crs_polygon(polygon, crs_fuente, crs_final):
    src_origen = pyproj.CRS(crs_fuente)
    src_destino = pyproj.CRS(crs_final)
    transformador = pyproj.Transformer.from_crs(src_origen, src_destino, always_xy=True)

    transformed_exterior = [transformador.transform(v[0], v[1]) for v in polygon.exterior.coords]
    transformed_interiors = [[transformador.transform(v[0], v[1]) for v in hole.coords] for hole in polygon.interiors]

    return Polygon(transformed_exterior, transformed_interiors)


def change_crs_tuple_point(punto, crs_in, crs_out):
    src_origen = pyproj.CRS(crs_in)
    src_destino = pyproj.CRS(crs_out)
    transformador = pyproj.Transformer.from_crs(src_origen, src_destino, always_xy=True)
    
    x=punto[0]
    y=punto[1]
    
    return transformador.transform(x, y)


def change_crs_point(punto, crs_in, crs_out):
    src_origen = pyproj.CRS(crs_in)
    src_destino = pyproj.CRS(crs_out)
    transformador = pyproj.Transformer.from_crs(src_origen, src_destino, always_xy=True)
    
    x=punto.x
    y=punto.y

    return Point(transformador.transform(x, y))


def change_crs_multipolygon(multi_polygon, crs_fuente, crs_final):
    src_origen = pyproj.CRS(crs_fuente)
    src_destino = pyproj.CRS(crs_final)
    transformador = pyproj.Transformer.from_crs(src_origen, src_destino, always_xy=True)

    multi_new = []
    
    for pol in multi_polygon.geoms:
        transformed_exterior = [transformador.transform(v[0], v[1]) for v in pol.exterior.coords]
        transformed_interiors = [[transformador.transform(v[0], v[1]) for v in hole.coords] for hole in pol.interiors]
        
        transformed_polygon = Polygon(transformed_exterior, transformed_interiors)
        multi_new.append(transformed_polygon)
    
    return unary_union(multi_new)


def change_crs_linestring(line, crs_fuente, crs_final):
    if not isinstance(line, LineString):
        raise Exception("Geometry Must Be A LineString")
    src_origen = pyproj.CRS(crs_fuente)
    src_destino = pyproj.CRS(crs_final)
    transformador = pyproj.Transformer.from_crs(src_origen, src_destino, always_xy=True)

    points = []
    for point in line.coords:
        points.append(transformador.transform(point[0], point[1]))
    
    return LineString(points)


def change_crs_multilinestring(multiline, crs_fuente, crs_final):
    if not isinstance(multiline, MultiLineString):
        raise Exception("Geometry Must Be A MultiLineString")
    src_origen = pyproj.CRS(crs_fuente)
    src_destino = pyproj.CRS(crs_final)
    transformador = pyproj.Transformer.from_crs(src_origen, src_destino, always_xy=True)

    lines = []
    for line in multiline.geoms:
        points = []
        for point in line.coords:
            points.append(transformador.transform(point[0], point[1]))
        lines.append(LineString(points))
    
    return MultiLineString(lines)


def change_crs(item, src_crs, dst_crs):
    if isinstance(item, Point):
        return change_crs_point(item, src_crs, dst_crs)
    if isinstance(item, Polygon):
        return change_crs_polygon(item, src_crs, dst_crs)
    if isinstance(item, MultiPolygon):
        return change_crs_multipolygon(item, src_crs, dst_crs)
    if isinstance(item, LineString):
        return change_crs_linestring(item, src_crs, dst_crs)
    if isinstance(item, MultiLineString):
        return change_crs_multilinestring(item, src_crs, dst_crs)
    if isinstance(item, tuple) and len(item) == 2:
        return change_crs_tuple_point(item, src_crs, dst_crs)
    
    if isinstance(item, list):
        new_gdf = gpd.GeoDataFrame({"geometry": item}, crs=src_crs)
        new_gdf = new_gdf.to_crs(dst_crs)
        return list(new_gdf["geometry"])

        # new_list = item.copy()
        # for i, sub_item in enumerate(item):
        #     new_list[i] = change_crs(sub_item, src_crs, dst_crs)
        
        # return new_list
    
    if isinstance(item, dict):
        new_dict = item.copy()
        for key, sub_item in item.items():
            new_dict[key] = change_crs(sub_item, src_crs, dst_crs)
        return new_dict

    if isinstance(item, gpd.GeoDataFrame):
        item.crs = src_crs
        return item.to_crs(dst_crs)

    if isinstance(item, DataFrame):
        new_df = item.copy()
        return new_df.applymap(lambda x: change_crs(x, src_crs, dst_crs))
    
    return item


def change_box_crs(bbox, bbox_crs, new_crs):
    """
    Change the CRS of a given bounding box (min_x, min_y, max_x, max_y)

    Parameters:
        - bbox: Bounding Box to change the crs of
        - bbox_crs: CRS of the given bounding box
        - new_crs: CRS to set to the bbox
    """
    if bbox_crs == new_crs:
        return bbox

    lowest_point = (bbox[0], bbox[1])
    lowest_point = change_crs(lowest_point, bbox_crs, new_crs)
    highest_point = (bbox[2], bbox[3])
    highest_point = change_crs(highest_point, bbox_crs, new_crs)

    new_bbox = [lowest_point[0], lowest_point[1], highest_point[0], highest_point[1]]

    return new_bbox