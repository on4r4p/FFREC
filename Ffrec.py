#!/usr/bin/python3
import sys,time,os,datetime,pyaudio,wave,subprocess,signal,fpstimer,keyboard
from argparse import ArgumentParser
from threading import Thread
from pynput import keyboard
Now = datetime.datetime.now()
DTime = (Now.strftime("%Y-%m-%d-%H-%M-%S"))
Wav_Chunks = []
Stop = False
Exit = 0

def handler(signum, frame):
        global Stop
        global Exit
        if Stop is False:
           if CAPTURE == "video":
              os.system("pkill -15 ffmpeg")
              Stop = True
              Exit += 1
              print("\nCome On !? Whats the rush!?")
           else:
              Stop = True
              Exit += 1
              print("\nScreenshoting stopped.")
        else:
           if Exit < 4:
              print("\nPress Ctrl+c %s times to exit."%(4-Exit))
              Exit += 1
           else:
              sys.exit(1)

signal.signal(signal.SIGINT, handler)

def Get_Resolution():
   answer = subprocess.check_output(["xrandr"]).decode(errors="ignore")
   try:
      res = "".join([x.strip() for x in answer.splitlines() if "*" in x]).split(" ")[0]
      return(res)
   except Exception as e:
     print("Error:",e)
     return('1024x768')

def Get_Source(api,device):
   if api == "alsa":

      audio = pyaudio.PyAudio()
      info = audio.get_host_api_info_by_index(0)
      numdevices = info.get('deviceCount')
      Dev_Id = ""
      for i in range(0, numdevices):
        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
           if Dev_Name in audio.get_device_info_by_host_api_device_index(0, i).get('name'):
                  Hw = audio.get_device_info_by_host_api_device_index(0, i).get('name')
                  if "(hw:" in Hw:
                       outputid = "hw:"+str(Hw.split("(hw:")[1].replace(")",""))
                       return(outputid)
      print("Device %s not found\n"%device)
      List_Audio()
      sys.exit()

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
                outputid = l.split("<")[1].split(">")[0]
            if device in l:
                 break
     if outputid is None:
             print(answer)
             print("\n")
             print("Havnt found %s api"%api) 
             sys.exit()
     else:
          print("Found device: %s"%outputid)
          return(outputid)
   else:
          print(answer)
          print("\nFound Nothing")
          sys.exit()

def Screenshot():
   global PngsLen
   print("Screenshooting..\nPress 'q' to stop..")
   Thread(target=Klisten).start()
   timer = fpstimer.FPSTimer(FRAMERATE)
   while Stop is False:
      timer.sleep()
      Screename = "SShot-" + str(PngsLen).zfill(12) + ".png"
      cmd = "import -silent -window root %s"%Screename
      os.system(cmd)
      PngsLen += 1

def on_press(key):
    global Stop
    try:
        if key == keyboard.KeyCode.from_char('q'):
            Stop = True
            return False
    except Exception as e:
        print("Error:",e)

def Klisten():
  with keyboard.Listener(on_press=on_press) as listener:
      listener.join()


def ffmpeg(wait=None):
          cmd = Get_Cmd().replace("  "," ")
          print()
          print(cmd)
          print()
          if wait is True:
             cmd = cmd.split(" ")
             process = subprocess.Popen(cmd)
             Thread(target=CheckProc).start()
          else:
              os.system(cmd)
              print("\nVideo saved at :",Tmp_Opt_File)


def Fix(audio1,audio2,atmp):
    if DEBUG is False:
           cmd = "ffmpeg -loglevel panic "
    else:
           cmd = "ffmpeg "
    if atmp != 0:
       cmd += "-i %s -filter:a atempo='%s' %s"%(audio1,atmp,audio2)
    else:
       cmd += "-i %s %s"%(audio1,audio2)
    print("\nLaunching ffmpeg(fix):\n")
    print(cmd)
    os.system(cmd)

