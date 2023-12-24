#USB3.2 to 16xUSB2.0 bridge IP Verification Project.

Problem Defenition
> Insert Text here for the problem defenition

Folder structre inside the source
- rtl
    - Contains all the RTL and Design related files
- verif
    - scoreboard
        - Contains the scoreboard and coverage releated files needed for the checker and 
        data verification part for the IP.
    - sequence
        - Has the sequences that should be extended from the uvc's sequence class for having more customizatation 
        on the testcases.
    - testbench
        - Contains the main testbench top file where the port connections are made and also contains the environment & 
        vsequencer files.
    - testcases
        - Contains the various number of testcases which is needed and creation of the appropriate sequences
    - usb_uvc
        - Contains the uvc files that will drive the signals and talk with the DUT
        usb_driver
            - Contains the driver related code and manages the protocol
        usb_monitor
            - Contains the uvc monitor related files
        usb_scoreboard
            - Contains asertion related stuff that is used to monitor the USB protocol connect to the usb_monitor
            - monitors the protocol violation and keeps track of the outgoing and incoming transactions
