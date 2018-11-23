import sys,os,string,time,telnetlib,re,serial,subprocess,ctypes,_winreg,bz2,thread
from errno import ESHUTDOWN
from win32file import ReadFile, WriteFile
from win32pipe import PeekNamedPipe
import win32api,msvcrt,Power,ColorConsole,socket,Snmp
from sysVars import *
import win32pdh,win32con
#import numpy,mechanize
from telnetlib import DO, DONT, WILL, WONT, theNULL, TTYPE, IAC, SB,SE, ECHO
import paramiko
#import winpcapy 


RESULT = [""]
backup_sys_stdout = sys.stdout

def telnet_negotiation(sock, command, option):
    #
    # Here's a function I came up with to handle sub-negotiation.
    # During session negotiation, the server can ask a series of
    # "will you or won't you" questions of the client. One of
    # those questions happens to be:
    # "Will you tell me what terminal type you are?"
    # This question is the only one out of the possible list of
    # such questions that I respond with "Yes, I will." Then later
    # the function reports that the terminal type is a DEC VT-100.
    # If you don't do the sub-negotiation and the server demands
    # to know the terminal type, the Telnet function will report
    # that the terminal type is simply "network". No server will
    # recognize this, and some will refuse to even start a session
    # with you using some default terminal type.
    # A couple of good links--
    # http://www.cs.cf.ac.uk/Dave/Internet/node136.html
    # http://www.scit.wlv.ac.uk/rfc/rfc8xx/RFC854.html
    #
    negotiation_list=[
        ['BINARY',WONT,'WONT'],
        ['ECHO',WONT,'WONT'],
        ['RCP',WONT,'WONT'],
        ['SGA',WONT,'WONT'],
        ['NAMS',WONT,'WONT'],
        ['STATUS',WONT,'WONT'],
        ['TM',WONT,'WONT'],
        ['RCTE',WONT,'WONT'],
        ['NAOL',WONT,'WONT'],
        ['NAOP',WONT,'WONT'],
        ['NAOCRD',WONT,'WONT'],
        ['NAOHTS',WONT,'WONT'],
        ['NAOHTD',WONT,'WONT'],
        ['NAOFFD',WONT,'WONT'],
        ['NAOVTS',WONT,'WONT'],
        ['NAOVTD',WONT,'WONT'],
        ['NAOLFD',WONT,'WONT'],
        ['XASCII',WONT,'WONT'],
        ['LOGOUT',WONT,'WONT'],
        ['BM',WONT,'WONT'],
        ['DET',WONT,'WONT'],
        ['SUPDUP',WONT,'WONT'],
        ['SUPDUPOUTPUT',WONT,'WONT'],
        ['SNDLOC',WONT,'WONT'],
        ['TTYPE',WILL,'WILL'],
        ['EOR',WONT,'WONT'],
        ['TUID',WONT,'WONT'],
        ['OUTMRK',WONT,'WONT'],
        ['TTYLOC',WONT,'WONT'],
        ['VT3270REGIME',WONT,'WONT'],
        ['X3PAD',WONT,'WONT'],
        ['NAWS',WONT,'WONT'],
        ['TSPEED',WONT,'WONT'],
        ['LFLOW',WONT,'WONT'],
        ['LINEMODE',WONT,'WONT'],
        ['XDISPLOC',WONT,'WONT'],
        ['OLD_ENVIRON',WONT,'WONT'],
        ['AUTHENTICATION',WONT,'WONT'],
        ['ENCRYPT',WONT,'WONT'],
        ['NEW_ENVIRON',WONT,'WONT']
    ]
    if ord(option)<40:
        received_option=negotiation_list[ord(option)][0]
        response=negotiation_list[ord(option)][1]
        print_response=negotiation_list[ord(option)][2]
    else:
        received_option='unrecognised'
        response=WONT
        print_response='WONT'
    if command==DO:
        print "TELNET Debug: Received request to DO %s, sending %s" % \
            (received_option,print_response)
        sock.sendall("%s%s%s" % (IAC, response, option))
    elif command==DONT:
        print 'TELNET Debug: Received the DONT command'
    elif command==WILL:
        print 'TELNET Debug: Received the WILL command'
    elif command==WONT:
        print 'TELNET Debug: Received the WONT command'
    elif command==theNULL:
        print 'TELNET Debug: Received the NULL command'
    elif command==SB:
        print 'TELNET Debug: Received the SB command'
        print ord(option)
        print self.conn.read_sb_data()
    elif command==SE:
        print 'TELNET Debug: Received the SE command'
        print repr(self.conn.read_sb_data())
        sock.sendall("%s%s%s%sDEC-VT100%s%s" % \
            (IAC,SB,TTYPE,chr(0),IAC,SE))
        print 'TELNET Debug: Sent all'
    else:
        print 'TELNET Debug: Received something, don''t know what.', ord(option)
    return

