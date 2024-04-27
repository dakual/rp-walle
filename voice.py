from vosk import Model, KaldiRecognizer
import sys
import json
import os
import sounddevice as sd
import queue
# import pyaudio


wmap = {
  "hey robot":         ["radio_on"],
  "hey sen":           ["radio_on"],
  "sağa dön":          ["radio_off"],
  "sola dön":          ["vol_up"],
  "ileri git":         ["vol_down"],
  "geri git":          ["radio_play_channel", "nr=1"],
  "dur":               ["sys_stop"],
  "senin adın ne":     ["_quit"],
  "oyun oynayalım mı": ["_set_cmd_mode"]
  }

q = queue.Queue()

def callback(indata, frames, time, status):
  if status:
    print(status, file=sys.stderr)
  q.put(bytes(indata))
    

dev_info = sd.query_devices(0, 'input')
rate     = int(dev_info['default_samplerate'])
print(dev_info)

model = Model(lang="tr")
rec   = KaldiRecognizer(model, rate, json.dumps(list(wmap.keys()), ensure_ascii=False))
#rec.SetWords(True)


with sd.RawInputStream(samplerate=rate, blocksize=1000, device=0, dtype="int16", channels=1, callback=callback):

  while True:
      data = q.get()     
      if rec.AcceptWaveform(data):
          phrase = json.loads(rec.FinalResult())['text']
          res = json.loads(rec.Result())
          if phrase in wmap:
            #if self._wmap[phrase][0] == "_set_cmd_mode":
            print(phrase)
