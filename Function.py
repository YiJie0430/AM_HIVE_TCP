import os,time,traceback
from toolslib_local import *
#import htx_wifi
import wx
import random
#from WLAN import *
#from htx_new import *
#from Retest import *
import subprocess as sp
#import multiprocessing

execfile("config.ini")
if os.path.isfile('c:\\station.ini'):
    execfile('c:\\station.ini')


def lLogin(dstip,pid,username,password):
    #term.host -- dst ip
    #term.port -- dst port
    #uid must be 101
    print 'Telnet login Start'
    for k in range(5):
        if isPortConnect(dstip,pid):
           print 'The port is open,wait telnet'
           break
        else:
           time.sleep(1)
           if k==4:raise Except('The port is close')          
    for a in range(5):
      time.sleep(2)
      access=0
      #term = htx.Telnet(dstip,pid)
      term=htx_wifi.Telnet(dstip,pid,3)
      data = term.wait("login:",5)[-1]
      print '[%s]%s'%(time.ctime(),data)
      print username
      print password    
      for i in range(5):
          term << username
          time.sleep(2)
          term << password
          data=term.wait('>',15)[-1]
          print '[%s]%s'%(time.ctime(),data)
          if '101' in data: access=1; break 
          else: term<<'\x03'; break
          if i == 4:
            term << '\x03'
            raise Except('Telnet login Failure')
      if access: return term    

def Telnet_arm(parent,arm_ip,log):
    parent.SendMessage("Telnet to ARM...\n", log)
    arm_term=htx_wifi.Telnet(arm_ip); time.sleep(5)
    test_time=time.time()
    while 1: 
        if time.time()-test_time>20: raise Except('Telnet Arm Fail')
        data=arm_term.get(); print data
        if 'Password' in data: arm_term << 'Hitron'; time.sleep(1)
        elif 'login as' in data: arm_term << 'admin'; time.sleep(1)
        if 'Menu>' in data: return arm_term 

def Enable_atom_telnet(parent,arm_ip,log):
    arm_term=Telnet_arm(parent,arm_ip,log)
    lWaitCmdTerm(arm_term,'shell','Password:',5)
    lWaitCmdTerm(arm_term,'password','#',5)
    lWaitCmdTerm(arm_term,'cd /var/tmp','#',5)
    lWaitCmdTerm(arm_term,'ln -s /usr/sbin/ht_iwcmd telnetd','#',5)
    lWaitCmdTerm(arm_term,'export PATH=/var/tmp:$PATH','#',5)
    lWaitCmdTerm(arm_term,'telnetd','#',5)
    lWaitCmdTerm(arm_term,'exit','>',5)
    arm_term<<'exit'
    parent.SendMessage('ATOM Telnet Enable\n',log)


def GetMacAddress(parent):
    val = parent.MAC.GetValue(); #return val
    try:
        if (len(val) == 12): return val          
    except ValueError:
           pass
    raise Except("Input MAC Label Error %s !"%val)

def GetSSidLabel(parent):
    val = parent.SSID.GetValue()
    try:
        if len(val) >= 8: return val
    except ValueError:
           pass
    raise Except("Input SSID Label Error %s !"%val)

def GetPasswordLabel(parent):
    val = parent.pswd.GetValue()
    try:
        if len(val) >=8: return val
    except ValueError:
           pass
    raise Except("Input WIFI Password Label Error %s !"%val)

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

def TelnetLogin(term,username='cusadmin',password='password'):
    print "Telnet Login..."
    flag=1
    term.wait(':',5)
    term<<username; term<<password
    #data=term.wait('#',5)
    term<<"cd /tmp && tftp -g '%s' -r Hitron_AP.sh"%tftp
    for i in xrange(3):
        data = lWaitCmdTerm(term,"ls | grep 'Hitron_AP'",'#',5)
        if 'Hitron_AP.sh' not in data: flag=0; term<<"cd /tmp && tftp -g '%s'%tftp -r Hitron_AP.sh && chmod -x Hitron_AP.sh" 
        else: break
    if flag: term<<'sh -x ./Hitron_AP.sh';time.sleep(8) #data = lWaitCmdTerm(term,'sh -x ./Hitron_AP.sh','#',15); print data
    else: raise Except("FAIL: Tftp server error")

def CheckValue(func):
    def checkdata(*args):
        import re
        result = 1
        rep = str()
        mac = args[2]
        mac1 = "%012X"%(int(mac,16))
        wanmac = mac1[0:2]+":"+mac1[2:4]+":"+mac1[4:6]+":"+mac1[6:8]+":"+mac1[8:10]+":"+mac1[10:12]
        mac2 = "%012X"%(int(mac,16) + 1)
        mac2g= mac2[0:2]+":"+mac2[2:4]+":"+mac2[4:6]+":"+mac2[6:8]+":"+mac2[8:10]+":"+mac2[10:12]
        mac3 = "%012X"%(int(mac,16) + 2)
        mac5g = mac3[0:2]+":"+mac3[2:4]+":"+mac3[4:6]+":"+mac3[6:8]+":"+mac3[8:10]+":"+mac3[10:12]
        data = func(args[0],args[1],args[2],args[3])
        mac4 = "%012X"%(int(mac,16) + 3)
        btmac = mac4[0:2]+":"+mac4[2:4]+":"+mac4[4:6]+":"+mac4[6:8]+":"+mac4[8:10]+":"+mac4[10:12]        
        parsing = re.findall(r'(?<=:\s\s)(.*)(?=.*)', data)
        if 'FAILED' in data:
            if str(parsing[8].split('\r')[0]) != 'OK' or str(parsing[9].split('\r')[0]) != 'OK' or str(parsing[10].split('\r')[0]) != 'OK':
                result = 0
            rep = data
        if str(wanmac) != str(parsing[1].split('\r')[0]): 
            result = 0
            rep = 'Wan MAC Failed:{}'.format(parsing[1].split('\r')[0])
        if str(mac2g) != str(parsing[2].split('\r')[0]): 
            result = 0
            rep = 'wifi0 MAC Failed:{}'.format(parsing[2].split('\r')[0])
        if str(mac5g) != str(parsing[3].split('\r')[0]): 
            result = 0
            rep = 'wifi1 MAC Failed:{}'.format(parsing[3].split('\r')[0])        
        if str(btmac) != str(parsing[4].split('\r')[0]): 
            result = 0
            rep = 'BT MAC Failed:{}'.format(parsing[4].split('\r')[0])        
        if '0xfe71' != str(parsing[5].split('\r')[0]):
            result = 0
            rep = 'BT UUID Failed:{}'.format(parsing[5].split('\r')[0])
        return (result, rep, data)
    return checkdata
    
def CheckBootUp(func):
    def checkstatus(*args):
        test_time = time.time()
        for count in range(2):
            if IsConnect_board(dut_ip,timeout=60):
               #term = htx_wifi.Telnet(dut_ip)
               term = htx_wifi.ssh(dut_ip)
               if not term:
                  raise Except('SSH connect Failed')
               else:
                  term << '\n'
            else:
               raise Except("Ping DUT Failed") 
            term.wait('#',3)
            term << 'pmf -e'
            #time.sleep(0.5)
            data = term.get()
            args[0].SendMessage(data,args[3])
            if 'already in factory mode' in data:
            	ver = lWaitCmdTerm(term, 'cat /.version', promp, 5)
                if SoftwareVersion not in ver:
                    raise Except('SoftwareVersion is Wrong : {}'.format(ver))
                args[0].SendMessage('\nSoftWare Version: {}\n'.format(ver.split('(')[0]), args[3])                
                break
            if count == 1:
                raise Except("Check Factory Mode Failed")
        data = func(args[0], term, args[2], args[3])
        if data[0]:
            args[0].SendMessage(data[2], args[3])
            args[0].SendMessage( "\nNrmCheck Test time: %3.2f (sec)\n"%((time.time() - test_time)),args[3])
            args[0].SendMessage( "---------------------------------------------------------------------------\n",args[3])
            return term
        else:
            raise Except('NrmCheck Failed : {}'.format(data[1]))
    return checkstatus

