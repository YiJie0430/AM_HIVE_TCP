import os,sys,time
from toolslib import *
execfile("config.ini")

class R_Flow:
    def __init__(self,term,record=None):
        self.term=term
        self.record=record

    def CrtMfgRecord(self,term,default):
        self.term << 'echo %s > %s'%(''.join(default),mfg_rcd)
        return default

    def SetMfgRecord(self,term,record,index,toogle=1):
        record[index]=str(toogle)
        record_str=''.join(record); #raw_input(record_str)
        self.term << 'echo %s > %s'%(record_str,mfg_rcd)

    def _GetMfgRecord(self,term):
        for try_ in xrange(3):
            try:
              data=lWaitCmdTerm(self.term,"tail -n 1 %s"%mfg_rcd,promp,3)
              if 'No such file or directory' in data: return self.CrtMfgRecord(self.term,['0' for n in xrange(len(test_item)+1)])
              data=data.split(mfg_rcd)[-1].split(promp)[0].strip()
              if int(data[-1])>=2 or '0' not in data[0:-1]: 
                self.term<<'rm %s && find /nvram/ -name "*mfgsubrcd*" -delete'%mfg_rcd
                return self.CrtMfgRecord(self.term,['0' for n in xrange(len(test_item)+1)])
              value=list(data)
              value[-1]=str(int(value[-1])+1)
              self.SetMfgRecord(self.term,value,-1,value[-1])
              return value
            except: continue
        raise Except('Fail:GetMfgRecord')


    def GetMfgRecord(self,term):
        for try_ in xrange(3):
            try:
              data=lWaitCmdTerm(self.term,"tail -n 1 %s"%mfg_rcd,promp,3)
              if 'No such file or directory' in data: return self.CrtMfgRecord(self.term,['0' for n in xrange(len(test_item)+1)])
              data=data.split(mfg_rcd)[-1].split('root')[0].strip()
              #data=data.split(self.promp)[0].strip()             
              value=list(data)
              value[-1]=str(int(value[-1])+1)
              self.SetMfgRecord(self.term,value,-1,value[-1])
              if int(value[-1])>2 or int(value[-2])==1: 
                self.term<<'rm %s && find /nvram/ -name "*mfgsubrcd*" -delete'%mfg_rcd
                return self.CrtMfgRecord(self.term,['0' for n in xrange(len(test_item)+1)])
              else: return value
            except: continue
        raise Except('Fail:GetMfgRecord')

    def ChkMfgRecord(self,record,index):
        return int(record[index])

    def SaveRcdLog(self,term,rcd):   
        if not rcd: rcd='None'
        rcd_str=''.join(rcd)
        self.term << 'echo %s >> %s'%(rcd_str,mfg_rcd_log)

    def CrtSubRcd(self,term,default_toogle,item):
        self.term << 'echo "%s" > %s_%s'%(default_toogle,mfg_sub_rcd,item)
        toogle_rcd=default_toogle.copy()
        return toogle_rcd

    def SetSubRcd(self,term,record_toogle,item,sub_item,toogle=0):
        record_toogle[sub_item]=toogle
        self.term << 'echo "%s" > %s_%s'%(record_toogle,mfg_sub_rcd,item)

    def GetSubRcd(self,term,item):
        for try_ in xrange(3):
            try:
              data=lWaitCmdTerm(self.term,"tail -n 1 %s_%s"%(mfg_sub_rcd,item),'#',3)
              if 'No such file or directory' in data: 
                 return eval('self.CrtSubRcd(self.term,sub_item_toogle_%s,item)'%item)
              data=eval(data.split('%s_%s'%(mfg_sub_rcd,item))[-1].split('root')[0].strip())
              return data
            except: continue
        raise Except('Fail: GetWifiSubRecord')

class Item_log(dict):
    def __init__(self):
        self=dict()

    def add(self,key):
        self[key]=list()
        
    def insert(self,key,value=str()):
        self[key].append(value)
        
    def desroy(self):
        self=dict()

class Encryption:
    def __init__(self,term):
        self.term=term
    
    def encrypt(self,folder):
        try:
          lWaitCmdTerm(self.term,"openssl enc -aes-256-ecb -in %s -out %s.encrypted"%(folder,folder),'password:',3)
        except:
          raise Except('Fail: Read file')
        else:
          lWaitCmdTerm(self.term,"taiwanno1",'password:',3)
          data=lWaitCmdTerm(self.term,"taiwanno1",'#',3); print data
          if 'failure' in data: raise Except('Fail:%s'%data)
          else: 
            data=lWaitCmdTerm(self.term,"rm %s && find /nvram -name AFIlog"%(folder),'#',3); print data
            if folder in data: raise Except('Fail:%s'%data)

    def decrypt(self,folder):
        try:
          lWaitCmdTerm(self.term,"openssl enc -aes-256-ecb -d -in %s.encrypted -out %s"%(folder,folder),'password:',3)
        except:
          raise Except('Fail: Read file')
        else:
          data=lWaitCmdTerm(self.term,"taiwanno1",'#',3); print data
          if 'bad decrypt' in data: raise Except('Fail:%s'%data)
