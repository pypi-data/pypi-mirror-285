""" 
    Deal with ImageViewer mouse events
"""

from typing import TypeVar, TYPE_CHECKING
from qimview.utils.qt_imports import QtGui, QtCore, QtWidgets
if TYPE_CHECKING:
    from qimview.image_viewers.image_viewer import ImageViewer
from .mouse_events import MouseEvents, MouseMotionActions

# T is a type that inherits from QWidget
V = TypeVar('V', bound='ImageViewer')

class MousePanActions(MouseMotionActions[V]):
    """ Panning while mouse button is pressed """
    def press(self, event : QtGui.QMouseEvent) -> None:
        """ Press event """
        super().press(event)
        event.setAccepted(True)
    def move(self, event: QtGui.QMoveEvent) -> None:
        """ Move event """
        super().move(event)
        self._widget.mouse_pos = event.pos()
        self._widget.mouse_displ = self._delta
        self._widget.viewer_update()
        self._widget.synchronize()
        event.accept()
    def release(self, event: QtGui.QMouseEvent) -> None:
        """ Release event """
        self._widget.current_dx = int(self._widget.check_translation()[0])
        self._widget.current_dy = int(self._widget.check_translation()[1])
        super().release(event)
        self._widget.mouse_displ = self._delta

class MouseZoomActions(MouseMotionActions[V]):
    """ Zooming while mouse button is pressed """
    def press(self, event : QtGui.QMouseEvent) -> None:
        """ Press event """
        super().press(event)
        event.setAccepted(True)
    def move(self, event: QtGui.QMoveEvent) -> None:
        """ Move event """
        super().move(event)
        self._widget.mouse_pos = event.pos()
        self._widget.mouse_zoom_displ = self._delta
        self._widget.viewer_update()
        self._widget.synchronize()
        event.accept()
    def release(self, event: QtGui.QMouseEvent) -> None:
        """ Release event """
        im = self._widget.get_image()
        if im is not None:
            self._widget.current_scale = self._widget.new_scale(-self._delta.y(),im.data.shape[0])
        super().release(event)
        self._widget.mouse_zoom_displ = self._delta

class ImageViewerMouseEvents(MouseEvents[V]):
    """ Implement events for ImageViewer """
 
    def __init__(self, viewer: V):
        super().__init__(viewer)

        # # Accept touch events
        # viewer._widget.setAttribute(QtCore.Qt.WidgetAttribute.WA_AcceptTouchEvents)

        self._mouse_callback.update({
            'Left+DblClick'              : self.toggle_fullscreen,
            'Left+DblClick on histogram' : self.toggle_histo_size,
            # Touch pad panning will be interpreted as Wheel event
            'Wheel'                      : self.wheel_pan,
            'Shft+Wheel'                 : self.wheel_pan_horizontal,
            # Set Ctrl+Wheel for touch pad zooming with 2 fingers
            'Ctrl+Wheel'                 : self.wheel_zoom,
            'Move on text'               : self.tooltip_image_filename,
        })

        self._motion_classes.update({
            'Left Motion'      : MousePanActions,
            'Ctrl+Left Motion' : MouseZoomActions,
            'Middle Motion'    : MouseZoomActions,
        })

        def in_histo(point:QtCore.QPoint)->bool:
            if self._widget._histo_rect:
                return self._widget._histo_rect.contains(point)
            return False

        def in_text(point:QtCore.QPoint)->bool:
            if self._widget._text_rect:
                return self._widget._text_rect.contains(point)
            return False

        self._regions.update({
            'histogram'  : in_histo,
            'text'       : in_text,
        })

    def mouse_move_unpressed(self, event: QtGui.QMoveEvent)->None:
        """ Actions while moving the mouse without pressing any button """
        if self._widget._show_overlap:
            self._widget.mouse_pos = event.pos()
            self._widget.viewer_update()
            event.accept()
        elif self._widget.show_cursor:
            self._widget.mouse_pos = event.pos()
            self._widget.viewer_update()
            self._widget.synchronize()
            event.accept()
        else:
            event.ignore()

    def toggle_histo_size(self, _)->bool:
        """ Switch histogram scale from 1 to 3 """
        self._widget._histo_scale = (self._widget._histo_scale % 3) + 1 
        self._widget.viewer_update()
        return True
    
    def toggle_fullscreen(self, _) -> bool:
        """ toggle fullscreen mode """
        return self._widget._fullscreen.toggle_fullscreen(self._widget._widget)

    def wheel_zoom(self, event: QtGui.QWheelEvent) -> bool:
        """ Zoom in/out based on wheel angle, works with touchpad 2 fingers """
        # Zoom by applying a factor to the distances to the sides
        # print(f"{event.angleDelta(), event.deviceType(), event.source()}")
        delta = event.angleDelta().y()
        # print("delta = {}".format(delta))
        coeff = delta/5
        # coeff = 20 if delta > 0 else -20
        if im := self._widget.get_image():
            self._widget.current_scale = self._widget.new_scale(coeff, im.data.shape[0])
            self._widget.viewer_update()
            self._widget.synchronize()
            return True
        return False

    def wheel_pan(self, event: QtGui.QWheelEvent) -> bool:
        """ Pan (image translation) based on wheel angle, mainly for touchpad """
        # Zoom by applying a factor to the distances to the sides
        # print(f"{event.angleDelta(), event.deviceType(), event.source()}")
        delta = event.angleDelta()
        if im := self._widget.get_image():
            # Reduce wheel delta for smaller translations
            self._widget.mouse_displ = delta/3
            # Update current displacement
            self._widget.current_dx = int(self._widget.check_translation()[0])
            self._widget.current_dy = int(self._widget.check_translation()[1])
            self._widget.viewer_update()
            self._widget.synchronize()
            return True
        return False

    def wheel_pan_horizontal(self, event: QtGui.QWheelEvent) -> bool:
        """ Pan horizontal (image horizontal translation) based on wheel angle """
        # Zoom by applying a factor to the distances to the sides
        # print(f"{event.angleDelta(), event.deviceType(), event.source()}")
        delta = event.angleDelta()
        # To translation horizontally using wheel mouse
        delta.setX(delta.y()/3)
        delta.setY(0)
        if im := self._widget.get_image():
            self._widget.mouse_displ = delta
            # Update current displacement
            self._widget.current_dx = int(self._widget.check_translation()[0])
            self._widget.current_dy = int(self._widget.check_translation()[1])
            self._widget.viewer_update()
            self._widget.synchronize()
            return True
        return False

    def tooltip_image_filename(self, event: QtGui.QMoveEvent) -> bool:
        """ Display image filename as tooltip """
        global_pos = self._widget.mapToGlobal(event.pos())
        QtWidgets.QToolTip.showText(global_pos, f"{self._widget._image.filename}", 
                                    self._widget, self._widget._text_rect)
        # Return False to allow event propagation
        return False
