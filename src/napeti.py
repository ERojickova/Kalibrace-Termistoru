from ADCDACPi import ADCDACPi

prevodnik = ADCDACPi(2)

v = prevodnik.read_adc_voltage(1,0)
print (v)



#print(read_adc_raw(1, 0))