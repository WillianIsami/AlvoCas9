# Manual do usuário

Este manual explica como instalar, executar e interpretar o AlvoCas9.

## Requisitos

- Python 3.11 ou superior.
- Ambiente de terminal.
- Dependências do projeto instaladas pelo `pyproject.toml`, que inclui `matplotlib` para os gráficos e `tzdata` para a base de fusos horários do relatório.

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

## Resumo impresso no terminal

Uma análise bem-sucedida termina imprimindo o resumo da execução:

```text
Analise concluida.
Sequencias lidas: 3
Avisos de validacao: 1
PAMs encontrados: 11
Candidatos extraidos: 7
  aprovado nos filtros básicos: 5
  requer cautela: 2
Resultados em: results/example_multiplas
Relatorio: results/example_multiplas/reports/technical_report.html
```

Como ler esse resumo:

- `Sequencias lidas` é o número de registros FASTA aceitos.
- `Avisos de validacao` indica situações que merecem atenção sem impedir a análise.
- `PAMs encontrados` conta todos os PAMs compatíveis nas duas fitas.
- `Candidatos extraidos` conta apenas os PAMs que tinham bases suficientes antes deles. A diferença entre os dois números são os PAMs descartados.
- As linhas recuadas mostram quantos candidatos ficaram em cada status dos filtros.

Se o terminal exibir os acentos de forma estranha, a causa é a configuração de
codificação do console. Os arquivos de saída são sempre gravados em UTF-8.

## Arquivos de exemplo

`exemplo_simples.fasta`

Arquivo válido com uma sequência e PAMs.

`exemplo_multiplas_sequencias.fasta`

Arquivo com múltiplas sequências, incluindo exemplo com N.

`exemplo_com_erros.fasta`

Arquivo propositalmente inválido para testar validação.

`exemplo_sem_pam.fasta`

Arquivo válido sem candidatos esperados.

## Sequência biológica real

Além dos exemplos sintéticos, o projeto inclui uma sequência pública curada em
`data/real/ADE2_scerevisiae.fasta`: o gene ADE2 de *Saccharomyces cerevisiae*,
com 1.716 pares de base. A procedência, os checksums e as verificações feitas
estão em `data/real/README.md`.

```powershell
python -m alvocas9 analyze --input data/real/ADE2_scerevisiae.fasta --output results/ade2
```

## Interpretação das saídas

`tables/candidates.csv`

Tabela principal de candidatos, completa e ordenada por score decrescente. Use
para conferir sequência, fita, coordenadas, sítio de corte, GC%, warnings,
score e status.

A coluna `cut_site_1based` informa a posição da base imediatamente anterior ao
corte previsto, na sequência original: o corte ocorre entre essa posição e a
seguinte. Vem do modelo da SpCas9, que corta cerca de 3 pares de base antes do
PAM. A coluna fica vazia quando a posição cairia fora da sequência.

A coluna `relative_position_percent` informa onde o ponto médio do candidato
está na sequência, de 0 a 100%. Serve para saber se o sítio está perto do
início, no meio ou perto do fim. Não entra no score e não é critério de
qualidade: a leitura comum em desenho de guias, de que sítios na porção inicial
da região codificante tendem a ser preferidos para nocaute, só vale quando a
entrada é de fato um gene na orientação codificante.

`tables/candidates.bed`

Os mesmos candidatos em formato BED, com seis colunas separadas por tabulação e
sem cabeçalho, prontos para carregar em um navegador genômico. Atenção à
diferença de convenção: o BED usa coordenadas **0-based semiabertas**, enquanto
as tabelas CSV e JSON usam **1-based inclusivas**. Por isso o início aparece
diminuído de uma unidade no BED. O score do BED é o score heurístico
multiplicado por dez, porque a faixa do formato vai de 0 a 1000.

`tables/sequences_summary.csv`

Resumo por sequência de entrada.

`tables/validation_summary.csv`

Mensagens de validação.

`json/validation.json`

Resultado estruturado da validação. Útil para depuração. Cada registro é
descrito por identificador, descrição, tamanho e hash SHA-256 da sequência. O
hash permite conferir a identidade do dado sem que o arquivo vire uma segunda
cópia do FASTA de entrada.

`json/candidates.json`

Candidatos em formato estruturado.

`json/run_config.json`

Configurações usadas na execução, junto com o que é preciso para repeti-la:
versão do AlvoCas9, versão do Python, data e hora, e o hash SHA-256 do arquivo
de entrada. O hash permite confirmar que uma nova execução usou exatamente o
mesmo dado.

O campo `executed_at` muda a cada execução, por definição. É o único campo de
saída não determinístico, junto com o carimbo do relatório.

`figures/*.png`

Quatro gráficos gerados pelo pipeline: candidatos por sequência, distribuição
de GC%, resumo dos status dos filtros e distribuição dos candidatos ao longo da
sequência.

`reports/technical_report.html`

Relatório principal para leitura. A tabela de candidatos mostra no máximo 50
linhas, as de maior score, com uma nota informando o total. Para ver todos os
candidatos, use o CSV ou o JSON.

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

**Parâmetros inválidos**

A mensagem começa com `Erro: Parametros invalidos:` e lista todos os problemas
encontrados de uma vez. Nenhum arquivo é gerado nesse caso. As regras são
`--target-length` maior ou igual a 1, GC entre 0 e 100 com `--min-gc` não maior
que `--max-gc`, `--max-homopolymer` maior ou igual a 1 e
`--min-sequence-length` maior ou igual a 1.

**Posição de PAM não suportada**

O parâmetro `--pam-position` aceita apenas `3linha`. O pipeline extrai o
protospacer a 5' do PAM, premissa válida para a SpCas9. Sistemas com PAM a 5',
como Cas12a, exigiriam outra lógica de extração e não são suportados.

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

Com medição de cobertura:

```powershell
python -m pytest --cov=alvocas9 --cov-report=term-missing
```