@CheckBootUp
@CheckValue
def CheckNrm(parent,term,mac,log):
    data = lWaitCmdTerm(term,"pmf -f -r", promp, 10)
    if 'Error' in data or 'timeout'in data:
        if 'exists in flash' in data:
            raise Except("please reboot DUT: {}".format(data))
        else: 
            raise Except("Nrm setup failed: {}".format(data))
    parent.SendMessage(data, log)    
    report = lWaitCmdTerm(term,"pmf --report", promp, 10)
    return report

def PingLinux(term,gd_term,interface,server,timeout):
    '''
    s = time.time()
    while True:
        if time.time()-s < 5:
           gd_term << "\n"
           data=gd_term.get()
           if '#' not in data: gd_term << chr(0x03); time.sleep(0.1)
           else: break
        else: raise Except('FAIL: plz check golden sample status(no prompt)')
    '''
    interrupt=chr(0x03)
    lWaitCmdTerm(gd_term,interrupt,'#',10)
    s_=time.time()
    while time.time()-s_ < timeout:
        data = lWaitCmdTerm(gd_term,"ping %s -w 5"%server,'loss',10); print data
        if "100% packet loss" not in data: 
            #data=lWaitCmdTerm(term,"iw %s station dump"%ap_argv[interface][0],promp,5)
            return 1
    data=lWaitCmdTerm(term,"iw %s info"%ap_argv[interface][0],promp,5)
    raise Except('FAIL: Cannot Ping to Iperf server: \n%s'%data)

def PingLinux(term,gd_term,interface,server,timeout):
    import win32api
    interrupt=chr(0x03)
    lWaitCmdTerm(gd_term,interrupt,'#',10)
    s_=time.time()
    while time.time()-s_ < timeout:
        #data = lWaitCmdTerm(gd_term,"ping %s -w 5"%server,'loss',10); print data
        PROCESS_TERMINATE=0
        start_T=time.time()
        process=sp.Popen("Fping %s -n 5 -t 100"%tcp_ip[interface][0], stdout=sp.PIPE, stderr=sp.PIPE)
        while process.poll() is None:
          if (time.time()-start_T) > 5:
            PROCESS_TERMINATE=1
            handle = win32api.OpenProcess(PROCESS_TERMINATE, False, process.pid); print handle
            if handle:
               win32api.TerminateProcess(handle, -1)
               win32api.CloseHandle(handle)
            break
        if PROCESS_TERMINATE: continue
        else: 
           data=process.stdout.read(); print data 
           if "100% loss" not in data: 
              #data=lWaitCmdTerm(term,"iw %s station dump"%ap_argv[interface][0],promp,5)
              return 1
    data=lWaitCmdTerm(term,"iw %s station dump"%ap_argv[interface][0],promp,3); #print data
    if data:
      rssi=data.split('signal avg:')[-1].split('dBm')[0].strip()
      tx_rate=data.split('tx bitrate:')[-1].split('MBit/s')[0].strip()
      rx_rate=data.split('rx bitrate:')[-1].split('MBit/s')[0].strip()
      raise Except('FAIL: Ping Iperf server(%s):\nRSSI: %s\nTX/RX:%s/%s Mbits'%(tcp_ip[interface][0],rssi,tx_rate,rx_rate))
    else:
      data=lWaitCmdTerm(term,"iw %s info"%ap_argv[interface][0],promp,5)
      raise Except('FAIL: Connect with client\n%s'%data)
    
def ChkConnetction(parent,interface,gd_term,timeout,log):    
    term =htx_wifi.Telnet(ap_ip['atom'])
    lWaitCmdTerm(term,'root',promp,3)
    parent.SendMessage("Check %s Connection Status...\n"%interface,log)
    test_time=time.time()
    #term_client<<'cd /etc/config && sh -x ./%s'%value[1]; time.sleep(10)
    for retry in range(3):
       count=0
       flag=0
       test_time_=time.time() 
       while time.time()-test_time_<45:
           print 'ChkConnetction %f'%float(time.time()-test_time_)
           data=lWaitCmdTerm(term,"iw %s station dump"%ap_argv[interface][0],promp,3)
           if 'Station' in data: 
              result=PingLinux(term,gd_term,interface,tcp_ip[interface][1],timeout)    
              if result: flag=result; break
           else: time.sleep(1); count+=1
           if count==15: print 'client setting'; gd_term<<'sh -x /nvram/wds_fixture.sh'; time.sleep(10)
       if flag: break       
       if retry==2: 
          data=lWaitCmdTerm(term,'iw %s info'%ap_argv[interface][0],promp,30)
          raise Except('FAIL: %s Connection\n%s'%(interface,data)) 
       else:
          lWaitCmdTerm(term,ap_argv[interface][1],'fcu] does not exists',50)
          #lWaitCmdTerm(term,ap_argv[interface][2],promp,3)
       
    parent.SendMessage("%s Connection Check PASS\n"%interface,log,color=2)
    parent.SendMessage( "WDS Connection Check time: %3.2f (sec)\n"%(time.time()- test_time),log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)

def ChkConnetction(parent,term,interface,gd_term,timeout,run,log):    
    #term =htx_wifi.Telnet(ap_ip['atom'])
    #lWaitCmdTerm(term,'root',promp,3)
    if not run: parent.SendMessage("Check %s Connection Status...\n"%interface,log)
    test_time=time.time()
    retry=0
    while True:
       count=0
       flag=0
       test_time_=time.time() 
       retry+=1
       while time.time()-test_time_<45:
           print 'ChkConnection %f'%float(time.time()-test_time_)
           data=lWaitCmdTerm(term,"wlanconfig %s list"%ap_argv[interface][0],promp,3)
           if 'ADDR' in data: 
              result=PingLinux(term,gd_term,interface,tcp_ip[interface][1],timeout)    
              if result: flag=result; break
           else: time.sleep(1); count+=1
           if count==15: print 'client setting'; gd_term<<'sh -x /nvram/wds_fixture_dual.sh'; time.sleep(10)
       if flag and not run: break
       if retry==1 and not flag:
          if run==2: 
             data=lWaitCmdTerm(term,"iwconfig {}".format(ap_argv[interface][0]),promp,5)
             raise Except('---wifi info---\n%s\nFAIL: Connect with client'%data)
          else: return flag
       if retry==1 and run<=2 and flag: 
          parent.SendMessage( "ChkConnection internal(%d) time: %3.2f (sec)\n"%(run,time.time()- test_time),log)
          return flag
          #raise Except('FAIL: %s Connection\n%s'%(interface,data)) 
       
    parent.SendMessage("%s Connection Check PASS\n"%interface,log,color=2)
    parent.SendMessage( "WDS Connection Check time: %3.2f (sec)\n"%(time.time()- test_time),log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)
    return flag
    
