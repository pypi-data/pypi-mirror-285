# pynovnc

<a href="https://colab.research.google.com/drive/1SMHc4PmG9AjnotQD6R5KQQfL7dNvvyE0" style="background-color: #007bff; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block;width:100%;text-align:center;font-weight:900;font-size:30">Colab</a>

## Install Requiements  : 
```bash 
apt install -y --fix-missing xserver-xephyr  x11vnc xvfb novnc  net-tools x11-apps x11-xkb-utils gedit tightvncserver x11-utils gnumeric
```

## Installation : 
```bash
pip install pynovnc 
```

## Quick start : 
```python
from pynovnc import VirtualDisplay
with  VirtualDisplay(h = 1040 , w = 1920 ) as x :
    app = x.run(["gedit"])
    port = x.vncport
    app.wait()
```

