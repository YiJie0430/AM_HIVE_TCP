#!/bin/sh
ifconfig apcli0 down
ifconfig apclii0 down
ifconfig apcli0 up
ifconfig apclii0 up
iwpriv apcli0 set ApCliEnable=0
iwpriv apclii0 set ApCliEnable=0
iwpriv apclii0 set HtBw=1
iwpriv apclii0 set VhtBw=0
iwpriv apclii0 set ApCliAuthMode=OPEN
iwpriv apclii0 set ApCliEncrypType=NONE
iwpriv apclii0 set ApCliSsid=Hitron_5G
iwpriv apclii0 set ApCliEnable=1