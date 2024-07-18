from .acceptability import Base_data_creation, Database_to_raster, Vulnerability, Acceptability
from .func import Accept_Manager

import wx
import logging
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar2Wx
class AcceptabilityGui(wx.Frame):

    def __init__(self, parent=None, width=1024, height=500):

        super(wx.Frame, self).__init__(parent, title='Acceptability', size=(width, height))

        self._manager = None
        self._mapviewer = None

        self.InitUI()

    @property
    def mapviewer(self):
        return self._mapviewer
    
    @mapviewer.setter
    def mapviewer(self, value):
        from ..PyDraw import WolfMapViewer

        if not isinstance(value, WolfMapViewer):
            raise TypeError("The mapviewer must be a WolfMapViewer")
        
        self._mapviewer = value
    
    def InitUI(self):

        sizer_hor_main = wx.BoxSizer(wx.HORIZONTAL)

        sizer_vert1 = wx.BoxSizer(wx.VERTICAL)

        sizer_hor1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_hor1_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_hor2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_hor3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_hor4 = wx.BoxSizer(wx.HORIZONTAL)

        panel = wx.Panel(self)

        self._but_maindir = wx.Button(panel, label='Main Directory')
        self._but_maindir.Bind(wx.EVT_BUTTON, self.OnMainDir)

        self._listbox_studyarea = wx.ListBox(panel, choices=[], style=wx.LB_SINGLE)
        self._listbox_studyarea.Bind(wx.EVT_LISTBOX, self.OnStudyArea)
        self._listbox_studyarea.SetToolTip("Choose the study area")

        self._listbox_scenario = wx.ListBox(panel, choices=[], style=wx.LB_SINGLE)
        self._listbox_scenario.Bind(wx.EVT_LISTBOX, self.OnScenario)
        self._listbox_scenario.SetToolTip("Choose the scenario")

        sizer_hor1.Add(self._but_maindir, 2, wx.ALL | wx.EXPAND, 0)
        sizer_hor1.Add(self._listbox_studyarea, 1, wx.ALL | wx.EXPAND, 0)
        sizer_hor1.Add(self._listbox_scenario, 1, wx.ALL | wx.EXPAND, 0)

        self._but_checkfiles = wx.Button(panel, label='Check Files')
        self._but_checkfiles.Bind(wx.EVT_BUTTON, self.OnCheckFiles)

        sizer_hor1_1.Add(self._but_checkfiles, 1, wx.ALL | wx.EXPAND, 0)

        self._but_creation = wx.Button(panel, label='DataBase Creation')
        self._but_creation.Bind(wx.EVT_BUTTON, self.OnCreation)

        self._but_vulnerability = wx.Button(panel, label='Vulnerability')
        self._but_vulnerability.Bind(wx.EVT_BUTTON, self.OnVulnerability)

        self._but_vulnerability1 = wx.Button(panel, label='only Phase 1')
        self._but_vulnerability1.Bind(wx.EVT_BUTTON, self.OnVulnerability1)

        self._but_vulnerability2 = wx.Button(panel, label='only Phase 2')
        self._but_vulnerability2.Bind(wx.EVT_BUTTON, self.OnVulnerability2)

        self._but_vulnerability3 = wx.Button(panel, label='only Phase 3')
        self._but_vulnerability3.Bind(wx.EVT_BUTTON, self.OnVulnerability3)

        self._but_acceptability = wx.Button(panel, label='Acceptability')
        self._but_acceptability.Bind(wx.EVT_BUTTON, self.OnAcceptability)

        sizer_hor2.Add(self._but_creation, 1, wx.ALL | wx.EXPAND, 0)

        sizer_hor3.Add(self._but_vulnerability, 3, wx.ALL | wx.EXPAND, 0)
        sizer_hor3.Add(self._but_vulnerability1, 1, wx.ALL | wx.EXPAND, 0)
        sizer_hor3.Add(self._but_vulnerability2, 1, wx.ALL | wx.EXPAND, 0)
        sizer_hor3.Add(self._but_vulnerability3, 1, wx.ALL | wx.EXPAND, 0)

        sizer_hor4.Add(self._but_acceptability, 1, wx.ALL | wx.EXPAND, 0)

        sizer_vert1.Add(sizer_hor1, 2, wx.EXPAND, 0)
        sizer_vert1.Add(sizer_hor1_1, 1, wx.EXPAND, 0)
        sizer_vert1.Add(sizer_hor2, 1, wx.EXPAND, 0)
        sizer_vert1.Add(sizer_hor3, 1, wx.EXPAND, 0)
        sizer_vert1.Add(sizer_hor4, 1, wx.EXPAND, 0)

        # ------

        sizer_vert2 = wx.BoxSizer(wx.VERTICAL)

        self._listbox_returnperiods = wx.ListBox(panel, choices=[], style=wx.LB_SINGLE)
        self._listbox_returnperiods.SetToolTip("All available return periods in the database")

        self._listbox_sims = wx.ListBox(panel, choices=[], style=wx.LB_SINGLE)
        self._listbox_sims.SetToolTip("All available simulations in the database")

        self._listbox_sims.Bind(wx.EVT_LISTBOX, self.OnSims)
        self._listbox_sims.Bind(wx.EVT_LISTBOX_DCLICK, self.OnSimsDBLClick)

        sizer_vert2.Add(self._listbox_returnperiods, 1, wx.EXPAND, 0)
        sizer_vert2.Add(self._listbox_sims, 1, wx.EXPAND, 0)

        # ------

        sizer_vert3 = wx.BoxSizer(wx.VERTICAL)
        
        matplotlib.use('WXAgg')

        self._figure = Figure(figsize=(5, 4), dpi=100)
        self._axes = self._figure.add_subplot(111)
        self._canvas = FigureCanvas(panel, -1, self._figure)
        self._toolbar = NavigationToolbar2Wx(self._canvas)
        self._toolbar.Realize()

        sizer_vert3.Add(self._canvas, 1, wx.EXPAND, 0)
        sizer_vert3.Add(self._toolbar, 0, wx.LEFT | wx.EXPAND, 0)

        # ------
        
        sizer_hor_main.Add(sizer_vert1, 1, wx.EXPAND, 0)
        sizer_hor_main.Add(sizer_vert2, 1, wx.EXPAND, 0)
        sizer_hor_main.Add(sizer_vert3, 1, wx.EXPAND, 0)
        
        panel.SetSizer(sizer_hor_main)
        panel.Layout()

        self._but_acceptability.Enable(False)
        self._but_vulnerability.Enable(False)
        self._but_vulnerability1.Enable(False)
        self._but_vulnerability2.Enable(False)
        self._but_vulnerability3.Enable(False)
        self._but_creation.Enable(False)

    def OnSims(self, e:wx.ListEvent):
        """ Load sim into the mapviewer """
        pass

    def OnSimsDBLClick(self, e:wx.ListEvent):
        """ Load sim into the mapviewer """
        if self.mapviewer is None:
            return
        
        from ..PyDraw import draw_type

        idx_sim = e.GetSelection()            
        tmppath = self._manager.get_filepath_for_return_period(self._manager.get_return_periods()[idx_sim])
        if tmppath.stem not in self.mapviewer.get_list_keys(drawing_type=draw_type.ARRAYS):
            self.mapviewer.add_object('array', filename=str(tmppath), id=tmppath.stem)
            self.mapviewer.Refresh()

    def OnCheckFiles(self, e):
        """ Check the files """

        if self._manager is None:
            logging.error("No main directory selected -- Nothing to check")
            return

        ret = self._manager.check_files()

        if ret == "":
            logging.info("All files are present")
            with wx.MessageDialog(self, "All files are present in the INPUT directory", "Info", wx.OK | wx.ICON_INFORMATION) as dlg:
                dlg.ShowModal()
        else:
            logging.error(f"Missing files: {ret}")
            with wx.MessageDialog(self, f"Missing files: \n{ret}", "Error", wx.OK | wx.ICON_ERROR) as dlg:
                dlg.ShowModal()

    def OnMainDir(self, e):

        with wx.DirDialog(self, "Choose the main directory containing the data:",
                          style=wx.DD_DEFAULT_STYLE
                          ) as dlg:
            
            if dlg.ShowModal() == wx.ID_OK:
                self._manager = Accept_Manager(dlg.GetPath(), Study_area=None)

                self._listbox_studyarea.Clear()
                self._listbox_studyarea.InsertItems(self._manager.get_list_studyareas(), 0)

                self._listbox_scenario.Clear()

                ret = self._manager.check_files()

                if ret == "":
                    logging.info("All files are present")
                    self._but_acceptability.Enable(True)
                    self._but_vulnerability.Enable(True)
                    self._but_vulnerability1.Enable(True)
                    self._but_vulnerability2.Enable(True)
                    self._but_vulnerability3.Enable(True)
                    self._but_creation.Enable(True)
                else:
                    logging.error(f"Missing files: {ret}")
                    with wx.MessageDialog(self, f"Missing files: \n{ret}", "Error", wx.OK | wx.ICON_ERROR) as dlg:
                        dlg.ShowModal()

            else:
                return
            
    def OnStudyArea(self, e):
        """ Change the study area """

        if self._manager is None:
            return

        study_area:str = self._manager.get_list_studyareas(with_suffix=True)[e.GetSelection()]
        self._manager.change_studyarea(study_area)

        self._listbox_scenario.Clear()
        self._listbox_scenario.InsertItems(self._manager.get_list_scenarios(), 0)

        if self.mapviewer is not None:
            tmp_path = self._manager.IN_STUDY_AREA / study_area
            
            from ..PyDraw import draw_type
            if not tmp_path.stem in self.mapviewer.get_list_keys(drawing_type=draw_type.VECTORS):
                self.mapviewer.add_object('vector', filename=str(tmp_path), id=tmp_path.stem)
                self.mapviewer.Refresh()

    def OnScenario(self, e):
        """ Change the scenario """

        if self._manager is None:
            return

        scenario = self._manager.get_list_scenarios()[e.GetSelection()]
        self._manager.change_scenario(scenario)

        self._listbox_returnperiods.Clear()
        rt = self._manager.get_return_periods()
        self._listbox_returnperiods.InsertItems([str(crt) for crt in rt],0)

        self._listbox_sims.Clear()
        sims = [str(self._manager.get_filepath_for_return_period(currt).name) for currt in rt]
        self._listbox_sims.InsertItems(sims, 0)

        ponds = self._manager.get_ponderations()

        self._axes.clear()
        ponds.plot(ax=self._axes, kind='bar')
        self._canvas.draw()

    def OnCreation(self, e):
        """ Create the database """

        if self._manager is None:
            return

        Base_data_creation(self._manager.main_dir, number_procs=1)

    def OnVulnerability(self, e):
        """ Run the vulnerability """

        if self._manager is None:
            return

        Vulnerability(self._manager.main_dir, 
                      scenario=self._manager.scenario,
                      Study_area=self._manager.Study_area,
                      steps=[1,2,3])
        
    def OnVulnerability1(self, e):
        """ Run the vulnerability - Phase 1"""

        if self._manager is None:
            return

        Vulnerability(self._manager.main_dir, 
                      scenario=self._manager.scenario,
                      Study_area=self._manager.Study_area,
                      steps=[1])
        
    def OnVulnerability2(self, e):
        """ Run the vulnerability - Phase 2"""

        if self._manager is None:
            return

        Vulnerability(self._manager.main_dir, 
                      scenario=self._manager.scenario,
                      Study_area=self._manager.Study_area,
                      steps=[2])
        
    def OnVulnerability3(self, e):
        """ Run the vulnerability - Phase 3"""

        if self._manager is None:
            return

        Vulnerability(self._manager.main_dir, 
                      scenario=self._manager.scenario,
                      Study_area=self._manager.Study_area,
                      steps=[3])
        
    def OnAcceptability(self, e):
        """ Run the acceptability """

        if self._manager is None:
            return

        Acceptability(self._manager.main_dir, 
                      scenario=self._manager.scenario,
                      Study_area=self._manager.Study_area)