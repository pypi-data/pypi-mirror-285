import geopandas as gpd
import pandas as pd

from geometry.change_crs import change_box_crs, change_crs
from geometry.checks import is_bbox, is_polygon_like, is_multi_geometry, is_geometry

from shapely.geometry import Polygon, MultiPolygon, box


def concat_geopandas(dataframes_to_join, crs=None, geometry_column="geometry"):
    """
    Concatenate geodataframes keeping the geodataframe format

    Parameters:
        - dataframes_to_join: List of dataframes to join.
        - crs (Optional): CRS to save the result in. If None, the one
            of the first dataframe will be used.
        - geometry_column (Optional): Name of the column where the geometry should be saved.
            By default "geometry" will be assumed
    """
    actual_gdfs = []
    for gdf in dataframes_to_join:
        if gdf is None:
            continue
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise Exception("Must Concatenate All GeoDataFrames")
        
        if gdf.crs is None:
            raise Exception("Can't Concatenate GeoDataFrames Without an assigned CRS")
        if gdf.geometry is None:
            raise Exception("Can't Concatenate GeoDataFrames Without an assigned Geometry Column")
        actual_gdfs.append(gdf)

    if len(actual_gdfs) == 0:
        raise Exception("Must Concatenate At Least 1 GeoDataFrame")
    
    if crs is None:
        crs = actual_gdfs[0].crs
    
    for gdf in actual_gdfs:
        gdf.to_crs(crs, inplace=True)
        geom_column = gdf.geometry.name
        if geom_column != geometry_column:
            gdf.rename(columns={geom_column: geometry_column}, inplace=True)
    
    total = pd.concat(actual_gdfs)

    return gpd.GeoDataFrame(total, crs=crs, geometry=geometry_column)




def filter_to_land(gdf, land_mask, mask_crs=None):
    """
    Given a geodataframe it filters it to a given mask.

    Parameters:
        - gdf: The GeoDataFrame to filter
        - land_mask: Mask to use as filter.
            Could be a list of polygons or a GDF a single polygon
            or a bound (min_x, min_y, max_x, max_y)
        - mask_crs: CRS of the given mask. If the mask is a gdf, the gdf crs
            will be used. Otherwise if this parameter is set in None it'll be
            assumed it's in the same crs as the gdf.
    """
    if isinstance(land_mask, gpd.GeoDataFrame):
        land_mask = land_mask.to_crs(gdf.crs)
    elif isinstance(land_mask, gpd.GeoSeries):
        land_mask = land_mask.to_crs(gdf.crs)
    elif is_bbox(land_mask):
        if mask_crs:
            land_mask = change_box_crs(land_mask, mask_crs, gdf.crs)
    elif is_polygon_like(land_mask):
        if mask_crs:
            land_mask = change_crs(land_mask, mask_crs, gdf.crs)
        land_mask = [land_mask]
    elif isinstance(land_mask, list):
        if len(land_mask) == 0:
            raise Exception("Can't Filter To An Empty List")
        if not is_polygon_like(land_mask[0]):
            raise Exception("Can't Filter From List Of Not Polygon-Like Geomtries")

        if mask_crs:
            land_mask = change_crs(land_mask, mask_crs, gdf.crs)
    
    land_mask = gpd.clip(land_mask, gdf.total_bounds)

    clipped_polygons = gpd.clip(gdf, land_mask, keep_geom_type=True)

    return clipped_polygons["geometry"].to_list()


def create_gdf_geometries(geometries, crs, split_multi=False, geometry_column="geometry"):
    """
    Given a group of geometries it creates a geodataframe with them.

    Parameters:
        - geometries: Geometries/Geometry to create a GDF for
        - crs: CRS of the given geometries
        - split_multi (Optional): If it should split the multigeometries into
            its separated parts. By default in False.
        - geometry_column (Optional): What name to give the geoemtry column.
            By default set in 'geometry'
    """
    if isinstance(geometries, gpd.GeoDataFrame):
        response = geometries.copy()
    elif isinstance(geometries, gpd.GeoSeries):
        response = gpd.GeoDataFrame({geometry_column: geometries}, geometry=geometry_column, crs=crs)
    elif is_bbox(geometries):
        pol = box(geometries)
        response = gpd.GeoDataFrame({geometry_column: [pol]}, geometry=geometry_column, crs=crs)
    elif is_multi_geometry(geometries) and split_multi:
        geometries = list(geometries.geoms)
        response = gpd.GeoDataFrame({geometry_column: geometries}, geometry=geometry_column, crs=crs)
    elif is_geometry(geometries):
        response = gpd.GeoDataFrame({geometry_column: [geometries]}, geometry=geometry_column, crs=crs)
    elif isinstance(geometries, list):
        if len(geometries) == 0:
            raise Exception("Can't Filter To An Empty List")
        if not is_geometry(geometries[0]):
            raise Exception("Can't Create A GDF from NOT Geometries")
        if is_multi_geometry(geometries) and split_multi:
            geometries = [geometry.geoms for geometry in geometries]

        response = gpd.GeoDataFrame({geometry_column: geometries}, geometry=geometry_column, crs=crs)
    
    geom_column = response.geometry.name
    if geom_column != geometry_column:
        response.rename(columns={geom_column: geometry_column}, inplace=True)

    return response.to_crs(crs)