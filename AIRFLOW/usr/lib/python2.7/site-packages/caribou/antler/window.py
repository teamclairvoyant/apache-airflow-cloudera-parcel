# -*- coding: utf-8 -*-
#
# Caribou - text entry and UI navigation application
#
# Copyright (C) 2009 Eitan Isaacson <eitan@monotonous.org>
# Copyright (C) 2010 Warp Networks S.L.
#  * Contributor: Daniel Baeyens <dbaeyens@warp.es>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import gi
gi.require_version('Clutter', '1.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Clutter
from .antler_settings import AntlerSettings
from math import sqrt
import os
import sys


class AnimatedWindowBase(Gtk.Window, Clutter.Animatable):
    __gproperties__ = {
        'antler-window-x' : (GObject.TYPE_INT, 'Window position',
                             'Window X coordinate',
                             GObject.G_MININT, GObject.G_MAXINT, 0,
                             GObject.PARAM_READWRITE),
        'antler-window-y' : (GObject.TYPE_INT, 'Window position',
                             'Window Y coordinate',
                             GObject.G_MININT, GObject.G_MAXINT, 0,
                             GObject.PARAM_READWRITE)
        }
    def __init__(self):
        GObject.GObject.__init__(self, type=Gtk.WindowType.POPUP)
        Clutter.init(None)

        # animation
        self._stage = Clutter.Stage.get_default()
        self._move_animation = None
        self._opacity_animation = None

    def do_get_property(self, property):
        if property.name == "antler-window-x":
            return self.get_position()[0]
        elif property.name == "antler-window-y":
            return self.get_position()[1]
        else:
            raise AttributeError('unknown property %s' % property.name)

    def do_set_property(self, property, value):
        if property.name == "antler-window-x":
            if value is not None:
                self.move(value, self.get_position()[1])
        elif property.name == "antler-window-y":
            if value is not None:
                self.move(self.get_position()[0], value)
        else:
            raise AttributeError('unknown property %s' % property.name)

    def do_animate_property(self, animation, prop_name, initial_value,
                            final_value, progress, gvalue):
        if prop_name == "antler-window-x":
            dx = int(initial_value * progress)
            self.move(initial_value + dx, self.get_position()[1])
            return True
        elif prop_name == "antler-window-y":
            dy = int(initial_value * progress)
            self.move(self.get_position()[0], initial_value + dy)
            return True
        if prop_name == "opacity":
            opacity = initial_value + ((final_value - initial_value) * progress)
            GObject.idle_add(lambda: self.set_opacity(opacity))
            return True
        else:
            return False

    def animated_move(self, x, y, mode=Clutter.AnimationMode.EASE_OUT_CUBIC):
        self._move_animation = Clutter.Animation(object=self,
                                            mode=mode,
                                            duration=250)
        self._move_animation.bind("antler-window-x", x)
        self._move_animation.bind("antler-window-y", y)

        timeline = self._move_animation.get_timeline()
        timeline.start()

        return self._move_animation

    def animated_opacity(self, opacity, mode=Clutter.AnimationMode.EASE_OUT_CUBIC):
        if opacity == self.get_opacity():
            return None
        if self._opacity_animation is not None:
            if self._opacity_animation.has_property('opacity'):
                timeline = self._opacity_animation.get_timeline()
                timeline.pause()
                self._opacity_animation.unbind_property('opacity')

        self._opacity_animation = Clutter.Animation(object=self, mode=mode,
                                                    duration=100)
        self._opacity_animation.bind("opacity", opacity)

        timeline = self._opacity_animation.get_timeline()
        timeline.start()

        return self._opacity_animation


class ProximityWindowBase(AnimatedWindowBase):
    def __init__(self):
        AnimatedWindowBase.__init__(self)
        self._poll_tid = 0
        settings = AntlerSettings()
        self.max_distance = settings.max_distance.value
        settings.max_distance.connect("value-changed", self._on_max_dist_changed)
        min_alpha = settings.min_alpha
        max_alpha = settings.max_alpha
        min_alpha.connect("value-changed",
                                   self._on_min_alpha_changed, max_alpha)
        max_alpha.connect("value-changed",
                                   self._on_max_alpha_changed, min_alpha)
        self.connect('map-event', self._onmapped, settings)

    def _on_max_dist_changed(self, setting, value):
        self.max_distance = value

    def _set_min_max_alpha(self, min_alpha, max_alpha):
        if min_alpha > max_alpha:
            min_alpha = max_alpha
        self.max_alpha = max_alpha
        self.min_alpha = min_alpha
        if self.max_alpha != self.min_alpha:
            if self._poll_tid == 0:
                self._poll_tid = GObject.timeout_add(100, self._proximity_check)
        elif self._poll_tid != 0:
            GObject.source_remove(self._poll_tid)

    def _onmapped(self, obj, event, settings):
        if self.is_composited():
            self._set_min_max_alpha(settings.min_alpha.value,
                                    settings.max_alpha.value)
            self._proximity_check()

    def _on_min_alpha_changed(self, setting, value, max_alpha):
        self._set_min_max_alpha(value, max_alpha.value)

    def _on_max_alpha_changed(self, setting, value, min_alpha):
        self._set_min_max_alpha(min_alpha.value, value)

    def _proximity_check(self):
        px, py = self.get_pointer()

        ww = self.get_allocated_width()
        wh = self.get_allocated_height()

        distance =  self._get_distance_to_bbox(px, py, ww, wh)

        opacity = (self.max_alpha - self.min_alpha) * \
            (1 - min(distance, self.max_distance)/self.max_distance)
        opacity += self.min_alpha

        self.animated_opacity(opacity)

        if not self.props.visible:
            self._poll_tid = 0
            return False

        return True

    def _get_distance_to_bbox(self, px, py, bw, bh):
        if px < 0:
            x_distance = float(abs(px))
        elif px > bw:
            x_distance = float(px - bw)
        else:
            x_distance = 0.0

        if py < 0:
            y_distance = float(abs(py))
        elif py > bh:
            y_distance = float(py - bh)
        else:
            y_distance = 0.0

        if y_distance == 0 and x_distance == 0:
            return 0.0
        elif y_distance != 0 and x_distance == 0:
            return y_distance
        elif y_distance == 0 and x_distance != 0:
            return x_distance
        else:
            x2 = 0 if x_distance > 0 else bw
            y2 = 0 if y_distance > 0 else bh
            return sqrt((px - x2)**2 + (py - y2)**2)

class AntlerWindow(ProximityWindowBase):
    def __init__(self, keyboard_view_factory, placement=None,
                 min_alpha=1.0, max_alpha=1.0, max_distance=100):
        ProximityWindowBase.__init__(self)

        self.set_name("AntlerWindow")

        ctx = self.get_style_context()
        ctx.add_class("antler-keyboard-window")

        settings = AntlerSettings()
        settings.keyboard_type.connect('value-changed', self.on_kb_type_changed)

        self._vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self._vbox)

        self.keyboard_view_factory = keyboard_view_factory
        self.keyboard_view = keyboard_view_factory (keyboard_type=settings.keyboard_type.value)

        self._vbox.pack_start(self.keyboard_view, True, True, 0)

        self.connect("size-allocate", self.on_size_allocate)

        self._cursor_location = Rectangle()
        self._entry_location = Rectangle()
        self.placement = placement or \
            AntlerWindowPlacement()

    def on_kb_type_changed(self, setting, value):
        self._vbox.remove(self.keyboard_view)
        self.resize(1, 1)
        self.keyboard_view = self.keyboard_view_factory (value)
        self._vbox.pack_start(self.keyboard_view, True, True, 0)
        self.keyboard_view.show_all()

    def on_size_allocate(self, widget, allocation):
        self._update_position()

    def destroy(self):
        self.keyboard.destroy()
        super(Gtk.Window, self).destroy()

    def set_cursor_location(self, x, y, w, h):
        self._cursor_location = Rectangle(x, y, w, h)
        self._update_position()

    def set_entry_location(self, x, y, w, h):
        self._entry_location = Rectangle(x, y, w, h)
        self._update_position()

    def set_placement(self, placement):
        self.placement = placement
        self._update_position()

    def _get_root_bbox(self):
        root_window = Gdk.get_default_root_window()
        args = root_window.get_geometry()

        root_bbox = Rectangle(*args)

        # TODO: Do whatever we need to do to place the keyboard correctly
        # in GNOME Shell and Unity.
        #

        return root_bbox

    def _calculate_position(self, placement=None):
        root_bbox = self._get_root_bbox()
        placement = placement or self.placement

        x = self._calculate_axis(placement.x, root_bbox)
        y = self._calculate_axis(placement.y, root_bbox)

        return x, y

    def get_expected_position(self):
        x, y = self._calculate_position()
        origx, origy = x, y
        root_bbox = self._get_root_bbox()
        proposed_position = Rectangle(x, y, self.get_allocated_width(),
                                      self.get_allocated_height())

        x += self.placement.x.adjust_to_bounds(root_bbox, proposed_position)
        y += self.placement.y.adjust_to_bounds(root_bbox, proposed_position)
        return self.get_position() != (x, y) != y, x, y

    def _update_position(self):
        changed, x, y = self.get_expected_position()
        if changed:
            self.move(x, y)

    def _calculate_axis(self, axis_placement, root_bbox):
        bbox = root_bbox

        if axis_placement.stickto == AntlerWindowPlacement.CURSOR:
            bbox = self._cursor_location
        elif axis_placement.stickto == AntlerWindowPlacement.ENTRY:
            bbox = self._entry_location

        offset = axis_placement.get_offset(bbox.x, bbox.y)

        if axis_placement.align == AntlerWindowPlacement.END:
            offset += axis_placement.get_length(bbox.width, bbox.height)
            if axis_placement.gravitate == AntlerWindowPlacement.INSIDE:
                offset -= axis_placement.get_length(
                    self.get_allocated_width(),
                    self.get_allocated_height())
        elif axis_placement.align == AntlerWindowPlacement.START:
            if axis_placement.gravitate == AntlerWindowPlacement.OUTSIDE:
                offset -= axis_placement.get_length(
                    self.get_allocated_width(),
                    self.get_allocated_height())
        elif axis_placement.align == AntlerWindowPlacement.CENTER:
            offset += axis_placement.get_length(bbox.width, bbox.height)/2

        return offset

