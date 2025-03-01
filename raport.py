
import psycopg2
import os
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle



#Próba połączenia z bazą danych

conn = psycopg2.connect(
    dbname="smaczne",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)


#Utworzenie kursora do wykonywania zapytań
cur = conn.cursor()

#Funkcja generująca wykres słupkowy i zapisująca go jako obraz
def wykres_slupkowy(x, y, title, xlabel, ylabel, filename, colors=None):
    plt.figure(figsize=(10, 6))
    plt.bar(x, y, color=colors, alpha=0.8)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


#Funkcja generująca wykres liniowy
def wykres_liniowy(x, y, title, xlabel, ylabel, filename):
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, marker='o', alpha=0.8)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.grid()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def tabela(data, column_names, filename):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')
    
    # Tworzymy tabelę z danymi
    table = ax.table(cellText=data, colLabels=column_names, loc='center', cellLoc='center', colLoc='center')
    
    # Zapisujemy tabelę jako plik PNG
    plt.savefig(filename, bbox_inches='tight', pad_inches=0.05)
    plt.close()

#Zapytania:

#Zestawienie liczby zamówień dla poszczególnych miesięcy
cur.execute("""
    SELECT TO_CHAR(data_zamowienia, 'MM-YYYY') as miesiac, COUNT(id_zamowienia) liczba_zamowien 
    FROM zamowienia
    GROUP BY miesiac
    ORDER BY liczba_zamowien;
""")
zestawienie_zamowien = cur.fetchall()
miesiace = [row[0] for row in zestawienie_zamowien]
liczba_zamowien = [row[1] for row in zestawienie_zamowien]
wykres_liniowy(
    miesiace,
    liczba_zamowien,
    "Zestawienie liczby zamówień dla poszczególnych miesięcy",
    "Miesiąc",
    "Liczba zamowień",
    "zestawienie_zamowien.png",
)

#Zestawienie średniej zamówień najbardziej aktywnych pracowników
cur.execute("""
WITH dlugosc_pracy AS(
    SELECT id_dostawcy, imie, nazwisko, current_date - data_zatrudnienia AS dni_zatrudnienia
    FROM dostawcy
    WHERE current_date - data_zatrudnienia > 10
), 
ilosci_zamowien AS (
    SELECT z.id_dostawcy AS id_dostawca, COUNT(z.id_zamowienia) AS liczba_zamowien
    FROM zamowienia AS z
    INNER JOIN dostawcy AS d 
    ON z.id_dostawcy = d.id_dostawcy
    WHERE z.status_zamowienia <> 'Anulowane' 
    GROUP BY z.id_dostawcy
)
SELECT CONCAT(dlug.imie,' ', dlug.nazwisko) AS imie_i_nazwisko, ROUND(ilosc.liczba_zamowien::decimal /dlug.dni_zatrudnienia,2) AS sred_zamowien
FROM dlugosc_pracy as dlug
JOIN ilosci_zamowien AS ilosc
ON dlug.id_dostawcy = ilosc.id_dostawca
ORDER BY sred_zamowien DESC
LIMIT 5
""")
pracownicy = cur.fetchall()
imiona = [row[0] for row in pracownicy]
sred_zamowien = [row[1] for row in pracownicy]

wykres_slupkowy(
    imiona,
    sred_zamowien,
    "Zestawienie średniej zamówień najbardziej aktywnych pracowników",
    "Pracownik",
    "Liczba zamowień",
    "zestawienie_pracowników.png",
    colors=["#632DA6"]
)

#Zestawienie adresów na które najczęściej dostarczano zamówienia
cur.execute("""
SELECT CONCAT(a.miasto, ', ul. ', a.ulica), COUNT(z.id_zamowienia) AS ilosc_zamowien
FROM zamowienia As z
JOIN adresy AS a
ON z.id_adresu_zamowienia = a.id_adresu
GROUP BY a.miasto, a.ulica
ORDER BY ilosc_zamowien DESC 
LIMIT 10
""")
zestawienie_adresy = cur.fetchall()
adresy = [row[0] for row in zestawienie_adresy]
zamowienia_na_adres = [row[1] for row in zestawienie_adresy]

wykres_slupkowy(
    adresy,
    zamowienia_na_adres,
    "Zestawienie adresów na które najczęściej dostarczano zamówienia",
    "Adres",
    "Liczba zamowień",
    "zestawienie_adresow.png",
    colors=["#632DA6"]
)