#iperf -c 192.168.1.140 -t 8 -w 212K -P 5 -r    
def IperfThroughput(parent,interface,log):
    val = list()
    link_rate = [None,None]
    direction = {0:"Tx",1:"Rx"}
    test_fail = 0
    parent.SendMessage( "WIFI Throughput Test...\n",log)
    test_time=time.time() 
    PingLinux(dut_term,ap_ip[interface],10)
    if interface == 'ra0': t = 5
    else: t = 8 
    lWaitCmdTerm(dut_term,"iperf -s -w 212k -p 8181",'Byte',5)
    data = lWaitCmdTerm(gd_term,"iperf -c %s -t %d -w 212K -P 5 -r"%(ap_ip[interface],t),'#',20) 
    try:
        for k in data.splitlines():
            if  '[SUM]' in k:
                if 'Kbits' in k: val.append(float(k.split()[-2])*0.001)
                else: val.append(float(k.split()[-2]))              
    except:
        dut_term << chr(0x03)   # Ctrl + c
        gd_term.close()
        dut_term.close()
        raise Except ("FAIL:Get Tx/Rx Value:" + val)
    dut_term << chr(0x03)  # Ctrl + c
    gd_term.close()
    dut_term.close()
    for i in range(2):        
        msg = "%s %s throughput = %.2f ( >= %d )\n"%(ap_freq[interface],direction[i],val[i],throughput_criteria[interface][i])    
        if val[i] < throughput_criteria[interface][i]: 
            parent.SendMessage(msg,log,color=1)
            test_fail+=1
        else: parent.SendMessage(msg,log,color=2)   
    if test_fail > 0 :  raise Except('FAIL: WIFI Throughput Test')
    
    parent.SendMessage("WIFI %s Throughput Test PASS\n"%ap_freq[interface] ,log,color=2)
    parent.SendMessage( "WIFI %s Throughput Test time: %3.2f (sec)\n"%(ap_freq[interface],time.time()- test_time) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log) 

def GDIperfsetup(parent,gd_term,log):
    test_time=time.time()
    while True:
        if time.time()-test_time<10:
           gd_term << chr(0x03);time.sleep(0.1)
           data=lWaitCmdTerm(gd_term,"iperf -s -w 212K -p 8181",'Byte',5)
           if 'Server listening on TCP port 8181' in data: return 1
           else: gd_term << chr(0x03)
        else: raise Except ("FAIL: Iperf server failed (golden sample)")

def IperfThroughput(parent,gd_term,interface,log):
    term =htx_wifi.Telnet(ap_ip['atom'])
    lWaitCmdTerm(term,'root',promp,3)
    direction = {0:"Transmit",1:"Receive"}
    parent.SendMessage("%s WIFI Throughput Test...\n"%interface,log)
    GDIperfsetup(parent,gd_term,log)
    test_time=time.time()
    for try_ in range(iperf_retry):        
        traffic=str()
        val = list()
        link_rate = [None,None]
        test_fail = 0
        #lWaitCmdTerm(term,ap_argv[interface][2],promp,3)
        data = os.popen("iperf -c %s -w 212K -P 8 -r"%tcp_ip[interface][0]).read(); print data
        try:
            if '[SUM]' in data:
                for k in data.splitlines():
                    if  '[SUM]' in k:
                        val.append(float(k.split()[-2])); print val
            else: GDIperfsetup(parent,gd_term,log); continue
        except:
            if try_==(iperf_retry-1):raise Except ("FAIL:Get Tx/Rx Value:" + data)
            else: GDIperfsetup(parent,gd_term,log); continue
                    
        for i in xrange(2):        
            color_flag=0
            msg = "%s TCP %s = %.2f ( >= %d )\n"%(interface,direction[i],val[i],throughput_criteria[interface][i])  
            traffic+=msg    
            if val[i] < throughput_criteria[interface][i]: color_flag=1; test_fail=1
            else: color_flag=0                 
            if try_==(iperf_retry-1) and color_flag: parent.SendMessage(msg,log,color=1)    
            if try_==(iperf_retry-1) and not color_flag: parent.SendMessage(msg,log,color=2)            
            if try_==(iperf_retry-1) and i==1 and test_fail: raise Except('FAIL: %s WIFI Throughput Test'%interface)
            
        if not test_fail: 
            if iperf_retry > 1: parent.SendMessage(traffic,log,color=2)
            break
    parent.SendMessage("%s WIFI Throughput Test PASS\n"%(interface),log,color=2)
    parent.SendMessage( "%s WIFI Throughput Test time: %3.2f (sec)\n"%(interface,(time.time()- test_time)),log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)
    gd_term << chr(0x03)
    return(link_rate[1],link_rate[0],val[1],val[0])  

