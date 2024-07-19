import geopandas as gpd
import numpy as np

import os

import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
from rasterio.merge import merge
from rasterio.features import shapes as shapes_rasterio
from rasterio.features import geometry_mask
from rasterio.windows import Window
from rasterio.mask import mask

import shapely
from shapely.geometry import mapping
from shapely.ops import unary_union
from shapely.geometry import LineString, Polygon, MultiPolygon

from geometry.change_crs import change_crs, change_box_crs
from geometry.checks import point_in_bbox, is_bbox
from geometry.dataframes import create_gdf_geometries
from geometry.polygons import get_total_bound

from enum import Enum

from .common import is_tiff, get_tiffs_from_folder


def join_tiffs(merged_file=None, rasters_folder=None, rasters_paths=[]):
    """
    Joins all the tiffs present in the rasters_paths or rasters_folder in a merged geo-referenced
    file saved in merged_file.

    Return the joined matrix.
    
    Parameters:
        merged_file (Optional): Path where to save the merged tiff file. If None,
            the matrix won't be saved
        rasters_folder (Optional): Path where to read files from (only tiffs file will be read)
        rasters_paths (Optional): List of tiff paths to be joined        
    """
    if rasters_folder is None and len(rasters_paths) == 0:
        raise Exception("Must Insert Some Input Rasters To Join")

    if rasters_folder is not None:
        rasters_paths = get_tiffs_from_folder(rasters_folder)
        if len(rasters_paths) == 0:
            raise Exception(f"No Tiffs Files Were Found In {rasters_folder}")
    else:
        asked_paths = rasters_paths.copy()
        rasters_paths = []
        for path in asked_paths:
            if is_tiff(path):
                rasters_paths.append(path)
        if len(rasters_paths) == 0:
            raise Exception(f"No Tiffs Files Were Found In Asked List")

    list_raster = []
    for path_raster in rasters_paths:
        raster_file = rasterio.open(path_raster)
        list_raster.append(raster_file)

    mosaic, out_trans = merge(list_raster)

    if merged_file is None:
        return mosaic
    
    with rasterio.open(merged_file, 'w', driver = 'GTiff',
            height = mosaic.shape[1],
            width = mosaic.shape[2],
            count = mosaic.shape[0],
            dtype = str(mosaic.dtype),
            crs = raster_file.crs,
            transform = out_trans,
            compress = "deflate") as dest:
        dest.write(mosaic)
    
    return mosaic


def reproject_raster(path_raster_in, path_raster_out, crs_out) -> None:
    """
    Change de CRS of an existing raster.
    
    Note: As squares are not exact from one crs to other, some exact coordinate might change its value.
    
    Parameters:
        - path_raster_in: (Relative) Path to the raster wanted to transform
        - path_raster_out: (Relative) Path where to save the raster with changed crs
        - crs_out: CRS code of the new CRS wanted for the raster
    """
    if not is_tiff(path_raster_in):
        raise Exception(f"Input Raster [{path_raster_in}] Is Not A Raster")
        
    if not is_tiff(path_raster_out):
        raise Exception(f"Output Raster [{path_raster_out}] Is Not A Raster")
    
    if not os.path.isfile(path_raster_in):
        raise Exception(f"Input Raster [{path_raster_in}] Doesn't Exist")
    
    bands = []
    write_file = "aux.tif"
    
    with rasterio.open(path_raster_in) as src:
        transform, width, height = calculate_default_transform(
            src.crs, crs_out, src.width, src.height, *src.bounds)

        kwargs = src.meta.copy()
        kwargs.update({
            'crs': crs_out,
            'transform': transform,
            'width': width,
            'height': height
        })
        tiff_transform = src.transform
        tiff_crs = src.crs
        for i in range(1, src.count + 1):
            band = rasterio.band(src, i)
            bands.append(band)
            
        with rasterio.open(write_file, 'w', **kwargs) as dst:
            for i, band in enumerate(bands):
                reproject(
                    source = band,
                    destination = rasterio.band(dst, i+1),
                    src_transform = tiff_transform,
                    src_crs = tiff_crs,
                    dst_transform = transform,
                    dst_crs = crs_out,
                    resampling = Resampling.nearest
                )
    
    os.rename(write_file, path_raster_out)


