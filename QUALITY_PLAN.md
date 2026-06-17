# QUALITY PLAN - AlvoCas9

## 1. Objetivo do plano de qualidade

Este plano define como validar o funcionamento do AlvoCas9, quais testes são obrigatórios, quais casos de borda devem ser cobertos e como reduzir o risco de erros em coordenadas, principalmente na fita reversa complementar.

O plano considera o projeto como ferramenta computacional in silico, exploratória e educacional. Nenhum teste deve tentar demonstrar segurança, eficácia clínica, uso terapêutico ou validação experimental.

## 2. Estratégia de testes

Tipos de teste:

- Testes unitários para funções pequenas.
- Testes de integração para o fluxo do pipeline.
- Testes de CLI para comandos principais.
- Testes de arquivos gerados.
- Testes de regressão para coordenadas da fita reversa.

Ferramenta recomendada:

- `pytest`.

Princípio:

Cada regra relevante da especificação deve ter pelo menos um teste automatizado ou uma verificação documentada.

## 3. Testes obrigatórios

### 3.1 Leitor FASTA

Testar:

- Um registro válido.
- Múltiplos registros.
- Sequência em várias linhas.
- Linhas vazias entre registros.
- Sequência antes do primeiro cabeçalho.
- Cabeçalho com descrição após identificador.

Critério de aceite:

- O leitor retorna identificador, descrição e sequência normalizada.
- Erros de parsing são reportados sem quebrar a execução de forma inesperada.

### 3.2 Validação FASTA

Testar:

- Arquivo inexistente.
- Arquivo vazio.
- FASTA sem registros.
- Registro sem identificador.
- Identificador duplicado.
- Sequência vazia.
- Sequência com caracteres inválidos.
- Sequência com N sem `allow_n`.
- Sequência com N com `allow_n`.
- Sequência menor que o tamanho mínimo.

Critério de aceite:

- Erros impedem análise.
- Avisos não impedem análise quando configurados.
- N é contado e reportado.

### 3.3 Utilitários de sequência

Testar:

- Reverso complementar de A, C, G, T.
- Reverso complementar contendo N.
- Sequência vazia.
- GC% de sequência sem GC.
- GC% de sequência 100% GC.
- GC% com N no denominador.
- Homopolímero simples.
- Homopolímero no início, meio e fim.

Critério de aceite:

- Resultados são previsíveis e documentados.

### 3.4 PAM

Testar:

- `AGG`, `CGG`, `GGG` e `TGG` contra `NGG`.
- Fragmentos que não casam com `NGG`.
- PAMs sobrepostos.
- Padrão PAM vazio.
- Código IUPAC inválido.
- Códigos IUPAC extras, se implementados: R, Y, S, W, K, M, B, D, H, V.

Critério de aceite:

- Busca encontra todos os PAMs esperados.
- Busca não encontra falsos positivos simples.
- Padrão inválido falha cedo.

### 3.5 Scanner na fita direta

Testar:

- PAM com exatamente 20 bases antes.
- PAM com menos de 20 bases antes.
- Mais de um PAM na mesma sequência.
- PAM no final da sequência.
- PAM sobreposto a outro PAM.
- Target length configurável.

Critério de aceite:

- Protospacer é extraído imediatamente antes do PAM.
- Coordenadas de saída são 1-based inclusivas.
- PAM sem upstream suficiente é ignorado e contabilizado.

### 3.6 Scanner na fita reversa complementar

Testar:

- Sequência original construída manualmente para gerar PAM no reverso complementar.
- Coordenadas mapeadas de volta para a sequência original.
- Protospacer exibido na orientação 5'->3' da fita analisada.
- PAM sem upstream suficiente no reverso complementar.
- Target length diferente de 20.

Critério de aceite:

- Coordenadas da fita reversa são coerentes com a sequência original.
- O intervalo completo do candidato cobre protospacer e PAM.
- Nenhum teste depende de interpretação visual ambígua.

