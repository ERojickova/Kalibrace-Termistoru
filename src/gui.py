import datetime
import os
import platform
import random
import threading
import time
from tkinter import *

import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from sklearn import linear_model
#from sklearn.linear_model import LinearRegression


class GUI:
    def __init__(self):
        """
        - Inicializace potředných vlastností
        - Vytvoření GUI
        """
        self.time_start = -1
        self.is_running = False
        self.from_df = False
        self.temperature = -1
        self.voltage = -1
        self.time_now = 0

        self.ls_temp = []
        self.ls_volt = []
        self.ls_time = []
        self.ls_log_R = []
        self.ls_inverted_temp = []

        self.ballast_resist = 10_000  # Ohmů
        self.kelvin = 273.15  # K
        self.total_volt = 3.3  # V

        self.datafile_write = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data.csv"
        )
        self.datafile_read = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data-read.csv"
        )

        self.rpi = platform.uname()[4] == "armv7l"

        if self.rpi:
            from napeti import read_voltage
            from teplota import read_temperature

            self.step_lenght = 30  # s
        else:
            self.step_lenght = 0.2  # s

        # Připravení GUI pro zobrazování dat
        # Vytvoření a nastavení okna
        self.root = Tk()
        self.root.config(background="white")
        self.root.geometry("1000x750")
        self.root.title("Termistor")

        # Vytvoření rámečku pro lepší responsibilitu
        self.frame = LabelFrame(self.root, bg="white", borderwidth=0, highlightthickness=0)
        self.frame.pack()

        # Vytvoření nadpisu
        self.heading = Label(self.frame, text="Termistor", bg="white", font=("Ariel, 20"))
        self.heading.grid(row=0, column=0, columnspan=4, pady=(20, 0))        

        self.fig = Figure(figsize=(9, 6))
        self.fig.subplots_adjust(hspace=0.4)

        self.ax1 = self.fig.add_subplot(311)
        self.ax2 = self.fig.add_subplot(312)
        self.ax3 = self.fig.add_subplot(313)

        self.RemakeAxis()

        self.graph = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.graph.get_tk_widget().grid(row=1, column=0, columnspan=4)

        # Tlačítka
        self.button1 = Button(self.frame, text ="Start z měření", command=lambda: self.OnClick(False), width=15, height=3, bg="darkturquoise", font=("Ariel, 12"))
        self.button2 = Button(self.frame, text='Start ze souboru', command=lambda: self.OnClick(True), width=15, height=3, bg='darkturquoise', font=("Ariel, 12"))
        self.button1.grid(row=2, column=0, pady=(0,30))
        self.button2.grid(row=2, column=3, pady=(0,30))

        # Texty
        self.text_R=Label(self.frame, text=u"Koeficient R:", font=('Arial,  15'), bg='white')
        self.text_B=Label(self.frame, text=u"Koeficient B:", font=('Arial,  15'), bg='white')
        self.text_R.grid(row=2, column=1, pady=(0,30))
        self.text_B.grid(row=2, column=2, pady=(0,30))

        self.root.mainloop()

    def RemakeAxis(self):
        """
        --- Metoda znovu vytvoření os ---
            - Smazání předchozího grafu v jednotlivých soustavách
            - Znovu popsání os
        """
        self.ax1.cla()
        self.ax1.set_xlabel("čas [s]")
        self.ax1.set_ylabel("teplota [°C]")
        self.ax1.grid()

        self.ax2.cla()
        self.ax2.set_xlabel("čas [s]")
        self.ax2.set_ylabel("napětí [V]")
        self.ax2.grid()

        self.ax3.cla()
        self.ax3.set_xlabel("1/teplota [K]")
        self.ax3.set_ylabel("ln(R) [ln(ohm)]")
        self.ax3.grid()


    def OnClick(self, boolean):
        """
        --- Metoda, která se spouští po zmáčknutí tlačítka ---
            - Pokud je potředa načte data z csv souboru
            - Zavolá metodu Execution()
        """
        self.from_df = boolean

        if self.from_df and not self.is_running:
            if os.path.exists(self.datafile_read):
                self.dataframe_read = pd.read_csv(self.datafile_read)
                self.dataframe_read["Čas"] = pd.to_datetime(self.dataframe_read["Čas"])
            else:
                self.text_R.config(text='Soubor s daty nenalezen')

        self.Execution()


    def Execution(self):
        """
        --- Metoda provedení výpočtu ---
            - Pomocí vlastnosti is_running zjistíme zda:
                - Výpočet zastavujeme (is_running == True):
                    - Změna is_running na False
                    - Změna nápisu na tlačítkách
                    - Uložení dat do souboru csv
                    - Vyprázdnění listů na ukládání dat
                    - Zavolání metody MyLinearRegresion()
                - Výpočet spouštíme (is_running == False):
                    - Změna is_running na False
                    - Změna nápisu na tlačítkách
                    - Změna textu u koeficientů --> "Počítá se"
                    - Zavolání metody RemakeAxis()
                    - Spuštění druhého vlákna s metodou Plotter()

        """
        if self.is_running:
            self.is_running = False

            self.button1.config(text='Start z měření')
            self.button2.config(text='Start ze souborů')

            data = {'Čas': self.ls_time, 'Teplota':self.ls_temp, 'Napětí':self.ls_volt, 'Převrácená teplota':self.ls_inverted_temp, 'Zlogaritmovaný odpor':self.ls_log_R}
            self.dataframe_write = pd.DataFrame(data)

            self.ls_temp = []
            self.ls_volt = []
            self.ls_time = []
            self.ls_log_R = []
            self.ls_inverted_temp = []

            if self.from_df:
                self.button1.config(state="normal")
            else:
                self.dataframe_write.to_csv(self.datafile_write, index=False)
                self.button2.config(state="normal")

            self.MyLinearRegression()

        else:
            self.is_running = True

            self.button1.config(text='Stop')
            self.button2.config(text='Stop')
            self.text_R.config(text='Koeficient R se počítá')
            self.text_B.config(text='Koeficient B se počítá')
            
            if self.from_df:
                self.time_start = self.dataframe_read.at[0, 'Čas']
                self.button1.config(state="disabled")
            else:
                self.time_start = datetime.datetime.now()
                self.button2.config(state="disabled")

            self.RemakeAxis()
            threading.Thread(target=self.Plotter).start()


    def MyLinearRegression(self):
        """
        --- Metoda pro lineární regresi ---
            - Proložení posledního grafu přímkou
            - Vypočítání koeficientů R_25 s B
                - B = směrnice přímky
                - R_25 = interpolovaný odpor pro teplotu 25 °C
        """
        y = self.dataframe_write['Zlogaritmovaný odpor'].values.reshape(-1, 1)
        x = self.dataframe_write['Převrácená teplota'].values.reshape(-1, 1)

        lm = linear_model.LinearRegression().fit(x, y)
        x2 = [min(x), max(x)]  # Protože vím, že to bude přímka
        y2 = lm.predict(x2)


        T = np.array([1/(25 + self.kelvin)])
        log_R_25 = lm.predict(T.reshape(-1, 1))
        koef_R_25 = round(np.exp(log_R_25[0][0]), 2)

        koef_B = lm.coef_
        self.text_R.config(text=f'Koeficient R: {koef_R_25}')
        self.text_B.config(text=f'Koeficient B: {round(koef_B.tolist()[0][0], 2)}') 

        self.ax3.plot(x2,y2, marker='o', lw=1, label='Lineární regrese', color="dodgerblue")
        self.ax3.legend()        
        self.graph.draw()

    def Plotter(self):
        """
        --- Metoda pro kreselní grafů ---
            - Zavolání metody ReadData() 
            - Vypočítání dalších dat
            - Uložení dat do listů (pro uložení dat do csv souboru na konci měření)
            - Pro první bod (pomocí vlastnosti been) kreslíme jen jeden bod (respektive dva které ale leží na sobě)
            - Pro další body kreslíme vždy nový bod a bod minulý a jejich spojnici
            - Časová prodleva před dalším měřením
        
        """
        self.been = False

        while self.is_running:
            self.wait_till = datetime.datetime.now()+datetime.timedelta(seconds=self.step_lenght)
            self.ReadData()
            time_full = self.time_now


            if self.time_start != -1:
                self.inverted_temperature = 1/(self.temperature + self.kelvin)
                self.resistance = (self.voltage * self.ballast_resist)/(self.total_volt - self.voltage)
                self.log_resistance = np.log(self.resistance)

                self.ls_temp.append(self.temperature)
                self.ls_volt.append(self.voltage)
                self.ls_time.append(time_full)
                self.ls_inverted_temp.append(self.inverted_temperature)
                self.ls_log_R.append(self.log_resistance)
        

            if self.is_running:
                if self.been:
                    self.time_diff = time_full - self.time_start
                    self.time_diff = self.time_diff.total_seconds()
                else:
                    self.time_diff = 0
                    self.time_diff_old = 0
                    self.temperature_old = self.temperature
                    self.voltage_old = self.voltage
                    self.inverted_temperature_old = self.inverted_temperature
                    self.log_resistance_old = self.log_resistance
                    self.been = True

                self.ax1.plot([self.time_diff_old, self.time_diff], [self.temperature_old, self.temperature], marker='o', color='orange', lw=1)
                self.ax2.plot([self.time_diff_old, self.time_diff], [self.voltage_old, self.voltage], marker='x', color='forestgreen', lw=1)
                self.ax3.plot([self.inverted_temperature], [self.log_resistance], marker='s', color='gold',)

                self.time_diff_old = self.time_diff
                self.temperature_old = self.temperature
                self.voltage_old = self.voltage

                self.graph.draw()
            
            while datetime.datetime.now() < self.wait_till:
                time.sleep(0.001)
                

    def ReadData(self):
        """
        --- Metoda pro získávání dat ---
            - Pokud beru data ze souboru:
                - Načtení dat z prvního řádku dataframe_read
                - Smazání prvního řádku
            - Pokud data měřím:
                    - Jsem na Raspberry Pi --> měření dat pomocí senzorů
                    - Nejsem na Raspberry PI --> generování náhodných čísel v odpovídajícím intervalu 
        """
        if self.from_df:
            if len(self.dataframe_read) > 0:
                self.temperature = self.dataframe_read.at[0, 'Teplota']
                self.voltage = self.dataframe_read.at[0, 'Napětí']
                self.time_now = self.dataframe_read.at[0, 'Čas']

                self.dataframe_read = self.dataframe_read.drop([0]).reset_index().drop(columns=['index'])
            else:
                self.temperature = -1
                self.voltage = -1
                self.time_now = -1
                self.OnClick(True)
        else:
            if self.rpi:
                self.temperature = self.read_temperature()
                self.voltage = self.read_voltage()
            else:
                self.temperature = random.uniform(0, 50)
                self.voltage = random.uniform(0.1, 3.2)

            self.time_now = datetime.datetime.now()
        

# Spuštení objektu GUI()
if __name__ == '__main__':
    x = GUI()

