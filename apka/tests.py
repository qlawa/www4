from random import randint
from django.contrib.auth.models import User
from selenium.webdriver.common.alert import Alert

from apka.models import Okreg, Gmina, Obwod, Wojewodztwo, Kandydat, Statystyka, Wynik
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver import ActionChains
from urllib.parse import urljoin
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import time

SLEEP_TIME = 0.5


def wypelnij_baze_danych():
    # przygotowanie struktury kraju
    wojewodztwo = Wojewodztwo(numer=60, nazwa='TestWojewództwa')
    okreg = Okreg(numer=61, wojewodztwo=wojewodztwo)
    gmina = Gmina(okreg=okreg, numer=62, nazwa='TestGminy')
    obwod1 = Obwod(numer=6, gmina=gmina, nazwa='TestObwodu1')
    obwod2 = Obwod(numer=7, gmina=gmina, nazwa='TestObwodu2')
    wojewodztwo.save()
    okreg.save()
    gmina.save()
    obwod1.save()
    obwod2.save()

    kandydaci = [{'imie': 'A', 'nazwisko': 'AA'},
                 {'imie': 'B', 'nazwisko': 'BB'},
                 {'imie': 'C', 'nazwisko': 'CC'},
                 ]
    for kandydat in kandydaci:
        Kandydat(imie=kandydat['imie'], nazwisko=kandydat['nazwisko']).save()

    # przygotowanie przykładowych wyników
    for obwod in Obwod.objects.all():
        glosy_wazne = 0
        for kandydat in Kandydat.objects.all():
            liczba = randint(0, 1000)
            Wynik(kandydat=kandydat, liczba=liczba, obwod=obwod).save()
            glosy_wazne += liczba

        glosy_niewazne = randint(1, 100)
        Statystyka(etykieta='Głosy ważne', liczba=glosy_wazne, obwod=obwod).save()
        Statystyka(etykieta='Głosy nieważne', liczba=glosy_niewazne, obwod=obwod).save()
        Statystyka(etykieta='Głosy oddane', liczba=glosy_niewazne + glosy_wazne, obwod=obwod).save()
        Statystyka(etykieta='Wydane karty', liczba=glosy_niewazne + glosy_wazne + randint(0, 50),
                   obwod=obwod).save()
        Statystyka(etykieta='Uprawnieni', liczba=2 * (glosy_niewazne + glosy_wazne) + randint(0, 50),
                   obwod=obwod).save()


def dodaj_uzytkownika(login='jan', haslo='kowalski'):
    User.objects.create_user(username=login, password=haslo)


def otwieranie_strony_glownej(klasa_test, selenium):
    selenium.get(klasa_test.live_server_url)
    selenium.implicitly_wait(10)  # seconds


def otwieranie_strony_logowania(klasa_test, selenium):
    selenium.get(urljoin(klasa_test.live_server_url, '/login/'))
    selenium.implicitly_wait(10)  # seconds


def logowanie(klasa_test, selenium, str_uzytkownik='jan', str_haslo='kowalski'):
    otwieranie_strony_logowania(klasa_test, selenium)
    reszta_logowania(selenium, str_uzytkownik, str_haslo)


def reszta_logowania(selenium, str_uzytkownik='jan', str_haslo='kowalski'):
    uzytkownik = selenium.find_element_by_id('login')
    haslo = selenium.find_element_by_id('password')
    uzytkownik.send_keys(str_uzytkownik)
    haslo.send_keys(str_haslo)
    zaloguj = selenium.find_element_by_id('zaloguj')
    zaloguj.click()
    time.sleep(SLEEP_TIME)


def wylogowywanie(klasa_test, selenium):
    otwieranie_strony_glownej(klasa_test, selenium)
    time.sleep(SLEEP_TIME)
    wyloguj = selenium.find_element_by_link_text('Wyloguj')
    wyloguj.click()
    time.sleep(SLEEP_TIME)


def assert_jestem_na_stronie_logowania(klasa_test):
    time.sleep(SLEEP_TIME)
    url = klasa_test.selenium.current_url
    url = url[-7:]
    print(url)
    klasa_test.assertEqual('/login/', url)


def przejdz_do_wojewodztwa(selenium):
    actions = ActionChains(selenium)
    lodz = selenium.find_element_by_id("polska")
    actions.move_to_element(lodz)
    actions.click()
    actions.perform()
    time.sleep(SLEEP_TIME)


