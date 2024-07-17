from .common import get_layer, get_fields_aux, field_present_layer, set_display_field_aux
from .constants import ESRI_DATA_TYPES, PYTHON_DATA_TYPES

from .properties import get_objectid_field_aux, get_display_field_aux
from .layers import read_full_layer, update_layer

def create_field_dict(name, alias, data_type):
    """
    Given a name, alias and data_type it creates the dictionary of items needed
    for it to be a valid ESRIField Dictionary
    
    Parameters:
        - name: Name of the field looking to be created
        - alias: Alias of the field looking to be created
        - data_type: String representing the data type of the field
            looking to be created
    """
    field = {"nullable": True, "defaultValue": None, "editable": True, "domain": None}
    
    esri_type = PYTHON_DATA_TYPES.get(data_type)
    if esri_type is None and data_type not in ESRI_DATA_TYPES:
        raise Exception(f"{data_type} Is Not A Valid Data Type For ESRI")
    elif esri_type is None:
        esri_type = data_type
    
    field["modelName"] = name
    field["name"] = name
    field["alias"] = alias
    field["type"] = esri_type
    
    if esri_type == "esriFieldTypeString":
        field["length"] = 256
    
    return field


def add_field_aux(layer, name, data_type, alias=None):
    """
    Adds a field to the layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be modified
        - name: Name of the field looking to be created
        - data_type: String representing the data type of the field
            looking to be created
        - alias (Optional): Alias of the field looking to be created. If None,
            it'll be the same as name
    """
    if alias is None:
        alias = name
    if field_present_layer(layer, name):
        raise Exception(f"Field {name} Already Exists")
    
    new_field = create_field_dict(name, alias, data_type)

    update_dict = {"fields": [new_field]}
    
    return layer.manager.add_to_definition(update_dict)


def add_field(gis, layer_id, name, data_type, alias=None, number=None):
    """
    Adds a field to the layer
    
    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be modified
        - name: Name of the field looking to be created
        - data_type: String representing the data type of the field
            looking to be created
        - alias (Optional): Alias of the field looking to be created. If None,
            it'll be the same as name
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)

    return add_field_aux(layer, name, data_type, alias)


def delete_field_aux(layer, name):
    """
    Deletes a field from the layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be modified
        - name: Name of the field looking to be removed
    """    
    if not field_present_layer(layer, name):
        raise Exception(f"Field {name} Doesn't Exist")
    
    display_field = get_display_field_aux(layer)
    if display_field == name:
        fields = get_fields_aux(layer)
        amount = 0
        new_display = name 
        while amount < len(fields) and new_display == name:
            new_display = fields[amount][0]
            amount += 1
        
        if new_display == name:
            raise Exception("Can't Remove Display Field")
        
        set_display_field_aux(layer, new_display)

    update_dict = {"fields": [{"name": name}]}
    
    return layer.manager.delete_from_definition(update_dict)


def delete_field(gis, layer_id, name, number=None):
    """
    Deletes a field from the layer
    
    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be modified
        - name: Name of the field looking to be removed
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)

    return delete_field_aux(layer, name)


def rename_fields(gis, layer_id, change_names, number=None):
    """
    Deletes a field from the layer
    
    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be modified
        - change_names: Dictionary to express the before_name and the new_name. {old: new}
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)
    
    old_names = []
    data_types = {}
    fields = get_fields_aux(layer)
    for old_name in change_names.keys():
        data_type = None
        for field in fields:
            if field[0] == old_name:
                data_types[old_name] = field[2]
                old_names.append(old_name)
                break
    
    if len(old_names) == 0:
        raise Exception("No Valid Field Found To Change")

    object_id_field = get_objectid_field_aux(layer)

    fields_to_ask = [object_id_field]
    fields_to_ask.extend(old_names)

    old_data = read_full_layer(gis, layer_id)[fields_to_ask]
    
    new_names = []
    for old_name, new_name in change_names.items():
        data_type = data_types.get(old_name)
        if data_type is None:
            continue
        new_names.append(new_name)
        add_field_aux(layer, new_name, data_type)

    new_data = old_data.rename(columns=change_names)

    adds = update_layer(new_data, gis, layer_id, columns=new_names)
    for old_name in old_names:
        delete_field_aux(layer, old_name)

    return adds


def set_display_field(gis, layer_id, display_field, number=None):
    """
    Sets the display field to the ask field

    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be modified
        - display_field: Name of the field looking to set as display_field
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)

    return set_display_field_aux(layer, display_field)
