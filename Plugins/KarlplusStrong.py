import pyaudio
import wx
import numpy as np
from Plugins.Oscillator.SawtoothSound import SawToothSound
from Plugins.Oscillator.SquareSound import SquareSound
from Plugins.SineOscillator import SineOscillator
from bin.plugin import PluginBase, PluginType


class KarlplusStrong(PluginBase):
    icon = wx.Bitmap('Plugins\icons\guitar.png')
    pluginType = PluginType.SOUNDGENERATOR

    def __init__(self, frameParent, **kwargs):
        window_title = self.window_title()
        super(KarlplusStrong, self).__init__(frameParent, PluginType.SOUNDGENERATOR
                                             , wx.Bitmap('Plugins\Oscillator\Graphics\icon.png')
                                             , name=kwargs.get('pluginName', window_title))

    def set_osc(self):
        self.oscSound = SawToothSound()

    def window_title(self):
        return "Karlplus Strong"

    def on_save(self, event):
        self.instrumentsPanel.add_instrument(KarlplusStrong, self.get_serialization_data()[1])

    def get_serialization_data(self):
        return ('KarlplusStrong', {'pluginName': self.instrumentNameTextCtrl.GetValue()})


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
        return self.sound_generator(frequency=frequency, duration=duration, sample_rate=sample_rate, bits=bits
                                             , framesInterval=1024, bpm=128)

    def sound_generator(self, frequency=440, duration=1.0, sample_rate=44100, bits=16, framesInterval=1024, bpm=128):
        n_samples = int(round(duration * sample_rate))

        wavetable_size = int(sample_rate // (frequency / 2))
        wavetable = (2 * np.random.randint(0, 2, wavetable_size) - 1).astype(np.float32)

        samples = []
        current_sample = 0
        previous_value = 0
        while len(samples) < n_samples:
            wavetable[current_sample] = 0.5 * (wavetable[current_sample] + previous_value)
            samples.append(wavetable[current_sample])
            previous_value = samples[-1]
            current_sample += 1
            current_sample = current_sample % wavetable.size
            yield wavetable[current_sample]
