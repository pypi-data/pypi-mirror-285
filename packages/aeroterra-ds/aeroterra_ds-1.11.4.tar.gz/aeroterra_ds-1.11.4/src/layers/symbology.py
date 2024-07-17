from .common import get_layer


def create_unique_values_symbology(colors, field, values, symbols):
    """
    Creates the dictionary of an unique value symbology.

    Parameters:
        - colors: List of colors (tuple of 4 values, RGB & transparency)
            of the unique values.
        - field: Name of the field to renderer from
        - values: List of tuples (Value, Label) to categorize the render
        - symbols: List of symbol dictionary (excl. Color) to assign to each value    
    """
    renderers = []
    
    for i, color in enumerate(colors):
        renderer_line = {}
        rend_symbol = {}
        rend_symbol["color"] = color
        symbol = symbols[i]
        for key, value in symbol.items():
            rend_symbol[key] = value
        
        renderer_line["symbol"] = rend_symbol
        renderer_line["value"] = values[i][0]
        renderer_line["label"] = values[i][1]
        
        renderers.append(renderer_line)

    renderer = {}
    renderer["field1"] = field
    renderer["defaultSymbol"] = None
    renderer["uniqueValueInfos"] = renderers
    renderer["type"] = "uniqueValue"

    return renderer


def reset_unique_values(gis, layer_id, colors, field, values, symbols, transparency=0):
    """
    Updates the symbology of an asked layer.

    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be modified
        - colors: List of colors (tuple of 4 values, RGB & transparency)
            of the unique values.
        - field: Name of the field to renderer from
        - values: List of tuples (Value, Label) to categorize the render
        - symbols: List of symbol dictionary (excl. Color) to assign to each value
        - transparecny (Optional): Total transparency of the layer, from 0 to 100.
    """
    layer = get_layer(gis, layer_id)
    new_renderer = create_unique_values_symbology(colors, field, values, symbols)
    
    update_dict = {"renderer": new_renderer}
    update_dict["transparency"] = transparency
    update_dict = {"drawingInfo": update_dict}

    status = layer.manager.update_definition(update_dict)

    if not status["success"]:
        raise Exception(f"Error Updating Symbology: {status}")