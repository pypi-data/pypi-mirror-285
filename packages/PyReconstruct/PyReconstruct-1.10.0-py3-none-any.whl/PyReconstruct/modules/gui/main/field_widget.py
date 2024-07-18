import os
import time

from PySide6.QtWidgets import (
    QWidget, 
    QMainWindow, 
    QInputDialog, 
    QGestureEvent,
    QTextEdit
)
from PySide6.QtCore import (
    Qt, 
    QPoint, 
    QEvent,
    QTimer,
    QLine,
)
from PySide6.QtGui import (
    QPixmap, 
    QPen,
    QColor,
    QPainter, 
    QPointingDevice,
    QCursor,
    QFont,
    QTransform,
    QAction
)

from PyReconstruct.modules.datatypes import Series, Trace, Ztrace, Flag
from PyReconstruct.modules.calc import pixmapPointToField, distance, colorize, ellipseFromPair, lineDistance
from PyReconstruct.modules.backend.view import FieldView, snapTrace, drawArrow
from PyReconstruct.modules.backend.table import (
    TableManager
)
from PyReconstruct.modules.gui.dialog import TraceDialog, QuickDialog, FlagDialog
from PyReconstruct.modules.gui.utils import notify, drawOutlinedText, notifyLocked
from PyReconstruct.modules.constants import locations as loc

