import numpy as np

from shapely.geometry import Point, Polygon, MultiPolygon, LineString, MultiLineString
from shapely.ops import unary_union

from geometry.checks import is_point

from pandas import DataFrame

import rasterio

def get_polygon_coords(polygon, transformer):
    """
    Given a polygon in pixel positions and a transform function,
    it returns the polygon in coords

    Parameters:
        - polygon: Shapely polygon to transform to coords
        - transformer: Rasterio Affine Transformer to use
    """
    coords = list(polygon.exterior.coords)

    new_coords = []

    for coord in coords:
        new_coord = transformer.xy(coord[0], coord[1])
        new_coords.append(new_coord)

    holes = []

    for hole in polygon.interiors:
        new_holes = []
        for coord in hole.coords:
            new_hole = transformer.xy(coord[0], coord[1])
            new_holes.append(new_hole)
        holes.append(new_holes)

    return Polygon(new_coords, holes)


def get_line_coords(line, transformer):
    """
    Given a line in coords positions and a transform function,
    it returns the line in pixels

    Parameters:
        - line: Shapely line to transform to pixels
        - transformer: Rasterio Affine Transformer to use
    """
    coords = list(line.coords)

    new_coords = []
    for coord in coords:
        new_coord = transformer.xy(coord[0], coord[1])
        new_coords.append(new_coord)
    
    return LineString(new_coords)


def transform_to_coords(item, transform_tif):
    """
    Given a item in pixel positions and a transform function,
    it returns the item in coords

    Parameters:
        - item: Shapely item to transform to coords
        - transform_tif: Rasterio Transform to use
    """
    transformer = rasterio.transform.AffineTransformer(transform_tif)
    if isinstance(item, Point):
        return transformer.xy(item.x, item.y)
    if is_point(item):
        return transformer.xy(item[0], item[1])
    if isinstance(item, Polygon):
        return get_polygon_coords(item, transformer)
    if isinstance(item, MultiPolygon):
        to_unify = []
        for polygon in item.geoms:
            new_pol = get_polygon_coords(polygon, transformer)
            to_unify.append(new_pol)
        return unary_union(to_unify)
    if isinstance(item, LineString):
        return get_line_coords(item)
    if isinstance(item, MultiLineString):
        to_unify = []
        for line in item.geoms:
            new_line = get_line_coords(line, transformer)
            to_unify.append(new_line)
        return unary_union(to_unify)

    if isinstance(item, list):
        new_list = item.copy()
        for i, sub_item in enumerate(item):
            new_list[i] = transform_to_coords(sub_item, transform_tif)

        return new_list
    
    if isinstance(item, dict):
        new_dict = item.copy()
        for key, sub_item in item.items():
            new_dict[key] = transform_to_coords(sub_item, transform_tif)
        return new_dict

    if isinstance(item, DataFrame):
        new_df = item.copy()
        return new_df.applymap(lambda x: transform_to_coords(x, transform_tif))
    
    return item


def get_polygon_pixeled(polygon, transformer):
    """
    Given a polygon in coords positions and a transform function,
    it returns the polygon in pixels

    Parameters:
        - polygon: Shapely polygon to transform to pixels
        - transformer: Rasterio Affine Transformer to use
    """
    coords = list(polygon.exterior.coords)
    new_coords = []

    for coord in coords:
        new_coord = transformer.rowcol(coord[0], coord[1])
        new_coords.append(new_coord)

    holes = []

    for hole in polygon.interiors:
        new_holes = []
        for coord in hole.coords:
            new_coord = transformer.rowcol(coord[0], coord[1])
            new_holes.append(new_coord)
        holes.append(new_holes)

    return Polygon(new_coords, holes)


def get_line_pixeled(line, transformer):
    """
    Given a line in coords positions and a transform function,
    it returns the line in pixels

    Parameters:
        - line: Shapely line to transform to pixels
        - transformer: Rasterio Affine Transformer to use
    """
    coords = list(line.coords)

    new_coords = []
    for coord in coords:
        new_coord = transformer.rowcol(coord[0], coord[1])
        new_coords.append(new_coord)
    
    return LineString(new_coords)



def transform_to_pixels(item, transform_tif):
    """
    Given an items in coords positions and a transform function,
    it returns the item in pixels

    Parameters:
        - item: Item to transform to pixels
        - transform_tif: Rasterio Transform to use
    """
    transformer = rasterio.transform.AffineTransformer(transform_tif)
    if isinstance(item, Point):
        return transformer.rowcol(item.x, item.y)
    if is_point(item):
        return transformer.rowcol(item[0], item[1])
    if isinstance(item, Polygon):
        return get_polygon_pixeled(item, transformer)
    if isinstance(item, MultiPolygon):
        to_unify = []
        for polygon in item.geoms:
            new_pol = get_polygon_pixeled(polygon, transformer)
            to_unify.append(new_pol)
        return unary_union(to_unify)
    if isinstance(item, LineString):
        return get_line_pixeled(item)
    if isinstance(item, MultiLineString):
        to_unify = []
        for line in item.geoms:
            new_line = get_line_pixeled(line, transformer)
            to_unify.append(new_line)
        return unary_union(to_unify)


    if isinstance(item, list):
        new_list = item.copy()
        for i, sub_item in enumerate(item):
            new_list[i] = transform_to_pixels(sub_item, transform_tif)

        return new_list
    
    if isinstance(item, dict):
        new_dict = item.copy()
        for key, sub_item in item.items():
            new_dict[key] = transform_to_pixels(sub_item, transform_tif)
        return new_dict

    if isinstance(item, DataFrame):
        new_df = item.copy()
        return new_df.applymap(lambda x: transform_to_pixels(x, transform_tif))
    
    return item
