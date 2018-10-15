# -*- coding: utf8 -*-

import os,sys, subprocess
#import commands
import re

def nicinfo():
    cmd = "ifconfig -a"
    raw_data = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.read().decode().split("\n")
    os_cmd = "cat /etc/redhat-release |head -1|awk '{print $1}'"
    os_data = subprocess.Popen(os_cmd, stdout=subprocess.PIPE, shell=True).stdout.read().decode().split()
    raw_nic_list = []
    temp_nic_list = []
    if os_data[0] == "CentOS":
        for line in raw_data:
            if "flags=" in line:
                if temp_nic_list:
                    raw_nic_list.append(temp_nic_list)
                    temp_nic_list = []
                temp_nic_list.append(line.strip())
            else:
                temp_nic_list.append(line.strip())
        raw_nic_list.append(temp_nic_list)
        nic_list = {}
        nic_dic = {}
        for nic_item in raw_nic_list:
            nic_dic = {}
            for info_line in nic_item:
                if "flags=" in info_line:
                    nic_name = info_line.split(":")[0]
                if "inet" in info_line and "netmask" in info_line and "broadcast" in info_line:
                    nic_ip = info_line.split()[1]
                    nic_network = info_line.split()[-1]
                    nic_netmask = info_line.split()[3]
                if info_line.startswith("ether"):
                    nic_mac = info_line.split()[1]
            p = r'eth(\d*)'
            if re.match(p, nic_name):
                nic_dic["name"] = nic_name
                nic_dic["macaddress"] = nic_mac
                nic_dic["network"] = nic_network
                nic_dic["netmask"] = nic_netmask
                nic_dic["bonding"] = 0
                nic_dic["model"] = 'unknown'
                nic_dic["ipaddress"] = nic_ip

                nic_list['name'] = nic_dic['name']
                nic_list['macaddress'] = nic_dic['macaddress']
                nic_list['network'] = nic_dic['network']
                nic_list['netmask'] = nic_dic['netmask']
                nic_list['bonding'] = "0"
                nic_list['model'] = "model"
                nic_list['ipaddress'] = nic_dic['ipaddress']
        print(nic_list)
        return nic_list

nicinfo()