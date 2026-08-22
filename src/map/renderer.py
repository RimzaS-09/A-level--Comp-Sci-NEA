from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QPainter,
    QPen,
    QBrush,
    QPolygonF,
    QPainterPath,
)

from models import Point, LineString, Polygon

import math


EXTENT = 4096



"""


class MapRenderer:
    def __init__(
        self,
        centre_x=0.0,
        centre_y=0.0,
        zoom=0
    ):
        pass
    
    def draw_polygon(polygon):
        pass
    
    def draw_linestring(linestring):
        pass
    
    def draw_point(point):
        pass
"""
    
from PySide6.QtCore import QPointF
from PySide6.QtGui import (
    QPainter,
    QPolygonF,
    QPainterPath
)

from models import Point, LineString, Polygon


class MapRenderer:

    TILE_SIZE = 256

    def render(self, tiles, viewport, painter):
        for tile in tiles:
            self.render_tile(tile, viewport, painter)

    def render_tile(self, tile, viewport, painter):
        for layer in tile.layers:
            self.render_layer(
                tile,
                layer,
                viewport,
                painter
            )

    def render_layer(self, tile, layer, viewport, painter):
        for feature in layer.features:
            self.render_feature(
                tile,
                layer,
                feature,
                viewport,
                painter
            )

    def render_feature(
        self,
        tile,
        layer,
        feature,
        viewport,
        painter
    ):
        for geometry in feature.geometry:

            if isinstance(geometry, Point):
                self.draw_point(
                    tile,
                    layer,
                    geometry,
                    viewport,
                    painter
                )

            elif isinstance(geometry, LineString):
                self.draw_linestring(
                    tile,
                    layer,
                    geometry,
                    viewport,
                    painter
                )

            elif isinstance(geometry, Polygon):
                self.draw_polygon(
                    tile,
                    layer,
                    geometry,
                    viewport,
                    painter
                )

    def world_coordinate(self, tile, layer, coordinate):
        """
        Convert MVT tile-local coordinates into world pixels.
        """

        x, y = coordinate

        world_x = (
            tile.x + x / layer.extent
        ) * self.TILE_SIZE

        world_y = (
            tile.y + y / layer.extent
        ) * self.TILE_SIZE

        return world_x, world_y

    def screen_coordinate(
        self,
        tile,
        layer,
        coordinate,
        viewport
    ):
        """
        Convert world pixels to screen pixels.
        """

        world_x, world_y = self.world_coordinate(
            tile,
            layer,
            coordinate
        )

        screen_x = (
            (world_x - viewport.centre_x)
            * viewport.zoom
            + viewport.width / 2
        )

        screen_y = (
            (world_y - viewport.centre_y)
            * viewport.zoom
            + viewport.height / 2
        )

        return QPointF(screen_x, screen_y)

    def draw_point(
        self,
        tile,
        layer,
        point,
        viewport,
        painter
    ):
        screen_point = self.screen_coordinate(
            tile,
            layer,
            point.get_points(),
            viewport
        )

        painter.drawEllipse(
            screen_point,
            3,
            3
        )

    def draw_linestring(
        self,
        tile,
        layer,
        linestring,
        viewport,
        painter
    ):
        points = [
            self.screen_coordinate(
                tile,
                layer,
                coordinate,
                viewport
            )
            for coordinate in linestring.get_points()
        ]

        if len(points) >= 2:
            painter.drawPolyline(
                QPolygonF(points)
            )

    def draw_polygon(
        self,
        tile,
        layer,
        polygon,
        viewport,
        painter
    ):
        exterior = polygon.get_points()

        if not exterior:
            return

        path = QPainterPath()

        path.moveTo(
            self.screen_coordinate(
                tile,
                layer,
                exterior[0],
                viewport
            )
        )

        for coordinate in exterior[1:]:
            path.lineTo(
                self.screen_coordinate(
                    tile,
                    layer,
                    coordinate,
                    viewport
                )
            )

        path.closeSubpath()

        for ring in polygon.interior:
            if not ring:
                continue

            path.moveTo(
                self.screen_coordinate(
                    tile,
                    layer,
                    ring[0],
                    viewport
                )
            )

            for coordinate in ring[1:]:
                path.lineTo(
                    self.screen_coordinate(
                        tile,
                        layer,
                        coordinate,
                        viewport
                    )
                )

            path.closeSubpath()

        painter.drawPath(path)