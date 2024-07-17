from arcgis.geometry.filters import intersects

import json

from shapely.geometry import Polygon

from .constants import ESRI_DATA_TYPES
from .common import get_layer, get_item, get_fields_aux

from geometry.geometry import create_geo_json


def get_fields(gis, layer_id, number=None):
    """
    Returns a list of the fields of a layer
    
    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be read
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    
    Returns a list of tuples of type (name, alias, field type)
    """
    layer = get_layer(gis, layer_id, number)
    
    return get_fields_aux(layer)


def get_objectid_field_aux(layer):
    """
    Returns the name of the field that works as the objectID field
    
    Parameters:
        - layer: Layer Item of the structure looking to be read
    """
    fields = get_fields_aux(layer)
    
    for field in fields:
        if field[2] == "ObjectID":
            return field[0]
    
    raise Exception(f"Couldn't Find ObjectID Field Between Given Fields [{fields}]")


def get_objectid_field(gis, layer_id, number=None):
    """
    Returns the name of the field that works as the objectID field
    
    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be read
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)
    
    return get_objectid_field_aux(layer)


def get_symbology_aux(layer):
    """
    Returns the symbology data of a given layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be read
    """
    return layer.properties.drawingInfo


def get_symbology(gis, layer_id, number=None):
    """
    Returns the symbology data of a given layer
    
    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be read
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)
    
    return get_symbology_aux(layer)


def get_layer_crs_aux(layer):
    """
    Returns the spatial reference of a given layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be read
    """
    extent = layer.properties["extent"]

    spatial_reference = extent["spatialReference"]

    if "latestWkid" in spatial_reference:
        crs = spatial_reference["latestWkid"]
    elif "wkid" in spatial_reference:
        crs = spatial_reference["wkid"]
    else:
        raise Exception(f"CRS Cant't Be Found In Spatial Reference {spatial_reference}")

    return crs


def get_layer_crs(gis, layer_id, number=None):
    """
    Returns the spatial reference of a given layer
    
    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be read
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)
    
    return get_layer_crs_aux(layer)


def get_layer_extent_aux(layer):
    """
    Returns the extent of a given layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be read
    """
    extent = layer.properties["extent"]

    min_x = extent["xmin"]
    max_x = extent["xmax"]
    min_y = extent["ymin"]
    max_y = extent["ymax"]

    polygon = Polygon([(min_x, min_y), (min_x, max_y), (max_x, max_y), (max_x, min_y)])

    return polygon


def get_layer_extent(gis, layer_id, number=None):
    """
    Returns the extent of a given layer
    
    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be read
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)
    
    return get_layer_extent_aux(layer)


def get_display_field_aux(layer):
    """
    Returns the display field of a given layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be read
    """
    display_field = layer.properties.displayField

    return display_field


def get_display_field(gis, layer_id, number=None):
    """
    Returns the display field of a given layer
    
    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be read
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)
    
    return get_display_field_aux(layer)



def get_layer_geom_type_aux(layer):
    """
    Returns the geometry type of a given layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be read
    """
    geom_type = layer.properties["geometryType"]

    return geom_type


def get_layer_geom_type(gis, layer_id, number=None):
    """
    Returns the geometry type of a given layer
    
    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be read
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)
    
    return get_layer_geom_type_aux(layer)


def get_pop_up(gis, layer_id, number=None):
    """
    Returns the popupInfo of a given layer
    
    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be read
        - number(Optional): Number layer of the layer wanting to be read. If
            not set, default at 0
    """
    layer_item = get_item(gis, layer_id)
    
    layers_data = layer_item.get_data()

    if "layers" not in layers_data:
        layers = layer_item.layers
        if number >= len(layers):
            raise Exception(f"Layer Number {number} Can't Be Found Inside Item {layer_id}")
        return {}            
    
    layer_data = None
    for layer in layers_data["layers"]:
        if layer["id"] == number:
            layer_data = layer
            break
    
    if layer_data is None:
        raise Exception(f"Layer Number {number} Can't Be Found Inside Item {layer_id}")
    
    if "popupInfo" in layer_data:
        popup_data = layer_data["popupInfo"]
    else:
        popup_data = {}
    
    return popup_data


def update_pop_up(gis, layer_id, number, pop_up_data):
    """
    Given a popupInfo dictionary, it updates the layer PopUp info with it

    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be read
        - number: Number layer of the layer wanting to be read. If
            not set, default at 0
        - pop_up_data: Dictionary representing the new pop up
    """
    layer_item = get_item(gis, layer_id)
    
    layers_data = layer_item.get_data()
    
    if "layers" not in layers_data:
        layers = layer_item.layers
        if number >= len(layers):
            raise Exception(f"Layer Number {number} Can't Be Found Inside Item {layer_id}")
        layers_data["layers"] = []
        layers_data["layers"].append({"popupInfo": pop_up_data, "id": number})
    else:
        layer_pos = None
        for i, layer in enumerate(layers_data["layers"]):
            if layer["id"] == number:
                layer_pos = i
                break

        if layer_pos is None:
            raise Exception(f"Layer Number {number} Can't Be Found Inside Item {layer_id}")

        layers_data["layers"][layer_pos]["popupInfo"] = pop_up_data
    
    update_dict = {"layers": layers_data["layers"]}
    update_dict = {"text": json.dumps(update_dict)}    

    return layer_item.update(update_dict)


def get_items_amount_aux(layer, query="1=1", geometry_filter=None, geometry_crs=4326):
    """
    Returns the amount of items saved in layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be read
        - query (Optional): String representing a SQL query to filter the data to 
            to be read from the layer. If None, all the data will be providen.
        - geometry_filter (Optional): Shapely (Multi)Polygon to filter data geographically.
            If None, all the data will be providen.
        - geometry_crs (Optional): CRS of the given geometry_filer. If missing, 4326 will be assumed.
    """
    geo_filter = None
    if geometry_filter is not None:
        bounds = create_geo_json(geometry_filter, geometry_crs)
        geo_filter = intersects(bounds)

    return layer.query(where = query, geometry_filter=geo_filter, return_count_only=True)


def get_items_amount(gis, layer_id, number=None):
    """
    Returns the amount of items saved in layer
    
    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be read
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)
    
    return get_items_amount_aux(layer)


def update_symbology_aux(layer, symbology):
    """
    Updates the symbology data of a given layer

    Parameters:
        - layer: Layer Item of the structure looking to be read
        - symbology: Dictionary to set as symbology of the layer
    """
    symbology_dict = {"drawingInfo": dict(symbology)}

    return layer.manager.update_definition(symbology_dict)


def update_symbology(gis, layer_id, symbology, number=None):
    """
    Updates the symbology data of a given layer

    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be read
        - symbology: Dictionary to set as symbology of the layer
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)
    
    return update_symbology_aux(layer, symbology)

