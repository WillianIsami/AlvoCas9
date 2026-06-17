# Manual do usuário

Este manual explica como instalar, executar e interpretar o AlvoCas9.

## Requisitos

- Python 3.11 ou superior.
- Ambiente de terminal.
- Dependências do projeto instaladas pelo `pyproject.toml`.

## Instalação

Na raiz do projeto:

```powershell
python -m pip install -e ".[dev]"
```

Esse comando instala o pacote em modo editável e instala dependências de teste.

## Verificar a CLI

```powershell
python -m alvocas9 --help
```

Comandos disponíveis:

- `validate`: valida FASTA.
- `analyze`: executa o pipeline completo.

## Validar um FASTA

```powershell
python -m alvocas9 validate --input data/examples/exemplo_simples.fasta
```

Com N permitido:

```powershell
python -m alvocas9 validate --input data/examples/exemplo_multiplas_sequencias.fasta --allow-n
```

## Executar análise completa

```powershell
python -m alvocas9 analyze --input data/examples/exemplo_simples.fasta --output results/example
```

Com opções explícitas:

```powershell
python -m alvocas9 analyze `
  --input data/examples/exemplo_simples.fasta `
  --output results/example `
  --pam NGG `
  --target-length 20 `
  --min-gc 40 `
  --max-gc 60 `
  --max-homopolymer 4
```

Com N permitido:

```powershell
python -m alvocas9 analyze --input data/examples/exemplo_multiplas_sequencias.fasta --output results/example_multiplas --allow-n
```

## Arquivos de exemplo

`exemplo_simples.fasta`

Arquivo válido com uma sequência e PAMs.

`exemplo_multiplas_sequencias.fasta`

Arquivo com múltiplas sequências, incluindo exemplo com N.

`exemplo_com_erros.fasta`

Arquivo propositalmente inválido para testar validação.

`exemplo_sem_pam.fasta`

Arquivo válido sem candidatos esperados.

## Interpretação das saídas

`tables/candidates.csv`

Tabela principal de candidatos. Use para conferir sequência, fita, coordenadas, GC%, warnings, score e status.

`tables/sequences_summary.csv`

Resumo por sequência de entrada.

`tables/validation_summary.csv`

Mensagens de validação.

`json/validation.json`

Resultado estruturado da validação. Útil para depuração.

`json/candidates.json`

Candidatos em formato estruturado.

`json/run_config.json`

Configurações usadas na execução.

`figures/*.png`

Gráficos gerados pelo pipeline.

`reports/technical_report.html`

Relatório principal para leitura.

`reports/technical_report.md`

Versão Markdown do relatório.

`logs/pipeline.log`

Registro da execução.

## Status dos filtros

`aprovado nos filtros básicos`

O candidato não disparou alertas relevantes dentro das regras simples do MVP.

`requer cautela`

O candidato disparou alertas moderados, como GC fora da faixa, homopolímero longo ou duplicação.

`reprovado nos filtros básicos`

O candidato falhou por condição crítica ou score baixo.

Nenhum status significa validação experimental.

## Erros comuns

**Erro: arquivo não existe**

Confira o caminho em `--input`.

**FASTA inválido**

Abra `results/.../json/validation.json` e `results/.../logs/pipeline.log`.

**N rejeitado**

Use `--allow-n` se a entrada deve aceitar base desconhecida.

**Sem candidatos**

Pode ser normal. O arquivo pode não ter PAM com bases suficientes antes dele.

**Acentos estranhos no terminal**

Pode ser configuração do PowerShell. Os arquivos são gravados em UTF-8.

## Como rodar testes

```powershell
python -m pytest
```
