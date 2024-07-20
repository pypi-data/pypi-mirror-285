import wx

from ..PyTranslate import _

def main(strmydir=''):
    ex = wx.App()

    from .splashscreen import WolfLauncher
    first_launch = WolfLauncher(play_sound=False)

    from ..PyGui import HydrologyModel

    exLocale = wx.Locale()
    exLocale.Init(wx.LANGUAGE_ENGLISH)
    mydro=HydrologyModel()
    ex.MainLoop()

if __name__=='__main__':
    main()