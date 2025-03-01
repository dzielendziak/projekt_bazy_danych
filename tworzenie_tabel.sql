CREATE TABLE adresy (
  id_adresu SERIAL PRIMARY KEY,
  miasto VARCHAR(50),
  ulica VARCHAR(50),
  numer_domu VARCHAR(50),
  kod_pocztowy VARCHAR(6)
);

CREATE TABLE restauracje (
  id_restauracji SERIAL PRIMARY KEY,
  nazwa VARCHAR(255),
  id_adresu INTEGER REFERENCES adresy(id_adresu),
  kategoria VARCHAR(255),
  procent_dla_restauracji INTEGER CHECK (procent_dla_restauracji BETWEEN 1 AND 100)
);

CREATE TABLE klienci (
  id_klienta SERIAL PRIMARY KEY,
  imie VARCHAR(50) NOT NULL,
  nazwisko VARCHAR(50) NOT NULL,
  nr_tel VARCHAR(20) UNIQUE,
  email VARCHAR(50) UNIQUE,
  konto_od DATE NOT NULL
);


CREATE TABLE pojazdy (
  id_pojazdu SERIAL PRIMARY KEY,
  rodzaj_pojazdu VARCHAR(50) NOT NULL
);

CREATE TABLE dostawcy (
  id_dostawcy SERIAL PRIMARY KEY,
  imie VARCHAR(50) NOT NULL,
  nazwisko VARCHAR(50) NOT NULL,
  data_urodzenia DATE NOT NULL,
  nr_tel VARCHAR(20) UNIQUE NOT NULL,
  email VARCHAR(50) UNIQUE NOT NULL,
  data_zatrudnienia DATE NOT NULL
);

CREATE TABLE platnosci (
  id_platnosci SERIAL PRIMARY KEY,
  metoda_platnosci VARCHAR(50) NOT NULL,
  kwota NUMERIC(10,2) NOT NULL,
  waluta VARCHAR(3) NOT NULL,
  status_platnosci VARCHAR(50) NOT NULL
);

CREATE TABLE serwis_sprzetu (
  id_serwisu SERIAL PRIMARY KEY,
  id_pojazdu INTEGER NOT NULL REFERENCES pojazdy(id_pojazdu),
  rodzaj_naprawy VARCHAR(50) NOT NULL,
  koszt_naprawy_zl NUMERIC(10,2) NOT NULL,
  data_naprawy DATE NOT NULL
);

CREATE TABLE stawki (
  id_stawki SERIAL PRIMARY KEY,
  nazwa_stawki VARCHAR(50) NOT NULL,
  opis VARCHAR(255) NOT NULL,
  procent_dla_dostawcy INTEGER CHECK (procent_dla_dostawcy BETWEEN 1 AND 100)
);


CREATE TABLE zamowienia (
  id_zamowienia SERIAL PRIMARY KEY,
  id_klienta INTEGER NOT NULL REFERENCES klienci(id_klienta),
  id_dostawcy INTEGER NOT NULL REFERENCES dostawcy(id_dostawcy),
  id_adresu_zamowienia INTEGER NOT NULL REFERENCES adresy(id_adresu),
  id_pojazdu INTEGER NOT NULL REFERENCES pojazdy(id_pojazdu),
  id_restauracji INTEGER NOT NULL REFERENCES restauracje(id_restauracji),
  data_zamowienia TIMESTAMP NOT NULL,
  id_platnosci INTEGER NOT NULL REFERENCES platnosci(id_platnosci),
  status_zamowienia VARCHAR(50) NOT NULL,
  id_stawki INTEGER NOT NULL REFERENCES stawki(id_stawki)
);

CREATE TABLE oceny (
  id_oceny SERIAL PRIMARY KEY,
  id_zamowienia INTEGER REFERENCES zamowienia(id_zamowienia),
  ocena_jedzenia INTEGER CHECK (ocena_jedzenia BETWEEN 1 AND 5),
  ocena_dostawy INTEGER CHECK (ocena_dostawy BETWEEN 1 AND 5),
  opis VARCHAR(255)
);

--Trigger, który przy każdym nowym pojeździe wpisanym do bazy automatycznie wprowadza też jego przegląd techniczny
CREATE FUNCTION nowy_przeglad_techniczny()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO serwis_sprzetu (id_pojazdu, rodzaj_naprawy, koszt_naprawy_zl, data_naprawy)
  VALUES (NEW.id_pojazdu, 'Przegląd techniczny', 200, CURRENT_DATE);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER przeglady_techniczne
AFTER INSERT ON pojazdy
FOR EACH ROW
EXECUTE FUNCTION nowy_przeglad_techniczny();

















