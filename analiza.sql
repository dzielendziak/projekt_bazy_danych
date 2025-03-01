--Zestawienie liczby zamówień w każdym z miesięcy
SELECT TO_CHAR(data_zamowienia, 'MM-YYYY') as miesiac, COUNT(id_zamowienia) liczba_zamowien 
FROM zamowienia
GROUP BY miesiac
ORDER BY liczba_zamowien 

--Klienci bez danych kontaktowych
SELECT imie, nazwisko
FROM klienci
WHERE nr_tel IS NULL AND email IS NULL 


--Wiekowi lub mało aktywni dostawcy
WITH dlugosc_pracy AS(
    SELECT id_dostawcy, imie, nazwisko, current_date - data_zatrudnienia AS dni_zatrudnienia
    FROM dostawcy
), ilosci_zamowien AS (
    SELECT z.id_dostawcy AS id_dostawca, COUNT(z.id_zamowienia) AS liczba_zamowien
    FROM zamowienia AS z
    JOIN dostawcy AS d 
    ON z.id_dostawcy = d.id_dostawcy
    WHERE z.status_zamowienia <> 'Anulowane' 
    GROUP BY z.id_dostawcy
)
SELECT dlug.imie, dlug.nazwisko
FROM dlugosc_pracy as dlug
JOIN ilosci_zamowien AS ilosc
ON dlug.id_dostawcy = ilosc.id_dostawca
WHERE ROUND(ilosc.liczba_zamowien::decimal /dlug.dni_zatrudnienia,2) < 1
UNION
SELECT imie, nazwisko
FROM dostawcy
WHERE data_urodzenia < '1980-01-01'
    AND current_date - data_zatrudnienia > 14

--5 Najbardziej aktywnych pracownikow
WITH dlugosc_pracy AS(
    SELECT id_dostawcy, imie, nazwisko, current_date - data_zatrudnienia AS dni_zatrudnienia
    FROM dostawcy
), ilosci_zamowien AS (
    SELECT z.id_dostawcy AS id_dostawca, COUNT(z.id_zamowienia) AS liczba_zamowien
    FROM zamowienia AS z
    INNER JOIN dostawcy AS d 
    ON z.id_dostawcy = d.id_dostawcy
    WHERE z.status_zamowienia <> 'Anulowane' 
    GROUP BY z.id_dostawcy
)
SELECT dlug.imie, dlug.nazwisko, ROUND(ilosc.liczba_zamowien::decimal /dlug.dni_zatrudnienia,2) AS sred_zamowien
FROM dlugosc_pracy as dlug
JOIN ilosci_zamowien AS ilosc
ON dlug.id_dostawcy = ilosc.id_dostawca
ORDER BY sred_zamowien DESC
LIMIT 5



--Najpopularniejsze adresy dostaw
SELECT a.miasto, a.ulica, COUNT(z.id_zamowienia) AS ilosc_zamowien
FROM zamowienia As z
JOIN adresy AS a
ON z.id_adresu_zamowienia = a.id_adresu
GROUP BY a.miasto, a.ulica
ORDER BY ilosc_zamowien DESC 
LIMIT 10



--Najbardziej dochodowe restauracje
SELECT r.nazwa,
ROUND(SUM(
    CASE 
        WHEN p.waluta = 'PLN' THEN  p.kwota * (1 - (r.procent_dla_restauracji::numeric /100+ s.procent_dla_dostawcy::numeric /100))
        WHEN p.waluta = 'EUR' THEN  4.14 * p.kwota * (1 - (r.procent_dla_restauracji::numeric/100 + s.procent_dla_dostawcy::numeric /100))
    END),2) AS zysk_w_pln
FROM platnosci AS p
JOIN zamowienia AS z
ON p.id_platnosci = z.id_platnosci
JOIN restauracje AS r
ON z.id_restauracji = r.id_restauracji
JOIN stawki AS s 
ON z.id_stawki = s.id_stawki
WHERE z.status_zamowienia = 'Zrealizowane' AND p.status_platnosci = 'Zrealizowana'
GROUP BY r.nazwa
ORDER BY zysk_w_pln DESC
LIMIT 5


