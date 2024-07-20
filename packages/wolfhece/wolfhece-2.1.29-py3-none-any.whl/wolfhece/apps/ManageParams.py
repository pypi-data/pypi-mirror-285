import wx

from ..PyTranslate import _

def main():
    ex = wx.App()

    from .splashscreen import WolfLauncher
    first_launch = WolfLauncher(play_sound=False)

    from ..PyParams import Wolf_Param

    frame = Wolf_Param(None,"Params")
    ex.MainLoop()

if __name__=="__main__":
    main()