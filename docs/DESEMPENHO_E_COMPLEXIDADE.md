# Desempenho e complexidade do AlvoCas9

Este documento analisa o custo computacional do pipeline. Ele existe porque o
AlvoCas9 é um trabalho de Ciência da Computação: o domínio da aplicação é
biológico, mas a contribuição está no tratamento computacional do problema, e
isso inclui saber quanto o programa custa e por quê.

As medições foram feitas com `scripts/benchmark_busca_pam.py` e estão
registradas em `docs/DESEMPENHO_MEDIDO.md`, que é gerado pelo próprio script.

## Notação

| Símbolo | Significado |
| --- | --- |
| `n` | número total de bases do arquivo de entrada |
| `m` | tamanho do padrão PAM, 3 para `NGG` |
| `L` | tamanho do protospacer, 20 por padrão |
| `k` | número de PAMs encontrados |
| `c` | número de candidatos extraídos, com `c ≤ k` |

## Custo de cada etapa

| Etapa | Tempo | Espaço adicional |
| --- | --- | --- |
| Leitura do FASTA | `O(n)` | `O(n)` |
| Validação das sequências | `O(n)` | `O(1)` por registro |
| Reverso complementar | `O(n)` | `O(n)` |
| Busca de PAM nas duas fitas | `O(n · m)` | `O(k)` |
| Extração dos protospacers | `O(k · L)` | `O(c · L)` |
| Cálculo das características | `O(c · L)` | `O(c · L)` |
| Filtros e score | `O(c)` | `O(c)` |
| Escrita das saídas | `O(c · L)` | — |

Somando as etapas, o tempo total é `O(n · m + c · L)`. Como `m` e `L` são
constantes de configuração, e não crescem com a entrada, o pipeline é
**linear no tamanho da entrada**: `O(n)`.

O espaço é `O(n + c · L)`. A parcela `O(n)` vem de manter a sequência e seu
reverso complementar em memória; a parcela `O(c · L)` vem de manter todos os
candidatos em memória antes de escrever os arquivos. Essa segunda parcela é a
que limita o uso do pipeline em entradas muito grandes.

### Por que a busca não precisa de retrocesso

A busca percorre cada posição da sequência e compara a janela de `m` bases com
o padrão. Não há retrocesso: o padrão é um conjunto de classes de caracteres
sem repetição nem alternância, então cada posição é examinada no máximo `m`
vezes. Com `m = 3`, o custo por base é constante e pequeno.

A busca permite PAMs sobrepostos, o que é necessário para não perder sítios:
em `CGGG` existem dois `NGG` válidos, nas posições 0 e 1. Por isso a varredura
avança uma posição por vez, e não `m` posições.

## Quantos candidatos esperar

Para DNA aleatório com as quatro bases equiprováveis, a probabilidade de uma
posição iniciar um PAM `NGG` é:

```text
P(NGG) = P(qualquer base) × P(G) × P(G) = 1 × 1/4 × 1/4 = 1/16 = 0,0625
```

Isso prevê **62,5 PAMs por kb em cada fita** e, somando as duas fitas, cerca de
**125 candidatos por kb**.

A medição confirma o modelo:

| Grandeza | Previsto | Medido |
| --- | --- | --- |
| PAMs por kb em uma fita | 62,5 | 61,8 |
| Candidatos por kb nas duas fitas | 125,0 | 123,5 |

Os valores medidos vêm de uma sequência aleatória de 200 kb, com 12.364 PAMs
em uma fita e 24.699 candidatos nas duas fitas. A diferença de cerca de 1% em
relação ao previsto é compatível com a variação de uma amostra aleatória.

Essa correspondência é útil por dois motivos. Primeiro, confirma que a busca
não está perdendo nem duplicando sítios. Segundo, permite estimar o tamanho da
saída antes de executar: uma entrada de 1 Mb produzirá da ordem de 125 mil
candidatos.

### O modelo aplicado a uma sequência real

