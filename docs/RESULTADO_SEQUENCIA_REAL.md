# Execução sobre sequência biológica real

Este documento registra a execução do AlvoCas9 sobre uma sequência pública
curada, e não sobre os arquivos sintéticos de exemplo.

## Por que executar sobre dado real

Até esta etapa, todo o comportamento do pipeline havia sido avaliado com
quatro arquivos sintéticos escritos pelo próprio autor, com 40 a 50 bases. Eles
são adequados para verificar o funcionamento do código, porque permitem
calcular as coordenadas à mão, mas não dizem nada sobre o comportamento do
pipeline diante de uma sequência com composição de bases real.

A execução sobre uma sequência curada responde a uma pergunta diferente: dado
um gene real, quantos sítios compatíveis existem, como eles se distribuem entre
as duas fitas e quantos sobrevivem aos filtros básicos.

## A sequência analisada

Gene **ADE2** (`YOR128C`) de *Saccharomyces cerevisiae* S288C, sequência
genômica de 1.716 pares de base, obtida do Ensembl release 116, assembly
R64-1-1, cromossomo XV, posições 564476 a 566191.

O ADE2 é o alvo canônico de CRISPR-Cas9 em levedura: sua interrupção faz a
colônia acumular pigmento vermelho, o que torna a edição visível sem
instrumentação. A procedência completa, os checksums e as verificações de
integridade estão em `data/real/README.md`.

A sequência foi conferida antes do uso: tem 1.716 bases, múltiplo de três,
começa com `ATG`, termina com `TAA` e **não possui nenhum códon de parada
interno**, o que confirma que está completa e na fase e orientação corretas.

## Comando executado

```bash
python -m alvocas9 analyze \
  --input data/real/ADE2_scerevisiae.fasta \
  --output results/ade2
```

Configuração padrão: PAM `NGG`, protospacer de 20 nucleotídeos, GC entre 40% e
60%, homopolímero máximo 4, modo estrito sem aceitação de `N`.

## Resultados

### Validação

A validação não encontrou erros nem avisos. A sequência usa apenas A, C, G e T,
tem identificador único e tamanho acima do mínimo configurado.

### Sítios encontrados

| Grandeza | Fita + | Fita − | Total |
| --- | --- | --- | --- |
| PAMs encontrados | 80 | 62 | 142 |
| PAMs descartados por falta de bases a montante | 2 | 0 | 2 |
| Candidatos extraídos | 78 | 62 | 140 |

Os dois PAMs descartados estão nas primeiras bases da fita direta, onde não
existem 20 nucleotídeos anteriores para formar o protospacer. A execução levou
cerca de 2 segundos.

### Classificação pelos filtros

| Status | Quantidade | Participação |
| --- | --- | --- |
| Aprovado nos filtros básicos | 80 | 57,1% |
| Requer cautela | 60 | 42,9% |
| Reprovado nos filtros básicos | 0 | 0% |

A distribuição de scores detalha o motivo de cada cautela:

| Score | Quantidade | Penalidade aplicada |
| --- | --- | --- |
| 100 | 80 | nenhuma |
| 90 | 5 | homopolímero acima do limite |
| 80 | 49 | GC fora da faixa configurada |
| 70 | 6 | GC fora da faixa **e** homopolímero |

Nenhum candidato foi reprovado porque nenhum acionou condição crítica: a
sequência não contém bases desconhecidas, e nenhum protospacer aparece
duplicado exatamente dentro da entrada.

### Características dos candidatos

| Característica | Valor |
| --- | --- |
| GC% mínimo | 20,0% |
| GC% mediano | 40,0% |
| GC% máximo | 70,0% |
| Candidatos dentro da faixa 40–60% | 85 (60,7%) |
| Maior homopolímero observado | 5 bases |
| Candidatos com homopolímero acima de 4 | 11 |
| Protospacers duplicados na entrada | 0 |
| Sítios de corte definidos | 140, entre as posições 23 e 1682 |

## Confronto com o modelo probabilístico

Esta é a parte mais informativa da execução. O modelo apresentado em
`docs/DESEMPENHO_E_COMPLEXIDADE.md` prevê, para DNA com bases equiprováveis,
cerca de 125 PAMs por kb somando as duas fitas. Aplicado às 1.716 bases do
ADE2, esse modelo preveria **214,5 PAMs**. Foram encontrados **142**.

A diferença não é erro do pipeline: é consequência da composição de bases. O
ADE2 tem GC de 40,21%, abaixo dos 50% de uma sequência uniforme, e guanina e
citosina não aparecem na mesma proporção.

| Base | Frequência |
| --- | --- |
| A | 31,53% |
| T | 28,26% |
| G | 21,56% |
| C | 18,65% |

Refinando o modelo com as frequências observadas, a probabilidade de uma
posição iniciar um PAM `NGG` é `f(G)²` na fita direta. Na fita reversa
complementar, um `GG` corresponde a um `CC` na sequência original, então a
probabilidade é `f(C)²`:

| Fita | Previsto pelo modelo refinado | Observado |
| --- | --- | --- |
| Fita + | 79,8 | 80 |
| Fita − | 59,7 | 62 |
| Total | 139,5 | 142 |

O desvio total é de **+1,8%**, e a previsão para a fita direta acertou
praticamente na mosca. O modelo refinado também explica a assimetria entre as
fitas, que o modelo uniforme não explicaria: há mais guaninas do que citosinas
na fita codificante, e por isso a fita direta oferece mais sítios.

Três conclusões:

1. A busca não está perdendo nem inventando sítios, porque o número encontrado
   corresponde ao previsto a partir da composição da própria sequência.
2. A quantidade de candidatos depende fortemente da composição de bases do
   alvo, e não apenas do seu tamanho. Estimativas baseadas em DNA uniforme
   superestimam o resultado em mais de 50% para este gene.
3. A assimetria entre as fitas é esperada e tem explicação quantitativa, o que
   evita interpretá-la como defeito do pipeline.

## Interpretação conservadora

Os 140 candidatos são **candidatos in silico**. O fato de 80 deles terem
passado pelos filtros básicos significa apenas que não acionaram nenhuma das
quatro regras simples do pipeline: faixa de GC, presença de base desconhecida,
homopolímero e duplicação exata na entrada.

Nada neste resultado indica que qualquer um desses sítios seria eficiente,
específico ou adequado para uso experimental. Não houve comparação contra o
genoma de levedura completo, e portanto não é possível afirmar nada sobre
especificidade genômica: um protospacer identificado aqui pode ter regiões
semelhantes em outros pontos do genoma, e o pipeline não verifica isso.

O sítio de corte reportado é derivado da premissa de que a SpCas9 corta cerca
de três pares de base antes do PAM. É um valor calculado, não medido.

## Reprodutibilidade

A execução pode ser repetida com o arquivo versionado em
`data/real/ADE2_scerevisiae.fasta`, cujo conteúdo é conferível pelo SHA-256
registrado em `data/real/README.md`. O pipeline é determinístico: a mesma
entrada com os mesmos parâmetros produz exatamente as mesmas saídas, com
exceção do carimbo de data e hora do relatório.
