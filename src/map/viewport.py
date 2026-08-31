import math

class Viewport:
    def __init__(self,
                centre: tuple[float, float],
                zoom_level = 6.0,
                dimensions: tuple[int, int] = (800, 600),       
                ):
        self.centre = centre
        self.zoom_level = zoom_level
        self.dimensions = dimensions
        
        self.min_zoom = 0
        self.max_zoom = 20
        
        self.TILE_SIZE = 256
    
    def pan(self, dx, dy):
        scale = self.get_scale()
        new_x = self.centre[0] - (dx / scale)
        new_y = self.centre[0] - (dy / scale)
        
        self.centre = (new_x, new_y)
        self.clamp()
    
    def get_scale(self):
        return 2 ** self.zoom_level
    
    def set_size(self, dimensions: tuple[int, int]):
        self.dimensions = dimensions
        
    def set_zoom_limits(self, minimum, maximum):
        self.min_zoom = minimum
        self.max_zoom = maximum
    
    def clamp(self):
        world_size = self.TILE_SIZE
        
        if self.centre[0] > world_size:
            clamped_x = world_size
        elif self.centre[0] < 0.0:
            clamped_x = 0.0
        else:
            clamped_x = self.centre[0]
            
        
        if self.centre[1] > world_size:
            clamped_y = world_size
        elif self.centre[1] < 0.0:
            clamped_y = 0.0
        else:
            clamped_y = self.centre[1]
            
        self.centre = (clamped_x, clamped_y)
        
        
        
    def check_zoom_level(self, new_zoom):
        """returns a bool, to ensure zoom is legal or not."""
        
        if (new_zoom < self.min_zoom) or (new_zoom > self.max_zoom):
            return False
        
        return True
    
    def zoom_to_point(self, mouse_x, mouse_y, delta):
        old_zoom = self.zoom_level
        new_zoom = old_zoom + delta
        
        if not self.check_zoom_level(new_zoom):
            return
        
        old_scale = 2 ** old_zoom
        new_scale = 2 ** new_zoom
        
        screen_centre = ( self.dimensions[0] / 2, self.dimensions[1] / 2 )
        
        offset_x = mouse_x - screen_centre[0]
        offset_y = mouse_y - screen_centre[1]
        
        world_x = self.centre[0] + (offset_x / old_scale)
        world_y = self.centre[1] + (offset_y / old_scale)
        
        self.centre = (world_x - (offset_x / new_scale) , world_y - (offset_y / new_scale))
        
        self.zoom_level = new_zoom
    
    def get_visible_world(self):
        """Returns the visible section of the map in world coords, as the midpoints of each side of a rectangle"""
        
        scale = self.get_scale()
        
        width_offset = self.dimensions[0] / 2 / scale
        height_offset = self.dimensions[1] / 2 / scale
        
        return (
            self.centre[0] - width_offset,
            self.centre[1] - height_offset,
            self.centre[0] + width_offset,
            self.centre[1] + height_offset
        )
        
    def get_tiles_visible(self, padding = 0):
        """
        Gets the tile rows and columns that would be seen by the user, so they can be loaded.
        
        The parameter `padding` controls what extra buffer of tiles should be visible. In case I want to
        make sure extra tiles outside the screen are loaded.
        """
        
        bounds = self.get_visible_world()
        
        left = bounds[0]
        top = bounds[1]
        right = bounds[2]
        bottom = bounds[3]
        
        num_tiles_across = 2 ** self.zoom_level
        
        # World coordinates go from 0-256 at zoom 0
        tile_world_size = self.TILE_SIZE / num_tiles_across

        min_x = math.floor(left / tile_world_size) - padding
        max_x = math.floor(right / tile_world_size) + padding
        min_y = math.floor(top / tile_world_size) - padding
        max_y = math.floor(bottom / tile_world_size) + padding
        
        if min_x < 0:
            min_x = 0
        elif min_x > (num_tiles_across - 1):
            min_x = num_tiles_across - 1
        
        if max_x < 0:
            max_x = 0
        elif max_x > (num_tiles_across - 1):
            max_x = num_tiles_across - 1

        if min_y < 0:
            min_y = 0
        elif min_y > (num_tiles_across - 1):
            min_y = num_tiles_across - 1

        if max_y < 0:
            max_y = 0
        elif max_y > (num_tiles_across - 1):
            max_y = num_tiles_across - 1
        
        return (min_x, max_x, min_y, max_y)
        
        
        
        