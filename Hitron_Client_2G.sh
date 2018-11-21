#!/bin/bash
ifconfig apcli0 down
ifconfig apcli0 up
iwpriv apcli0 set ApCliEnable=0
iwpriv apcli0 set ApCliAuthMode=OPEN 
iwpriv apcli0 set ApCliEncrypType=NONE 
iwpriv apcli0 set ApCliSsid=Hitron_2G
iwpriv apcli0 set ApCliEnable=1