def Mix(video,audio):
   if DEBUG is False:
           cmd = "ffmpeg -loglevel panic "
   else:
           cmd = "ffmpeg "

   print("\nNow mixing both:")

   fname = "FFinal-%s.%s"%(str(DTime),FORMAT)
   if len(FFDEV)>0 and len(PYADEV)>0:
       cmd += "-i %s -i %s -filter_complex '[1]amix=inputs=2[a]' -map 0:v -map '[a]' -c:v copy  %s"%(video,audio,fname)
   else:
       cmd += "-i %s -i %s %s"%(video,audio,fname)

   print(cmd)

   os.system(cmd)

def Mixshot(audio=None):
    if DEBUG is False:
           cmd = "ffmpeg -loglevel panic "
    else:
           cmd = "ffmpeg "
    fname = "FFinal-%s.%s"%(str(DTime),FORMAT)
    Fps = Wav_Duration(audio)
    if audio:
       cmd += """-framerate %s -pattern_type glob -i "*.png" -i %s -vf scale=720:-1 -c:v libx264 -pix_fmt yuv420p %s"""%(Fps,audio,fname)
    else:
       cmd += """-framerate %s -pattern_type glob -i "*.png" -vf scale=720:-1 -c:v libx264 -pix_fmt yuv420p %s"""%(Fps,fname)
    print()
    print(cmd)
    print()
    os.system(cmd)

def Enum_Devices(Dev_Name):
   audio = pyaudio.PyAudio()
   info = audio.get_host_api_info_by_index(0)
   numdevices = info.get('deviceCount')
   Dev_Id = ""
   for i in range(0, numdevices):
        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
           print("id(%s):%s"%(i,audio.get_device_info_by_host_api_device_index(0, i).get('name')))
           if Dev_Name in audio.get_device_info_by_host_api_device_index(0, i).get('name'):
              Dev_Id = i
   if type(Dev_Id) == int:
      return(Dev_Id)
   else:
      print("\nDevice not found:%s\n"%Dev_Name)
      sys.exit()

def CheckProc():
   global Stop
   while True:
        try:
           checkproc = int(subprocess.check_output(["pidof","-s","ffmpeg"]))
           time.sleep(0.5)
        except Exception as e:
           if "returned non-zero exit status 1" in str(e):
                Stop = True
                print("\nVideo saved at :",Tmp_Opt_File)
                return

def Wav_Duration(file):
   try:
       with wave.open(file,'r') as f:
           frames = f.getnframes()
           rate = f.getframerate()
           wln = round(frames/rate,2)
           print("\nWav Duration:%s\n"%datetime.timedelta(seconds=int(wln)))
           Fps = Find_Fps(PngsLen,wln)
           print("Nearest frame per seconde : Png-files:%s/Wav-Duration:%s = %s fps"%(PngsLen,wln,Fps))
           return(Fps)
   except Exception as e:
           print("Error:",str(e))

def Ffsplit(audio,Mic_Rate,dvid):
       global Wav_Chunks

       Wav_Chunks = []

       if CAPTURE == "video":
          Thread(target=ffmpeg(True)).start()
       elif CAPTURE == "screenshot":
          Thread(target = Screenshot).start()
       if CAPTURE == "video":
           while True:
               if os.path.exists(Tmp_Opt_File) is False:
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
                  if "Stream closed" in str(e):
                     try:
                        stream.stop_stream()
                     except Exception as e:
                        print(e)
                     try:
                        stream.close()
                     except Exception as e:
                        print(e)
                     try:
                        audio.terminate()
                     except Exception as e:
                        print(e)
                     try:
                        print("\nError:%s [Restarting]"%str(e))
                        stream = audio.open(format=pyaudio.paInt16, channels=1,rate=Mic_Rate,
                              input=True,input_device_index = dvid,frames_per_buffer=512)
                     except Exception as e:
                         print(e)
       elapse = datetime.datetime.now() - Now
       print("\nRecording has stopped (%s seconds Recorded) .\n"%elapse.seconds)

       try:
          stream.stop_stream()
       except Exception as e:
          print("\nError:",e)

       try:
          stream.close()
       except Exception as e:
          print("\nError:",e)

       try:
          audio.terminate()
       except Exception as e:
          print("\nError:",e)

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
          print("\nWav saved at :",WavePath)

       except Exception as e:
           print("\nAudIO Error:",str(e))
           sys.exit()
   else:
      print("\nMic not found.\n")
      sys.exit()

