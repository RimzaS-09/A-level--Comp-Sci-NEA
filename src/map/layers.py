from dataclasses import dataclass
from PySide6.QtGui import QPen, QBrush, QColor, QColorConstants



@dataclass
class LayerStyle:
    outline: QPen
    fill: QBrush




### TODO:
###     - Expand the no. of layer styles here to include more layers
###     - Make design of this function neater, so accessing layer_styles is easier
###     - Find some way to make it global, so I dont need to make a new object every time
class Layers:
    # TODO: Make this custom hashmap
    _layer_styles = {
        "greenspaces": LayerStyle(
            fill=QBrush(
                QColor(120, 190, 120)
            ),
            outline=QPen(
                QColor(80, 140, 80),
                0.75
            )
        ),

        "surfacewater": LayerStyle(
            fill=QBrush(
                QColorConstants.Blue
            ),
            outline=QPen(
                QColor(70, 120, 190),
                0.75
            )
        ),
        
        "sea": LayerStyle(
            fill=QBrush(
                QColorConstants.Blue
            ),
            outline=QPen(
                QColor(80, 140, 80),
                0.75
            )
        ),

        "buildings": LayerStyle(
            fill=QBrush(
                QColorConstants.Gray
            ),
            outline=QPen(
                QColor(160, 160, 160),
                0.5
            )
        ),
        
        "default": LayerStyle(
            fill=QBrush(
                QColorConstants.Gray
            ),
            outline=QPen(
                QColorConstants.Black,
                0.75
            )
        )
    }
    
    _layer_min_zoom = {
        "building" : 12,
    }
    
    def get_min_zooms(self):
        return self._layer_min_zoom
    
    ### Getters and setters for layer styles ###
    
    def get_layer_styles(self):
        return self._layer_styles
    
    def set_layer_style(self, layer_name, layer_style: LayerStyle):
        self._layer_styles[layer_name] = layer_style
    
    def set_layer_fill(self, layer_name, layer_colour):
        self._layer_styles[layer_name].fill.setColor(layer_colour)
        
    def set_layer_outline_colour(self, layer_name, colour):
        self._layer_styles[layer_name].outline.setColor(colour)
        
    def set_layer_outline_width(self, layer_name, width):
        self._layer_styles[layer_name].outline.setWidth(width)

