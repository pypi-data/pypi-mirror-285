import wx

from ..PyTranslate import _

def main():
    app = wx.App()

    from .splashscreen import WolfLauncher
    first_launch = WolfLauncher(play_sound=False)

    from ..hydrology.Optimisation import Optimisation

    myOpti = Optimisation()
    myOpti.Show()
    app.MainLoop()
    print("That's all folks! ")

if __name__=='__main__':
    main()
