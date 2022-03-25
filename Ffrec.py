#!/usr/bin/python3
import sys,os,datetime,pyaudio,wave,signal,subprocess
from threading import Thread
DTime = (datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
Opt_Dir = "ffrec-" + str(DTime)
Opt_File = "ffrec-%s.mp4"%str(DTime)
Wavname = "ffrec-%s.wav"%str(DTime)
Stop = False

if os.path.exists(Opt_Dir) is False:
   os.makedirs(Opt_Dir)

os.chdir("./"+str(Opt_Dir))


def handler(signum, frame):
        global Stop
        Stop = True
        print("\n\nCome on ! Calm Down!\n\n")

signal.signal(signal.SIGINT, handler)


def ffmpeg(action,wvp=None,vp=None):

   if action == "rec":
      cmd = "ffmpeg -video_size 1024x768 -framerate 4 -f x11grab -i :0.0 %s"%Opt_File
      print("\n\nLaunching ffmpeg(rec):\n\n")
      print(cmd)
      os.system(cmd)
      Thread(target=CheckProc).start()

   if action == "mix":
      fname = "FFinal-%s.mp4"%str(DTime)
      cmd = "ffmpeg -i %s -i %s %s"%(wvp,vp,fname)
      print("\n\nLaunching ffmpeg(mix):\n\n")
      print(cmd)
      os.system(cmd)

def Enum_Devices():
   audio = pyaudio.PyAudio()
   info = audio.get_host_api_info_by_index(0)
   numdevices = info.get('deviceCount')
   Mic_Name = "pulse"
   Dev_Id = ""
   for i in range(0, numdevices):
        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
           print("id(%s):%s"%(i,audio.get_device_info_by_host_api_device_index(0, i).get('name')))
           if Mic_Name in audio.get_device_info_by_host_api_device_index(0, i).get('name'):
              Dev_Id = i
   if type(Dev_Id) == int:
      return(Dev_Id)
   else:
      print("\n\nMic not found\n")
      sys.exit()

def CheckProc():
   global Stop
   while True:
        try:
           checkproc = int(subprocess.check_output(["pidof","-s","ffmpeg"]))
           time.sleep(1)
        except Exception as e:
           if "returned non-zero exit status 1" in str(e):
                Stop = True
                print("\n\nRecording has stopped.\n\n")
                return

def Record(Mic_Device):

   audio = pyaudio.PyAudio()
   info = audio.get_host_api_info_by_index(0)
   frames = []

   if type(Mic_Device) == int:
       Mic_Rate = int(audio.get_device_info_by_index(Mic_Device).get('defaultSampleRate'))
       stream = audio.open(format=pyaudio.paInt16, channels=1,
                rate=Mic_Rate, input=True,input_device_index = Mic_Device,
                frames_per_buffer=512)
       print("\n\nRecording ...\n\n")
       ffmpeg("rec")
       while Stop is False:
                try:
                   chunk = stream.read(512)
                   frames.append(chunk)
                except Exception as e:
                   print("\nError:",e)
       stream.stop_stream()
       stream.close()
       audio.terminate()
       try:
          with wave.open(str(Wavname),"wb") as w:
               w.setnchannels(1)
               w.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
               w.setframerate(Mic_Rate)
               w.writeframes(b''.join(frames))
               return(Opt_Dir+"/"+str(Wavname))
       except Exception as e:
           print("\n\nError:",str(e))
           sys.exit()
   else:
      print("\n\nMic not found.\n\n")
      sys.exit()


Mic_Device = Enum_Devices()

WavePath = Record(Mic_Device)
print("\n\nWav saved at :",WavePath)
print("\n\nmp4 saved at :",Opt_File)
print("\n\nNow mixing both:")
ffmpeg("mix",Wavname,Opt_File)
