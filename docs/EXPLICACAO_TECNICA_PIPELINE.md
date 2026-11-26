# Explicação técnica do pipeline

Este documento explica o funcionamento do AlvoCas9 como software. O objetivo é permitir que a lógica computacional seja entendida, testada e mantida, não apenas executada por comandos.

## Fluxo geral

O pipeline executa as seguintes etapas:

1. Recebe caminho do FASTA e diretório de saída pela CLI.
2. Monta uma configuração de execução e valida seus parâmetros.
3. Lê e valida o FASTA.
4. Se houver erro crítico, salva `validation.json`, `run_config.json`, log e encerra.
5. Se houver apenas avisos, continua a análise e registra os avisos.
6. Calcula resumo das sequências.
7. Procura PAMs nas fitas `+` e `-`.
8. Extrai protospacers adjacentes ao PAM e calcula o sítio de corte previsto.
9. Calcula características dos candidatos.
10. Aplica filtros básicos, score heurístico e ordena por score.
11. Gera CSV, JSON, gráficos, relatórios e log.
12. Devolve um resumo da execução, que a CLI imprime no terminal.

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
- `--pam-position`
- `--allow-n`
- `--min-sequence-length`

## Validação dos parâmetros de execução

Antes de ler o arquivo, o pipeline valida a própria configuração. O padrão PAM
é validado por `core/pam.validate_pam_pattern`, que recusa códigos fora do
conjunto IUPAC suportado. Os parâmetros numéricos são validados no
`__post_init__` de `PipelineConfig`:

- `pam_position` igual a `3linha`, único valor suportado;
- `target_length` maior ou igual a 1;
- `min_gc` e `max_gc` entre 0 e 100;
- `min_gc` não maior que `max_gc`;
- `max_homopolymer` maior ou igual a 1;
- `min_sequence_length` maior ou igual a 1.

Todos os problemas encontrados são reportados em uma única mensagem, para
evitar correção por tentativa e erro.

Essa checagem existe porque valores aparentemente inofensivos produziam
resultado sem significado em silêncio. Com `target_length` igual a zero ou
negativo, por exemplo, cada PAM gerava um candidato de protospacer vazio, com
coordenada inicial maior que a final, e a execução terminava com código de
sucesso. Uma faixa de GC impossível, como mínimo 90 e máximo 10, reprovava
todos os candidatos sem indicar o motivo.

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

Permitir sobreposição é necessário para não perder sítios: em `CGGG` existem
dois `NGG` válidos, nas posições 0 e 1.

O módulo tem duas implementações equivalentes da busca:

- `find_pam_positions` usa o padrão compilado como expressão regular com
  lookahead. É a implementação usada pelo pipeline. O lookahead verifica a
  janela sem consumir caracteres, o que preserva as ocorrências sobrepostas.
- `find_pam_positions_by_scan` compara posição a posição, em Python. É a
  referência legível da regra, usada no teste de equivalência e no benchmark.

Um teste de equivalência compara as duas em sequências aleatórias de vários
tamanhos, com cinco padrões PAM diferentes e com bases desconhecidas. A análise
de custo das duas está em `docs/DESEMPENHO_E_COMPLEXIDADE.md`.

## Extração de candidatos

Para cada PAM encontrado, o pipeline verifica se há bases suficientes antes dele.

Regra padrão:

- PAM: `NGG`;
- protospacer: 20 bases antes do PAM;
- orientação: 5'->3' da fita analisada.

Se o PAM aparece no início da sequência e não há 20 bases antes dele, esse PAM é ignorado e contabilizado como PAM sem upstream suficiente.

## Sítio de corte

Além das coordenadas do protospacer e do PAM, o pipeline informa o sítio de
corte previsto, no campo `cut_site_1based`.

Na SpCas9, o corte de dupla-fita ocorre cerca de 3 pares de base a 5' do PAM,
isto é, entre as posições 17 e 18 de um protospacer de 20 nucleotídeos. O campo
informa a posição da base imediatamente anterior ao corte, na sequência
original, e o corte acontece entre essa posição e a seguinte.

O cálculo parte da posição do PAM, e não do protospacer, porque a distância é
definida em relação ao PAM:

```text
fita +:  posição = pam_start_1based - 3 - 1
fita -:  posição = pam_end_1based + 3
```

Na fita reversa complementar o PAM aparece em coordenadas menores da sequência
original, então o corte fica depois dele na numeração, e não antes. O campo
fica vazio quando a posição calculada cairia fora da sequência.

Esse valor é uma premissa do modelo, válida para sistemas com PAM a 3' do
protospacer. Ele não é uma medição e não deve ser apresentado como tal.

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

## Posição relativa na sequência

Cada candidato recebe o campo `relative_position_percent`, que é a posição do
seu ponto médio dividida pelo tamanho da sequência, em porcentagem.

É uma indicação de onde o sítio está, e não um critério de qualidade: o campo
não entra no score. A leitura usual em desenho de guias, de que sítios na
porção inicial da região codificante tendem a ser preferidos para nocaute,
porque uma interrupção precoce tem mais chance de inativar a proteína, só vale
quando a entrada é de fato um gene na orientação codificante. O pipeline não
tem como verificar isso, e por isso não assume.

