"""
Split from `renderer.py` since it was getting too large.

This serves the purpose of rendering any overlays onto the map.
Processed separately to the tilemap in renderer.py, but is merged in `paintEvent` in map_widget.py

Current overlay:
    - Two-point Route path

Planned overlay:
    - Multi-point Route path
    
Considered overlay:
    - Labels on POIs and symbols (e.g. NatRail symbol) on relevant locations
"""
from PySide6.QtGui import (
    QBrush,
    QColor,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QColorConstants,
    QTransform,
    QPolygonF,
)

from PySide6.QtCore import QPointF

from map.viewport import Viewport


class OverlayRenderer:
    def render_overlay(self, route_coords: list[tuple[float, float]], viewport: Viewport, painter: QPainter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.resetTransform()
        
        # Considering the route overlay as a single polygon with no filled in area is more efficient to render than as individual points passed
        # Through a for loop. Converts all the route coords from world coords into screen coords first,
        # Then casts them into QPoints. Afterwards, it appends to a list of QPoints, then that list is converted into a QPolygon.
        route_in_qpoints = []
        for coord in route_coords:
            translated_coord = viewport.graph_to_screen_coords(*coord)
            route_in_qpoints.append(QPointF(*translated_coord))
        
        route_as_polyline = QPolygonF(route_in_qpoints)
        
        self.render_route(route_as_polyline, painter)
        
    
    def render_route(self, route_coords: QPolygonF, painter: QPainter):
        # NOTE: these are RGB values for the default route when its drawn. In future revisions, I want to move this to styles.py and allow customisation.
        # For now, we'll keep them as constants
        
        # These are the same colours used by google maps. Taken via a color picker.
        ROUTE_COLOUR = QColor("#450efb")
        ROUTE_OUTLINE_COLOUR = QColor("#23038e")
        ROUTE_THICKNESS = 10.0
        ROUTE_OUTLINE_THICKNESS = 15.0
        
        # TODO: these are constants for rendering individual stops. Will have to be done later.
        POINT_RADIUS = 8
        INNER_POINT_FILL = QColorConstants.White
        OUTER_POINT_FILL = QColor("#ea4335")
        
        route_pen = QPen(ROUTE_COLOUR, ROUTE_THICKNESS)
        route_outline_pen = QPen(ROUTE_OUTLINE_COLOUR, ROUTE_OUTLINE_THICKNESS)
                
        painter.setPen(route_outline_pen)
        painter.drawPolyline(route_coords)
        
        painter.setPen(route_pen)
        painter.drawPolyline(route_coords)