def IperfThroughput(parent,term,gd_term,interface,run,log):
    import win32api
    #term =htx_wifi.Telnet(ap_ip['atom'])
    #lWaitCmdTerm(term,'root',promp,5)
    direction = {0:"Transmit",1:"Receive"}
    if not run: parent.SendMessage("%s WIFI Throughput Test...\n"%interface,log)
    GDIperfsetup(parent,gd_term,log)
    test_time=time.time()
    for try_ in range(iperf_retry):        
        PROCESS_TERMINATE=0
        traffic=str()
        val = list()
        tx_link_rate = list()
        rx_link_rate = list()
        rssi_list=list()
        chain_rssi = list()
        rssi = rate = [None,None]
        rssi_fail = 0
        test_fail = 0
        start_T=time.time()
        process=sp.Popen("iperf -c %s -t 10 -w 212K -P 8 -r -p 8181"%tcp_ip[interface][0], stdout=sp.PIPE, stderr=sp.PIPE)
        while process.poll() is None:
          time.sleep(5)
          '''
          data=lWaitCmdTerm(term,"iw %s station dump"%ap_argv[interface][0],promp,3); #print data
          if data:
            rssi=data.split('signal avg:')[-1].split('dBm')[0].strip()
            rssi_list.append(rssi); #print 'rssi_list:',rssi_list
            tx_rate=data.split('tx bitrate:')[-1].split('MBit/s')[0].strip()
            tx_link_rate.append(tx_rate); #print 'tx_list:',tx_link_rate          
            rx_rate=data.split('rx bitrate:')[-1].split('MBit/s')[0].strip()
            rx_link_rate.append(rx_rate); #print 'rx_list:',rx_link_rate
          '''
          
          if interface == '2.4G':
              try:
                  data = lWaitCmdTerm(term, "athstats -i wifi0 | grep rssi", promp, 3); #print data
                  rssi_0 = data.split('ch0]:')[-1].split('\n')[0].strip(); print rssi_0
                  rssi_1 = data.split('ch1]:')[-1].split('\n')[0].strip(); print rssi_1
                  rssi_0_1 = [rssi_0,rssi_1]; print rssi_0_1
              except:
                  rssi_0_1 = [40,40]
              for idx, i in enumerate(rssi_0_1):
                  if not 40 <= int(i) <= 80:
                      raise Except('chain{} rssi fail: {} (40 ~ 80 dBm)'.format(idx,i))
          else:
              try:
                  data = lWaitCmdTerm(term, "athstats -i wifi1 | grep rssi", promp, 3); #print data
                  rssi_0 = data.split('ast_rx_rssi_chain0  :   ')[-1].split('      ')[0].strip(); print rssi_0
                  rssi_1 = data.split('ast_rx_rssi_chain1  :   ')[-1].split('      ')[0].strip(); print rssi_1
                  rssi_0_1 = [rssi_0,rssi_1]
              except:
                  rssi_0_1 = [30,30]
              for idx, i in enumerate(rssi_0_1):
                  if not 30 <= int(i) <= 60:
                      raise Except('chain{} rssi fail: {} (30 ~ 60 dBm)'.format(idx,i))
          
          data=lWaitCmdTerm(term,"iwinfo %s assoc"%ap_argv[interface][0],promp,3); print data
          if data:
            rssi=data.split('SNR')[-1].split(')')[0].strip()
            rssi_list.append(rssi); #print 'rssi_list:',rssi_list
            tx_rate=data.split('TX:')[-1].split('MBit/s')[0].strip()
            tx_link_rate.append(tx_rate); #print 'tx_list:',tx_link_rate          
            rx_rate=data.split('RX:')[-1].split('MBit/s')[0].strip()
            rx_link_rate.append(rx_rate); #print 'rx_list:',rx_link_rate
          
          if (time.time()-start_T) > 30:
            if process.poll() is None:
               PROCESS_TERMINATE = 1
               handle = win32api.OpenProcess(PROCESS_TERMINATE, False, process.pid)
               if handle:
                  win32api.TerminateProcess(handle, -1)
                  win32api.CloseHandle(handle)
               break
        
        from collections import Counter
        rssi_count=Counter(rssi_list)
        rssi=rssi_count.most_common(1); print 'rssi:',rssi
        if int(rssi[0][0])<=int(rssi_criteria): rssi_fail=1
        #rssi_list.sort(reverse=True)
        #rssi=rssi_list[0:3]/3
        tx_rate_count=Counter(tx_link_rate)
        tx_rate=tx_rate_count.most_common(1); #print 'tx:',tx_rate
        rx_rate_count=Counter(rx_link_rate)
        rx_rate=rx_rate_count.most_common(1); #print 'rx:',rx_rate
        rate=[tx_rate[0][0],rx_rate[0][0]]; #print 'rate:',rate   
        
        if PROCESS_TERMINATE or rssi_fail: 
          if try_==(iperf_retry-1): 
            data=lWaitCmdTerm(term,"wlanconfig %s list"%ap_argv[interface][0],promp,2)
            parent.SendMessage("[%s linkinfo]:\n%s\n"%(interface,data),log,color=0)
            if rssi_fail:
              raise Except('Fail: %s AVG. RSSI: %s (>(%s))\n'%(interface,rssi[0][0],rssi_criteria))          
            return 1 #raise Except ("FAIL:Iperf Error")
          else: GDIperfsetup(parent,gd_term,log); continue
        else: iperf_data=process.stdout.read(); print iperf_data 
        if '[SUM]' in iperf_data:
            count=0
            try:
               for k in iperf_data.splitlines():
                   if '[SUM]' in k: 
                      val.append(float(k.split()[-2])); print val; count+=1
               if count<>2: GDIperfsetup(parent,gd_term,log)
            except:
               GDIperfsetup(parent,gd_term,log)
        else: 
            if try_==(iperf_retry-1):
               parent.SendMessage('AVG. RSSI: %s\n'%(rssi[0][0]),log,color=0)
               parent.SendMessage('TX/RX link rate: %s/%s Mbits\n'%(rate[0],rate[1]),log,color=0)
               raise Except('Fail: ---Iperf---\n%s\n'%iperf_data)
            else:
               GDIperfsetup(parent,gd_term,log); continue                    
        throughput_criteria=[int(float(rate[0])*throughput_loss),int(float(rate[1])*throughput_loss)]
        #throughput_criteria=[50, 50]
        rssi_show=0  
        tpt_log=[None,None]
        for i in xrange(2):        
            if float(rate[i]) < float(linkrate_criteria[interface]): 
              raise Except('FAIL: %s %s linkrate out of criteria | TX %s > (%d), RX %s > (%d)'%(interface,direction[i],rate[0],linkrate_criteria[interface],rate[1],linkrate_criteria[interface]))
            msg = "%s %s linkrate is %s MBit/s, Throughput = %.2f ( >= %d )\n"%(interface,direction[i],rate[i],val[i],throughput_criteria[i])       
            if val[i] < throughput_criteria[i]: 
               tpt_log[i]=[1,msg]
               test_fail=1
            else: tpt_log[i]=[0,msg]
            if try_==(iperf_retry-1) and test_fail and run<2: gd_term << chr(0x03); return test_fail #parent.SendMessage('link info:\n%s'%data,log,color=2); return test_fail #add by YiJie            
        if try_==(iperf_retry-1) or not test_fail: 
            parent.SendMessage('%s AVG. RSSI: %s (>(%s))\n'%(interface,rssi[0][0],rssi_criteria),log,color=0)
            for i in xrange(2):
                parent.SendMessage(tpt_log[i][1],log,color=int(tpt_log[i][0]))
            break
    if test_fail: raise Except('FAIL: %s WIFI Throughput Test'%interface)
    parent.SendMessage("%s WIFI Throughput Test PASS\n"%(interface),log,color=2)
    parent.SendMessage( "%s WIFI Throughput Test time: %3.2f (sec)\n"%(interface,(time.time()- test_time)),log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)
    gd_term << chr(0x03)
    return test_fail
    #return(link_rate[1],link_rate[0],val[1],val[0])  



def EnableNc(parent,term,log):
    lWaitCmdTerm(term,"top",'mainMenu>',10,2)    
    lWaitCmdTerm(term,"shell",'Password:',10,2)
    term.get()
    term<<"password"
    #term<<"AccessDeny"
    time.sleep(2)
    data=term.get()
    print "1111111111111111"
    print data
    print "1111111111111111"
    if "Wrong password!" in data:
        lWaitCmdTerm(term,"shell",'Password:',10,2)
        lWaitCmdTerm(term,"AccessDeny",'#',10)
    lWaitCmdTerm(term,"ht_led_test 1234 start&",'#',5,2)
    term<<"nc 192.168.254.254 1234"

def EnableNc(parent,log):
    term=lLogin(ap_ip['arm'],23,username='admin',password='admin')        
    parent.SendMessage("Create connection for ARM to Atom (nc)...\n",log)
    test_time=time.time()
    lWaitCmdTerm(term,"top",'mainMenu>',3,2)    
    lWaitCmdTerm(term,"script",'Main>',3,2)
    lWaitCmdTerm(term,"um_auth_account_password admin %s"%shellpassword,'Main>',3,2)
    lWaitCmdTerm(term,"commit",'Main>',3,2)
    lWaitCmdTerm(term,"exit",'mainMenu>',3,2)
    lWaitCmdTerm(term,"shell",'Password:',3,2)
    lWaitCmdTerm(term,shellpassword,'#',3,2)      
    lWaitCmdTerm(term,"ht_led_test 1234 start&",'#',3,2)
    term<<"nc 192.168.254.254 1234"; time.sleep(0.2)
    data=lWaitCmdTerm(term,"cat cl2400/scripts/env.sh",'YOCTO',5,2)
    parent.SendMessage("Arm nc to Atom success\n",log,color=2)
    try: 
        drv_ver=data.split('clr_package_version=')[-1].split('export')[0].strip()
        parent.SendMessage( "WIFI driver: %s\n"%drv_ver,log)
    except:
        parent.SendMessage("== parsing error ==\n%s\n"%data,log) 
        #raise Except("== parsing error ==\n%s\n"%data)
    parent.SendMessage("Create connection time: %3.2f (sec)\n"%(time.time()- test_time),log)
    parent.SendMessage("---------------------------------------------------------------------------\n",log)