def Rm(files):
#  return()
  print("\nRemoving old files")
  for r in files:
     if "*.png" not in r:
        print("-deleting:",r)
        try:
          os.remove(r)
        except Exception as e:
          print("Error:",e)
     else:
        os.system('find . -type f -name "*.png" -delete"')
  print("\nDone")

def Rmshot():
#   return()
   files = os.listdir(".")
   for item in files:
      if item.endswith(".png"):
        os.remove(item)
   print("Done Removing screenshots")

def Get_Lenght(video,audio):

   print("\nChecking lenght:")

   cmdv= ("ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 %s"%video).split(" ")
   cmda= ("ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 %s"%audio).split(" ")
   v_len = subprocess.check_output(cmdv).decode(errors="ignore")
   a_len = subprocess.check_output(cmda).decode(errors="ignore")
#   print("\nAdding 2 seconds to video cauz ur computer sucks..")

   try:
#      v_len = float(v_len) - float(2.0)
      if float(v_len) > float(a_len):
          print("Video is longer than audio: %s/%s"%(float(v_len),float(a_len)))
          return(float(a_len)/float(v_len))
      else:
          print("Audio is longer than video: %s/%s"%(float(a_len),float(v_len)))
          return(float(v_len)/float(a_len))
   except Exception as e:
      print("Error:",e)
      return 0

def Get_Cmd():
       if DEBUG is False:
           cmd = "ffmpeg -loglevel panic "
       else:
           cmd = "ffmpeg "

       if len(FFDEV) == 0:
            cmd += "-video_size %s -r %s -f x11grab -i :0.0 -c:v h264 -crf 23 -preset ultrafast -color_range 2 %s"%(RESOLUTION,FRAMERATE,Tmp_Opt_File)
            return(cmd)

       if len(FFDEV) == 1:
              cmd += "-video_size %s -r %s -f x11grab -i :0.0 -f %s  -i %s -c:v h264 -crf 23 -preset ultrafast -color_range 2  %s"%(RESOLUTION,FRAMERATE,api,FFDEV[0],Tmp_Opt_File)
       if len(FFDEV) == 2:
              cmd += "-video_size %s -r %s -f x11grab -i :0.0 -f %s -i %s -f %s -i %s -map 0:0 -map 1:0 -c:v h264 -crf 23 -preset ultrafast -color_range 2 %s"%(RESOLUTION,FRAMERATE,api,FFDEV[0],api,FFDEV[1],Tmp_Opt_File)
       return(cmd)




def main():

   if os.path.exists(Output_Dir) is False:
      os.makedirs(Output_Dir)

   os.chdir("./"+str(Output_Dir))

   if CAPTURE == "screenshot":

      
     if len(PYADEV) > 0:
            Mic_Device = Enum_Devices(PYADEV[0])
            AudIO(Mic_Device)
            Mixshot(Wavname)
            Rm([Wavname])
            Rmshot()
     else:
         Screenshot()
         Mixshot()
         Rmshot()

   elif CAPTURE == "video":

      if len(PYADEV) > 0:
            Mic_Device = Enum_Devices(PYADEV[0])
            AudIO(Mic_Device)
            atmp = Get_Lenght(Tmp_Opt_File,Wavname)
            Fix(Wavname,Mp3name,atmp)
            Mix(Tmp_Opt_File,Mp3name)
            Rm([Wavname,Mp3name,Tmp_Opt_File])

      else:
            ffmpeg()

def Find_Fps(p,w):
    f = 0.0001
    while True:
       f += 0.0001
       r = p/f
       if r <= w:return(round(f,2))

def List_Audio():
   audio = pyaudio.PyAudio()
   info = audio.get_host_api_info_by_index(0)
   numdevices = info.get('deviceCount')
   Mic_Name = "pulse"
   Dev_Id = ""
   print("\n\n")
   print('Using Alsa api choose a device using its hardware id like this : -a "ffmpeg=hw:0 pyaudio=hw:1,0"')
   print("\n")
   for i in range(0, numdevices):
        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
           print("Device name :%s"%(audio.get_device_info_by_host_api_device_index(0, i).get('name')))
   print("\n\n")
   print('Using Pulse api choose a device using its name like this : "ffmpeg=output.pci.analog-stereo.monitor"')
   print("\n")

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
               print(l.strip())

