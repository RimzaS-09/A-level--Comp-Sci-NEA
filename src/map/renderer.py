"""
The file is designed to have the purpose of decoding+rendering raw tile data

split up into two parts:

# TileRenderer:
Decodes 1 raw_tile data into a QImage

# MapRender:
Stitches multiple QImage rendered tiles together

In the previous major version, This just constructed some geometry primaries (either point, linestring, or polygon)
as modeled classes, which was THEN rendered, but this was slow af.

Now, It directly rasterizes the vector_tiles into QImages.

NOTE: I might need to split this file up later. Its a bit long
"""



import math
import gzip

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QColorConstants
)

from utils.vector_tile_parsing import vector_tile_pb2
from utils.errors.errors import Error
from map.layers import Layers, LayerStyle
from models import TileKey, RenderedTile
from map.viewport import Viewport





EXTENT = 4096



class TileRenderer:
    """
    Renders only 1 tile into a `QImage`
    """
    
    
    # Constant containing the width/height of 1 tile, in pixels
    TILE_LENGTH = 256

    def _decode_zigzag(self, val):
        return (val >> 1) ^ -(val & 1)


    ### QT's OddEvenFillRule does this automatically. This is the manaual method.
    def _shoelace_area(self, coords):
        area = 0

        for i in range(len(coords)):
            x1, y1 = coords[i]
            x2, y2 = coords[(i + 1) % len(coords)]

            area += x1 * y2 - x2 * y1

        return area / 2


    def _create_linestring_pen(self):
        pen = QPen(QColorConstants.Black)
        pen.setWidth(1)
        return pen


    def _create_polygon_pen(self):
        
        ### TODO: this was previously used to create a polygon's default pen.
        ### I've since added this pen into layers, so I should safely delete it.
        ### But I should first benchmark what performance the layer class is giving me before doing that
        ### If poor, revert to ts
        
        pen = QPen(QColorConstants.Black)
        pen.setWidthF(0.75)
        return pen


    ###     Note for rendering:
    ###     -
    ###
    ###



    def _render_point(self, painter: QPainter, geometry):
        radius = 2.5
        
        painter.setPen(self._create_linestring_pen())
        
        painter.setBrush(QBrush(QColorConstants.Black))
        
        # Just a matrix to store how to transofrm the image
        # Earlier we did operations regarding scaling the painter. to fit into the worldcoords.
        # Retrive this to ensure the pointer's radius won't be too large/small
        transform = painter.transform()
        # M11 returns the horizontal scaling factor
        scale_x = transform.m11()
        
        # Prevent divide by 0 error
        if scale_x == 0:
            return
        radius = radius / scale_x
        x = 0
        y = 0

        index = 0
        length = len(geometry)

        while index < length:

            command_integer = geometry[index]

            index += 1

            command_id = (
                command_integer & 0x7
            )

            command_count = (
                command_integer >> 3
            )

            if command_id != 1:
                # Point geometry should only use MoveTo.
                # TODO:
                #   -Implement some sort of InvalidGeometry Exception to this
                break

            for command in range(command_count):

                dx = self._decode_zigzag(geometry[index])
                dy = self._decode_zigzag(geometry[index + 1])

                x += dx
                y += dy

                painter.drawEllipse(
                    QPointF(x, y),
                    radius,
                    radius
                )

                index += 2


    def _render_linestring(self, painter: QPainter, geometry):
        painter.setPen(self._create_linestring_pen())
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        path = QPainterPath()
        
        x = 0
        y = 0
        
        index = 0
        length = len(geometry)
        
        while index < length:
            command_integer = geometry[index]
            index += 1
            
            command_id = command_integer & 0x7
            command_count = command_integer >> 3
            
            match command_id:
                # i.e, a  MoveTo
                case 1:
                    for i in range(command_count):
                        dx = self._decode_zigzag(geometry[index])
                        dy = self._decode_zigzag(geometry[index + 1])
                        
                        x += dx
                        y += dy
                        
                        path.moveTo(x, y)
                        
                        index += 2
                
                # i.e, a LineTo
                case 2:
                    for i in range(command_count):
                        dx = self._decode_zigzag(geometry[index])
                        dy = self._decode_zigzag(geometry[index + 1])
                        
                        x += dx
                        y += dy
                        
                        path.lineTo(x, y)
                        
                        index += 2
                
                # i.e, a ClosePath
                case 7:
                    path.closeSubpath()
                
                case _:
                    # TODO: Implement an InvalidGeometry error here
                    break
        
        painter.drawPath(path)          

    def _render_polygon(self, painter: QPainter, geometry, style: LayerStyle):
        painter.setPen(style.outline)
        painter.setBrush(style.fill)
        
        path = QPainterPath()
        
        # OddEvenFill SHOULD be the same as manually doing the shoelace algorithm. Hopefully.
        path.setFillRule(Qt.FillRule.OddEvenFill)
        
        x = 0
        y = 0
        
        index = 0
        length = len(geometry)
        
        while index < length:
            command_integer = geometry[index]
            index += 1
            
            command_id = command_integer & 0x7
            command_count = command_integer >> 3
            
            match command_id:
                # i.e, MoveTo
                case 1:
                    for i in range(command_count):
                        dx = self._decode_zigzag(geometry[index])
                        dy = self._decode_zigzag(geometry[index + 1])
                        
                        x += dx
                        y += dy
                        
                        path.moveTo(x, y)
                        
                        index += 2
                
                # i.e, a LineTo
                case 2:
                    for i in range(command_count):
                        dx = self._decode_zigzag(geometry[index])
                        dy = self._decode_zigzag(geometry[index + 1])
                        
                        x += dx
                        y += dy
                        
                        path.lineTo(x, y)
                        
                        index += 2
                        
                # i.e, a ClosePath
                case 7:
                    path.closeSubpath()
                
                case _:
                    # TODO: Implement an InvalidGeometry error here           
                    break
        
        painter.drawPath(path)
        
        


    def _render_layer(self, painter: QPainter, layer, style: LayerStyle):
        for feature in layer.features:
            geometry_type = feature.type
            
            if geometry_type == vector_tile_pb2.Tile.GeomType.POINT: # type: ignore
                self._render_point(painter, feature.geometry)
                
            elif geometry_type == vector_tile_pb2.Tile.GeomType.LINESTRING: # type: ignore
                self._render_linestring(painter, feature.geometry)
                
            elif geometry_type == vector_tile_pb2.Tile.GeomType.POLYGON: # type: ignore
                self._render_polygon(painter, feature.geometry, style)
            
            else:
                # TODO: Implement Special Geo-error for this!!!
                # Dont forget it
                raise Error


    def render_tile(self, tile_key: TileKey, gzipped_raw_tile) -> RenderedTile:
        """Renders the requested tile & tileKey"""
        styles = Layers().get_layer_styles()

        raw_tile = gzip.decompress(gzipped_raw_tile)
        
        tile_data = vector_tile_pb2.Tile() # type: ignore
        tile_data.ParseFromString(raw_tile)
        
        image = QImage(self.TILE_LENGTH, self.TILE_LENGTH, QImage.Format.Format_RGB32)
        image.fill(QColorConstants.White)
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        
        for layer in tile_data.layers:
            layer_name = layer.name
            
            # Ignore any layers for contours. Probs don't need them
            # TODO: in the future, I need to expand it to other layer types asw
            # maybe store it in a skip_layers array
            if (layer_name == "contours") or (not Layers().get_min_zooms().get(layer_name, None)):
                continue
            
            layer_styling = styles.get(layer_name, None)
            if not layer_styling:
                layer_styling = styles["default"]
            
            extent = layer.extent
            scale_to_image = self.TILE_LENGTH / extent
            
            painter.save()
            painter.scale(scale_to_image, scale_to_image)
            
            self._render_layer(painter, layer, layer_styling)
            
            painter.restore()
        
        painter.end()
        
        return RenderedTile(tile_key, image)






class MapRenderer:
    def render_map(self, tiles: list[RenderedTile], viewport: Viewport, painter: QPainter):
        print(viewport.get_visible_world())