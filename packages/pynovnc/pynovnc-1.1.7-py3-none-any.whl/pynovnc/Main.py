import sys 
from pynovnc import VirtualDisplay

def main():
    with  VirtualDisplay(h = 1040 , w = 1920 ) as x :
        app = x.run(sys.argv[1:])
        port = x.vncport
        print("run app : " , " ".join(sys.argv[1:]))
        print(f"* Open url ;\n\thttp:0.0.0.0:{x.vncport}")

        app.wait()
if __name__ == "__main__":
    
    main()