def przejdz_do_okregu(selenium):
    okreg = selenium.find_element_by_link_text("Okreg 18")
    okreg.click()
    time.sleep(SLEEP_TIME)


def przejdz_do_gminy(selenium):
    selenium.find_element_by_link_text("Gmina Buczek").click()
    time.sleep(SLEEP_TIME)


def przejdz_do_obwodu(selenium):
    selenium.find_element_by_id("90595").click()
    time.sleep(SLEEP_TIME)


def sprawdz_spojnosc_danych_na_stronie(klasa_test, selenium):
    liczby = selenium.find_elements_by_xpath("//table[@class='tabela_wynikow']/tbody[1]/tr/td[2]")
    staty = selenium.find_elements_by_xpath("//table[@class='tabela_statystyk']/tbody[1]/tr/td[2]")

    suma_kandydatow = 0
    for liczba in liczby:
        foo = int(liczba.text)
        suma_kandydatow += foo
        klasa_test.assertTrue(foo >= 0)

    etykiety = ['Uprawnieni', 'Wydane karty', 'Głosy oddane', 'Głosy ważne', 'Głosy nieważne']
    statystyki = {}
    for i in range(0, len(etykiety)):
        statystyki[etykiety[i]] = int(staty[i].text)

    klasa_test.assertTrue(statystyki['Uprawnieni'] >= statystyki['Wydane karty'])
    klasa_test.assertTrue(statystyki['Wydane karty'] >= statystyki['Głosy oddane'])
    klasa_test.assertEqual(statystyki['Głosy oddane'], statystyki['Głosy ważne'] + statystyki['Głosy nieważne'])
    klasa_test.assertTrue(statystyki['Głosy nieważne'] >= 0)
    klasa_test.assertEqual(suma_kandydatow, statystyki['Głosy ważne'],
                           'Suma liczby głosów oddana na kandydatów jest różna od głosów ważnych')


def pobieranie_wartosci_z_roznych_podzialow(klasa_test, selenium):
    wynik = []
    otwieranie_strony_glownej(klasa_test, selenium)
    wynik.append(daj_wynik_kandydata_nr(klasa_test, selenium))
    przejdz_do_wojewodztwa(selenium)
    wynik.append(daj_wynik_kandydata_nr(klasa_test, selenium))
    przejdz_do_okregu(selenium)
    wynik.append(daj_wynik_kandydata_nr(klasa_test, selenium))
    przejdz_do_gminy(selenium)
    wynik.append(daj_wynik_kandydata_nr(klasa_test, selenium))
    wynik.append(daj_wynik_kandydata_nr(klasa_test, selenium, czy_obwod=True))
    print('wyniki = {}'.format(wynik))
    return wynik


def zmniejsz_wartosc(selenium, zmniejszenie=1, kandydat=1):
    input_wynik = selenium.find_element_by_xpath("//table[@class='wierszeFormularza']/tbody[1]/tr[" +
                                                 str(kandydat) + "]/td[2]/input")
    liczba = int(input_wynik.get_attribute('value'))

    if liczba - zmniejszenie < 0:
        if liczba == 0:
            zmniejszenie = -1
        else:
            zmniejszenie = 1

    input_wynik.clear()
    input_wynik.send_keys(int(liczba) - zmniejszenie)
    input_wynik.submit()
    return zmniejszenie


def daj_wynik_kandydata_nr(klasa_test, selenium, numer_kandydata=1, czy_obwod=False, numer_obwodu=1):
    klasa_test.assertTrue(1 <= numer_kandydata <= len(Kandydat.objects.all()))
    xpath = "//table[@class='tabela_wynikow']/tbody[1]/tr[" + str(numer_kandydata) + "]/td[2]"
    if czy_obwod:
        xpath = "//table[@class='wynikiObwody']/tbody[1]/tr[" + str(numer_obwodu) + "]/td[" + \
                str(numer_kandydata + 1) + "]"
    return int(selenium.find_element_by_xpath(xpath=xpath).text)


class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(MySeleniumTests, cls).setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--disable-web-security")
        cls.selenium = webdriver.Chrome(chrome_options=chrome_options)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(MySeleniumTests, cls).tearDownClass()


