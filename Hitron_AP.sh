#!/bin/bash
killall -q htx_lan
iwpriv apcli0 set ApCliEnable=0
iwpriv apclii0 set ApCliEnable=0
iwpriv ra0 set IEEE8021X=0
iwpriv ra0 set AuthMode=OPEN
iwpriv ra0 set EncrypType=NONE
iwpriv ra0 set Channel=6
iwpriv ra0 set SSID=Hitron_2G
iwpriv rai0 set IEEE8021X=0
iwpriv rai0 set HtBw=1
iwpriv rai0 set VhtBw=0
iwpriv rai0 set AuthMode=OPEN
iwpriv rai0 set EncrypType=NONE
iwpriv rai0 set Channel=36
iwpriv rai0 set SSID=Hitron_5G
