import subprocess , os , json , time , portpicker , threading

class X11vnc(threading.Thread):
    def __init__(self, rfbport , options ):
        super().__init__()
        self.rfbport = rfbport
        self.cmd = ["x11vnc" , "-rfbport", f"{self.rfbport}"]  + options
        self.pid = subprocess.Popen(self.cmd)
        print(f">_$ X11vnc  {self.pid.pid } started ")


    def kill(self) :
        self.pid.kill()
        print(f">_$ X11vnc  {self.pid.pid } killed ")

class Novnc(threading.Thread):
    def __init__(self, rfbport , vncport ):
        super().__init__()
        self.rfbport = rfbport
        self.vncport = vncport
        self.cmd = ["/usr/bin/novnc" ,"--vnc" ,  f"localhost:{self.rfbport}" ,  "--listen" ,  f"{self.vncport}"]
        self.pid = subprocess.Popen(self.cmd)
        print(f">_$ Novnc started on port {self.vncport }")



    def kill(self) :
        self.pid.kill()
        print(f">_$ Novnc  {self.pid.pid } killed ")

class Application(threading.Thread):
    def __init__(self, args , **kwags ):
        super().__init__()
        self.cmd = args
        self.name = args[0]
        self.process = subprocess.Popen(self.cmd , **kwags)
        print(f">_$ Application started {self.name } :\n\t{' '.join(self.cmd) }")
        self.pid = self.process.pid

    def wait(self) :
        self.process.wait()


    def kill(self) :
        self.process.kill()
        print(f">_$ Application  {self.name } killed ")

class VirtualDisplay :
    def __init__(self,port= 0 , w = 1280 , h  = 1080,dp = 24 , vncport = None , rfbport = None ) :
        self.id , self.w , self.h , self.dp = port , w , h , dp
        self.x11vnc_options =  [
                "-quiet",
                "-cursor",
                "-localhost",
                "-nopw",
                "-forever",
                "-shared",
                "-enablehttpproxy" ,
                "--multiptr"
                ]
        self.rfbport = rfbport if vncport is not None else portpicker.pick_unused_port() 
        self.vncport = vncport if vncport is not None else portpicker.pick_unused_port()
        self.app = None

    def start(self) :
        print(f">_$ Virtual Display {self.id} opened ")
        self.xvfb  = subprocess.Popen(["Xvfb", f":{self.id}", f"-screen", f"0", f"{self.w}x{self.h}x{self.dp}"])
        time.sleep(1)
        self.x11vnc = X11vnc(self.rfbport , options = self.x11vnc_options)
        time.sleep(1)
        self.novnc = Novnc(self.rfbport ,self.vncport )


    def run(self, args , **kwargs) :
        if not ("env" in kwargs) : kwargs["env"] = dict()
        kwargs["env"]["DISPLAY"] = f":{self.id}"
        self.app = Application(args, **kwargs)
        return self.app


    def close(self) :
        self.novnc.kill()
        self.x11vnc.kill()
        self.xvfb.kill()
        print(f">_$ Virtual Display {self.id} closed ")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
