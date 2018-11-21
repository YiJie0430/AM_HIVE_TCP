import os,time,threading,thread,htx,ctypes
from subprocess import Popen, PIPE, STDOUT
from ctypes import byref
print os.getcwd()
from toolslib import *
dll=ctypes.WinDLL('WiFiMan.dll')
ERROR_OFFSET = 0x70000000

wifi0=thread.allocate_lock()
wifi1=thread.allocate_lock()
wifi2=thread.allocate_lock()
wifi3=thread.allocate_lock()
WIFIMutex = [wifi0,wifi1,wifi2,wifi3]
tool_dir= 'C:/Net-SNMP/bin/'


class Except:
    """    example:
        try:
            if ....:
                raise Except("Error!!")
        except Except, msg:
            print msg    """
    def __init__(self,msg):
        self.value = msg
    def __str__(self):
        return self.value
    def __repr__(self):
        return self.value

class WIFIThread(threading.Thread):
      def __init__(self,id,ssid,wpakey,wifi_target,packetsize,ping_loss,nic_ip):
          threading.Thread.__init__(self)
          self.id=id
          self.wifi_id=int((id-1)/2)
          self.ssid=ssid
          self.wpakey=wpakey
          self.wifi_target=wifi_target
          self.packetsize = packetsize
          self.ping_loss = ping_loss
          self.nic_ip = nic_ip
          self.running=True
          self.mainrunning=True
          #self.msg=[1,'[%s]wifi error,no test'%self.ssid]
          self.value = 100
          self.testflag=1
          self.pingtest=0
          self.err = ''
          
      def run(self):
          try:
              if self.id < 8: WIFIMutex[0].acquire()  #for DUT1,DUT4  wifi_adaptor= 0, DUT5,DUT8 wifi_adaptor=1             
              else: WIFIMutex[1].acquire() 
              print '%s WIFI function to start the test'%self.ssid             
              if self.mainrunning:
                  for i in range(5):
                      Connected=''
                      Connected=WLAN(self.ssid,self.id,self.wpakey).connect()
                      print Connected 
                      if 'ERROR' not in Connected: break
                      else:
                          print "wlan connect count %d"%i
                          if i == 4:
                              self.err = Connected 
                              raise Except(Connected) 
              os.system('arp -d')
              #htx.IsConnect(self.wifi_target,10)
              if not IsConnect(self.wifi_target,10): raise Except("FAIL: WIFI Ping Test Fail")
              else: self.pingtest = 1
              '''
              print 'Ping function to start the test'                   
              for j in range(3):                                                                     
                  self.value = MSPing(self.nic_ip,self.wifi_target)
                  print 'Count %d %s Ping %s packet loss: %.1f'%(j,self.ssid,self.wifi_target,self.value)                                                                  
                  if self.value < self.ping_loss:
                      self.testflag=0
                      break
                  else: time.sleep(1)
              '''
              if self.id < 8:  #for DUT1,DUT4  wifi_adaptor= 0, DUT5,DUT8 wifi_adaptor=1                
                  if WIFIMutex[0].locked():
                     WIFIMutex[0].release()
              else:
                  if WIFIMutex[1].locked():
                     WIFIMutex[1].release()
              self.running=False   
          except Except,msg:            
              if self.id < 8:  #for DUT1,DUT4  wifi_adaptor= 0, DUT5,DUT8 wifi_adaptor=1                
                  if WIFIMutex[0].locked():
                     WIFIMutex[0].release()
              else:
                  if WIFIMutex[1].locked():
                     WIFIMutex[1].release()
              self.running=False
              self.pingtest = 0
              
           
