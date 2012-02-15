#!/usr/bin/env python
#encoding:utf-8

#Author: Matt Chen
#Last Modify: 2012-2-13

'''In order to run the script, you must install Python,the pywin32 extensions
and the WMI Python module.
'''
import psutil,wmi,os
from time import localtime,strftime

def get_diskio_info():
    '''This function will get the Disk I/O performance data,focused on
    DiskReadBytesPerSec,DisWriteBytesPerSec and CurrentDiskQueueLength.
    '''
    c=wmi.WMI()
    wql="SELECT * FROM Win32_PerfFormattedData_perfDisk_LogicalDisk where name='_total'"
    M=1024*1024
    ioInfo=[]
    for diskio in c.query(wql):
        data=[int(diskio.DiskReadBytesPerSec)/M,int(diskio.DiskWriteBytesPerSec)/M,int(diskio.CurrentDiskQueueLength)/M]
        ioInfo.append(data)
    return ioInfo

def performance_factors():
    '''This function will get all the performance foctors ,include CPU
    percent,Memory percent and Disk I/O data.
    '''
    utilization_factor=[]
    for x in range(12):
        timestamp=strftime('%H:%M:%S',localtime())
        cpu_percent=psutil.cpu_percent(interval=5)
        mem_percent=psutil.phymem_usage().percent
        utilization_factor.append([timestamp,cpu_percent,mem_percent,get_diskio_info(),get_process_info()])
    return utilization_factor

def get_process_info():
    c=wmi.WMI()
    pids=[]
    process_info=[]
    for process in c.Win32_Process(name="QQ.exe"):
        pids.append(process.ProcessId)
    if pids:
        for pid in pids:
            p=psutil.Process(pid)
            data={}
            data['name']=p.name
            data['cpu_percent']=p.get_cpu_percent(interval=0)
            data['memory_percent']=round(p.get_memory_percent(),2)
            process_info.append(data)
    return process_info
        
def main():
    '''This function will write the performance factor data into a log file
    every minute.
    '''
    path=os.path.join(os.path.dirname(__file__),'performance_factor.log')
    file=open(path,'a+')
    file.write("Time: CPU Percent Memory Percent  Disk I/O "+'\n')
    while True:
        factor=performance_factors()
        for x in range(len(factor)):
            timestamp=str(factor[x][0])
            cpu_percent=str(factor[x][1])
            mem_percent=str(factor[x][2])
            diskio_data=str(factor[x][3][0])
            process_data=factor[x][4][0]
            data="%8s  %5s  %5s  %12s  %s %s %s" %(timestamp,cpu_percent,mem_percent,diskio_data,str(process_data['name']),str(process_data['cpu_percent']),str(process_data['memory_percent']))
            file.write(data+'\n')
        file.flush()
    file.close

if __name__=='__main__':
    main()

