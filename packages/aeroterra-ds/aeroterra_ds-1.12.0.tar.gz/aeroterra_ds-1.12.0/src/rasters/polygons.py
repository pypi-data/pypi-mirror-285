import numpy as np

from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import unary_union

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


def transform_geometry_to_coords(geometry, transform_tif):
    """
    Given a polygon in pixel positions and a transform function,
    it returns the polygon in coords

    Parameters:
        - polygon: Shapely polygon to transform to coords
        - transform_tif: Rasterio Transform to use
    """
    transformer = rasterio.transform.AffineTransformer(transform_tif)
    if isinstance(geometry, Point):
        return transformer.xy(geometry.x, geometry.y)
    if isinstance(geometry, Polygon):
        return get_polygon_coords(geometry, transformer)
    if isinstance(geometry, MultiPolygon):
        to_unify = []
        for polygon in geometry.geoms:
            new_pol = get_polygon_coords(polygon, transformer)
            to_unify.append(new_pol)
        return unary_union(to_unify)
    if isinstance(geometry, tuple) and len(geometry) == 2:
        return transformer.xy(geometry[0], geometry[1])

    if isinstance(geometry, list):
        new_list = geometry.copy()
        for i, sub_item in enumerate(geometry):
            new_list[i] = transform_geometry_coords(sub_item, transform_tif)

        return new_list


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


def transform_geometry_to_pixels(geometry, transform_tif):
    """
    Given a polygon in coords positions and a transform function,
    it returns the polygon in pixels

    Parameters:
        - polygon: Shapely polygon to transform to pixels
        - transform_tif: Rasterio Transform to use
    """
    transformer = rasterio.transform.AffineTransformer(transform_tif)
    if isinstance(geometry, Point):
        return transformer.rowcol(geometry.x, geometry.y)
    if isinstance(geometry, Polygon):
        return get_polygon_pixeled(geometry, transformer)
    if isinstance(geometry, MultiPolygon):
        to_unify = []
        for polygon in geometry.geoms:
            new_pol = get_polygon_pixeled(polygon, transformer)
            to_unify.append(new_pol)
        return unary_union(to_unify)
    if isinstance(geometry, tuple) and len(geometry) == 2:
        return transformer.rowcol(geometry[0], geometry[1])

    if isinstance(geometry, list):
        new_list = geometry.copy()
        for i, sub_item in enumerate(geometry):
            new_list[i] = transform_geometry_pixels(sub_item, transform_tif)

        return new_list
