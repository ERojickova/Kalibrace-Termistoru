import os
import glob
import time
import numpy as np

#nezapomenout pustit pomoci suda
#os.system("modprobe w1-gpio")
#os.system("modprobe w1-therm")

base_dir = '/sys/bus/w1/devices'
#device_path = glob.glob(base_dir + '28*')[0]
device_path = glob.glob(os.path.join(base_dir,'28*'))[0]
def read_temperature_raw():
    with open(os.path.join(device_path, 'w1_slave'), 'r') as file:
        valid, temp = file.readlines()
        return valid, temp
        #print (valid)
        #print(temp)
        
def read_temperature():
    valid, temp = read_temperature_raw()
    counter = 0
    while 'YES' not in valid:
        counter += 1
        time.sleep(0.2)
        valid, temperature = read_temperature_raw()
        if counter > 100:
            print('Nepodarilo se mi nacist spravne teplotu')
            return np.nan
    pos = temp.index('t=')
    if pos != -1:
        temp_str = temp[pos+2:]
        temp_float = float(temp_str)/1000
        return temp_float
    else:
        print('Nepodarilo se mi nacist spravne teplotu')
        return np.nan
            
print(read_temperature())
    