class WLAN:
      def __init__(self,ssid,dut_id,pwd='u',signal=30):
          #self.mac=bssid.lower()
          #self.bssid=self.mac[:2] + ' ' + self.mac[2:4] + ' ' + self.mac[4:6] + ' ' + self.mac[6:8] + ' ' + self.mac[8:10] + ' ' + self.mac[10:]
          self.ssid=ssid
          self.dut_id = dut_id
          self.pwd=pwd
          self.signal=signal
          self.StartSVC()
          msg=self.GetGUID()
          #print msg
          if 'ERROR' in msg:return msg
          if self.dut_id < 4: self.guid = msg[0][0] 
          else: self.guid = msg[0][1] 
          #print "dut id: %d"%self.dut_id
          print "self guid:%s"%self.guid
          #raw_input('#####')
          self.profilepath='profile.xml'
          
          
          
      def StartSVC(self):
          os.popen('net start wzcsvc')
          
      def StopSVC(self):
          os.popen('net stop wzcsvc')
      
      def GetGUID(self):
          guid = []
          state = []
          msg=os.popen('WLAN.exe ei').read()
          #print msg
          if 'GUID' not in msg:
             raise Except('ERROR : No wifi dongle')
          for g in msg.split('\n'):
              if 'GUID' in g:
                 guid.append(g.split('GUID:')[-1].strip())
              if 'State' in g:
                 state.append(g.split('State: "')[-1].split('"')[0])  
          return guid,state
          
      def scan(self):
          msg=os.popen('WLAN.exe scan %s'%self.guid).read()
          if 'successfully' not in msg:
             raise Except('ERROR:WIFI dongle scan failed')
          return 'WIFI dongle scan successfully'
      
      def GetBSSID(self):
          msg=os.popen('WLAN.exe gbs %s'%self.guid).read()
          if 'successfully' not in msg:
             raise Except('ERROR:WIFI dongle get bssid failed')
          if self.bssid in msg:
             ssid=msg.split(self.bssid)[-1].split('Beacon period:')[0].split('SSID:')[-1].strip()
             if self.ssid <> ssid:
                raise Except('ERROR:DUT SSID set failed:%s(%s)'%(ssid,self.ssid))
             return 'WIFI dongle get ssid successfully'
          if self.ssid in msg:
            bssid=msg.split(self.ssid)[0].split('MAC address:')[-1].strip().split()[0]
            if self.bssid<>bssid:
               raise Except('ERROR:DUT BSSID set failed:%s(%s)'%(bssid,self.bssid))
          raise Except('ERROR:WIFI dongle not search for \'%s\' signal'%self.ssid)
             
      def GetVNL(self):
          msg=os.popen('wlan.exe gvl %s'%self.guid).read() 
          if 'successfully' not in msg:
             raise Except('ERROR:WIFI dongle get visible wireless networks failed')  
          if self.ssid not in msg:
             raise Except('ERROR:WIFI dongle not search for \'%s\' signal'%self.ssid)
          msg=msg.split(self.ssid)[-1].split('Default')[0]
          if self.pwd<>'u' and 'Security not enabled' in msg:
             raise Except('ERROR:DUT WIFI did not set up encryption')
          elif self.pwd=='u' and 'Security enabled' in msg:
             raise Except('ERROR:DUT WIFI set up encryption')    
          if 'Infrastructure' in msg:
             bsstype='i'
          else:
             bsstype='a' 
          signal=int(msg.split('Signal quality:')[-1].split('%')[0].strip())
          if signal < self.signal:
             raise Except('ERROR:DUT WIFI signal is too low:%s (<%s)'%(signal,self.signal))
          #return bsstype
          return 'WIFI dongle check %s network info successfully'%self.ssid
      
      def GetQI__(self):
          for try_ in range(6):
              time.sleep(3)
              print self.guid 
              msg=os.popen('WLAN.exe qi %s'%self.guid).read()
              print msg
              #raw_input('pause') 
              if 'successfully' not in msg:
                 raise Except('ERROR:WIFI dongle query interface failed')  
              if self.ssid not in msg:
                 time.sleep(1)
                 if try_==5:raise Except('ERROR:WIFI dongle query %s failed'%self.ssid)
              else:                  
                  msg=self.GetGUID()
                  print msg
                  if self.dut_id < 4: state = msg[1][0] 
                  else: state = msg[1][1]
                  if not state=='connected':
                      continue
                      if try_==5:raise Except('ERROR:WIFI dongle state connect %s failed'%self.ssid)
                      #time.sleep(2)  
                      continue
                  else: return 'WIFI dongle connect %s successfully'%self.ssid     
      def GetQI(self):
          for i in range(30):
              print self.guid 
              msg=os.popen('WLAN.exe qi %s'%self.guid).read()
              #print msg
              #raw_input('pause') 
              #if 'successfully' not in msg:
              #   raise Except('ERROR:WIFI dongle query interface failed')  
              if self.ssid not in msg:
                 print "No:%d WIFI dongle query %s failed"%(i,self.ssid)
                 time.sleep(1)
                 continue
                 raise Except('ERROR:WIFI dongle query %s failed'%self.ssid)
              else: break
          for i in range(30):                  
              msg=self.GetGUID()
              print "NO: %d "%i 
              print msg
              if self.dut_id < 4: state = msg[1][0] 
              else: state = msg[1][1]
              if not state=='connected':
                  time.sleep(1)
                  continue
                  raise Except('ERROR:WIFI dongle state connect %s failed'%self.ssid)
                  #time.sleep(2)  
              else: return 'WIFI dongle connect %s successfully'%self.ssid     
      def disconnect(self):
          msg=os.popen('WLAN.exe dc %s'%self.guid).read() 
          if 'successfully' not in msg:
             raise Except('ERROR:WIFI dongle disconnect failed')
          return 'WIFI dongle disconnect successfully'  
      
      def delprofile(self):
          msg=os.popen('WLAN.exe gpl %s'%self.guid).read() 
          if 'successfully' not in msg:
             raise Except('ERROR:WIFI dongle list profile failed')
          profile=msg.split('Command')[0].split('interface.')[-1]
          for f in profile.split('\n'):
              f=f.strip()
              if f:
                  msg=os.popen('WLAN.exe dp %s %s'%(self.guid,f)).read() 
                  if 'successfully' not in msg:
                     raise Except('ERROR:WIFI dongle delete %s profile failed'%f)
          return 'WIFI dongle delete profile list successfully'
            
      def setprofile(self):
          #print self.profilepath
          msg=os.popen('wlan.exe sp %s %s'%(self.guid,self.profilepath)).read() 
          if 'successfully' not in msg:
             raise Except('ERROR:WIFI dongle set profile failed')
          return 'WIFI dongle set profile successfully'
      
             
      def createprofile(self):
          ssid_=''
          for s in self.ssid:
              ssid_ += '%X'%ord(s)
          profile='''<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
	<name>%s</name>
	<SSIDConfig>
		<SSID>
			<hex>%s</hex>
			<name>%s</name>
		</SSID>
	</SSIDConfig>
	<connectionType>ESS</connectionType>
	<MSM>
		<security>
			<authEncryption>
				<authentication>open</authentication>
				<encryption>none</encryption>
				<useOneX>false</useOneX>
			</authEncryption>
		</security>
	</MSM>
</WLANProfile>
'''%(self.ssid,ssid_,self.ssid) 

          profile_securited = '''<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
	<name>%s</name>
	<SSIDConfig>
		<SSID>
			<name>%s</name>
		</SSID>
	</SSIDConfig>
	<connectionType>ESS</connectionType>
	<connectionMode>auto</connectionMode>
	<MSM>
		<security>
			<authEncryption>
				<authentication>WPA2PSK</authentication>
				<encryption>AES</encryption>
				<useOneX>false</useOneX>
			</authEncryption>
			<sharedKey>
				<keyType>passPhrase</keyType>
				<protected>false</protected>
				<keyMaterial>%s</keyMaterial>
			</sharedKey>
		</security>
	</MSM>
</WLANProfile>'''%(self.ssid,self.ssid,self.pwd)
      
          f=open(self.profilepath,'w')
          if self.pwd <>'1111111111': xml = profile_securited
          else: xml = profile 
          f.write(xml)
          f.close()
          return 'Create profile successfully'   
                     
      def discover(self):
          try:
             self.StartSVC()
             print '[%s]%s'%(self.ssid,self.scan()) 
             time.sleep(1)
             print '[%s]%s'%(self.ssid,self.GetVNL())
             #print '[%s]%s'%(self.ssid,self.GetBSSID())
             msg=self.GetGUID()
             if self.dut_id < 4: state = msg[1][0] 
             else: state = msg[1][1] 
             if state=='connected':
                print '[%s]%s'%(self.ssid,self.disconnect())
                time.sleep(1)
             time.sleep(1)
             msg=os.popen('wlan.exe disc %s %s %s %s'%(self.guid,self.ssid,bss,self.pwd)).read()
             if 'successfully' not in msg:
                raise Except('ERROR:WIFI dongle connect %s failed'%self.ssid)  
             return '[%s]%s'%(self.ssid,self.GetQI())    
          except Except,msg:
             return '[%s]%s'%(self.ssid,msg)
             
      def connect(self):
          try:
               self.StopSVC()
               self.StartSVC()
      
               print '[%s]%s'%(self.ssid,self.createprofile())
               print '[%s]%s'%(self.ssid,self.scan())
               time.sleep(1)
               #print '[%s]%s'%(self.ssid,self.GetVNL())
               msg=self.GetGUID()
               if self.dut_id < 4: state = msg[1][0] 
               else: state = msg[1][1]
               if state=='connected':
                  print '[%s]%s'%(self.ssid,self.disconnect())
               print '[%s]%s'%(self.ssid,self.delprofile())
               print '[%s]%s'%(self.ssid,self.setprofile())
               return '[%s]%s'%(self.ssid,self.GetQI())    
          except Except,msg:
             return '[%s]%s'%(self.ssid,msg)    

