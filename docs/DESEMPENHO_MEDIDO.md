# Desempenho medido da busca de PAM

- Python: 3.11.9
- Sistema: Windows 10 (build 10.0.26200)
- Processador: Intel64 Family 6 Model 186 Stepping 2, GenuineIntel
- Padrão PAM: `NGG`
- Repetições por medição: 3 (menor tempo)
- Semente das sequências: 20261116

## Busca de PAM em uma fita

As três implementações foram verificadas durante a execução e produziram
exatamente as mesmas posições em todos os tamanhos testados.

| Tamanho da sequência | Implementação | Tempo (ms) | Taxa (kb/s) |
| --- | --- | --- | --- |
| 1.000 bp | Versao inicial (revalidando o padrao) | 1,84 | 544 |
| 1.000 bp | Varredura direta | 0,92 | 1.082 |
| 1.000 bp | Expressao regular com lookahead | 0,05 | 19.084 |
| 10.000 bp | Versao inicial (revalidando o padrao) | 18,31 | 546 |
| 10.000 bp | Varredura direta | 7,81 | 1.281 |
| 10.000 bp | Expressao regular com lookahead | 0,26 | 37.864 |
| 50.000 bp | Versao inicial (revalidando o padrao) | 68,51 | 730 |
| 50.000 bp | Varredura direta | 42,73 | 1.170 |
| 50.000 bp | Expressao regular com lookahead | 1,33 | 37.636 |
| 200.000 bp | Versao inicial (revalidando o padrao) | 341,32 | 586 |
| 200.000 bp | Varredura direta | 135,01 | 1.481 |
| 200.000 bp | Expressao regular com lookahead | 5,97 | 33.515 |

PAMs encontrados por tamanho: 1.000 bp = 53, 10.000 bp = 608, 50.000 bp = 3.144, 200.000 bp = 12.364.

Nesta execução, em 200 kb, a varredura direta foi 2,6 vezes mais rápida que a versão inicial, e a expressão regular foi 46,1 vezes mais rápida que a versão inicial e 17,7 vezes mais rápida que a varredura direta. As razões variam de uma execução para outra; a ordem de grandeza é o que se mantém.

## Extração completa de candidatos nas duas fitas

Inclui reverso complementar, busca nas duas fitas, extração dos
protospacers e mapeamento das coordenadas.

| Tamanho da sequência | Candidatos extraídos | Tempo (ms) | Taxa (kb/s) |
| --- | --- | --- | --- |
| 1.000 bp | 122 | 0,62 | 1.614 |
| 10.000 bp | 1.220 | 6,85 | 1.460 |
| 50.000 bp | 6.244 | 43,67 | 1.145 |
| 200.000 bp | 24.699 | 339,63 | 589 |
