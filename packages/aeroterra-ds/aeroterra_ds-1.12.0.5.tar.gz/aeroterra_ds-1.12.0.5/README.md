# Aeroterra Data Science

A python library with basic functions to ahieve your geospatial data science projects using the arcgis environment.


# Packages

The Library counts with different packages across its extension

## Layers

Created to handle arcgis layers, their information and metadata.

 - layers
	 - get_layer
	 - clone_layer
	 - create_layer
	 - add_to_layer
	 - update_layer
	 - empty_layer
	 - create_empty_gdf
	 - read_full_layer
	 - read_layer_gdf
	 - update_pop_up
	 - update_symbology
 - fields
	 - add_field
	 - delete_field
	 - get_fields
	 - get_objectid_field
	 - rename_fields
	 - set_display_field
 - properties
	 - get_symbology
	 - get_layer_crs
	 - get_layer_extent
	 - get_layer_geom_type
	 - get_pop_up
	 - get_display_field
	 - get_items_amount
	 - get_layer_geom_type

## Geometry

Created to handle geometries, in arcgis and shapely formats.
 - change_crs
	 - change_crs
	 - change_box_crs
 - geometry
     - get_arcgis_geometry
     - get_geo_json
 - checks
	 - is_number
	 - is_box_polygon
	 - is_bbox
	 - is_polygon_like
	 - is_linestring_like
	 - is_point
	 - point_in_bbox
	 - is_multi_geometry
	 - is_single_geometry
	 - is_geometry
	 - is_thin
 - filters
	 - filter_collection
	 - filter_to_land
	 - filter_thin_polygons
	 - detect_and_cut_thin_parts
 - dataframes
	 - concat_geopandas
	 - create_gdf_geometries
 - distance
	 - distance_geometries
	 - line_length
	 - estimate_area
	 - buffer_kilometers
 - polygons
	 - get_intersections
	 - join_by_intersections
	 - get_polygons_hit
	 - generate_triangles
	 - get_total_bound

## Rasters

Created to handle rasters and shapely_geometry combined in a more armonic way.

 - handler
	- join_tiffs
	- reproject_raster
	- get_polygons_from_tiff
	- create_tiff_from_polygons
	- crop_geotiff
	- clip_tiff
	- grid_raster (Needs Borders Enum)
	- join_bands
 - properties
	- get_transform
	- get_crs
	- get_extent
 - polygons
	- transform_to_pixels
	- transform_to_coords