class AutoryzacjaTest(MySeleniumTests):
    @classmethod
    def setUp(cls):
        super(AutoryzacjaTest, cls).setUpClass()
        dodaj_uzytkownika()

    def test_login(self):
        logowanie(self, self.selenium)
        otwieranie_strony_glownej(self, self.selenium)
        time.sleep(0.5)
        text = self.selenium.find_element_by_id('loginPanel').text
        self.assertEqual('Jesteś zalogowany jako jan. Wyloguj', text)
        self.selenium.close()

    def test_logout(self):
        logowanie(self, self.selenium)
        wylogowywanie(self, self.selenium)
        time.sleep(0.5)
        text = self.selenium.find_element_by_id('loginPanel').text
        self.assertEqual('Zaloguj', text)
        self.selenium.close()

    def test_bad_login(self):
        logowanie(self, self.selenium, str_uzytkownik='blabla')
        alert = Alert(self.selenium)
        self.assertEqual(alert.text, 'Nieprawidłowe dane logowania')
        alert.accept()
        assert_jestem_na_stronie_logowania(self)
        self.selenium.close()

    def test_bad_password(self):
        logowanie(self, self.selenium, str_haslo='jakieś słabe hasło')
        alert = Alert(self.selenium)
        self.assertEqual(alert.text, 'Nieprawidłowe dane logowania')
        alert.accept()
        assert_jestem_na_stronie_logowania(self)
        self.selenium.close()


class ZmianaWynikow(MySeleniumTests):
    @classmethod
    def setUp(cls):
        super(ZmianaWynikow, cls).setUpClass()
        wypelnij_baze_danych()
        dodaj_uzytkownika()

    def test_wyswietlania_ekranow_dla_niezalogowanego_uzytkownika(self):
        otwieranie_strony_glownej(self, self.selenium)
        sprawdz_spojnosc_danych_na_stronie(self, self.selenium)
        przejdz_do_wojewodztwa(self.selenium)
        sprawdz_spojnosc_danych_na_stronie(self, self.selenium)
        przejdz_do_okregu(self.selenium)
        sprawdz_spojnosc_danych_na_stronie(self, self.selenium)
        przejdz_do_gminy(self.selenium)
        sprawdz_spojnosc_danych_na_stronie(self, self.selenium)
        przejdz_do_obwodu(self.selenium)
        alert = Alert(self.selenium)
        self.assertEqual(alert.text, 'Edycja dostępna jest tylko dla zalogowanych użytkowników.')
        alert.accept()
        self.selenium.close()

    def test_zmiany_w_obwodzie_dla_zalogowanego_uzytkownika(self):
        otwieranie_strony_logowania(self, self.selenium)
        logowanie(self, self.selenium)
        wyniki = pobieranie_wartosci_z_roznych_podzialow(self, self.selenium)

        przejdz_do_obwodu(self.selenium)
        wartosc_zmniejszenia = zmniejsz_wartosc(self.selenium)
        time.sleep(SLEEP_TIME)

        nowe_wyniki = pobieranie_wartosci_z_roznych_podzialow(self, self.selenium)
        for i in range(0, len(wyniki)):
            self.assertEqual(nowe_wyniki[i] + wartosc_zmniejszenia, wyniki[i])

        sprawdz_spojnosc_danych_na_stronie(self, self.selenium)
        self.selenium.close()

    def test_na_niedozwolona_zmiane(self):
        otwieranie_strony_logowania(self, self.selenium)
        logowanie(self, self.selenium)

        wartosci = pobieranie_wartosci_z_roznych_podzialow(self, self.selenium)
        przejdz_do_obwodu(self.selenium)
        zmniejsz_wartosc(self.selenium, -10000)

        time.sleep(SLEEP_TIME)
        alert = Alert(self.selenium)
        text = alert.text
        print(text)
        self.assertTrue('Suma głosów nieważnych i głosów oddanych na wszystkich kandydatów ' in text)
        self.assertTrue(' jest większa niż liczba wydanych kart ' in text)
        alert.accept()

        nowe_wartosci = pobieranie_wartosci_z_roznych_podzialow(self, self.selenium)
        self.assertEqual(wartosci, nowe_wartosci)
        self.selenium.close()