class FieldWidget(QWidget, FieldView):
    # mouse modes
    POINTER, PANZOOM, KNIFE, SCISSORS, CLOSEDTRACE, OPENTRACE, STAMP, GRID, FLAG, HOST = range(10)

    def __init__(self, series : Series, mainwindow : QMainWindow):
        """Create the field widget.
        
            Params:
                series (Series): the series object
                mainwindow (MainWindow): the main window that contains this widget
        """
        super().__init__(mainwindow)
        self.mainwindow = mainwindow
        self.setMouseTracking(True)

        # enable touch gestures
        Qt.WA_AcceptTouchEvents = True
        gestures = [Qt.GestureType.PinchGesture]
        for g in gestures:
            self.grabGesture(g)
        self.is_gesturing = False

        # set initial geometry to match parent
        parent_rect = self.mainwindow.geometry()
        self.pixmap_dim = parent_rect.width(), parent_rect.height()-20
        self.setGeometry(0, 0, *self.pixmap_dim)

        # misc defaults
        self.current_trace = []
        self.max_click_time = 0.15
        self.click_time = None
        self.single_click = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.clicked_trace = None
        self.mouse_boundary_timer = None
        pencil_pm = QPixmap(os.path.join(loc.img_dir, "pencil.cur"))
        self.pencil_r = QCursor(
            pencil_pm,
            hotX=5, hotY=5
        )
        self.pencil_l = QCursor(
            pencil_pm.transformed(QTransform(-1, 0, 0, 1, 0, 0)),
            hotX=pencil_pm.width()-5, hotY=5
        )
        self.table_manager = None
        self.hosted_trace = None

        # set up the information display widget
        self.hover_display = None
        self.displayed_item = None
        self.hover_display_timer = QTimer(self)
        self.hover_display_timer.setSingleShot(True)
        self.hover_display_timer.timeout.connect(
            self.displayHoverInfo
        )
        # set up flag edit event
        self.edit_flag_event = QAction(self)
        self.edit_flag_event.triggered.connect(self.editFlag)
        self.trigger_edit_flag = False

        self.createField(series)

        self.show()
    
    def createField(self, series : Series):
        """Re-creates the field widget.
        
            Params:
                series (Series): the new series to load
        """
        # close the manager if applicable
        if self.table_manager:
            self.table_manager.closeAll()
        
        self.series = series
        self.createFieldView(series)

        # create a new manager
        self.table_manager = TableManager(
            self.series,
            self.section,
            self.series_states,
            self.mainwindow,
        )

        # default mouse mode: pointer
        self.mouse_mode = FieldWidget.POINTER
        self.setCursor(QCursor(Qt.ArrowCursor))

        # ensure that the first section is found
        if self.series.current_section not in self.series.sections:
            self.series.current_section = self.series.sections.keys()[0]

        # establish misc defaults
        self.tracing_trace = Trace("TRACE", (255, 0, 255))
        self.status_list = ["Section: " + str(self.series.current_section)]
        self.blend_sections = False
        self.lclick = False
        self.rclick = False
        self.mclick = False

        self.erasing = False
        self.is_panzooming = False
        self.is_gesturing = False
        self.is_line_tracing = False
        self.is_moving_trace = False
        self.is_selecting_traces = False
        self.is_scissoring = False
        self.closed_trace_shape = "trace"

        self.selected_trace_names = {}
        self.selected_ztrace_names = {}

        # set up the timer
        if not self.series.isWelcomeSeries():
            self.time = str(round(time.time()))
            open(os.path.join(self.series.getwdir(), self.time), "w").close()
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.markTime)
            self.timer.start(5000)

        self.generateView()

    def markTime(self):
        """Keep track of the time on the series file."""
        try:
            for f in os.listdir(self.series.getwdir()):
                if "." not in f and f.isnumeric():
                    os.remove(os.path.join(self.series.getwdir(), f))
                    break
            self.time = str(round(time.time()))
            open(os.path.join(self.series.getwdir(), self.time), "w").close()
        except FileNotFoundError:
            pass
    
    def toggleBlend(self):
        """Toggle blending sections."""
        self.blend_sections = not self.blend_sections
        self.generateView()
    
    def setViewMagnification(self, new_mag : float = None):
        """Set the scaling for the section view.
        
            Params:
                new_mag (float): the new magnification (pixels per micron)
        """
        if new_mag is None:
            new_mag, confirmed = QInputDialog.getText(
                self,
                "View Magnification",
                "Enter view magnification (pixels per micron):",
                text=str(round(1 / self.series.screen_mag, 6))
            )
            if not confirmed:
                return
            try:
                new_mag = float(new_mag)
            except ValueError:
                return
        else:
            new_mag = 1 / new_mag
        
        self.setView(new_mag)
    
    def generateView(self, generate_image=True, generate_traces=True, update=True):
        """Generate the output view.
        
            Params:
                generate_image (bool): True if image should be regenerated
                generate_traces (bool): True if traces should be regenerated
                update (bool): True if view widget should be updated
        """
        self.field_pixmap = FieldView.generateView(
            self,
            self.pixmap_dim,
            generate_image,
            generate_traces,
            blend=self.blend_sections
        )
        self.mainwindow.checkActions()
        if update:
            self.update()
    
    def openList(self, list_type : str):
        """Open a list.
        
            Params:
                list_type (str): object, trace, section, ztrace, or flag
        """
        self.table_manager.newTable(list_type, self.section)
    
    def unlockSection(self):
        """Unlock the current section."""
        self.section.align_locked = False
        self.updateData()
        self.mainwindow.seriesModified()
    
    def findContourDialog(self):
        """Open a dilog to prompt user to find contour."""
        contour_name, confirmed = QInputDialog.getText(
            self,
            "Find Contour",
            "Enter the contour name:",
        )
        if not confirmed:
            return
        self.findContour(contour_name)
    
    def drawBorder(self, painter : QPainter, color : tuple):
        """Draw a border around the field (called during paintEvent).
        
            Params:
                painter (QPainter): the painter for the field
                color(tuple): the color for the border
        """
        pen = QPen(QColor(*color), 8)
        if self.border_exists:
            pen.setDashPattern([2, 2, 2, 2])
        painter.setPen(pen)
        w, h = self.width(), self.height()
        points = [
            (0, 0),
            (0, h),
            (w, h),
            (w, 0)
        ]
        for i in range(len(points)):
            painter.drawLine(*points[i-1], *points[i])
        self.border_exists = True
    
    def closeHoverDisplay(self):
        """Close the hover information display."""
        if self.hover_display:
            self.hover_display.close()
            self.hover_display = None
        self.displayed_item = None
        if self.hover_display_timer.isActive():
            self.hover_display_timer.stop()
    
    def displayHoverInfo(self):
        """Display the information for an item that has been hovered over."""
        text = ""
        if type(self.displayed_item) is Flag:
            # create text edit display for comments
            comments = []
            for c in self.displayed_item.comments:
                t = c.text.replace("\n", "<br>")
                comments.append(
                    f"<b>{c.user}</b> ({c.date}):<br>{t}"
                )
            text = "<hr>".join(comments)
        elif type(self.displayed_item) is Trace:
            t = self.displayed_item
            lines = []
            # lines.append([f"<b>{t.name}</b>"])
            def addLine(header, desc):
                if desc: lines.append(f"<b>{header}</b> {desc}")
            
            addLine("Host:", ", ".join(self.series.getObjHosts(t.name)))
            addLine("Comment:", self.series.getAttr(t.name, "comment"))
            addLine("Object Alignment:", self.series.getAttr(t.name, "alignment"))
            addLine("Object Groups:", ", ".join(self.series.object_groups.getObjectGroups(t.name)))
            addLine("Trace Tags:", ", ".join(t.tags))
            cat_cols = self.series.getAttr(t.name, "user_columns")
            for col_name, opt in cat_cols.items():
                addLine(f"{col_name}:", opt)

            text = "<hr>".join(lines)
        
        if not text:
            return
        
        # create the widget
        self.hover_display = QTextEdit(self.mainwindow, text=text)
        # show
        self.hover_display.show()
        # adjust the width and height
        self.hover_display.resize(self.width() // 5, 1)
        h = self.hover_display.document().size().toSize().height() + 3
        if h == 3:
            self.hover_display.setText("X")
            h = self.hover_display.document().size().toSize().height()
            self.hover_display.setText("")
        elif h > self.height() - 6:
            h = self.height() - 6
        self.hover_display.resize(self.width() // 5, h)
        # move to proper location
        right_justified = self.mainwindow.mouse_palette.mode_x <= .5
        if right_justified:
            self.hover_display.move(
                self.x() + self.width() - self.hover_display.width() - 3,
                self.y() + self.height() - self.hover_display.height() - 3
            )
        else:
            self.hover_display.move(
                self.x() + 3,
                self.y() + self.height() - self.hover_display.height() - 3
            )
        # scroll all the way down
        sb = self.hover_display.verticalScrollBar()
        sb.setValue(sb.maximum())
    
    def paintBorder(self, field_painter : QPainter):
        """Paint the borders for the field."""
        # draw record dot on the screen if recording transforms
        if self.propagate_tform:
            field_painter.setBrush(QColor(255, 0, 0))
            field_painter.drawEllipse(20, 20, 40, 40)
        
        # add red border if trace layer is hidden
        self.border_exists = False
        if self.hide_trace_layer:
            self.drawBorder(field_painter, (255, 0, 0))
        # add green border if all traces are being shown
        elif self.show_all_traces:
            self.drawBorder(field_painter, (0, 255, 0))
        # add magenta border if image is hidden
        if self.hide_image:
            self.drawBorder(field_painter, (255, 0, 255))
        # add cyan border if sections are being blended
        if self.blend_sections:
            self.drawBorder(field_painter, (0, 255, 255))
    
    def paintWorkingTrace(self, field_painter : QPainter):
        """Paint the work trace on the field."""
        # draw the working trace on the screen
        if self.current_trace:
            pen = None
            # if drawing lasso
            if ((self.mouse_mode == FieldWidget.POINTER and self.is_selecting_traces) or
                (self.mouse_mode == FieldWidget.STAMP and self.is_drawing_rad)
            ):
                closed = True
                pen = QPen(QColor(255, 255, 255), 1)
                pen.setDashPattern([4, 4])
            # if drawing host line
            if self.mouse_mode == FieldWidget.HOST:
                closed = False
                pen = QPen(QColor(255, 255, 255), 2)
            # if drawing knife
            elif self.mouse_mode == FieldWidget.KNIFE:
                closed = False
                pen = QPen(QColor(255, 0, 0), 1)
            # if drawing trace
            elif (
                self.mouse_mode == FieldWidget.OPENTRACE or
                self.mouse_mode == FieldWidget.CLOSEDTRACE
            ):
                closed = (self.mouse_mode == FieldWidget.CLOSEDTRACE and self.is_line_tracing or
                          self.mouse_mode == FieldWidget.CLOSEDTRACE and self.closed_trace_shape != "trace")
                color = QColor(*self.tracing_trace.color)
                pen = QPen(color, 1)
            
            # draw current trace if exists
            if pen:
                if self.mouse_mode == FieldWidget.HOST:
                    if len(self.current_trace) > 1:
                        line = QLine(*self.current_trace[0], *self.current_trace[1])
                        drawArrow(field_painter, line, False, True)
                else:
                    field_painter.setPen(pen)
                    if closed:
                        start = 0
                    else:
                        start = 1
                    for i in range(start, len(self.current_trace)):
                        field_painter.drawLine(*self.current_trace[i-1], *self.current_trace[i])
                    # draw dashed lines that connect to mouse pointer
                    if self.is_line_tracing:
                        pen.setDashPattern([2,5])
                        field_painter.setPen(pen)
                        field_painter.drawLine(*self.current_trace[-1], self.mouse_x, self.mouse_y)
                        if closed:
                            field_painter.drawLine(*self.current_trace[0], self.mouse_x, self.mouse_y)
            
        # unique method for drawing moving traces
        elif self.is_moving_trace:
            dx = self.mouse_x - self.clicked_x
            dy = self.mouse_y - self.clicked_y
            # redraw the traces with translatation
            for points, color, closed in self.moving_traces:
                field_painter.setPen(QPen(QColor(*color), 1))
                plot_points = [QPoint(x+dx, y+dy) for x,y in points]
                if closed:
                    field_painter.drawPolygon(plot_points)
                else:
                    field_painter.drawPolyline(plot_points)
            # redraw points with translation
            for (x, y), color in self.moving_points:
                field_painter.setPen(QPen(QColor(*color), 6))
                qpoint = QPoint(x+dx, y+dy)
                field_painter.drawPoint(qpoint)
            # redraw flag with translation
            for (x, y), color in self.moving_flags:
                field_painter.setPen(QPen(QColor(*color), 6))
                field_painter.setFont(QFont("Courier New", self.series.getOption("flag_size"), QFont.Bold))
                qpoint = QPoint(x+dx, y+dy)
                field_painter.drawText(qpoint, "⚑")

    def paintText(self, field_painter : QPainter):
        """Paint the corner text onto the field."""
        # place text on other side of mode palette (if applicable)
        if self.mainwindow.mouse_palette.mode_x > .5:
            x = 10
            right_justified = False
        else:
            x = self.width() - 10
            right_justified = True
        y = 0
        
        # draw the name of the closest trace on the screen
        # draw the selected traces to the screen
        ct_size = 12
        st_size = 14
        closest = None
        closest_type = None
        close_hover_display = True  # assume the hover display will be closed
        if (
            not (self.lclick or self.rclick or self.mclick) and
            not self.is_gesturing
        ):
            # get closest trace
            closest, closest_type = self.section_layer.getTrace(self.mouse_x, self.mouse_y)

            # get zarr label
            if self.zarr_layer:
                label_id = self.zarr_layer.getID(self.mouse_x, self.mouse_y)
            else:
                label_id = None

            if (
                self.mouse_mode == FieldWidget.POINTER or
                self.mouse_mode == FieldWidget.HOST and not self.hosted_trace
            ):
                # prioritize showing label name
                if label_id is not None:
                    pos = self.mouse_x, self.mouse_y
                    c = colorize(label_id)
                    drawOutlinedText(
                        field_painter,
                        *pos,
                        str(label_id),
                        c,
                        None,
                        ct_size
                    )
                # if no label found, check for closest traces
                else:
                    # check for ztrace segments
                    if not closest:
                        closest = self.section_layer.getZsegment(self.mouse_x, self.mouse_y)
                        closest_type = "ztrace_seg"
                    
                    # draw name of closest trace
                    if closest:
                        if closest_type == "trace":
                            name = closest.name
                            if closest.negative:
                                name += " (negative)"
                        elif closest_type == "ztrace_seg":
                            name = f"{closest.name} (ztrace)"
                        # ztrace tuple returned
                        elif closest_type == "ztrace_pt":
                            closest = closest[0]
                            name = f"{closest.name} (ztrace)"
                        # flag returned
                        elif closest_type == "flag":
                            name = closest.name
                        
                        if self.series.getOption("display_closest"):
                            # set up the corner display for the attributes
                            if closest_type in ("trace", "flag"):
                                if closest != self.displayed_item:
                                    self.closeHoverDisplay()
                                    self.displayed_item = closest
                                    self.hover_display_timer.start(1000)
                                close_hover_display = False

                            # display the name of the item by the mouse
                            mouse_x, mouse_y = self.mouse_x, self.mouse_y
                            if self.series.getOption("left_handed"): mouse_x += 10
                            c = closest.color
                            drawOutlinedText(
                                field_painter,
                                mouse_x, mouse_y,
                                name,
                                c,
                                None,
                                ct_size,
                                not self.series.getOption("left_handed")
                            )
            elif self.mouse_mode == FieldWidget.HOST and self.hosted_trace:
                # set up text position
                mouse_x, mouse_y = self.mouse_x, self.mouse_y
                if self.series.getOption("left_handed"): mouse_x += 10
                # display the proposed host relationship by the mouse
                t = [
                    self.hosted_trace.name,
                    " hosted by ",
                    closest.name if closest_type == "trace" else "..."
                ]
                t_copy = t.copy()
                for i, text in enumerate(t_copy):
                    for j in range(len(t_copy)):
                        if j < i:
                            t[i] = " "*len(t_copy[j]) + t[i]
                        elif j > i:
                            t[i] += " "*len(t_copy[j])
                c = [
                    self.hosted_trace.color,
                    (255, 255, 255),
                    closest.color if closest_type == "trace" else (255, 255, 255)
                ]
                for text, color in zip(t, c):
                    drawOutlinedText(
                        field_painter,
                        mouse_x, mouse_y,
                        text,
                        color,
                        None,
                        ct_size,
                        not self.series.getOption("left_handed")
                    )
            
            # get the names of the selected traces
            names = {}
            counter = 0
            height = self.height()
            for trace in self.section.selected_traces:
                # check for max number
                if counter * (st_size + 10) + 20 > height / 3:
                    names["..."] = 1
                    break
                if trace.name in names:
                    names[trace.name] += 1
                else:
                    names[trace.name] = 1
                    counter += 1
            self.selected_trace_names = names
            
            names = {}
            counter = 0
            for ztrace, i in self.section.selected_ztraces:
                # check for max number
                if counter * (st_size + 10) + 20 > height / 3:
                    names["..."] = 1
                    break
                if ztrace.name in names:
                    names[ztrace.name] += 1
                else:
                    names[ztrace.name] = 1
                    counter += 1
            self.selected_ztrace_names = names

        # draw the names of the blended sections
        if self.blend_sections and self.b_section:
            y += 20
            drawOutlinedText(
                field_painter,
                x, y,
                f"Blended sections: {self.b_section.n} and {self.section.n}",
                (255, 255, 255),
                (0, 0, 0),
                st_size,
                right_justified
            )
            y += st_size
        
        # draw the number of selected flags
        if self.section.selected_flags:
            y += 20
            l = len(self.section.selected_flags)
            drawOutlinedText(
                field_painter,
                x, y,
                f"{l} flag{'s' if l > 1 else ''} selected",
                (255, 255, 255),
                (0, 0, 0),
                st_size,
                right_justified
            )
            y += st_size
        
        # draw the names of the selected traces
        if self.selected_trace_names:
            y += 20
            drawOutlinedText(
                field_painter,
                x, y,
                "Selected Traces:",
                (255, 255, 255),
                (0, 0, 0),
                st_size,
                right_justified
            )
            for name, n in self.selected_trace_names.items():
                y += st_size + 10
                if n == 1:
                    text = name
                else:
                    text = f"{name} * {n}"
                drawOutlinedText(
                    field_painter,
                    x, y,
                    text,
                    (255, 255, 255),
                    (0, 0, 0),
                    st_size,
                    right_justified
                )
            y += st_size
        
        # draw the names of the selected ztraces
        if self.selected_ztrace_names:
            y += 20
            drawOutlinedText(
                field_painter,
                x, y,
                "Selected Ztraces:",
                (255, 255, 255),
                (0, 0, 0),
                st_size,
                right_justified
            )
            for name, n in self.selected_ztrace_names.items():
                y += st_size + 10
                if n == 1:
                    text = name
                else:
                    text = f"{name} * {n}"
                drawOutlinedText(
                    field_painter,
                    x, y,
                    text,
                    (255, 255, 255),
                    (0, 0, 0),
                    st_size,
                    right_justified
                )
            y += st_size
        
        # close the flag display if needed
        if close_hover_display:
            self.closeHoverDisplay()

        # update the status bar
        if not self.is_panzooming:
            if closest_type == "flag":
                self.updateStatusBar()
            else:
                self.updateStatusBar(closest)

    def paintEvent(self, event):
        """Called when self.update() and various other functions are run.
        
        Overwritten from QWidget.
        Paints self.field_pixmap onto self (the widget).
        """
        field_painter = QPainter(self)

        # draw the field
        field_painter.drawPixmap(0, 0, self.field_pixmap)
        self.paintBorder(field_painter)
        self.paintWorkingTrace(field_painter)
        self.paintText(field_painter)

        field_painter.end()
    
    def resizeEvent(self, event):
        """Scale field window if main window size changes.
        
        Overwritten from QWidget Class.
        """
        # resize the mouse palette
        self.mainwindow.mouse_palette.resize()

        # resize the zarr palette
        if self.mainwindow.zarr_palette:
            self.mainwindow.zarr_palette.placeWidgets()
        
        # ensure field is below palettes
        self.lower()

        w = event.size().width()
        h = event.size().height()
        self.pixmap_dim = (w, h)
        self.generateView()
    
    def updateStatusBar(self, trace : Trace = None):
        """Update status bar with useful information.
        
            Params:
                trace (Trace): optional trace to add to status bar
        """
        self.status_list = []

        # display current section
        section = "Section: " + str(self.series.current_section)
        self.status_list.append(section)

        # display the alignment setting
        alignment = "Alignment: " + self.series.alignment
        self.status_list.append(alignment)

        # display the brightness/contrast setting
        bc_profile = "B/C Profile: " + self.series.bc_profile
        self.status_list.append(bc_profile)

        # display mouse position in the field
        x, y = pixmapPointToField(
            self.mouse_x, 
            self.mouse_y, 
            self.pixmap_dim, 
            self.series.window, 
            self.section.mag
        )
        position = "x = " + str("{:.4f}".format(x)) + ", "
        position += "y = " + str("{:.4f}".format(y))
        self.status_list.append(position)
        
        # display the distance between the current position and the last point if line tracing
        if self.is_line_tracing:
            last_x, last_y = self.current_trace[-1]
            d = distance(last_x, last_y, self.mouse_x, self.mouse_y)
            d = d / self.scaling * self.section.mag
            dist = f"Line distance: {round(d, 5)}"
            self.status_list.append(dist)
        elif trace is not None:
            if type(trace) is Trace:
                self.status_list.append(f"Closest trace: {trace.name}")
            elif type(trace) is Ztrace:
                self.status_list.append(f"Closest trace: {trace.name} (ztrace)")
         
        s = "  |  ".join(self.status_list)
        self.mainwindow.statusbar.showMessage(s)
    
    def traceDialog(self):
        """Opens dialog to edit selected traces."""
        # do not run if both types of traces are selected or none are selected
        if not(bool(self.section.selected_traces) ^ bool(self.section.selected_ztraces)):
            return
        # run the ztrace dialog if only ztraces selected
        elif self.section.selected_ztraces:
            self.ztraceDialog()
            return
        
        t, confirmed = TraceDialog(
            self,
            self.section.selected_traces,
        ).exec()
        if not confirmed:
            return
        
        name, color, tags, mode = (
            t.name, t.color, t.tags, t.fill_mode
        )
        self.section.editTraceAttributes(
            traces=self.section.selected_traces.copy(),
            name=name,
            color=color,
            tags=tags,
            mode=mode
        )

        self.generateView(generate_image=False)
        self.saveState() 

    def ztraceDialog(self):
        """Opens a dialog to edit selected traces."""
        if not self.section.selected_ztraces:
            return
        
        # check only one ztrace selected
        first_ztrace, i = self.section.selected_ztraces[0]
        for ztrace, i in self.section.selected_ztraces:
            if ztrace != first_ztrace:
                notify("Please modify only one ztrace at a time.")
                return
        
        name = first_ztrace.name
        color = first_ztrace.color
        structure = [
            ["Name:", ("text", name)],
            ["Color:", ("color", color)]
        ]
        response, confirmed = QuickDialog.get(self, structure, "Set Attributes")
        if not confirmed:
            return
        
        # save the series state
        self.series_states.addState()
        
        new_name, new_color = response
        self.series.editZtraceAttributes(
            ztrace.name,
            new_name,
            new_color
        )

        self.updateData()

        self.generateView(generate_image=False)

    def setMouseMode(self, mode : int):
        """Set the mode of the mouse.
        
            Params:
                mode (int): number corresponding to mouse mode
        """
        self.endPendingEvents()  # end any mouse-related pending events
        self.mouse_mode = mode

        # set the cursor icon
        if mode in (FieldWidget.POINTER, FieldWidget.HOST):
            cursor = QCursor(Qt.ArrowCursor)
        elif mode == FieldWidget.PANZOOM:
            cursor = QCursor(Qt.SizeAllCursor)
        elif mode == FieldWidget.KNIFE:
            cursor = QCursor(
                QPixmap(os.path.join(loc.img_dir, "knife.cur")),
                hotX=5, hotY=5
            )
        elif (mode == FieldWidget.OPENTRACE or
              mode == FieldWidget.CLOSEDTRACE):
            cursor = self.pencil_l if self.series.getOption("left_handed") else self.pencil_r
        elif (mode == FieldWidget.STAMP or
              mode == FieldWidget.GRID):
            cursor = QCursor(Qt.CrossCursor)
        elif mode == FieldWidget.SCISSORS:
            cursor = QCursor(Qt.CrossCursor)
        elif mode == FieldWidget.FLAG:
            cursor = QCursor(Qt.WhatsThisCursor)
        self.setCursor(cursor)
    
    def setTracingTrace(self, trace : Trace):
        """Set the trace used by the pencil/line tracing/stamp.
        
            Params:
                trace (Trace): the new trace to use as refernce for further tracing
        """
        self.endPendingEvents()
        t = trace.copy()
        for c in "{}<>":  # increment characters
            t.name = t.name.replace(c, "")
        self.tracing_trace = t
    
    def usingLocked(self):
        """Returns true if the current tracing trace is locked."""
        return self.series.getAttr(self.tracing_trace.name, "locked")
    
    def notifyLocked(self, names):
        """Notify to the user that a trace is locked."""
        if type(names) is str:
            names = [names]
        else:
            names = set(names)

        unlocked = notifyLocked(names, self.series, self.series_states)
        
        if unlocked:
            self.table_manager.updateObjects(names)

        return unlocked

    def event(self, event):
        """Overwritten from QWidget.event.
        
        Added to catch gestures and zorder events.
        """
        if event.type() == QEvent.Gesture:
            self.gestureEvent(event)
        elif event.type() == QEvent.ZOrderChange:
            r = super().event(event)
            self.lower()
            return r
        
        return super().event(event)

    def gestureEvent(self, event : QGestureEvent):
        """Called when gestures are detected."""
        g = event.gesture(Qt.PinchGesture)

        if g.state() == Qt.GestureState.GestureStarted:
            self.is_gesturing = True
            p = g.centerPoint()
            if os.name == "nt":
                p = self.mapFromGlobal(p)
            self.clicked_x, self.clicked_y = p.x(), p.y()
            self.panzoomPress(self.clicked_x, self.clicked_y)

        elif g.state() == Qt.GestureState.GestureUpdated:
            p = g.centerPoint()
            if os.name == "nt":
                p = self.mapFromGlobal(p)
            x, y = p.x(), p.y()
            self.panzoomMove(x, y, g.totalScaleFactor())

        elif g.state() == Qt.GestureState.GestureFinished:
            self.is_gesturing = False
            p = g.centerPoint()
            if os.name == "nt":
                p = self.mapFromGlobal(p)
            x, y = p.x(), p.y()
            self.panzoomRelease(x, y, g.totalScaleFactor())
        
    def mousePressEvent(self, event):
        """Called when mouse is clicked.
        
        Overwritten from QWidget class.
        """
        # check what was clicked
        self.lclick = Qt.LeftButton in event.buttons()
        self.rclick = Qt.RightButton in event.buttons()
        self.mclick = Qt.MiddleButton in event.buttons()

        # ignore middle clicks combined with other clicks
        if self.mclick and (self.lclick or self.rclick):
            if self.is_panzooming:
                self.lclick = False
                self.rclick = False
            else:
                self.mclick = False
            return
        # favor right click if both left and right are clicked
        if self.lclick and self.rclick:
            if not self.is_line_tracing:
                self.current_trace = []
            self.lclick = False

        self.setFocus()
        self.mouse_x = event.x()
        self.mouse_y = event.y()
        if not self.is_gesturing:
            self.clicked_x = self.mouse_x
            self.clicked_y = self.mouse_y
        self.click_time = time.time()
        self.single_click = True

        # ignore ALL finger touch for windows
        if os.name == "nt":
            if event.pointerType() == QPointingDevice.PointerType.Finger:
                return

        # if any finger touch
        if self.is_gesturing:
            return
        
        # if any eraser touch
        if event.pointerType() == QPointingDevice.PointerType.Eraser:
            self.erasing = True
            return

        # pan if middle button clicked
        if self.mclick:
            self.mousePanzoomPress(event)
            return

        # pull up right-click menu if requirements met
        context_menu = (
            self.rclick and
            not (self.mouse_mode == FieldWidget.PANZOOM) and
            not self.is_line_tracing and
            not self.hosted_trace
        )
        if context_menu:
            clicked_label = None
            if self.zarr_layer:
                clicked_label = self.zarr_layer.getID(event.x(), event.y())
            self.clicked_trace, clicked_type = self.section_layer.getTrace(event.x(), event.y())
            self.mainwindow.checkActions(context_menu=True, clicked_trace=self.clicked_trace, clicked_label=clicked_label)
            self.lclick, self.rclick, self.mclick = False, False, False
            if clicked_label:
                self.mainwindow.label_menu.exec(event.globalPos())
            elif clicked_type == "flag":
                self.trigger_edit_flag = True
            else:
                self.mainwindow.field_menu.exec(event.globalPos())
            self.mainwindow.checkActions()
            return

        if self.mouse_mode == FieldWidget.POINTER:
            self.pointerPress(event)
        elif self.mouse_mode == FieldWidget.PANZOOM:
            self.mousePanzoomPress(event) 
        elif self.mouse_mode == FieldWidget.KNIFE:
            self.knifePress(event)
        elif self.mouse_mode == FieldWidget.SCISSORS:
            self.scissorsPress(event)
        
        elif self.usingLocked():
            self.notifyLocked(self.tracing_trace.name)

        elif (
            self.mouse_mode == FieldWidget.CLOSEDTRACE or
            self.mouse_mode == FieldWidget.OPENTRACE
        ):
            self.tracePress(event)
        elif self.mouse_mode == FieldWidget.STAMP:
            self.stampPress(event)
        elif self.mouse_mode == FieldWidget.GRID:
            self.gridPress(event)
        elif self.mouse_mode == FieldWidget.HOST:
            self.hostPress(event)

    def mouseMoveEvent(self, event):
        """Called when mouse is moved.
        
        Overwritten from QWidget class.
        """
        # keep track of position
        self.mouse_x = event.x()
        self.mouse_y = event.y()
        self.single_click = False

        # ignore ALL finger touch for windows
        if os.name == "nt":
            if event.pointerType() == QPointingDevice.PointerType.Finger:
                return

        # if any finger touch
        if self.is_gesturing:
            return
        
        # if any eraser touch
        elif event.pointerType() == QPointingDevice.PointerType.Eraser:
            self.eraserMove(event)
        
        # check if user is zooming with the mouse wheel
        if self.mainwindow.is_zooming:
            self.panzoomRelease(zoom_factor=self.mainwindow.zoom_factor)
            self.mainwindow.is_zooming = False
        
        # update click status
        if not event.buttons():
            self.lclick = False
            self.rclick = False
            self.mclick = False
            self.erasing = False
        
        # panzoom if middle button clicked
        if self.mclick:
            self.mousePanzoomMove(event)
            return
        
        # update the screen if not pressing buttons
        if not event.buttons():
            self.update()
        
        # mouse functions
        if self.mouse_mode == FieldWidget.POINTER:
            self.pointerMove(event)
        elif self.mouse_mode == FieldWidget.PANZOOM:
            self.mousePanzoomMove(event)
        elif self.mouse_mode == FieldWidget.KNIFE:
            self.knifeMove(event)

        elif self.usingLocked():
            pass
        
        elif (
            self.mouse_mode == FieldWidget.CLOSEDTRACE or
            self.mouse_mode == FieldWidget.OPENTRACE
        ):
            self.traceMove(event)
        elif self.mouse_mode == FieldWidget.STAMP:
            self.stampMove(event)
        elif self.mouse_mode == FieldWidget.HOST:
            self.hostMove(event)

    def mouseReleaseEvent(self, event):
        """Called when mouse button is released.
        
        Overwritten from QWidget Class.
        """
        # wait until all buttons are released
        if event.buttons(): return
        
        # ignore ALL finger touch for windows
        if os.name == "nt":
            if event.pointerType() == QPointingDevice.PointerType.Finger:
                return
        
        # if any finger touch
        if self.is_gesturing:
            return
        
        # if any eraser touch
        elif event.pointerType() == QPointingDevice.PointerType.Eraser:
            self.erasing = False
            return
        
        # panzoom if middle button
        if self.mclick:
            self.mousePanzoomRelease(event)
            self.mclick = False
            return
        
        # modify flags as requested
        if self.trigger_edit_flag:
            self.edit_flag_event.trigger()
            self.trigger_edit_flag = False
            return

        if self.mouse_mode == FieldWidget.POINTER:
            self.pointerRelease(event)
        elif self.mouse_mode == FieldWidget.PANZOOM:
            self.mousePanzoomRelease(event)
        elif self.mouse_mode == FieldWidget.KNIFE:
            self.knifeRelease(event)
        elif self.mouse_mode == FieldWidget.FLAG:
            self.flagRelease(event)

        elif self.usingLocked():
            pass

        elif (
            self.mouse_mode == FieldWidget.CLOSEDTRACE or
            self.mouse_mode == FieldWidget.OPENTRACE
        ):
            self.traceRelease(event)
        elif self.mouse_mode == FieldWidget.STAMP:
            self.stampRelease(event)
        elif self.mouse_mode == FieldWidget.GRID:
            self.gridRelease(event)
        elif self.mouse_mode == FieldWidget.HOST:
            self.hostRelease(event)
        
        self.lclick = False
        self.rclick = False
        self.mclick = False
        self.single_click = False
    
    def checkMouseBoundary(self):
        """Move the window if the mouse is close to the boundary."""
        x, y = self.mouse_x, self.mouse_y

        # check if mouse is is wthin 2% of screen boundary
        xmin, xmax = round(self.width() * 0.02), round(self.width() * .98)
        ymin, ymax = round(self.height() * 0.02), round(self.height() * .98)

        shift = [0, 0]

        if x <= xmin:
            shift[0] -= xmin
        elif x >= xmax:
            shift[0] += xmin
        if y <= ymin:
            shift[1] -= ymin
        elif y >= ymax:
            shift[1] += ymin
        
        # move the window and current trace
        if shift[0] or shift[1]:
            s = self.section.mag / self.section_layer.scaling
            w = self.series.window
            w[0] += shift[0] * s
            w[1] -= shift[1] * s
            self.current_trace = [(x-shift[0], y-shift[1]) for x, y in self.current_trace]
            self.generateView()
    
    def activateMouseBoundaryTimer(self):
        """Activate the timer to check the mouse boundary."""
        if self.mouse_boundary_timer is None:
            self.mouse_boundary_timer = QTimer(self)
            self.mouse_boundary_timer.timeout.connect(self.checkMouseBoundary)
            self.mouse_boundary_timer.start(100)
    
    def deactivateMouseBoundaryTimer(self):
        """Deactivate the timer to check the mouse near boundary."""
        if self.mouse_boundary_timer:
            self.mouse_boundary_timer.stop()
            self.mouse_boundary_timer = None
    
    def isSingleClicking(self):
        """Check if user is single-clicking.
        
            Returns:
                (bool) True if user is single-clicking
        """
        if self.single_click or (time.time() - self.click_time <= self.max_click_time):
            return True
        else:
            return False
    
    def autoMerge(self):
        """Automatically merge the selected traces of the same name."""
        # merge with existing selected traces of the same name
        if not self.series.getOption("auto_merge"):
            return
        traces_to_merge = []
        for t in self.section.selected_traces:
            if t.name == self.tracing_trace.name and t.closed:
                traces_to_merge.append(t)
        if len(traces_to_merge) > 1:
            self.mergeSelectedTraces(traces_to_merge)

    def pointerPress(self, event):
        """Called when mouse is pressed in pointer mode.

        Selects/deselects the nearest trace
        """
        # select, deselect or move
        if self.lclick:
            self.is_moving_trace = False
            self.is_selecting_traces = False
            self.clicked_x, self.clicked_y = event.x(), event.y()
            self.selected_trace, self.selected_type = self.section_layer.getTrace(
                self.clicked_x,
                self.clicked_y
            )
    
    def pointerMove(self, event):
        """Called when mouse is moved in pointer mode."""
        # ignore if not clicking
        if not self.lclick:
            return
        
        # keep track of possible lasso if insufficient time has passed
        if self.isSingleClicking():
            self.current_trace.append((event.x(), event.y()))
            return
        
        # left button is down and user clicked on a trace
        if (
            self.is_moving_trace or 
            self.selected_trace in self.section.selected_traces or
            self.selected_trace in self.section.selected_ztraces or
            self.selected_trace in self.section.selected_flags
        ): 
            if not self.is_moving_trace:  # user has just decided to move the trace
                self.is_moving_trace = True
                # clear lasso trace
                self.current_trace = []
                # get pixel points
                self.moving_traces = []
                self.moving_points = []
                self.moving_flags = []
                for trace in self.section.selected_traces:
                    # hide the trace
                    self.section.temp_hide.append(trace)
                    # get points and other data
                    pix_points = self.section_layer.traceToPix(trace)
                    color = trace.color
                    closed = trace.closed
                    self.moving_traces.append((pix_points, color, closed))
                for ztrace, i in self.section.selected_ztraces:
                    # hide the ztrace
                    self.section.temp_hide.append(ztrace)
                    # get points and other data
                    point = ztrace.points[i][:2]
                    pix_point = self.section_layer.pointToPix(point)
                    color = ztrace.color
                    self.moving_points.append((pix_point, color))
                for flag in self.section.selected_flags:
                    # hide the flag
                    self.section.temp_hide.append(flag)
                    # get point and other data
                    pix_point = self.section_layer.pointToPix((flag.x, flag.y))
                    color = flag.color
                    self.moving_flags.append((pix_point, color))

                self.generateView(update=False)
            
            self.update()

        # no trace was clicked on OR user clicked on unselected trace
        # draw lasso for selecting traces
        else:
            if not self.is_selecting_traces:  # user just decided to group select traces
                self.is_selecting_traces = True
                self.activateMouseBoundaryTimer()
            if self.series.getOption("pointer")[0] == "rect":
                x2, y2 = event.x(), event.y()
                if self.current_trace:
                    x1, y1 = self.current_trace[0]
                else:
                    x1, y1 = x2, y2

                self.current_trace = [
                    (x1, y1),
                    (x2, y1),
                    (x2, y2),
                    (x1, y2)
                ]
                
            else:
                x = event.x()
                y = event.y()
                self.current_trace.append((x, y))

            # draw to screen
            self.update()
    
    def pointerRelease(self, event):
        """Called when mouse is released in pointer mode."""

        # user single-clicked
        if self.lclick and self.isSingleClicking():
            # if user selected a label id
            if self.zarr_layer and self.zarr_layer.selectID(
                self.mouse_x, self.mouse_y
            ):
                self.generateView(update=False)
            # if user selected a trace
            elif self.selected_trace:
                # if user selected a normal trace
                if self.selected_type == "trace":
                    if not self.series.getAttr(self.selected_trace.name, "locked"):
                        self.selectTrace(self.selected_trace)
                # if user selected a ztrace
                elif self.selected_type == "ztrace_pt":
                    self.selectZtrace(self.selected_trace)
                # if user selected a flag
                elif self.selected_type == "flag":
                    self.selectFlag(self.selected_trace)
        
        # user moved traces
        elif self.lclick and self.is_moving_trace:
            # unhide the traces
            self.section.temp_hide = []
            # save the traces in their final position
            self.is_moving_trace = False
            dx = (event.x() - self.clicked_x) * self.series.screen_mag
            dy = (event.y() - self.clicked_y) * self.series.screen_mag * -1
            self.section.translateTraces(dx, dy)
            self.generateView(update=False)
            self.saveState()
        
        # user selected an area (lasso) of traces
        elif self.lclick and self.is_selecting_traces:
            self.is_selecting_traces = False
            self.deactivateMouseBoundaryTimer()
            selected_traces = self.section_layer.getTraces(self.current_trace)
            if selected_traces:
                self.selectTraces(selected_traces, [])
        
        # clear any traces made
        self.current_trace = []
        self.update()
    
    def eraserMove(self, event):
        """Called when the user is erasing."""
        if not self.erasing:
            return
        erased = self.section_layer.eraseArea(event.x(), event.y())
        if erased:
            self.generateView(generate_image=False)
            self.saveState()
    
    def panzoomPress(self, x, y):
        """Initiates panning and zooming mode.
        
            Params:
                x: the x position of the start
                y: the y position of the start
        """
        self.clicked_x = x
        self.clicked_y = y
        self.endPendingEvents()
        self.field_pixmap_copy = self.field_pixmap.copy()
        
    def mousePanzoomPress(self, event):
        """Called when mouse is clicked in panzoom mode.
        
        Saves the position of the mouse.
        """
        if self.mainwindow.is_zooming:
            return
        self.panzoomPress(event.x(), event.y())
    
    def panzoomMove(self, new_x=None, new_y=None, zoom_factor=1):
        """Generates image output for panning and zooming.
        
            Params:
                new_x: the x from panning
                new_y: the y from panning
                zoom_factor: the scale from zooming
        """
        self.is_panzooming = True
        field = self.field_pixmap_copy
        # calculate pan
        if new_x is not None and new_y is not None:
            move_x = new_x - self.clicked_x
            move_y = new_y - self.clicked_y
        else:
            move_x, move_y = 0, 0
        # calculate new geometry of window based on zoom factor
        if zoom_factor is not None:
            xcoef = (self.clicked_x / self.pixmap_dim[0]) * 2
            ycoef = (self.clicked_y / self.pixmap_dim[1]) * 2
            w = self.pixmap_dim[0] * zoom_factor
            h = self.pixmap_dim[1] * zoom_factor
            x = (self.pixmap_dim[0] - w) / 2 * xcoef
            y = (self.pixmap_dim[1] - h) / 2 * ycoef
        else:
            x, y = 0, 0
            w, h = self.pixmap_dim
        # adjust field
        new_field = QPixmap(*self.pixmap_dim)
        new_field.fill(QColor(0, 0, 0))
        painter = QPainter(new_field)
        painter.drawPixmap(move_x + x, move_y + y, w, h, field)
        self.field_pixmap = new_field
        self.update()

    def mousePanzoomMove(self, event):
        """Called when mouse is moved in panzoom mode."""
        if self.mainwindow.is_zooming:
            return
        # if left mouse button is pressed, do panning
        if self.lclick or self.mclick:
            self.panzoomMove(new_x=event.x(), new_y=event.y())
        # if right mouse button is pressed, do zooming
        elif self.rclick:
            # up and down mouse movement only
            move_y = event.y() - self.clicked_y
            zoom_factor = 1.005 ** (move_y) # 1.005 is arbitrary
            self.panzoomMove(zoom_factor=zoom_factor)
        
    def panzoomRelease(self, new_x=None, new_y=None, zoom_factor=None):
        """Generates image output for panning and zooming.
        
            Params:
                new_x: the x from panning
                new_y: the y from panning
                zoom_factor: the scale from zooming
        """
        section = self.section

        # zoom the series window
        if zoom_factor is not None:
            x_scaling = self.pixmap_dim[0] / (self.series.window[2] / section.mag)
            y_scaling = self.pixmap_dim[1] / (self.series.window[3] / section.mag)
            # calculate pixel equivalents for window view
            xcoef = (self.clicked_x / self.pixmap_dim[0]) * 2
            ycoef = (self.clicked_y / self.pixmap_dim[1]) * 2
            w = self.pixmap_dim[0] * zoom_factor
            h = self.pixmap_dim[1] * zoom_factor
            x = (self.pixmap_dim[0] - w) / 2 * xcoef
            y = (self.pixmap_dim[1] - h) / 2 * ycoef
            # convert pixel equivalents to field coordinates
            window_x = - x  / x_scaling / zoom_factor * section.mag
            window_y = - (self.pixmap_dim[1] - y - self.pixmap_dim[1] * zoom_factor)  / y_scaling / zoom_factor * section.mag
            self.series.window[0] += window_x
            self.series.window[1] += window_y
            self.series.window[2] /= zoom_factor
            # set limit on how far user can zoom in
            if self.series.window[2] < section.mag:
                self.series.window[2] = section.mag
            self.series.window[3] /= zoom_factor
            if self.series.window[3] < section.mag:
                self.series.window[3] = section.mag
            
        # move the series window
        if new_x is not None and new_y is not None:
            x_scaling = self.pixmap_dim[0] / (self.series.window[2] / section.mag)
            y_scaling = self.pixmap_dim[1] / (self.series.window[3] / section.mag)
            move_x = -(new_x - self.clicked_x) / x_scaling * section.mag
            move_y = (new_y - self.clicked_y) / y_scaling * section.mag
            self.series.window[0] += move_x
            self.series.window[1] += move_y
        
        self.is_panzooming = False        
        self.generateView()

    def mousePanzoomRelease(self, event):
        """Called when mouse is released in panzoom mode."""
        if self.mainwindow.is_zooming:
            return
        # set new window for panning
        if self.lclick or self.mclick:
            self.panzoomRelease(new_x=event.x(), new_y=event.y())
        # set new window for zooming
        elif self.rclick:
            move_y = event.y() - self.clicked_y
            zoom_factor = 1.005 ** (move_y)
            self.panzoomRelease(zoom_factor=zoom_factor)
    
    def tracePress(self, event):
        """Called when mouse is pressed in trace mode."""
        if self.is_line_tracing:
            self.linePress(event)
        else:
            self.last_x = event.x()
            self.last_y = event.y()
            self.current_trace = [(self.last_x, self.last_y)]

        # start line tracing of only trace mode set
        trace_mode = self.series.getOption("trace_mode")
        if trace_mode == "poly":
            self.is_line_tracing = True
            self.activateMouseBoundaryTimer()
            self.mainwindow.checkActions()

    def traceMove(self, event):
        """Called when mouse is moved in trace mode."""
        if self.is_line_tracing:
            self.update()
        else:
            self.pencilMove(event)
    
    def traceRelease(self, event):
        """Called when mouse is released in trace mode."""
        trace_mode = self.series.getOption("trace_mode")
        # user is already line tracing
        if self.is_line_tracing:
            self.lineRelease(event)
        # user decided to line trace (in combo trace_mode)
        elif trace_mode == "combo" and self.isSingleClicking():
            self.current_trace = [self.current_trace[0]]
            self.is_line_tracing = True
            self.activateMouseBoundaryTimer()
            self.mainwindow.checkActions()
        # user is not line tracing
        elif not self.is_line_tracing:
            self.pencilRelease(event)

    def pencilMove(self, event):
        """Called when mouse is moved in pencil mode with the left mouse button pressed.

        Draws continued trace on the screen.
        """
        if self.lclick:
            # draw trace on pixmap
            x = event.x()
            y = event.y()
            if self.closed_trace_shape == "trace" or self.mouse_mode == FieldWidget.OPENTRACE:
                self.current_trace.append((x, y))
            elif self.closed_trace_shape == "rect":
                x1, y1 = self.current_trace[0]
                self.current_trace = [
                    (x1, y1),
                    (x, y1),
                    (x, y),
                    (x1, y)
                ]
            elif self.closed_trace_shape == "circle":
                self.current_trace = ellipseFromPair(self.clicked_x, self.clicked_y, x, y)
            self.last_x = x
            self.last_y = y
            self.update()

    def pencilRelease(self, event):
        """Called when mouse is released in pencil mode.

        Completes and adds trace.
        """
        closed = (self.mouse_mode == FieldWidget.CLOSEDTRACE)
        if self.lclick:
            if len(self.current_trace) < 2:
                return
            self.newTrace(
                self.current_trace,
                self.tracing_trace,
                closed=closed
            )
            if closed and len(self.current_trace) > 2:
                self.autoMerge()
            self.current_trace = []
    
    def linePress(self, event):
        """Called when mouse is pressed in a line mode.
        
        Begins create a line trace.
        """
        x, y = event.x(), event.y()
        if self.lclick:  # begin/add to trace if left mouse button
            if self.is_line_tracing:  # continue trace
                self.current_trace.append((x, y))
                self.update()
    
    def lineRelease(self, event=None, override=False, log_event=True):
        """Called when mouse is released in line mode."""
        if override or self.rclick and self.is_line_tracing:  # complete existing trace if right mouse button
            closed = (self.mouse_mode == FieldWidget.CLOSEDTRACE)
            self.is_line_tracing = False
            self.deactivateMouseBoundaryTimer()
            if len(self.current_trace) > 1:
                current_trace_copy = self.current_trace.copy()
                self.newTrace(
                    current_trace_copy,
                    self.tracing_trace,
                    closed=closed,
                    log_event=(log_event and (not self.is_scissoring))
                )
                if log_event and self.is_scissoring:
                    self.series.addLog(self.tracing_trace.name, self.section.n, "Modify trace(s)")
                if closed and len(self.current_trace) > 2:
                    self.autoMerge()
                self.current_trace = []
            else:
                self.current_trace = []
                self.update()
            if self.is_scissoring:
                self.is_scissoring = False
                self.setMouseMode(FieldWidget.SCISSORS)
                self.setTracingTrace(
                    self.series.palette_traces[self.series.palette_index[0]][self.series.palette_index[1]]
                )
    
    def backspace(self):
        """Called when backspace OR Del is pressed: either delete traces or undo line trace."""
        if self.is_line_tracing and len(self.current_trace) > 1:
            self.current_trace.pop()
            self.update()
        elif len(self.current_trace) == 1:
            self.is_line_tracing = False
            self.deactivateMouseBoundaryTimer()
            self.update()
        else:
            self.deleteTraces()
    
    def stampPress(self, event):
        """Called when mouse is pressed in stamp mode.
        
        Creates a stamp centered on the mouse location.
        """
        # get mouse coords and convert to field coords
        if self.lclick:
            self.is_drawing_rad = False
            self.clicked_x, self.clicked_y = event.x(), event.y()
    
    def stampMove(self, event):
        """Called when mouse is moved in stamp mode."""
        if not self.lclick:
            return
        
        self.current_trace = [
            (self.clicked_x, self.clicked_y),
            (event.x(), event.y())
        ]

        if not self.isSingleClicking():
            self.is_drawing_rad = True

        self.update()
    
    def stampRelease(self, event):
        """Called when mouse is released in stamp mode."""
        # user single-clicked
        if self.lclick and self.isSingleClicking():
            self.placeStamp(event.x(), event.y(), self.tracing_trace)
        # user defined a radius
        elif self.lclick and self.is_drawing_rad:
            x, y = event.x(), event.y()
            r = distance(
                *pixmapPointToField(
                    self.clicked_x,
                    self.clicked_y,
                    self.pixmap_dim,
                    self.series.window,
                    self.section.mag
                ),
                *pixmapPointToField(
                    x,
                    y,
                    self.pixmap_dim,
                    self.series.window,
                    self.section.mag
                ),
            ) / 2
            stamp = self.tracing_trace.copy()
            stamp.resize(r)
            center = (
                (x + self.clicked_x) / 2,
                (y + self.clicked_y) / 2
            )
            self.placeStamp(*center, stamp)
        
        self.current_trace = []
        self.is_drawing_rad = False
        self.update()
    
    def gridPress(self, event):
        """Creates a grid on the mouse location."""
        # get mouse coords and convert to field coords
        if self.lclick:
            pix_x, pix_y = event.x(), event.y()
            self.placeGrid(
                pix_x, pix_y,
                self.tracing_trace,
                *tuple(self.series.getOption("grid"))
            )
    
    def gridRelease(self, event):
        """Called when mouse is released in grid mode."""
        self.update()
    
    def scissorsPress(self, event):
        """Identifies the nearest trace and allows user to poly edit it."""
        # select, deselect or move
        if self.lclick:
            self.selected_trace, self.selected_type = self.section_layer.getTrace(
                self.clicked_x,
                self.clicked_y
            )
            if self.selected_type == "trace":
                if self.series.getAttr(self.selected_trace.name, "locked"):
                    self.notifyLocked(self.selected_trace.name)
                    return
                self.is_scissoring = True
                self.deselectAllTraces()
                self.section.deleteTraces([self.selected_trace])
                self.generateView(generate_image=False)
                self.current_trace = self.section_layer.traceToPix(self.selected_trace)

                # find the index of the closest point
                least_dist = distance(self.clicked_x, self.clicked_y, *self.current_trace[0])
                least_i = 0
                for (i, p) in enumerate(self.current_trace):
                    d = distance(self.clicked_x, self.clicked_y, *p)
                    if d < least_dist:
                        least_dist = d
                        least_i = i

                # reverse the trace if closed (to operate same as legacy version)
                if self.selected_trace.closed:
                    self.mouse_mode = FieldWidget.CLOSEDTRACE
                    self.current_trace = self.current_trace[least_i:] + self.current_trace[:least_i]
                    self.current_trace.reverse()
                else:
                    self.mouse_mode = FieldWidget.OPENTRACE
                    # calculate distance for each segment
                    seg1 = self.current_trace[:least_i+1]
                    seg2 = self.current_trace[least_i:]
                    if lineDistance(seg2, closed=False) > lineDistance(seg1, closed=False):
                        self.current_trace = seg2[::-1]
                    else:
                        self.current_trace = seg1
                self.is_line_tracing = True
                self.activateMouseBoundaryTimer()
                self.mainwindow.checkActions()
                self.tracing_trace = self.selected_trace
                self.update()

    def knifePress(self, event):
        """Called when mouse is pressed in knife mode.

        Begins creating a new trace.
        """
        self.last_x = event.x()
        self.last_y = event.y()
        self.current_trace = [(self.last_x, self.last_y)]

    def knifeMove(self, event):
        """Called when mouse is moved in pencil mode with a mouse button pressed.

        Draws continued knife trace on the screen.
        """
        if self.lclick:
            # draw knife trace on pixmap
            x = event.x()
            y = event.y()
            self.current_trace.append((x, y))
            self.update()

    def knifeRelease(self, event):
        """Called when mouse is released in pencil mode.

        Completes and adds trace.
        """
        if self.lclick:
            self.cutTrace(self.current_trace)
        self.current_trace = []
        self.update()
    
    def flagRelease(self, event):
        """Called when mouse is released in flag mode."""
        if self.lclick and self.series.getOption("show_flags") != "none":
            default_name = self.series.getOption("flag_name")
            if not default_name:
                self.section.save()  # ensure all flags are in the series data object
                flag_count = self.series.data.getFlagCount()
                default_name = f"flag_{flag_count + 1}"
            structure = [
                ["Name:", (True, "text", default_name)],
                ["Color:", ("color", self.series.getOption("flag_color")), ""],
                ["Comment (opt):"],
                [("textbox", "")]
            ]
            response, confirmed = QuickDialog.get(self, structure, "Flag")
            if not confirmed:
                return
            
            pix_x, pix_y = event.x(), event.y()
            title = response[0]
            color = response[1]
            comment = response[2]
            self.placeFlag(
                title,
                pix_x, pix_y,
                color,
                comment
            )

        self.update()
    
    def hostPress(self, event):
        """Called when mouse is pressed in host mode."""
        pass
        
    
    def hostMove(self, event):
        """Called when mouse is moved in host mode."""
        if self.hosted_trace:
            self.current_trace = self.current_trace[:1]
            self.current_trace.append((self.mouse_x, self.mouse_y))

    def hostRelease(self, event):
        # cancel operation if user right-clicked
        if self.rclick and self.hosted_trace:
            self.hosted_trace = None
            self.current_trace = []
            self.update()
            return
        
        closest, closest_type = self.section_layer.getTrace(self.mouse_x, self.mouse_y)
        if self.hosted_trace:
            if closest_type == "trace":
                host = closest.name
                hosted = self.hosted_trace.name
                if host == hosted:
                    notify("An object cannot be a host of itself.")
                elif hosted in self.series.getObjHosts(host, traverse=True):
                    notify("Objects cannot be hosts of each other.")
                else:
                    self.series_states.addState()
                    self.series.host_tree.add(
                        hosted, 
                        [host],
                    )
                    self.table_manager.updateObjects(self.series.host_tree.getObjToUpdate([hosted, host]))
            self.hosted_trace = None
            self.current_trace = []
        else:
            if closest_type == "trace":
                self.hosted_trace = closest
                self.current_trace = [(self.mouse_x, self.mouse_y)]
            else:
                self.hosted_trace = None
                self.current_trace = []
        self.update()
    
    def editFlag(self, event=None):
        """Edit a flag. (Triggered by action)"""
        flag = self.clicked_trace
        response, confirmed = FlagDialog(self, flag).exec()
        if confirmed:
            flag.name, flag.color, flag.comments, new_comment, resolved = response
            if new_comment: flag.addComment(self.series.user, new_comment)
            flag.resolve(self.series.user, resolved)
            self.generateView(generate_image=False)
            self.saveState()
    
    def createTraceFlag(self, trace : Trace = None):
        """Create a flag associated with a trace."""
        if trace is None and self.clicked_trace:
            trace = self.clicked_trace
            if not trace:
                return
        
        structure = [
            ["Name:", (True, "text", f"{trace.name}")],
            ["Color:", ("color", trace.color), ""],
            ["Comment:"],
            [("textbox", "")]
        ]
        response, confirmed = QuickDialog.get(self, structure, "Flag")
        if not confirmed:
            return
        
        x, y = trace.getCentroid()
        name = response[0]
        color = response[1]
        comment = response[2]
        f = Flag(name, x, y, self.section.n, color)
        if comment:
            f.addComment(self.series.user, comment)
        self.section.addFlag(f)

        self.saveState()
        self.generateView(generate_image=False)

    def setCuration(self, cr_status : str, traces : list = None):
        """Set the curation for the selected traces.
        
            Params:
                cr_status (str): the curation status to set for the traces
                traces (list): the list of traces to set
        """
        if not traces:
            traces = self.section.selected_traces.copy()

        if cr_status == "Needs curation":
            assign_to, confirmed = QInputDialog.getText(
                self,
                "Assign to",
                "Assign curation to username:\n(press enter to leave blank)"
            )
            if not confirmed:
                return
        else:
            assign_to = ""
        
        self.series.setCuration([t.name for t in traces], cr_status, assign_to)

        # manually mark as edited
        [self.section.modified_contours.add(t.name) for t in traces]

        self.saveState()
    
    def setLeftHanded(self, left_handed=None):
        """Set the handedness of the user
        
            Params:
                left_handed (bool): True if user is left handed
        """
        if left_handed is not None:
            self.series.setOption("left_handed", left_handed)
        else:
            self.series.setOption("left_handed", self.mainwindow.lefthanded_act.isChecked())

        # adjust handedness of the cursor
        if (self.mouse_mode == FieldWidget.OPENTRACE or
            self.mouse_mode == FieldWidget.CLOSEDTRACE):
            cursor = self.pencil_l if self.series.getOption("left_handed") else self.pencil_r
            if cursor != self.cursor(): self.setCursor(cursor)
    
    def deleteAll(self, tags=False):
        """Delete all traces in the series that match the trace name (and possibly tags).
        
            Params:
                tags (bool): True if tags should be compared
        """
        if len(self.section.selected_traces) != 1:
            notify("Please select only one trace.")
            return
        trace = self.section.selected_traces[0]

        if tags:
            self.series.deleteAllTraces(trace.name, trace.tags, self.series_states)
        else:
            self.series.deleteAllTraces(trace.name, series_states=self.series_states)
        
        self.table_manager.updateObjects([trace.name])
        self.reload()

    def endPendingEvents(self):
        """End ongoing events that are connected to the mouse."""
        if self.is_line_tracing:
            self.lineRelease(override=True)
    
    def setObjComment(self):
        """Set the object comment."""
        names = set(t.name for t in self.section.selected_traces)
        if not names:
            return
        elif len(names) == 1:
            comment = self.series.getAttr(list(names)[0], "comment")
        else:
            comment = ""
        
        new_comment, confirmed = QInputDialog.getText(
            self,
            "Object Comment",
            "Comment:",
            text=comment
        )
        if not confirmed:
            return
        
        self.series_states.addState()
        
        for name in names:
            self.series.setAttr(name, "comment", new_comment)
        
        self.table_manager.updateObjects(names)
    
    def setUserCol(self, col_name : str, opt : str):
        """Set the user column option for an object.
        
            Params:
                col_name (str): the name of the column
                opt (str): the name of the category
        """
        self.series_states.addState()

        names = set(t.name for t in self.section.selected_traces)
        for name in names:
            self.series.setUserColAttr(name, col_name, opt)
        
        self.table_manager.updateObjects(names)
        self.mainwindow.seriesModified(True)
    
    def editUserCol(self, col_name : str):
        """Edit a user-defined column.
        
            Params:
                col_name (str): the name of the user-defined column to edit
        """
        structure = [
            ["Column name:"],
            [(True, "text", col_name)],
            [" "],
            ["Options:"],
            [(True, "multitext", self.series.user_columns[col_name])]
        ]
        response, confirmed = QuickDialog.get(self, structure, "Add Column")
        if not confirmed:
            return
        
        name = response[0]
        opts = response[1]

        if name != col_name and name in self.series.user_columns:
            notify("This group already exists.")
            return
        
        self.series_states.addState()
        self.series.editUserCol(col_name, name, opts)
        self.mainwindow.seriesModified(True)
        self.mainwindow.createContextMenus()

    def addUserCol(self):
        """Add a user-defined column."""
        structure = [
            ["Column name:"],
            [(True, "text", "")],
            [" "],
            ["Options:"],
            [(True, "multitext", [])]
        ]
        response, confirmed = QuickDialog.get(self, structure, "Add Column")
        if not confirmed:
            return
    
        name = response[0]
        opts = response[1]

        if name in self.series.getOption("object_columns"):
            notify("This column already exists.")
            return
        
        self.series_states.addState()
        self.series.addUserCol(name, opts)

        self.mainwindow.seriesModified(True)
        self.mainwindow.createContextMenus()
    
    def setHosts(self):
        """Set the host of the selected object(s)."""
        names = set(t.name for t in self.section.selected_traces)
        if not names:
            return
        elif len(names) == 1:
            current_hosts = self.series.getObjHosts(tuple(names)[0])
        else:
            current_hosts = []
        
        structure = [
            ["Host Name:"],
            [("multicombo", list(self.series.data["objects"].keys()), current_hosts)]
        ]
        response, confirmed = QuickDialog.get(self, structure, "Object Host")
        if not confirmed:
            return
        host_names = set(response[0])
        
        # check to ensure that objects are not hosts of each other
        for hn in host_names:
            if hn in names:
                notify("An object cannot be a host of itself.")
                return
            if bool(set(names) & set(self.series.getObjHosts(hn, traverse=True))):  # if any intersection exists between the two
                notify("Objects cannot be hosts of each other.")
                return
        
        self.series_states.addState()
        self.series.setObjHosts(names, host_names)

        self.table_manager.updateObjects(
            self.series.host_tree.getObjToUpdate(names)
        )
    
    def snapTraces(self):
        """Snap the selected traces."""
        for trace in self.section.selected_traces:
            trace.points = snapTrace(self.series, self.section, trace)
        self.generateView(generate_image=False)
        

def formatAsParagraph(text : str, per_line=50, max_lines=20):
    """Format text as a paragraph.
    
        Params: 
            text (str): the text to format
            per_line (int): the characters per line
            max_lines (int): max number of lines in paragraph
    """
    text = text.replace("\n", "\n ")
    text_split = text.split(" ")
    num_chars = 0
    final_str = ""
    for word in text_split:
        if num_chars + len(word) > per_line:
            final_str += "\n"
            num_chars = 0
        if "\n" in word:
            num_chars = 0
        else:
            word += " "
        final_str += word
        num_chars += len(word) + 1
        
        if max_lines and final_str.count("\n") >= max_lines:
            return final_str + "..."
    return final_str


