# AlvoCas9

AlvoCas9 é um pipeline in silico e exploratório para triagem inicial de potenciais sítios-alvo CRISPR-Cas9 em sequências de DNA no formato FASTA.

O foco do projeto é computacional: leitura e validação de FASTA, busca de PAM, extração de candidatos, cálculo de características simples, filtros heurísticos e geração de resultados reprodutíveis. Ele não é uma ferramenta clínica, terapêutica ou experimental. Os candidatos identificados são apenas candidatos in silico e não constituem recomendação de uso em laboratório, humanos, animais, plantas ou qualquer aplicação real.

## O que o pipeline faz

- Lê arquivos FASTA com uma ou mais sequências de DNA.
- Valida identificadores, sequências vazias, caracteres permitidos e tamanho mínimo.
- Aceita apenas A, C, G e T por padrão.
- Permite aceitar N opcionalmente com `--allow-n`.
- Analisa fita direta e reversa complementar.
- Procura PAMs compatíveis com SpCas9 usando `NGG` como padrão.
- Extrai o protospacer de 20 nucleotídeos antes do PAM na orientação 5'->3' da fita analisada.
- Calcula GC%, contagem de N, homopolímeros, duplicatas exatas e score heurístico.
- Gera CSV, JSON, gráficos PNG, logs e relatório técnico em HTML/Markdown.

## O que o pipeline não faz

- Não valida eficiência real de edição.
- Não faz análise completa de off-target em genoma de referência.
- Não substitui ferramentas especializadas como CRISPOR ou CHOPCHOP.
- Não recomenda guias para uso experimental, clínico ou terapêutico.
- Não executa BLAST completo no MVP.

## Instalação

Requisitos:

- Python 3.11 ou superior.
- `matplotlib` para geração dos gráficos.
- `pytest` para testes.

Instalação em modo editável:

```bash
python -m pip install -e ".[dev]"
```

Caso prefira não instalar o pacote, use `PYTHONPATH=src` ao executar comandos locais.

No PowerShell:

```powershell
$env:PYTHONPATH = "src"
```

## Validar FASTA

```bash
python -m alvocas9 validate --input data/examples/exemplo_simples.fasta
```

Com N permitido:

```bash
python -m alvocas9 validate --input data/examples/exemplo_multiplas_sequencias.fasta --allow-n
```

## Executar análise completa

```bash
python -m alvocas9 analyze --input data/examples/exemplo_simples.fasta --output results/exemplo_simples
```

Com parâmetros explícitos:

```bash
python -m alvocas9 analyze --input data/examples/exemplo_simples.fasta --output results/exemplo_simples --pam NGG --target-length 20 --min-gc 40 --max-gc 60 --max-homopolymer 4
```

Com N aceito:

```bash
python -m alvocas9 analyze --input data/examples/exemplo_multiplas_sequencias.fasta --output results/exemplo_multiplas --allow-n
```

## Rodar testes

```bash
python -m pytest
```

## Saídas geradas

Após a análise, o diretório de resultados contém:

```text
results/
├── tables/
│   ├── sequences_summary.csv
│   ├── candidates.csv
│   └── validation_summary.csv
├── json/
│   ├── validation.json
│   ├── candidates.json
│   └── run_config.json
├── figures/
│   ├── candidates_per_sequence.png
│   ├── gc_distribution_candidates.png
│   └── filter_status_summary.png
├── reports/
│   ├── technical_report.html
│   └── technical_report.md
└── logs/
    └── pipeline.log
```

## Documentação principal

- `docs/EXPLICACAO_TECNICA_PIPELINE.md`: explicação módulo a módulo do código.
- `docs/GLOSSARIO.md`: definições curtas dos termos técnicos.
- `docs/MANUAL_USUARIO.md`: uso prático da CLI.
- `docs/ARQUITETURA.md`: organização dos módulos e fluxo de dados.
- `docs/LIMITACOES_ETICAS_E_TECNICAS.md`: limites técnicos e éticos do MVP.
- `docs/REFERENCIAS_BASE.md`: fontes de referência usadas para embasar o projeto.

## Aviso de escopo

Os resultados apresentados representam uma triagem computacional inicial baseada em padrões de sequência. Os candidatos identificados não constituem recomendação experimental, clínica ou terapêutica. A seleção real de guias CRISPR-Cas9 exige análises adicionais, incluindo avaliação de off-target em genoma de referência, contexto biológico, validação experimental e revisão especializada.