#Zestawienie dochodów firmy z poszczególnych restauracji
cur.execute("""
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
""")

zestawienie_dochodow_restauracje = cur.fetchall()
nazwy_restauracji = [row[0] for row in zestawienie_dochodow_restauracje]
dochody_restauracje = [row[1] for row in zestawienie_dochodow_restauracje]

wykres_slupkowy(
    nazwy_restauracji,
    dochody_restauracje,
    "Zestawienie przychodów firmy z dostaw z poszczególnych restauracji",
    "Nazwa Restauracji",
    "Przychód w PLN",
    "zestawienie_dochodow_restauracji.png",
    colors=["#632DA6"]
)

#Sumaryczny dochód firmy przez kolejne miesiące
cur.execute("""
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
""")

sumaryczne_dochody = cur.fetchall()
miesiace = [row[0] for row in sumaryczne_dochody]
wartosci_dochodu = [row[1] for row in sumaryczne_dochody]

wykres_liniowy(
    miesiace,
    wartosci_dochodu,
    "Sumaryczny przychód firmy przez kolejne miesiące",
    "Miesiąc",
    "Przychód w PLN",
    "sumaryczne_przychody.png"
)



#Trzy najgorzej oceniane restauracje
cur.execute("""
SELECT r.nazwa, ROUND(AVG(o.ocena_jedzenia), 2) AS sred_ocen
FROM zamowienia AS z
JOIN oceny AS o   
ON z.id_zamowienia = o.id_zamowienia
JOIN restauracje AS r
ON z.id_restauracji = r.id_restauracji
GROUP BY r.nazwa
ORDER BY sred_ocen ASC
LIMIT 3
""")

oceny_restauracji = cur.fetchall()
nazwy_restauracji = [row[0] for row in oceny_restauracji]
wartosci_ocen = [row[1] for row in oceny_restauracji]

wykres_slupkowy(
    nazwy_restauracji,
    wartosci_ocen,
    "Trzy najgorzej oceniane restauracje",
    "Nazwa Restauracji",
    "Średnia ocen",
    "zestawienie_ocen_restauracji.png",
    colors=["#632DA6"]
)


#Trzej najlepiej oceniani dostawcy
cur.execute("""
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
""")

oceny_dostawcow = cur.fetchall()
imiona_dostawcow = [row[0] for row in oceny_dostawcow]
wartosci_ocen = [row[1] for row in oceny_dostawcow]

wykres_slupkowy(
    imiona_dostawcow,
    wartosci_ocen,
    "Trzej najlepiej oceniani dostawcy",
    "Imię i Nazwisko",
    "Średnia ocen",
    "zestawienie_ocen_dostawcow.png",
    colors=["#632DA6"]
)

#Pięć najpopularniejszych rodzajów kuchni
cur.execute("""
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
""")

rozklad_kategorii = cur.fetchall()
rodzaje_kuchni = [row[0] for row in rozklad_kategorii]
ilosci_zamowien = [row[1] for row in rozklad_kategorii]

wykres_slupkowy(
    rodzaje_kuchni,
    ilosci_zamowien,
    "Pięć najpopularniejszych rodzajów kuchni",
    "Kategoria (% we wszystkich zamówieniach)",
    "Liczba zamówień",
    "zestawienie_kuchni.png",
    colors=["#632DA6"]
)

#Pięć najmniej opłacalnych pojazdów
cur.execute("""
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
SELECT CONCAT(p.rodzaj_pojazdu, ' ', p.id_pojazdu), 
ROUND(k.suma_kosztow/il.suma_zam::numeric,2) AS koszt_na_zamowienie_zl
FROM pojazdy AS p
RIGHT JOIN koszty_napraw AS k 
ON p.id_pojazdu = k.id_pojazdu
JOIN ilosc_zamowien AS il
ON p.id_pojazdu = il.id_pojazdu
ORDER BY koszt_na_zamowienie_zl DESC
LIMIT 5
""")

naprawy = cur.fetchall()
pojazdy = [row[0] for row in naprawy]
zl_na_wyjazd = [row[1] for row in naprawy]

wykres_slupkowy(
    pojazdy,
    zl_na_wyjazd,
    "Pięć najmniej opłacalnych pojazdów",
    "Pojazd",
    "Średni koszt naprawy na dostawe w PLN",
    "zestawienie_pojazdow.png",
    colors=["#632DA6"]
)