def EnableWifiInterface(parent,term,interface,run,log):
    if not run: parent.SendMessage("Init %s Interface(%d)...\n"%(interface,run),log)
    else: parent.SendMessage("Re-init %s Interface(%d)...\n"%(interface,run),log)
    test_time=time.time()
    result=0
    for try_ in xrange(3):
       test_time_ = time.time()
       lWaitCmdTerm(term,ap_argv[interface][1],promp,10)
       channel = ap_channel[interface][0]
       random.shuffle(channel); print channel
       lWaitCmdTerm(term,'{} {}'.format(ap_channel[interface][1], channel[0]), promp, 10)
       while time.time()-test_time_<10:
          data=lWaitCmdTerm(term,'iwconfig {}'.format(ap_argv[interface][0]),promp,3); print data
          if ap_argv[interface][2] not in data: time.sleep(1); continue
          else: 
             #lWaitCmdTerm(term,ap_argv[interface][2],'#',3); 
             result=1; break
       if result: break
       if try_==2 and not result: raise Except('FAIL: wifi interface(%s): \n%s'%(interface,data))
    parent.SendMessage(lWaitCmdTerm(term,"iwconfig %s"%ap_argv[interface][0],"#",3)+'\n',log)
    parent.SendMessage("%s up internal(%d) time: %3.2f (sec)\n"%(interface,run,(time.time()- test_time)),log)
    parent.SendMessage("---------------------------------------------------------------------------\n",log)

def check_production_dat(parent,term,interface,log):
    data=lWaitCmdTerm(term,'grep "ce_recalib_dcoc\|ce_recalib_iq" %s/CL2400.dat'%ap_argv[interface][2],promp,30); print data    
    parent.SendMessage("%s.Production_DAT:\n%s\n"%(interface,data),log)
    if '4.6.92' in data: raise Except("ErrorCode[2000]: DUT Issue | %s_Production_DAT Failure"%interface)
    return 1    
      
def LinkPing(ip,count):
    #print ip
    result = os.popen('ping -w 1000 -n %d %s'%(count,ip)).read(); print result
    return float(result[result.rfind("(")+1:result.rfind("%")])

def IsConnect(ip,timeout):
    ip = ip.strip()
    current = time.time()
    timeout += current
    os.popen("arp -d")
    while current < timeout:
        rate = LinkPing(ip,3)
        if rate == 0: return 1 
        time.sleep(1)                             
        current = time.time()
    return 0

def IsConnect(ip,timeout):
    ip = ip.strip()
    current = time.time()
    timeout += current
    os.popen("arp -d")
    while current < timeout:
        try:
            data=int(os.popen("ping %s -n 3"%ip).read().split('(')[-1].split('%')[0])
        except:
            data=100
        if not data:return 1
        current = time.time()
    return 0

def IsConnect_board(ip,timeout):
    ip = ip.strip()
    current = time.time()
    timeout += current
    os.popen("arp -d")
    while current < timeout:
        try:
            data=int(os.popen("ping %s -n 5"%ip).read().split('(')[-1].split('%')[0])
        except:
            data=100
        if not data:return 1
        current = time.time()
    return 0

def IsDisconnect(ip,timeout):
    ip = ip.strip()
    current = time.time()
    timeout += current
    os.popen("arp -d")
    while current < timeout:
        rate = LinkPing(ip,3)
        if rate == 100: return 1  
        time.sleep(1)
        current = time.time()
    return 0
              
def CheckRemoteLink(SSID,R_IP,Timeout):
      print 'waitting remote PC link to UUT...'
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.sendto('%s,%s,%s'%(SSID,R_IP,Timeout), ((s_IP, 65534)))
      s.close()
      server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      server.settimeout(Timeout+10)
      server.bind(("", 65534))

      try:
         data,address = server.recvfrom(256)
         #print data
         server.close()
         if str(data) == 'OK':
             print 'Remote PC link is up'
             return 1
         else:return 0
      except (socket.timeout):
         return 0


def iperfN(parent,term,ssid,remote,interface,log):
    val = []
    link_rate = [None,None]
    direction = {0:"Transmit",1:"Receive"}
    test_fail = 0
    parent.SendMessage("%s WIFI Throughput Test...\n"%interface,log)
    test_time=time.time()

    for try_ in range(2):
        for j in range(3):
            if CheckRemoteLink(ssid,remote,30):
                break
            if j == 2:
                raise Except ("failed:Remote PC link to UUT timeout!")
        time.sleep(2)
        if not IsConnect('%s'%remote,10):continue
        val = []
        link_rate = [None,None]
        test_fail = 0
        data = os.popen("iperf -c %s -t 8 -w 212K -P 8 -r"%remote).read() 
        print data
        try:
            for k in data.splitlines():
                if  '[SUM]' in k:
                    val.append(float(k.split()[-2]))              
        except:
            if try_==1:raise Except ("FAIL:Get Tx/Rx Value:" + val)
        
        traffic_=""
        for i in range(2):        
            msg = "%s %s throughput = %.2f ( >= %d )\n"%(interface,direction[i],val[i],throughput_criteria[interface][i])  
            traffic_=traffic_+msg  
            if val[i] < throughput_criteria[interface][i]: 
                print msg
                test_fail+=1
            #else: parent.SendMessage(msg,log,color=2)            
        if test_fail==0:
            parent.SendMessage(traffic_,log,color=2)
            break
        else:
            if try_==1:
                term.get()
                data_=term<<"iw wlan0_0 station dump"
                time.sleep(0.5)
                data_=term.get()
                #print data_
                parent.SendMessage(data_,log)
                parent.SendMessage(traffic_,log)
                raise Except('FAIL: %s WIFI Throughput Test'%interface)
    #if test_fail > 0 :  raise Except('FAIL: %s WIFI Throughput Test'%interface)
    term.get()
    data_=term<<"iw wlan0_0 station dump"
    time.sleep(0.5)
    data_=term.get()
    #print data_
    parent.SendMessage(data_,log)
    
    parent.SendMessage("%s WIFI Throughput Test PASS\n"%(interface),log,color=2)
    parent.SendMessage( "%s WIFI Throughput Test time: %3.2f (sec)\n"%(interface,(time.time()- test_time)) ,log)
    parent.SendMessage( "---------------------------------------------------------------------------\n",log)
    return(link_rate[1],link_rate[0],val[1],val[0])  

def iperfN__(parent,wls_n_throughput_tx,wls_n_throughput_rx,ssid,remote,term,log):
    parent.SendMessage("2.4G WIFI Throughput Test...\n",log)
    direction = {0:"Transmit",1:"Receive"}
    va1=va2=0
    for i in xrange(3):
        for j in range(3):
            if CheckRemoteLink(ssid,remote,30):
                break
            if j == 2:
                raise Except ("failed:Remote PC link to UUT timeout!")
        time.sleep(2)
        if not IsConnect('%s'%remote,10):continue
        for k in range(3):
            n = os.popen('iperf.exe -c %s -n 100000 -t 5 -w 212k -r'%remote)
            data = n.read()
            n.close()
            if data.count('Mbits/sec') > 1:
                value = data.splitlines(14)
                va1 = str(value[10]).split("MBytes")[-1].split("Mbits/sec")[0].strip()
                va2 = str(value[13]).split("MBytes")[-1].split("Mbits/sec")[0].strip()
                break
            if k == 2:
                raise Except ("failed:Get Tx/Rx Value FAIL!")
                
        if (float(va1)>=wls_n_throughput_tx) and (float(va2)>=wls_n_throughput_rx):
            SetPatternColor(1)
            print "2.4G Transmit throughput = %.2f Mbits/sec(>%s)" % (float(va1),wls_n_throughput_tx)
            print "2.4G Receive throughput = %.2f Mbits/sec(>%s) \n" % (float(va2),wls_n_throughput_rx)
            SetPatternColor()
            break
        else:
            if i == 2: break
            print "\nTry %d to retest.\n" % i


    msg1 = "N mode BandWidth TX is %.2f Mbits/sec less than %f Mbits/sec."%(float(va1),wls_n_throughput_tx)
    msg2 = "N mode BandWidth RX is %.2f Mbits/sec less than %f Mbits/sec."%(float(va2),wls_n_throughput_rx)
    if (float(va1)<wls_n_throughput_tx) and (float(va2)<wls_n_throughput_rx):
        raise Except("Fail:"+msg1+"\n     "+msg2)
    if (float(va1)<wls_n_throughput_tx):
        raise Except("Fail:"+msg1)
    if (float(va2)<wls_n_throughput_rx):
        raise Except("Fail:"+msg2)

