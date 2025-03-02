# Projekt: Baza danych dla fikcyjnej firmy smaczne.pl realizującej dowóz jedzenia na terenie Wrocławia i okolic

## Opis projektu

Najważniejsze założenia działania firmy smaczne.pl:
- Firma obsługuje 30 restauracji na terenie Wrocławia i okolicznych wiosek. Działa od 12 miesięcy.
- Zatrudnia obecnie 50 dostawców.
- Dostawy to osobny dział firmy, dlatego pracownicy marketingu lub innych działów nie są uwzględnieni w bazie danych.
- Flota pojazdów obejmuje w sumie 50 rowerów, skuterów i samochodów. Pracownicy dowożą tylko na służbowych pojazdach.
- Smaczne.pl dzieli się zyskami z każdego zamówienia z restauracją i dostawcą po określonej stawce procentowej. Jest to jedyny sposób na zarobek dla dostawców, nie ma stawki kilometrowej lub stałej stawki godzinowej. Zarobki kurierów różnią się w zależności od godzin (stawka nocna) lub aktywności.
- Koszty serwisu również podjegają działowi dostaw.
- Każdy klient po otrzymaniu zamówienia może wystawić ocene restauracji i ocene dostawcy (w skali 1-5).
- Pojazd nie jest przypisany do dostawcy, każdy z nich ma prawo jazdy i pracuje na pojeździe, który akurat dostępny jest w magazynie.
- Czas zamówienia jest równy czasowi zrealizowania płatności internetowej lub płatności przy odbiorze dostawy.
- Zamówienia mogą być opłacane w PLN lub EUR, kurs Euro używany w tym projekcie wynosi 4,14zł.

Część techniczna projektu zawiera zestaw zaawansowanych zapytań SQL, które pozwalają na:
- Analizę liczby zamówień w poszczególnych miesiącach.
- Wyszukiwanie klientów bez danych kontaktowych.
- Identyfikację najmniej aktywnych oraz najstarszych dostawców.
- Ranking najbardziej aktywnych pracowników.
- Analizę najpopularniejszych adresów dostaw.
- Obliczenie najbardziej dochodowych restauracji.
- Wyliczenie sumarycznego dochodu firmy dla każdego z miesięcy.
- Ranking najgorzej ocenianych restauracji.
- Identyfikację najlepiej ocenianych dostawców.
- Analizę procentowego rozkładu zamówień na kategorie kuchni.
- Wyszukiwanie najmniej opłacalnych w utrzymaniu pojazdów.
- Wykrywanie dostaw, które nie spełniły standardów firmy.

Dodatkowo projekt zawiera narzędzia do generowania danych testowych oraz raportu, co pozwala na symulację rzeczywistych warunków i analizę wyników. 

## Struktura projektu - pliki
- **tworzenie_tabel.sql** - Funkcje tworzące tabele w SQL oraz trigger używany przy zakupie nowych pojazdów.
- **wypelnianie_bazy.py** - Skrypt Python wypełniający bazę danych sztucznymi danymi. 
- **analiza.sql** - Zbiór zapytań SQL do analizy danych, używany później w raporcie.
- **raport.py** - Skrypt Python generujący raport w formacie PDF.
- **README.md** - Dokumentacja projektu, opis jego funkcjonalności i sposób użycia.
- **schemat_bazy.png** - Wizualne przedstawienie relacji w bazie danych.
- **Nunito-Light.ttf**  - Font używany w raporcie.

## Technologia
Projekt wykorzystuje:
- **PostgreSQL** - Relacyjna baza danych, obsługująca zaawansowane operacje analityczne.
- **PL/pgSQL** - Proceduralny język SQL używany do tworzenia funkcji i triggerów.
- **Python** - Skrypty Python wspomagające generowanie danych oraz tworzenie raportów w formacie PDF.
- **Pandas** - Biblioteka Python do analizy danych i ich przekształcania.
- **Matplotlib** - Wizualizacja wyników analiz.
- **reportLab** - Tworzenie raportów w PDF.
- **Faker** - Generowanie sztucznych danych w Python.

## Uruchomienie
Pliki w kolejności wymaganej do uzyskania gotowego projektu:
1. **tworzenie_tabel.sql**
2. **wypelnianie_bazy.py**
3. **raport.py**

Po tych krokach dostępny będzie plik raport.pdf z wykresami i tabelami pozwalającymi na analizę działania firmy.

## Motywacje autora
Projekt powstał z potrzeby nauki języka SQL i jego praktycznych zastosowań, a w szczególności projektowania bazy danych i formułowania złożonych zapytań. Insipracją do stworzenia takiej bazy był bardzo podobny w swoich założeniach projekt wieńczący kurs Baz Danych na trzecim semestrze Matematyki Stosowanej na temat firmy wycieczkowej, który miałem przyjemność tworzyć z dwójką innych studentów. Wtedy jednak nie udało mi się zagłębić we wszystkie aspekty tworzenia bazy danych od podstaw, stąd pomysł żeby po dwóch miesiącach zrobić to samemu i użyć bardziej zaawansowanych zapytań.