#Mało aktywni lub wiekowi pracownicy
cur.execute("""
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
WHERE ROUND(ilosc.liczba_zamowien::decimal /dlug.dni_zatrudnienia,2) < 0.5
UNION
SELECT imie, nazwisko
FROM dostawcy
WHERE data_urodzenia < '1980-01-01'
    AND current_date - data_zatrudnienia > 14
""")
pracownicy = cur.fetchall()

# Kolumny tabeli
column_names = ['Imię', 'Nazwisko']
tabela(pracownicy, column_names, 'malo_aktywni_wiekowi.png')

#Zamówienia, które przyjechały zimne
cur.execute("""
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
""")
zimne = cur.fetchall()

column_names = ['Dostawca', 'Restauracja', 'Liczba zimnych posiłków']
tabela(zimne, column_names, 'zimne_jedzenie.png')



#Zamknięcie połączenia z bazą danych
cur.close()
conn.close()


project_folder = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(project_folder, 'Nunito-Light.ttf')

# Rejestracja czcionki, jeśli plik istnieje
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('Nunito-Light', font_path))
    font_name = "Nunito-Light"
else:
    raise FileNotFoundError(f"Nunito-Light.ttf nie została znaleziona w: {font_path}")


#Przygotowanie pliku PDF z wykresami
#Uzyskujemy absolutną ścieżkę do folderu projektu
pdf_file = "raport.pdf"
c = canvas.Canvas(pdf_file, pagesize=letter)

# Lista sekcji do raportu PDF
sekcje = [
    ("Liczba zamówień w poszczególnych miesiącach", "zestawienie_zamowien.png"),
    ("Najbardziej aktywni pracownicy", "zestawienie_pracowników.png"),
    ("Adresy z największą ilością zamówień", "zestawienie_adresow.png"),
    ("Zestawienie kuchni świata", "zestawienie_kuchni.png"),
    ("Przychody z restauracji", "zestawienie_dochodow_restauracji.png"),
    ("Sumaryczne przychody", "sumaryczne_przychody.png"),
    ("Oceny restauracji", "zestawienie_ocen_restauracji.png"),
    ("Oceny dostawców", "zestawienie_ocen_dostawcow.png"),
    ("Zamówienia, w których jedzenie było zimne", "zimne_jedzenie.png"),
    ("Mało aktywni lub wiekowi pracownicy", "malo_aktywni_wiekowi.png"),
    ("Najbardziej kosztowne pojazdy", "zestawienie_pojazdow.png")
]