def get_image_polygon_aux(image, transform_tif, max_value, min_value, joined, crs_og, crs_asked):
    """
    Returns a (list of) polygon(s) of the values between 2 extremes values in a raster
    
    Parameters:
        - image: Numpy matrix of the data to analyze
        - transform_tif: The transform function of the tif associated to the image
        - max_value: Max value valid for pixel to be included (<=) in polygon.
        - min_value: Min value valid for pixel to be excluded (>) in polygon.
        - joined: Boolean that indicates if should join all polygons into a multiplyogn or return a list
            of polygons.
        - crs_og: crs of the image data
        - crs_asked: crs asked for the polygons
    """
    mascara = np.where(image <= max_value, image, min_value)
    mascara = np.where(mascara > min_value, np.uint8(1), np.uint8(0)).astype("uint8")
    if np.sum(mascara) == 0:
        if joined:
            return None
        else:
            return []
    
    results = ({'properties': {'raster_val': v}, 'geometry': s} 
               for i, (s, v) in enumerate(shapes_rasterio(mascara, mask=(mascara==1), transform=transform_tif)))
    sub_mask = [shapely.geometry.shape(v['geometry']) for v in results]

    if crs_og != crs_asked:
        sub_mask = change_crs(sub_mask, crs_og.to_epsg(), crs_asked)
    
    if joined:
        extent = unary_union(sub_mask)
        return extent
    else:
        return sub_mask


def get_polygons_from_tiff(tiff_file, max_value=None, min_value=0, joined=True, raster_band=1, crs=None):
    """
    Returns a (list of) polygon(s) of the values between 2 extremes values in a raster
    
    Parameters:
        - tiff_file: (Relative) Path to the raster wanted to check.
        - max_value (Optional): Max value valid for pixel to be included (<=) in polygon. By deafult is 
            the max value found there.
        - min_value (Optional): Min value valid for pixel to be excluded (>) in polygon. By default is 0.
        - joined (Optional): Boolean that indicates if should join all polygons into a multiplyogn or return a list
            of polygons. By default is set to True.
        - raster_band (Optional): int indicating what raster to read. By default set to 1.    
        - crs (Optional): crs to get the polygon(s) in. If None, the crs of the image will be used.
    """
    if not is_tiff(tiff_file):
        raise Exception(f"Input Raster [{tiff_file}] Is Not A Raster")
    
    if not os.path.isfile(tiff_file):
        raise Exception(f"Input Raster [{tiff_file}] Doesn't Exist")

    with rasterio.open(tiff_file) as src:
        data = src.read(raster_band)
        transform_tif = src.transform
        tif_crs = src.crs
    
    if max_value is None:
        max_value = np.max(data)
    
    if crs is None:
        crs = tif_crs
    
    return get_image_polygon_aux(data, transform_tif, max_value, min_value, joined, tif_crs, crs)


