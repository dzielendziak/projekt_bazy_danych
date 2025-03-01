import random
from datetime import datetime, timedelta
from faker import Faker
import psycopg2

fake = Faker("pl_PL")

# Połączenie z bazą danych
conn = psycopg2.connect(
    dbname="smaczne",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Lista miast - głównie Wrocław, ale z kilkoma okolicznymi miejscowościami
miasta_wroclaw = ["Wrocław"] * 25 + ["Iwiny", "Łany", "Wysoka", "Bielany Wrocławskie"]

# Lista restauracji i ich kategorii
restauracje_lista = [
    ("Pizzeria Napoli", "Kuchnia włoska"),
    ("Sushi Master", "Kuchnia japońska"),
    ("Burger House", "Kuchnia amerykańska"),
    ("Pierogi Babci", "Kuchnia polska"),
    ("Chińska Perła", "Kuchnia chińska"),
    ("Kebab King", "Kuchnia turecka"),
    ("Steak & Grill", "Kuchnia amerykańska"),
    ("Włoska Uczta", "Kuchnia włoska"),
    ("Wege Zielarnia", "Kuchnia wegetariańska"),
    ("Tajski Smak", "Kuchnia tajska"),
    ("Meksykańska Fiesta", "Kuchnia meksykańska"),
    ("Francuski Zakątek", "Kuchnia francuska"),
    ("Indyjska Przygoda", "Kuchnia indyjska"),
    ("Grecka Tawerna", "Kuchnia grecka"),
    ("Orient Express", "Kuchnia azjatycka"),
    ("Hiszpańska Paella", "Kuchnia hiszpańska"),
    ("Bistro Provence", "Kuchnia francuska"),
    ("Nowojorska Deli", "Kuchnia amerykańska"),
    ("Seul Street Food", "Kuchnia koreańska"),
    ("Smaki Wietnamu", "Kuchnia wietnamska"),
    ("Domowe Smaki", "Kuchnia polska"),
    ("Neapolitańska Pizza", "Kuchnia włoska"),
    ("Bar Baryłka", "Kuchnia polska"),
    ("Podhalańska Chata", "Kuchnia góralska"),
    ("Fińska Laguna", "Kuchnia skandynawska"),
    ("Hawajska Fala", "Kuchnia hawajska"),
    ("Balkan Grill", "Kuchnia bałkańska"),
    ("Szwajcarski Fondue", "Kuchnia szwajcarska"),
    ("Gruzja Smaku", "Kuchnia gruzińska"),
    ("Argentyński Stek", "Kuchnia argentyńska")
]

# Funkcja do generowania adresów
def insert_adresy(n=5000):
    adresy = []
    for _ in range(n):
        miasto = random.choice(miasta_wroclaw)
        ulica = fake.street_name()
        numer_domu = str(random.randint(1, 100))
        kod_pocztowy = str(random.randint(54,56))+'-'+str(random.randint(100,999))
        cursor.execute(
            "INSERT INTO adresy (miasto, ulica, numer_domu, kod_pocztowy) VALUES (%s, %s, %s, %s) RETURNING id_adresu",
            (miasto, ulica, numer_domu, kod_pocztowy)
        )
        adresy.append(cursor.fetchone()[0])
    return adresy

# Funkcja do generowania restauracji
def insert_restauracje(adresy, n=30):
    restauracje = []
    for i in range(n):
        nazwa, kategoria = restauracje_lista[i]
        id_adres = random.choice(adresy)
        procenty = random.choice([65, 70, 72])
        cursor.execute(
            "INSERT INTO restauracje (nazwa, id_adresu, kategoria, procent_dla_restauracji) VALUES (%s, %s, %s, %s) RETURNING id_restauracji",
            (nazwa, id_adres, kategoria, procenty)
        )
        restauracje.append(cursor.fetchone()[0])
    return restauracje

# Funkcja do generowania klientów
def insert_klienci(n=4500):
    klienci = []
    for _ in range(n):
        imie = fake.first_name()
        nazwisko = fake.last_name()
        nr_tel = fake.phone_number() if random.random() > 0.1 else None
        email = imie.lower()+random.choice(['.','_',''])+nazwisko.lower()+str(random.randint(0,999))+'@example.com' if random.random() > 0.1 else None
        konto_od = fake.date_between(start_date="-1y", end_date="-2d")
        cursor.execute(
            "INSERT INTO klienci (imie, nazwisko, nr_tel, email, konto_od) VALUES (%s, %s, %s, %s, %s) RETURNING id_klienta",
            (imie, nazwisko, nr_tel, email, konto_od)
        )
        klienci.append(cursor.fetchone()[0])
    return klienci

# Funkcja do generowania dostawców
def insert_dostawcy(n=50):
    dostawcy = []
    for _ in range(n):
        imie = fake.first_name()
        nazwisko = fake.last_name()
        data_urodzenia = fake.date_of_birth(minimum_age=18, maximum_age=50)
        nr_tel = fake.phone_number()
        email = imie.lower()+random.choice(['.','_',''])+nazwisko.lower()+str(random.randint(0,999))+'@smaczne.pl'
        data_zatrudnienia = fake.date_between(start_date="-1y", end_date="-10w")
        cursor.execute(
            "INSERT INTO dostawcy (imie, nazwisko, data_urodzenia, nr_tel, email, data_zatrudnienia) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_dostawcy",
            (imie, nazwisko, data_urodzenia, nr_tel, email, data_zatrudnienia)
        )
        dostawcy.append(cursor.fetchone()[0])
    return dostawcy

# Funkcja do generowania zamówień
def insert_zamowienia(klienci, dostawcy, restauracje, adresy, platnosci, pojazdy, klienci_daty, dostawcy_daty, n):
    zamowienia = []
    for _ in range(n):
        id_klient = random.choice(klienci)
        id_dostawca = random.choice(dostawcy)
        id_restauracja = random.choice(restauracje)
        id_adres = random.choice(adresy)
        id_platnosci = random.choice(platnosci)
        id_pojazd = random.choice(pojazdy)

        # Pobranie minimalnej daty dla zamówienia (najpóźniejsza z dwóch dat)
        min_data_zamowienia = max(klienci_daty[id_klient], dostawcy_daty[id_dostawca])
        
        # Losowanie daty zamówienia z ograniczeniem czasowym i datowym
        while True:
            data_zamowienia = fake.date_time_between(start_date=min_data_zamowienia, end_date="now")
            godzina_zamowienia = data_zamowienia.hour
            if godzina_zamowienia >= 10 or godzina_zamowienia < 2:
                break  # Akceptujemy tylko godziny 10:00 - 01:59

        if godzina_zamowienia >= 22 or godzina_zamowienia < 2:
            # Stawka nocna (Wyższa)
            id_stawka = 3
        else:
            # Stawka standardowa
            id_stawka = str(random.randint(1,2))
        status_zamowienia =  "Zrealizowane" if random.random() < 0.98 else random.choice(["Anulowane", "W trakcie"])
        cursor.execute(
            "INSERT INTO zamowienia (id_klienta, id_dostawcy, id_adresu_zamowienia, id_pojazdu, id_restauracji, data_zamowienia, id_platnosci, status_zamowienia, id_stawki) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_zamowienia",
            (id_klient, id_dostawca, id_adres, id_pojazd, id_restauracja, data_zamowienia, id_platnosci, status_zamowienia, id_stawka)
        )
        zamowienia.append(cursor.fetchone()[0])
    return zamowienia

# Funkcja do generowania ocen
def insert_oceny(zamowienia, n=970):
    for _ in range(n):
        id_zamowienia = random.choice(zamowienia)
        ocena_jedzenia = random.randint(1, 5)
        ocena_zamowienia = random.randint(1, 5)
        opis = fake.sentence()
        cursor.execute(
            "INSERT INTO oceny (id_zamowienia, ocena_jedzenia, ocena_dostawy, opis) VALUES (%s, %s, %s, %s)",
            (id_zamowienia, ocena_jedzenia, ocena_zamowienia, opis)
        )

# Funkcja do generowania serwisu sprzętu
def insert_serwis(pojazdy, n=23):
    for _ in range(n):
        id_pojazd = random.choice(pojazdy)
        rodzaj_naprawy = random.choice(["Wymiana opony", "Naprawa silnika", "Przegląd techniczny"])
        koszt_naprawy = round(random.uniform(50, 500), 2)
        data_naprawy = fake.date_time_between(start_date="-26w", end_date="now")
        cursor.execute(
            "INSERT INTO serwis_sprzetu (id_pojazdu, rodzaj_naprawy, koszt_naprawy_zl, data_naprawy) VALUES (%s, %s, %s, %s)",
            (id_pojazd, rodzaj_naprawy, koszt_naprawy, data_naprawy)
        )

# Funkcja do generowania płatności
def insert_platnosci(n=10000):
    platnosci = []
    metody = ["Karta", "Gotówka", "Blik"]
    for _ in range(n):
        metoda_platnosci = random.choice(metody)
        kwota = round(random.uniform(20, 200), 2)
        waluta = "PLN" if random.random() < 0.95 else "EUR"
        status_platnosci = "Zrealizowana" if random.random() < 0.99 else "Nieudana"
        cursor.execute(
            "INSERT INTO platnosci (metoda_platnosci, kwota, waluta, status_platnosci) VALUES (%s, %s, %s, %s) RETURNING id_platnosci",
            (metoda_platnosci, kwota, waluta, status_platnosci)
        )
        platnosci.append(cursor.fetchone()[0])
    return platnosci

# Funkcja do generowania stawek
def insert_stawki():
    stawki = [
        ("Podstawowa", "Standardowa stawka", 10),
        ("Premium", "Wyższa stawka dla aktywnych", 20),
        ("Specjalna", "Stawka dla nocnych dostaw", 18)
    ]
    for nazwa, opis, procent in stawki:
        cursor.execute(
            "INSERT INTO stawki (nazwa_stawki, opis, procent_dla_dostawcy) VALUES (%s, %s, %s) RETURNING id_stawki",
            (nazwa, opis, procent)
        )

# Funkcja do generowania pojazdów
def insert_pojazdy(n=30):
    pojazdy = []
    rodzaje_pojazdow = ["Skuter", "Samochód", "Rower"]
    for _ in range(n):
        rodzaj_pojazdu = random.choice(rodzaje_pojazdow)
        cursor.execute(
            "INSERT INTO pojazdy (rodzaj_pojazdu) VALUES (%s) RETURNING id_pojazdu",
            (rodzaj_pojazdu,)
        )
        pojazdy.append(cursor.fetchone()[0])
    return pojazdy

def get_klienci_daty():
    cursor.execute("SELECT id_klienta, konto_od FROM klienci")
    return {row[0]: row[1] for row in cursor.fetchall()}

def get_dostawcy_daty():
    cursor.execute("SELECT id_dostawcy, data_zatrudnienia FROM dostawcy")
    return {row[0]: row[1] for row in cursor.fetchall()}


# Główna funkcja do wykonania wstawień
def main():
    adresy = insert_adresy()
    restauracje = insert_restauracje(adresy)
    klienci = insert_klienci()
    dostawcy = insert_dostawcy()
    platnosci = insert_platnosci()
    pojazdy = insert_pojazdy()
    insert_stawki()
    klienci_daty = get_klienci_daty()
    dostawcy_daty = get_dostawcy_daty()

    zamowienia = insert_zamowienia(klienci, dostawcy, restauracje, adresy, platnosci, pojazdy, klienci_daty, dostawcy_daty, 10000)

    insert_oceny(zamowienia)
    insert_serwis(pojazdy)
    conn.commit()
    print("Dane zostały poprawnie dodane do bazy!")

if __name__ == "__main__":
    main()
    cursor.close()
    conn.close()