# Opisy do wszystkich zapytań
opisy = {
    "Liczba zamówień w poszczególnych miesiącach": (
        '''
        Firma prężnie się rozwija i w każdym kolejnym miesiącu obsługuje więcej zamówień. Umożliwiają to stale zatrudniani nowi dostawcy
        oraz dział marketingu, który odpowiada za skuteczną promocję. W następnych miesiącach można spodziewać się dalszego wzrostu zamówień.
        '''
    ),

    "Najbardziej aktywni pracownicy": (
        '''
        Spośród najbardziej aktywnych pracowników wyróżnia się Elżbieta Pasieczna notująca średnio ponad 2.5 zrealizowanych zamówień dziennie.
        Powyżej granicy dwóch zamówień dziennie znaleźli się również Tomasz Trepczyk i Bartosz Nabiałek. Należy zaznaczyć, że w przygotowanym 
        zestawieniu są brani pod uwagę tylko pracownicy, którzy są zatrudnieni więcej niż 10 dni. Ma to na celu zapobiec
        analizowaniu danych z bardzo
        małych próbek czasowych, które mogłyby zaburzać obraz sytuacji.
        '''
    ),

    "Adresy z największą ilością zamówień" : (
        '''
        Wykres przedstawia ulice, na które klienci firmy najczęściej klienci zamawiali jedzenie. Numerem jeden jest ulica Zwycięstwa
        we Wrocławiu na którą dowożono 56 razy. Dane z zestawienia są bardzo wyrównane co sugeruje, że firma jest równie rozpoznawalna
        przez klientów z różnych części miasta i powinna konsekwentnie zatrudniać nowych dostawców.
        '''
    ),

    "Przychody z restauracji" : (
        '''
        W zestawieniu przedstawiono 30 restauracji, z którymi współpracowała nasza firma. Najbardziej opłacalna dotychczas
        okazała się współpraca z restauracją Tajski Smak, która przyniosła ponad 8000 zł przychohodu. Najmniej zarobiliśmy
        na realizacji zamówień z Gruzji Smaku.
        '''
    ),

    "Sumaryczne przychody": (
        '''
        Powyższy wykres przedstawia sumę przychodów od pierwszego dnia podczas kolejnych miesięcy działania firmy.
        Wpływający kapitał rośnie nieliniowo co jest ściśle powiązane z rosnącą ilością zamówień przedstawioną wcześniej w raporcie.
        '''
    ),

    "Oceny restauracji" : (
        '''
        Trzy najgorzej oceniane restauracje to: Włoska Uczta, Hiszpańska Paella i Wege Zieleniarnia. 
        Hiszpańska Paella jednak pojawia się już w zestawieniu 10 najbardziej dochodowych dla nas współprac.
        Zatem gdyby pojawiła się potrzeba zrezygnowania z obsługi któregoś z lokali gastronomicznych aktualnie obsługiwanych,
        w pierwszej kolejności należy brać pod uwagę Włoską Ucztę i Wege Zieleniarnię.
        '''
    ),

    "Oceny dostawców" : (
        '''
        Najlepiej oceniani dostawcy zostali średnio ocenieni na ponad 3.5 gwiazdki na 5 możliwych. Jest to zbyt niski wynik, żeby móc konkurować
        w jakości dostaw z bardziej popularnymi firmami. Ten obszar funkcjonowania firmy wymaga znacznej poprawy.
        '''
    ),

    "Zestawienie kuchni świata" : (
        '''
        Najczęściej nasi klienci zamawiają dania z restauracji amerykańskich, polskich i włoskich. Każda z tych kategorii 
        stanowi w przybliżeniu 10% wszystkich zamówień. W przyszłości należałoby zastanowić się jak zwiększyć udział kuchni azjatyckiej lub
        tureckiej w tym zestawieniu, gdyż we Wrocławiu są one bardzo popularne. 
        '''
    ),

    "Najbardziej kosztowne pojazdy" : (
        '''
        Wśród pojazdów z naszej floty, których serwis kosztuje nas najwięcej w przeliczeniu na zrealizowane zamówienia 
        znalazło się najwięcej skuterów. Zarząd firmy powinien zastanowić się czy nie znaleźć innego producenta tego typu pojazdów,
        zważywszy na ich awaryjność i koszty napraw.
        '''
    ),

    "Mało aktywni lub wiekowi pracownicy" : (
        '''
        Tabela przedstawia pracowników którzy mają już więcej niż 45 lat lub notują średnio mniej niż 0.5 zrealizowanego zamówienie dziennie.
        Gdy zaistnieje potrzeba cięcia kosztów i zwolnień, należy zwrócić szczególną uwage na wyżej przedstawionych dostawców.
        '''
    ),

    "Zamówienia, w których jedzenie było zimne" : (
        '''
        W tabeli przedstawieni są dostawcy i restauracje, które były odpowiedzialne za
        dostarczenie zimnego jedzenie do klienta. W trzeciej kolumnie znajduje
        się liczba takich zamówień dla danej kombinacji. Przesłanki o zimnym jedzeniu
        pochodzą z ocen wystawianych przez klientów.
        '''
    )

}

# Styl tekstu
styles = getSampleStyleSheet()
normal_style = ParagraphStyle(
    'Normal',
    parent=styles['Normal'],
    alignment=0,
    fontName=font_name, 
    fontSize=12,
    leading=14
)

# Dodanie wykresów i wniosków do raportu PDF
for title, image in sekcje:
    c.setFont(font_name, 16)
    c.drawString(100, 750, title)
    c.drawImage(ImageReader(image), 100, 400, width=400, height=300)
    
    if title in opisy:
        conclusion_text = opisy[title]
        conclusion_para = Paragraph(conclusion_text, normal_style)
        frame_width = 400
        frame_height = 200
        x = 100
        y = 150
        conclusion_frame = Frame(x, y, frame_width, frame_height, showBoundary=0)
        conclusion_frame.addFromList([conclusion_para], c)
    
    c.showPage()

c.save()

print(f"Raport PDF został wygenerowany pod nazwą: {pdf_file}")

