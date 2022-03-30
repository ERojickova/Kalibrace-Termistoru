from ADCDACPi import ADCDACPi

prevodnik = ADCDACPi(2)


def read_voltage():
    """
    --- Funkce na měření napětí ---
        - funkce využívá knihovnu ADCDACPi a z ní konkrétně stejnojmennou třídu ADCDACPi()
        - pomocí funkce read_adc_voltage() změří aktuální napětí
    """
    return prevodnik.read_adc_voltage(1,0)
