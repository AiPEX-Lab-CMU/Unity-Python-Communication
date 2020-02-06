# Unity-Python-Communication
Contains the newest version of the Python Communication components

The first time before starting the simulation:
1. Run setup.py (python setup.py), this will install the required packages for the python component.

To start the simulation:
1. Run server.py, to enable printing out the receipts during data collection, option verbose is required (-v or --verbose).
2. Run the executable and click "start simulation".
3. If the verbose is enabled, you'll see the receipts popping out when the customers checkout.
4. The python side is blocked during the simulation process, after the simulation ends the python side will continue executing.

** Always make sure that the python side is running during the simulation or the simulation will get stuck (the same applies to the python side, it will be blocked until an instance of simulation has terminated).