DNA real não tem bases equiprováveis, e o modelo precisa ser refinado para a
composição observada. Para o padrão `NGG`, a probabilidade passa a ser `f(G)²`
na fita direta e `f(C)²` na fita reversa complementar, já que um `GG` na fita
reversa corresponde a um `CC` na sequência original.

Aplicado ao gene ADE2 de *Saccharomyces cerevisiae*, com 1.716 pares de base e
GC de 40,21%, o modelo refinado prevê 79,8 PAMs na fita direta e 59,7 na
reversa. Foram observados 80 e 62, um desvio total de 1,8%. O modelo uniforme
preveria 214,5 PAMs, superestimando em mais de 50%.

O refinamento também explica a assimetria entre as fitas: a fita codificante do
ADE2 tem 21,56% de guanina contra 18,65% de citosina, e por isso oferece mais
sítios. Os detalhes estão em `docs/RESULTADO_SEQUENCIA_REAL.md`.

## Três implementações da busca de PAM

A busca foi escrita de três formas ao longo do projeto. Todas produzem
exatamente as mesmas posições, o que é verificado por um teste de equivalência
em `tests/test_pam.py`, que compara as implementações em sequências aleatórias
de vários tamanhos, com cinco padrões PAM diferentes e com bases desconhecidas.

1. **Versão inicial.** Para cada posição, chamava `pam_matches`, que revalidava
   o padrão PAM inteiro antes de comparar. A revalidação era redundante, porque
   o padrão não muda durante a varredura. Essa versão não está mais no código
   do pipeline; ela é reproduzida dentro do script de benchmark para que a
   comparação seja possível.
2. **Varredura direta**, em `find_pam_positions_by_scan`. Valida o padrão uma
   única vez, converte cada código IUPAC no conjunto de bases aceitas e compara
   posição a posição. É a referência legível da regra e permanece no código.
3. **Expressão regular com lookahead**, em `find_pam_positions`. Compila o
   padrão uma vez em `(?=[ACGT][G][G])` e deixa a varredura para o autômato da
   biblioteca `re`. O lookahead não consome caracteres, o que preserva a
   detecção de PAMs sobrepostos. É a implementação usada pelo pipeline.

A complexidade assintótica das três é a mesma, `O(n · m)`. O que muda é a
constante: a terceira executa o laço em código nativo, enquanto as duas
primeiras executam um laço do interpretador Python a cada base.

## Resultados medidos

Sequência aleatória de 200 kb, padrão `NGG`, menor de três execuções. A
execução registrada é a de `docs/DESEMPENHO_MEDIDO.md`, que traz também os
demais tamanhos.

| Implementação | Tempo (ms) | Taxa (kb/s) | Ganho sobre a versão inicial |
| --- | --- | --- | --- |
| Versão inicial, revalidando o padrão | 303,71 | 659 | — |
| Varredura direta | 135,70 | 1.474 | 2,0× |
| Expressão regular com lookahead | 5,75 | 34.758 | 69,7× |

Os tempos absolutos variam de uma execução para outra, e as razões variam
junto. Em execuções sucessivas na mesma máquina, a varredura direta ficou
entre 1,9 e 2,4 vezes mais rápida que a versão inicial, e a expressão regular,
entre 41 e 70 vezes. O que deve ser citado é a ordem de grandeza, e não um
número específico: a varredura direta é cerca de **duas vezes** mais rápida, e
a expressão regular, cerca de **uma ordem de grandeza e meia**.

A separação em três versões mostra de onde vem cada parte do ganho. Remover a
revalidação redundante do padrão explica um fator próximo de 2, obtido sem
mudar o algoritmo. Trocar o laço do interpretador pelo autômato da biblioteca
explica todo o resto, e também não muda o algoritmo: as três implementações
percorrem a sequência uma vez e comparam `m` posições por base.