def create_tiff_from_polygons(polygons, width, height, tiff_file=None, crs_pol=None, crs_img=None, transform=None, fill=True):
    """
    Returns a numpy matrix with the keys of the dict inside the polygons area and 0 outside. 
    If a file is provided, the image will be saved with georeference
    
    Parameters:
        - polygons: Dict of Polygons wanting to be saved as tiff with the key being the value on the
            tiff and the value being the polygons
        - width: Width of the image wanting to be created
        - height: Height of the image wanting to be created
        - tiff_file (Optional): (Relative) Path where to save the tiff image file.
            If included, crs_pol MUST be included.
        - crs_pol (Optional): CRS in which the data of the polygon is stored
        - crs_img (Optional): What CRS to save the image with. By default it'll
            be saved with the crs of the polygon.
        - transform: The transform function wanted to be used to create the image. If
            not given it'll create the simplest that fits the box asked and extent
            of the polygons
        - fill (Optional): Bool indicating if the tiff created should fill
            the polygon. By default in True
    """
        
    if tiff_file and not is_tiff(tiff_file):
        raise Exception(f"Input Raster [{tiff_file}] Is Not A Raster File")
    
    if tiff_file and not crs_pol:
        raise Exception("When given a File, a CRS of polygon MUST be provided")

    width = int(width)
    height = int(height)

    shape = (height, width)
    raster_data = np.zeros(shape, dtype=np.uint8)

    if len(polygons) == 0:
        return raster_data
    
    if crs_pol is not None and crs_img is not None:
        if crs_pol != crs_img:
            for tiff_value, polygons_assigned in polygons.items():
                polygons_new = change_crs(polygons_assigned, crs_pol, crs_img)
                polygons[tiff_value] = polygons_new
        crs_pol = crs_img

    all_polygons = []
    for pol_aux in polygons.values():
        all_polygons.extend(pol_aux)

    if not transform:
        extremes = get_total_bound(all_polygons)
        transform = rasterio.transform.from_bounds(*extremes, width, height)

    for value, polygons_val in polygons.items():
        pol_filter = polygons_val
        if not fill:
            pol_filter = []
            for pol in polygons_val:
                if isinstance(pol, Polygon):
                    pol_filter.append(LineString(pol.exterior.coords))
                elif isinstance(pol, MultiPolygon):
                    for sub_pol in pol.geoms:
                        pol_filter.append(LineString(sub_pol.exterior.coords))
                elif isinstance(pol, LineString):
                    pol_filter.append(pol)
                else:
                    raise Exception(f"{type(pol)} Not A Valid Geometry For Creating Tiff")
    
        mask = geometry_mask(pol_filter,
                            out_shape=shape,
                            transform=transform,
                            all_touched=True,
                            invert=True)

        raster_data[mask] = value
    
    if tiff_file:
        with rasterio.open(tiff_file, "w", driver = 'GTiff',
            height = height,
            width = width,
            count = 1,
            dtype = "uint8",
            crs = crs_img,
            transform = transform,
            nodata = 0,
            compress = "deflate") as dest:
            dest.write(raster_data, 1)

    return raster_data


def crop_geotiff(input_paths, bbox, bbox_crs=None, pad=10, output_path=None):
    """
    Crops geotiffs given a bbox, and creates a pad if asked.
    Returns the cropped matrix.

    Parameters:
        - input_paths: Paths to the tiffs to crop
        - bbox: Bounding Box to cut the geotiff from (min_x, min_y, max_x, max_y)
        - bbox_crs (Optional): CRS of the given bounding box. By default it'll be assumed it matches
            the crs of the input_path.
        - pad (Optional): How many pixels to extend the image by.
        - output_path (Optional): Path where to save the cropped tiff. If None,
            the result won't be saved in a file.
    """
    datas = []

    if not is_bbox(bbox):
        raise Exception(f"Invalid bbox {bbox}")

    bbox = list(bbox)
    if output_path and not is_tiff(output_path):
        raise Exception(f"Save Raster [{output_path}] Is Not A Raster Valid Name")
    
    for input_path in input_paths:
        if not is_tiff(input_path):
            raise Exception(f"Input Raster [{input_path}] Is Not A Raster")
        
        if not os.path.isfile(input_path):
            raise Exception(f"Input Raster [{input_path}] Doesn't Exist")
    
    for i, input_path in enumerate(input_paths):
        with rasterio.open(input_path) as src:
            if i == 0:
                bounds = src.bounds
                tiff_crs = src.crs
                if bbox_crs:
                    bbox = change_box_crs(bbox, bbox_crs, tiff_crs)
                    bbox_crs = tiff_crs

                if bbox[0] < bounds[0]:
                    bbox[0] = bounds[0]

                if bbox[1] < bounds[1]:
                    bbox[1] = bounds[1]
    
                if bbox[2] > bounds[2]:
                    bbox[2] = bounds[2]

                if bbox[3] > bounds[3]:
                    bbox[3] = bounds[3]

                row_start, col_start = src.index(bbox[0], bbox[3])
                row_start -= pad
                if row_start < 0:
                    row_start = 0
                
                col_start -= pad
                if col_start < 0:
                    col_start = 0
                
                row_stop, col_stop = src.index(bbox[2], bbox[1])
                row_stop += pad
                if row_stop > src.height:
                    row_stop = src.height
                
                col_stop += pad
                if col_stop > src.width:
                    col_stop = src.width
                
                width = abs(col_stop - col_start)
                height = abs(row_stop - row_start)

                if width == 0 or height == 0:
                    raise Exception("bbox too small for the quality of the tiff asked")

            for index in src.indexes:
                data = src.read(window=Window(col_start, row_start, width, height), indexes=index)
                datas.append(data)

    stacked_data = np.stack(datas)
    num_bands = len(datas)

    # Use metadata from the first input raster
    metadata = src.meta.copy()

    if output_path is None:
        return stacked_data

    # Update metadata for the output file
    metadata.update({
        'count': num_bands,
        'width': width,
        'height': height,
        'transform': rasterio.windows.transform(window=Window(col_start, row_start, width, height), transform=src.transform)
    })
    metadata["compress"] = "deflate"

    # Write the data to a new raster file
    with rasterio.open(output_path, 'w', **metadata) as dst:
        for i in range(num_bands):
            band_data = stacked_data[i, :, :]
            dst.write(band_data, i + 1)
    
    return stacked_data


