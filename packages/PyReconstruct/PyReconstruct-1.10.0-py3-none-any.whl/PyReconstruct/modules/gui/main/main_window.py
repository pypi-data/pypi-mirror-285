import os
import sys
import re
import time
import webbrowser
from datetime import datetime
import json
import subprocess

from PySide6.QtWidgets import (
    QMainWindow, 
    QInputDialog, 
    QApplication,
    QMessageBox, 
    QMenu
)
from PySide6.QtGui import (
    QKeySequence,
    QShortcut,
    QPixmap
)
from PySide6.QtCore import Qt, QSettings

from .field_widget import FieldWidget

from PyReconstruct.modules.gui.palette import MousePalette, ZarrPalette
from PyReconstruct.modules.gui.dialog import (
    AlignmentDialog,
    GridDialog,
    CreateZarrDialog,
    TrainDialog,
    SegmentDialog,
    PredictDialog,
    QuickDialog,
    FileDialog,
    AllOptionsDialog,
    BCProfilesDialog,
    BackupDialog,
    ShortcutsDialog,
    BackupCommentDialog,
    ImportSeriesDialog,
)
from PyReconstruct.modules.gui.popup import TextWidget, CustomPlotter, AboutWidget
from PyReconstruct.modules.gui.utils import (
    populateMenuBar,
    populateMenu,
    notify,
    saveNotify,
    unsavedNotify,
    setMainWindow,
    noUndoWarning,
    checkMag,
    getUserColsMenu,
    getAlignmentsMenu,
    getOpenRecentMenu,
)
from PyReconstruct.modules.gui.table import HistoryTableWidget, CopyTableWidget, ObjectTableWidget
from PyReconstruct.modules.backend.func import (
    xmlToJSON,
    jsonToXML,
    importTransforms,
    importSwiftTransforms
)
from PyReconstruct.modules.backend.view import (
    optimizeSeriesBC
)
from PyReconstruct.modules.backend.autoseg import seriesToZarr, seriesToLabels, labelsToObjects, groupsToVolume
from PyReconstruct.modules.backend.volume import export3DObjects
from PyReconstruct.modules.datatypes import Series, Transform, Flag
from PyReconstruct.modules.constants import (
    welcome_series_dir,
    assets_dir,
    img_dir,
    kh_web,
    kh_wiki,
    kh_atlas,
    gh_repo,
    gh_issues,
    gh_submit,
    developers_mailto_str,
    repo_info,
    repo_string
)

