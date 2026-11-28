# QUALITY_CHECKLIST - AlvoCas9

Checklist de qualidade do projeto de software AlvoCas9.

## Escopo atual do repositório

O repositório contém somente o projeto de software, seus testes, exemplos de entrada e documentação técnica do pipeline.

## Arquivos mantidos

### Projeto Python

- `pyproject.toml`
- `src/alvocas9/__init__.py`
- `src/alvocas9/__main__.py`
- `src/alvocas9/cli.py`
- `src/alvocas9/config.py`
- `src/alvocas9/io/fasta_reader.py`
- `src/alvocas9/validation/dna_validator.py`
- `src/alvocas9/core/sequence_utils.py`
- `src/alvocas9/core/pam.py`
- `src/alvocas9/core/scanner.py`
- `src/alvocas9/analysis/features.py`
- `src/alvocas9/analysis/filters.py`
- `src/alvocas9/visualization/plots.py`
- `src/alvocas9/reporting/report_generator.py`
- `src/alvocas9/reporting/templates/technical_report.html.j2`
- `src/alvocas9/reporting/templates/technical_report.md.j2`
- `src/alvocas9/utils/logging_utils.py`

### Testes

- `tests/test_package_import.py`
- `tests/test_cli.py`
- `tests/test_config.py`
- `tests/test_fasta_reader.py`
- `tests/test_dna_validator.py`
- `tests/test_sequence_utils.py`
- `tests/test_pam.py`
- `tests/test_scanner_plus_strand.py`
- `tests/test_scanner_minus_strand.py`
- `tests/test_features.py`
- `tests/test_filters.py`
- `tests/test_report_generator.py`
- `tests/test_real_sequence.py`

### Resultados de referência versionados

- `docs/resultados_referencia/ade2/` com as 14 saídas da execução sobre o gene ADE2
- `docs/resultados_referencia/README.md`

### Dados e scripts

- `data/examples/exemplo_simples.fasta`
- `data/examples/exemplo_multiplas_sequencias.fasta`
- `data/examples/exemplo_com_erros.fasta`
- `data/examples/exemplo_sem_pam.fasta`
- `data/real/ADE2_scerevisiae.fasta`
- `data/real/README.md`
- `scripts/run_example.py`
- `scripts/gerar_figura_arquitetura.py`
- `scripts/benchmark_busca_pam.py`
- `scripts/verificar_coordenadas.py`

### Documentação técnica mantida

- `README.md`
- `SPEC.md`
- `ROADMAP.md`
- `QUALITY_PLAN.md`
- `docs/ARQUITETURA.md`
- `docs/EXPLICACAO_TECNICA_PIPELINE.md`
- `docs/GLOSSARIO.md`
- `docs/MANUAL_USUARIO.md`
- `docs/LIMITACOES_ETICAS_E_TECNICAS.md`
- `docs/REFERENCIAS_BASE.md`
- `docs/DESEMPENHO_E_COMPLEXIDADE.md`
- `docs/DESEMPENHO_MEDIDO.md`
- `docs/figuras/arquitetura_pipeline.png`

## Comandos testados

Testes automatizados:

```bash
python -m pytest --cov=alvocas9 --cov-report=term
```

Resultado:

```text
119 passed in 32.74s, com 99% de cobertura
```

Validação FASTA:

```bash
python -m alvocas9 validate --input data/examples/exemplo_simples.fasta
```

Resultado:

```text
Valido: True
Registros: 1
Erros: 0
Avisos: 0
```

Análise completa:

```bash
python -m alvocas9 analyze --input data/examples/exemplo_simples.fasta --output results/exemplo_simples
```

Resultado:

- comando executado com código de saída 0;
- todos os arquivos esperados foram gerados;
- resumo da execução impresso no terminal.

Análise da sequência biológica real:

```bash
python -m alvocas9 analyze --input data/real/ADE2_scerevisiae.fasta --output results/ade2
```

Resultado:

```text
Sequencias lidas: 1
Avisos de validacao: 0
PAMs encontrados: 142
Candidatos extraidos: 140
  aprovado nos filtros básicos: 80
  requer cautela: 60
```

- validação sem erros nem avisos;
- 2 PAMs descartados por falta de bases antes deles;
- números protegidos por `tests/test_real_sequence.py`.

Verificação independente das coordenadas:

```bash
python scripts/verificar_coordenadas.py
```

Resultado:

```text
TOTAL: 405 candidato(s) conferido(s), 0 divergencia(s).
RESULTADO: OK. Todas as coordenadas conferem com a sequencia original.
```

Benchmark da busca de PAM:

```bash
python scripts/benchmark_busca_pam.py --saida docs/DESEMPENHO_MEDIDO.md
```

Resultado:

- as três implementações produziram as mesmas posições em todos os tamanhos;
- tabelas gravadas em `docs/DESEMPENHO_MEDIDO.md`.

Geração da figura de arquitetura:

```bash
python scripts/gerar_figura_arquitetura.py
```

Resultado:

- `docs/figuras/arquitetura_pipeline.png` gravado.

Parâmetros inválidos:

```bash
python -m alvocas9 analyze --input data/examples/exemplo_simples.fasta --output results/teste --target-length -5
```

Resultado:

```text
Erro: Parametros invalidos: target_length deve ser maior ou igual a 1. Valor informado: -5.
```

- código de saída 1;
- nenhum arquivo gerado.

## Arquivos de saída confirmados

Na execução de smoke test, foram confirmados:

- `tables/sequences_summary.csv`
- `tables/candidates.csv`
- `tables/validation_summary.csv`
- `json/validation.json`
- `json/candidates.json`
- `json/run_config.json`
- `figures/candidates_per_sequence.png`
- `figures/gc_distribution_candidates.png`
- `figures/filter_status_summary.png`
- `reports/technical_report.html`
- `reports/technical_report.md`
- `logs/pipeline.log`

## Limitações mantidas

O projeto continua explicitamente limitado:

- não é ferramenta clínica;
- não é ferramenta terapêutica;
- não é protocolo experimental;
- não recomenda guias CRISPR para uso real;
- não garante eficiência;
- não garante segurança;
- não executa off-target genômico completo;
- não substitui ferramentas especializadas como CRISPOR ou CHOPCHOP;
- não substitui validação experimental.