def SetDongleConnection(ssid,wpakey):
    WIFI_Adapter_ID=0
    p = Popen('c:\\TermScript\\wifi_link.exe', stdout=PIPE, stdin=PIPE, stderr=STDOUT,shell=True)
    grep_stdout = p.communicate(input= '%s\n%s\n%s\n'%(WIFI_Adapter_ID,ssid,wpakey))[0]   
    if 'Success' in grep_stdout:
       return 1
    return 0                         
                  
#print WLAN('HOME-67A8').connect()                      
#print WLAN('Test5/6/7/8 AP').connect() 
          
          
def Ping(ip,length,count,interval):
    """    Ping(ip,length,count,interval), return the loss rate (float)
        where ip is target ip address, length is IP packet length
              count is packet number, interval is ms unit"""
    result = os.popen("Fping %s -s %d -t %d -n %d"%(ip,length,interval,count)).read()
    return float(result[result.rfind("(")+1:result.rfind("%")])
'''          
def Ping(ip,length,count,interval):
    """    Ping(ip,length,count,interval), return the loss rate (float)
        where ip is target ip address, length is IP packet length
              count is packet number, interval is ms unit"""        
    result = os.popen(tool_dir+"/hrping -f -l %d -s %d -n %d %s"%(length-14,interval,count,ip)).read()
    #print result
    return float(result[result.rfind("(")+1:result.rfind("%")])
'''   
'''          
def Pingtry(term,ip,port,timeout):
    stime=time.time()
    while time.time()-stime < timeout:
          data=lWaitCmdTerm(term,'ping %s %s 64 5 200'%(port,ip),'%',15)
          if ('0%' in data) and ('100%' not in data):
             return 1
    return 0                  
'''          
class WIFIThread_wpakey(threading.Thread):
      def __init__(self,target,ssid,wpakey,log):
          threading.Thread.__init__(self)
          self.target=target
          self.ssid=ssid[0]
          self.wpakey=wpakey
          self.log=log
          self.running=True
      def run(self):
          #try:
          WIFIMutex.acquire()
          log('WIFI function test')
          self.msg=WIFITest(self.target,self.ssid,self.wpakey)
          #except:
          #    self.msg='WIFI function test abnormal termination' 
          if WIFIMutex.locked: 
             WIFIMutex.release()
          print self.msg
          log(self.msg)
          self.running=False
     
