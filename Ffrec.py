#!/usr/bin/python3
import sys,time,os,datetime,pyaudio,wave,subprocess,signal
from threading import Thread
Now = datetime.datetime.now()
DTime = (Now.strftime("%Y-%m-%d-%H-%M-%S"))
Wav_Chunks = []
Stop = False


def handler(signum, frame):
        global Stop
        if Stop is False:
           os.system("pkill -15 ffmpeg")
           time.sleep(2)
           Stop = True
           print("\nCome On !? Whats the rush!?")
        else:
           print("\nNot my problem dude just find another way")

signal.signal(signal.SIGINT, handler)

def Get_Source(api,mic):

   cmd = "pacmd list-sources"
   cmd = cmd.split(" ")
   answer = subprocess.check_output(cmd).decode(errors="ignore")
   outputid = None
   micid = None
   if "index:" in answer:
     answersplit = answer.split("index:")
     for line in answersplit:
         line = [l.strip("\n") for l in line.splitlines() if l.strip()]
         for l in line:
            if "name:" in l:
                if api in l and "monitor" in l and "output" in l:
                    outputid = l.split("<")[1].split(">")[0]
                if api in l and mic in l and "input" in l:
                    micid = l.split("<")[1].split(">")[0]

     if micid is None or outputid is None:

          print(answer)
          print("\n")
          if micid is None:
             print("Havnt found %s"%mic)
          if outputid is None:
             print("Havnt found %s api"%api) 
          sys.exit()
     else:
          print("Found system output: %s"%outputid)
          print("Found mic input: %s"%micid)
          return(outputid,micid)
   else:
          print(answer)
          print("\nFound Nothing")
          sys.exit()
   
def ffmpeg(action,arg1=None,arg2=None,arg3=None):

   if action == "rec":

      if arg2:
          cmd = "ffmpeg -loglevel panic -video_size 1024x768 -r %s -use_wallclock_as_timestamps 1 -f x11grab -i :0.0 -use_wallclock_as_timestamps 1 -f pulse -i %s -use_wallclock_as_timestamps 1 -f pulse -i %s -map 0:0 -use_wallclock_as_timestamps 1 -map 1:0 -c:v h264 -crf 23 -preset ultrafast -color_range 2 %s"%(FRAMERATE,arg1,arg2,Opt_File)
          print("\nLaunching ffmpeg(recall):\n")
          print(cmd)
          print()
          os.system(cmd)

      if arg2 is None:
          cmd = "ffmpeg -loglevel panic -video_size 1024x768 -r %s -use_wallclock_as_timestamps 1 -f x11grab -i :0.0 -use_wallclock_as_timestamps 1 -f pulse -i %s -use_wallclock_as_timestamps 1 -c:v h264 -crf 23 -preset ultrafast -color_range 2 %s"%(FRAMERATE,arg1,Opt_File)
          print("\nLaunching ffmpeg(recall):\n")
          print(cmd)
          print()
          cmd = cmd.split(" ")
          process = subprocess.Popen(cmd)
          Thread(target=CheckProc).start()

   if action == "fix":
          if arg3 != 0:
             cmd = "ffmpeg -loglevel panic -i %s -filter:a atempo='%s' %s"%(arg1,arg3,arg2)
          else:
             cmd = "ffmpeg -loglevel panic -i %s %s"%(arg1,arg2)
          print("\nLaunching ffmpeg(fix):\n")
          print(cmd)
          os.system(cmd)

   if action == "mix":
         fname = "FFinal-%s.mp4"%str(DTime)
         cmd = "ffmpeg -loglevel panic -i %s -i %s -filter_complex '[1]amix=inputs=2[a]' -map 0:v -map '[a]' -c:v copy  %s"%(arg1,arg2,fname)
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
           time.sleep(0.5)
        except Exception as e:
           if "returned non-zero exit status 1" in str(e):
                elapse = datetime.datetime.now() - Now
                Stop = True
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

def Ffsplit(audio,Mic_Rate,dvid,ffcmd=None):
       global Wav_Chunks
       Wav_Chunks = []

       Thread(target=ffmpeg("rec",Built_in_Audio)).start()

       while True:
           if os.path.exists(Opt_File) is False:
              time.sleep(0.1)
           else:
              break

       stream = audio.open(format=pyaudio.paInt16, channels=1,
                rate=Mic_Rate, input=True,input_device_index = dvid,
                frames_per_buffer=512)
       print("\nRecording Audio...\n")
       while Stop is False:
                try:
                   chunk = stream.read(512)
                   Wav_Chunks.append(chunk)
                except Exception as e:
                   print("\nError:",e)
 
       elapse = datetime.datetime.now() - Now
       print("\nRecording has stopped (%s seconds Recorded) .\n"%elapse.seconds)
       stream.stop_stream()
       stream.close()
       audio.terminate()

def AudIO(Mic_Device):

   audio = pyaudio.PyAudio()
   Mic_Rate = int(audio.get_device_info_by_index(Mic_Device).get('defaultSampleRate'))

   if type(Mic_Device) == int:

       Ffsplit(audio,Mic_Rate,Mic_Device)

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

def Rm(files):
  print("\nRemoving old files")
  for r in files:
     print("-deleting:",r)
     os.remove(r)
  print("\nDone")


def Get_Lenght(video,audio):

   cmdv= ("ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 %s"%video).split(" ")
   cmda= ("ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 %s"%audio).split(" ")
#   print(cmdv)
#   print(cmda)
   v_len = subprocess.check_output(cmdv).decode(errors="ignore")
   a_len = subprocess.check_output(cmda).decode(errors="ignore")
   try:
      if float(v_len) > float(a_len):
          print("Video is longer than audio: %s/%s"%(float(v_len),float(a_len)))
          return(float(v_len)/float(a_len))
      else:
          print("Audio is longer than video: %s/%s"(float(a_len),float(v_len)))
          return(float(a_len)/float(v_len))
   except Exception as e:
      print("Error:",e)
      return 0


def Split_record():
  Mic_Device = Enum_Devices()
  AudIO(Mic_Device)

  print("\nWav saved at :",WavePath)
  print("\nVideo saved at :",Opt_File)
  print("\nChecking lenght:")

  atmp = Get_Lenght(Opt_File,Wavname)
  ffmpeg("fix",Wavname,Mp3name,atmp)

  print("\nNow mixing both:")
#  ffmpeg("mix",Opt_File,Mp3name)
  ffmpeg("mix",Opt_File,Wavname)
####
Built_in_Audio,Microphone = Get_Source("alsa","Microphone") 

FRAMERATE = 4
V_Format = "avi" #FUCK MP4 !!!...AND MKV !!!!
Opt_Dir = "ffrec-" + str(DTime)
Wavname = "ffrec-%s.wav"%str(DTime)
Mp3name = "ffrec-%s.mp3"%str(DTime)
WavePath = Opt_Dir+"/"+str(Wavname)
Opt_File = "ffrec-%s.%s"%(str(DTime),V_Format)
####

if os.path.exists(Opt_Dir) is False:
   os.makedirs(Opt_Dir)

os.chdir("./"+str(Opt_Dir))

######recording screen only with ffmpeg and mic with pyaudio

Split_record()

Rm([Wavname,Mp3name,Opt_File])

####### Uncomment for Recording both screen mic and output audio with ffmpeg
#ffmpeg("rec",Built_in_Audio,Microphone)
#print("\nVideo saved at :",Opt_File)

