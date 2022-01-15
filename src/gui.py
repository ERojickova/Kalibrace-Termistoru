from inspect import indentsize
from logging import log
from tkinter import *
import random

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import threading
import datetime
import numpy as np
from sklearn import linear_model
from sklearn.linear_model import LinearRegression
import os
import platform



"""
Vyzkoušení zda program běží na Raspberry Pi či nikoli
Při použití jiného Raspberry Pi je možná potřeba změnit název procesoru
"""
rpi = platform.uname()[4] == 'armv7l'

if rpi:
    from napeti import read_voltage
    from teplota import read_temperature


cas_start = -1
vypocet_bezi = False
z_dataframu = False

ls_temperature = []
ls_voltage = []
ls_time = []
ls_log_R = []
ls_temperature_ratio = []


oochrany_R = 10_000 #ohmů
kelvin = 273.15 #K
celkove_napeti = 3.3 #V
# pocet_dat = 0

datafile = os.path.join (os.path.dirname(os.path.abspath(__file__)), 'data.csv')
df = pd.DataFrame()



def app():
    if rpi:
        delka_kroku = 30 #s
    else:
        delka_kroku = 1 #s


    def onClick(boolean):
        global z_dataframu
        global temp 
        global volt
        global cas_ted
        global df2
        global vypocet_bezi
        # global pocet_dat

        z_dataframu = boolean
        temp = 0
        volt = 0
        cas_ted = 0

        # nacti csv data pokud nechci realne mereni
        if z_dataframu and not vypocet_bezi:
            if os.path.exists(datafile):
                df2 = pd.read_csv(datafile)
                df2 ['Čas'] = pd.to_datetime(df2['Čas'])

                # pocet_dat = len(df2)
            else:
                print (f'Nemam {datafile}, koncim')
                text_R.config(text='Soubor s daty nenalezen')
                return

        zaciname()
        

    def readData():
        global df2


        if z_dataframu:
            if len(df2) > 0:
                temp = df2.at[0, 'Teplota']
                volt = df2.at[0, 'Napětí']
                cas_ted = df2.at[0, 'Čas']

                df2 = df2.drop([0]).reset_index().drop(columns=['index'])
            else:
                # dosla data, zastav vypocet, stejne jako bych kliknul na tlacitko
                cas_ted = -1 # zadna dalsi data
                temp = -1
                volt = -1
                onClick(True)

        else:
            if rpi:
                temp = read_temperature()
                volt = read_voltage()
            else:
                # generace náhodných čísel, pokud chceme data měřit ale nemáme senzory (respektive nejsme na rpi)
                temp = random.uniform(0, 50)
                volt = random.uniform(0.1, 3.2)
                
            cas_ted = datetime.datetime.now()


        return cas_ted, temp, volt

    def plotter():
        global cas_start
        global kelvin
        global oochrany_R
        global celkove_napeti


        # Proměna do které se ukláda jestli je to první hodnota na nebo ne
        been = False

        while vypocet_bezi:
            pockej_do_casu = datetime.datetime.now()+datetime.timedelta(seconds=delka_kroku)
            cas_full, teplota, napeti = readData()

            if cas_full != -1:
                podelena_teplota = 1/(teplota + kelvin)
                odpor = (napeti * oochrany_R)/(celkove_napeti - napeti)
                log_odpor = np.log(odpor)

                ls_temperature.append(teplota)
                ls_voltage.append(napeti)
                ls_time.append(cas_full) 
                ls_temperature_ratio.append(podelena_teplota)
                ls_log_R.append(log_odpor)
                


             # v readData se mohl zmenit stav vypocet_bezi
            if vypocet_bezi:
                if been:
                    cas_diff = cas_full - cas_start
                    cas_diff = cas_diff.total_seconds()
                else:
                    # Pro první hodnotu se nakreslí jen bod, bez spojnice
                    cas_diff = 0
                    cas_old_diff = 0
                    teplota_old = teplota
                    napeti_old = napeti
                    podelena_teplota_old = podelena_teplota
                    log_odpor_old = log_odpor
                    been = True

                # Kreslení grafů
                ax1.plot([cas_old_diff, cas_diff], [teplota_old, teplota], marker='o', color='orange', lw=1)
                ax2.plot([cas_old_diff, cas_diff], [napeti_old, napeti], marker='x', color='forestgreen', lw=1)
                ax3.plot([podelena_teplota_old, podelena_teplota], [log_odpor_old, log_odpor], marker='s', color='gold', lw=0)


                # Přenastavení proměnných pro příští kreslení
                cas_old_diff = cas_diff
                teplota_old = teplota
                napeti_old = napeti

                # Zobrazení grafu
                graph.draw()

            # Prodleva před dalším kreslením
            while datetime.datetime.now() < pockej_do_casu:
                time.sleep(0.001)

    def zaciname():

        # spust vlakno, ktere meri teploty a kresli
        global cas_start
        global vypocet_bezi
        global datafile
        global df
        global ls_temperature
        global ls_voltage
        global ls_time
        global ls_temperature_ratio
        global ls_log_R
        #global pocet_dat

        # zastav, kdyz dojdou hodnoty z csv souboru
        # if z_dataframu:
        #     if pocet_dat < 1:
        #         vypocet_bezi = False
        #     else:
        #         vypocet_bezi = True

        if vypocet_bezi:
            vypocet_bezi = False

            tlacitko.config(text='Start z měření')
            tlacitko2.config(text='Start ze souborů')

            # if os.path.exists(datafile):
            #     os.remove(datafile)

            data = {'Čas': ls_time, 'Teplota':ls_temperature, 'Napětí':ls_voltage, 'Podíl teplot':ls_temperature_ratio, 'Zlogaritmovaný odpor':ls_log_R}
            df = pd.DataFrame(data)

            ls_temperature = []
            ls_voltage = []
            ls_time = []
            ls_log_R = []
            ls_temperature_ratio = []

            if z_dataframu:
                tlacitko.config(state="normal")  # obnovim tlacitko mereni
            else:
                df.to_csv(datafile, index=False)
                tlacitko2.config(state="normal")  # obnovim tlacitko ze souboru

            y = df['Zlogaritmovaný odpor'].values.reshape(-1, 1)
            x = df['Podíl teplot'].values.reshape(-1, 1)

            lm = linear_model.LinearRegression().fit(x, y)
            x2 = [min(x), max(x)] #Protože vím, že to bude přímka
            y2 = lm.predict(x2)

            koef_R = lm.coef_
            koef_B = lm.intercept_
            text_R.config(text=f'Koeficient R: {round(koef_R.tolist()[0][0], 2)}')
            text_B.config(text=f'Koeficient B: {round(koef_B.tolist()[0], 2)}')   
            ax3.plot(x2,y2, marker='o', lw=1, label='Lineární regrese', color="dodgerblue")
            ax3.legend()        
            graph.draw()

        else:
            tlacitko.config(text='Stop')
            tlacitko2.config(text='Stop')

            text_R.config(text='Koeficient R se počítá')
            text_B.config(text='Koeficient B se počítá') 
            

            if z_dataframu:
                cas_start = df2.at[0, 'Čas']
                tlacitko.config(state="disabled") #zrusim tlacitko mereni
            else:
                cas_start = datetime.datetime.now() #skutecny cas, kdy zacinam kreslit
                tlacitko2.config(state="disabled") #zrusim tlacitko ze souboru

            vypocet_bezi = True
            ax1.cla()
            ax2.cla()
            ax3.cla()

            ax1.set_xlabel("čas [s]")
            ax1.set_ylabel("teplota [°C]")
            ax1.grid()

            ax2.set_xlabel("čas [s]")
            ax2.set_ylabel("napětí [V]")
            ax2.grid()

            ax3.set_xlabel("1/teplota [K]")
            ax3.set_ylabel("ln(R) [ln(ohm)]")
            ax3.grid()

            threading.Thread(target=plotter).start()

        return



    # Vytvoření okna
    root = Tk()
    root.config(background='white')
    root.geometry("1000x750")
    root.title("Termistor")

    # Vytvoření rámečku pro lepší responsibilitu
    frame = LabelFrame(root, bg='white', borderwidth=0, highlightthickness=0)
    frame.pack()

    # Vytvoření nadpisu
    nadpis = Label(frame, text="Termistor", bg='white', font=("Ariel, 20"))
    nadpis.grid(row=0, column=0, columnspan=4, pady=(20,0))

    
    fig = Figure(figsize=(9,6))
    fig.subplots_adjust(hspace=0.4)

    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)


    ax1.set_xlabel("čas [s]")
    ax1.set_ylabel("teplota [°C]")
    ax1.grid()
    ax2.set_xlabel("čas [s]")
    ax2.set_ylabel("napětí [V]")
    ax2.grid()
    ax3.set_xlabel("1/teplota [K]")
    ax3.set_ylabel("ln(R) [ln(ohm)]")
    ax3.grid()
    

    

    graph = FigureCanvasTkAgg(fig, master=frame)
    graph.get_tk_widget().grid(row=1, column=0, columnspan=4)


    # Tlačítko start/stop
    tlacitko = Button(frame, text ="Start z měření", command=lambda: onClick(False), width=15, height=3, bg="darkturquoise", font=("Ariel, 12"))
    tlacitko.grid(row=2, column=0, pady=(0,30))


    # Zobrazení koeficientu R nekonečno
    text_R=Label(frame, text=u"Koeficient R:", font=('Arial,  15'), bg='white')
    text_R.grid(row=2, column=1, pady=(0,30))
    
    # Zobrazení koeficinetu B
    text_B=Label(frame, text=u"Koeficient B:", font=('Arial,  15'), bg='white')
    text_B.grid(row=2, column=2, pady=(0,30))

    # Tlačítko na zavření okna
    tlacitko2 = Button(frame, text='Start ze souboru', command=lambda: onClick(True), width=15, height=3, bg='darkturquoise', font=("Ariel, 12"))
    tlacitko2.grid(row=2, column=3, pady=(0,30))

    root.mainloop()


app()