def WIFITest(target,ssid,wpakey):
    print 'WIFI function to start the test'
    Connected=''
    msg='WIFI function test : FAIL'
    for i in range(3):
        if not Connected:
           Connected=SetDongleConnection(ssid,wpakey)
        if Connected:
           try:
               print '%s to wait for wireless connectivity'%target
               if htx.IsConnect(target,20):   
                  print 'Ping function to start the test'
                  value = Ping(target,1024,10,200)
               else:
                  value=200
           except ValueError:
               value=200
           if value > ping_loss:
              if value == 200:
                 Connected='' 
           else:
              msg='WIFI function test : PASS'
              break              
    return msg
          
def SetDongleConnection(ssid,wpakey):
    WIFI_Adapter_ID=0
    p = Popen('c:\\TermScript\\wifi_link.exe', stdout=PIPE, stdin=PIPE, stderr=STDOUT,shell=True)
    grep_stdout = p.communicate(input= '%s\n%s\n%s\n'%(WIFI_Adapter_ID,ssid,wpakey))[0]   
    if 'Success' in grep_stdout:
       return 1
    return 0


class WIFIThread_SMCD3GNVtelnet(threading.Thread):
      def __init__(self,id,ssid,wpakey,wifi_target,packetsize,ping_loss,log):
          threading.Thread.__init__(self)
          self.id=id
          self.wifi_id=int((id-1)/2)
          self.ssid=ssid[0]
          #self.wpakey=wpakey[0]
          self.wpakey=wpakey
          self.wifi_target=wifi_target
          self.packetsize = packetsize
          self.ping_loss = ping_loss
          self.running=True
          self.mainrunning=True
          self.msg=[1,'[%s]wifi error,no test'%self.ssid]
      def run(self):
          try:              
              WIFIMutex[0].acquire()
              print '[%s]WIFI function to start the test'%self.ssid
              Connected=''
              testflag=1
              value='[%s]wifi error,no test'%self.ssid
              for i in range(10):
                  if self.mainrunning:
                      if not Connected:
                         print self.ssid
                         print self.wpakey
                         Connected=SetDongleConnection(self.ssid,self.wpakey)
                      #Connected=WLAN(self.ssid).connect()
                      print Connected
                      if Connected:
                         try:
                             print '%s to wait for wireless connectivity'%self.wifi_target
                             os.system('arp -d')
                             if htx.IsConnect(self.wifi_target,50):   
                                print 'Ping function to start the test'
                                value = FPing(self.wifi_target,self.packetsize,100,10)
                                #value = Ping(self.wifi_target,self.packetsize,10,800)
                                print '#############################'
                                print value
                                print '#############################'
                             else:
                                value=200
                         except ValueError:
                             value=200
                         if value > self.ping_loss:
                            if value == 200:
                               Connected='' 
                         if value < self.ping_loss:
                            testflag=0
                            break
              self.msg= testflag,value
              print 'msg:%s'%self.msg
          except:
             pass
          if WIFIMutex[0].locked():
             WIFIMutex[0].release()
          self.running=False                   



                
        

