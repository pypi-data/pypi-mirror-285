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
 - fields
	 - add_field
	 - delete_field
	 - get_fields
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

## Geometry

Created to handle geometries, in arcgis and shapely formats.
 - change_crs
	 - change_crs
	 - change_box_crs
 - geometry
     - get_arcgis_geometry
     - get_geo_json


## Rasters

Created to handle rasters and shapely_geometry combined in a more armonic way.

 - handler
	- join_tiffs
	- reproject_raster
	- get_polygons_from_tiff
	- create_tiff_from_polygons
	- crop_geotiff
	- clip_tiff
	- grid_raster
	- join_bands
 - propeerties
	- get_transform
	- get_crs
	- get_extent