# Explicação técnica do pipeline

Este documento explica o funcionamento do AlvoCas9 como software. O objetivo é permitir que a lógica computacional seja entendida, testada e mantida, não apenas executada por comandos.

## Fluxo geral

O pipeline executa as seguintes etapas:

1. Recebe caminho do FASTA e diretório de saída pela CLI.
2. Monta uma configuração de execução.
3. Lê e valida o FASTA.
4. Se houver erro crítico, salva `validation.json`, `run_config.json`, log e encerra.
5. Se houver apenas avisos, continua a análise e registra os avisos.
6. Calcula resumo das sequências.
7. Procura PAMs nas fitas `+` e `-`.
8. Extrai protospacers adjacentes ao PAM.
9. Calcula características dos candidatos.
10. Aplica filtros básicos e score heurístico.
11. Gera CSV, JSON, gráficos, relatórios e log.

## Entrada

A entrada principal é um arquivo FASTA de DNA. Cada registro deve ter cabeçalho iniciado por `>` e sequência em uma ou mais linhas.

Exemplo:

```text
>gene_exemplo
ATGCGTACGTAGCTAGCTAGAGG
```

Os parâmetros principais são:

- `--input`
- `--output`
- `--pam`
- `--target-length`
- `--min-gc`
- `--max-gc`
- `--max-homopolymer`
- `--allow-n`
- `--min-sequence-length`

## Validação

A validação diferencia erros e avisos.

Erros críticos:

- arquivo inexistente;
- arquivo vazio;
- sequência antes do primeiro cabeçalho;
- cabeçalho vazio;
- sequência vazia;
- identificador duplicado;
- caracteres inválidos;
- N em modo estrito.

Avisos:

- sequência curta;
- presença de N em modo flexível;
- proporção alta de N.

Se houver erro crítico, a análise não prossegue para busca de PAM. Essa decisão evita gerar candidatos a partir de dados inválidos.

## Busca por PAM

O módulo de PAM transforma o padrão IUPAC em regra de correspondência. O padrão inicial é `NGG`.

No projeto:

- `N` no padrão PAM significa A, C, G ou T;
- `N` na sequência de entrada representa base desconhecida;
- um PAM real não é confirmado quando depende de N desconhecido na própria sequência.

A busca percorre a sequência com uma janela do tamanho do PAM e permite ocorrências sobrepostas.

## Extração de candidatos

Para cada PAM encontrado, o pipeline verifica se há bases suficientes antes dele.

Regra padrão:

- PAM: `NGG`;
- protospacer: 20 bases antes do PAM;
- orientação: 5'->3' da fita analisada.

Se o PAM aparece no início da sequência e não há 20 bases antes dele, esse PAM é ignorado e contabilizado como PAM sem upstream suficiente.

## Análise das duas fitas

O pipeline analisa:

- fita `+`: sequência original do FASTA;
- fita `-`: reverso complementar da sequência original.

Para a fita `-`, a sequência é transformada antes da busca. O protospacer é salvo na orientação da fita analisada, mas as coordenadas são mapeadas para a sequência original.

## Cálculo de coordenadas

Internamente, Python usa índices 0-based e intervalos semiabertos `[start, end)`.

Na saída, o projeto usa coordenadas 1-based inclusivas.

Fita `+`:

```text
protospacer_start_1based = protospacer_start_0based + 1
protospacer_end_1based = protospacer_end_0based
```

Fita `-`:

```text
start_original_1based = original_length - end_0 + 1
end_original_1based = original_length - start_0
```

Essa fórmula é testada com sequências pequenas para evitar erro silencioso.

## Cálculo de GC

GC% é calculado como:

```text
(quantidade de G + quantidade de C) / tamanho da sequência * 100
```

No candidato, o cálculo é feito sobre o protospacer.

## Filtros

Os filtros básicos avaliam:

- GC abaixo do mínimo;
- GC acima do máximo;
- presença de N;
- homopolímero maior que o limite;
- duplicação exata do protospacer dentro da entrada.

Esses filtros são heurísticos e não validam eficiência biológica.

## Score

O score começa em 100:

- -20 se GC estiver fora da faixa;
- -25 se houver N;
- -10 se homopolímero exceder o limite;
- -20 se houver duplicação exata.

O score é limitado entre 0 e 100.

Status:

- `aprovado nos filtros básicos`;
- `requer cautela`;
- `reprovado nos filtros básicos`.

## Geração de arquivos

O pipeline gera:

```text
tables/sequences_summary.csv
tables/candidates.csv
tables/validation_summary.csv
json/validation.json
json/candidates.json
json/run_config.json
figures/candidates_per_sequence.png
figures/gc_distribution_candidates.png
figures/filter_status_summary.png
reports/technical_report.html
reports/technical_report.md
logs/pipeline.log
```

## Relatório

O relatório técnico resume:

- configurações;
- validação;
- conceitos de CRISPR-Cas9;
- candidatos;
- gráficos;
- interpretação conservadora;
- limitações.

O relatório usa linguagem de triagem exploratória e evita termos que indiquem recomendação experimental, clínica ou terapêutica.

## Logs

O log registra:

- início;
- arquivo usado;
- diretório de saída;
- número de sequências;
- erros e avisos de validação;
- número de candidatos;
- arquivos gerados;
- fim da execução.

Em caso de erro crítico, o log registra a falha e o pipeline encerra antes da busca de PAM.

## Testes

Os testes cobrem:

- leitura FASTA;
- validação;
- reverso complementar;
- PAM;
- scanner na fita `+`;
- scanner na fita `-`;
- features;
- filtros;
- CLI;
- relatório.

O teste mais importante do ponto de vista técnico é o da fita reversa, porque valida o mapeamento de coordenadas para a sequência original.
