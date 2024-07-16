from .constants import ESRI_DATA_TYPES

def ordinal(n: int):
    """
    Returns the string representing the ordinal of the number n. 
    
    Parameters:
        - n: int wanting to cast to ordinal
    """
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix


def get_item(gis, item_id):
    """
    Find Item from its id
    
    Parameters:
        - gis: GIS object logged in where to search from
        - item_id: ID of the asked item
    
    Returns the item object inside the service
    """
    gis_item = gis.content.get(item_id)
    if gis_item is None:
        raise Exception(f"Layer (Id: {item_id}) Can't Be Found")
    
    return gis_item

def get_layer(gis, layer_id, number=None):
    """
    Find Layer from its id
    
    Parameters:
        - gis: GIS object logged in where to search from
        - layer_id: ID of the asked layer
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    
    Returns the layer object inside the service
    """
    layer_item = get_item(gis, layer_id)
    
    layers = layer_item.layers
    if layers is None:
        raise Exception(f"Layer (Id: {layer_id}) Has NO Layers")
    if len(layers) > 1 and number is None:
        raise Exception(f"Layer (Id: {layer_id}) Has Too Many Layers ({layers})")
    elif len(layers) == 0:
        raise Exception(f"Layer (Id: {layer_id}) Has NO Layers")
    
    if number is None:
        return layers[0]
    
    if len(layers) < number:
        ord_num = ordinal(number)
        raise Exception(f"Layer (Id: {layer_id}) Has Not Enough Layers To Get the {ord_num} One [{len(layers)} < {number}]")

    return layers[number]

def get_fields_aux(layer):
    """
    Returns a list of the fields of a layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be read
    
    Returns a list of tuples of type (name, alias, field type)
    """
    fields = layer.properties.fields
    condensed_fields = []

    for field in fields:
        name = field.name
        alias = field.alias
        field_type = ESRI_DATA_TYPES.get(field.type, field.type)
        condensed_fields.append((name, alias, field_type))

    return condensed_fields


def field_present_layer(layer, field_name):
    """
    Checks if field_name is present in layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be read
        - field_name: Name of the field wanting to check if present.
    
    Returns a bool
    """
    fields = get_fields_aux(layer)
    for field in fields:
        if field[0] == field_name:
            return True
    
    return False



def set_display_field_aux(layer, display_field):
    """
    Sets the display field to the ask field
    
    Parameters:
        - layer: Layer Item of the structure looking to be modified
        - display_field: Name of the field looking to set as display_field
    """
    if not field_present_layer(layer, display_field):
        raise Exception(f"Field {display_field} Doesn't Exist")

    update_dict = {"displayField": display_field}
    
    return layer.manager.update_definition(update_dict)


def standarize_columns(gdf):
    new_names = {}
    for column in gdf.columns:
        new_name = column.lower()
        if new_name[:1].isnumeric():
            new_name = "f"+new_name
        if len(new_name) > 10:
            new_name = new_name[:10]
        new_names[column] = new_name
    
    return gdf.rename(columns=new_names)