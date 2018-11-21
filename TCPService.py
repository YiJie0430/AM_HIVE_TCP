import threading,socket

class TCPService(threading.Thread):
      def __init__(self,parent):
          threading.Thread.__init__(self)
          self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # s = socket.socket()
          self.server.bind(("",2398))
          self.server.listen(5)
          self.buf = ''
          self.parent = parent
          self.ss = None
          
      def run(self):
          self.ss, addr = self.server.accept()
          while self.parent.running:
                self.buf = self.ss.recv(1024).strip()
                self.parent.SendMessage(self.buf)
                if "7004 ERROR Can't open file " in self.buf:
                   break 
                            
      def set(self,val):
          if self.ss:
             self.ss.send("%s\n"%val)
             return len(val)
          
      def close(self):
          self.server.close()
          self.ss.close()
      
      def __del__(self):
          self.close()
      