Para a extração completa de candidatos nas duas fitas, que inclui reverso
complementar, busca, recorte dos protospacers, cálculo do sítio de corte e da
posição relativa, e mapeamento das coordenadas, a medição é bem menos estável
que a da busca isolada. Em execuções sucessivas na mesma máquina, no mesmo dia,
a entrada de 200 kb levou entre 103 e 340 milissegundos, ou seja, entre cerca
de 590 e 1.950 kb/s.

Essa dispersão é de ambiente, não de algoritmo: a etapa aloca dezenas de
milhares de objetos pequenos, e o custo de alocação e de coleta de lixo varia
conforme o estado da máquina. A busca de PAM isolada, que quase não aloca, tem
medições estáveis.

O que se pode afirmar com segurança:

- a etapa opera na **ordem de 1.000 a 2.000 kb/s**;
- a taxa não degrada conforme a entrada cresce, o que é o comportamento
  esperado de um algoritmo linear;
- antes da otimização, a mesma etapa foi medida em cerca de 200 kb/s, então o
  ganho é de **aproximadamente uma ordem de grandeza**.

Citar um número isolado aqui seria enganoso. A tabela completa de uma execução
específica está em `docs/DESEMPENHO_MEDIDO.md`, com a ressalva de que ela
registra uma execução, e não uma constante.

## Onde o tempo é gasto hoje

Otimizar a busca deslocou o gargalo. Medindo cada fase separadamente em uma
entrada de 50 kb, que produz 6.206 candidatos:

| Fase | Tempo aproximado | Participação |
| --- | --- | --- |
| Importar o matplotlib | 550 ms | 38% |
| Validação do FASTA | 2 ms | 0,1% |
| Busca e extração nas duas fitas | 32 ms | 2% |
| Cálculo das características | 23 ms | 2% |
| Filtros e score | 8 ms | 0,5% |
| Escrita das saídas, incluindo os gráficos | 855 ms | 58% |

Esta medição é de uma execução única e serve para comparar as proporções, não
para fixar valores absolutos.

A busca de PAM, que era o foco da otimização, responde hoje por cerca de 2% do
tempo. Quase todo o resto está em dois pontos que não têm relação com o
algoritmo: o carregamento da biblioteca de gráficos e a escrita dos arquivos.

Durante essa medição apareceu um custo que não era evidente. A conversão de
cada candidato para dicionário usava `dataclasses.asdict`, que faz cópia
recursiva de todos os campos. Com 6.206 candidatos, isso custava mais do que a
própria busca: a fase de busca e extração caiu de cerca de 105 ms para 32 ms
quando a conversão passou a ser escrita campo a campo. É um lembrete de que,
depois de um certo ponto, o custo deixa de estar no algoritmo e passa a estar
na forma como os dados são movimentados.

Os tempos de escrita variam bastante entre execuções, porque dependem do disco
e da renderização dos gráficos. As proporções, não.

## O que ainda não escala

A busca escala bem; a **saída, não**. O relatório técnico embute a tabela
completa de candidatos, então uma entrada de 50 kb gera um relatório HTML de
cerca de 1,9 MB com mais de 6 mil linhas de tabela, e o `candidates.json`
passa de 4 MB. Para entradas na ordem de megabases, o relatório deixa de ser
legível em um navegador, mesmo que a análise termine rapidamente.

Também é preciso registrar que todos os candidatos são mantidos em memória
antes da escrita, o que torna o consumo proporcional ao tamanho da entrada.

Essas duas limitações são de apresentação e de uso de memória, não do
algoritmo de busca, e estão declaradas aqui para que não sejam confundidas com
limitação do método.

## Como reproduzir

```bash
python scripts/benchmark_busca_pam.py
python scripts/benchmark_busca_pam.py --saida docs/DESEMPENHO_MEDIDO.md
```

As sequências de teste são geradas com semente fixa, então a mesma execução
pode ser repetida em outra máquina e comparada. O script confere, durante a
execução, que as três implementações encontram exatamente as mesmas posições,
e interrompe com erro se houver divergência.

Os tempos absolutos dependem da máquina. As razões entre as implementações e o
comportamento linear da taxa são o que deve se manter.