################################################################################
#    Function Library
################################################################################
def SendRemote(remote,data,timeout=0,bind_port=0):
    client = UDPService(remote,servicePort,timeout)
    if not bind_port:
        client.setOption(listen_addr=("",bind_port))
    client.set(bz2.compress(data))



def WaitRemote(port=servicePort,timeout=10):
    server = UDPService("",0,timeout)
    server.setOption(listen_addr=("",port))
    return bz2.decompress(server.get())



def ExtractFloat(data):
    return re.findall(r'[+-]?\d+\.?\d*',data)



def IsConnect(ip,timeout):
    ip = ip.strip()
    current = time.time()
    timeout += current
    os.system("arp -d")
    while current < timeout:
        #data = os.popen("ipconfig").read()
        #if data.find("IP Address")>=0 and data.find(ip[:ip.rfind(".")+1])>=0 and \
        #   os.popen("ping -w 1000 -n 1 %s"%ip).read().find("Reply")>=0:
        #    return 1
        if os.popen("ping -w 1000 -n 1 %s"%ip).read().find(r"100%")<0:
            return 1
        current = time.time()
    return 0



def IsDisconnect(ip,timeout):
    ip = ip.strip()
    current = time.time()
    timeout += current
    while current < timeout:
        if os.popen("ping -w 500 -n 1 %s"%ip).read().find(r"100%")>=0 and \
           os.popen("ping -w 500 -n 2 %s"%ip).read().find(r"100%")>=0:
            return 1
        time.sleep(1)
        current = time.time()
    return 0



def WalkDir(dir,pattern=""):
    "walk a directory tree, using a generator"
    for f in os.listdir(dir):
        fullpath = os.path.join(dir,f)
        if os.path.isdir(fullpath) and not os.path.islink(fullpath):
            for x in WalkDir(fullpath,pattern):  # recurse into subdir
                yield x
        else:
            if pattern:
                r = re.compile(pattern)
                if not r.match(f):
                    continue
            yield fullpath



def Win32Message(title,text):
    win32api.MessageBox(0,text,title)



def Win32InputBox(title,prompt,defaultvalue=''):
    from pywin.mfc import dialog
    return dialog.GetSimpleInput(prompt,defaultvalue,title)



def TransferString2Unit(format_sample, data):
    if data == None: return None
    if not format_sample: return data
    data = data.strip()
    if type(format_sample) is int:
        if type(data) is str and data[:2].upper() == "0X":
            return int(data,16)
        return int(data)
    elif type(format_sample) is float:
        return float(data)
    return data



def GetValue(name,data,pattern="\n"):
    if type(pattern) in (int,float):
        r = re.compile(name+r"\W+([+-]?\d+\.?\d*)")
    elif pattern == "":
        r = re.compile(name+r"\W+(.+?)[\s\W]")
    elif pattern == "\n":
        r = re.compile(name+r"\W+(.*)")
    else:
        r = re.compile(pattern)
    m = r.search(data)
    if m:
        if pattern == "\n":
            return m.group(1).rstrip()
        return m.group(1)
    return None



