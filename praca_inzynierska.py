import numpy as np
import random

"====================== DANE ================================================"

ilosc_wyrobow = 6
ilosc_okresow = 17

A = np.random.randint(500, 3000)
koszty_stale = [np.random.randint(200, 1200) for i in range(ilosc_wyrobow)]
wartosci_wyrobow = [np.random.randint(5, 20) for i in range(ilosc_wyrobow)]
koszty_magazynowania = [np.random.randint(1, 10) for i in range(ilosc_wyrobow)]

popyt = np.zeros((ilosc_wyrobow, ilosc_okresow)).astype(int)
zmienna_losowosci_popytu = [random.random() for i in range(ilosc_wyrobow)]

for i in range(ilosc_wyrobow):
    for j in range(ilosc_okresow):
        if (zmienna_losowosci_popytu[i] <= 0.4):
            popyt[i][j] = np.random.randint(20, 150)
        elif (0.4 < zmienna_losowosci_popytu[i] <= 0.6):
            popyt[i][j] = np.random.randint(10, 200)
        elif (0.6 < zmienna_losowosci_popytu[i]):
            popyt[i][j] = np.random.randint(1, 20)

"=============== OBLICZANIE OKRESU T DLA ZAMÓWIEŃ GRUPOWYCH ================="

sredni_popyt = [int(round((sum(popyt[i])) / ilosc_okresow, 0))
                for i in range(ilosc_wyrobow)]

lista_x = [koszty_stale[i] / (wartosci_wyrobow[i] * sredni_popyt[i])
           for i in range(ilosc_wyrobow)]

wyrob_xmin = lista_x.index(min(lista_x))
wskaznik_xmin = (sredni_popyt[wyrob_xmin] * wartosci_wyrobow[wyrob_xmin]) / (A + koszty_stale[wyrob_xmin])

lista_m = [np.sqrt(lista_x[i] * wskaznik_xmin)
           for i in range(ilosc_wyrobow)]

k_zam = [koszty_stale[i] / lista_m[i] for i in range(ilosc_wyrobow)]
k_mag = [koszty_magazynowania[i] * sredni_popyt[i] * lista_m[i]
         for i in range(ilosc_wyrobow)]

T = int(round(np.sqrt((2 * (A + sum(k_zam))) / sum(k_mag)), 0))

"===================== OBLICZANIE POPYTU DLA OKRESU T ======================="

popyt_T = [[] for i in range(ilosc_wyrobow)]

for i in range(ilosc_wyrobow):
    popyt_T[i] = [sum(popyt[i][j:j+T]) for j in range(0, ilosc_okresow, T)]

ilosc_okresow_T = len(popyt_T[0])

"===================== METODA SILVERA-MEALA =============================="

srednie = [[] for i in range(ilosc_wyrobow)]
na_ile_okresow_T = [[] for i in range(ilosc_wyrobow)]

for i in range(ilosc_wyrobow):

    lista_kosztow_magazynowania = []
    zmienna_kosztow = (sum(popyt_T[i]) + koszty_stale[i]) * ilosc_okresow_T
    okres_T = 0
    okres = 0
    koszt_magazynowania_dla_okresu = 0
    srednia_kosztow = 0

    while okres_T <= ilosc_okresow_T - 1:

        koszt_magazynowania_dla_okresu = popyt_T[i][okres_T] * koszty_magazynowania[i] * T * okres
        lista_kosztow_magazynowania.append(koszt_magazynowania_dla_okresu)
        srednia_kosztow = (sum(lista_kosztow_magazynowania) + koszty_stale[i]) / (okres + 1)
        srednie[i].append(srednia_kosztow)

        if (srednia_kosztow <= zmienna_kosztow):
            zmienna_kosztow = srednia_kosztow
            okres += 1
            okres_T += 1

        else:
            na_ile_okresow_T[i].append(okres)
            lista_kosztow_magazynowania.clear()
            zmienna_kosztow = (sum(popyt_T[i]) + koszty_stale[i]) * ilosc_okresow_T
            okres = 0

    na_ile_okresow_T[i].append(ilosc_okresow_T - sum(na_ile_okresow_T[i]))

"==== OBLICZANIE W KTÓRYCH OKRESACH T I OKRESACH ZWYKLYCH NALEŻY ZŁOŻYĆ ZAMÓWIENIE ===="

kiedy_zamawiac_T = [[] for i in range(ilosc_wyrobow)]
kiedy_zamawiac = [[] for i in range(ilosc_wyrobow)]

for i in range(ilosc_wyrobow):
    kiedy_zamawiac_T[i] = [sum(na_ile_okresow_T[i][0:j])
                           for j in range(len(na_ile_okresow_T[i]))]
    kiedy_zamawiac[i] = [element * T for element in kiedy_zamawiac_T[i]]

"====== OBLICZANIE SKORYGOWANEGO POPYTU DLA OKRESU T ========================="

popyt_T_skorygowany = [ [] for i in range(ilosc_wyrobow)]

