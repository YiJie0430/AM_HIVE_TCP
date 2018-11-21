import os,time,traceback
from testlibs import *
from toolslib import *
from htx import Win32Message
import wx
import random
from WLAN import *

execfile("config.ini")
if os.path.isfile('c:\\station.ini'):
    execfile('c:\\station.ini')


def GetMacAddress(parent):
    val = parent.MAC.GetValue()
    try:
        #if len(val) == 12 and int(val,16):
        if (len(val) == 12 or len(val) == 10):
           return val
    except ValueError:
           pass
    raise Except("Input Label Error %s !"%val)

def GetSN(parent):
    val = parent.SN.GetValue()
    try:
        #if len(val) == 12 and int(val,16):
        if (len(val) == 12 or len(val) == 10):
           return val
    except ValueError:
           pass
    raise Except("Input Label Error %s !"%val)

def lWaitCmdTcp(parent,cmd,waitstr,timeout=10):
    s = time.time()
    while time.time() - s < timeout:
          if waitstr in parent.tcps.buf:
             if cmd:parent.tcps.set(cmd)
             return 0
    raise Except("failed :%s,%s"%(cmd,waitstr))         

def lWaitTcpBuf(parent,waitstr,timeout=10):
    s = time.time()
    while time.time() - s < timeout:
          if waitstr in parent.tcps.buf:
             return 1
    return 0

def TelnetLogin(term,username=None,password=None):
    print "Telnet Login..."
    data = term.wait('#',5)