def RunCommandList(cmdList,term=""):
    if type(cmdList) is not list:
        term, cmdList = cmdList, term    
    result = RESULT[0]
    res = 0                                   #for local command
    for cmd in cmdList:
        if type(cmd) == str:                    # is prompt
            print cmd
        elif hasattr(cmd,'func_code'):          # is function
            if cmd(term,result):
                print "Error:", cmd.__name__, '"(%s)"'%result
                return 1
        elif type(cmd) == list:                 # is command set
            if len(cmd) == 1:                   # print RESULT
                print result
            elif cmd[0] == None:                # check RESULT
                for i in result.splitlines():
                    if cmd[1] in i:
                        print "Pass: Match string '%s'"%cmd[1]
                        break
                else:
                    print "Fail:", cmd[3]
                    return 1
            elif not cmd[1]:                    # set command(no waiting prompt)
                if not term:
                    os.popen(cmd[0])            # run command in local pc
                else:
                    term.set(cmd[0])
                time.sleep(cmd[2])
            else:                               # setWait command
                if cmd[0] == "":                # if no commands, wait only
                    if not term:
                        print result
                        return 1
                    else:
                        timeout, result = term.wait(cmd[1],cmd[2])
                else:                           # have commands, set and wait
                    if not term:
                        res = os.popen(cmd[0]).read().find(cmd[1])
                    else:
                        timeout, result = term.setWait(cmd[0],cmd[1],cmd[2])
                result = result.split(cmd[1])[0]
                RESULT[0] = result
                if timeout or res < 0:
                    print "Fail:",  cmd[3]
                    print "Result:",result
                    return 1
        else:
            print "Syntax Error:",cmd
    return 0



def GetProcesses():
    win32pdh.EnumObjects(None, None, win32pdh.PERF_DETAIL_WIZARD)
    junk, instances = win32pdh.EnumObjectItems(None,None,'Process', win32pdh.PERF_DETAIL_WIZARD )
    proc_dict = {}
    for instance in instances:
        if proc_dict.has_key(instance):
            proc_dict[instance] = proc_dict[instance] + 1
        else:
            proc_dict[instance]=0
    proc_ids = []
    for instance, max_instances in proc_dict.items():
        for inum in xrange(max_instances+1):
            hq = win32pdh.OpenQuery() # initializes the query handle
            try:
                path = win32pdh.MakeCounterPath( (None, 'Process', instance, None, inum, 'ID Process') )
                counter_handle=win32pdh.AddCounter(hq, path) #convert counter path to counter handle
                try:
                    win32pdh.CollectQueryData(hq) #collects data for the counter
                    type, val = win32pdh.GetFormattedCounterValue(counter_handle, win32pdh.PDH_FMT_LONG)
                    proc_ids.append((instance, val))
                except win32pdh.error, e:
                    print e
                win32pdh.RemoveCounter(counter_handle)
            except win32pdh.error, e:
                print e
            win32pdh.CloseQuery (hq)
    return proc_ids



def KillProcess(id):
    handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, id)
    if handle:
        win32api.TerminateProcess(handle,0)
        win32api.CloseHandle (handle)

def KillImageName(name):
    os.popen('taskkill /F /IM %s /T'%name)


def GetTermPyPath():
    x = _winreg.ConnectRegistry(None,_winreg.HKEY_LOCAL_MACHINE)
    y = _winreg.OpenKey(x, r"Software\TermScript",0,_winreg.KEY_ALL_ACCESS)
    p = _winreg.QueryValueEx(y,"Install_Dir")
    _winreg.CloseKey(y)
    _winreg.CloseKey(x)
    return p[0]



################################################################################
#    Class
################################################################################
class Controller(object):
    def get(self):
        return ""
    def set(self, value):
        pass
    def wait(self,timeout):
        return (False,"")
    def setWait(self,value,timeout):
        return (False,"")
    def isConnect(self):
        return True