--Rolling income
WITH miesieczne_przychody AS(
    SELECT DATE_TRUNC('month', z.data_zamowienia) AS miesiac,
    SUM(
    CASE 
        WHEN p.waluta = 'PLN' THEN  p.kwota * (1 - (r.procent_dla_restauracji::numeric/100 + s.procent_dla_dostawcy::numeric/100))
        WHEN p.waluta = 'EUR' THEN  4.14 * p.kwota * (1 - (r.procent_dla_restauracji::numeric/100 + s.procent_dla_dostawcy::numeric/100))
    END) AS przychod_w_pln
    FROM platnosci AS p
    JOIN zamowienia AS z
    ON p.id_platnosci = z.id_platnosci
    JOIN restauracje AS r
    ON z.id_restauracji = r.id_restauracji
    JOIN stawki AS s 
    ON z.id_stawki = s.id_stawki
    WHERE z.status_zamowienia = 'Zrealizowane' AND p.status_platnosci = 'Zrealizowana'
    GROUP BY miesiac
)
SELECT TO_CHAR(m.miesiac, 'MM-YYYY') AS miesiac, 
ROUND(SUM(przychod_w_pln) OVER(PARTITION BY miesiac ORDER BY m.miesiac),2) AS rolling_income_zl
FROM miesieczne_przychody AS m 


--Najgorzej oceniane restauracje
SELECT r.nazwa, ROUND(AVG(o.ocena_jedzenia), 2) AS sred_ocen
FROM zamowienia AS z
JOIN oceny AS o   
ON z.id_zamowienia = o.id_zamowienia
JOIN restauracje AS r
ON z.id_restauracji = r.id_restauracji
GROUP BY r.nazwa
ORDER BY sred_ocen ASC
LIMIT 3

--Najlepiej oceniani dostawcy
WITH oceny_dostawcow AS(
    SELECT z.id_dostawcy, ROUND(AVG(o.ocena_dostawy), 2) AS sred_ocen
    FROM zamowienia AS z
    JOIN oceny AS o   
    ON z.id_zamowienia = o.id_zamowienia
    GROUP BY z.id_dostawcy
    HAVING COUNT(z.id_dostawcy) >= 10
    ORDER BY sred_ocen DESC
    LIMIT 3
) 
SELECT CONCAT(d.imie, ' ', d.nazwisko), o.sred_ocen
FROM oceny_dostawcow AS o 
JOIN dostawcy AS d 
ON o.id_dostawcy = d.id_dostawcy


--Rozkład procentowy zamówień dla każdej z kuchni
WITH suma_zam AS(
    SELECT COUNT(id_zamowienia) AS suma
    FROM zamowienia
    WHERE status_zamowienia = 'Zrealizowane'
)
SELECT
CONCAT(r.kategoria,' (',ROUND((COUNT(id_zamowienia) / (SELECT suma FROM suma_zam)::numeric) * 100, 2), '%)') AS procent_zamowien, COUNT(id_zamowienia) AS ilosc_zamowien
FROM zamowienia AS z
JOIN restauracje AS r  
ON z.id_restauracji = r.id_restauracji
GROUP BY r.kategoria
ORDER BY ilosc_zamowien DESC
LIMIT 5

-- 5 najmniej opłacalnych pojazdów
WITH koszty_napraw AS(
    SELECT id_pojazdu, SUM(koszt_naprawy_zl) suma_kosztow
    FROM serwis_sprzetu
    GROUP BY id_pojazdu
),
ilosc_zamowien AS(
    SELECT id_pojazdu, COUNT(id_zamowienia) suma_zam
    FROM zamowienia
    GROUP BY id_pojazdu
)
SELECT p.rodzaj_pojazdu, p.id_pojazdu, 
CONCAT(ROUND(k.suma_kosztow/il.suma_zam::numeric,2),' zl') AS koszt_na_zamowienie
FROM pojazdy AS p
RIGHT JOIN koszty_napraw AS k 
ON p.id_pojazdu = k.id_pojazdu
JOIN ilosc_zamowien AS il
ON p.id_pojazdu = il.id_pojazdu
ORDER BY koszt_na_zamowienie DESC
LIMIT 5

--Zamówienia, które przyjechały
SELECT CONCAT(d.imie, ' ', d.nazwisko) dostawca, r.nazwa restauracja, COUNT(o.id_oceny) zimne_posilki
FROM oceny AS o
JOIN zamowienia AS z 
ON o.id_zamowienia = z.id_zamowienia
JOIN restauracje AS r 
ON z.id_restauracji = r.id_restauracji
JOIN dostawcy AS d 
ON z.id_dostawcy = d.id_dostawcy
WHERE LOWER(o.opis) LIKE '%zimn%'
GROUP BY dostawca, r.nazwa








