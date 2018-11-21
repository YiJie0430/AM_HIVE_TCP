# -*- coding:BIG5-*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 30 2011)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx,cStringIO,os,sys,ConfigParser
import wx.xrc,thread
#from TCPService import TCPService
#from tftp import tftpcfg, tftp_engine
#import htx_wifi
sys.path.append(os.getcwd())
from Function import *
log_lock = thread.allocate_lock()  
###########################################################################
## Class MyFrame1
###########################################################################
execfile("config.ini")
if os.path.isfile('c:\\station.ini'):
   execfile('c:\\station.ini')


    
def GetCableLoss():
    import glob   
    return "Table"


    
    

class AtherosFrame ( wx.Frame ):
      def __init__( self ):
          wx.Frame.__init__ ( self, None, id = wx.ID_ANY, title = '%s  |  Version: %s'%(StationCaption,version), pos = wx.DefaultPosition, size = wx.Size( 620,650 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
          #self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
          self.SetBackgroundColour( wx.Colour( 0xcc,0xee,0xdd ))
          #IconStream='\x00\x00\x01\x00\x01\x00  \x10\x00\x00\x00\x00\x00\xe8\x02\x00\x00\x16\x00\x00\x00(\x00\x00\x00 \x00\x00\x00@\x00\x00\x00\x01\x00\x04\x00\x00\x00\x00\x00\x80\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x80\x00\x00\x00\x80\x80\x00\x80\x00\x00\x00\x80\x00\x80\x00\x80\x80\x00\x00\x80\x80\x80\x00\xc0\xc0\xc0\x00\x00\x00\xff\x00\x00\xff\x00\x00\x00\xff\xff\x00\xff\x00\x00\x00\xff\x00\xff\x00\xff\xff\x00\x00\xff\xff\xff\x00\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\x00\x00\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\x00\x00\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\x00\x00\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\x00\x00\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\x00\x00\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\x00\x00\x00\x00\x00\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\x00\x00\x00\x00\x00\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\x00\x00\x00\x00\x00\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\x00\x00\x00\x00\x00\x00\n\xaa\xa0\n\xaa\xa0\n\xaa\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\xaa\xa0\n\xaa\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\xaa\xa0\n\xaa\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\xaa\xa0\n\xaa\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\xaa\xa0\n\xaa\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\xaa\xa0\n\xaa\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\xaa\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\xaa\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\xaa\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\xaa\xa0\xe1\x86\x18a\xe1\x86\x18a\xe1\x86\x18a\xe1\x86\x18a\xe1\x86\x18a\xe1\x86\x18a\xe1\x86\x18a\xe1\x86\x18a\xe1\x86\x18a\xe1\x86\x18a\xe1\x86\x18a\xe1\x86\x18a\xe1\x86\x18a\xe1\x86\x18a\xff\x86\x18a\xff\x86\x18a\xff\x86\x18a\xff\x86\x18a\xff\x86\x18a\xff\xfe\x18a\xff\xfe\x18a\xff\xfe\x18a\xff\xfe\x18a\xff\xff\xf8a\xff\xff\xf8a\xff\xff\xf8a\xff\xff\xf8a\xff\xff\xf8a\xff\xff\xff\xe1\xff\xff\xff\xe1\xff\xff\xff\xe1\xff\xff\xff\xe1'
          #stream = cStringIO.StringIO(IconStream)         
          #icon = wx.EmptyIcon()
          #icon.CopyFromBitmap(wx.BitmapFromImage(wx.ImageFromStream(stream)))
          icon = wx.Icon('images/ico.ico',wx.BITMAP_TYPE_ICO)
          self.SetIcon(icon) 
          
          bSizer1 = wx.BoxSizer( wx.VERTICAL )
          bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
          self.m_bitmap3 = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 130,40 ), 0 )
          img=wx.Image('images/hitron_logol.png')
          img.Rescale(130,40)
          #self.m_bitmap3.SetBitmap( wx.BitmapFromImage(img))
          #bSizer2.Add( self.m_bitmap3, 0, wx.ALL, 5 )
          ###########capiton###########
          self.Caption = wx.StaticText( self, wx.ID_ANY, StationCaption , wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
          self.Caption.Wrap( -1 )
          self.Caption.SetFont( wx.Font( 18, 74, 90, 92, False, "Tahoma" ) )
          bSizer2.Add( self.Caption, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
          bSizer1.Add( bSizer2, 0, wx.EXPAND|wx.ALL, 5 )
          ###########################
          self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
          bSizer1.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )
          bSizer3 = wx.BoxSizer( wx.VERTICAL )
          bSizer4 = wx.BoxSizer( wx.HORIZONTAL )
          ############station##############
          self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Station:", wx.DefaultPosition, wx.DefaultSize, 0 )
          self.m_staticText4.Wrap( -1 )
          self.m_staticText4.SetFont( wx.Font( 10, 74, 90, 90, False, "Tahoma" ) )
          bSizer4.Add( self.m_staticText4, 0, wx.ALL, 5 )
          self.station = wx.StaticText( self, wx.ID_ANY, u"%s"%Teststation, wx.DefaultPosition, wx.Size( 100,-1 ), wx.ALIGN_CENTRE )
          self.station.Wrap( -1 )
          self.station.SetFont( wx.Font( 10, 74, 90, 90, False, "Tahoma" ) )
          self.station.SetBackgroundColour( wx.Colour( 255, 255, 208 ) )
          bSizer4.Add( self.station, 0, wx.ALL, 5 )
          bSizer3.Add( bSizer4, 0, wx.EXPAND, 5 )
          bSizer41 = wx.BoxSizer( wx.HORIZONTAL )
          ###############IC Type###############
          self.m_staticText41 = wx.StaticText( self, wx.ID_ANY, u"Model:  ", wx.DefaultPosition, wx.DefaultSize, 0 )
          self.m_staticText41.Wrap( -1 )
          self.m_staticText41.SetFont( wx.Font( 10, 74, 90, 90, False, "Tahoma" ) )
          bSizer41.Add( self.m_staticText41, 0, wx.ALL, 5 )
          self.ICType = wx.StaticText( self, wx.ID_ANY, u"%s"%dut_model, wx.DefaultPosition, wx.Size( 100,-1 ), wx.ALIGN_CENTRE )
          self.ICType.Wrap( -1 )
          self.ICType.SetFont( wx.Font( 10, 74, 90, 90, False, "Tahoma" ) )
          self.ICType.SetBackgroundColour( wx.Colour( 255, 255, 208 ) )
          bSizer41.Add( self.ICType, 0, wx.ALL, 5 )
          bSizer3.Add( bSizer41, 0, wx.EXPAND, 5 )
          
          ###############IQ Port###############
          '''
          bSizer411 = wx.BoxSizer( wx.HORIZONTAL )
          self.m_staticText411 = wx.StaticText( self, wx.ID_ANY, u"IQ Port:  ", wx.DefaultPosition, wx.DefaultSize, 0 )
          self.m_staticText411.Wrap( -1 )
          self.m_staticText411.SetFont( wx.Font( 10, 74, 90, 90, False, "Tahoma" ) )
          bSizer411.Add( self.m_staticText411, 0, wx.ALL, 5 )
          self.IQPort = wx.StaticText( self, wx.ID_ANY, u"%s"%IQPort, wx.DefaultPosition, wx.Size( 100,-1 ), wx.ALIGN_CENTRE )
          self.IQPort.Wrap( -1 )
          self.IQPort.SetFont( wx.Font( 10, 74, 90, 90, False, "Tahoma" ) )
          self.IQPort.SetBackgroundColour( wx.Colour( 255, 255, 208 ) )
          bSizer411.Add( self.IQPort, 0, wx.ALL, 5 )
          bSizer3.Add( bSizer411, 0, wx.EXPAND, 5 )   
          bSizer4111 = wx.BoxSizer( wx.HORIZONTAL ) 
          ''' 
          
          ###############Target Power###############
          #self.m_staticText4111 = wx.StaticText( self, wx.ID_ANY, u"Target Power: ", wx.DefaultPosition, wx.DefaultSize, 0 )
          #self.m_staticText4111.Wrap( -1 )
          #self.m_staticText4111.SetFont( wx.Font( 10, 74, 90, 90, False, "Tahoma" ) )
          #bSizer4111.Add( self.m_staticText4111, 0, wx.ALL, 5 )
          #self.TargetPower = wx.StaticText( self, wx.ID_ANY, u"%s dbm"%GetTargetPower(), wx.DefaultPosition, wx.Size( 65,-1 ), wx.ALIGN_CENTRE )
          #self.TargetPower.Wrap( -1 )
          #self.TargetPower.SetFont( wx.Font( 10, 74, 90, 90, False, "Tahoma" ) )
          #self.TargetPower.SetBackgroundColour( wx.Colour( 255, 255, 208 ) )
          #bSizer4111.Add( self.TargetPower, 0, wx.ALL, 5 )
          #bSizer3.Add( bSizer4111, 0, wx.EXPAND, 5 )
          
          
          ###############Cable loss file###############
          bSizer41111 = wx.BoxSizer( wx.HORIZONTAL )
          '''
          self.m_staticText41111 = wx.StaticText( self, wx.ID_ANY, u"Cable Loss Path:", wx.DefaultPosition, wx.DefaultSize, 0 )
          self.m_staticText41111.Wrap( -1 )
          self.m_staticText41111.SetFont( wx.Font( 10, 74, 90, 90, False, "Tahoma" ) )
          bSizer41111.Add( self.m_staticText41111, 0, wx.ALL, 5 )
          self.CableLossFile = wx.StaticText( self, wx.ID_ANY, u"%s    "%ReadCompensation("pathloss","Station.Cal")[0].strip(), wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
          self.CableLossFile.Wrap( -1 )
          self.CableLossFile.SetFont( wx.Font( 10, 74, 90, 90, False, "Tahoma" ) )
          self.CableLossFile.SetBackgroundColour( wx.Colour( 255, 255, 208 ) )
          bSizer41111.Add( self.CableLossFile, 0, wx.ALL, 5 )
          '''
          ########## Cable Loss Calibrate ##############
          #bSizer41111.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
          '''
          self.Btn_StationCal = wx.Button( self, wx.ID_ANY, u"Cable Loss Calibrate", wx.DefaultPosition, wx.DefaultSize, 0 )
          bSizer41111.Add( self.Btn_StationCal, 0, wx.ALL, 5 )
          '''
          bSizer3.Add( bSizer41111, 0, wx.EXPAND, 5 )
          self.m_staticline3 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
          bSizer3.Add( self.m_staticline3, 0, wx.EXPAND |wx.ALL, 5 )
          bSizer1.Add( bSizer3, 0, wx.EXPAND|wx.ALL, 5 )
          bSizer20 = wx.BoxSizer( wx.VERTICAL )
          bSizer41112 = wx.BoxSizer( wx.HORIZONTAL )
          self.m_staticText41112 = wx.StaticText( self, wx.ID_ANY, u"MAC:  ", wx.DefaultPosition, wx.DefaultSize, 0 )
          self.m_staticText41112.Wrap( -1 )
          self.m_staticText41112.SetFont( wx.Font( 10, 74, 90, 90, False, "Tahoma" ) )
          bSizer41112.Add( self.m_staticText41112, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
          self.MAC = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 110,-1 ), wx.TE_PROCESS_ENTER  )
          #self.MAC = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 110,-1 ), 0 )
          self.MAC.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
          self.MAC.SetBackgroundColour( wx.Colour( 255, 255, 0 ) )
          bSizer41112.Add( self.MAC, 0, wx.ALL, 5 )
          #bSizer41112.AddSpacer( ( 235, 0), 0, wx.EXPAND, 5 )
          if start_button:
               self.m_start = wx.Button( self, wx.ID_OK, u"START", wx.DefaultPosition, wx.Size( 130,-1 ), wx.TE_PROCESS_ENTER )
               bSizer41112.Add( self.m_start, 0, wx.ALL, 5 )
               #bSizer41112.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
          bSizer20.Add( bSizer41112, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
          bSizer411121 = wx.BoxSizer( wx.HORIZONTAL )
          self.m_staticText411121 = wx.StaticText( self, wx.ID_ANY, u"SSID:   ", wx.DefaultPosition, wx.DefaultSize, 0 )
          self.m_staticText411121.Wrap( -1 )
          self.m_staticText411121.SetFont( wx.Font( 10, 74, 90, 90, False, "Tahoma" ) )
          bSizer411121.Add( self.m_staticText411121, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
          self.SSID = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 110,-1 ), wx.TE_PROCESS_ENTER  )
          #self.SSID = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 110,-1 ), 0 )
          self.SSID.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
          self.SSID.SetBackgroundColour( wx.Colour( 255, 255, 0 ) )
          bSizer411121.Add( self.SSID, 0, wx.ALL, 5 )
          #bSizer411121.AddSpacer( ( 10, 0), 0, wx.EXPAND, 5 )
          #self.m_staticText4111211 = wx.StaticText( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0 )
          #self.m_staticText4111211.Wrap( -1 )
          #self.m_staticText4111211.SetFont( wx.Font( 10, 74, 90, 90, False, "Tahoma" ) )
          #bSizer411121.Add( self.m_staticText4111211, 0, wx.ALL, 5 )
          #self.pswd = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 110,-1 ), wx.TE_PROCESS_ENTER  )
          #self.pswd = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 110,-1 ), 0 )
          #self.pswd.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
          #self.pswd.SetBackgroundColour( wx.Colour( 255, 255, 0 ) )
          #bSizer411121.Add( self.pswd, 0, wx.ALL, 5 )
          #bSizer411121.AddSpacer( ( 30, 0), 0, wx.EXPAND, 5 )
          self.Result = wx.StaticText( self, wx.ID_ANY, u"Result", wx.DefaultPosition, wx.Size( 130,-1 ), wx.ALIGN_CENTRE )
          self.Result.Wrap( -1 )
          self.Result.SetFont( wx.Font( 12, 74, 90, 92, False, "Tahoma" ) )
          self.Result.SetBackgroundColour( wx.Colour( 0, 255, 0 ) )
          bSizer411121.Add( self.Result, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
          
     
     
           
          bSizer20.Add( bSizer411121, 1, wx.EXPAND, 5 ) 
          self.m_staticline4 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
          bSizer20.Add( self.m_staticline4, 0, wx.EXPAND |wx.ALL, 5 )     
          bSizer1.Add( bSizer20, 0, wx.EXPAND, 5 )      
          ############### Log ###############   
          self.Log = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_TAB|wx.TE_MULTILINE
                                                                                              |wx.HSCROLL|wx.TE_RICH2|wx.TE_READONLY
                                                                                              |wx.HSCROLL|wx.VSCROLL )
          self.Log.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
          self.Log.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
          self.Log.SetBackgroundColour( wx.Colour( 0, 0, 0 ) )          
          bSizer1.Add( self.Log, 1, wx.ALL|wx.EXPAND, 5 )          
          self.SetSizer( bSizer1 )
          self.Layout()          
          self.Centre( wx.BOTH ) 
          self.buf = ''
          #self.run_cart=False
          
          #self.InitailFixtureBoard()
          self.SSID.Enable(False)
          #self.pswd.Enable(True)
          self.running = True
          #self.MAC.Bind( wx.EVT_TEXT_ENTER, self.Scan_lbl_ssid )
          #self.SSID.Bind( wx.EVT_TEXT_ENTER, self.Scan_lbl_pwd )
          if start_button:
               self.MAC.Bind( wx.EVT_TEXT_ENTER, self.OnFocusStart)
               self.Bind(wx.EVT_BUTTON, self.scan, self.m_start)
          else: 
               self.MAC.Bind( wx.EVT_TEXT_ENTER, self.scan1)
             #self.pswd.Bind(wx.EVT_TEXT_ENTER, self.scan1)
          self.Bind( wx.EVT_CLOSE, self.close )
          self.MAC.SetValue("688F2E470700")
          '''
          if station_cal: 
              self.Btn_StationCal.Enable(True)          
              self.Btn_StationCal.Bind( wx.EVT_BUTTON, self.CableLossCalibrate )
          '''    
          
          '''
          ##########inint tcp and tftp service############
          #os.popen("TASKKILL /F /IM cart.exe /T")
          self.tcps = TCPService(self)
          self.tcps.start()
          configFile=ConfigParser.SafeConfigParser()
          if configFile.read('tftp.ini'):
             configFile.set('TFTPSERVER','tftprootfolder',tftp_dir_path)
             fp=open('tftp.ini','w')
             configFile.write(fp)
             fp.close()
          cfgdict = tftpcfg.getconfigstrict(os.getcwd, 'tftp.ini')
          self.TFTPServer = tftp_engine.ServerState(**cfgdict)
          thread.start_new_thread(tftp_engine.loop_nogui, (self.TFTPServer,))     
          '''
      def OnFocusStart(self,event):
          self.m_start.SetFocus()

      def ShowResult(self,val):
          color = {"PASS":wx.Colour( 0, 255, 0 ),
                   "FAIL":wx.Colour( 255, 0, 0 ),
                   "START":wx.Colour( 255, 255, 0 )
                  }
          self.Result.SetBackgroundColour(color[val])  
          if val=="START":
             self.Log.SetValue("")
             val="Running" 
             self.MAC.Enable(False) 
             self.SSID.Enable(False)
             #self.pswd.Enable(False)
             if start_button: self.m_start.Enable(False)
             #self.Btn_StationCal.Enable(False)
          else:
             self.MAC.Enable(True)
             #self.SSID.Enable(True)
             #self.pswd.Enable(True)
             if start_button: self.m_start.Enable(True)
             #self.Btn_StationCal.Enable(True)
             time.sleep(0.1)
             self.MAC.SetFocus()
             self.MAC.SetSelection(-1,-1)

          self.Result.SetLabel("     %s     "%val)
          
      def SendMessage(self,val,log=None,state="",color=0,uart=None):
          colors=[(255,255,255),(255,0,0),(0,255,0)]
          log_lock.acquire()
          beg = self.Log.GetLastPosition()
          end = self.Log.GetLastPosition() + len(val)
          self.Log.SetStyle(beg,end,wx.TextAttr(colors[color],'black'))
          self.Log.AppendText(val)
          self.Log.ShowPosition(end)
          log_lock.release()
          
          if log:log.write(val)
          if uart: uart<<'echo "%s" >> %s'%(val,mfg_log)
          if state in ("PASS","FAIL","START"):
             self.ShowResult(state)
      def Scan_lbl_ssid(self,evt):
          '''
          self.SSID.Enable(True)
          time.sleep(0.1)
          self.SSID.SetFocus()
          self.SSID.SetSelection(-1,-1) 
          '''
          pass
      
      def Scan_lbl_pwd(self,evt):
          
          self.pswd.Enable(True)
          time.sleep(0.1)
          self.pswd.SetFocus()
          self.pswd.SetSelection(-1,-1) 
               
          pass

      def scan_start(self,evt):
          time.sleep(0.1)
          self.m_start.SetFocus()
          self.m_start.SetDefault()
          #self.m_start.SetSelection(-1,-1)

      def scan(self,evt):
          self.m_start.Enable(False)
          thread.start_new_thread(eval(FunctionName),(self,))
          self.MAC.SetFocus()
          self.MAC.SetSelection(-1,-1)

      def scan1(self,evt):
          thread.start_new_thread(eval(FunctionName),(self,))
          self.MAC.SetFocus()
          self.MAC.SetSelection(-1,-1)
      '''
      def CableLossCalibrate(self,evt):  
          thread.start_new_thread(PathCalibrate,(self,))
      ''' 
      
      def InitailFixtureBoard(self):
          term =htx.SerialTTY(comport[0],b_rate)
          lWaitCmdTerm(term,"",'#',3)
          lWaitCmdTerm(term,"cd /nvram/",'#',3)    
          data = lWaitCmdTerm(term,"ls",'#',3)
          if "wds_fixture.sh" not in data:
              self.MessageBox('No shell script file: wds_fixture.sh','Check file',wx.OK|wx.ICON_ERROR) 
              self.SendMessage( "Test Result:FAIL"+'\n',log,color=1)
          else:
              term << ". wds_fixture.sh"
              time.sleep(1)
              term.close() 
              if not IsDisconnect(ftx_ip["eth0"],30):  raise Except("FAIL: DUT apdown Fail")
              
                                                                                      
      def close( self,evt ):
          try:
              self.TFTPServer.shutdown()
              if self.running:
                 self.running = False
                 self.tcps.close()
          except:
              pass
          sys.exit(1)
      
      
      def MessageBox(self,content,title,msg_type):
          dlg = wx.MessageDialog(self,content, title, msg_type)
          result = dlg.ShowModal()
          dlg.Destroy()  
          return result 
      '''
      def MessageBox(self,msg,title,style):
          MessageBox = windll.user32.MessageBoxA
          return MessageBox(0,'%s'%msg,'%s'%title,style)
      '''


################################
#          Main Code           #
################################     
class App(wx.App):
    def OnInit(self):
        try:
            self.main = AtherosFrame()
            self.main.Show(True)
            self.SetTopWindow(self.main)
        except Exception,e:
            print e
        return True
        
if __name__ == '__main__':
   application = App(0)
   application.MainLoop()