class Terminal(Controller):
    LOST_CONNECT = "**Fail Connection **"
    def __init__(self,host,port):
        self.log = DEFAULT_LOG
        self.host = host
        self.cr = "\n"   # default Carriage Return
        self.buffer_size = 32768   # default waiting buffer size
        self.port = port
        self.tn = None

    def _init(self):
        return self.tn
    
    def _get(self):
        pass
    
    def _set(self,value):
        pass

    def _close(self):
        self.tn.close()

    def init(self):
        self.close(0)
        try:
           self._init()
        except:
           self.tn = 0

    def isConnect(self):
        return self.tn

    def __get(self):
        if self.tn == None:
            self.init()
        if self.tn == 0:
            print self.LOST_CONNECT
            return ""
        r=''
        try:            
            r = self._get()
        except:
            self.tn = 0
            print self.LOST_CONNECT
            return ""
        if self.log&2:
            print "[GET]:",r
        #print 'wifi_local', r
        return r

    def get(self):
        if self.tn == None:
            self.init()
        if self.tn == 0:
            print self.LOST_CONNECT
            return ""
        r=''
        try:            
            r = self._get()
        except:
            a, b, c = sys.exc_info()
            print(a)
            print(b)
            print(c)
            self.tn = 0
            print self.LOST_CONNECT
            return ""
        if self.log&2:
            print "[GET]:",r
        #print 'wifi_local', r
        return r
    
    def set(self,value):
        if self.tn == None:
            self.init()
        if self.tn == 0:
            print self.LOST_CONNECT
            return 0
        if self.log&1:
            print "[SET]:",value
        try:  
            self._set(value+self.cr)
        except:
            self.tn = 0
            print self.LOST_CONNECT
            return 0
        #return r

    def close(self,force=1):
        if self.tn:
            self._close()
            self.tn = None
            time.sleep(0.1)
        elif force:
            self.tn = None

    def wait(self,prompt,timeout):
        if self.tn == None:
            self.init()
        if self.tn == 0:
            print self.LOST_CONNECT
            return (False, "")
        prompt = str(prompt)
        timeout += time.time()+0.1
        response = str()
        count = 0 
        while time.time() < timeout and self.tn:
            count += 1
            #if not (count&3):
            #    print "+",
            if len(response)>self.buffer_size:
                response = response[-len(prompt):]
            d = self.get(); #raw_input(d)
            response += d; 
            if not prompt:
                if not d:
                    return (True, response)
            else:
                if prompt in response:
                    #if count >= 3:  print
                    return (True, response)
            #time.sleep(0.1)
        #if count >= 3: print
        if self.log&1:
            print "Terminal: Timeout"
        return (False, response)

    def __del__(self):
        self.close()

    def getOption(self,optionName):
        return self.__dict__[optionName]

    def setOption(self,**options):
        for k in options.keys():
            self.__dict__[k] = options[k]

    def setWait(self,setData,prompt,timeout):
        if self.tn == 0:
            print self.LOST_CONNECT
            return (False,"")
        self.set(setData)
        return self.wait(prompt,timeout)

    def __repr__(self):
        return self.get()

    def __call__(self):
        return self.get()

    def __str__(self):
        return self.get()

    def __lshift__(self,data):
        return self.set(data)

def TCPKeepAlive(tn,t):
    while 1:
          for i in range(t*100):
              if not tn:return
              time.sleep(t/100.0)
          try:
             tn.sock.sendall("\xff\xf1")
          except:break