class Wyszukiwanie(MySeleniumTests):
    @classmethod
    def setUp(cls):
        super(Wyszukiwanie, cls).setUpClass()
        wypelnij_baze_danych()
        dodaj_uzytkownika()

    def wstukaj_do_wyszukania(self, gmina):
        time.sleep(SLEEP_TIME)
        gmina_input = self.selenium.find_element_by_name('szukanaGmina')
        gmina_input.send_keys(gmina)
        gmina_input.submit()

    def daj_wyniki(self):
        return self.selenium.find_elements_by_class_name('odnosnikGminaZSzukania')

    def czy_dobrze_znaleziono(self, gmina, lista):
        for i in lista:
            self.assertTrue(gmina in i.text)

    def wejdz_do_wyszukanej_gminy(self, lista, numer_na_liscie=0):
        lista[numer_na_liscie].click()
        time.sleep(SLEEP_TIME)

    def test_szukania(self):
        gmina = 'Warszawa'
        otwieranie_strony_glownej(self, self.selenium)
        self.wstukaj_do_wyszukania(gmina)
        wynik = self.daj_wyniki()
        self.czy_dobrze_znaleziono(gmina, wynik)
        self.wejdz_do_wyszukanej_gminy(wynik)
        time.sleep(SLEEP_TIME)
        tytul = self.selenium.find_element_by_id('podtytulGmina').text
        self.assertTrue(gmina in tytul)
        self.selenium.close()


def przejdz_do_formularza(klasa_test, selenium):
    selenium.get(klasa_test.live_server_url)
    time.sleep(SLEEP_TIME)
    actions = ActionChains(selenium)
    lodz = selenium.find_element_by_id("polska")
    actions.move_to_element(lodz)
    actions.click()
    actions.perform()
    time.sleep(SLEEP_TIME)

    okreg = selenium.find_element_by_link_text("Okreg 18")
    okreg.click()
    time.sleep(SLEEP_TIME)

    selenium.find_element_by_link_text("Gmina Buczek").click()
    print("jestem tu")
    time.sleep(SLEEP_TIME)
    karty = selenium.find_element_by_xpath(
        "//table[@class='statystykiObwody']/tbody[1]/tr[1]/td[3]")
    print(karty)
    print(karty.text)
    selenium.find_element_by_id("90595").click()


class Wyscig(MySeleniumTests):

    def test_wyscig(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-web-security")
        driver1 = self.selenium
        driver2 = webdriver.Chrome(chrome_options=chrome_options)
        time.sleep(SLEEP_TIME)
        logowanie(self, driver1)
        logowanie(self, driver2, 'admin', 'admin123')
        time.sleep(SLEEP_TIME)
        otwieranie_strony_glownej(self, driver1)
        otwieranie_strony_glownej(self, driver2)
        time.sleep(SLEEP_TIME)
        # przechodzę do obwodu
        przejdz_do_formularza(self, driver1)
        przejdz_do_formularza(self, driver2)
        # wpisuję dane
        sub1 = wpisz_dane(driver1, 2, 2, 1)
        sub2 = wpisz_dane(driver2, 3, 3, 2)
        time.sleep(SLEEP_TIME * 10)
        # wyślij formularz
        sub1.click()
        sub2.click()
        time.sleep(SLEEP_TIME)
        driver2.close()
        # sprawdź spójność danych
        otwieranie_strony_glownej(self, driver1)
        sprawdz_spojnosc_danych_na_stronie(self, driver1)
        przejdz_do_wojewodztwa(driver1)
        sprawdz_spojnosc_danych_na_stronie(self, driver1)
        przejdz_do_okregu(driver1)
        sprawdz_spojnosc_danych_na_stronie(self, driver1)
        przejdz_do_gminy(driver1)
        sprawdz_spojnosc_danych_na_stronie(self, driver1)
        driver1.close()


def wpisz_dane(selenium, dane1=0, dane2=0, numer_selenuim=1):
    my_input_1 = selenium.find_element_by_xpath(
        "//table[@class='wierszeFormularza']/tbody[1]/tr[" + str(numer_selenuim) + "]/td[2]/input")
    my_input_2 = selenium.find_element_by_xpath(
        "//table[@class='wierszeFormularza']/tbody[1]/tr[" + str(numer_selenuim) + "]/td[2]/input")
    my_input_1.clear()
    my_input_1.send_keys(dane1)
    my_input_2.clear()
    my_input_2.send_keys(dane2)
    return my_input_1
