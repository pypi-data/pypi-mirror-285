import wx
import logging


from . import Parser, Expression

class Calculator(wx.Frame):
 
    def __init__(self, mapviewer=None):
        
        from ..PyDraw import WolfMapViewer, draw_type, WolfArray

        super(Calculator, self).__init__(None, title='Calculator', size=(500, 300))

        self._memory = {}

        self._parser = Parser()
        self._parsed_command:Expression = None

        self._mapviewer:WolfMapViewer = mapviewer
        self._last_command = None

        keys = '()C<789/456*123-.0=+'
        self._btns:list[list[wx.Button]] = [[wx.Button(self, label=c) for c in keys[i:i+4]] for i in range(0,20,4)]

        self._disp = wx.TextCtrl(self, style=wx.TE_RIGHT|wx.TE_RICH2|wx.TE_MULTILINE)

        self._comment = wx.TextCtrl(self, style=wx.TE_RIGHT|wx.TE_RICH2|wx.TE_MULTILINE)
        self.memory   = wx.TextCtrl(self, style=wx.TE_RIGHT|wx.TE_RICH2|wx.TE_MULTILINE)
        self.btn_reset_memory = wx.Button(self, label='Reset Memory')
        
        self.Bind(wx.EVT_BUTTON, lambda v: self.bt_press(v.EventObject.Label))

        self._btns[-1][-2].SetDefault() 

        self.Bind(wx.EVT_CHAR_HOOK, self.char_press)
        self.btn_reset_memory.Bind(wx.EVT_BUTTON, lambda v: self._memory.clear())
        
        self.SetSizer(self.pack([self._disp] + [self.pack(x) for x in self._btns] + [self.pack([self._comment, self.btn_reset_memory, self.memory])], orient=wx.VERTICAL))

        self._disp.SetFocus()

        self.Show()

    def pack(self, items, orient=wx.HORIZONTAL):
        """ Pack items in a sizer """
        sizer = wx.BoxSizer(orient)
        sizer.AddMany((i, 1, wx.EXPAND|wx.ALL, 0) for i in items)
        return sizer
    
    @property
    def command(self) -> str:
        return self._disp.Value  
    
    @command.setter
    def command(self, value):
        self._disp.Value = str(value)
        self._disp.SetInsertionPointEnd()

    @property
    def comment(self) -> str:
        return self._comment.Value
    
    @comment.setter
    def comment(self, value):
        self._comment.Value = str(value)

    def check_command(self) -> bool:
        """ Check if the command is valid """        
        
        from ..PyDraw import draw_type
        
        if '\n' in self.command:
            self.evaluate_multilines()
            return False
        else:

            self._parsed_command = self._parser.parse(self.command)

            symbols = self._parsed_command.symbols()
            variables = self._parsed_command.variables()
            functions = self._parsed_command.functions

            if self._mapviewer is not None:
                id_arrays = self._mapviewer.get_list_keys(drawing_type=draw_type.ARRAYS,
                                                       checked_state=None)
                
                for id_array in id_arrays:
                    self._memory[id_array] = self._mapviewer.get_obj_from_id(id_array, drawtype=draw_type.ARRAYS)

            if len(variables) > 0:
                for var in variables:
                    if var not in self._memory:
                        self.comment = f'Variable {var} not defined'
                        return False

            return True

    def evaluate_multilines(self):
        """ Evaluate multiline commands """

        self._last_command = self.command

        commands = self.command.split('\n')

        ret = []
        for command in commands:
            self.command = command
            ret.append(str(self.evaluate(mem_last_command=False)))

        self.command = '\n'.join(ret)


    def evaluate(self, mem_last_command=True):
        """ Evaluate the command """
        from ..PyDraw import WolfArray, draw_type
        
        if mem_last_command:
            self._last_command = self.command

        ret = self.check_command()
        
        if ret:
            args = {var:self._memory[var] for var in self._parsed_command.variables()}
            res = self._parsed_command.evaluate(args)

            if isinstance(res, dict):
                
                comment = 'Storing\n'
                
                for key, value in res.items():
                    self._memory[key] = value
                    comment += f'{key} = {value}\n'
                
                self.comment = comment
                self.command = ''
            
            elif isinstance(res, str|int|float):
                self.command = res

            elif isinstance(res, WolfArray):

                ids = self._mapviewer.get_list_keys(drawing_type=draw_type.ARRAYS, checked_state=None)
                id = self.command
                while id in ids:
                    id += '_'
                
                self._mapviewer.add_object('array', newobj=res, id = id)
                self.command = ''
                
            return res

    def char_press(self, e:wx.KeyEvent):
        """ Handle key press """

        egal = '='
        egal_code = [ord(egal)]

        unicodekey = e.GetUnicodeKey()
        key = e.GetKeyCode()
 
        ctrl = e.ControlDown()
        alt  = e.AltDown()
        shift= e.ShiftDown()

        if unicodekey in egal_code:
            if not shift : 
                self.evaluate()
                return

        e.Skip()

    def bt_press(self, key):
        """ Handle button press  """
        if   key == 'C': self._disp.Value = ''
        elif key == '<': self.command =self._last_command
        elif key == '=': self.evaluate()
        else           : self._disp.Value += key
 