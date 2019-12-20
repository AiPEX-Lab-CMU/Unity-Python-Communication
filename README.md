# Unity-Python-Communication
Contains the newest version of the Python Communication components

How to use:
Install the 2 .dll files (in vscode that is Project->Add Reference->Choose the 2 files and click ok
When want to send something, call SendMessage.sendBytes(), 1st argument is data type and 2nd argument is the file position of the stored data
Required packages for python(can be done via pip install):
1. time
2. zmq
3. numpy
4. scipy
5. io
6. os
7. stl
8. matplotlib
9. Pillow
10. datetime

When actually running:
1. Run server.py
2. Directly start the unity side and it will start sending messages when the function SendMessage.sendBytes() is called
3. When the unity side exits the python side will exit too
