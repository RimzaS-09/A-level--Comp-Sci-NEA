import math

from PySide6.QtCore import QObject, Signal, Slot
from models import tms_to_xyz, longlat_to_world

TILE_SIZE = 256
PI = math.pi






class Viewport(QObject):
    
    # Will emit signal in format:
    #   ( zoom_level: int, (min_x, max_x, min_y, max_y) )
    tiles_in_viewport = Signal(tuple)
    
    def __init__(self,
                longlat_centre: tuple,
                zoom_level = 0,
                screen_dimensions: tuple[int, int] = (800, 600),       
                ):
        super().__init__()
        
        self._centre = longlat_to_world(zoom_level, math.radians(longlat_centre[0]), math.radians(longlat_centre[1]))
        self._zoom_level = zoom_level
        self._screen_dimensions = screen_dimensions
        self._screen_centre = ( screen_dimensions[0] / 2, screen_dimensions[1] / 2 )
        
        self._min_zoom = 0
        self._max_zoom = 20
                
    
    def calculate_centre(self, lower_bound, upper_bound) -> tuple:
        centre_x = (lower_bound[0] + upper_bound[0]) / 2
        centre_y = (lower_bound[1] + upper_bound[1]) / 2
        
        return (centre_x, centre_y)
    
    def pan(self, dx, dy):
        scale = self.get_scale()
        new_x = self._centre[0] - dx
        new_y = self._centre[1] - dy
        
        self._centre = (new_x, new_y)
        
        self.tiles_in_viewport.emit( (self._zoom_level, self.get_tiles_visible()) )
        self.clamp()
    
    
    ### Getters and setters ###
    
    def get_centre(self):
        return self._centre
    
    def get_zoom_level(self):
        return self._zoom_level
    
    def get_screen_size(self):
        return self._screen_dimensions
        
    def get_screen_centre(self):
        return self._screen_centre
    
    def set_screen_size(self, screen_dimensions: tuple[int, int]):
        self._screen_dimensions = screen_dimensions
        self._screen_centre = ( screen_dimensions[0] / 2, screen_dimensions[1] / 2 )
        
        
    def set_zoom_limits(self, minimum, maximum):
        self._min_zoom = minimum
        self._max_zoom = maximum
    
    
    
    def clamp(self):
        world_size = TILE_SIZE * (2 ** self._zoom_level)
        
        if self._centre[0] > world_size:
            clamped_x = world_size
        elif self._centre[0] < 0.0:
            clamped_x = 0.0
        else:
            clamped_x = self._centre[0]
            
        
        if self._centre[1] > world_size:
            clamped_y = world_size
        elif self._centre[1] < 0.0:
            clamped_y = 0.0
        else:
            clamped_y = self._centre[1]
            
        self._centre = (clamped_x, clamped_y)
        
    def get_scale(self):
        return 2 ** self._zoom_level
        
    def check_zoom_level(self, new_zoom):
        """returns a bool, to ensure zoom is legal or not."""
        
        if (new_zoom < self._min_zoom) or (new_zoom > self._max_zoom):
            return False
        
        return True
    
    def zoom_to_point(self, mouse_x, mouse_y, delta):
        
        old_zoom = self._zoom_level
        new_zoom = old_zoom + delta
        
        if not self.check_zoom_level(new_zoom):
            return
        
        old_scale = 2 ** old_zoom
        new_scale = 2 ** new_zoom
        
        scale_ratio = new_scale / old_scale
        
        screen_centre = ( self._screen_dimensions[0] / 2, self._screen_dimensions[1] / 2 )
        
        offset_x = mouse_x - screen_centre[0]
        offset_y = mouse_y - screen_centre[1]
        
        world_x = ( self._centre[0] + (offset_x) ) * (scale_ratio)
        world_y = ( self._centre[1] + (offset_y) ) * (scale_ratio)
        
        self._centre = (world_x - (offset_x) , world_y - (offset_y))
                
        self._zoom_level = new_zoom
        
        self.tiles_in_viewport.emit( (self._zoom_level, self.get_tiles_visible()) )
    
    def get_visible_world(self):
        """Returns the visible section of the map in world coords, as the midpoints of each side of a rectangle"""
        
        scale = self.get_scale()
        
        width_offset = self._screen_dimensions[0] / 2
        height_offset = self._screen_dimensions[1] / 2
        
        return (
            self._centre[0] - width_offset,
            self._centre[1] - height_offset,
            self._centre[0] + width_offset,
            self._centre[1] + height_offset
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
        
        num_tiles_across = 2 ** self._zoom_level
        
        # World coordinates go from 0-256 at zoom 0
        tile_world_size = TILE_SIZE

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
            
        # TMS conversion 
        min_y = tms_to_xyz(min_y, self._zoom_level)
        max_y = tms_to_xyz(max_y, self._zoom_level)
        
        # The TMS conversion flips the two variables. min becomes max, max becomes min. This reverses it (hopefully)
        if max_y < min_y:
            temp = min_y
            min_y = max_y
            max_y = temp
        
        return (min_x, max_x, min_y, max_y)
        
        
        
        