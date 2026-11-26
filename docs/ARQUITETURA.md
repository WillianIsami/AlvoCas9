# Arquitetura do AlvoCas9

O AlvoCas9 foi estruturado como um pacote Python simples, com separação entre entrada, validação, núcleo de análise, filtros, visualização, relatório e interface de linha de comando.

## Visão geral

```text
FASTA
  |
  v
CLI -> PipelineConfig
  |
  v
Leitura FASTA
  |
  v
Validação
  |
  +--> erro crítico: validation.json + log + encerramento
  |
  v
Scanner PAM nas fitas + e -
  |
  v
Features dos candidatos
  |
  v
Filtros e score
  |
  v
CSV / JSON / PNG / HTML / Markdown / log
```

A mesma visão geral está disponível como figura em
`docs/figuras/arquitetura_pipeline.png`, gerada por
`scripts/gerar_figura_arquitetura.py`. A figura é produzida por script, e não
desenhada à mão, para poder ser regerada quando a estrutura mudar.

## Módulos e responsabilidades

`src/alvocas9/cli.py`

Define os comandos `validate` e `analyze`. É a entrada principal do usuário.

`src/alvocas9/config.py`

Define `PipelineConfig`, que concentra parâmetros da execução e valida seus
valores antes do início da análise.

`src/alvocas9/io/fasta_reader.py`

Lê FASTA e retorna registros com `identifier`, `description` e `sequence`.

`src/alvocas9/validation/dna_validator.py`

Valida arquivo e registros. Separa erros globais, avisos globais, erros por registro e avisos por registro.

`src/alvocas9/core/sequence_utils.py`

Contém funções básicas: reverso complementar, GC% e homopolímero máximo.

`src/alvocas9/core/pam.py`

Valida padrões PAM, converte IUPAC para regras de busca e localiza os PAMs.
Mantém duas implementações equivalentes da busca, uma com expressão regular,
usada pelo pipeline, e uma por varredura direta, usada como referência.

`src/alvocas9/core/scanner.py`

Busca PAMs, extrai candidatos e calcula coordenadas 1-based inclusivas.

`src/alvocas9/analysis/features.py`

Calcula características dos candidatos.

`src/alvocas9/analysis/filters.py`

Aplica filtros básicos e score heurístico.

`src/alvocas9/visualization/plots.py`

Gera gráficos PNG.

`src/alvocas9/reporting/report_generator.py`

Gera tabelas, JSON, relatório HTML e relatório Markdown.

`src/alvocas9/utils/logging_utils.py`

Configura o log da execução.

## Fluxo de dados

1. O usuário informa um FASTA.
2. A CLI transforma argumentos em `PipelineConfig`, que valida os parâmetros.
3. O validador lê e avalia o FASTA.
4. Registros válidos seguem para o scanner.
5. O scanner retorna candidatos brutos.
6. Features e filtros enriquecem os candidatos.
7. O gerador salva resultados em múltiplos formatos.
8. O pipeline devolve um `RunSummary`, que a CLI imprime no terminal.

## Estrutura de pastas

```text
src/alvocas9/
├── cli.py
├── config.py
├── io/
├── validation/
├── core/
├── analysis/
├── visualization/
├── reporting/
└── utils/
```

Pastas auxiliares:

```text
data/examples/   arquivos FASTA de exemplo
tests/           testes automatizados
docs/            documentação técnica
scripts/         scripts auxiliares
results/         saídas geradas
```

## Decisões de projeto

- Usar Python 3.11+ por legibilidade e suporte moderno.
- Manter leitura FASTA própria para deixar a validação explícita no código.
- Evitar dependências pesadas.
- Usar CLI como interface principal.
- Usar coordenadas 1-based inclusivas na saída.
- Tratar erro crítico de validação como bloqueio da análise.
- Validar os parâmetros da execução antes de qualquer leitura de arquivo.
- Registrar no log qualquer falha, prevista ou inesperada.
- Manter a escrita em tela na CLI: o pipeline devolve um resumo, não imprime.
- Registrar configuração e logs para reprodutibilidade.
- Gerar relatórios com linguagem conservadora.

## Por que não usar arquitetura mais complexa

O projeto foi mantido como um MVP de linha de comando. Uma arquitetura com banco de dados, filas, API web ou microsserviços aumentaria complexidade sem melhorar o objetivo do pipeline. A divisão atual é suficiente para testar e manter cada parte com baixo acoplamento.
