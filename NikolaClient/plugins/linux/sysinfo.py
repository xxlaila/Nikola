# -*- coding: utf8 -*-

import os,sys, subprocess
#import commands
import re

def collect():
    filter_keys = ['Manufacturer', 'Serial Number', 'Product Name', 'UUID', 'Wake-up Type', 'Version', 'Family']
    raw_data = {}
    data = {}
 #   filter_keys = ['Manufacturer', 'Serial Number', 'Product Name', 'UUID', 'Wake-up Type']
    for key in filter_keys:
        try:
            cmd_result = subprocess.Popen("sudo dmidecode -t system|grep '%s'" % key, stdout=subprocess.PIPE,
                                          shell=True).stdout.read()
            cmd_result = cmd_result.decode().strip()
            raw_data[key] = cmd_result.split(':')[1].strip() if cmd_result.split(':')[1] else -1
        except Exception as e:
            print(e)
            raw_data[key] = -2
    data['asset_type'] = 'server'
    data['manufactory'] = raw_data['Manufacturer']
    data['sn'] = raw_data['Serial Number']
    data['model'] = raw_data['Product Name']
    data['uuid'] = raw_data['UUID']
    data['wake_up_type'] = raw_data['Wake-up Type']
    data['family'] = raw_data['Family']
    data['version'] = raw_data['Version']

    data.update(cpuinfo())
    data.update(diskinfo())
    data.update(osinfo())
    data.update(hosts())
    data.update(raminfo())
    data.update(nicinfo())
    #print(data)
    return data

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
                nic_list.append(nic_dic)
                nic_list['name'] = nic_dic['name']
                nic_list['macaddress'] = nic_dic['macaddress']
                nic_list['network'] = nic_dic['network']
                nic_list['netmask'] = nic_dic['netmask']
                nic_list['bonding'] = "0"
                nic_list['model'] = "model"
                nic_list['ipaddress'] = nic_dic['ipaddress']
        #print(nic_list)
        return nic_list
    elif os_data[0] == "Red":
        for line in raw_data:
            if "HWaddr" in line:
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
                if "HWaddr" in info_line:
                    nic_name = info_line.split()[0]
                    nic_mac = info_line.split()[4]
                if "inet addr" in info_line and "Mask" in info_line and "Bcast" in info_line:
                    nic_ip = info_line.split(":")[1].split()[0]
                    nic_netmask = info_line.split(":")[3]
                    nic_network = info_line.split(":")[2]
            p = r'eth(\d*)'
            if re.match(p, nic_name):
                nic_dic["name"] = nic_name
                nic_dic["macaddress"] = nic_mac
                nic_dic["network"] = nic_network
                nic_dic["netmask"] = nic_netmask
                nic_dic["bonding"] = 0
                nic_dic["model"] = 'unknown'
                nic_dic["ipaddress"] = nic_ip

                nic_list.append(nic_dic)
                nic_list['name'] = nic_dic['name']
                nic_list['macaddress'] = nic_dic['macaddress']
                nic_list['network'] = nic_dic['network']
                nic_list['netmask'] = nic_dic['netmask']
                nic_list['bonding'] = "0"
                nic_list['model'] = "model"
                nic_list['ipaddress'] = nic_dic['ipaddress']
        # print(nic_list)
        return nic_list

def raminfo():
    '''监控red hat 和 centos系统'''
    cmd = "sudo dmidecode -t 17"
    raw_data_list = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.read().decode().split("\n")
    raw_data_list = raw_data_list[4:]  # 删除dmidecode开头3行
    raw_ram_list = []
    temp_raw_item = []
    for line in raw_data_list:
        if line.strip().startswith("Memory Device"):
            if temp_raw_item:
                raw_ram_list.append(temp_raw_item)
                temp_raw_item = []
        else:
            temp_raw_item.append(line.strip())
    temp_raw_item.append(temp_raw_item)  # 最后一个插槽的信息补上
    ram_list = []
    for ram_item in raw_ram_list:
        ram_item_size = 0
        ram_item_to_dic = {}
        for i in ram_item:
            data_list = i.split(':')
            if len(data_list) == 2:
                k, v = data_list
                if k == 'Size':
                    if v.strip() != "No Module Installed":
                        ram_item_to_dic['capacity'] = v.strip().split()[0]
                        ram_item_size = v.strip().split()[0]
                    else:
                        ram_item_to_dic['capacity'] = 0
                if k == 'Type':
                    ram_item_to_dic['model'] = v.strip()
                if k == 'Manufacturer':
                    ram_item_to_dic['manufactory'] = v.strip()
                if k == 'Serial Number':
                    ram_item_to_dic['sn'] = v.strip()
                if k == 'Asset Tag':
                    ram_item_to_dic['asset_tag'] = v.strip()
                if k == 'Locator':
                    ram_item_to_dic['slot'] = v.strip()
        if ram_item_size == 0:  # 大小为0， 空插槽，汇报
            pass
        else:
            ram_list.append(ram_item_to_dic)
    ram_size_cmd = "cat /proc/meminfo|grep MemTotal"
    ram_total_size = \
        subprocess.Popen(ram_size_cmd, stdout=subprocess.PIPE, shell=True).stdout.read().decode().split(":")[1].strip()
    ram_total_mb_size = int(ram_total_size.split()[0]) / 1024
    ram_data = {'ram': ram_list,
                'ram_size': ram_total_mb_size}
    #print(ram_data)
    return ram_data