def StartService():
    if not dll.GetWIFIServiceStatus():
       dll.SetWIFIServiceStatus(1)

def RefreshAdapters():
    ad_num=dll.EnumerateAdapters()
    adapter=[]
    buf=ctypes.c_buffer(256)
    if ad_num > 0 and ad_num < ERROR_OFFSET:
       for ad in range(ad_num):
           dll.GetAdapterName(ad,buf,len(buf))
           adapter.append(buf.value)
    return adapter

def ScanWifiSignal(ad):
    networks=[]
    ssid=ctypes.c_buffer(256)
    d1=ctypes.c_int()
    d2=ctypes.c_int()
    d3=ctypes.c_int()
    d4=ctypes.c_int()
    d5=ctypes.c_int()
    d6=ctypes.c_int()
    net_num=dll.EnumerateAvailableNetworks(ad,1)
    if net_num > 0 and net_num < ERROR_OFFSET:
       for net_c in range(net_num):
           dll.GetAvailableNetworkName(ad, net_c, ssid, len(ssid))
           dll.GetAvailableNetworkMac(ad, net_c, byref(d1), byref(d2), byref(d3), byref(d4), byref(d5), byref(d6))
           wtype=dll.GetAvailableNetworkType(ad,net_c)
           if wtype==1:
              wtype='Infrastructure'
           elif wtype==2:
              wtype='ad hoc'
           else:
              wtype=''
           signal=dll.GetAvailableNetworkSignalQuality(ad,net_c)
           if signal < ERROR_OFFSET:
              signal = '%s'%signal
           else:signal = '0'
           Rssi=dll.GetAvailableNetworkRSSI(ad,net_c)
           if Rssi < ERROR_OFFSET:
              Rssi = '%s db'%Rssi
           else:Rssi = '0 db'    
           Secure=dll.IsAvailableNetworkSecure(ad,net_c)
           if Secure==0:
              Secure='NO'
           elif Secure==1:
              Secure='YES'
           else:Secure='' 
           AuthMode=dll.GetAvailableNetworkAuthMode(ad,net_c)
           if AuthMode==0:AuthMode='Open'
           elif AuthMode==1:AuthMode='Shared'
           elif AuthMode==2:AuthMode='AutoSwitch'
           elif AuthMode==3:AuthMode='WPA'
           elif AuthMode==4:AuthMode='WPAPSK'
           elif AuthMode==5:AuthMode='WPANone'
           elif AuthMode==6:AuthMode='WPA2'
           elif AuthMode==7:AuthMode='WPA2PSK'
           else: AuthMode=''
           CipherMode=dll.GetAvailableNetworkCipherMode(ad,net_c)
           if CipherMode==0:CipherMode='None'
           elif CipherMode==1:CipherMode='WEP 40 bits'
           elif CipherMode==2:CipherMode='TKIP'
           elif CipherMode==4:CipherMode='AES'
           elif CipherMode==5:CipherMode='WEP 104 bits'
           elif CipherMode==0x100:CipherMode='WPA Group'
           elif CipherMode==0x101:CipherMode='WEP'
           else: CipherMode=''
           Channel=dll.GetAvailableNetworkChannel(ad,net_c)
           if Channel < ERROR_OFFSET:
              Channel= '%s'%Channel
           else:Channel=''
           #networks.append([ssid.value,'%02X%02X%02X%02X%02X%02X'%(d1.value,d2.value,d3.value,d4.value,d5.value,d6.value),
           #                 wtype,signal,Rssi,Secure,AuthMode,CipherMode,Channel]) 
           networks.append([ssid.value,'%02X%02X%02X%02X%02X%02X'%(d1.value,d2.value,d3.value,d4.value,d5.value,d6.value),signal,Rssi])
    return networks         