class Telnet(Terminal):
    def __init__(self,host,port=23,keepalive = 0):
        Terminal.__init__(self,host,port)
        self.keepalive = int(keepalive)

    def _init(self):
        self.tn = telnetlib.Telnet()
        self.tn.set_option_negotiation_callback(telnet_negotiation)
        self.tn.open(self.host,self.port)
        self.tn.get_socket().setblocking(0)
        #self.tn.debuglevel(2)
        time.sleep(0.5)
        if self.keepalive:
           thread.start_new_thread(TCPKeepAlive,(self.tn,self.keepalive))

    def _get(self):
        rep = self.tn.read_very_eager()
        t = time.time()
        while time.time() - t <= 0.5:
            rep += self.tn.read_very_eager()
        return rep

    def prv_set(self,value):
        if value[:-1]:self.tn.write(value[:-1])
        #for i in value:
        #    self.tn.write(i)
        time.sleep(0.05)
        self.tn.write(value[-1])
        return len(value)

    def _set(self,value):
        self.tn.write(value)
        time.sleep(0.01)

class ssh(Terminal):
    def __init__(self, host, user='root', psw='', port=22):
        Terminal.__init__(self,host,port)
        self.host = host
        self.user = user
        self.psw = psw
        self.port = port
        self.shell = None
    
    def _init(self):
        self.tn = paramiko.SSHClient()
        self.tn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.tn.connect(self.host, username=self.user, password=self.psw, port=self.port)
        shell = self.tn.invoke_shell()
        self.stdin = shell.makefile('wb', 1024)
        self.stdout = shell.makefile('r', 1024)
        self.finish = 'end of stdOUT buffer'

    def _get(self):
        shout = list()
        sherr = list()
        exit_status = False
        for line in self.stdout:
            if str(line).startswith(self.finish):
                exit_status = int(str(line).rsplit(self.finish)[1])
                if exit_status:
                    sherr = shout
                    #shout = list()
                break
            else:                
                shout.append(re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]').sub('', line).
                             replace('\b', '').replace('\r', ''))
        print shout

        try:
            shout.remove('$?\n')
        except Exception as err:
            print err

        for idx, elm in enumerate(shout):
            if 'echo' in elm and self.finish in elm:
                shout[idx] = elm.split('echo')[0]
                break
        
        shout = ''.join(shout)
        return shout

    def _set(self,value):
        if self.tn.get_transport().is_active():
            #value = value.strip('\n')
            self.stdin.write(value + '\n')
            time.sleep(0.1)
            echo_cmd = 'echo {} $?'.format(self.finish)
            self.stdin.write(echo_cmd + '\n')
            time.sleep(0.1)
            self.stdin.flush()
        else:
            raise ('LOST_CONNECT')


class UDPService(Terminal):
    def __init__(self,host,port,listen_timeout=1):
        Terminal.__init__(self,host,port)
        self.listen_timeout = listen_timeout
        self.cr = ""
        self.addr = None
        self.listen_addr = None

    def _init(self):
        self.tn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.listen_timeout:
            self.tn.settimeout(self.listen_timeout)
        if self.listen_addr:
            self.tn.bind(self.listen_addr)
            time.sleep(0.2)

    def _get(self):
        try:
            data, self.addr = self.tn.recvfrom(65536)
        except socket.timeout:
            data = ""
        return data

    def _set(self,value):
        self.tn.sendto(value, (self.host, self.port))
        return len(value)



class TCPClient(Terminal):
    def __init__(self,host,port,timeout=1):
        Terminal.__init__(self,host,port)
        self.timeout = timeout
        self.cr = "\n"

    def _init(self):
        self.tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.timeout:
            self.tn.settimeout(self.timeout)
            time.sleep(0.1)
        self.tn.connect((self.host,self.port))
        time.sleep(0.1)

    def _get(self):
        try:
            data = self.tn.recv(65536)
        except socket.timeout:
            data = ""
        return data

    def _set(self,value):
        self.tn.send(value)
        return len(value)



class SerialTTY(Terminal):
    def __init__(self,host,port=115200):
        Terminal.__init__(self,host,port)

    def _init(self):
        try:
            self.tn = serial.Serial(self.host, self.port, timeout=0.5)
        except:
            self.tn = 0

    def _get(self):
        buf = str()
        wait=0
        while wait<2:
            time.sleep(0.05)
            count = self.tn.inWaiting()
            if not count: wait+=1
            else: 
               wait=0
               buf += self.tn.read(count)
        return buf

    def _set(self,value):
        self.tn.write(value)
        #return len(value)

