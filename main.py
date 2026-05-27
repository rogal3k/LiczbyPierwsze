import os
import time
import random
from multiprocessing import Pool, cpu_count

# Pre-generujemy listę małych liczb pierwszych (pre-filtr)
# Wystarczy pierwsze kilkadziesiąt, aby odsiewać większość liczb złożonych
SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]

def is_probably_prime(n, k=5):
    if n < 2:
        return False
        
    # Krok 1: Superszybki pre-filtr. Odsiewa ~75% liczb bez ciężkich obliczeń.
    for p in SMALL_PRIMES:
        if n % p == 0:
            return n == p

    # Krok 2: Algorytm Millera-Rabina (dla tych, które przetrwały pre-filtr)
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randrange(2, n - 1)
        # Funkcja pow(base, exp, mod) w Pythonie jest zaimplementowana w C
        x = pow(a, d, n) 
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False # Na pewno liczba złożona
    return True # Prawdopodobnie pierwsza

def process_chunk(chunk_data):
    """Konwertuje 256 bajtów na liczbę i sprawdza czy jest pierwsza."""
    chunk_index, chunk_bytes = chunk_data

    number = int.from_bytes(chunk_bytes, byteorder='big')
    
    if is_probably_prime(number):
        return chunk_index, number
    return None

def main():
    file_path = "TRNG_P.bit"
    chunk_size = 256 # 256 bajtów = 2048 bitów
    
    # 1. Wczytanie pliku
    print(f"Wczytywanie pliku {file_path}...")
    start_time = time.time()
    
    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Nie znaleziono pliku {file_path}!")
        return

    # Tworzymy listę krotek (indeks, bajty)
    chunks = [(i, data[i:i+chunk_size]) for i in range(0, len(data), chunk_size) if len(data[i:i+chunk_size]) == chunk_size]
    total_chunks = len(chunks)
    print(f"Plik podzielono na {total_chunks} liczb (2048-bitowych).")

    # 2. Przetwarzanie wielordzeniowe
    cores = cpu_count()
    print(f"Uruchamianie algorytmu Millera-Rabina na {cores} rdzeniach procesora...")
    
    primes_found = []
    
    # Używamy puli procesów - omija to GIL w Pythonie i wykorzystuje 100% procesora
    with Pool(processes=cores) as pool:
        for result in pool.imap_unordered(process_chunk, chunks, chunksize=1000):
            if result is not None:
                primes_found.append(result)

    end_time = time.time()
    execution_time = end_time - start_time
    
    # 3. Podsumowanie
    print("\n" + "="*50)
    print(f"Zakończono! Czas egzekucji: {execution_time:.2f} sekund.")
    print(f"Znaleziono liczb pierwszych: {len(primes_found)}")
    print("="*50)

    print("Zapisywanie znalezionych liczb do pliku 'znalezione_liczby.txt'...")
    with open("znalezione_liczby.txt", "w") as out:
        for idx, prime in sorted(primes_found):
            out.write(f"Blok {idx}: {prime}\n")
    print("Gotowe! Plik został zapisany.")

if __name__ == '__main__':
    main()