O campo também alimenta o gráfico de distribuição dos candidatos ao longo da
sequência. Usar porcentagem em vez de posição absoluta mantém o gráfico legível
quando a entrada tem várias sequências de tamanhos diferentes.

## Exportação em formato BED

Além do CSV e do JSON, os candidatos são exportados em `tables/candidates.bed`,
com seis colunas separadas por tabulação e sem cabeçalho.

O ponto central dessa saída é a conversão de coordenadas. O projeto usa
**1-based inclusivas** e o BED usa **0-based semiabertas**:

```text
inicio_bed = inicio_1based - 1
fim_bed    = fim_1based
```

O fim não muda de valor porque o limite semiaberto do BED coincide
numericamente com o limite inclusivo 1-based: o intervalo que vai da base 1 à
base 23 em 1-based inclusivo é `[0, 23)` em 0-based semiaberto. Os dois têm 23
bases de comprimento, e é isso que o teste verifica.

O score do BED vai de 0 a 1000, enquanto o score heurístico do projeto vai de 0
a 100, então o valor é multiplicado por dez. A ordem das linhas acompanha a do
`candidates.csv`, ou seja, por score decrescente.

## Ordenação e limite do relatório

Depois dos filtros, os candidatos são ordenados por score decrescente. Empates
são resolvidos por identificador da sequência, fita e posição inicial, para que
duas execuções sobre a mesma entrada produzam exatamente a mesma ordem.

A tabela do relatório técnico mostra no máximo 50 candidatos, acompanhados de
uma nota com o total encontrado. As tabelas CSV e JSON continuam completas.

O limite existe por uma razão medida: sem ele, uma entrada de 50 kb gera um
relatório HTML de quase 2 MB, com mais de seis mil linhas de tabela, que
nenhum navegador apresenta de forma útil. A análise permanece completa; o que
muda é apenas o que o relatório exibe.

A ordenação serve para leitura, e não estabelece preferência biológica entre
os candidatos.

## Geração de arquivos

O pipeline gera:

```text
tables/sequences_summary.csv
tables/candidates.csv
tables/candidates.bed
tables/validation_summary.csv
json/validation.json
json/candidates.json
json/run_config.json
figures/candidates_per_sequence.png
figures/gc_distribution_candidates.png
figures/filter_status_summary.png
figures/candidate_density.png
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

Falhas inesperadas em qualquer outra etapa também são registradas. O
`run_pipeline` envolve a execução em um tratamento que grava a exceção com
rastreamento de pilha e encerra o log com `Fim da execucao com erro.`, antes de
propagar o erro para a CLI. A distinção entre as duas situações é feita pela
exceção `ValidationFailedError`: ela representa a interrupção prevista por
FASTA inválido, que já foi registrada em detalhe, e por isso não é relatada
como falha inesperada.

Sem esse tratamento, uma falha na etapa de geração de saídas encerrava a
execução com o log interrompido na validação, sem nenhum registro do erro.

## Reprodutibilidade registrada na saída

O `run_config.json` registra, além dos parâmetros da execução:

- `alvocas9_version`, a versão do software;
- `python_version`, a versão do interpretador;
- `executed_at`, a data e hora;
- `input_sha256`, o hash do arquivo de entrada.

Sem esses campos, dois arquivos de configuração idênticos podiam corresponder a
execuções diferentes, sobre arquivos diferentes ou versões diferentes do
software. Com eles, é possível afirmar que duas execuções usaram exatamente o
mesmo dado e o mesmo código.

O `input_sha256` fica vazio quando o arquivo de entrada não pode ser lido no
momento da escrita das saídas, em vez de interromper a execução.

A execução é determinística: a mesma entrada com os mesmos parâmetros produz
exatamente as mesmas saídas. As únicas exceções são `executed_at` e o carimbo
de data e hora do relatório.

## Testes

Os testes cobrem:

- leitura FASTA;
- validação;
- validação dos parâmetros de execução;
- reverso complementar;
- PAM;
- scanner na fita `+`;
- scanner na fita `-`;
- features;
- filtros;
- CLI;
- relatório;
- caminhos de erro, como arquivo inexistente, caminho que não é arquivo e arquivo sem registros;
- execução completa sem nenhum candidato.

O teste mais importante do ponto de vista técnico é o da fita reversa, porque valida o mapeamento de coordenadas para a sequência original.

O segundo mais importante é o da execução sem candidatos, porque exercita a
geração de tabelas, gráficos e relatórios com conjunto vazio, caminho em que o
pipeline precisa continuar funcionando em vez de quebrar.

O terceiro é o da verificação de linguagem: ele confirma que o gerador
realmente **recusa** escrever um relatório contendo qualquer uma das frases
proibidas. Até então, os testes só confirmavam que relatórios legítimos
passavam, e o controle nunca tinha sido visto falhando como deveria.