if __name__ == "__main__":
    FFDEV = []
    PYADEV = []


    parser = ArgumentParser()
    parser.add_argument(
        "-o", "--output", dest="OUTPUT", help="Video File Output Name ex: -o video.mp4", default=None, metavar="FILE"
    )

    parser.add_argument(
        "-c",
        "--capture",
        dest="CAPTURE",
        help="Choose Capture screen -c video or -c screenshot",
        default=None
    )

    parser.add_argument(
        "-p",
        "--api",
        dest="api",
        help="Choose api -p pulse or -p alsa",
        default=None
    )

    parser.add_argument(
        "-a",
        "--audio",
        dest="AUDIO",
        help='Record Device audio with ffmpeg or pyaudio or both: -a "[ffmpeg]=[MIC],[Speakers] [pyaudio]=[DEVICE]"',
        default=None,
        metavar="option"
    )
    parser.add_argument(
        "-f",
        "--framerate",
        dest="FRAMERATE",
        help='Framerate',
        default=None,
        metavar="option"
    )
    parser.add_argument(
        "-l",
        "--list",
        dest="LISTA",
        help="List audio devices",
        action="store_true",
    )

    parser.add_argument(
        "-d",
        "--debug",
        dest="DEBUG",
        help="makes ffmpeg verbose",
        action="store_true",
    )

    Args, unknown = parser.parse_known_args()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    if Args.LISTA is True:
        List_Audio()
        sys.exit(1)
    if Args.OUTPUT is None:
        print("-o,--output arguments is missing.")
        parser.print_help(sys.stderr)
        sys.exit(1)
    if Args.CAPTURE is None:
        print("-c,--capture arguments is missing.")
        parser.print_help(sys.stderr)
        sys.exit(1)

    if Args.FRAMERATE is None:
        print("-f,--framerate arguments is missing.")
        parser.print_help(sys.stderr)
        sys.exit(1)

    if Args.AUDIO:
      if "=" in Args.AUDIO:
         audio_options = (Args.AUDIO).split(" ")
         for o in audio_options:
             o = o.split("=")
             prog = o[0]
             option = o[1]
             if prog != "ffmpeg" and prog != "pyaudio":
                print("-a,--audio wrong arguments.")
                print(prog)
                parser.print_help(sys.stderr)
                sys.exit(1)
             if prog == "ffmpeg":
                if option.count(" ") >1:
                    print("Max 2 devices for ffmpeg cauz im lazy")
                    sys.exit(1)
                FFDEV.append(option)
             if prog == "pyaudio":
                if " " in option:
                    print("Max 1 devices for pyaudio cauz im lazy")
                    sys.exit(1)
                PYADEV.append(option)

      else:
         print("-a,--audio wrong arguments.")
         parser.print_help(sys.stderr)
         sys.exit(1)

    if Args.AUDIO:
       if Args.api:
          if Args.api != "pulse" and Args.api != "alsa":
              print("-p,--api wrong arguments.")
              parser.print_help(sys.stderr)
              sys.exit(1)
       else:
         print("-p,--api must be set.")
         parser.print_help(sys.stderr)
         sys.exit(1)

     #Built_in_Audio,Microphone = Get_Source("alsa","Microphone") 
    FRAMERATE = int(Args.FRAMERATE)
    OUTPUT = Args.OUTPUT.split(".")[0]
    FORMAT = Args.OUTPUT.split(".")[1]
    CAPTURE = Args.CAPTURE
    DEBUG = Args.DEBUG
    api = Args.api
    RESOLUTION = Get_Resolution()
    Output_Dir = "ffrec-" + str(DTime)
    Wavname = "%s-ffrec-%s.wav"%(str(OUTPUT),str(DTime))
    Mp3name = "%s-ffrec-%s.mp3"%(str(OUTPUT),str(DTime))
    WavePath = Output_Dir+"/"+str(Wavname)
    Tmp_Opt_File = "%s-ffrec-%s.avi"%(str(OUTPUT),str(DTime))
    Opt_File = "%s-ffrec-%s.%s"%(str(OUTPUT),str(DTime),FORMAT)
    PngsLen = 0
    main()