def clip_tiff(tiff_file, land, save_file=None, geometry_crs=None):
    """
    Clips a geotif given a geodataframe extent.

    Parameters:
        - tiff_file: Path to the tif to clip
        - land: GeoDataframe/(Multi)Polygon/(Multi)Polygons List where to get the geometries from
        - save_file: Path where to save the clipped tiff
        - geometry_crs: If the land is not a GDF, the crs of the geometries. If None,
            it'll be assumed it's the same as the crs of the tiff.
    """
    if not is_tiff(tiff_file):
        raise Exception(f"Input Raster [{tiff_file}] Is Not A Raster")
    
    if not is_tiff(save_file):
        raise Exception(f"Save Raster [{save_file}] Is Not A Raster Valid Name")
    
    if not os.path.isfile(tiff_file):
        raise Exception(f"Input Raster [{tiff_file}] Doesn't Exist")

    with rasterio.open(tiff_file) as src:
        crs_tif = src.crs 
        if geometry_crs is None:
            geometry_crs = crs_tif
        geom_col = "geometry"
        land = create_gdf_geometries(land, geometry_crs, True, geom_col)
        land.to_crs(crs_tif, inplace=True)
        masas_tierra = [mapping(v) for v in land[geom_col].to_list()]
        clip, transf = mask(src, masas_tierra, invert = False, nodata=0, indexes=src.indexes)

        cut = clip[0, :, :]
        bands = src.meta["count"]
        kwargs = src.meta.copy()
        kwargs["transform"] = transf
        
        land_bbox = get_total_bound(land[geom_col].to_list())

        with rasterio.open(save_file, 'w', **kwargs) as dst:
            for i in range(bands):
                data = src.read(i+1)
                imagen = np.where(cut != 0, data, 0)
                dst.write(imagen, i+1)
    
    crop_geotiff([save_file], land_bbox, output_path=save_file)


class Borders(Enum):
    IGNORE = 0
    OVERLAP = 1
    FILL = 2


def create_window(tiff_src, start_x, start_y, size, output_path, ignore_end=False):
    """
    Crop Tiff into a smaller square window

    Parameters:
        - tiff_src: Rasterio Opened File of the tiff to crop
        - start_x: X position where to start the window
        - start_y: Y Position where to start the window
        - size: Size of the square to create
        - output_path: (Relative) Path where to save the clip
        - ignore_end (Optional): Bool indicating if it should create extending over the 
            existing end.
    """
    end_x = start_x + size
    if end_x > tiff_src.width and not ignore_end:
        end_x = tiff_src.width

    end_y = start_y + size
    if end_y > tiff_src.height and not ignore_end:
        end_y = tiff_src.height
    
    window_width = end_x - start_x
    window_height = end_y - start_y

    window = Window(start_x, start_y, window_width, window_height)
    datas = []
    for index in tiff_src.indexes:
        data = tiff_src.read(window=window, indexes=index)
        datas.append(data)
        stacked_data = np.stack(datas)

    num_bands = len(datas)
    metadata = tiff_src.meta.copy()
    metadata.update({
        'count': num_bands,
        'width': window_width,
        'height': window_height,
        'transform': rasterio.windows.transform(window=window, transform=tiff_src.transform)
    })
    metadata["compress"] = "deflate"

    with rasterio.open(output_path, 'w', **metadata) as dst:
        for i in range(num_bands):
            band_data = stacked_data[i, :, :]
            dst.write(band_data, i + 1)


