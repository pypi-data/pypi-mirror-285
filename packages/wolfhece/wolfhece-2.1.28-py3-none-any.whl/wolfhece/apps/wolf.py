import wx
from ..PyTranslate import _

def main():
    ex = wx.App()

    from .splashscreen import WolfLauncher
    first_launch = WolfLauncher(play_sound=False)

    from ..PyGui import MapManager

    mywolf=MapManager()
    ex.MainLoop()

if __name__=='__main__':
    main()