class MainWindow(QMainWindow):

    def __init__(self, filename):
        """Constructs the skeleton for an empty main window."""
        super().__init__() # initialize QMainWindow
        self.setWindowTitle("PyReconstruct")

        # catch all exceptions and display error message
        def customExcepthook(exctype, value, traceback):
            """
            Global exception hook to display a notification window.
            """
            sys.__excepthook__(exctype, value, traceback)  # Call the default exception hook
            message = f"An error occurred:\n\n{str(value)}\n\n(See console for more info.)\n\nIf you think this is a bug or need help, please issue a bug report at:\n\nhttps://github.com/synapseweb/pyreconstruct/issues"
            QMessageBox.critical(None, "Error", message, QMessageBox.Ok)

        # Set the exception hook
        sys.excepthook = customExcepthook

        # set the window icon
        pix = QPixmap(os.path.join(img_dir, "PyReconstruct.ico"))
        self.setWindowIcon(pix)

        # set the main window to be slightly less than the size of the monitor
        screen = QApplication.primaryScreen()
        screen_rect = screen.size()
        x = 50
        y = 80
        w = screen_rect.width() - 100
        h = screen_rect.height() - 160
        self.setGeometry(x, y, w, h)

        # misc defaults
        self.series = None
        self.series_data = None
        self.field = None  # placeholder for field
        self.menubar = None
        self.mouse_palette = None  # placeholder for palettes
        self.zarr_palette = None
        self.viewer = None
        self.shortcuts_widget = None
        self.setMouseTracking(True) # set constant mouse tracking for various mouse modes
        self.is_zooming = False
        self.restart_mainwindow = False
        self.check_actions_enabled = False
        self.actions_initialized = False

        # create status bar at bottom of window
        self.statusbar = self.statusBar()

        # open the series requested from command line
        if filename and os.path.isfile(filename):
            self.openSeries(jser_fp=filename)
        else:
            welcome_series = Series(
                os.path.join(
                    welcome_series_dir,
                    "welcome.ser"
                ),
                {0: "welcome.0"}
            )
            welcome_series.src_dir = os.path.dirname(welcome_series_dir)  # set the images directory for the welcome series
            self.openSeries(welcome_series)

        # set the main window as the parent of the progress bar
        setMainWindow(self)

        # set the theme
        self.setTheme(self.series.getOption("theme"))

        self.show()

        # prompt the user for a username
        self.changeUsername()

    def createMenuBar(self):
        """Create the menu for the main window."""
        menu = [
            
            {
                "attr_name": "filemenu",
                "text": "File",
                "opts":
                [   
                    {
                        "attr_name": "newseriesmenu",
                        "text": "New",
                        "opts":
                        [
                            ("newfromimages_act", "From images...", self.series, self.newSeries),
                            ("newfromzarr_act", "From zarr...", "", lambda : self.newSeries(from_zarr=True)),
                            ("newfromxml_act", "From legacy .ser...", "", self.newFromXML)
                        ]
                    },
                    ("open_act", "Open", self.series, self.openSeries),
                    getOpenRecentMenu(self.series, self.openSeries),
                    None,  # None acts as menu divider
                    ("save_act", "Save", self.series, self.saveToJser),
                    ("saveas_act", "Save as...", "", self.saveAsToJser),
                    {
                        "attr_name": "backupmenu",
                        "text": "Backup",
                        "opts":
                        [
                            ("setbackup_act", "Settings...", "", self.setBackup),
                            ("manualbackup_act", "Backup with comment...", self.series, self.manualBackup),
                            # None,
                            # ("autobackup_act", "Toggle auto-backup", "checkbox", self.toggleAutoBackup),
                        ]
                    },
                    None,
                    ("username_act", "Change username...", "", self.changeUsername),
                    None,
                    ("restart_act", "Reload", self.series, self.restart),
                    ("quit_act", "Quit", self.series, self.close),
                    ##("test_act", "Test", "", self.test),
                ]
            },

            {
                "attr_name": "editmenu",
                "text": "Edit",
                "opts":
                [
                    ("undo_act", "Undo", self.series, self.undo),
                    ("redo_act", "Redo", self.series, lambda : self.undo(True)),
                    None,
                    ("cut_act", "Cut", self.series, self.field.cut),
                    ("copy_act", "Copy", self.series, self.copy),
                    ("paste_act", "Paste", self.series, self.field.paste),
                    ("pasteattributes_act", "Paste attributes", self.series, self.field.pasteAttributes),
                    None,
                    ("pastetopalette_act", "Paste attributes to palette", self.series, self.pasteAttributesToPalette),
                    ("pastetopalettewithshape_act", "Paste attributes to palette (include shape)", self.series, lambda : self.pasteAttributesToPalette(True)),
                    None,
                    {
                        "attr_name": "bcmenu",
                        "text": "Brightness/contrast",
                        "opts":
                        [
                            ("incbr_act", "Increase brightness", self.series, lambda : self.editImage(option="brightness", direction="up")),
                            ("decbr_act", "Decrease brightness", self.series, lambda : self.editImage(option="brightness", direction="down")),
                            ("inccon_act", "Increase contrast", self.series, lambda : self.editImage(option="contrast", direction="up")),
                            ("deccon_act", "Decrease contrast", self.series, lambda : self.editImage(option="contrast", direction="down"))
                        ]
                    }
                ]
            },

            {
                "attr_name": "seriesmenu",
                "text": "Series",
                "opts":
                [
                    ("alloptions_act", "Options...", self.series, self.allOptions),
                    {
                        "attr_name": "importmenu",
                        "text": "Import",
                        "opts":
                        [
                            ("importfromseries_act", "From other series...", "", self.importFromSeries),
                            None,
                            ("importtracepalettecsv_act", "Trace palette from CSV...", "", self.importTracePaletteCSV),
                        ]
                    },
                    {
                        "attr_name": "exportmenu",
                        "text": "Export",
                        "opts":
                        [
                            ("exportxml_act", "as legacy XML series...", "", self.exportToXML),
                            ("exporttracepalette_act", "trace palette as CSV...", "", self.exportTracePaletteCSV),
                        ]
                    },
                    {
                        "attr_name": "imagesmenu",
                        "text": "Images",
                        "opts":
                        [
                            ("change_src_act", "Find/change image directory", "", self.changeSrcDir),
                            ("zarrimage_act", "Convert to zarr", "", self.srcToZarr),
                            ("scalezarr_act", "Update zarr scales", "", lambda : self.srcToZarr(create_new=False)),
                        ]
                    },
                    {
                        "attr_name": "serieshidemenu",
                        "text": "Hide",
                        "opts":
                        [
                            ("hidealltraces_act", "Hide all traces", "", self.hideSeriesTraces),
                            ("unhidealltraces_act", "Unhide all traces", "", lambda : self.hideSeriesTraces(hidden=False))
                        ]
                    },
                    {
                        "attr_name": "threedeemenu",
                        "text": "3D",
                        "opts":
                        [
                            ("load3Dscene_act", "Load 3D scene...", "", self.load3DScene),
                        ]
                    },
                    {
                        "attr_name": "tracepalette_menu",
                        "text": "Trace Palette",
                        "opts":
                        [
                            ("modifytracepalette_act", "All palettes...", self.series, self.mouse_palette.modifyAllPaletteButtons),
                            ("resetpalette_act", "Reset current palette", "", self.resetTracePalette)
                        ]
                    },
                    {
                        "attr_name": "calibrationmenu",
                        "text": "Calibration",
                        "opts":
                        [
                            ("calibrate_act", "Calibrate pixel size...", "", self.calibrateMag),
                            ("setmag_act", "Manually set magnification...", "", self.setSeriesMag),
                        ]
                    },
                    {
                        "attr_name": "seriescodemenu",
                        "text": "Series Code",
                        "opts":
                        [
                            ("setseriescode_act", "Set series code", "", self.setSeriesCode),
                            ("seriescodepattern_act", "Modify regex pattern", "", self.editSeriesCodePattern),
                        ]
                    },
                    None,
                    ("findobjectfirst_act", "Find first object contour...", self.series, self.findObjectFirst),
                    ("removeduplicates_act", "Remove duplicate traces", "", self.deleteDuplicateTraces),
                    None,
                    ("updatecuration_act", "Update curation from history", "", self.updateCurationFromHistory),
                    None,
                    ("bcprofiles_act", "Brightness/contrast profiles...", "", self.changeBCProfiles),
                    None,
                    ("about_act", "About this series...", "", self.displayAbout),
                ]
            },
            
            {
                "attr_name": "sectionmenu",
                "text": "Section",
                "opts":
                [
                    ("nextsection_act", "Next section", "PgUp", self.incrementSection),
                    ("prevsection_act", "Previous section", "PgDown", lambda : self.incrementSection(down=True)),
                    None,
                    ("goto_act", "Go to section", self.series, self.changeSection),
                    None,
                    ("flicker_act", "Flicker section", self.series, self.flickerSections),
                    None,
                    ("findcontour_act", "Find contour...", self.series, self.field.findContourDialog),
                ]
            },
            {
                "attr_name": "listsmenu",
                "text": "Lists",
                "opts":
                [
                    ("objectlist_act", "Object list", self.series, lambda : self.field.openList(list_type="object")),
                    ("tracelist_act", "Trace list", self.series, lambda : self.field.openList(list_type="trace")),
                    ("sectionlist_act", "Section list", self.series, lambda : self.field.openList(list_type="section")),
                    ("ztracelist_act", "Z-trace list", self.series, lambda : self.field.openList(list_type="ztrace")),
                    ("flaglist_act", "Flag list", self.series, lambda : self.field.openList(list_type="flag")),
                    ("history_act", "Series history", "", self.viewSeriesHistory)
                ]
            },
            {
                "attr_name": "alignmentsmenu",
                "text": "Alignments",
                "opts":
                [
                    ("changealignment_act", "Modify alignments", self.series, self.modifyAlignments),
                    None,
                    {
                        "attr_name": "importmenu",
                        "text": "Import alignments",
                        "opts":
                        [
                            ("importtransforms_act", ".txt file", "", self.importTransforms),
                            ("import_swift_transforms_act", "SWiFT project", "", self.importSwiftTransforms),
                        ]
                    },
                    None,
                    {
                        "attr_name": "propagatemenu",
                        "text": "Propagate transform",
                        "opts":
                        [
                            ("startpt_act", "Start propagation recording", "", lambda : self.field.setPropagationMode(True)),
                            ("endpt_act", "End propagation recording", "", lambda : self.field.setPropagationMode(False)),
                            None,
                            ("proptostart_act", "Propagate to start", "", lambda : self.field.propagateTo(False)),
                            ("proptoend_act", "Propagate to end", "", lambda : self.field.propagateTo(True))
                        ]
                    },
                    None,
                    ("unlocksection_act", "Unlock current section", self.series, self.field.unlockSection),
                    ("changetform_act", "Change transformation", self.series, self.changeTform),
                    ("linearalign_act", "Estimate affine transform", "", self.field.affineAlign),
                    # ("quickalign_act", "Auto-align", "Ctrl+\\", self.field.quickAlign)
                ]
            },
            # {
            #     "attr_name": "autosegmenu",
            #     "text": "Autosegment",
            #     "opts":
            #     [
            #         ("export_zarr_act", "Export to zarr...", "", self.exportToZarr),
            #         ("trainzarr_act", "Train...", "", self.train),
            #         ("retrainzarr_act", "Retrain...", "", lambda : self.train(retrain=True)),
            #         ("predictzarr_act", "Predict (infer)...", "", self.predict),
            #         ("sementzarr_act", "Segment...", "", self.segment),
            #         {
            #             "attr_name": "zarrlayermenu",
            #             "text": "Zarr layer",
            #             "opts":
            #             [
            #                 ("setzarrlayer_act", "Set zarr layer...", "", self.setZarrLayer),
            #                 ("removezarrlayer_act", "Remove zarr layer", "", self.removeZarrLayer)
            #             ]
            #         }
            #     ]
            # },
            {
                "attr_name": "viewmenu",
                "text": "View",
                "opts":
                [
                    ("changetheme_act", "Change theme", "", self.setTheme),
                    None,
                    ("fillopacity_act", "Edit fill opacity...", "", self.setFillOpacity),
                    None,
                    ("homeview_act", "Set view to image", "Home", self.field.home),
                    ("viewmag_act", "View magnification...", "", self.field.setViewMagnification),
                    ("findview_act", "Set zoom for finding contours...", "", self.setFindZoom),
                    None,
                    ("toggleztraces_act", "Toggle show Z-traces", "", self.toggleZtraces),
                    None,
                    {
                        "attr_name": "palettemenu",
                        "text": "Palette",
                        "opts":
                        [
                            {
                                "attr_name": "togglepalettemenu",
                                "text": "Toggle palette",
                                "opts":
                                [
                                    ("togglepalette_act", "Trace palette", "checkbox", self.mouse_palette.togglePalette),
                                    ("toggleinc_act",  "Section increment buttons", "checkbox", self.mouse_palette.toggleIncrement),
                                    ("togglebc_act", "Brightness/contrast sliders", "checkbox", self.mouse_palette.toggleBC),

                                ]
                            },
                            {
                                "attr_name": "incpalettemenu",
                                "text": "Increment palette buttons",
                                "opts":
                                [
                                    ("incpaletteup_act", "Up", self.series, lambda : self.mouse_palette.incrementPalette(True)),
                                    ("incpalettedown_act", "Down", self.series, lambda : self.mouse_palette.incrementPalette(False)),
                                ]
                            },
                            ("resetpalette_act", "Reset palette position", "", self.mouse_palette.resetPos),
                        ]
                    },
                    ("lefthanded_act", "Left handed", "checkbox", self.field.setLeftHanded),
                    None,
                    ("togglecuration_act", "Toggle curation in object lists", self.series, self.toggleCuration),
                ]
            },
            {
                "attr_name": "helpmenu",
                "text": "Help",
                "opts":
                [
                    ("repobranch_act", repo_string, "", self.copyCommit),
                    None,
                    ("shortcutshelp_act", "Shortcuts list", "?", self.displayShortcuts),
                    None,
                    {
                        "attr_name": "onlinemenu",
                        "text": "Online resources",
                        "opts": [
                            ("openwiki_act", "PyReconstruct user guide", "", lambda : self.openWebsite(kh_wiki)),
                            ("openrepo_act", "PyReconstruct source code", "", lambda : self.openWebsite(gh_repo)),
                            ("openkhlab_act", "KH lab website", "", lambda : self.openWebsite(kh_web)),
                            ("openkhatlast_act", "Atlas of Ultrastructural Neurocytology", "", lambda : self.openWebsite(kh_atlas))
                        ]
                    },
                    {
                        "attr_name": "issuemenu",
                        "text": "Report issues (GitHub)",
                        "opts":
                        [
                            ("submitissue_act", "Report bug / Request feature", "", lambda : self.openWebsite(gh_submit)),
                            ("seeissues_act", "See unresolved issues", "", lambda : self.openWebsite(gh_issues))
                        ]
                    },
                    ("emailteam_act", "Email developers", "", lambda : self.openWebsite(developers_mailto_str)),
                ]
            }
        ]

        if self.menubar:
            self.menubar.clear()
        else:
            self.menubar = self.menuBar()
            self.menubar.setNativeMenuBar(False)

        # Populate menu bar with menus and options
        populateMenuBar(self, self.menubar, menu)
    
    def createContextMenus(self):
        """Create the right-click menus used in the field."""
        # create the user columns options
        field_menu_list = [
            ("edittrace_act", "Edit attributes...", self.series, self.field.traceDialog),
            {
                "attr_name": "objectattrsmenu",
                "text": "Object attributes",
                "opts":
                [
                    ("objcomment_act", "View/Edit object comment...", "", self.field.setObjComment),
                    ("sethosts_act", "Set host(s)...", self.series, self.field.setHosts),
                ]
            },
            {
                "attr_name": "modifymenu",
                "text": "Modify",
                "opts":
                [
                    ("mergetraces_act", "Merge traces", self.series, self.field.mergeSelectedTraces),
                    ("mergeobjects_act", "Merge attributes...", self.series, lambda : self.field.mergeSelectedTraces(merge_attrs=True)),
                    None,
                    ("makenegative_act", "Make negative", "", self.field.makeNegative),
                    ("makepositive_act", "Make positive", "", lambda : self.field.makeNegative(False)),
                ]
            },
            getUserColsMenu(self.series, self.field.addUserCol, self.field.setUserCol, self.field.editUserCol),
            {
                "attr_name": "lockmenu",
                "text": "Lock/Unlock",
                "opts":
                [
                    ("lockobject_act", "Lock object", "", self.field.lockObjects),
                    ("unlockobject_act", "Unlock object", "", self.field.unlockObject),
                ]
            },
            {
                "attr_name": "curatemenu",
                "text": "Set curation",
                "opts":
                [
                    ("blankcurate_act", "Blank", "", lambda : self.field.setCuration("")),
                    ("needscuration_act", "Needs curation", "", lambda : self.field.setCuration("Needs curation")),
                    ("curated_act", "Curated", "", lambda : self.field.setCuration("Curated"))
                ]
            },
            {
                "attr_name": "viewmenu",
                "text": "View",
                "opts":
                [
                    ("hidetraces_act", "Hide traces", self.series, self.field.hideTraces),
                    ("unhideall_act", "Unhide all traces", self.series, self.field.unhideAllTraces),
                    None,
                    ("hideall_act", "Toggle hide all", self.series, self.field.toggleHideAllTraces),
                    ("showall_act", "Toggle show all", self.series, self.field.toggleShowAllTraces),
                    None,
                    ("hideimage_act", "Toggle hide image", self.series, self.field.toggleHideImage),
                    ("blend_act", "Toggle section blend", self.series, self.field.toggleBlend),
                ]
            },
            getAlignmentsMenu(self.series, self.changeAlignment),
            None,
            self.cut_act,
            self.copy_act,
            self.paste_act,
            self.pasteattributes_act,
            None,
            ("selectall_act", "Select all traces", self.series, self.field.selectAllTraces),
            ("deselect_act", "Deselect traces", self.series, self.field.deselectAllTraces),
            None,
            ("createflag_act", "Create flag...", "", self.field.createTraceFlag),
            None,
            {
                "attr_name": "deleteallmenu",
                "text": "Delete all",
                "opts":
                [
                    ("deletealltraces_act", "traces with same name", "", self.field.deleteAll),
                    ("deletealltracestags_act", "traces with same name and tags", "", lambda : self.field.deleteAll(True))
                ]
            },
            ("delete_act", "Delete", "Del", self.backspace),
        ]
        self.field_menu = QMenu(self)
        populateMenu(self, self.field_menu, field_menu_list)

        # organize actions
        self.trace_actions = [
            self.edittrace_act,
            self.objectattrsmenu,
            self.objcomment_act,
            self.sethosts_act,
            self.modifymenu,
            self.mergetraces_act,
            self.makepositive_act,
            self.makenegative_act,
            self.lockmenu,
            self.lockobject_act,
            self.unlockobject_act,
            self.curatemenu,
            self.blankcurate_act,
            self.needscuration_act,
            self.curated_act,
            self.hidetraces_act,
            self.cut_act,
            self.copy_act,
            self.pasteattributes_act,
            self.createflag_act,
            self.deleteallmenu
        ]
        self.ztrace_actions = [
            self.edittrace_act
        ]

        # create the label menu
        label_menu_list = [
            ("importlabels_act", "Import label(s)", "", self.importLabels),
            ("mergelabels_act", "Merge labels", "", self.mergeLabels)
        ]
        self.label_menu = QMenu(self)
        populateMenu(self, self.label_menu, label_menu_list)

        # check the alignment in the alignment submenu
        self.changeAlignment(self.series.alignment)
    
    def checkActions(self, context_menu=False, clicked_trace=None, clicked_label=None):
        """Check for actions that should be enabled or disabled
        
            Params:
                context_menu (bool): True if context menu is being generated
                clicked_trace (Trace): the trace that was clicked on IF the cotext menu is being generated
        """
        # skip if actions not initialized yet
        if not self.actions_initialized:
            return
        
        # if both traces and ztraces are highlighted or nothing is highlighted, only allow general field options
        if not (bool(self.field.section.selected_traces) ^ 
                bool(self.field.section.selected_ztraces)
        ):
            for a in self.trace_actions:
                a.setEnabled(False)
            for a in self.ztrace_actions:
                a.setEnabled(False)
        # if selected trace in highlighted traces
        elif ((not context_menu and self.field.section.selected_traces) or
              (context_menu and clicked_trace in self.field.section.selected_traces)
        ):
            for a in self.ztrace_actions:
                a.setEnabled(False)
            for a in self.trace_actions:
                a.setEnabled(True)
        # if selected ztrace in highlighted ztraces
        elif ((not context_menu and self.field.section.selected_ztraces) or
              (context_menu and clicked_trace in self.field.section.selected_ztraces)
        ):
            for a in self.trace_actions:
                a.setEnabled(False)
            for a in self.ztrace_actions:
                a.setEnabled(True)
        else:
            for a in self.trace_actions:
                a.setEnabled(False)
            for a in self.ztrace_actions:
                a.setEnabled(False)
            
        # check for objects (to allow merging)
        names = set()
        for trace in self.field.section.selected_traces:
            names.add(trace.name)
        if len(names) > 1:
            self.mergeobjects_act.setEnabled(True)
        else:
            self.mergeobjects_act.setEnabled(False)

        # check labels
        if clicked_label:
            if clicked_label in self.field.zarr_layer.selected_ids:
                self.importlabels_act.setEnabled(True)
                if len(self.zarr_layer.selected_ids) > 1:
                    self.mergelabels_act.setEnabled(True)
            else:
                self.importlabels_act.setEnabled(False)
                self.mergelabels_act.setEnabled(False)
        
        # check if locked trace was right-clicked
        if clicked_trace and self.series.getAttr(clicked_trace.name, "locked"):
            self.unlockobject_act.setEnabled(True)
        else:
            self.unlockobject_act.setEnabled(False)
        
        # MENUBAR

        # disable saving for welcome series
        is_not_welcome_series = not self.series.isWelcomeSeries()
        self.save_act.setEnabled(is_not_welcome_series)
        self.saveas_act.setEnabled(is_not_welcome_series)
        self.backupmenu.setEnabled(is_not_welcome_series)

        # check for palette
        self.togglepalette_act.setChecked(not self.mouse_palette.palette_hidden)
        self.toggleinc_act.setChecked(not self.mouse_palette.inc_hidden)
        self.togglebc_act.setChecked(not self.mouse_palette.bc_hidden)

        # undo/redo
        can_undo_3D, can_undo_2D, _ = self.field.series_states.canUndo(self.field.section.n)
        self.undo_act.setEnabled(can_undo_3D or can_undo_2D)
        can_redo_3D, can_redo_2D, _ = self.field.series_states.canUndo(self.field.section.n, redo=True)
        self.redo_act.setEnabled(can_redo_3D or can_redo_2D)

        # check clipboard for paste options
        if self.field.clipboard:
            self.paste_act.setEnabled(True)
        else:
            self.paste_act.setEnabled(False)
            self.pasteattributes_act.setEnabled(False)

        # zarr images
        self.zarrimage_act.setEnabled(not self.field.section_layer.is_zarr_file)
        self.scalezarr_act.setEnabled(self.field.section_layer.is_zarr_file)

        # calibrate
        self.calibrate_act.setEnabled(bool(self.field.section.selected_traces))

        # # zarr layer
        # self.removezarrlayer_act.setEnabled(bool(self.series.zarr_overlay_fp))
            
    def createShortcuts(self):
        """Create shortcuts that are NOT included in any menus."""
        # domain translate motions
        shortcuts = [
            ("Backspace", self.backspace),

            ("Ctrl+Left", lambda : self.translate("left", "small")),
            ("Left", lambda : self.translate("left", "med")),
            ("Shift+Left", lambda : self.translate("left", "big")),
            ("Ctrl+Right", lambda : self.translate("right", "small")),
            ("Right", lambda : self.translate("right", "med")),
            ("Shift+Right", lambda : self.translate("right", "big")),
            ("Ctrl+Up", lambda : self.translate("up", "small")),
            ("Up", lambda : self.translate("up", "med")),
            ("Shift+Up", lambda : self.translate("up", "big")),
            ("Ctrl+Down", lambda : self.translate("down", "small")),
            ("Down", lambda : self.translate("down", "med")),
            ("Shift+Down", lambda : self.translate("down", "big")),

            ("Ctrl+Shift+Left", self.field.rotateTform),
            ("Ctrl+Shift+Right", lambda : self.field.rotateTform(cc=False))
        ]

        for kbd, act in shortcuts:
            self.addAction("", kbd, act)
    
    def createPaletteShortcuts(self):
        """Create shortcuts associate with the mouse palette."""
        # trace palette shortcuts (1-20)
        trace_shortcuts = []
        for i in range(1, 21):
            sc_str = ""
            if (i-1) // 10 > 0:
                sc_str += "Shift+"
            sc_str += str(i % 10)
            s_switch = (
                sc_str,
                lambda pos=i-1 : self.mouse_palette.activatePaletteButton(pos)
            )
            s_modify = (
                "Ctrl+" + sc_str,
                lambda pos=i-1 : self.mouse_palette.modifyPaletteButton(pos)
            )
            trace_shortcuts.append(s_switch)
            trace_shortcuts.append(s_modify)
        
        for kbd, act in trace_shortcuts:
            self.addAction("", kbd, act)

        
        # mouse mode shortcuts (F1-F8)
        mode_shortcuts = [
            ("usepointer_act", lambda : self.mouse_palette.activateModeButton("Pointer")),
            ("usepanzoom_act", lambda : self.mouse_palette.activateModeButton("Pan/Zoom")),
            ("useknife_act", lambda : self.mouse_palette.activateModeButton("Knife")),
            ("usectrace_act", lambda : self.mouse_palette.activateModeButton("Closed Trace")),
            ("useotrace_act", lambda : self.mouse_palette.activateModeButton("Open Trace")),
            ("usestamp_act", lambda : self.mouse_palette.activateModeButton("Stamp")),
            ("usegrid_act", lambda : self.mouse_palette.activateModeButton("Grid")),
            ("useflag_act", lambda : self.mouse_palette.activateModeButton("Flag")),
            ("usehost_act", lambda : self.mouse_palette.activateModeButton("Host")),
        ]
  
        for act_name, act in mode_shortcuts:
            setattr(
                self, 
                act_name, 
                self.addAction("", self.series.getOption(act_name), act)
            )
    
    def changeSrcDir(self, new_src_dir : str = None, notify=False):
        """Open a series of dialogs to change the image source directory.
        
            Params:
                new_src_dir (str): the new image directory
                notify (bool): True if user is to be notified with a pop-up
        """
        if notify:
            reply = QMessageBox.question(
                self,
                "Images Not Found",
                "Images not found.\nWould you like to locate them?",
                QMessageBox.Yes,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        if new_src_dir is None:
            new_src_dir = FileDialog.get(
                "dir",
                self,
                "Select folder containing images",
            )
        if not new_src_dir: return
        
        self.series.src_dir = new_src_dir
        if self.field:
            self.field.reloadImage()
        self.seriesModified(True)
        
        # prompt user to scale zarr images if not scaled
        if (self.field.section_layer.image_found and 
            self.field.section_layer.is_zarr_file and
            not self.field.section_layer.is_scaled):
            reply = QMessageBox.question(
                self,
                "Zarr Scaling",
                "Zarr file not scaled.\nWould you like to update the zarr with scales?",
                QMessageBox.Yes,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.srcToZarr(create_new=False)
    
    def srcToZarr(self, create_new=True):
        """Convert the series images to zarr."""
        if not self.field.section_layer.image_found:
            notify("Images not found.")
            return
        
        if self.field.section_layer.is_zarr_file and create_new:
            notify("Images are already in zarr format.")
            return
        elif not self.field.section_layer.is_zarr_file and not create_new:
            notify("Images are not in zarr format.\nPlease convert to zarr first.")
            return
        
        if create_new:
            zarr_fp = FileDialog.get(
                "save",
                self,
                "Convert Images to Zarr",
                file_name=f"{self.series.name}_images.zarr",
                filter="Zarr Directory (*.zarr)"
            )
            if not zarr_fp: return

        python_bin = sys.executable
        zarr_converter = os.path.join(assets_dir, "scripts", "convert_zarr", "start_process.py")
        if create_new:
            convert_cmd = [python_bin, zarr_converter, self.series.src_dir, zarr_fp]
        else:
            convert_cmd = [python_bin, zarr_converter, self.series.src_dir]

        if os.name == 'nt':

            subprocess.Popen(convert_cmd, creationflags=subprocess.CREATE_NO_WINDOW)
            
        else:

            convert_cmd = " ".join(convert_cmd)
            subprocess.Popen(convert_cmd, shell=True, stdout=None, stderr=None)

    def changeUsername(self, new_name : str = None):
        """Edit the login name used to track history.
        
            Params:
                new_name (str): the new username
        """
        if new_name is None:
            new_name, confirmed = QInputDialog.getText(
                self,
                "Username",
                "Enter your username:",
                text=QSettings("KHLab", "PyReconstruct").value("username", self.series.user),
            )
            if not confirmed or not new_name:
                return
        
        QSettings("KHLab", "PyReconstruct").setValue("username", new_name)
        self.series.user = new_name

        self.notifyNewEditor()
    
    def setFillOpacity(self, opacity : float = None):
        """Set the opacity of the trace highlight.
        
            Params:
                opacity (float): the new fill opacity
        """
        if opacity is None:
            opacity, confirmed = QInputDialog.getText(
                self,
                "Fill Opacity",
                "Enter fill opacity (0-1):",
                text=str(round(self.series.getOption("fill_opacity"), 3))
            )
            if not confirmed:
                return
        
        try:
            opacity = float(opacity)
        except ValueError:
            return
        
        if not (0 <= opacity <= 1):
            return
        
        self.series.setOption("fill_opacity", opacity)
        self.field.generateView(generate_image=False)

    def openSeries(self, series_obj=None, jser_fp=None):
        """Open an existing series and create the field.
        
            Params:
                series_obj (Series): the series object (optional)
        """
        # user has another series open
        if self.series:
            first_open = False
            response = self.saveToJser(notify=True)
            if response == "cancel":
                return
        else:
            first_open = True
        
        if not series_obj:  # if series is not provided            
            # get the new series
            new_series = None
            if not jser_fp:
                jser_fp = FileDialog.get("file", self, "Open Series", filter="*.jser")
                if not jser_fp: return  # exit function if user does not provide series

            # check for a hidden series folder
            sdir = os.path.dirname(jser_fp)
            sname = os.path.basename(jser_fp)
            sname = sname[:sname.rfind(".")]
            hidden_series_dir = os.path.join(sdir, f".{sname}")

            if os.path.isdir(hidden_series_dir):
                # find the series and timer files
                new_series_fp = ""
                sections = {}
                for f in os.listdir(hidden_series_dir):
                    # check if the series is currently being modified
                    if "." not in f:
                        current_time = round(time.time())
                        time_diff = current_time - int(f)
                        if time_diff <= 7:  # the series is currently being operated on
                            QMessageBox.information(
                                self,
                                "Series In Use",
                                "This series is already open in another window.",
                                QMessageBox.Ok
                            )
                            if not self.series:
                                exit()
                            else:
                                return
                    else:
                        ext = f[f.rfind(".")+1:]
                        if ext.isnumeric():
                            sections[int(ext)] = f
                        elif ext == "ser":
                            new_series_fp = os.path.join(hidden_series_dir, f)                    

                # if a series file has been found
                if new_series_fp:
                    # ask the user if they want to open a previously unsaved series
                    open_unsaved = unsavedNotify()
                    if open_unsaved:
                        new_series = Series(new_series_fp, sections)
                        new_series.modified = True
                        new_series.jser_fp = jser_fp
                    else:
                        # remove the folder if not needed
                        for f in os.listdir(hidden_series_dir):
                            os.remove(os.path.join(hidden_series_dir, f))
                        os.rmdir(hidden_series_dir)
                else:
                    # remove the folder if no series file detected
                    for f in os.listdir(hidden_series_dir):
                        os.remove(os.path.join(hidden_series_dir, f))
                    os.rmdir(hidden_series_dir)

            # open the JSER file if no unsaved series was opened
            if not new_series:
                new_series = Series.openJser(jser_fp)
                # user pressed cancel
                if new_series is None:
                    if self.series is None:
                        exit()
                    else:
                        return
            
            # clear the series
            if self.series and not self.series.isWelcomeSeries():
                self.series.close()

            self.series = new_series

        # else series already provided
        else:
            # clear current series
            if self.series and not self.series.isWelcomeSeries():
                self.series.close()
                
            # set new series
            self.series = series_obj
        
        # set the title of the main window
        self.seriesModified(self.series.modified)

        # set explorer filepath
        if not self.series.isWelcomeSeries() and self.series.jser_fp:
            settings = QSettings("KHLab", "PyReconstruct")
            settings.setValue("last_folder", os.path.dirname(self.series.jser_fp))

        # create field
        if self.field is not None:  # close previous field widget
            self.field.createField(self.series)
        else:
            self.field = FieldWidget(self.series, self)
            self.setCentralWidget(self.field)

        # create mouse palette
        if self.mouse_palette: # close previous mouse dock
            self.mouse_palette.reset()
        else:
            self.mouse_palette = MousePalette(self)
            self.createPaletteShortcuts()
        palette_group, index = tuple(self.series.palette_index)
        self.changeTracingTrace(
            self.series.palette_traces[palette_group][index]
        ) # set the current trace

        # ensure that images are found
        if not self.field.section_layer.image_found:
            # check jser directory
            src_path = os.path.join(
                os.path.dirname(self.series.jser_fp),
                os.path.basename(self.field.section.src)
            )
            images_found = os.path.isfile(src_path)
            
            if images_found:
                self.changeSrcDir(src_path)
            else:
                self.changeSrcDir(notify=True)
        # prompt user to scale zarr images if not scaled
        elif (self.field.section_layer.image_found and 
            self.field.section_layer.is_zarr_file and
            not self.field.section_layer.is_scaled):
            reply = QMessageBox.question(
                self,
                "Zarr Scaling",
                "Zarr not scaled.\nWould you like to scale now?",
                QMessageBox.Yes,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.srcToZarr(create_new=False)
        
        # get the series code from the user if needed
        if not self.series.isWelcomeSeries() and not self.series.code:
            detected_code = re.search(
                self.series.getOption("series_code_pattern"), 
                self.series.name
            )
            if detected_code:
                self.series.code = detected_code.group()
            self.setSeriesCode(cancelable=False)
            self.seriesModified()
        
        # notify new users of any warnings
        if not first_open:
            self.notifyNewEditor()
        
        # create the menus
        self.createMenuBar()
        self.createContextMenus()
        if not self.actions_initialized:
            self.createShortcuts()
        self.actions_initialized = True

        # add the series to recently opened
        self.addToRecentSeries()
        
    def newSeries(
        self,
        image_locations : list = None,
        series_name : str = None,
        mag : float = None,
        thickness : float = None,
        from_zarr : bool = False
    ):
        """Create a new series from a set of images.
        
            Params:
                image_locations (list): the filepaths for the section images.
        """
        # get images from user
        if not image_locations:
            if from_zarr:
                valid_zarr = False
                while not valid_zarr:
                    zarr_fp = FileDialog.get(
                        "dir",
                        self,
                        "Select Zarr"
                    )
                    if not zarr_fp: return
                    
                    # get the image names in the zarr
                    if "scale_1" in os.listdir(zarr_fp):
                        valid_zarr = True
                        image_locations = []
                        for f in os.listdir(os.path.join(zarr_fp, "scale_1")):
                            if not f.startswith("."):
                                image_locations.append(os.path.join(zarr_fp, "scale_1", f))
                    else:
                        notify("Please select a valid zarr file.")                
            else:
                image_locations = FileDialog.get(
                    "files",
                    self,
                    "Select Images",
                    filter="*.jpg *.jpeg *.png *.tif *.tiff *.bmp"
                )
                if len(image_locations) == 0: return
        
        # get the name of the series from user
        if series_name is None:
            series_name, confirmed = QInputDialog.getText(
                self, "New Series", "Enter series name:")
            if not confirmed:
                return
        # get calibration (microns per pix) from user
        if mag is None:
            mag, confirmed = QInputDialog.getDouble(
                self, "New Series", "Enter image calibration (μm/px):",
                0.00254, minValue=0.000001, decimals=6)
            if not confirmed:
                return
        # get section thickness (microns) from user
        if thickness is None:
            thickness, confirmed = QInputDialog.getDouble(
                self, "New Series", "Enter section thickness (μm):",
                0.05, minValue=0.000001, decimals=6)
            if not confirmed:
                return
        
        # save and clear the existing backend series
        self.saveToJser(notify=True, close=True)
        
        # create new series
        series = Series.new(sorted(image_locations), series_name, mag, thickness)
    
        # open series after creating
        self.openSeries(series)

        # prompt the user to save the series
        self.saveAsToJser()
    
    def newFromXML(self, series_fp : str = None):
        """Create a new series from a set of XML files.
        
            Params:
                series_fp (str): the filepath for the XML series
        """

        # get xml series from user
        if not series_fp:
            series_fp = FileDialog.get(
                "file",
                self,
                "Select XML Series",
                filter="*.ser"
            )
            if not series_fp: return  # exit function if no series provided

        # convert the series
        series = xmlToJSON(os.path.dirname(series_fp))

        if not series:
            return

        # open new series
        self.openSeries(series)

        # prompt user to save series
        self.saveAsToJser()
    
    def exportToXML(self, export_fp : str = None):
        """Export the current series to XML.
        
            Params:
                export_fp (str): the filepath for the XML .ser file
        """

        # save the current data
        self.saveAllData()

        # get the new xml series filepath from the user
        if not export_fp:
            export_fp = FileDialog.get(
                "save",
                self,
                "Export Series",
                file_name=f"{self.series.name}.ser",
                filter="XML Series (*.ser)"
            )
            if not export_fp: return False
        
        # convert the series
        jsonToXML(self.series, os.path.dirname(export_fp))
    
    def seriesModified(self, modified=True):
        """Change the title of the window reflect modifications."""
        # check for welcome series
        if self.series.isWelcomeSeries():
            self.setWindowTitle("PyReconstruct")
            return
        
        if modified:
            self.setWindowTitle(self.series.name + "*")
        else:
            self.setWindowTitle(self.series.name)
        self.series.modified = modified

        if self.field:
            self.checkActions()
    
    def importTransforms(self, tforms_fp : str = None):
        """Import transforms from a text file.
        
            Params:
                tforms_file (str): the filepath for the transforms file
        """
        self.saveAllData()
        # get file from user
        if tforms_fp is None:
            tforms_fp = FileDialog.get(
                "file",
                self,
                "Select file containing transforms"
            )
        if not tforms_fp: return
        
        # import the transforms
        importTransforms(self.series, tforms_fp, series_states=self.field.series_states)
        
        # reload the section
        self.field.reload()

        # refresh the data and lists
        self.field.table_manager.recreateTables()

        notify("Transforms imported successfully.")

    def importSwiftTransforms(self, swift_fp=None):
        """Import transforms from a text file.
        
            Params:
                swift_fp (str): the filepath for the transforms file
        """

        self.saveAllData()
        
        # get file from user
        if not swift_fp:
            swift_fp = FileDialog.get("file", self, "Select SWiFT project file")
            
        if not swift_fp:
            return

        # get scales from the swift project file
        with open(swift_fp, "r") as fp: swift_json = json.load(fp)

        scale_names = swift_json.get("level_data")

        if scale_names:  # new swift project file formatting
        
            scale_names = list(swift_json["level_data"].keys())
            scales_available = [int(scale[1:]) for scale in scale_names]

        else:  # old swift project file formatting

            scales_data = swift_json["data"]["scales"]
            scale_names = list(scales_data.keys())
            scales_available = [int(scale[6:]) for scale in scale_names]

        scales_available.sort()
        
        print(f'Available SWiFT project scales: {scales_available}')

        structure = [
            ["Scale:", (True, "combo", [str(s) for s in scales_available])],
            [("check", ("Includes cal grid", False))]
        ]

        response, confirmed = QuickDialog.get(self, structure, "Import SWiFT Transforms")
        if not confirmed:
            return
        scale = response[0]
        cal_grid = response[1][0][1]

        # import transforms
        print(f'Importing SWiFT transforms at scale {scale}...')
        if cal_grid: print('Cal grid included in series')
        importSwiftTransforms(self.series, swift_fp, scale, cal_grid, series_states=self.field.series_states)
        
        self.field.reload()

        # refresh the data and lists
        self.field.table_manager.recreateTables()

        notify("Transforms imported successfully.")
    
    def editImage(self, option : str, direction : str, log_event=True):
        """Edit the brightness or contrast of the image.
        
            Params:
                option (str): brightness or contrast
                direction (str): up or down
        """
        if option == "brightness" and direction == "up":
            self.field.changeBrightness(1)
        elif option == "brightness" and direction == "down":
            self.field.changeBrightness(-1)
        elif option == "contrast" and direction == "up":
            self.field.changeContrast(2)
        elif option == "contrast" and direction == "down":
            self.field.changeContrast(-2)
        self.mouse_palette.updateBC()
    
    def changeMouseMode(self, new_mode):
        """Change the mouse mode of the field (pointer, panzoom, tracing...).

        Called when user clicks on mouse mode palette.

            Params:
                new_mode: the new mouse mode to set
        """
        self.field.setMouseMode(new_mode)
    
    def changeTraceMode(self):
        """Change the trace mode and shape."""
        current_shape = self.field.closed_trace_shape
        current_mode = self.series.getOption("trace_mode")
        structure = [
            ["Mode:"],
            [("radio",
                ("Scribble", current_mode == "scribble"),
                ("Poly", current_mode == "poly"),
                ("Combo", current_mode == "combo")
            )],
            ["Closed Trace Shape:"],
            [("radio",
                ("Trace", current_shape == "trace"),
                ("Rectangle", current_shape == "rect"),
                ("Ellipse", current_shape == "circle")
            )],
            [("check", ("Automatically merge selected traces", self.series.getOption("auto_merge")))]
        ]
        response, confirmed = QuickDialog.get(self, structure, "Closed Trace Mode")
        if not confirmed:
            return
        
        if response[0][0][1]:
            new_mode = "scribble"
        elif response[0][1][1]:
            new_mode = "poly"
        else:
            new_mode = "combo"
        
        if response[1][1][1]:
            new_shape = "rect"
        elif response[1][2][1]:
            new_shape = "circle"
        else:
            new_shape = "trace"
        
        self.series.setOption("trace_mode", new_mode)
        self.field.closed_trace_shape = new_shape
        self.series.setOption("auto_merge", response[2][0][1])

    def changeTracingTrace(self, trace):
        """Change the trace utilized by the user.

        Called when user clicks on trace palette.

            Params:
                trace: the new tracing trace to set
        """
        self.field.setTracingTrace(trace)
    
    def changeSection(self, section_num : int = None, save=True):
        """Change the section of the field.
        
            Params:
                section_num (int): the section number to change to
                save (bool): saves data to files if True
        """
        if section_num is None:
            section_num, confirmed = QInputDialog.getText(
                self, "Go To Section", "Enter the desired section number:", text=str(self.series.current_section))
            if not confirmed:
                return
            try:
                section_num = int(section_num)
            except ValueError:
                return
        
        # end the field pending events
        self.field.endPendingEvents()
        # save data
        if save:
            self.saveAllData()
        # change the field section
        self.field.changeSection(section_num)
        # update status bar
        self.field.updateStatusBar()
        # update the mouse palette
        self.mouse_palette.updateBC()
    
    def flickerSections(self):
        """Switch between the current and b sections."""
        if self.field.b_section:
            self.changeSection(self.field.b_section.n, save=False)
    
    def incrementSection(self, down=False):
        """Increment the section number by one.
        
            Params:
                down (bool): the direction to move
        """
        section_numbers = sorted(list(self.series.sections.keys()))  # get list of all section numbers
        section_number_i = section_numbers.index(self.series.current_section)  # get index of current section number in list
        if down:
            if section_number_i > 0:
                self.changeSection(section_numbers[section_number_i - 1])  
        else:   
            if section_number_i < len(section_numbers) - 1:
                self.changeSection(section_numbers[section_number_i + 1])       
    
    def wheelEvent(self, event):
        """Called when mouse scroll is used."""
        # do nothing if middle button is clicked
        if self.field.mclick:
            return
        
        modifiers = QApplication.keyboardModifiers()

        # if zooming
        if modifiers == Qt.ControlModifier:
            self.activateWindow()
            field_cursor = self.field.cursor()
            p = self.field.mapFromGlobal(field_cursor.pos())
            x, y = p.x(), p.y()
            if not self.is_zooming:
                # check if user just started zooming in
                self.field.panzoomPress(x, y)
                self.zoom_factor = 1
                self.is_zooming = True

            if event.angleDelta().y() > 0:  # if scroll up
                self.zoom_factor *= 1.1
            elif event.angleDelta().y() < 0:  # if scroll down
                self.zoom_factor *= 0.9
            self.field.panzoomMove(zoom_factor=self.zoom_factor)
        
        # if changing sections
        elif modifiers == Qt.NoModifier:
            # check for the position of the mouse
            mouse_pos = event.point(0).pos()
            field_geom = self.field.geometry()
            if not field_geom.contains(mouse_pos.x(), mouse_pos.y()):
                return
            # change the section
            if event.angleDelta().y() > 0:  # if scroll up
                self.incrementSection()
            elif event.angleDelta().y() < 0:  # if scroll down
                self.incrementSection(down=True)
    
    def keyReleaseEvent(self, event):
        """Overwritten: checks for Ctrl+Zoom."""
        if self.is_zooming and event.key() == 16777249:
            self.field.panzoomRelease(zoom_factor=self.zoom_factor)
            self.is_zooming = False
        
        super().keyReleaseEvent(event)
    
    def saveAllData(self):
        """Write current series and section data into hidden JSON files."""
        if self.series.isWelcomeSeries():
            return
        # # save the trace palette
        # self.series.palette_traces = []
        # for button in self.mouse_palette.palette_buttons:  # get trace palette
        #     self.series.palette_traces.append(button.trace)
        #     if button.isChecked():
        #         self.series.current_trace = button.trace
        self.field.section.save(update_series_data=False)
        self.series.save()
    
    def backup(self, check_auto=False, comment=""):
        """Automatically backup the jser if requested."""
        if check_auto and not self.series.getOption("autobackup"):
            return
        
        # make sure the backup directory exists
        if not os.path.isdir(self.series.getOption("backup_dir")):
            notify(
                "Backup folder not found.\n" + 
                "Please set the backup folder in following dialog."
            )
            self.series.setOption("backup_dir", "")
            self.setBackup()
        
        # double check if user entered a valid backup directory
        if os.path.isdir(self.series.getOption("backup_dir")):
            fp = self.series.getBackupPath(comment)
            self.series.saveJser(fp)
        else:
            notify(
                "Backup folder not found.\n" +
                "Backup file not saved."
            )
            self.series.setOption("backup_dir", "")
            self.series.setOption("autobackup", False)
    
    def saveToJser(self, notify=False, close=False):
        """Save data to JSER file.
        
        Params:
            notify (bool): If true, display notification.
            close (bool): If true, delete hidden series files.
        """

        # store series data in hidden files
        self.saveAllData()

        # if welcome series, close without saving
        if self.series.isWelcomeSeries():
            return
        
        # notify user and series modified
        if notify and self.series.modified:
            save = saveNotify()
            if save == "no":
                if close:
                    self.series.close()
                return
            elif save == "cancel":
                return "cancel"
        
        # user closing and series not modified
        if close and not self.series.modified:
            self.series.close()
            return

        # save-as if no jser filepath
        if not self.series.jser_fp:
            self.saveAsToJser(close=close)
        else:  
            self.backup(check_auto=True)
            self.series.saveJser(close=close)
        
        # mark series as unmodified
        self.seriesModified(False)
    
    def saveAsToJser(self, close=False):
        """Prompt user to determine save location."""
        # store series data in hidden files
        self.saveAllData()

        # if welcome series, close without saving
        if self.series.isWelcomeSeries():
            return

        # get location from user
        new_jser_fp = FileDialog.get(
            "save",
            self,
            "Save Series",
            filter="*.jser",
            file_name=f"{self.series.name}.jser"
        )
        if not new_jser_fp: return
        
        # move hidden folder to new jser directory
        self.series.move(
            new_jser_fp,
            self.field.section,
            self.field.b_section
        )
        
        # clear section states
        self.field.series_states.clear()
        self.field.series_states[self.field.section]
        if self.field.b_section:
            self.field.series_states[self.field.b_section]
        
        # save file
        self.backup(check_auto=True)
        self.series.saveJser(close=close)

        # mark series as unmodified
        self.seriesModified(False)
    
    def setBackup(self):
        """Set up backup directory and settings."""
        confirmed = BackupDialog(self, self.series).exec()
        self.seriesModified()
    
    def manualBackup(self):
        """Back up series to a specified location."""
        self.saveAllData()

        response, confirmed = BackupCommentDialog(self, self.series).exec()
        if not confirmed:
            return
        
        comment, open_settings = response
        if open_settings:
            self.setBackup()
            self.manualBackup()
        else:
            self.backup(comment=comment)
    
    def viewSeriesHistory(self):
        """View the history for the entire series."""
        HistoryTableWidget(self.series.getFullHistory(), self)
    
    def toggleZtraces(self):
        """Toggle whether ztraces are shown."""
        self.field.deselectAllTraces()
        self.series.setOption("show_ztraces", not self.series.getOption("show_ztraces"))
        self.field.generateView(generate_image=False)
    
    def setToObject(self, obj_name : str, section_num : int):
        """Focus the field on an object from a specified section.
        
            Params:
                obj_name (str): the name of the object
                section_num (int): the section the object is located
        """
        if obj_name is not None and section_num is not None:
            self.changeSection(section_num)
            self.field.findContour(obj_name)
            self.field.setFocus()
    
    def setToFlag(self, flag : Flag):
        """Focus the field on a flag.
        
            Params:
                flag (Flag): the flag
        """
        if flag is not None:
            self.changeSection(flag.snum)
            self.field.findFlag(flag)
            self.field.setFocus()
    
    def findObjectFirst(self, obj_name=None):
        """Find the first or last contour in the series.
        
            Params:
                obj_name (str): the name of the object to find
        """
        if obj_name is None:
            obj_name, confirmed = QInputDialog.getText(
                self,
                "Find Object",
                "Enter the object name:",
            )
            if not confirmed:
                return

        # find the contour
        self.setToObject(obj_name, self.series.data.getStart(obj_name))
    
    def changeTform(self, new_tform_list : list = None):
        """Open a dialog to change the transform of a section."""
        # check for section locked status
        if self.field.section.align_locked:
            return
        
        if new_tform_list is None:
            current_tform = " ".join(
                [str(round(n, 5)) for n in self.field.section.tform.getList()]
            )
            new_tform_list, confirmed = QInputDialog.getText(
                self, "New Transform", "Enter the desired section transform:", text=current_tform)
            if not confirmed:
                return
            try:
                new_tform_list = [float(n) for n in new_tform_list.split()]
                if len(new_tform_list) != 6:
                    return
            except ValueError:
                return
        self.field.changeTform(Transform(new_tform_list))
    
    def translate(self, direction : str, amount : str):
        """Translate the current transform.
        
            Params:
                direction (str): left, right, up, or down
                amount (str): small, med, or big
        """
        if amount == "small":
            num = self.series.getOption("small_dist")
        elif amount == "med":
            num = self.series.getOption("med_dist")
        elif amount == "big":
            num = self.series.getOption("big_dist")
        if direction == "left":
            x, y = -num, 0
        elif direction == "right":
            x, y = num, 0
        elif direction == "up":
            x, y = 0, num
        elif direction == "down":
            x, y = 0, -num
        self.field.translate(x, y)
    
    def newAlignment(self, new_alignment_name : str):
        """Add a new alignment (based on existing alignment).
        
            Params:
                new_alignment_name (str): the name of the new alignment
        """
        if new_alignment_name in self.field.section.tforms:
            QMessageBox.information(
                self,
                " ",
                "This alignment already exists.",
                QMessageBox.Ok
            )
            return
        self.series.newAlignment(
            new_alignment_name,
            self.series.alignment
        )
    
    def modifyAlignments(self):
        """Open dialog to modify alignments."""
        self.saveAllData()
        
        alignments = list(self.field.section.tforms.keys())

        response, confirmed = AlignmentDialog(
            self,
            alignments,
            self.series.alignment
        ).exec()
        if not confirmed:
            return
        
        alignment_name, alignment_dict = response

        modified = False
        if alignment_dict:
            for k, v in alignment_dict.items():
                if k != v:
                    modified = True
                    break
            if modified:
                self.series.modifyAlignments(alignment_dict, self.field.series_states)
                self.createContextMenus()
        
        if alignment_name:
            self.changeAlignment(alignment_name, overwrite=True)
        else:
            self.changeAlignment(self.series.alignment, overwrite=True)

    def changeAlignment(self, new_alignment : str, overwrite=False):
        """Change the current sereis alignment.
        
            Params:
                alignment (str): the alignment to switch to
                overwrite (bool): change the alignment even if the name is the same
        """
        attr = getattr(self, f"{new_alignment}_alignment_act")
        attr.setChecked(True)

        current_alignment = self.series.alignment
        if overwrite or new_alignment != current_alignment:
            attr = getattr(self, f"{current_alignment}_alignment_act")  # generated from createContextMenu
            attr.setChecked(False)
            self.field.changeAlignment(new_alignment)
    
    def changeBCProfiles(self):
        """Open dialog to modify and change brightness/contrast profiles."""
        self.saveAllData()
        
        bc_profiles = list(self.field.section.bc_profiles.keys())

        response, confirmed = BCProfilesDialog(
            self,
            bc_profiles,
            self.series.bc_profile
        ).exec()
        if not confirmed:
            return
        
        profile_name, profiles_dict = response

        modified = False
        if profiles_dict:
            for k, v in profiles_dict.items():
                if k != v:
                    modified = True
                    break
            if modified:
                self.series.modifyBCProfiles(profiles_dict, self.field.series_states)
                self.field.reload()
        
        if profile_name:
            self.field.changeBCProfile(profile_name)
        elif modified:
            self.field.changeBCProfile(self.series.bc_profile)
            
    def calibrateMag(self, trace_lengths : dict = None):
        """Calibrate the pixel size for the series.
        
            Params:
                trace_lengths (dict): the lengths of traces to calibrate
        """
        self.saveAllData()
        
        if trace_lengths is None:
            # gather trace names
            names = []
            for trace in self.field.section.selected_traces:
                if trace.name not in names:
                    names.append(trace.name)
            
            if len(names) == 0:
                notify("Please select traces for calibration.")
            
            # prompt user for length of each trace name
            trace_lengths = {}
            for name in names:
                d, confirmed = QInputDialog.getText(
                    self,
                    "Trace Length",
                    f'Length of "{name}" in microns:'
                )
                if not confirmed:
                    return
                try:
                    d = float(d)
                except ValueError:
                    return
                trace_lengths[name] = d
        
        self.field.calibrateMag(trace_lengths)
    
    def setSeriesMag(self):
        """Manually set (or view) the series magnification."""
        response, confirmed = QInputDialog.getDouble(
            self, 
            "Set Magnification", 
            "Series magnification (microns per image pixel):",
            self.series.avg_mag,
            decimals=8,
            step = 0.001
        )
        if not confirmed:
            return
        if response <= 0:
            notify("Magnification cannot be less than or equal to zero.")
        
        self.saveAllData()
        
        self.field.setMag(response)
    
    def modifyPointer(self, event=None):
        """Modify the pointer properties."""
        s, t = tuple(self.series.getOption("pointer"))
        structure = [
            ["Shape:"],
            [("radio", ("Rectangle", s=="rect"), ("Lasso", s=="lasso"))],
            ["Type:"],
            [("radio", ("Include intersected traces", t=="inc"), ("Exclude intersected traces", t=="exc"))],
            [("check", ("Diplay closest field item", self.series.getOption("display_closest")))]
        ]
        response, confirmed = QuickDialog.get(self, structure, "Pointer Settings")
        if not confirmed:
            return
        
        s = "rect" if response[0][0][1] else "lasso"
        t = "inc" if response[1][0][1] else "exc"
        self.series.setOption("pointer", [s, t])
        self.series.setOption("display_closest", response[2][0][1])
        self.seriesModified()
    
    def modifyGrid(self, event=None):
        """Modify the grid properties."""
        response, confirmed = GridDialog(
            self,
            tuple(self.series.getOption("grid")),
            self.series.getOption("sampling_frame_grid")
        ).exec()
        if not confirmed:
            return
        
        grid_response, sf_grid = response
        self.series.setOption("grid", grid_response)
        self.series.setOption("sampling_frame_grid", sf_grid)
        self.seriesModified()
    
    def modifyKnife(self, event=None):
        """Modify the knife properties."""
        structure = [
            ["Delete traces smaller than this percent of the"],
            ["original trace when using the knife."],
            ["% area:", ("float", self.series.getOption("knife_del_threshold"), (0, 100))],
        ]
        response, confirmed = QuickDialog.get(self, structure, "Knife")
        if not confirmed:
            return
        
        self.series.setOption("knife_del_threshold", response[0])
        self.seriesModified()
    
    def resetTracePalette(self):
        """Reset the trace palette to default traces."""
        self.mouse_palette.resetPalette()
        self.saveAllData()
        self.seriesModified()
    
    def setZarrLayer(self, zarr_dir=None):
        """Set a zarr layer."""
        if not zarr_dir:
            zarr_dir = FileDialog.get(
                "dir",
                self,
                "Select overlay zarr",
            )
            if not zarr_dir: return

        self.series.zarr_overlay_fp = zarr_dir
        self.series.zarr_overlay_group = None

        groups = []
        for g in os.listdir(zarr_dir):
            if os.path.isdir(os.path.join(zarr_dir, g)):
                groups.append(g)

        self.zarr_palette = ZarrPalette(groups, self)
    
    def setLayerGroup(self, group_name):
        """Set the specific group displayed in the zarr layer."""
        if not group_name:
            group_name = None
        if self.zarr_palette.cb.currentText != group_name:
            self.zarr_palette.cb.setCurrentText(group_name)
        self.series.zarr_overlay_group = group_name
        self.field.createZarrLayer()
        self.field.generateView()
    
    def removeZarrLayer(self):
        """Remove an existing zarr layer."""
        self.series.zarr_overlay_fp = None
        self.series.zarr_overlay_group = None
        if self.zarr_palette:
            self.zarr_palette.close()
        self.field.createZarrLayer()
        self.field.generateView()

    def exportToZarr(self):
        """Create a neuroglancer-compatible zarr for autosegmentation."""

        pass  # TODO: Update for new zarring method
    
        # self.saveAllData()
        # self.removeZarrLayer()

        # inputs, dialog_confirmed = CreateZarrDialog(self, self.series).exec()

        # if not dialog_confirmed: return

        # border_obj, srange, mag = inputs

        # # convert border obj to window
        # window = borderToWindow(border_obj, srange, self.series)

        # print("Making zarr directory...")
        
        # # export to zarr
        # data_fp = seriesToZarr(
        #     self.series,
        #     srange,
        #     mag,
        #     window
        # )

        # self.series.options["autoseg"]["zarr_current"] = data_fp

        # print(f"Zarr directory done and located here: {data_fp}")
    
    def train(self, retrain=False):
        """Train an autosegmentation model."""
        self.saveAllData()
        self.removeZarrLayer()

        model_paths = {"a":{"b":"a/b/m.py"}}

        opts = self.series.options["autoseg"]

        response, confirmed = TrainDialog(self, self.series, model_paths, opts, retrain).exec()
        if not confirmed: return
        
        (data_fp, iterations, save_every, group, model_path, cdir, \
         pre_cache, min_masked, downsample) = response

        training_opts = {
            'zarr_current': data_fp,
            'iters': iterations,
            'save_every': save_every,
            'group': group,
            'model_path': model_path,
            'checkpts_dir': cdir,
            'pre_cache': pre_cache,
            'min_masked': min_masked,
            'downsample_bool': downsample
        }

        for k, v in training_opts.items():
            opts[k] = v
        self.seriesModified(True)

        print("Exporting labels to zarr directory...")
        
        if retrain:
            group_name = f"labels_{self.series.getRecentSegGroup()}_keep"
            seriesToLabels(self.series, data_fp)
            
        else:
            group_name = f"labels_{group}"
            seriesToLabels(self.series, data_fp, group)

        print("Zarr directory updated with labels!")

        if retrain:
            self.field.reload()
            self.field.table_manager.refresh()

        print("Starting training....")

        print("Importing training modules...")

        from autoseg import train, make_mask, model_paths

        make_mask(data_fp, group_name)
        
        sources = [{
            "raw" : (data_fp, "raw"),
            "labels" : (data_fp, group_name),
            "unlabelled" : (data_fp, "unlabelled")
        }]

        train(
            iterations=iterations,
            save_every=save_every,
            sources=sources,
            model_path=model_path,
            pre_cache=pre_cache,
            min_masked=min_masked,
            downsample=downsample,
            checkpoint_basename=os.path.join(cdir, "model")  # where existing checkpoints
        )

        print("Done training!")
    
    def markKeep(self):
        """Add the selected trace to the most recent "keep" segmentation group."""
        keep_tag = f"{self.series.getRecentSegGroup()}_keep"
        for trace in self.field.section.selected_traces:
            trace.addTag(keep_tag)
        # deselect traces and hide
        self.field.hideTraces()
        self.field.deselectAllTraces()

    def predict(self, data_fp : str = None):
        """Run predictons.
        
            Params:
                data_fp (str): the filepath for the zarr
        """
        self.saveAllData()
        self.removeZarrLayer()

        print("Importing models...")
        
        from autoseg import predict, model_paths
        # model_paths = {"a":{"b":"a/b/m.py"}}

        opts = self.series.options["autoseg"]

        response, dialog_confirmed = PredictDialog(self, model_paths, opts).exec()

        if not dialog_confirmed: return

        data_fp, model_path, cp_path, write_opts, increase, downsample, full_out_roi = response

        predict_opts = {
            'zarr_current': data_fp,
            'model_path': model_path,
            'checkpts_dir': os.path.dirname(cp_path),
            'write': write_opts,
            'increase': increase,
            'downsample_bool': downsample,
            'full_out_roi': full_out_roi
        }

        for k, v in predict_opts.items():
            opts[k] = v
        self.seriesModified(True)
                
        print("Running predictions...")

        zarr_datasets = predict(
            sources=[(data_fp, "raw")],
            out_file=data_fp,
            checkpoint_path=cp_path,
            model_path=model_path,
            write=write_opts,
            increase=increase,
            downsample=downsample,
            full_out_roi=full_out_roi
        )

        # display the affinities
        self.setZarrLayer(data_fp)
        for zg in os.listdir(data_fp):
            if zg.startswith("pred_affs"):
                self.setLayerGroup(zg)
                break

        print("Predictions done.")
        
    def segment(self, data_fp : str = None):
        """Run an autosegmentation.
        
            Params:
                data_fp (str): the filepath for the zarr
        """
        self.saveAllData()
        self.removeZarrLayer()

        print("Importing modules...")
        
        from autoseg import hierarchical

        opts = self.series.options["autoseg"]

        response, dialog_confirmed = SegmentDialog(self, opts).exec()

        if not dialog_confirmed: return

        data_fp, thresholds, downsample, norm_preds, min_seed, merge_fun = response

        segment_opts = {
            "zarr_current": data_fp,
            "thresholds": thresholds,
            "downsample_int": downsample,
            "norm_preds": norm_preds,
            "min_seed": min_seed,
            "merge_fun": merge_fun
        }

        for k, v in segment_opts.items():
            opts[k] = v
        self.seriesModified(True)

        print("Running hierarchical...")

        dataset = None
        for d in os.listdir(data_fp):
            if "affs" in d:
                dataset = d
                break

        print("Segmentation started...")
            
        hierarchical.run(
            data_fp,
            dataset,
            thresholds=list(sorted(thresholds)),
            normalize_preds=norm_preds,
            min_seed_distance=min_seed,
            merge_function=merge_fun
        )

        print("Segmentation done.")

        # display the segmetnation
        self.setZarrLayer(data_fp)
        for zg in os.listdir(data_fp):
            if zg.startswith("seg"):
                self.setLayerGroup(zg)
                break
    
    def importLabels(self, all=False):
        """Import labels from a zarr."""
        if not self.field.zarr_layer or not self.field.zarr_layer.is_labels:
            return
        
        # get necessary data
        data_fp = self.series.zarr_overlay_fp
        group_name = self.series.zarr_overlay_group

        labels = None if all else self.field.zarr_layer.selected_ids
        
        labelsToObjects(
            self.series,
            data_fp,
            group_name,
            labels
        )
        self.field.reload()
        self.removeZarrLayer()
        self.field.table_manager.refresh()

        notify("Labels imported successfully.")
    
    def mergeLabels(self):
        """Merge selected labels in a zarr."""
        if not self.field.zarr_layer:
            return
        
        self.field.zarr_layer.mergeLabels()
        self.field.generateView()
    
    def hideSeriesTraces(self, hidden=True):
        """Hide or unhide all traces in the entire series.
        
            Params:
                hidden (bool) True if traces will be hidden
        """
        self.saveAllData()
        self.series.hideAllTraces(hidden)
        self.field.reload()
    
    def setFindZoom(self):
        """Set the magnification for find contour."""
        z, confirmed = QInputDialog.getInt(
            self,
            "Find Contour Zoom",
            "Enter the find contour zoom (0-100):",
            value=self.series.getOption("find_zoom"),
            minValue=0,
            maxValue=100
        )
        if not confirmed:
            return

        self.series.setOption("find_zoom", z)
    
    def deleteDuplicateTraces(self):
        """Remove all duplicate traces from the series."""
        self.saveAllData()

        structure = [
            ["Overlap threshold:", ("float", 0.95, (0, 1))],
            [("check", ("check locked traces", True))]
        ]
        response, confirmed = QuickDialog.get(self, structure, "Remove duplicate traces")
        if not confirmed:
            return
        threshold = response[0]
        include_locked = response[1][0][1]
        
        removed = self.series.deleteDuplicateTraces(threshold, include_locked, self.field.series_states)

        if removed:
            message = "The following duplicate traces were removed:"
            for snum in removed:
                message += f"\nSection {snum}: " + ", ".join(removed[snum])
            TextWidget(self, message, title="Removed Traces")
        else:
            notify("No duplicate traces found.")

        self.field.reload()
        self.seriesModified(True)

    def addTo3D(self, names, ztraces=False):
        """Generate the 3D view for a list of objects.
        
            Params:
                obj_names (list): a list of object names
        """
        self.saveAllData()
        
        if not self.viewer or self.viewer.is_closed:
            self.viewer = CustomPlotter(self, names, ztraces)
        else:                
            if ztraces:
                self.viewer.addToScene([], names)
            else:
                self.viewer.addToScene(names, [])
        self.viewer.activateWindow()
        
    def removeFrom3D(self, obj_names, ztraces=False):
        """Remove objects from 3D viewer.
        
            Params:
                obj_names (list): a list of object names
        """
        self.saveAllData()
        if not self.viewer or self.viewer.is_closed:
            return
        
        if ztraces:
            self.viewer.removeZtraces(obj_names)
        else:
            self.viewer.removeObjects(obj_names)
        self.viewer.activateWindow()

    def exportAs3D(self, obj_names, export_type, ztraces=False):
        """Export 3D objects."""
        self.saveAllData()
        export_dir = FileDialog.get(
                "dir",
                self,
                "Select folder to export objects to",
            )
        if not export_dir: return
        export3DObjects(self.series, obj_names, export_dir, export_type)
    
    def toggleCuration(self):
        """Quick shortcut to toggle curation on/off for the tables."""
        self.field.table_manager.toggleCuration()
    
    def backspace(self):
        """Called when backspace is pressed."""
        w = self.focusWidget()
        if isinstance(w, CopyTableWidget):
            w.backspace()
        else:
            self.field.backspace()
    
    def undo(self, redo=False):
        """Perform an undo/redo action.
        
            Params:
                redo (bool): True if redo should be performed
        """
        self.saveAllData()
        can_3D, can_2D, linked = self.field.series_states.canUndo(redo=redo)
        def act2D():
            self.field.undoState(redo)
        def act3D():
            self.field.series_states.undoState(redo)
            self.field.reload()
            self.field.table_manager.recreateTables()

        # both 3D and 2D possible and they are linked
        if can_3D and can_2D and linked:
            mbox = QMessageBox(self)
            mbox.setWindowTitle("Redo" if redo else "Undo")
            mbox.setText("This action is linked to multiple sections.\nPlease select how you would like to proceed.")
            mbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            mbox.setButtonText(QMessageBox.Yes, "All sections")
            mbox.setButtonText(QMessageBox.No, "Only this section")
            mbox.setButtonText(QMessageBox.Cancel, "Cancel")
            response = mbox.exec()
            if response == QMessageBox.Yes:
                act3D()
            elif response == QMessageBox.No:
                act2D()
        # both 3D and 2D possible but they are not linked
        elif can_3D and can_2D and not linked:
            favor_3D = self.field.series_states.favor3D(redo=redo)
            if favor_3D:
                act3D()
            else:
                act2D()
        # only 3D possible
        elif can_3D:
            act3D()
        # only 2D possible
        elif can_2D:
            act2D()
    
    def copy(self):
        """Called when Ctrl+C is pressed."""
        w = self.focusWidget()
        if isinstance(w, CopyTableWidget):
            w.copy()
        else:
            self.field.copy()
        
    def pasteAttributesToPalette(self, use_shape=False):
        """Paste the attributes from the first clipboard trace to the selected palette button."""
        if not self.field.clipboard and not self.field.section.selected_traces:
            return
        elif not self.field.clipboard:
            trace = self.field.section.selected_traces[0]
        else:
            trace = self.field.clipboard[0]
        self.mouse_palette.pasteAttributesToButton(trace, use_shape)
    
    def displayShortcuts(self):
        """Display the shortcuts."""
        response, confirmed = ShortcutsDialog(self, self.series).exec()
        if not confirmed:
            return
        
        self.resetShortcuts(response)

    def openWebsite(self, site):
        """Open website in user's browser."""
        webbrowser.open(site)

    def copyCommit(self):
        """Copy current commit or repo."""
        clipboard = QApplication.clipboard()
        clipboard.setText(repo_info["commit"])

    def updateCurationFromHistory(self):
        """Update the series curation from the history."""
        self.field.series_states.addState()
        self.series.updateCurationFromHistory()
        self.field.table_manager.recreateTables()
        self.seriesModified()
    
    def allOptions(self):
        """Display the series options dialog."""
        confirmed = AllOptionsDialog(self, self.series).exec()
        if confirmed:
            self.field.generateView()
            self.mouse_palette.reset()
            self.setTheme(self.series.getOption("theme"))
    
    def optimizeBC(self, sections : list = None):
        """Optimize the brightness and contrast of the series.
        
            Params:
                sections (list): the list of section numbers
        """
        structure = [
            ["Mean (0-255):", ("int", 128, range(256))],
            ["Standard Devation:", ("float", 60)],
            [("radio", ("Use full image", True), ("Use current window view only", False))],
        ]
        response, confirmed = QuickDialog.get(self, structure, "Optimize Images")
        if not confirmed:
            return
        
        mean = response[0]
        std = response[1]
        full_image = response[2][0][1]
        
        if not noUndoWarning():
            return
        
        if sections is None:
            sections = list(self.series.sections.keys())
        
        optimizeSeriesBC(
            self.series, 
            mean,
            std,
            sections,
            None if full_image else self.series.window.copy()
        )
        self.field.reload()
        self.field.table_manager.updateSections(sections)
    
    def resetShortcuts(self, shortcuts_dict : dict = None):
        """Reset the shortcuts for the window.
        
            Params:
                shortcuts_dict: the action name : shortcut pairs (will use series opts if not provided)
        """
        if shortcuts_dict is None:
            shortcuts_dict = {}
            for k in Series.qsettings_defaults:
                if k.endswith("_act") and getattr(self, k):
                    shortcuts_dict[k] = self.series.getOption(k)
        
        for act_name, kbd in shortcuts_dict.items():
            getattr(self, act_name).setShortcut(kbd)
            self.series.setOption(act_name, kbd)
    
    def displayAbout(self):
        """Display the widget display information about the series."""
        # update the editors
        editors = self.series.getEditorsFromHistory()
        self.series.editors = self.series.editors.union(editors)

        AboutWidget(self, self.series)
    
    def exportTracePaletteCSV(self):
        """Export the current trace palette as CSV file."""
        name = self.series.palette_index[0]
        fp = FileDialog.get(
            "save",
            self,
            "Export Trace Palette",
            filter="*.csv",
            file_name=f"{name}.csv"
        )
        if not fp: return

        self.series.exportTracePaletteCSV(fp)
    
    def importTracePaletteCSV(self):
        """Import a trace palette from a CSV file."""
        fp = FileDialog.get(
            "file",
            self,
            "Import Trace Palette",
            filter="*.csv"
        )
        if not fp: return

        # get the new name of the palette
        name = os.path.basename(fp)
        name = name[:name.rfind(".")]

        i = 0
        while name in self.series.palette_traces:
            i += 1
            name = f"{name}-{i}"

        self.series.importTracePaletteCSV(fp, name)
        self.series.palette_index[0] = name

        self.mouse_palette.reset()

        notify(f"Trace palette '{name}' successfully imported.\n" +
               f"Press {self.series.getOption('modifytracepalette_act')} to view all palettes.")
    
    def notifyNewEditor(self):
        """Provide any relevant notifications to new editors."""
        if (
            not self.series.isWelcomeSeries() and
            self.series.user not in self.series.editors and
            len(self.series.getAlignments()) > 2
        ):
            notify(
                "Note: this series has multiple alignments.\n" + 
                f"Press {self.series.getOption('changealignment_act')} to view"
            )
    
    def editSeriesCodePattern(self):
        """Edit the regex pattern used to automatically detect series codes."""
        response, confirmed = QInputDialog.getText(
            self,
            "Series Code Pattern",
            "Enter the regex pattern for series codes:",
            text=self.series.getOption("series_code_pattern")
        )
        if not confirmed:
            return
        
        self.series.setOption("series_code_pattern", response)
    
    def setSeriesCode(self, cancelable=True):
        """Set the series code (ensure that user enters a valid series code)."""
        code_is_valid = False
        while not code_is_valid:
            structure = [
                ["The series code is a unique set of characters that identifies\n" + 
                "a specific series, regardless of the file name."],
                [" "],
                ["Series code:", (True, "text", self.series.code)]
            ]
            response, confirmed = QuickDialog.get(self, structure, "Series Code", cancelable=cancelable)
            if confirmed:
                self.series.code = response[0]
            
            code_is_valid = bool(self.series.code)

            if not code_is_valid:
                notify("Please enter a code for the series.")
    
    def setPaletteButtonFromObj(self, name : str):
        """Set the name for the selected palette button.
        
        (Used by the object list)
        
            Params:
                name (str): the name to set the button
        """
        # get the first instance of the object
        first_section = self.series.data.getStart(name)
        if first_section is None:
            return
        
        section = self.series.loadSection(first_section)
        obj_trace = section.contours[name][0].copy()

        pname, i = self.series.palette_index
        trace = self.series.palette_traces[pname][i]
        trace.name = name
        trace.color = obj_trace.color
        trace.fill_mode = obj_trace.fill_mode
        self.mouse_palette.modifyPaletteButton(i, trace)
    
    def load3DScene(self):
        """Load a 3D scene."""
        load_fp = FileDialog.get(
            "file",
            self,
            "Load 3D Scene",
            "JSON file (*.json)"
        )
        if not load_fp:
            return
        
        if not self.viewer or self.viewer.is_closed:
            self.viewer = CustomPlotter(self, load_fp=load_fp)
        else:
            self.viewer.loadScene(load_fp)
        
        self.viewer.setFocus()
    
    def setTheme(self, new_theme=None):
        """Change the theme."""
        if new_theme is None:
            theme = self.series.getOption("theme")
            structure = [
                ["Theme:"],
                [("radio", ("Default", theme=="default"), ("Dark", theme=="qdark"))]
            ]
            response, confirmed = QuickDialog.get(
                self, structure, "Theme"
            )
            if not confirmed:
                return
            
            if response[0][0][1]:
                new_theme = "default"
            elif response[0][1][1]:
                new_theme = "qdark"
            else:
                return
        
        app = QApplication.instance()
        if new_theme == "default":
            self.series.setOption("theme", "default")
            app.setStyleSheet("")
            app.setPalette(app.style().standardPalette())
        elif new_theme == "qdark":
            try:
                import qdarkstyle
            except:
                notify("Unable to import dark theme.")
                return
            self.series.setOption("theme", "qdark")
            app.setStyleSheet(
                qdarkstyle.load_stylesheet_pyside6() + 
                qdark_addon
            )
    
    def setHost(self):
        """Set the host of the selected object(s) in the field or on the table."""
        w = self.focusWidget()
        if isinstance(w, ObjectTableWidget):
            w.setHosts()
        else:
            self.field.setHosts()
    
    def addToRecentSeries(self, series_fp : str = None):
        """Add a series to the recently opened series list."""
        if series_fp is None:
            if self.series.isWelcomeSeries():
                return
            series_fp = self.series.jser_fp
        
        opened = self.series.getOption("recently_opened_series")

        # remove redundant filepaths
        while series_fp in opened:
            opened.remove(series_fp)
        
        opened.insert(0, series_fp)

        # limit to ten items
        if len(opened) > 10:
            opened.pop()
                
        self.series.setOption("recently_opened_series", opened)
    
    def importFromSeries(self):
        """Import from another series."""
        jser_fp = FileDialog.get(
            "file",
            self,
            "Select Series",
            filter="*.jser"
        )
        if not jser_fp: return  # exit function if user does not provide series

        self.saveAllData()

        # open the other series
        o_series = Series.openJser(jser_fp)

        # check the manigifcations
        if not checkMag(self.series, o_series):
            o_series.close()
            return
        
        response, confirmed = ImportSeriesDialog(self, self.series, o_series).exec()
        if not confirmed or not response:
            o_series.close()
            return
        
        if "traces" in response:
            (
                srange,
                regex_filters,
                threshold,
                flag_conflicts,
                check_history,
                import_obj_attrs,
                keep_above,
                keep_below,
            ) = tuple(response["traces"])

            self.series.importTraces(
                o_series, 
                srange, 
                regex_filters, 
                threshold, 
                flag_conflicts, 
                check_history,
                import_obj_attrs,
                keep_above,
                keep_below, 
                self.field.series_states
            )
        
        if "z-traces" in response:
            regex_filters = response["z-traces"][0]
            import_attrs = response["z-traces"][1][0][1]
            self.series.importZtraces(
                o_series, 
                regex_filters,
                import_attrs,
                series_states=self.field.series_states
            )
            
        if "flags" in response:
            srange = (
                response["flags"][0],
                response["flags"][1] + 1
            )
            self.series.importFlags(
                o_series, 
                srange,
                self.field.series_states
            )
        
        if "attributes" in response:
            bools = [b for n, b in response["attributes"][0]]
            if bools[0]:
                self.series.importObjectGroups(o_series)
            if bools[1]:
                self.series.importHostTree(o_series)
            if bools[2]:
                self.series.importUserCols(o_series)
            if bools[3]:
                self.series.importZtraceGroups(o_series)
            if bools[4]:
                self.series.importObjAttrs(o_series)
        
        if "alignments" in response:
            import_as = response["alignments"]
            self.series.importTransforms(
                o_series,
                import_as,
                self.field.series_states
            )
            self.createContextMenus()

        if "palettes" in response:
            import_as = response["palettes"]
            self.series.importPalettes(  # cannot be undone
                o_series,
                import_as
            )

        if "brightness/contrast profiles" in response:
            print("wowze")
            import_as = response["brightness/contrast profiles"]
            self.series.importBC(  # cannot be undone
                o_series,
                import_as
            )

        # close other series
        o_series.close()

        # refresh the data and lists
        self.field.reload()
        self.field.table_manager.refresh()

        notify("Import successful.")
        
    def restart(self):
        self.restart_mainwindow = True

        # Clear console
        
        if os.name == 'nt':  # Windows
            _ = os.system('cls')
        
        else:  # Mac and Linux
            _ = os.system('clear')
        
        self.close()
            
    def closeEvent(self, event):
        """Save all data to files when the user exits."""
        response = self.saveToJser(notify=True, close=True)
        if response == "cancel":
            event.ignore()
            return
        if self.viewer and not self.viewer.is_closed:
            self.viewer.close()
        event.accept()

qdark_addon = """
QPushButton {border: 1px solid transparent}
QComboBox {padding-right: 40px}
"""
# QTableWidget:item:alternate {background-color: #222C36;}  # removed because it overrides the background color of qtablewidgetitems
