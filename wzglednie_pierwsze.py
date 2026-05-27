import random
import math
import time
import concurrent.futures
import os

def mine_coprimes(data_tuple):
    """
    Funkcja przypisana do jednego rdzenia. 
    Szuka kluczy 'e' przez określony limit czasu.
    """
    idx, p, q, time_limit = data_tuple
    
    L = ((p - 1) * (q - 1)) // math.gcd(p - 1, q - 1)
    
    found_count = 0
    start_time = time.time()
    
    # Sprawdzamy tylko liczby nieparzyste, bo L jest parzyste (więc parzyste 'e' na pewno odpadają)
    e_candidate = 3
    
    # Pętla działa dopóki nie minie time_limit sekund
    while time.time() - start_time < time_limit:
        if math.gcd(e_candidate, L) == 1:
            found_count += 1
            
        e_candidate += 2 
        
    return f"Para {idx}: W czasie {time_limit} sekund zdołano znaleźć {found_count} liczb względnie pierwszych."


if __name__ == '__main__':
    primes_list = []
    try:
        with open('znalezione_liczby.txt', 'r') as file:
            for line in file:
                parts = line.strip().split()
                if parts:
                    primes_list.append(int(parts[-1]))
    except FileNotFoundError:
        print("Nie znaleziono pliku! Program wymaga prawdziwych liczb.")
        exit()

    # 2. Losowanie 10 par
    pairs = []
    for _ in range(10):
        p, q = random.sample(primes_list, 2)
        pairs.append((p, q))

    # Konfiguracja eksperymentu
    TIME_LIMIT_PER_PAIR = 1.0  # Ile sekund procesor ma szukać liczb dla jednej pary
    cores = os.cpu_count()
    
    print(f"Rozpoczynam zmasowane poszukiwania na {cores} rdzeniach.")
    print(f"Czas szukania dla każdej pary: {TIME_LIMIT_PER_PAIR} sekund...\n" + "-"*50)

    # Pakujemy dane dla procesów: (indeks, p, q, limit_czasu)
    tasks = [(idx, p, q, TIME_LIMIT_PER_PAIR) for idx, (p, q) in enumerate(pairs, 1)]

    # 3. Wieloprocesowe "kopanie" liczb
    start_total_time = time.time()
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=cores) as executor:
        results = executor.map(mine_coprimes, tasks)
        
    for res in results:
        print(res)
        
    end_total_time = time.time()
    print("-" * 50)
    print(f"Eksperyment zakończony. Całkowity czas działania programu: {end_total_time - start_total_time:.2f} s.")