def getSelfAddr():
    ip = socket.gethostbyname_ex(socket.gethostname())
    for i in ip[-1]:
       if '172.28.' in i:
          return i
    return 0

def lLogin(dstip,pid,username,password):
    #term.host -- dst ip
    #term.port -- dst port
    #uid must be 101
    print 'Telnet login Start'
    for k in range(5):
        if isPortConnect(dstip,pid):
           print 'The port is open,wait telnet'
           break
        else:
           time.sleep(1)
           if k==4:raise Except('The port is close')          
    for a in range(5):
      time.sleep(2)
      access=0
      term = htx_wifi.Telnet(dstip,pid)
      #term=Telnet(dstip,pid,3)
      data = term.wait("login:",5)[-1]
      print '[%s]%s'%(time.ctime(),data)
      print username
      print password    
      for i in range(5):
          term << username
          time.sleep(2)
          term << password
          data=term.wait('>',15)[-1]
          print '[%s]%s'%(time.ctime(),data)
          if '101' in data: access=1; break 
          else: term<<'\x03'; break
          if i == 4:
            term << '\x03'
            raise Except('Telnet login Failure')
      if access: return term            

def CheckMac(parent,term,mac,log):
    print " "
    print "Check MAC"
    rf_mac = "%012X"%(int(mac,16))
    lan_mac = "%012X"%(int(mac,16)+2)
    #usb_host_mac = "%012X"%(int(mac,16)+1)
    
    rf_mac = rf_mac[0:2]+"-"+rf_mac[2:4]+"-"+rf_mac[4:6]+"-"+rf_mac[6:8]+"-"+rf_mac[8:10]+"-"+rf_mac[10:12]
    lan_mac = lan_mac[0:2]+"-"+lan_mac[2:4]+"-"+lan_mac[4:6]+"-"+lan_mac[6:8]+"-"+lan_mac[8:10]+"-"+lan_mac[10:12]
    #usb_host_mac = usb_host_mac[0:2]+"-"+usb_host_mac[2:4]+"-"+usb_host_mac[4:6]+"-"+usb_host_mac[6:8]+"-"+usb_host_mac[8:10]+"-"+usb_host_mac[10:12]
    usb_host_mac = "00-00-00-00-00-00"
    #lWaitCmdTerm(term,"cli",">",8,2)
    lWaitCmdTerm(term,"doc","docsis>",5)
    lWaitCmdTerm(term,"Prod","Production>",5)
    term.get()
    data = lWaitCmdTerm(term,"prodsh","Production>",5,3)
    for i in data.split("\n"):
        if "Cable Modem MAC" in i:
            msg = "RF MAC:" + i.split("<")[1].split(">")[0] + " (%s) "%rf_mac
            if not rf_mac in i:raise Except ("failed:%s"%msg)
            parent.SendMessage( "%s\n"%msg,log)
            break

def CheckMac(parent,mac,cpu,log):
    ###"Check MAC"###
    l2sd0_2_mac = "%012X"%(int(mac,16)+7)
    mac = l2sd0_2_mac[0:2]+"-"+l2sd0_2_mac[2:4]+"-"+l2sd0_2_mac[4:6]+"-"+l2sd0_2_mac[6:8]+"-"+l2sd0_2_mac[8:10]+"-"+l2sd0_2_mac[10:12]
    for t in xrange(3):
        sp.check_call(['ping',ap_ip[cpu],'-n','1'])
        if mac.lower() in sp.check_output(['arp','-a']): 
            parent.SendMessage('Label MAC matched : %s'%sp.check_output(['arp','-a']),log)
            break
        else:
            if t == 2: raise Except("Failed: label mac mismatched") 
            sp.call(['arp','-d'])

def CheckMac(parent,mac,cpu,run,log):
    ###"Check MAC"###
    l2sd0_2_mac = "%012X"%(int(mac,16)+7)
    mac = l2sd0_2_mac[0:2]+":"+l2sd0_2_mac[2:4]+":"+l2sd0_2_mac[4:6]+":"+l2sd0_2_mac[6:8]+":"+l2sd0_2_mac[8:10]+":"+l2sd0_2_mac[10:12]
    term =htx_wifi.Telnet(ap_ip[cpu])
    for t in xrange(3):
        term<<'ping 192.168.254.254 -w 1'; time.sleep(1)
        data=lWaitCmdTerm(term,'arp | grep eth0.4093','#',3); print data
        if mac.lower() in data: 
            parent.SendMessage('Label MAC matched : %s\n'%data,log,color=2)
            break
        else:
            if t == 2: raise Except("Failed: label mac mismatched") 

def getmac(mac):
    ServerIP = '127.0.0.1'
    ServerPort = 1800
    timeout = 30
    sn = ""
    MesSocket=htx_wifi.UDPService(ServerIP,int(ServerPort),int(timeout))
    MesSocket.set('2,' + mac)  
    Result=MesSocket.get()
    print Result
    Result=Result.strip()
    if Result:
       if len(Result)<>12 or Result[0] == '2':
          raise Except("ErrorCode(0005):Get MAC Failed:%s"%Result)
       else:
          sn = Result
          return sn
    raise Except("ErrorCode(0005):Connection MES Server Fail ")

def ChkWifiMac(parent,term,interface,mac,log):
    parent.SendMessage("Check %s WIFI MAC... \n"%interface,log)
    test_time=time.time()
    mac = "%012X"%(int(mac,16)+int(mac_rule[interface]))
    wifimac = mac[0:2]+":"+mac[2:4]+":"+mac[4:6]+":"+mac[6:8]+":"+mac[8:10]+":"+mac[10:12]
    term.get()
    data=lWaitCmdTerm(term,"iw %s e2p get mac"%ap_argv[interface][0],promp,5,2); #raw_input(data)
    if wifimac.lower() not in data: raise Except('[%s] Fail: %s - mismatch(%s)'%(interface,data,wifimac)) 
    parent.SendMessage('[%s]: %s\n'%(interface,data),log) 
    parent.SendMessage("WIFI MAC check time: %3.2f (sec)\n"%(time.time()-test_time),log)
    parent.SendMessage("---------------------------------------------------------------------------\n",log)

