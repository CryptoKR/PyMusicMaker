import wx
from wx.lib.masked import NumCtrl

iconsBase = 'Icons/typicons/png/'


class PlayMenu:
    def __init__(self, parent, max_icons_size=(25, 25)):
        self.parent = parent
        toolbar = parent.CreateToolBar()
        self.play_menu = toolbar.AddTool(wx.ID_ANY, 'Play', shortHelp='Play',
                                         bitmap=scale_image(iconsBase + 'play-button-1.png',
                                                            max_icons_size=max_icons_size))

        self.pause_menu = toolbar.AddTool(wx.ID_ANY, 'Stop', shortHelp='Pause',
                                          bitmap=scale_image(iconsBase + 'pause-button.png',
                                                             max_icons_size=max_icons_size))
        toolbar.Realize()

        self.bpm = NumCtrl(toolbar, value=128, pos=(80, 3), size=(50, 25), min=50, max=250)

    def bind_play_button(self, event_function):
        self.parent.Bind(wx.EVT_MENU, event_function, self.play_menu)

    def bind_stop_button(self, event_function):
        self.parent.Bind(wx.EVT_MENU, event_function, self.pause_menu)

    def unbind_play_button(self, event_function):
        self.parent.Unbind(event=wx.EVT_MENU, handler=event_function, source=self.play_menu)

    def unbind_stop_button(self, event_function):
        self.parent.Unbind(event=wx.EVT_MENU, handler=event_function, source=self.pause_menu)


def scale_image(image_dir, max_icons_size=(25, 25)):
    return wx.Bitmap(
        wx.Bitmap(image_dir).ConvertToImage().Scale(max_icons_size[0], max_icons_size[1], wx.IMAGE_QUALITY_HIGH))
