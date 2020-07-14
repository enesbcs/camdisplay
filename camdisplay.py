import cv2
import threading
import time
import requests
import numpy as np
import os

os.putenv('DISPLAY', ':0')

rtspurl = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov"
snapurl = "https://storage.needpix.com/rsynced_images/tv-test-pattern-146649_1280.png"
auser = "username"
apass = "password"
screensize = [1027, 768] # display size!

tryrtsp = True

class RTSPGrabber:
 def __init__(self,url=None, user="", passw=""):
   self.dtime = 1/20
   self.url = url
   self.cap = None
   self.started = False
   self.frame = None
   try:
    self.init = self.open()
   except:
    self.init = False
    self.url = None

 def isopened(self):
  return self.init

 def open(self):
   init = False
   try:
    if self.url != None:
     self.cap = cv2.VideoCapture(self.url)
     time.sleep(3)
     init = self.cap.isOpened()
   except:
    init = False
    self.cap = None
   return init

 def startgrab(self):
     if self.init:
       if self.started==False:
        self.started = True
        thread = threading.Thread(target=self.update, args=())
        thread.daemon = True
        thread.start()
       time.sleep(0.1)
       starttime = time.time()
       while (self.frame is None) and (time.time()-starttime<10):
         self.getimage(True)
         time.sleep(0.1)
       if self.frame is None:
        self.started = False
        self.init = False

 def update(self):
        while self.started:
         try:
           grabbed = self.cap.grab()
         except Exception as e:
           time.sleep(1)
        try:
         self.cap.release()
        except:
         pass

 def stop(self):
        self.started = False
        time.sleep(0.5)

 def getimage(self,force=False):
     try:
       grabbed, self.frame = self.cap.retrieve()
     except Exception as e:
       pass
     return self.frame

class IMGGrabber:
 def __init__(self,url=None,user="",passw=""):
   self.url = url
   self.user = user
   self.passw = passw
   self.frame = None
   self.started = False
   try:
    self.frame = self.getimage(True)
    self.init = (self.frame is not None)
   except:
    self.init = False
    self.url = None
    self.frame = None

 def isopened(self):
  return self.init

 def startgrab(self):
     if self.init:
       if self.started==False:
        self.started = True

 def getimage(self,force=False):
    if self.started or force:
     try:
       response = requests.get(self.url,auth=requests.auth.HTTPBasicAuth(self.user, self.passw))
       arr = np.asarray(bytearray(response.content), dtype=np.uint8)
       self.frame = cv2.imdecode(arr, -1)
     except Exception as e:
      pass
     return self.frame

 def stop(self):
   self.started = False

vcap = None
pdelay = 1/10
if tryrtsp:
 vcap = RTSPGrabber(rtspurl)
 if vcap.isopened():
  print("RTSP open ok")
  vcap.startgrab()
  if vcap.isopened()==False:
   print("RTSP grab failed, abort")
   vcap = None
 else:
  print("RTSP open failed")
  vcap = None
if vcap is None:
 vcap = IMGGrabber(snapurl,auser,apass)
 if vcap.isopened():
  print("IMG open ok")
  pdelay = 0
  vcap.startgrab()
 else:
  print("IMG open failed")
  vcap = None
if vcap is not None:
 cv2.namedWindow('VIDEO', cv2.WND_PROP_FULLSCREEN)
 cv2.setWindowProperty('VIDEO', cv2.WND_PROP_FULLSCREEN, 1)
 while(1):
   frame = vcap.getimage()
   try:
    resframe = cv2.resize(frame, (screensize[0],screensize[1]))
    cv2.imshow('VIDEO', resframe)
   except Exception as e:
    pass
   time.sleep(pdelay)
   if cv2.waitKey(1) == 27 :
            break
 vcap.stop()
 cv2.destroyAllWindows()