class AntlerWindowDocked(AntlerWindow):
    def __init__(self, keyboard_view_factory, horizontal_roll=False):
        placement = AntlerWindowPlacement(
            xalign=AntlerWindowPlacement.START,
            yalign=AntlerWindowPlacement.END,
            xstickto=AntlerWindowPlacement.SCREEN,
            ystickto=AntlerWindowPlacement.SCREEN,
            xgravitate=AntlerWindowPlacement.INSIDE)

        AntlerWindow.__init__(self, keyboard_view_factory, placement)

        self.horizontal_roll = horizontal_roll
        self._rolled_in = False


    def show_all(self):
        super(AntlerWindow, self).show_all()

    def on_size_allocate(self, widget, allocation):
        self._roll_in()

    def _roll_in(self):
        if self._rolled_in:
            return
        self._rolled_in = True

        x, y = self._get_preroll_position()
        self.move(x, y)

        x, y = self._get_postroll_position()
        return self.animated_move(x, y)

    def _get_preroll_position(self):
        _, x, y = self.get_expected_position()

        if self.horizontal_roll:
            newy = y
            if self.placement.x.align == AntlerWindowPlacement.END:
                newx = x + self.get_allocated_width()
            else:
                newx = x - self.get_allocated_width()
        else:
            newx = x
            if self.placement.y.align == AntlerWindowPlacement.END:
                newy = y + self.get_allocated_height()
            else:
                newy = y - self.get_allocated_height()

        return newx, newy

    def _get_postroll_position(self):
        x, y = self.get_position()

        if self.horizontal_roll:
            newy = y
            if self.placement.x.align != AntlerWindowPlacement.END:
                newx = x + self.get_allocated_width()
            else:
                newx = x - self.get_allocated_width()
        else:
            newx = x
            if self.placement.y.align != AntlerWindowPlacement.END:
                newy = y + self.get_allocated_height()
            else:
                newy = y - self.get_allocated_height()

        return newx, newy

    def _roll_out(self):
        if not self._rolled_in:
            return
        self._rolled_in = False;
        x, y = self.get_position()
        return self.animated_move(x + self.get_allocated_width(), y)

    def hide(self):
        animation = self._roll_out()
        animation.connect('completed', lambda x: AntlerWindow.hide(self))