### 3.7 Features

Testar:

- GC% do protospacer.
- Contagem de N.
- `has_n`.
- Homopolímero máximo.
- Duplicata exata dentro de uma sequência.
- Duplicata exata entre sequências diferentes.

Critério de aceite:

- Features são calculadas por candidato.
- Duplicatas são contadas no conjunto inteiro de entrada.

### 3.8 Filtros

Testar:

- Candidato dentro da faixa GC.
- Candidato abaixo do GC mínimo.
- Candidato acima do GC máximo.
- Candidato com N.
- Candidato com homopolímero acima do limite.
- Candidato duplicado.
- Combinação de penalidades.
- Score mínimo 0.
- Score máximo 100.

Critério de aceite:

- Penalidades seguem a especificação.
- Status usa apenas termos permitidos.
- Nenhum status usa termos clínicos ou terapêuticos.

### 3.9 Saídas

Testar:

- Criação de diretórios.
- Criação de CSV.
- Criação de JSON.
- Criação de gráficos.
- Criação de relatório HTML.
- Criação de relatório Markdown.
- Criação de log.
- Cabeçalho obrigatório de `candidates.csv`.
- Presença do texto obrigatório de limitação no relatório.

Critério de aceite:

- Todos os arquivos esperados são gerados.
- Arquivos podem ser abertos como texto ou imagem.
- Relatório referencia os gráficos.

### 3.10 CLI

Testar:

- `validate` com arquivo válido.
- `validate` com arquivo inválido.
- `analyze` com arquivo válido.
- `analyze` com `--allow-n`.
- `analyze` com PAM configurado.
- `analyze` com target length configurado.

Critério de aceite:

- Comandos retornam código de saída coerente.
- Erros são compreensíveis para o usuário.

## 4. Casos de borda

Casos de entrada:

- FASTA vazio.
- FASTA com apenas cabeçalho.
- FASTA com sequência antes de cabeçalho.
- FASTA com identificador duplicado.
- FASTA com espaços em linhas de sequência.
- FASTA com letras minúsculas.
- FASTA com N em modo padrão.
- FASTA com N em modo flexível.
- Sequência exatamente no tamanho mínimo.
- Sequência abaixo do tamanho mínimo.
- Sequência sem PAM.
- Sequência com PAM no início.
- Sequência com PAM no final.
- Sequência com PAMs sobrepostos.
- Sequência com múltiplos registros.

Casos de análise:

- Nenhum candidato extraído.
- Um único candidato.
- Muitos candidatos.
- Candidatos duplicados.
- Candidato com GC 0%.
- Candidato com GC 100%.
- Candidato com homopolímero longo.
- Candidato com N.
- PAM encontrado na fita direta.
- PAM encontrado apenas na fita reversa complementar.
- PAM encontrado nas duas fitas.

Casos de configuração:

- PAM `NGG`.
- PAM com IUPAC diferente de N.
- PAM inválido.
- Target length 20.
- Target length menor para teste manual.
- Faixa GC alterada.
- Limite de homopolímero alterado.

## 5. Como validar o funcionamento

Validação mínima antes de considerar a entrega pronta:

1. Rodar todos os testes:

```bash
python -m pytest
```

2. Rodar validação de exemplo:

```bash
python -m alvocas9 validate --input data/examples/exemplo_simples.fasta
```

3. Rodar análise de exemplo:

```bash
python -m alvocas9 analyze --input data/examples/exemplo_simples.fasta --output results/exemplo_simples
```

4. Conferir arquivos esperados:

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

5. Abrir `technical_report.html`.

6. Conferir se o relatório contém:

- Data/hora da execução.
- Configurações usadas.
- Resumo das sequências.
- Validação.
- Quantidade de PAMs.
- Quantidade de candidatos.
- Tabela de candidatos.
- Gráficos.
- Limitações.
- Texto obrigatório de limitação.