LEFT_CCU = 0
RIGHT_CCU = 1

class PacketTTY(Terminal):
    def __init__(self,host,port):
        Terminal.__init__(self,host,port)
       
    def _init(self):
        flag = [0]*2
        for self.dev in winpcapy.GetNIC():
            print self.dev
            if self.host in self.dev:
               self.tn  =  winpcapy.open_live(self.dev)
               for try_ in range(3):
                   winpcapy.sendto(self.tn,'info',0) 
                   for try__ in range(5):
                       if flag.count(1) == 2:return
                       self.rev = winpcapy.Recived(self.tn)
                       if self.rev:   
                          d = self.getValue(self.rev)
                          if 'CCU\tinfo\t' in d:
                             c = d.split()
                             if c[2]=='0':
                                dst_mac=[]
                                for mac in c[3].upper().split(':'):
                                    dst_mac.append(int(mac,16))
                                winpcapy.dst_mac[0] = dst_mac
                                flag[0] = 1
                             if c[2]=='1':
                                dst_mac=[]
                                for mac in c[3].upper().split(':'):
                                    dst_mac.append(int(mac,16))
                                winpcapy.dst_mac[1] = dst_mac
                                flag[1] = 1
            if flag.count(0)==2:self.tn = 0             
  
    def close(self,force=1):
        if self.tn:
           winpcapy.close(self.tn) 
    
    def getValue(self,rev):
        buf = ""
        for i in range(14,rev[0].contents.len-14):
            if rev[1][i]==0x00:break
            buf += chr(rev[1][i]) 
        return buf
    
    def set(self,value):
        if self.tn == None:
            self.init()
        if self.tn == 0:
            print self.LOST_CONNECT
            return 0
        if self.log&1:
            print "[SET]:",value
        try:
            if 'CCU' not in self.port[1].strip():
                value += self.cr
            r = self._set(value)
        except:
            self.tn = 0
            print self.LOST_CONNECT
            return 0
        return r
    
    def _get(self):
        buf = ""
        while 1:
            rev = winpcapy.Recived(self.tn)        
            if winpcapy.dst_mac[self.port[0]] == rev[1][6:12]:
               buf = self.getValue(rev)
            if self.port[1] in buf:
               buf = buf.split(self.port[1].strip()+'\t')[-1]
               return buf 
                      
    def _set(self,value):
        value = self.port[1].strip()+'\t'+value
        winpcapy.sendto(self.tn,value,self.port[0]) 
        return len(value)

class Popen(subprocess.Popen):
    #def send_recv(self, input='', maxsize=None):
    #    return self.send(input), self.recv(maxsize), self.recv_err(maxsize)

    def _close(self, which):
        getattr(self, which).close()
        setattr(self, which, None)

    def send(self, data):
        if not self.stdin:
            return None
        try:
            x = msvcrt.get_osfhandle(self.stdin.fileno())
            (errCode, written) = WriteFile(x, data)
        except ValueError:
            return self._close('stdin')
        except (subprocess.pywintypes.error, Exception), why:
            if why[0] in (109, ESHUTDOWN):
                return self._close('stdin')
            print "Error: Shell no stdin"
        return written

    def _recv(self, which, maxsize = 32768):
        conn = getattr(self, which)
        if conn is None:
            return None
        try:
            x = msvcrt.get_osfhandle(conn.fileno())
            (read, nAvail, nMessage) = PeekNamedPipe(x, 0)
            if maxsize < nAvail:
                nAvail = maxsize
            if nAvail > 0:
                (errCode, read) = ReadFile(x, nAvail, None)
        except ValueError:
            return self._close(which)
        except (subprocess.pywintypes.error, Exception), why:
            if why[0] in (109, ESHUTDOWN):
                return self._close(which)
            print "Error: Shell no stdout"
        if self.universal_newlines:
            read = self._translate_newlines(read)
        return read

    def recv(self):
        return self._recv('stdout') + self._recv('stderr') 