for i in range(ilosc_wyrobow):
    popyt_T_skorygowany[i] = [sum(popyt_T[i]
                                  [kiedy_zamawiac_T[i][j-1]:kiedy_zamawiac_T[i][j]])
                           for j in range(1, len(kiedy_zamawiac_T[i]))]

    popyt_T_skorygowany[i].append(sum(popyt_T[i]) - sum(popyt_T_skorygowany[i]))

"============== WIELKOŚĆ ZAMÓWIENIA W KOLEJNYCH OKRESACH  ========================="

zamowienie = np.zeros((ilosc_wyrobow, ilosc_okresow)).astype(int)

for i in range(ilosc_wyrobow):
    okres_popytu_T = 0
    for j in range(ilosc_okresow):
        if (j in kiedy_zamawiac[i]):
            zamowienie[i][j] = popyt_T_skorygowany[i][okres_popytu_T]
            okres_popytu_T += 1

"================== ZAPAS NA KONIEC KAŻDEGO OKRESU  ========================="

zapas_koniec = np.zeros((ilosc_wyrobow, ilosc_okresow)).astype(int)

for i in range(ilosc_wyrobow):
    ilosc = 0
    for j in range(ilosc_okresow):
        ilosc = ilosc + zamowienie[i][j] - popyt[i][j]
        zapas_koniec[i][j] = ilosc

"============== ZAPAS NA POCZATKU KAŻDEGO OKRESU  ========================="

zapas_poczatek = np.zeros((ilosc_wyrobow, ilosc_okresow)).astype(int)

for i in range(ilosc_wyrobow):
    ilosc = 0
    for j in range(ilosc_okresow):
        if (j == 0):
            ilosc = zamowienie[i][j]
        else:
            ilosc = zapas_koniec[i][j-1] + zamowienie[i][j]
        zapas_poczatek[i][j] = ilosc

"================== OBLICZANIE KOSZTU CAŁKOWITEGO  ========================="

calkowity_koszt_magazynowania = sum([sum(zapas_koniec[i]) * koszty_magazynowania[i]
                                     for i in range(ilosc_wyrobow)])

calkowity_koszt_zamawiania  = sum([len(kiedy_zamawiac_T[i]) * koszty_stale[i]
                               for i in range(ilosc_wyrobow)]) + ilosc_okresow_T * A

calkowity_koszt = calkowity_koszt_magazynowania + calkowity_koszt_zamawiania

"============ GENEROWANIE ZMIENNYCH BINARNYCH DLA ZAMÓWIEŃ ==============="

zmienna_zamowienia_wspolnego = np.zeros(ilosc_okresow).astype(int)

for i in range(0, ilosc_okresow, T):
    zmienna_zamowienia_wspolnego[i] = 1

zmienna_zamowienia_dla_wyrobow = [ [] for i in range(ilosc_wyrobow)]

for i in range(ilosc_wyrobow):
    zmienna_zamowienia_dla_wyrobow[i] = [1 if zamowienie[i][j] != 0 else 0
                                      for j in range(ilosc_okresow)]

"======================== GENEROWANIE PLIKU TXT I CSV ==========================="

plik_txt = open("wyniki.txt", "w")
plik_txt.write("Harmonogram zamawiania dla {} materiałów dla {} okresów.\n".format(ilosc_wyrobow, ilosc_okresow))
plik_txt.write("Wielkość T (częstość zamówień): {}\n".format(T))
for i in range(ilosc_wyrobow):
    plik_txt.write("\n\nMateriał {}".format(i+1))
    plik_txt.write("\nWielkość zamówienia w kolejnych okresach (rozpoczynając od okresu 0): {}\n".format(list(zamowienie[i])))
    plik_txt.write("\nZapas na początku okresu (rozpoczynając od okresu 1): {}".format(list(zapas_poczatek[i])))
    plik_txt.write("\nPopyt w danym okresie (rozpoczynając od okresu 1):    {}".format(list(popyt[i])))
    plik_txt.write("\nZapas na koniec okresu (rozpoczynając od okresu 1):   {}\n".format(list(zapas_koniec[i])))
plik_txt.write("\n\nCałkowity koszt: {}".format(calkowity_koszt))
plik_txt.close()

plik_csv = open('wyniki.csv', 'w')
plik_csv.write('zmienna;wyrob;okres;wartosc')
for i in range(ilosc_wyrobow):
    for j in range(ilosc_okresow):
        plik_csv.write('\nzamowienie;{};{};{}'.format(i + 1, j + 1, zamowienie[i][j]))
        plik_csv.write('\nzapas_poczatek;{};{};{}'.format(i + 1, j + 1, zapas_poczatek[i][j]))
        plik_csv.write('\npopyt;{};{};{}'.format(i + 1, j + 1, popyt[i][j]))
        plik_csv.write('\nzapas_koniec;{};{};{}'.format(i + 1, j + 1, zapas_koniec[i][j]))
        plik_csv.write('\nczy_zamawiac;{};{};{}'.format(i + 1, j + 1, zmienna_zamowienia_dla_wyrobow[i][j]))
for i in range(ilosc_okresow):
    plik_csv.write('\nczy_zamawiac_grupowo;;{};{}'.format(i + 1, zmienna_zamowienia_wspolnego[i]))
plik_csv.close()

