# Automatska provjera citiranih članaka

Provjerava se je li svaki članak koji model navodi bio u dostavljenom kontekstu. Citat članka izvan konteksta predstavlja izmišljanje.

## Sažetak po modelu

| Model | Odgovora | Ukupno citata | Izvan konteksta | Udio |
|---|---|---|---|---|
| gemma3:12b | 30 | 35 | 1 | 2.9 % |
| qwen3:8b | 30 | 53 | 1 | 1.9 % |
| mistral-nemo | 30 | 30 | 1 | 3.3 % |

## Sažetak po tipu pitanja

| Tip | gemma3:12b | qwen3:8b | mistral-nemo |
|---|---|---|---|
| A | 0 | 1 | 0 |
| B | 1 | 0 | 0 |
| C | 0 | 0 | 0 |
| D | 0 | 0 | 0 |
| E | 0 | 0 | 1 |

## Pojedinačni slučajevi izmišljenih citata

**[2] Što je izvanredni otkaz ugovora o radu?**  
qwen3:8b, prolaz 1 — izvan konteksta: čl. 113.  
*u kontekstu bili:* 150, 104, 116, 47, 115

**[7] Što se događa ako sud utvrdi da mi otkaz nije bio zakonit?**  
gemma3:12b, prolaz 2 — izvan konteksta: čl. 35.  
*u kontekstu bili:* 124, 125, 229, 46, 150

**[15] Kada radnica ima pravo na rodiljni dopust?**  
mistral-nemo, prolaz 2 — izvan konteksta: čl. 28.  
*u kontekstu bili:* 36, 35, 34, 86, 32

