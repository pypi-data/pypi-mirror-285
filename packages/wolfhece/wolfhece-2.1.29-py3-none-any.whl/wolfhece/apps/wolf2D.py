import wx

def main():
    ex = wx.App()

    from .splashscreen import WolfLauncher
    first_launch = WolfLauncher(play_sound=False)

    from ..PyGui import Wolf2DModel

    mydro=Wolf2DModel()
    ex.MainLoop()

if __name__=='__main__':
    main()