def CheckUSB(parent,term,log):
    test_time = time.time()
    parent.SendMessage("USB Test Start...\n" ,log)
    test_fail = 0
    usb_id = 0
    for i in ['--bh-atom','--ap-atom']:  
    #for i in ['--bh-atom']:       
        data = lWaitCmdTerm(term,"ht_iwcmd mount %s"%i,"sda",5,3)
        time.sleep(0.5)
        #print data
        if 'sda1' not in data:
            parent.SendMessage("FAIL: USB %d Mount\n"%usb_id ,log,color=1)
            test_fail+=1
        else:
            usb_path = data.split("sda1 on")[-1].split("type vfat")[0].strip() 
            term.get()
            #term << "ht_iwcmd cp %s/%s /tmp %s"%(usb_path,usb_file_name,i)
            t = time.time() 
            lWaitCmdTerm(term,"ht_iwcmd cp %s/%s /tmp %s"%(usb_path,usb_file_name,i),"#",10)
            t_toatl = time.time() - t
            #speed = (55469492/t_toatl)*8/1000000.0
            speed = (110939472/t_toatl)*8/1000000.0
            data = lWaitCmdTerm(term,"ht_iwcmd ls /tmp/ %s"%i,"#",10)
            if usb_file_name not in data: 
                parent.SendMessage("FAIL: USB %d Test\n"%usb_id ,log,color=1)
                test_fail+=1
            else:
                lWaitCmdTerm(term,"ht_iwcmd rm /tmp/%s %s"%(usb_file_name,i),"#",10)
                parent.SendMessage('USB file transfer speed = %.3f\n'%speed,color=2) 
                parent.SendMessage('USB %d Test: PASS (PASS)\n'%usb_id,color=2)
    if test_fail > 0: raise Except ("USB Test FAIL")
    '''
    test_fail = 0
    for i in ['--bh-atom','--ap-atom']: 
        term.get()
        data = lWaitCmdTerm(term,"ht_iwcmd cat /sys/bus/usb/devices/usb1/speed %s"%i,"#",5,3)
        speed = int(data.split('\n')[1].strip())
        msg = 'USB%d check speed = %d ( %d ) Mbps\n'%(usb_id,speed,usb_speed)
        if  speed <> usb_speed:
            test_fail+=1
            parent.SendMessage(msg,log,color=1)
        else: parent.SendMessage(msg,log,color=2) 
        usb_id+=1
    if test_fail > 0: raise Except ("USB Speed Check FAIL")
    '''
    parent.SendMessage( "USB Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)

def CheckPcieDevice(parent,term,log):
    test_time = time.time()
    parent.SendMessage("PCIE Device Check Start...\n" ,log)
    test_fail = 0
    msg = [None,None]
    c = 0
    for i in ['bh','ap']:
        for j in range(3):
            term.get()
            data = ""
            data = lWaitCmdTerm(term,"ht_iwcmd lspci -mk --%s-atom"%i,"#",3,3)
            #print data
            #device = data.count('wdev%1d')
            device = data.count(lspci_msg[i]) 
            msg[c] = "%s PCIE Device = %d (%d)"%(i.upper(),device,wifi_device[c])
            if device <> wifi_device[c]:                
                term.get()
                time.sleep(0.5)
                if j == 2:
                    parent.SendMessage("%s\n"%msg[c] ,log,color=1)
                    for k in eval('%s_pci'%i).keys():
                      if k not in data: parent.SendMessage('%s detect FAIL\n'% eval('%s_pci'%i)[k],color=1) 
                    test_fail+=1
                else:
                    continue 
                
            else:
                parent.SendMessage('%s\n'%msg[c],color=2) 
                break
                    
        c +=1    
    if test_fail > 0: raise Except ("PCIE Device Check FAIL") 
    parent.SendMessage( "PCIE Device Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)

def CheckSensor(parent,term,log):
    test_time = time.time()
    parent.SendMessage("Sensor Test Start...\n" ,log)
    #Cli_Manufacture(term,10)
    if 'Manufacture>' not in lWaitCmdTermOutput(term,"","Manufacture>",3):
        lWaitCmdTerm(term,"cli","mainMenu>",10)
        lWaitCmdTerm(term,"Manu","Manufacture>",5)
    data = lWaitCmdTerm(term,"getSensor","Manufacture>",5)
    get_tmp = float(data.split('(local):')[-1].split('\n')[0].strip())
    msg = 'BH Temperature (local)= %.2f (%d ~ %d)'%(get_tmp,chip_temperature[0],chip_temperature[1]) 
    if get_tmp < chip_temperature[0] or get_tmp > chip_temperature[1]: 
        raise Except("FAIL: " + msg)
    parent.SendMessage(msg + "\n" ,log,color=2)    
    get_tmp = float(data.split('(remote):')[-1].split('\n')[0].strip())
    msg = 'AP Temperature (remote)= %.2f (%d ~ %d)'%(get_tmp,chip_temperature[0],chip_temperature[1]) 
    if get_tmp < chip_temperature[0] or get_tmp > chip_temperature[1]: 
        raise Except("FAIL: " + msg)
    parent.SendMessage(msg + "\n" ,log,color=2)    
    
    ap_term =htx.Telnet(target_ap)
    TelnetLogin(ap_term,username=None,password=None)
    #Cli_Manufacture(ap_term,10)
    lWaitCmdTerm(ap_term,"cli","mainMenu>",10)
    lWaitCmdTerm(ap_term,"Manu","Manufacture>",5)
    data = lWaitCmdTerm(ap_term,"getSensor","Manufacture>",5)
    get_hmd = float(data.split('Humidity:')[-1].split('%')[0].strip())
    msg = 'AP Humidity= %.2f (%d ~ %d)'%(get_hmd,humidy[0],humidy[1]) 
    if get_hmd < humidy[0] or get_hmd > humidy[1]: 
        raise Except("FAIL: " + msg)
    parent.SendMessage(msg + "\n" ,log,color=2)
    
    get_tmp = float(data.split('Temperature:')[-1].split('\n')[0].strip())
    msg = 'AP Temperature= %.2f (%d ~ %d)'%(get_tmp,evm_temperature[0],evm_temperature[1]) 
    if get_tmp < evm_temperature[0] or get_tmp > evm_temperature[1]: 
        raise Except("FAIL: " + msg)
    parent.SendMessage(msg + "\n" ,log,color=2)
    
    get_psr = float(data.split('Pressure:')[-1].split('mbar')[0].strip())
    msg = 'AP Pressure= %.2f (%d ~ %d)'%(get_psr,pressure[0],pressure[1]) 
    if get_psr < pressure[0] or get_psr > pressure[1]: 
        raise Except("FAIL: " + msg)
    parent.SendMessage(msg + "\n" ,log,color=2)
    ap_term.close()
    
    parent.SendMessage( "Sensor Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)


def NvmProgram(parent,term,mac,sn,log):
    print mac, sn
    test_time = time.time()
    parent.SendMessage("Set NVM Parameter Start...\n" ,log)
    if 'Manufacture>' not in lWaitCmdTermOutput(term,"","Manufacture>",3):
        lWaitCmdTerm(term,"cli","mainMenu>",10)
        lWaitCmdTerm(term,"Manu","Manufacture>",5)
    lWaitCmdTerm(term,"macAddr %s"%mac ,"Manufacture>",3)
    parent.SendMessage( "Set Main MAC Address: %s \n"%mac ,log)
    lWaitCmdTerm(term,"setSN %s"%sn ,"Manufacture>",3)
    parent.SendMessage( "Set Serial Number: %s \n"%sn ,log) 
    lWaitCmdTerm(term,"sethwver %s %s"%(hw_ver[0],hw_ver[1]),"saved",3)
    parent.SendMessage( "Set HW Version: %s %s\n"%(hw_ver[0],hw_ver[1]) ,log)
    #lWaitCmdTerm(term,"top","mainMenu>",3)
    #lWaitCmdTerm(term,"exit","#",3)
    parent.SendMessage( "Set NVM Parameter time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)
    
def ChangeSSID(parent,term,log):
    test_time = time.time()
    parent.SendMessage("Change SSID Start...\n" ,log)
    if 'Manufacture>' not in lWaitCmdTermOutput(term,"","Manufacture>",3):
        lWaitCmdTerm(term,"cli","mainMenu>",10)
        lWaitCmdTerm(term,"Manu","Manufacture>",5)
    for i in range(len(ssid_list)):  
        lWaitCmdTerm(term,"wls_ssid_name %d 1 %s_%d"%(i+1,ssid_list[i],station_id),"Manufacture>",8,3)
        parent.SendMessage('Change WIFI SSID %s_%d OK\n'%(ssid_list[i],station_id),log)
    lWaitCmdTerm(term,"top","mainMenu>",3)
    lWaitCmdTerm(term,"exit","#",3)
    parent.SendMessage( "Change WIFI SSID time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)
    
    
def CheckNvm(parent,term,mac,sn,log):
    print mac, sn
    test_time = time.time()
    parent.SendMessage("Check NVM Parameter Start...\n" ,log)
    if 'Manufacture>' not in lWaitCmdTermOutput(term,"","Manufacture>",3):
        lWaitCmdTerm(term,"cli","mainMenu>",10)
        lWaitCmdTerm(term,"Manu","Manufacture>",5) 
    data = lWaitCmdTerm(term,"ven","Manufacture>",5)
    #get_mac = data.split("LAN MAC Address:")[-1].split('LAN MAC')[0].strip()
    #get_mac = data.split("LAN MAC Address:")[-1].split('\n')[0].strip()
    #get_mac = "".join(get_mac.split(':')) 
    #mac = "%012X"%(int(mac,16)+1)  
    #msg = "Get LAN MAC Address = %s (%s)"%(get_mac,mac)
    #if get_mac <> mac: raise Except("FAIL: " + msg)
    #parent.SendMessage( msg + "\n" ,log,color=2)
    
    get_sn = data.split("Serial Number:")[-1].split('------------Version')[0].strip()
    msg = "Get Serial Number = %s (%s)"%(get_sn,sn)
    if get_sn <> sn: raise Except("FAIL: " + msg)
    parent.SendMessage( msg + "\n" ,log,color=2)
    
    get_hw = data.split("Hardware Version:")[-1].split('Software Version')[0].strip()
    msg = "Get HW version = %s (%s%s)"%(get_hw,hw_ver[0],hw_ver[1])
    if get_hw <> '%s%s'%(hw_ver[0],hw_ver[1]): raise Except("FAIL: " + msg)
    parent.SendMessage( msg + "\n" ,log,color=2)
    
    get_sw = data.split("Software Version:")[-1].split('S/W Build')[0].strip()
    msg = "Get SW version = %s (%s)"%(get_sw,sw_ver)
    if get_sw <> sw_ver: raise Except("FAIL: " + msg)
    parent.SendMessage( msg + "\n" ,log,color=2)
    
    data = lWaitCmdTerm(term,"gettestmode","Manufacture>",5)
    get_testmode = int(data.split("testmode:")[-1].split('\n')[0].strip())
    msg = "Get Test Mode = %d (%d)"%(get_testmode,test_mode)
    if get_testmode <> test_mode: raise Except("FAIL: " + msg)
    parent.SendMessage( msg + "\n" ,log,color=2)
    lWaitCmdTerm(term,"top","mainMenu>",3)
    lWaitCmdTerm(term,"exit","#",3)   
    parent.SendMessage( "Check NVM Parameter time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)


def EtherTest(parent,link_rate,log):
    test_time = time.time()
    parent.SendMessage("Ether switch Test Start...\n" ,log)
    for i in range(2):
        data = os.popen("wmic NIC where NetEnabled=true get Name, Speed").read()
        d_rate = int(data.split(NIC_NAME[i])[-1].split('\n')[0].strip())/1000000
        msg = "NIC%d detect link rate = %d (%d) Mbps"%(i,d_rate,link_rate)
        if d_rate <> link_rate:
            parent.SendMessage( msg + "\n" ,log,color=1)
            raise Except("NIC%d Link Rate Detect FAIL"%i)
        else: parent.SendMessage( msg + "\n" ,log,color=2)
    for i in [NIC1,NIC2]:
        if link_rate == 1000: ping_count  = 4
        else: ping_count = 1    
        for j in range(ping_count):        
            rate = MSPing(i,ping_target[j])
            msg = "%s Ping %s Packet loss rate = %d (<= %d)"%(i,ping_target[j],rate,ping_loss)
            if rate > ping_loss: raise Except("FAIL: " + msg)
            else: parent.SendMessage( msg + "\n" ,log,color=2)
                       
    parent.SendMessage("Ether Switch link_rate = %d Ping Test Pass\n"%link_rate,log,color=2)
    parent.SendMessage( "Ethernet Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)
    
def EtherTest__(parent,link_rate,log):
    test_time = time.time()
    parent.SendMessage("Ether switch Test Start...\n" ,log)
    #if link_rate == 100:
    for i in range(2):
        if i:
            data = os.popen("devcon disable %s"%NIC_ID[i-1]).read()
            print data
            if not "device(s) disabled" in data: raise Except("FAIL: Disable NIC%d"%i-1)
            data = os.popen("devcon enable %s"%NIC_ID[i]).read()
            print data
            if not "device(s) are enabled" in data: raise Except("FAIL: Enable NIC%d"%i)
        else:
            data = os.popen("devcon disable %s"%NIC_ID[i+1]).read()
            print data
            if not "device(s) disabled" in data: raise Except("FAIL: Disable NIC%d"%i+1)
            data = os.popen("devcon enable %s"%NIC_ID[i]).read()
            print data
            if not "device(s) are enabled" in data: raise Except("FAIL: Enable NIC%d"%i)
        #time.sleep(2)
        Check_boot(parent,log)
        data = os.popen("wmic NIC where NetEnabled=true get Name, Speed").read()
        #a.split('I218-LM')[-1].split('\n')[0].strip()
        #print data
        #print "-------"
        #print data.split(NIC_NAME[i])[-1]
        #raw_input("####")
        d_rate = int(data.split(NIC_NAME[i])[-1].split('\n')[0].strip())/1000000
        msg = "NIC%d detect link rate = %d Mbps (%d)"%(i,d_rate,link_rate)
        if d_rate <> link_rate:
            parent.SendMessage( msg + "\n" ,log,color=1)
            raise Except("NIC%d Link Rate Detect FAIL"%i+1)
        else: parent.SendMessage( msg + "\n" ,log,color=2) 
             
        for target in ping_target:
            for j in xrange(5):
                rate = FPing(target,64,10,10)
                msg = "Ether %s: Ping %s Packet loss rate = %d (<= %d)"%(i+1,target,rate,ping_loss)                  
                if rate > ping_loss:
                    if i == 4: raise Except("FAIL: " + msg)
                    else: 
                      time.sleep(1)
                      continue 
                else: break                 
            parent.SendMessage( msg + "\n" ,log,color=2)
    
    parent.SendMessage("Ether Switch link_rate = %d Ping Test Pass\n"%link_rate,log,color=2)
    parent.SendMessage( "Ethernet Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)

def RebootTest(parent,term,log): 
    test_time = time.time()   
    parent.MessageBox('Press Reset Button','Reset Button Test',wx.OK|wx.ICON_INFORMATION)
    if not IsDisconnect(target_bh,30):  raise Except("FAIL: DUT Reset Fail")
    parent.SendMessage("DUT Rebooting...\n",log)
    parent.SendMessage("Check Reboot Button Pass\n",log,color=2)
    parent.SendMessage( "Reboot Button Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)


def FactoryReset(parent,term,log):    
    test_time = time.time()
    parent.SendMessage("Factory Reset Start...\n" ,log)
    if 'Manufacture>' not in lWaitCmdTermOutput(term,"","Manufacture>",3):
        lWaitCmdTerm(term,"cli","mainMenu>",10)
        lWaitCmdTerm(term,"Manu","Manufacture>",5)
    #term << 'factoryReset'
    lWaitCmdTerm(term,"reset cleanall","Y or N)",5)
    lWaitCmdTerm(term,"y","Success",5)
    parent.SendMessage("Factory Reset Finished\n",log,color=2)
    parent.SendMessage( "Factory Reset Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)

       

def Check_LED(parent,term,log):
    test_time = time.time()
    '''
    if 'Manufacture>' not in lWaitCmdTermOutput(term,"","Manufacture>",3):
        lWaitCmdTerm(term,"cli","mainMenu>",10)
        lWaitCmdTerm(term,"Manu","Manufacture>",5)
    lWaitCmdTerm(term,"ledd -m %d 1"%i,"#",3) 
    '''
    if '#' not in lWaitCmdTermOutput(term,"","#",3):
        lWaitCmdTerm(term,"top","mainMenu>",3)
        lWaitCmdTerm(term,"exit","#",3)
    #for i in range(5): 
    #    lWaitCmdTerm(term,"ledd -m %d 1"%i,"#",3) 
    lWaitCmdTerm(term,"touch /var/ledTest.token","#",3)
    lWaitCmdTerm(term,"/usr/sbin/ledAll.sh &","#",3)  
    if parent.MessageBox('LED loop blinking ','LED Test',wx.YES_NO|wx.ICON_QUESTION) == wx.ID_NO:  raise Except("FAIL: LED Test")
    lWaitCmdTerm(term,"rm -f /var/ledTest.token","#",3)
    parent.SendMessage("LED Test PASS\n" ,log,color=2)
    parent.SendMessage( "LED Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)

def Check_Buzzer(parent,term,log):
    test_time = time.time()
    if '#' not in lWaitCmdTermOutput(term,"","#",3):
        lWaitCmdTerm(term,"top","mainMenu>",3)
        lWaitCmdTerm(term,"exit","#",3)
    lWaitCmdTerm(term,"echo 14 1 >/proc/hitron/gpio_out_en","#",3)
    lWaitCmdTerm(term,"echo 14 1 >/proc/hitron/gpio_output_data","#",3)
    #lWaitCmdTerm(term,"echo 14 1>/proc/hitron/gpio_out_en"%i,"#",3)   
    if parent.MessageBox('Buzzer Sound on','Buzzer Test',wx.YES_NO|wx.ICON_QUESTION) == wx.ID_NO:  raise Except("FAIL: Buzzer Test")
    lWaitCmdTerm(term,"echo 14 0 >/proc/hitron/gpio_output_data","#",3)
    parent.SendMessage("Buzzer Sound Test PASS\n" ,log,color=2)
    parent.SendMessage( "Buzzer Sound Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)
    
def Check_DipSwitch(parent,term,log):
    test_time = time.time()
    test_fail = 0
    if 'Manufacture>' not in lWaitCmdTermOutput(term,"","Manufacture>",3):
        lWaitCmdTerm(term,"cli","mainMenu>",10)
        lWaitCmdTerm(term,"Manu","Manufacture>",5) 
    for i in ["Down","Up"]:
        parent.MessageBox('Press Pull %s Dip Switch'%i,'Dip Switch Test',wx.OK|wx.ICON_INFORMATION) 
        parent.SendMessage("DIP Switch Pull %s Test....\n"%i ,log) 
        data = ""   
        data = lWaitCmdTerm(term,"dipread 0","Manufacture>",10)    
        for j in range(4):
            try:
            #print "----------------"
                val = int(data.split("#%d value"%(j+1))[-1].split("\n")[1].strip())
            #val = int(data.split("#%d value\n"%(j+1))[-1].split("\n")[0].strip())
            except:
                raise Except("FAIL: Console Parsing Exception")
            msg = "DIP %d Read Value = %d (%d)\n"%((j+1),val,dip_val[i])
            if val <> dip_val[i]:
                test_fail+=1
                parent.SendMessage(msg ,log,color=1) 
            else: parent.SendMessage(msg ,log,color=2)
    
    if  test_fail>0:  raise Except("Dip Switch Test FAIL\n") 
    else: parent.SendMessage("Dip Switch Test PASS\n" ,log,color=2)  
    
    parent.SendMessage( "Dip Switch Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)
    
def Check_DipSwitch__(parent,term,log):
    test_time = time.time()
    test_fail = 0
    #for i in ["Down","Up"]:
    for i in ["Down"]:
        #parent.MessageBox('Press Pull %s Dip Switch'%i,'Dip Switch Test',wx.OK|wx.ICON_INFORMATION) 
        parent.SendMessage("DIP Switch Pull %s Test....\n"%i ,log) 
        data = ""   
           
        for j in range(4):
            try:
                print "----------------"
                lWaitCmdTerm(term,"echo %d 0 > /proc/hitron/gpio_out_en"%j,"#",5) 
                lWaitCmdTerm(term,"echo %d > /proc/hitron/gpio_input_data"%j,"#",5)
                term.get()
                #lWaitCmdTerm(term,"cat /proc/hitron/gpio_input_data","#",5)
                data = term.setWait("cat /proc/hitron/gpio_input_data",dip_val[i],5)[-1]
                val = int(data.split("\n")[1].strip())
                #raw_input(val) 
                #val = int(data.splitsplit("\n")[1].strip())
            #val = int(data.split("#%d value\n"%(j+1))[-1].split("\n")[0].strip())
            except:
                raise Except("FAIL: Console Parsing Exception")
            msg = "DIP %d Read Value = %d (%d)\n"%((j+1),val,dip_val[i])
            if val <> dip_val[i]:
                test_fail+=1
                parent.SendMessage(msg ,log,color=1) 
            else: parent.SendMessage(msg ,log,color=2)
    
    if  test_fail>0:  raise Except("Dip Switch Test FAIL\n") 
    else: parent.SendMessage("Dip Switch Test PASS\n" ,log,color=2)  
    
    parent.SendMessage( "Dip Switch Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)

def Check_IC_Type(parent,term,log):
    test_time = time.time()
    test_fail = 0
    parent.SendMessage( "Check Main Chip ID...\n",log)
    
    if '#' not in lWaitCmdTermOutput(term,"","#",3):
        lWaitCmdTerm(term,"top","mainMenu>",3)
        lWaitCmdTerm(term,"exit","#",3) 
    term.get()
    data = lWaitCmdTerm(term,"ht_iwcmd get_soc_info_utility STEPPING STRING --ap-atom","#",3) # Puma6
    get_id = data.split('\n')[1].strip()
    msg = 'Puma6 IC type = %s ( %s )\n'%(get_id,puma6_type)
    if  get_id <> puma6_type:
        test_fail+=1 
        parent.SendMessage(msg,log,color=1)
    else: parent.SendMessage(msg,log,color=2)  
    
    #if "SOC_STEPPING_C1" in data: parent.SendMessage("Puma6 IC type: %s\n"%puma6_type ,log,color=2) 
    #else: raise Except("Puma6 IC type Check FAIL\n") 
    term.get()
    data = lWaitCmdTerm(term,'ht_iwcmd /sbin/lspci -n --bh-atom | grep "07:00.0" | cut -c 15-',"#",5) # RTL8111
    get_id = data.split('\n')[1].strip()
    msg = 'RTL8111 chip version = %s ( %s )\n'%(get_id,RTL8111_id)
    if  get_id <> RTL8111_id:
        test_fail+=1 
        parent.SendMessage(msg,log,color=1)
    else: parent.SendMessage(msg,log,color=2) 
    
    for i in ['--bh-arm','--ap-arm']:    #Checking eMMC Controller PS8211
        term.get()
        get_id = {'version':'None','id':'None'}        
        data = lWaitCmdTerm(term,"ht_iwcmd phison info %s"%i,"Done.",5) 
        get_id['version'] = data.split('FW ver:')[-1].split('\n')[0].strip() #version
        get_id['id'] = data.split('ID:')[-1].split('\n')[0].strip() # id
        for j in get_id.keys(): 
            msg = 'PS8211 %s chip %s = %s ( %s )\n'%(i[2:].upper(),j,get_id[j],PS8211_id[j])
            if  get_id[j] <> PS8211_id[j]:
                test_fail+=1 
                parent.SendMessage(msg,log,color=1)
            else: parent.SendMessage(msg,log,color=2)
    
    term.get()        
    data = lWaitCmdTerm(term,'ht_iwcmd /sbin/lspci -n --bh-atom | grep "03:00.0" | cut -c 15-',Pericom_id,5) #Checking PCIe Switch (Pericom)  
    get_id = data.split('\n')[1].strip() 
    msg = 'Pericom PCIe Switch chip ID = %s ( %s )\n'%(get_id,Pericom_id)
    if  get_id <> Pericom_id:
        test_fail+=1 
        parent.SendMessage(msg,log,color=1)
    else: parent.SendMessage(msg,log,color=2)  
    
    lWaitCmdTerm(term,"cli","mainMenu>",10)
    lWaitCmdTerm(term,"system","system>",3)
    lWaitCmdTerm(term,"l2switch","l2switch>",3)
    for i in AR8035_id.keys():
        data = lWaitCmdTerm(term," readMDIO %s"%i,"l2switch>",3)
        get_id = data.split('Value:')[-1].split('\n')[0].strip()
        msg = 'PHY chip AR8035 address %s value = %s ( %s )\n'%(i,get_id,AR8035_id[i])
        if  get_id <> AR8035_id[i]:
            test_fail+=1 
            parent.SendMessage(msg,log,color=1)
        else: parent.SendMessage(msg,log,color=2)            
    lWaitCmdTerm(term,"top","mainMenu>",3)
    lWaitCmdTerm(term,"exit","#",3) 
    if  test_fail>0:  raise Except("Main Chip ID check FAIL\n") 
    else: parent.SendMessage("Main Chip ID check PASS\n" ,log,color=2)  
    
    parent.SendMessage( "Main Chip ID check time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)

def Check_boot(parent,log):
    parent.SendMessage( "Waitting for DUT bootup...\n",log)
    test_time=time.time()    
    if not IsConnect(target_bh,100):  raise Except("FAIL: DUT Boot Fail") 
    parent.SendMessage( "DUT bootup connected...\n",log)

def CheckWifiRssi(parent,log): 
    parent.SendMessage( "Scanning WIFI SSID...\n",log)
    test_time=time.time()   
    wifi_adaptor = 0  #for DUT1,DUT4  wifi_adaptor= 0, DUT5,DUT8 wifi_adaptor=1    
    flag = []
    ssid_count = len(ssid_list)
    for i in range(ssid_count): flag.append(0)
    for i in range(5):         
        print RefreshAdapters()
        wifi_list = ScanWifiSignal(wifi_adaptor)
        if len(wifi_list) ==0: raise Except('FAIL WIFI Dongle driver installation') 
        #print wifi_list  
        print "WIFI Client Scan %d ....\n"%i
        for j in wifi_list:
            for k in range(len(ssid_list)):                       
                if  '%s_%d'%(ssid_list[k],station_id) in j:
                    if flag[k]: break
                    else:
                        parent.SendMessage("SSID= %s BSSID= %s RSSI=%s Signal Quality=%s\n"%(j[0],j[1],j[3],j[2]),log,color=2)
                        flag[k] = 1
                        break
        count = 0
        for c in range(ssid_count):
            count+=flag[c]
            if i == 4:
                if not flag[c]: raise Except('WIFI SSID %s_%d Check Fail'%(ssid_list[c],station_id))
        if count ==ssid_count: return 1        
        time.sleep(0.5)
    parent.SendMessage("Scan WIFI SSID Test PASS\n" ,log,color=2)
    parent.SendMessage( "Scan WIFI SSID Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)    

def PingWiFiAP(parent,log):
    parent.SendMessage( "WIFI Ping Test...\n",log)
    test_time=time.time() 
    count,size,interval,ping_loss = map(int,wifipingparameter)  
    for i in ssid_list:
        a=WIFIThread(1,'%s_%d'%(i,station_id),target_bh,size,ping_loss,NIC3)
        a.start()
        while 1:
            if not a.running:
                if  len(a.err) > 0: raise Except('FAIL: %s'%a.err) 
                msg = 'SSID: %s Ping %s Lost = %.1f (<= %d)\n'%(a.ssid,a.wifi_target,a.value,a.ping_loss)
                if a.testflag > 0: 
                    raise Except('FAIL: %s'%msg) 
                else:
                    parent.SendMessage(msg,log,color=2)    
                break
            else: time.sleep(0.5)
    parent.SendMessage("WIFI Ping Test PASS\n" ,log,color=2)
    parent.SendMessage( "WIFI Ping Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log) 

def WriteRtlEfuse(parent,term,tftp_server,log):
    ''' Need 2 Ether cable and 2 Network card,
        The wireless network card installed in advance
        P500:Network card set speed 1G,
        P901 Network card set speed 100M
        '''
    parent.SendMessage( "Ethernet LED Efuse Writing...\n",log)
    test_time=time.time()  
    #lWaitCmdTerm(term,"quit","#",5)
    lWaitCmdTerm(term,"ifconfig eth1 down","#",5)
    lWaitCmdTerm(term,"rmmod r8168","#",5)
    lWaitCmdTerm(term,"cd /tmp/","#",5)   
    print 'Install Ether LED Key...'
    lWaitCmdTerm(term,"tftp -g %s -r pgdrv.ko"%tftp_server,"#",5)
    lWaitCmdTerm(term,"tftp -g %s -r rtnicpg-i686"%tftp_server,"#",5)
    lWaitCmdTerm(term,"tftp -g %s -r 8168GEF.cfg"%tftp_server,"#",5)
    lWaitCmdTerm(term,"tftp -g %s -r 8168GUEF.cfg"%tftp_server,"#",5)

    lWaitCmdTerm(term,"insmod ./pgdrv.ko","#",5)
    lWaitCmdTerm(term,"chmod u+x rtnicpg-i686","#",5)
    lWaitCmdTerm(term,"./rtnicpg-i686 /efuse","#",5)
    data = lWaitCmdTerm(term,"./rtnicpg-i686 /efuse /r","#",5)
    efuse_led_cfg = data.split('LEDCFG =')[-1].split('\n')[0].strip()
    msg = 'Efuse LED Config Compare = %s (%s)'%(efuse_led_cfg,led_cfg)
    if  efuse_led_cfg <> led_cfg: raise Except('FAIL: %s'%msg)
    parent.SendMessage( msg + "\n" ,log,color=2)      
    lWaitCmdTerm(term,"rmmod pgdrv","#",5)
    lWaitCmdTerm(term,"insmod /lib/modules/r8168.ko","#",5)
    lWaitCmdTerm(term,"ifconfig eth1 up","#",5)
    lWaitCmdTerm(term,"brctl addif brlan2 eth1","#",5)
    if parent.MessageBox('Ether Link rate = 100Mbit  LED = RED','LED Test',wx.YES_NO|wx.ICON_QUESTION) == wx.ID_NO:  raise Except("FAIL: Ether LED Test")
    parent.SendMessage("Ethernet LED Efuse Write PASS\n" ,log,color=2)
    parent.SendMessage( "Ethernet LED Efuse Writing Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log) 
        
        
            
        
def T1(parent):
    try: 
        result = 0
        term = 0
        log = None
        mac = ""
        parent.SendMessage("START",state = "START")
        start_time = end_time = 0
        #mac = GetMacAddress(parent)
        sn = GetSN(parent) 
        t= str(round(time.time(),1)).split(".")
        log = open(logPath+sn+"_%s%s.t1"%(t[0][7:],t[1]),"w")
        start_time=time.time()
        parent.SendMessage("Sharp-Dragon test program version: %s , Station: %s\n"%(version,Test_station),log)
        parent.SendMessage( "---------------------------------------\n",log)
        parent.SendMessage( "Start Time:"+time.ctime()+"\n",log)
        #parent.SendMessage( "Scan MAC address:"+mac+"\n",log)
        parent.SendMessage( "Scan SN:"+sn+"\n",log)
        parent.SendMessage( "---------------------------------------------------------------------------\n",log)
        Check_boot(parent,log)
        if ETH_TEST: EtherTest(parent,100,log)
        #cosole_term =htx.SerialTTY(comport,115200)  #Console: BH-ATOM        
        #if EFUSE_WRITE: WriteRtlEfuse(parent,cosole_term,tftp_server,log)
        #Check_boot(parent,log)
        #term =htx.Telnet(target_bh)
        #if USB_TEST: CheckUSB(parent,term,log)        
        #if NVRAM_PROGRAM: NvmProgram(parent,term,mac,sn,log)
        #if DIP_SWITCH: Check_DipSwitch(parent,term,log)     
        #if LED_TEST: Check_LED(parent,term,log)
        #if BUZZER_TEST: Check_Buzzer(parent,term,log)          
        #if CHECK_IC_Type: Check_IC_Type(parent,term,log)     
         
        
    except Except,msg:
        parent.SendMessage("\n%s\n"%msg,log,color=1)
        result = 1
    except: 
        parent.SendMessage("\n%s\n"% traceback.print_exc(),log,color=1)
        result = 1
    end_time = time.time()
    parent.SendMessage('\n'+"End Time:"+time.ctime()+'\n',log)
    parent.SendMessage("total time: %3.2f"%(end_time-start_time)+'\n',log)
    if result:
       parent.SendMessage( "Test Result:FAIL"+'\n',log,color=1)
    else:
       parent.SendMessage( "Test Result:PASS"+'\n',log,color=2)
    if log:log.close()
    if cosole_term: cosole_term.close()
    if term: term.close()
    if sn: 
       #travel = passtravel(mac,'127.0.0.1',1800,30)
       #if travel or result:
       if result:
          parent.SendMessage('\n',state = "FAIL",color=1)
       else:
          parent.SendMessage( "",state = "PASS")   
    else: parent.SendMessage("",state = "FAIL")       
        
                   
        
def T2(parent):
    try: 
        result = 0
        term = 0
        log = None
        mac = ""
        parent.SendMessage("START",state = "START")
        start_time = end_time = 0
        #mac = GetMacAddress(parent)
        sn = GetSN(parent) 
        t= str(round(time.time(),1)).split(".")
        #log = open(logPath+mac+"_%s%s.t2"%(t[0][7:],t[1]),"w")
        log = open(logPath+sn+"_%s%s.t2"%(t[0][7:],t[1]),"w")
        start_time=time.time()
        parent.SendMessage("Sharp-Dragon test program version: %s , Station: %s\n"%(version,Test_station),log)
        parent.SendMessage( "---------------------------------------\n",log)
        parent.SendMessage( "Start Time:"+time.ctime()+"\n",log)
        #parent.SendMessage( "Scan MAC address:"+mac+"\n",log)
        parent.SendMessage( "Scan SN:"+sn+"\n",log)
        parent.SendMessage( "---------------------------------------------------------------------------\n",log)
        Check_boot(parent,log)
        if ETH_TEST: EtherTest(parent,100,log)
        term =htx.Telnet(target_bh)
        TelnetLogin(term,username=None,password=None)
        if PCIE_TEST: CheckPcieDevice(parent,term,log)
        if CHECK_NVM: CheckNvm(parent,term,mac,sn,log) 
        if SSID_CHANGE: ChangeSSID(parent,term,log)
        if WIFI_SSID: CheckWifiRssi(parent,log)
        if WIFI_PING: PingWiFiAP(parent,log)
        
                
       
               
        
        
        
                
    except Except,msg:
        parent.SendMessage("\n%s\n"%msg,log,color=1)
        result = 1
    except: 
        parent.SendMessage("\n%s\n"% traceback.print_exc(),log,color=1)
        result = 1
    end_time = time.time()
    parent.SendMessage('\n'+"End Time:"+time.ctime()+'\n',log)
    parent.SendMessage("total time: %3.2f"%(end_time-start_time)+'\n',log)
    if result:
       parent.SendMessage( "Test Result:FAIL"+'\n',log,color=1)
    else:
       parent.SendMessage( "Test Result:PASS"+'\n',log,color=2)
    if log:log.close()
    if term: term.close()
    if sn: 
       #travel = passtravel(mac,'127.0.0.1',1800,30)
       #if travel or result:
       if result:
          parent.SendMessage('\n',state = "FAIL",color=1)
       else:
          parent.SendMessage( "",state = "PASS")   
    else: parent.SendMessage("",state = "FAIL")  
        
    



    
    