def FactoryReset(parent,arm_ip,log):    
    test_time = time.time()
    parent.SendMessage("Factory Reset Start...\n",log) 
    term=Telnet_arm(parent,arm_ip,log)
    lWaitCmdTerm(term,"rg","MAIN>",8)
    lWaitCmdTerm(term,"reset cleanall","factory defaults? (Y or N)",15)
    data=lWaitCmdTerm(term,"Y","MAIN>",30)
    time.sleep(1)
    parent.SendMessage("%s\n"%data,log) 
    if not htx_wifi.IsDisconnect(target,30):
       raise Except("Fail: Can't reset in 30 seconds")
    parent.SendMessage("Reboot...\n",log) 
    time.sleep(25)
    parent.SendMessage("Factory Reset Finished\n",log,color=2) 
    parent.SendMessage("Factory Reset Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
    parent.SendMessage("---------------------------------------------------------------------------\n",log)

def readytouse(*args):
    print '**********************'
    EnableWifiInterface(args[0],args[1],args[2])

def RestoreDat(parent,term,log):
    #term=htx_wifi.Telnet(ap_ip['atom']); time.sleep(2)
    #lWaitCmdTerm(term,'root',promp,5)
    parent.SendMessage("Restore default Configuration...",log)
    data=lWaitCmdTerm(term,'/cl2400/scripts/restore_defaults.sh all',promp,30); print data
    parent.SendMessage("\n%s\n"%(data),log)
    data=lWaitCmdTerm(term,dat_cmd,promp,30); print data    
    parent.SendMessage("%s\n"%(data),log)
    if '+' not in data: raise Except("ErrorCode[1000]: Operating Issue | ce_dat_restore.sh not found")
    data=lWaitCmdTerm(term,'grep "ce_recalib_dcoc\|ce_recalib_iq\|bss_num\|ce_lam_enable\|first_mask_bit" /nvram/cl2400/CL2400.dat',promp,30); print data    
    parent.SendMessage("CL2430:%s\n"%(data),log)
    if '4.6.92' in data: raise Except("ErrorCode[2000]: DUT Issue | CL2430_DAT Failure")
    data=lWaitCmdTerm(term,'ls /nvram/cl2400',promp,30); print data    
    parent.SendMessage("CL2430 file:\n%s\n"%(data),log)
    if '4.6.92.8.2.0' in data: raise Except("ErrorCode[2000]: DUT Issue | CL2432_DC/IQ Failure")
    
    data=lWaitCmdTerm(term,'grep "ce_recalib_dcoc\|ce_recalib_iq\|bss_num\|ce_lam_enable\|first_mask_bit" /nvram/cl2400_24g/CL2400.dat',promp,30); print data    
    parent.SendMessage("CL2430:%s\n"%(data),log)
    if '4.6.92' in data: raise Except("ErrorCode[2000]: DUT Issue | CL2432_DAT Failure")
    data=lWaitCmdTerm(term,'ls /nvram/cl2400_24g',promp,30); print data    
    parent.SendMessage("CL2432 file:\n%s\n"%(data),log)
    if '4.6.92.8.2.0' in data: raise Except("ErrorCode[2000]: DUT Issue | CL2432_DC/IQ Failure")

def BTScan(parent,mac,log):
    mac2 = "%012X"%(int(mac,16) + 3)
    btmac = mac2[0:2]+":"+mac2[2:4]+":"+mac2[4:6]+":"+mac2[6:8]+":"+mac2[8:10]+":"+mac2[10:12]
    test_time = time.time()
    btmac = '58:EF:68:84:4A:FB'
    for i in xrange(5):
        data = os.popen('.\\BTexe\\btdiscovery').read(); print data
        if btmac in data:
            parent.SendMessage("BT Scan: {}\n".format(data),log,color=2) 
            parent.SendMessage("BT Test time: %3.2f (sec)\n"%(time.time()- test_time) ,log)
            parent.SendMessage("---------------------------------------------------------------------------\n",log)
            return 0
    raise Except('BT Test Failed: {}'.format(data))

def w21_production(parent):
    gd_term=0
    result = 0
    log = None
    file = None
    term = None
    gd_term = None
    mac = str()
    parent.SendMessage("START",state = "START")
    start_time = end_time = 0
    try:
        gd_term=htx_wifi.SerialTTY(comport[0],b_rate)
        mac=GetMacAddress(parent)
        #mac=mac.strip().upper()
        if mac[0]=="3":mac=getmac(mac)
        logname = logPath+mac+'_'+test_item[0]+".w21"
        log = htx_wifi.RedirectStdout(open(logname,"w")) 
        checktravel(mac,'127.0.0.1',1800,30)
        station_ip = getSelfAddr()
        msg = "station_ip=%s"%(station_ip)
        #log = open(logPath+mac+'_'+test_item[0]+".w21","w")    
        start_time=time.time()
        parent.SendMessage("HIVE-2200 Throughput/RSSI production version: %s , Station: %s\n"%(version,Teststation),log)
        parent.SendMessage( "---------------------------------------------------------------------------\n",log)
        parent.SendMessage( "DUT MAC:"+mac+"\n",log)
        parent.SendMessage( "Start Time:"+time.ctime()+"\n",log)
        parent.SendMessage( "%s\n"%msg,log)
        parent.SendMessage( "---------------------------------------------------------------------------\n",log)
        interface_list=ap_argv.keys()
        random.shuffle(interface_list)
        term=CheckNrm(parent,term,mac,log)
        result = BTScan(parent, mac, log)     
        for interface in interface_list:
            for retry_ in xrange(3):
                result=0
                EnableWifiInterface(parent,term,interface,retry_,log)
                if ChkConnetction(parent,term,interface,gd_term,30,retry_,log):
                   result=IperfThroughput(parent,term,gd_term,interface,retry_,log)
                   if not result: break
                if retry_==2: raise Except('FAIL: %s Iperf no response\n'%(interface)) #raise Except('FAIL: %s Connection\n'%(interface))
        if product_mode:
            data = lWaitCmdTerm(term, 'pmf -q', 'product mode', 10)
            parent.SendMessage('{}'.format(data),log,color=2)
        #travel = passtravel(mac,'127.0.0.1',1800,30)
    except Except,msg: 
        parent.SendMessage("\n%s\n"%msg,log,color=1)
        result = 1
        #travel = passtravel(mac,'127.0.0.1',1800,30)
    except:
        parent.SendMessage("%s"% traceback.format_exc(),log,color=1)
        parent.SendMessage("%s"% traceback.print_exc(),log,color=1)
        result=1   
        #travel = passtravel(mac,'127.0.0.1',1800,30)
    if travel or result:
      print 'fail' 
      parent.SendMessage('',state = "FAIL")
      parent.SendMessage("\nTest Result: FAIL",log,color=1) 
    else:
      print 'pass' 
      parent.SendMessage('',state = "PASS")
      parent.SendMessage("\nTest Result: PASS",log,color=2)        
    end_time = time.time()
    parent.SendMessage("\nEnd Time:"+time.ctime(),log)
    parent.SendMessage("\nTotal Test Time: %3.1f sec"%(end_time-start_time),log) 
    log.close()
    gd_term=None
            
def w21_lab(parent):
    gd_term=0
    result = 0
    log = None
    file = None
    term = None
    gd_term = None
    mac = str()
    parent.SendMessage("START",state = "START")
    start_time = end_time = 0
    try:
        #term=htx_wifi.Telnet(ap_ip['atom'])
        gd_term=htx_wifi.SerialTTY(comport[0],b_rate)
        mac = GetMacAddress(parent)
        result=0            
        parent.SendMessage("START",state = "START")
        log = open(logPath+mac+".tpt","w")
        file=logPath+mac+'.tpt'
        #parent.SendMessage('****** no.%s*******\n'%i,log)
        start_time=time.time()
        parent.SendMessage("HIVE-2200 Throughput/RSSI production version: %s , Station: %s\n"%(version,Teststation),log)
        parent.SendMessage( "---------------------------------------------------------------------------\n",log)
        parent.SendMessage( "DUT MAC:"+mac+"\n",log)
        parent.SendMessage( "Start Time:"+time.ctime()+"\n",log)
        parent.SendMessage( "---------------------------------------------------------------------------\n",log)
        interface_list=ap_argv.keys()
        random.shuffle(interface_list)       
        term=CheckNrm(parent,term,mac,log)
        #result = BTScan(parent, mac, log)
        for interface in interface_list:
            for retry_ in xrange(3):
                result=0
                EnableWifiInterface(parent,term,interface,retry_,log)
                if ChkConnetction(parent,term,interface,gd_term,30,retry_,log):
                   result=IperfThroughput(parent,term,gd_term,interface,retry_,log)
                   if not result: break
                if retry_== 2: raise Except('FAIL: %s Iperf no response\n'%(interface)) #raise Except('FAIL: %s Connection\n'%(interface))
        if product_mode:
            data = lWaitCmdTerm(term, 'pmf -q', 'product mode', 10)
            parent.SendMessage('{}'.format(data),log,color=2)    
        parent.SendMessage('',state = "PASS"); parent.SendMessage("\nTest Result: PASS"+'',log,color=2)
        end_time = time.time()
        parent.SendMessage('\n'+"End Time:"+time.ctime()+'',log)
        parent.SendMessage("\nTotal Test Time: %3.1fs"%(end_time-start_time)+'',log)
        log.close()
        update_file=logPath+mac+'_PASS.tpt'
        os.rename(file,update_file+'('+time.strftime("%H'%M'%S',%Y-%m-%d",time.localtime())+')')      
        #Snmp.SnmpSet("192.168.1.10","1.3.6.1.4.1.26104.1.1.1.5.1.24","i",3,community="public")  #.24 #Power 1 , .25 Power 2, .31 power 8
        #term_=lLogin(ap_ip['arm'],23,username='admin',password='Hitron')
        #term_<<'reboot'; time.sleep(20)
    except Except,msg: 
        if not log:
            log = open(logPath+mac+".tpt","w")
        if not file:
            file=logPath+mac+'.tpt'
        #parent.SendMessage("%s"% traceback.format_exc(),log,color=1)
        parent.SendMessage("\n%s\n"%msg,log,color=1)
        parent.SendMessage('',state = "FAIL"); parent.SendMessage("\nTest Result: FAIL"+'',log,color=1) 
        end_time = time.time()
        parent.SendMessage('\n'+"End Time:"+time.ctime()+'',log)
        parent.SendMessage("\nTotal Test Time: %3.1fs"%(end_time-start_time)+'',log) 
        log.close()
        update_file=logPath+mac+'_Fail.tpt'
        os.rename(file,update_file+'('+time.strftime("%H'%M'%S',%Y-%m-%d",time.localtime())+')')
        #Snmp.SnmpSet("192.168.1.10","1.3.6.1.4.1.26104.1.1.1.5.1.24","i",3,community="public")  #.24 #Power 1 , .25 Power 2, .31 power 8
        #term_=lLogin(ap_ip['arm'],23,username='admin',password='Hitron')
        #term_<<'reboot'; time.sleep(20)
        result=1
    except:
        parent.SendMessage("%s"% traceback.format_exc(),log,color=1)
        parent.SendMessage("%s"% traceback.print_exc(),log,color=1)
        parent.SendMessage('',state = "FAIL"); parent.SendMessage("\nTest Result: FAIL"+'',log,color=1) 
        end_time = time.time()
        parent.SendMessage('\n'+"End Time:"+time.ctime()+'',log)
        parent.SendMessage("\nTotal Test Time: %3.1fs"%(end_time-start_time)+'',log) 
        log.close()
        update_file=logPath+mac+'_Fail.tpt'
        os.rename(file,update_file+'('+time.strftime("%H'%M'%S',%Y-%m-%d",time.localtime())+')')
        #Snmp.SnmpSet("192.168.1.10","1.3.6.1.4.1.26104.1.1.1.5.1.24","i",3,community="public")  #.24 #Power 1 , .25 Power 2, .31 power 8
        #term_=lLogin(ap_ip['arm'],23,username='admin',password='Hitron')
        #term_<<'reboot'; time.sleep(20)
        result=1
    if not result: parent.SendMessage('',state = "PASS")
    gd_term=None
    
"""
def w21_retest_opt(parent):
    try: 
        result = 0
        log = None
        mac = str()
        rcd=None
        parent.SendMessage("",state = "START")
        start_time = end_time = 0
        mac = GetMacAddress(parent)
        t= str(round(time.time(),1)).split(".")
        log = open(logPath+mac+".W21","w")
        start_time=time.time()
        gd_term=htx_wifi.SerialTTY(com_port,b_rate)
        Check_boot(parent,'atom',time_out,log)
        #CheckMac(parent,mac,'atom',log)
        term=htx_wifi.Telnet(ap_ip['atom'])
        flow=R_Flow(term)
        '''
        ###mutileprocess###
        multiprocessing.freeze_support()
        pool=multiprocessing.Pool(multiprocessing.cpu_count())
        results=[]
        function_list=[[readytouse,(parent,'2.4G',log)],[readytouse,(parent,'5G',log)]]
        for func in function_list:  
            results.append(pool.apply_async(func[0],args=(func[-1])))    
        pool.close()
        pool.join()
        #for result in results: print result.get(); raw_input('multiprocessing')
        #######################
        '''
        term<<'sh -x /nvram/MFG/ht_cl_normal.sh'
        rcd=flow.GetMfgRecord(term)
        for idx,item in enumerate(test_item):
            print item
            if flow.ChkMfgRecord(rcd,idx): continue
            if item == '2.4G' or item == '5G':
               EnableWifiInterface(parent,item,log)
               ChkWifiMac(parent,item,mac,term,log)
               ChkConnetction(parent,item,gd_term,30,log)
               IperfThroughput(parent,gd_term,item,log)
               flow.SetMfgRecord(term,rcd,idx)
            else:
               pass
               #toogle=eval(test_function[item])
               #if toogle: flow.SetMfgRecord(term,rcd,idx)
        flow.SaveRcdLog(term,rcd)
        #factoryreset
    except Except,msg:
        parent.SendMessage("\n%s\n"%msg,log,color=1)
        flow.SaveRcdLog(term,rcd)
        result = 1
    except: 
        parent.SendMessage("\n%s\n"% traceback.print_exc(),log,color=1)
        flow.SaveRcdLog(term,rcd)
        result = 1

    end_time = time.time()
    parent.SendMessage('\n'+"End Time:"+time.ctime()+'\n',log)
    parent.SendMessage("total time: %3.2f"%(end_time-start_time)+'\n',log)
    file=logPath+mac+".W21"
    if result:
       parent.SendMessage( "Test Result:FAIL"+'\n',log,color=1)
       parent.SendMessage('',state = "FAIL")
       log.close()
       update_file=logPath+mac+'_Fail.W21'
       os.rename(file,update_file+'('+time.strftime("%H'%M'%S',%Y-%m-%d",time.localtime())+')')
    else:
       parent.SendMessage( "Test Result:PASS"+'\n',log,color=2)
       parent.SendMessage( "",state = "PASS") 
       log.close()
       update_file=logPath+mac+'_PASS.W21'
       os.rename(file,update_file+'('+time.strftime("%H'%M'%S',%Y-%m-%d",time.localtime())+')')
    term=None
"""  