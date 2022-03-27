#!/usr/bin/python3
import sys,os,datetime,pyaudio,wave,subprocess,signal
from threading import Thread
Now = datetime.datetime.now()
DTime = (Now.strftime("%Y-%m-%d-%H-%M-%S"))
Opt_Dir = "ffrec-" + str(DTime)
Opt_File = "ffrec-%s.mp4"%str(DTime)
Wavname = "ffrec-%s.wav"%str(DTime)
WavePath = Opt_Dir+"/"+str(Wavname)
Wav_Chunks = []
Stop = False

if os.path.exists(Opt_Dir) is False:
   os.makedirs(Opt_Dir)

os.chdir("./"+str(Opt_Dir))


def handler(signum, frame):
        global Stop
        Stop = True
        print(glob.glob(str(OptDir)+"/*.png"))
        print("\nCome On !? Whats the rush!?")

signal.signal(signal.SIGINT, handler)

def ffmpeg(action,wvp=None,vp=None):

   if action == "rec":
      cmd = "ffmpeg -loglevel panic -video_size 1024x768 -framerate 4 -f x11grab -i :0.0 %s"%Opt_File
      print("\nLaunching ffmpeg(rec):\n")
      print(cmd)
      process = subprocess.Popen(['ffmpeg','-loglevel','panic', '-video_size', '1024x768','-framerate','4','-f','x11grab','-i',':0.0',Opt_File])
      Thread(target=CheckProc).start()

   if action == "mix":
      fname = "FFinal-%s.mp4"%str(DTime)
      cmd = "ffmpeg -i %s -i %s %s"%(wvp,vp,fname)
      print("\nLaunching ffmpeg(mix):\n")
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
      print("\nMic not found\n")
      sys.exit()

def CheckProc():
   global Stop
   while True:
        try:
           checkproc = int(subprocess.check_output(["pidof","-s","ffmpeg"]))
           time.sleep(1)
        except Exception as e:
           if "returned non-zero exit status 1" in str(e):
                elapse = datetime.datetime.now() - Now
                Stop = True
                print("\nRecording has stopped (%s seconds Recorded) .\n"%elapse.seconds)
                return

def Wav_Duration(file):
   try:
       with wave.open(file,'r') as f:
           frames = f.getnframes()
           rate = f.getframerate()
           wln = round(frames/rate,2)
           print("\nWav Duration:%s\n"%datetime.timedelta(seconds=int(wln)))
   except Exception as e:
           print("Error:",str(e))

def Recording(audio,Mic_Rate,dvid):
       global Wav_Chunks
       Wav_Chunks = []

       stream = audio.open(format=pyaudio.paInt16, channels=1,
                rate=Mic_Rate, input=True,input_device_index = dvid,
                frames_per_buffer=512)
       print("\nRecording Audio...\n")
       Thread(target=ffmpeg("rec")).start()
       while Stop is False:
                try:
                   chunk = stream.read(512)
                   Wav_Chunks.append(chunk)
                except Exception as e:
                   print("\nError:",e)

       elapse = datetime.datetime.now() - Now
       print("\nRecording has stopped2 (%s seconds Recorded) .\n"%elapse.seconds)
       stream.stop_stream()
       stream.close()
       audio.terminate()

def AudIO(Mic_Device):

   audio = pyaudio.PyAudio()
   Mic_Rate = int(audio.get_device_info_by_index(Mic_Device).get('defaultSampleRate'))

   if type(Mic_Device) == int:

       Recording(audio,Mic_Rate,Mic_Device)

       try:
          with wave.open(str(Wavname),"wb") as w:
               w.setnchannels(1)
               w.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
               w.setframerate(Mic_Rate)
               w.writeframes(b''.join(Wav_Chunks))
          Wav_Duration(Wavname)

       except Exception as e:
           print("\niciError:",str(e))
           sys.exit()
   else:
      print("\nMic not found.\n")
      sys.exit()


Mic_Device = Enum_Devices()

AudIO(Mic_Device)
print("\nWav saved at :",WavePath)
print("\nmp4 saved at :",Opt_File)
print("\nNow mixing both:")
ffmpeg("mix",Wavname,Opt_File)
