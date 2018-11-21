#! /bin/sh


apdown

cfg -a AP_STARTMODE=dual
cfg -a AP_MODE=sta-wds
cfg -a AP_MODE_2=wds
cfg -a AP_CHMODE=11GHT40MINUS
cfg -a AP_SSID=Hitron_ATH_2G
cfg -a AP_SSID_2=Hitron_ATH_5G__
cfg -a AP_SECMODE=None
cfg -a AP_SECMODE_2=None
apup

ifconfig eth0 192.168.0.22
ifconfig ath0 192.168.1.22