def grid_raster(tiff_file, size, save_folder, overlap=0, extremes = Borders.IGNORE, extent=None, extent_crs=None):
    """
    Clips the raster into smaller rasters of size x size
    
    Parameters:
        - tiff_file: (Relative) Path to the raster wanted to grid.
        - size: integer representing the size wanted for the smaller rasters.
        - save_folder: (Relative) Path where to save the smaller rasters.
        - overlap (Optional): Pixels that overlap between neighbours clips. By 
            default set in 0.
        - extremes (Optional): How to handle the extremes. IGNORE = Create smaller clip, OVERLAP = Overlap with previous
            FILL = Fill the missing space with 0s. By defualt set in IGNORE.
        - extent (Optional): Extent (min_x, min_y, max_x, max_y) to grid the image in.
        - extent_crs (Optional): If using a extent, provide its crs. If not given it'll be assumed
            the extent uses the crs of the tiff_file
    """

    if not is_tiff(tiff_file):
        raise Exception(f"Input Raster [{tiff_file}] Is Not A Raster")
    
    if overlap < 0:
        raise Exception(f"Overlap value can't be negative")
    
    if not os.path.isdir(save_folder):
        os.makedirs(save_folder)

    x_pos = 0
    y_pos = 0

    with rasterio.open(tiff_file) as src:
        height = src.height
        width = src.width
        if extent:
            if extent_crs:
                extent = change_box_crs(extent, extent_crs, src.crs)
            row_start, col_start = src.index(extent[0], extent[3])
            row_stop, col_stop = src.index(extent[2], extent[1])
            row_start -= size
            col_start -= size
        else:
            row_start, col_start = (-1, -1)
            row_stop, col_stop = (height+1, width+1)
        extent_bbox = (col_start, row_start, col_stop, row_stop)
        while x_pos * size - overlap * x_pos < width:
            while y_pos * size - overlap * y_pos < height:
                start_x = x_pos * size
                start_x -= overlap * x_pos
                if extremes == Borders.OVERLAP and start_x + size > width:
                    start_x = width - size
                                
                start_y = y_pos * size
                start_y -= overlap * y_pos
                if extremes == Borders.OVERLAP and start_y + size > height:
                    start_y = height - size

                point = (start_x, start_y)
                if point_in_bbox(point, extent_bbox):
                    output_path = f"{save_folder}/{x_pos}_{y_pos}.tif"
                    create_window(src, start_x, start_y, size, output_path, ignore_end = True)
                y_pos += 1
            y_pos = 0
            x_pos += 1


def join_bands(input_rasters, output_path, exclude=None):
    """
    Join the bands in the input rasters into only one raster

    Parameters:
        - input_rasters: List of paths of the rasters to join
        - output_path: Path where to save the joined raster
        - exclude_bands(Optional): List of bands to exclude per rasters. By
            default set in none
    """
    if not is_tiff(output_path):
        raise Exception(f"Save Raster [{output_path}] Is Not A Raster Valid Name")
    
    if exclude is None:
        exclude = [[] for i in input_rasters]
    
    for input_path in input_rasters:
        if not is_tiff(input_path):
            raise Exception(f"Input Raster [{input_path}] Is Not A Raster")
        
        if not os.path.isfile(input_path):
            raise Exception(f"Input Raster [{input_path}] Doesn't Exist")

    datas = []
    for i, input_path in enumerate(input_rasters):
        with rasterio.open(input_path) as src:
            if i == 0:
                metadata = src.meta.copy()
            for index in src.indexes:
                if index in exclude[i]:
                    continue
                data = src.read(indexes=index)
                datas.append(data)

    stacked_data = np.stack(datas)
    num_bands = len(datas)

    metadata.update({
        'count': num_bands
    })
    metadata["compress"] = "deflate"

    with rasterio.open(output_path, 'w', **metadata) as dst:
        for i in range(num_bands):
            band_data = stacked_data[i, :, :]
            dst.write(band_data, i + 1)