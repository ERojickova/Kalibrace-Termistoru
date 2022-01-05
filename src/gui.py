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

#from napeti import read_voltage
#from teplota import read_temperature


cas_start = -1
vypocet_bezi = False
temperature = []
voltage = []
z_dataframu = False
datafile = 'data.csv'
df = pd.DataFrame()


def app():
    delka_kroku = 1 #s


    def onClick(boolean):
        global z_dataframu 
        z_dataframu = boolean
        zaciname()
        

    def readData():
        global temperature
        global voltage
        if z_dataframu:
            pass
        else:
            # temp = read_temperature()
            # volt = read_volateg()

            temp = random.random()*10+10
            volt = random.random()*10+10

            temperature.append(temp)
            voltage.append(volt)

            return datetime.datetime.now(), temp, volt
        

    # def readTemp():
    #     # temp = read_temperature()
    #     temp = random.random()*10+10
    #     temperature.append(temp)
    #     return datetime.datetime.now(), temp

    # def readVoltage():
    #     # volt = read_volateg()
    #     volt = random.random()*10+10
    #     voltage.append(volt)
    #     return datetime.datetime.now(), volt
        

    def plotter():
        global cas_start


        # Proměna do které se ukláda jestli je to první hodnota na nebo ne
        been = False

        while vypocet_bezi:
            pockej_do_casu = datetime.datetime.now()+datetime.timedelta(seconds=delka_kroku)
            cas_full, teplota, napeti = readData()

            if been:
                cas_diff = cas_full - cas_start
                cas_diff = cas_diff.total_seconds()
            else:
                # Pro první hodnotu se nakreslí jen bod, bez spojnice
                cas_diff = 0
                cas_old_diff = 0
                teplota_old = teplota
                napeti_old = napeti
                been = True

            # Kreslení grafů
            ax1.plot([cas_old_diff, cas_diff], [teplota_old, teplota], marker='o', color='orange', lw=1)
            ax2.plot([cas_old_diff, cas_diff], [napeti_old, napeti], marker='x', color='forestgreen', lw=1)
            ax3.plot([teplota_old, teplota], [napeti_old, napeti], marker='s', color='gold', lw=0)
    

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
        global temperature
        global voltage
        
        if vypocet_bezi:
            vypocet_bezi = False

            tlacitko.config(text='Start z měření')
            tlacitko2.config(text='Start ze souborů')

            if os.path.exists(datafile):
                os.remove(datafile)
            data = {'Teplota':temperature, 'Napětí':voltage}
            df = pd.DataFrame(data)
            temperature = []
            voltage = []



            df.to_csv(datafile)
            y = df['Napětí'].values.reshape(-1, 1)
            x = df['Teplota'].values.reshape(-1, 1)

            lm = linear_model.LinearRegression().fit(x, y)
            x2 = [min(x), max(x)] #Protože vím, že to bude přímka
            y2 = lm.predict(x2)

            seebecuv_koeficient = lm.coef_
            text_seeb_koef.config(text=f'Seebecův koeficient: {round(seebecuv_koeficient.tolist()[0][0], 2)}')       
            ax3.plot(x2,y2, marker='o', lw=1, label='Lineární regrese', color="dodgerblue")
            ax3.legend()        
            graph.draw()

        else:
            cas_start = datetime.datetime.now() #skutecny cas, kdy zacinam kreslit
            tlacitko.config(text = 'Stop')
            vypocet_bezi = True
            ax1.cla()
            ax2.cla()
            ax3.cla()

            ax1.set_xlabel("cas (s)")
            ax1.set_ylabel("teplota (°C)")
            ax1.grid()

            ax2.set_xlabel("cas (s)")
            ax2.set_ylabel("napětí (V)")
            ax2.grid()

            ax3.set_xlabel("rozdíl teplot(K)")
            ax3.set_ylabel("napětí (V)")
            ax3.grid()

            threading.Thread(target=plotter).start()

        return

     


    # Vytvoření okna
    root = Tk()
    root.config(background='white')
    root.geometry("1000x750")

    # Vytvoření rámečku pro lepší responsibilitu
    frame = LabelFrame(root, bg='white', borderwidth=0, highlightthickness=0)
    frame.pack()

    # Vytvoření nadpisu
    nadpis = Label(frame, text="Seebecův jev", bg='white', font=("Ariel, 20"))
    nadpis.grid(row=0, column=0, columnspan=3, pady=(20,0))

    
    fig = Figure(figsize=(10,6))
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)

    ax1.set_xlabel("čas (s)")
    ax1.set_ylabel("teplota (°C)")
    ax1.grid()

    ax2.set_xlabel("čas (s)")
    ax2.set_ylabel("napětí (V)")
    ax2.grid()

    ax3.set_xlabel("rozdíl teplot(K)")
    ax3.set_ylabel("napětí (V)")
    ax3.grid()

    graph = FigureCanvasTkAgg(fig, master=frame)
    graph.get_tk_widget().grid(row=1, column=0, columnspan=3)


    # Tlačítko start/stop
    tlacitko = Button(frame, text ="Start z měření", command=lambda: onClick(False), width=15, height=3, bg="darkturquoise", font=("Ariel, 12"))
    tlacitko.grid(row=2, column=0, pady=(0,30))


    # Zobrazení seebecova koeficientu
    text_seeb_koef=Label(frame, text=u"Seebecův koeficient:", font=('Arial,  15'), bg='white')
    text_seeb_koef.grid(row=2, column=1, pady=(0,30))

    # Tlačítko na zavření okna
    tlacitko2 = Button(frame, text='Start ze souboru', command=lambda: onClick(True), width=15, height=3, bg='darkturquoise', font=("Ariel, 12"))
    tlacitko2.grid(row=2, column=2, pady=(0,30))


    root.mainloop()


app()