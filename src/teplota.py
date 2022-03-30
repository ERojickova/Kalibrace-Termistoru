import os
import glob
import time
import numpy as np

"""
Nahrání potřebných ovladačů 
 - potřeba na RPi spustit pomocí suda
 - vytvoří se tak virtuální zařízení 
"""
#os.system("modprobe w1-gpio")
#os.system("modprobe w1-therm")

base_dir = '/sys/bus/w1/devices'
device_path = glob.glob(os.path.join(base_dir,'28*'))[0]

def read_temperature_raw():
    """
    - Načtení souboru po řádcích do dvou proměnných bez úpravy  
    """
    with open(os.path.join(device_path, 'w1_slave'), 'r') as file:
        valid, temp = file.readlines()
        return valid, temp

        
def read_temperature():
    """
    --- Upravení teploty na hodnotu se kterou můžeme dále počítat ---
        - První provedení kontroly, zda se teplota načetla
        - Načtení teploty do proměnné temp_float, kterou pak funkce vrací
    """
    valid, temp = read_temperature_raw()
    counter = 0
    while 'YES' not in valid:
        counter += 1
        time.sleep(0.2)
        valid, temp = read_temperature_raw()
        if counter > 100:
            print('Nepodařilo se správně načíst teplotu')
            return np.nan
    pos = temp.index('t=')
    if pos != -1:
        temp_str = temp[pos+2:]
        temp_float = float(temp_str)/1000
        return temp_float
    else:
        print('Nepodařilo se správně načíst teplotu')
        return np.nan