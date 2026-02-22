# 🕹️ Pac-Man

Klasyczna gra Pac-Man zaimplementowana w języku Python przy użyciu biblioteki Pygame. 👻🍒

https://github.com/user-attachments/assets/1b71e21c-0876-483c-b60b-977e3cda33ea

## ⚙️ Wymagania

Do uruchomienia gry potrzebny jest środowisko **Python (wersja 3.x)** oraz biblioteka **Pygame**. 
Aby zainstalować wymagane zależności, otwórz terminal i wykonaj polecenie:

`pip install pygame`

## 🚀 Uruchomienie

Aby rozpocząć rozgrywkę, przejdź do głównego folderu projektu w terminalu i uruchom skrypt:

`python pac_man.py`

## ⌨️ Sterowanie

* ⬆️ ⬇️ ⬅️ ➡️ **Strzałki kierunkowe:** Poruszanie się postacią Pac-Mana.
* 🖱️ **Myszka / Klawiatura:** Wpisywanie nicku gracza oraz klikanie przycisku "ZATWIERDŹ" w menu startowym i opcji w menu końcowym.

## 🧩 Główne mechaniki gry

* 🟡 **Zjadanie kropek:** Standardowe kropki dają 10 punktów.
* 🔵 **Power Pellets (Duże kropki):** Dają 50 punktów i aktywują na 5 sekund tryb ucieczki duchów.
* 👻 **Zjadanie duchów:** W trybie ucieczki zjedzenie ducha nagradzane jest 200 punktami. Zjedzony duch powraca jako "oczy" 👁️ do swojej bazy (wykorzystując algorytm przeszukiwania wszerz - **BFS** do znalezienia najkrótszej drogi).
* 🍒 **Owoce:** Pojawiają się na planszy dwa razy na dany poziom (po zebraniu 70 i 170 kropek). Rodzaj owocu zależy od aktualnego poziomu (Wiśnia 🍒, Truskawka 🍓, Jabłko 🍎, Brzoskwinia 🍑). Zebranie owocu daje `100 x numer poziomu` punktów.
* 🏆 **Tablica wyników:** Najlepsze 3 wyniki (Nick + Score) są automatycznie zapisywane i wczytywane z lokalnego pliku `scores.txt`.
* 📈 **Poziomy:** Po wyczyszczeniu całej planszy z kropek następuje płynne przejście do kolejnego, trudniejszego poziomu (z zachowaniem zdobytych punktów i żyć).

## 👻 Sztuczna Inteligencja Duchów

W grze występują 4 duszki: **Blinky** ❤️, **Pinky** 🩷, **Inky** 🩵 oraz **Clyde** 🧡. Ich zachowanie definiują 3 główne stany:

* 🎯 **Pościg i Rozproszenie:** Duchy obliczają odległość z sąsiednich kafelków do celu, korzystając z metryki euklidesowej:
  $$d = \sqrt{(x_{target} - x_{next})^2 + (y_{target} - y_{next})^2}$$
  Wybierają zawsze kierunek, dla którego wartość $d$ jest najmniejsza. Celem jest odpowiednio: pozycja Pac-Mana (pościg) lub przypisany róg planszy (rozproszenie).
* 🌀 **Ucieczka (Frightened):** Logika celowania zostaje wyłączona. Na każdym skrzyżowaniu duchy wybierają drogę pseudolosowo z prawdopodobieństwem:
  $$P = \frac{1}{n}$$
  gdzie $n$ to liczba dostępnych, odblokowanych ścieżek.
* 👁️ **Powrót do bazy (Dead Mode):** Po zjedzeniu, duch musi najkrótszą drogą wrócić do "domku". Odpowiada za to algorytm przeszukiwania grafu wszerz (**BFS - Breadth-First Search**) o złożoności czasowej:
  $$O(|V| + |E|)$$
  gwarantujący znalezienie bezkolizyjnej trasy powrotnej.

## ⚖️ Prawa autorskie i źródła

Projekt został stworzony w celach edukacyjnych. Nie roszczę sobie praw autorskich do wykorzystanych w nim zasobów audiowizualnych:
* 🔊 **Efekty dźwiękowe i muzyka** pochodzą ze strony [https://downloads.khinsider.com/game-soundtracks/album/pac-man-game-sound-effect-original-soundtrack-2024](https://downloads.khinsider.com/game-soundtracks/album/pac-man-game-sound-effect-original-soundtrack-2024).
* 🖼️ **Grafiki i animacje** (sprites) zostały pozyskane z ogólnodostępnych, darmowych zasobów w Internecie na potrzeby implementacji tego projektu.
