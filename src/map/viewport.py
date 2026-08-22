from dataclasses import dataclass


def lon_to_world_x(lon: float, zoom: int) -> float:
    """Convert longitude to global MVT/Web-Mercator pixel coordinates."""
    return (lon + 180.0) / 360.0 * (2 ** zoom) * EXTENT


def lat_to_world_y(lat: float, zoom: int) -> float:
    """Convert latitude to global MVT/Web-Mercator pixel coordinates."""
    lat = max(-85.05112878, min(85.05112878, lat))

    lat_rad = math.radians(lat)

    mercator_y = (
        1.0 - math.asinh(math.tan(lat_rad)) / math.pi
    ) / 2.0

    return mercator_y * (2 ** zoom) * EXTENT


def lon_lat_to_world(lon: float, lat: float, zoom: int) -> tuple[float, float]:
    """Convert longitude/latitude to global world coordinates."""
    return (
        lon_to_world_x(lon, zoom),
        lat_to_world_y(lat, zoom),
    )



@dataclass
class Viewport:
    # Centre of the viewport in world-pixel coordinates
    centre_x: float
    centre_y: float

    # Visual zoom level
    zoom: float = 1.0

    # Size of the widget in screen pixels
    width: int = 800
    height: int = 600

    TILE_SIZE: int = 256

    def set_size(self, width: int, height: int):
        self.width = width
        self.height = height

    def pan(self, dx: float, dy: float):
        """
        Move the viewport by screen/world pixels.
        """
        self.centre_x -= dx
        self.centre_y -= dy

    def zoom_at(
        self,
        mouse_x: float,
        mouse_y: float,
        zoom_factor: float
    ):
        """
        Zoom while keeping the point underneath the mouse cursor
        in approximately the same screen position.
        """

        old_zoom = self.zoom
        new_zoom = old_zoom * zoom_factor

        # Position of the cursor relative to the viewport centre
        offset_x = mouse_x - self.width / 2
        offset_y = mouse_y - self.height / 2

        # Convert the cursor's screen offset into world offset
        old_world_x = offset_x / old_zoom
        old_world_y = offset_y / old_zoom

        new_world_x = offset_x / new_zoom
        new_world_y = offset_y / new_zoom

        # Adjust centre so the same world position remains beneath
        # the cursor.
        self.centre_x += old_world_x - new_world_x
        self.centre_y += old_world_y - new_world_y

        self.zoom = new_zoom

    def visible_bounds(self):
        """
        Return the world-pixel coordinates of the viewport edges.
        """

        half_width = self.width / (2 * self.zoom)
        half_height = self.height / (2 * self.zoom)

        left = self.centre_x - half_width
        right = self.centre_x + half_width

        top = self.centre_y - half_height
        bottom = self.centre_y + half_height

        return left, top, right, bottom

    def visible_tile_range(self):
        """
        Determine which tile indices intersect the current viewport.
        """

        left, top, right, bottom = self.visible_bounds()

        tile_left = int(left // self.TILE_SIZE)
        tile_right = int(right // self.TILE_SIZE)

        tile_top = int(top // self.TILE_SIZE)
        tile_bottom = int(bottom // self.TILE_SIZE)

        return (
            tile_left,
            tile_right,
            tile_top,
            tile_bottom
        )