class Shell(Terminal):
    def __init__(self,cmd,port=""):
        Terminal.__init__(self,cmd,port)
        self.cr = "\n"   # default Carriage Return

    def _init(self):
        self.close()
        self.tn = Popen(self.host, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #self.tn.read_very_eager = self.tn.recv
        #self.tn.write = self.tn.send

    def _get(self):
        return self.tn.recv()

    def _set(self,value):
        return self.tn.send(value)

    def _close(self):
        handle = win32api.OpenProcess(1, 0, self.tn.pid)
        self.tn._close("stdin")
        self.tn._close("stdout")
        self.tn._close("stderr")
        try:
            win32api.TerminateProcess(handle, 0)
            #print "Terminate",self.host
        except:
            print self.host,"Terminated"
            time.sleep(0.1)



class RedirectStdout(object):
    def __init__(self,fileobj=None):
        if not fileobj:
            self.fileobj = open(DEFAULT_LOG_FILE,"a")
            sys.stdout = self
        elif type(fileobj) == type(sys.stdout):
            self.fileobj = fileobj
            sys.stdout = self

    def write(self,s):
        backup_sys_stdout.write(s)
        self.fileobj.write(s)

    def close(self):
        if not self.fileobj.closed:
            sys.stdout = backup_sys_stdout
            self.fileobj.close()

    def __del__(self):
        self.close()


"""
class Snmp(Controller):
    execPath = ""
    NOT_INSTALL = "Error: No Net-SNMP Install"
    def __init__(self, host , oid = "sysDescr.0", mib = 'ALL', community = 'private', unit = ""):
        if not Snmp.execPath:
            x = _winreg.ConnectRegistry(None,_winreg.HKEY_LOCAL_MACHINE)
            y = _winreg.OpenKey(x, r"Software\Net-SNMP",0,_winreg.KEY_ALL_ACCESS)
            p = _winreg.QueryValueEx(y,"InstallDir")
            _winreg.CloseKey(y)
            _winreg.CloseKey(x)
            if os.path.isfile(os.path.join(p[0],"bin/snmpget.exe")):
                Snmp.execPath = os.path.join(p[0],"bin")
            else:
                print Snmp.NOT_INSTALL
                self.status = None
                return False
        self.status = 1
        self.log = DEFAULT_LOG
        self.host = host
        self.community = community
        self.mibfile = mib
        self.mibobj = oid
        self.unit = unit

    def getValue(self,data):
        r = re.compile(".*= (.*?): (.*)")
        m = r.match(data)
        if m:
            u, value = m.groups()
            if not self.unit:
                u = u.upper()
                if "IPADDR" == u:
                    self.unit = "a"
                elif u in ("INTEGER","TIMETICKS","BITS"):
                    self.unit = "i"
                else:
                    self.unit = "s"
                    return value        
            r = re.compile(".*\((.*)\)")
            m = r.match(value)
            if m:
                value = m.group(1)
            return value
        return None

    def isConnect(self):
        if self.status == None:
            print Snmp.NOT_INSTALL
            return ""
        data = os.popen(Snmp.execPath+"/snmpget -O 0 -r 1 -t 2 -c %s -v 2c %s sysUpTime.0"%\
                        (self.community,self.host)).read()
        data = data[:-1]
        return self.getValue(data)

    def get(self, mibobj=""):
        if self.status == None:
            print Snmp.NOT_INSTALL
            return ""
        if mibobj:
            if self.mibobj != mibobj:
                self.unit = ""
            self.mibobj = mibobj
        data = os.popen(Snmp.execPath+"/snmpget -m %s -O 0 -r 1 -t 3 -c %s -v 2c %s %s"%\
                        (self.mibfile,self.community,self.host,self.mibobj)).read()
        data = data[:-1]
        if self.log&2:
            print "[SNMPGET]:",data
        v = self.getValue(data)
        if not v:
            print "Error: Can't get SNMP MIBObject:", self.mibobj
            v = ""
        return v

    def set(self,value,unit=""):
        if self.status == None:
            print Snmp.NOT_INSTALL
            return ""
        if self.log&1:
            print "[SNMPSET]:",value
        if unit:
            self.unit = unit
        if not self.unit:
            if not self.get():
                return None

        if self.unit == "s" : value='"'+value+'"'
        data = os.popen(Snmp.execPath+'/snmpset -r 1 -m %s -c %s -v 2c %s %s %s %s'%\
                       (self.mibfile,self.community,self.host,self.mibobj,self.unit,value)).read()
        if self.log&1:
            print "[SNMPSET Response]:",data
        return data

    def setWait(self,value,expect,timeout,unit=""):
        if self.status == None:
            print Snmp.NOT_INSTALL
            return ""
        if value != None:
            self.set(value,unit)
        timeout = time.time()+0.1
        while time.time() < timeout:
            result = self.get()
            if str(expect) == result:
                break
        return result

    def walkTable(self, mibobj=""):
        if self.status == None:
            print Snmp.NOT_INSTALL
            return ""
        if mibobj:
            self.mibobj = mibobj
        data = os.popen(Snmp.execPath+"/snmpwalk -m %s -O 0 -r 1 -t 3 -c %s -v 2c %s %s"%\
                        (self.mibfile,self.community,self.host,self.mibobj)).read()
        data = data[:-1].splitlines()
        if self.log&2:
            print "[SNMPWALK]:",data

        r = re.compile(".*?(\d+) = (.*?): (.*)")
        rv = re.compile(".*\((.*)\)")
        a = {}
        for l in data:
            m = r.match(l)
            if m:
                i, u, value = m.groups()
                if u.upper() in ("INTEGER","TIMETICKS","BITS"):
                    m = rv.match(value)
                    if m:
                        value = m.group(1)
                a[int(i)] = value
        return a
"""


import operator
from UserDict import UserDict

class Multicast(UserDict):
    "Class multiplexes messages to registered objects"
    def __init__(self, objs=[]):
        UserDict.__init__(self)
        for alias, obj in objs: self.data[alias] = obj

    def __call__(self, *args, **kwargs):
        "Invoke method attributes and return results through another Multicast"
        return self.__class__( [ (alias, obj(*args, **kwargs) ) for alias, obj in self.data.items() ] )

    def __nonzero__(self):
        "A Multicast is logically true if all delegate attributes are logically true"
        return operator.truth(reduce(lambda a, b: a and b, self.data.values(), 1))

    def __getattr__(self, name):
        "Wrap requested attributes for further processing"
        return self.__class__( [ (alias, getattr(obj, name) ) for alias, obj in self.data.items() ] )

    def __setattr__(self, name, value):
        if name == "data":
            self.__dict__[name]=value
            return
        for object in self.values():
            setattr(object, name, value)



class MulticastConcurrent(Multicast):
    "Class MulticastConcurrent messages to registered objects running concurrently"
    def __init__(self, objs=[]):
        Multicast.__init__(self,objs)

    def __call__(self, *args, **kwargs):
        import threading
        lock = threading.RLock()
        result = {}

        def invoke(alias, object):
            value = object(*args, **kwargs)
            lock.acquire()
            result[alias] = value
            lock.release()

        threadlist = [threading.Thread(
                      target=invoke, args=item)
                      for item in self.items()]
        for thread in threadlist:
            thread.start()
        for thread in threadlist:
            thread.join()
        return result


def main():
    term = ssh('192.168.1.1', 'root')
    if term: print 'connection'
    term << '\n'
    r = term.wait('#',5) 
    print r
    term << 'ps'
    data=term.get()
    print data
    term << 'pmf --report'
    data=term.get()    
    print data


if __name__ == '__main__':
    main()
