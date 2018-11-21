import os,sys,time
execfile("config.ini")

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

def lWaitCmdTerm(term,cmd,waitstr,sec,count=1):
    for i in range(count):
        data=list()
        term << cmd
        data = term.wait(waitstr,sec); #raw_input(data[-1])
        if "help" in data[-1]: raise Except("wifi interface down")        
        if "ttyS" in data[-1]:
            time.sleep(2)
            term<<""
            term.get()            
            #data = term.wait("%s"%promp,sec) 
            term << "%s"%cmd
            data = term.wait("%s"%waitstr,sec)
            #print data[-1]
        data=data[-1].split(cmd)[-1].split(waitstr)[0].strip()
        return data
    raise Except("failed: %s,%s"%(cmd,data))


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

    def GetMfgRecord(self,term):
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