def hosts():
    host = subprocess.check_output("hostname |head -1|awk '{print $1}'", shell=True).decode().strip()
    data = {
        "host_name": host.split()[0],
    }
    # print(data_host)
    return data

def hosts():
    host = subprocess.check_output("hostname |head -1|awk '{print $1}'", shell=True).decode().strip()
    data_host = {
        "host_name": host.split()[0],
    }
    # print(data_host)
    return data_host

def osinfo():
    '''现在用的是centos 7.3/4，没有lsb_release命令，故采用查看系统文件方式来提取'''
    distributor = subprocess.check_output("cat /etc/redhat-release |head -1|awk '{print $1}'",shell=True).decode().strip()
    #distributor = commands.getoutput(" lsb_release -a|grep 'Distributor ID'").split(":")
    release  = subprocess.check_output("cat /etc/redhat-release |head -1 |awk '{print $(NF-1)}'",shell=True).decode().split()
    #release = commands.getoutput(" lsb_release -a|grep Description").split(":")
    data = {
        "os_distribution": distributor.split()[0],
        "os_release": release[0].strip(),
        "os_type": "Linux",
    }
    # print(data_dic)
    return data


def cpuinfo():
    base_cmd = "cat /proc/cpuinfo"
    raw_cmd = {
        'cpu_model': "%s | grep 'model name' | head -1 | awk -F: '{print $2}'" % base_cmd,
        'cpu_count': "%s | grep 'processor' | wc -l" % base_cmd,
        'cpu_core_count': "%s | grep 'cpu cores' | awk -F: '{SUM+=$2} END {print SUM}'" % base_cmd,
    }
    '''Red Hat和centos 系统有点区别，这里先判断操作系统的版本，然后在进行cpu的提取'''
    os_cmd = "cat /etc/redhat-release |head -1|awk '{print $1}'"
    os_data = subprocess.Popen(os_cmd, stdout=subprocess.PIPE, shell=True).stdout.read().decode().split()
    '''先判断是否是Red Hat操作系统'''
    if os_data[0] == "Red":
        raw_data = {}
        for k, cmd in raw_data.items():
            try:
                cmd_res = subprocess.check_output(cmd, shell=True)
                # cmd_res = commands.getoutput(cmd)
                raw_data[k] = cmd_res.strip()

            # except Exception,e:
            except ValueError as e:
                print(e)

        data = {
            "cpu_model": raw_data["cpu_model"].strip(),
            "cpu_count": raw_data["cpu_count"],
            "cpu_core_count": raw_data["cpu_core_count"],
        }
        cpu_model = raw_data["cpu_model"].strip()
        if len(cpu_model) > 1:
            data["cpu_model"] = cpu_model[1].strip()
        else:
            data["cpu_model"] = -1

        #print(data)
        return data

    else:
        raw_data = {}
        for k, v in raw_cmd.items():
            try:
                cmd_result = subprocess.Popen(v, stdout=subprocess.PIPE, shell=True).stdout.read().decode().strip()
                raw_data[k] = cmd_result
            except ValueError as e:
                print(e)
                raw_data[k] = -1

        data = {
            "cpu_model": raw_data["cpu_model"].strip(),
            "cpu_count": raw_data["cpu_count"],
            "cpu_core_count": raw_data["cpu_core_count"],
        }
        #print(data)
        return data

def diskinfo():
    cmd = "lsblk"
    cmd_result = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.read().decode().strip().split("\n")
    disk_list = []
    uuid_result = subprocess.Popen("sudo dmidecode -t system|grep 'UUID'|awk -F: '{print $2}'", stdout=subprocess.PIPE,
                                  shell=True).stdout.read().decode().strip()
    for line in cmd_result:
        if re.match(r'[a-z]d[a-z]', line):
            diskname = line.split()[0]
            disksize = line.split()[3]
            disk_data = {
                'uuid': uuid_result + '-' + diskname,
                'diskname': diskname,
                'disksize': disksize,
            }
    #print (disk_list)
    return disk_data
