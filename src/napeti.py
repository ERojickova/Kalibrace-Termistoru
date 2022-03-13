from ADCDACPi import ADCDACPi

prevodnik = ADCDACPi(2)

def read_voltage():
    return prevodnik.read_adc_voltage(1,0)