7. Conferir `candidates.csv`.

O cabeçalho deve conter:

```text
sequence_id,strand,protospacer_sequence_5to3,pam_sequence_5to3,protospacer_start_1based,protospacer_end_1based,pam_start_1based,pam_end_1based,full_candidate_start_1based,full_candidate_end_1based,target_length,pam_pattern,gc_percent,n_count,has_n,max_homopolymer_run,duplicate_exact_count_within_input,warnings,heuristic_score,filter_status
```

## 6. Como evitar erros de coordenada na fita reversa

Erros de coordenada na fita reversa são um dos maiores riscos do projeto. A estratégia deve ser:

### 6.1 Usar sequências pequenas e calculáveis manualmente

Criar testes com sequências curtas em que a posição do PAM seja óbvia.

Exemplo conceitual:

```text
Original: CCT + 20 bases T
Reverso complementar: 20 bases A + AGG
```

Nesse caso:

- Na fita reversa complementar, o PAM é `AGG`.
- Na sequência original, o PAM correspondente é `CCT` nas posições 1 a 3.
- O protospacer fica nas posições 4 a 23 da sequência original.

### 6.2 Separar coordenada interna e coordenada de saída

Regra:

- Internamente, Python usa 0-based e intervalo semiaberto `[start, end)`.
- Na saída, usar 1-based inclusivo.

Nunca misturar os dois modelos na mesma variável sem nome claro.

Nomes recomendados:

- `start_0`
- `end_0`
- `start_1based`
- `end_1based`

### 6.3 Documentar fórmula de mapeamento

Para intervalo `[start, end)` no reverso complementar:

```text
start_original_1based = original_length - end + 1
end_original_1based = original_length - start
```

Essa fórmula deve aparecer no código, na documentação técnica e nos testes.

### 6.4 Testar protospacer e PAM separadamente

Não validar apenas o intervalo completo. Validar:

- Início e fim do protospacer.
- Início e fim do PAM.
- Início e fim do candidato completo.
- Sequência do protospacer em orientação 5'->3'.
- Sequência do PAM em orientação 5'->3'.

### 6.5 Testar target length diferente de 20

Usar um teste com `target_length = 5` ajuda a conferir a fórmula de forma mais simples.

Exemplo:

```text
Original: CCTTTTT
RC:       AAAAAGG
```

Resultado esperado:

- PAM original: posições 1 a 3.
- Protospacer original: posições 4 a 8, se houver tamanho suficiente.

### 6.6 Evitar inferência visual

Não confiar apenas em inspeção manual de strings grandes. Cada teste deve ter valores esperados explícitos.

### 6.7 Criar teste de regressão obrigatório

Um teste chamado de forma clara, como `test_minus_strand_coordinates_map_to_original_sequence`, deve permanecer no projeto. Se esse teste falhar, a implementação não deve ser considerada válida.

## 7. Critérios gerais de aceite

O projeto só deve ser considerado pronto quando:

- Todos os testes passam.
- O exemplo principal executa sem erro.
- Todos os arquivos esperados são gerados.
- O relatório HTML abre e contém tabelas e gráficos.
- `candidates.csv` contém todas as colunas obrigatórias.
- O log é gerado.
- A documentação técnica explica o projeto e suas limitações.
- As limitações estão explícitas.
- Nenhum texto chama candidatos de seguros, eficientes, clínicos, terapêuticos ou recomendados.

## 8. Checklist de revisão manual

Antes de publicar ou entregar o software:

- Revisar README.
- Revisar SPEC.
- Revisar ROADMAP.
- Revisar QUALITY_PLAN.
- Rodar testes em ambiente limpo.
- Rodar exemplo.
- Conferir relatório técnico.
- Conferir documentação técnica.
- Conferir referências.
- Ensaiar explicação de fita reversa complementar.
- Ensaiar explicação das limitações.