class AntlerWindowEntry(AntlerWindow):
    def __init__(self, keyboard_view_factory):
        placement = AntlerWindowPlacement(
            xalign=AntlerWindowPlacement.START,
            xstickto=AntlerWindowPlacement.ENTRY,
            ystickto=AntlerWindowPlacement.ENTRY,
            xgravitate=AntlerWindowPlacement.INSIDE,
            ygravitate=AntlerWindowPlacement.OUTSIDE)

        AntlerWindow.__init__(self, keyboard_view_factory, placement)


    def _calculate_axis(self, axis_placement, root_bbox):
        offset = AntlerWindow._calculate_axis(self, axis_placement, root_bbox)
        if axis_placement.axis == 'y':
            if offset + self.get_allocated_height() > root_bbox.height + root_bbox.y:
                new_axis_placement = axis_placement.copy(align=AntlerWindowPlacement.START)
                offset = AntlerWindow._calculate_axis(self, new_axis_placement, root_bbox)

        return offset

class AntlerWindowPlacement(object):
    START = 'start'
    END = 'end'
    CENTER = 'center'

    SCREEN = 'screen'
    ENTRY = 'entry'
    CURSOR = 'cursor'

    INSIDE = 'inside'
    OUTSIDE = 'outside'

    class _AxisPlacement(object):
        def __init__(self, axis, align, stickto, gravitate):
            self.axis = axis
            self.align = align
            self.stickto = stickto
            self.gravitate = gravitate

        def copy(self, align=None, stickto=None, gravitate=None):
            return self.__class__(self.axis,
                                  align or self.align,
                                  stickto or self.stickto,
                                  gravitate or self.gravitate)

        def get_offset(self, x, y):
            return x if self.axis == 'x' else y

        def get_length(self, width, height):
            return width if self.axis == 'x' else height

        def adjust_to_bounds(self, root_bbox, child_bbox):
            child_vector_start = self.get_offset(child_bbox.x, child_bbox.y)
            child_vector_end = \
                self.get_length(child_bbox.width, child_bbox.height) + \
                child_vector_start
            root_vector_start = self.get_offset(root_bbox.x, root_bbox.y)
            root_vector_end = self.get_length(
                root_bbox.width, root_bbox.height) + root_vector_start

            if root_vector_end < child_vector_end:
                return root_vector_end - child_vector_end

            if root_vector_start > child_vector_start:
                return root_vector_start - child_vector_start

            return 0


    def __init__(self,
                 xalign=None, xstickto=None, xgravitate=None,
                 yalign=None, ystickto=None, ygravitate=None):
        self.x = self._AxisPlacement('x',
                                     xalign or self.END,
                                     xstickto or self.CURSOR,
                                     xgravitate or self.OUTSIDE)
        self.y = self._AxisPlacement('y',
                                     yalign or self.END,
                                     ystickto or self.CURSOR,
                                     ygravitate or self.OUTSIDE)

class Rectangle(object):
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

if __name__ == "__main__":
    import keyboard_view
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    w = AntlerWindowDocked(keyboard_view.AntlerKeyboardView)
    w.show_all()

    try:
        Gtk.main()
    except KeyboardInterrupt:
        Gtk.main_quit()
