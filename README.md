# Kalibrace termistoru
Maturitní práce 
Gymnázium Nad Štolou, Praha 2022

### Požadavky

* Python 3.9+
* Tkinter
* Sklearn
* Pandas
* Numpy

### Instalace

Pro spustění kódu je potřeba instalovat:

```sh
# install tkinter
pip install tk
# install Sklearn
pip install scikit-learn
# install Pandas
pip install pandas
# install Numpy
pip install numpy

```

### Použití
Program slouží k vytvoření uživatelského prostředí pro experiment kalibrace termistoru pomocí Raspberry Pi. 
 * Po spuštění souboru `gui.py` se zobrazí dialogové okno, kde vidíme prostředí připravené pro měření grafů.
 * Nachází se tam dvě tlačítka
     *  Levé pro spuštění se zapojeným obvodem, kdy se budou data měřit z reálného experimentu. 
     * Pravé spustí kód s tím, že se data budou brát z csv souboru, kde jsou hodnoty naměřené z předchozího měření.
 * Pro zastavení experimentu je potřeba zmáčknout tlačítko Stop, lineární regrese a hodnoty koeficientů se vypočítají a zobrazí automaticky.
 * Program pozná zda běží na RPi nebo na počítači podle typu procesoru, při spouštění na RPi s jiným procesorem než armv71 je potřeba změnit typ procesoru (v souboru `gui.py` na řádku 48)
 * Při snaze spustit měření se zapojeným obvodem, ovšem na počítači se do grafů začnou generovat náhodná čísla a koeficienty nebudou o ničem vypovídat.
