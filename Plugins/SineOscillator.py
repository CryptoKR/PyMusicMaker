import numpy as np
import pyaudio
import wx
import wx.lib.agw.knobctrl as KC

from Plugins.Oscillator.OscSound import OscSound
from bin.plugin import PluginBase, PluginType


class SineOscillator(PluginBase):
    icon = wx.Bitmap('Plugins\icons\sine.png')
    pluginType = PluginType.SOUNDGENERATOR

    def __init__(self, frameParent, **kwargs):
        window_title = self.window_title()
        super(SineOscillator, self).__init__(frameParent, PluginType.SOUNDGENERATOR
                                             , wx.Bitmap('Plugins\Oscillator\Graphics\icon.png')
                                             , name=kwargs.get('pluginName', window_title)
                                             , **kwargs)

        self.oscSound = None
        self.instrumentsPanel = None

        self.knob1 = KC.KnobCtrl(self, -1, size=(100, 100))
        self.knob2 = KC.KnobCtrl(self, -1, size=(100, 100))
        self.knob3 = KC.KnobCtrl(self, -1, size=(100, 100))

        # noise
        self.knob1.SetTags(range(0, 101, 5))
        self.knob1.SetAngularRange(-45, 225)
        self.knob1.SetValue(kwargs.get('knob1Value', 0))

        # fading
        self.knob2.SetTags(range(0, 101, 5))
        self.knob2.SetAngularRange(-45, 225)
        self.knob2.SetValue(kwargs.get('knob2Value', 0))

        # damping
        self.knob3.SetTags(range(0, 101, 5))
        self.knob3.SetAngularRange(-45, 225)
        self.knob3.SetValue(kwargs.get('knob3Value', 50))

        self.knobtracker1 = wx.StaticText(self, -1, "Value = " + str(self.knob1.GetValue()))
        self.knobtracker2 = wx.StaticText(self, -1, "Value = " + str(self.knob2.GetValue()))
        self.knobtracker3 = wx.StaticText(self, -1, "Value = " + str(self.knob3.GetValue() - 50))

        self.knob1BeforeSave = self.knob1.GetValue()
        self.knob2BeforeSave = self.knob2.GetValue()
        self.knob3BeforeSave = self.knob3.GetValue()

        leftknobsizer_staticbox = wx.StaticBox(self, -1, "Noise")
        middleknobsizer_staticbox = wx.StaticBox(self, -1, "Fading")
        tightknobsizer_staticbox = wx.StaticBox(self, -1, "Damping")

        self.base_menu = self.base_top_window_menu_sizer_getter(
            frameParent, PluginType.SOUNDGENERATOR, SineOscillator.icon, **kwargs)

        panelsizer = wx.BoxSizer(wx.VERTICAL)
        menusizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomsizer = wx.BoxSizer(wx.HORIZONTAL)
        leftknobsizer = wx.StaticBoxSizer(leftknobsizer_staticbox, wx.VERTICAL)
        middleknobsizer = wx.StaticBoxSizer(middleknobsizer_staticbox, wx.VERTICAL)
        rightknobsizer = wx.StaticBoxSizer(tightknobsizer_staticbox, wx.VERTICAL)

        menusizer.Add(self.base_menu, 1, wx.ALL | wx.EXPAND, 5)
        panelsizer.Add(menusizer, 0, wx.EXPAND | wx.ALL)

        leftknobsizer.Add(self.knob1, 1, wx.ALL | wx.EXPAND, 5)
        leftknobsizer.Add(self.knobtracker1, 0, wx.ALL, 5)
        bottomsizer.Add(leftknobsizer, 1, wx.ALL | wx.EXPAND, 5)
        middleknobsizer.Add(self.knob2, 1, wx.ALL | wx.EXPAND, 5)
        middleknobsizer.Add(self.knobtracker2, 0, wx.ALL, 5)
        bottomsizer.Add(middleknobsizer, 1, wx.ALL | wx.EXPAND, 5)
        rightknobsizer.Add(self.knob3, 1, wx.ALL | wx.EXPAND, 5)
        rightknobsizer.Add(self.knobtracker3, 0, wx.ALL, 5)
        bottomsizer.Add(rightknobsizer, 1, wx.ALL | wx.EXPAND, 5)
        panelsizer.Add(bottomsizer, 1, wx.EXPAND | wx.ALL, 20)

        self.SetSizer(panelsizer)
        panelsizer.Layout()
        self.sound = None

        self.Bind(KC.EVT_KC_ANGLE_CHANGED, self.on_angle_changed1, self.knob1)
        self.Bind(KC.EVT_KC_ANGLE_CHANGED, self.on_angle_changed2, self.knob2)
        self.Bind(KC.EVT_KC_ANGLE_CHANGED, self.on_angle_changed3, self.knob3)

        if self.isSound:
            self.win.Bind(wx.EVT_CLOSE, self.on_exit_app)
            self.Bind(wx.EVT_WINDOW_DESTROY, self.on_close)
            self.Bind(wx.EVT_BUTTON, self.on_modify)
        else:
            self.Bind(wx.EVT_BUTTON, self.on_save)

    def window_title(self):
        return "Sine Oscillator"

    def set_osc(self):
        self.oscSound = OscSound()

    def set_instruments_panel_window(self, instrumentsPanel):
        self.instrumentsPanel = instrumentsPanel

    def on_exit_app(self, event):
        self.show_window(False)

    def on_char(self, event):
        if event.GetUnicodeKey() == wx.WXK_SPACE:
            p = pyaudio.PyAudio()
            # for paFloat32 sample values must be in range [-1.0, 1.0]
            stream = p.open(format=pyaudio.paFloat32,
                            channels=1,
                            rate=44100,
                            output=True,
                            frames_per_buffer=44100)

            stream.start_stream()
            stream.write(np.array([x for x in self.generate_sound()]).astype(np.float32))
            stream.stop_stream()
            stream.close()

            # close PyAudio (7)
            p.terminate()

        event.Skip()

    def generate_sound(self, frequency=440, duration=1.0, sample_rate=44000, bits=16, framesInterval=1024, bpm=128):
        if not self.oscSound:
            self.set_osc()
        self.oscSound.update_noise_parameter(self.knob1.GetValue())
        self.oscSound.update_fading_parameter(self.knob2.GetValue())
        self.oscSound.update_damping_parameter(self.knob3.GetValue() - 50)
        return self.oscSound.sound_generator(frequency=frequency, duration=duration, sample_rate=sample_rate, bits=bits
                                             , framesInterval=1024, bpm=128)

    def get_color(self):
        return self.instrumentColorPicker.GetColour()

    def on_close(self, event):
        self.knob1.SetValue(self.knob1BeforeSave)
        self.knob2.SetValue(self.knob2BeforeSave)
        self.knob3.SetValue(self.knob3BeforeSave)

        print('closing')

    def on_modify(self, event):
        self.knob1BeforeSave = self.knob1.GetValue()
        self.knob2BeforeSave = self.knob2.GetValue()
        self.knob3BeforeSave = self.knob3.GetValue()

    def get_serialization_data(self):
        return ('SineOscillator', {'isSound': True,
                                   'knob1Value': self.knob1.GetValue(),
                                   'knob2Value': self.knob2.GetValue(),
                                   'knob3Value': self.knob3.GetValue(),
                                   'colourRed': self.colourRed,
                                   'colourGreen': self.colourGreen,
                                   'colourBlue': self.colourBlue,
                                   'colourAlpha': self.colourAlpha,
                                   'pluginName': self.instrumentNameTextCtrl.GetValue()})

    def on_save(self, event):
        self.instrumentsPanel.add_instrument(SineOscillator, self.get_serialization_data()[1])

    def on_angle_changed1(self, event):

        value = event.GetValue()
        self.knobtracker1.SetLabel("Value = " + str(value))
        self.knobtracker1.Refresh()

    def on_angle_changed2(self, event):

        value = event.GetValue()
        self.knobtracker2.SetLabel("Value = " + str(value))
        self.knobtracker2.Refresh()

    def on_angle_changed3(self, event):

        value = event.GetValue()
        self.knobtracker3.SetLabel("Value = " + str(value - 50))
        self.knobtracker3.Refresh()