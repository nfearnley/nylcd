from typing import List, Tuple
import cv2
import numpy as np

import pygame.surfarray
import pygame.font

from pygame.color import Color
from pygame.constants import BLEND_MULT, BLEND_SUB
from pygame.surface import Surface

class LCDSegment:
    def __init__(self, surf, pos: Tuple[int, int], fgcolor, shadowcolor=None):
        self.pos = pos
        self.fg_surf = shape_color(surf, fgcolor)
        self.shadow_surf = shape_color(surf, shadowcolor)
        self.active = False

    def toggle(self):
        self.active = not self.active

    @property
    def x(self):
        return self.pos[0]
        
    @property
    def y(self):
        return self.pos[1]

    @property
    def center(self):
        w, h = self.fg_surf.get_size()
        return self.x+(w//2), self.y+(h//2)

    def render_shadow_to(self, dest):
        dest.blit(self.shadow_surf, (self.x-2, self.y+3))

    def render_fg_to(self, dest):
        dest.blit(self.fg_surf, (self.x, self.y))

    def render_debug_to(self, dest, num, font: pygame.font.Font):
        surf = font.render(f"{num:X}", False, Color("red"), Color("#ff00ff"))
        w, h = surf.get_size()
        x, y = self.center
        x -= w//2
        y -= h//2
        surf.set_colorkey("#ff00ff")
        dest.blit(surf, (x,y))



class LCDSurface:
    def __init__(self, src: Surface, *,
        fgcolor: Color = Color("#111d29"),
        shadowcolor: Color = Color("#5a605a"),
        bgcolor: Color = Color("#7d8176"),
    ):
        self.surface: Surface = Surface(src.get_size())
        self.segments = split_lcd_segments(src, fgcolor, shadowcolor)
        self.show_shadow = shadowcolor is not None
        self.show_debug = False
        if bgcolor is None:
            bgcolor = Color("#ff00ff")
            self.surface.set_colorkey(Color("#ff00ff"))
        self.bgcolor = bgcolor
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 64)

    def render(self):
        self.surface.fill(self.bgcolor)
        segments = self.get_active_segments()
        if self.show_shadow:
            for seg in segments:
                seg.render_shadow_to(self.surface)
        for seg in segments:
            seg.render_fg_to(self.surface)
        if self.show_debug:
            for num, seg in enumerate(self.segments):
                seg.render_debug_to(self.surface, num, self.font)
            

    def get_active_segments(self):
        return [seg for seg in self.segments if seg.active]

    def get_size(self):
        return self.surface.get_size()


def split_lcd_segments(surf, fgcolor, shadowcolor=None):
    image = pygame.surfarray.array3d(surf).swapaxes(0, 1)
    if image is None:
        print(f"Unable to load image")
        raise FileNotFoundError("Unable to load image")

    image = ~image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    num_labels, labels = cv2.connectedComponents(binary, connectivity=4)

    segments: List[LCDSegment] = []
    for labelnum in range(1, num_labels):
        segment_arr = np.array(labels, dtype=np.uint8)
        segment_arr[labels == labelnum] = 255
        segment_arr[labels != labelnum] = 0
        x, y, w, h = cv2.boundingRect(segment_arr)
        segment_cropped = segment_arr[y:y+h, x:x+w]
        segment_cropped = cv2.cvtColor(segment_cropped, cv2.COLOR_GRAY2RGB)
        segment_surf = pygame.surfarray.make_surface(segment_cropped.swapaxes(0, 1))
        segment = LCDSegment(segment_surf, (x, y), fgcolor, shadowcolor)
        segments.append(segment)
    
    return segments

def shape_color(surf, color):
    if color is None:
        return None
    out_surf = Surface(surf.get_size())
    if color == Color("black"):
        out_surf.fill(Color("white"))
        out_surf.blit(surf, (0,0), special_flags=BLEND_SUB)
        out_surf.set_colorkey(Color("white"))
    else:
        out_surf.fill(color)
        out_surf.blit(surf, (0,0), special_flags=BLEND_MULT)
        out_surf.set_colorkey(Color("black"))
    return out_surf
