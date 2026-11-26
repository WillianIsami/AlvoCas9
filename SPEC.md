# SPEC - AlvoCas9

## 1. Objetivo do projeto

O AlvoCas9 tem como objetivo desenvolver um pipeline computacional in silico para triagem inicial e caracterização de potenciais sítios-alvo CRISPR-Cas9 em sequências gênicas representadas no formato FASTA.

O foco principal é computacional: validação de dados, processamento de sequências, busca por padrões, geração de resultados estruturados, testes automatizados, documentação e reprodutibilidade.

O projeto não deve ser apresentado como ferramenta clínica, terapêutica ou experimental.

## 2. Escopo

O MVP deve:

- Receber arquivos FASTA contendo uma ou mais sequências de DNA.
- Validar a integridade computacional do arquivo e das sequências.
- Aceitar A, C, G e T como bases válidas por padrão.
- Permitir modo flexível para aceitar N como base desconhecida.
- Calcular estatísticas básicas das sequências.
- Gerar reverso complementar.
- Procurar PAMs compatíveis com SpCas9, usando `NGG` como padrão inicial.
- Analisar fita direta e fita reversa complementar.
- Extrair protospacers adjacentes ao PAM.
- Calcular características simples dos candidatos.
- Aplicar filtros heurísticos transparentes.
- Gerar resultados em CSV, JSON, gráficos, logs e relatório técnico.
- Produzir documentação técnica suficiente para instalação, execução, compreensão do pipeline e registro das limitações.

## 3. Fora de escopo

Não faz parte do MVP:

- Recomendação de guias CRISPR para uso real.
- Validação experimental.
- Validação clínica ou terapêutica.
- Predição definitiva de eficiência de edição.
- Análise completa de off-target em genoma humano ou genoma de referência.
- BLAST completo.
- Banco de dados remoto obrigatório.
- Dependência obrigatória de internet.
- Interface web ou interface gráfica.
- Uso de GPU.
- Protocolos de laboratório.
- Promessas de segurança, eficácia ou aplicabilidade médica.

## 4. Requisitos funcionais

RF01 - Ler arquivo FASTA informado pelo usuário.

RF02 - Aceitar FASTA com uma ou múltiplas sequências.

RF03 - Validar se o arquivo existe.

RF04 - Validar se o arquivo não está vazio.

RF05 - Validar se cada cabeçalho FASTA começa com `>`.

RF06 - Validar se cada registro possui identificador.

RF07 - Detectar identificadores duplicados.

RF08 - Validar se cada registro possui sequência não vazia.

RF09 - Validar caracteres permitidos na sequência.

RF10 - Aceitar apenas A, C, G e T por padrão.

RF11 - Permitir aceitar N com configuração explícita.

RF12 - Calcular proporção de N por sequência.

RF13 - Diferenciar erros e avisos de validação.

RF14 - Calcular tamanho da sequência.

RF15 - Calcular GC% da sequência.

RF16 - Gerar reverso complementar da sequência.

RF17 - Procurar PAMs na fita direta.

RF18 - Procurar PAMs na fita reversa complementar.

RF19 - Usar `NGG` como PAM padrão.

RF20 - Permitir configurar o padrão PAM.

RF21 - Suportar códigos IUPAC simples no PAM, pelo menos N, A, C, G e T.

RF22 - Extrair protospacer imediatamente antes do PAM na orientação 5'->3' da fita analisada.

RF23 - Permitir configurar tamanho do protospacer, com padrão 20.

RF24 - Ignorar PAMs sem bases suficientes antes dele para extrair o protospacer.

RF25 - Registrar estatística de PAMs ignorados por falta de sequência upstream.

RF26 - Gerar candidatos com coordenadas 1-based inclusivas.

RF27 - Mapear corretamente coordenadas da fita reversa complementar para a sequência original.

RF28 - Calcular GC% do protospacer candidato.

RF29 - Calcular contagem de N do candidato.

RF30 - Identificar se o candidato possui N.

RF31 - Calcular maior homopolímero do candidato.

RF32 - Calcular duplicação exata do protospacer dentro do conjunto de entrada.

RF33 - Aplicar filtros heurísticos configuráveis.

RF34 - Calcular score heurístico transparente.

RF35 - Classificar candidatos como `aprovado nos filtros básicos`, `requer cautela` ou `reprovado nos filtros básicos`.

RF36 - Gerar tabelas CSV.

RF37 - Gerar arquivos JSON.

RF38 - Gerar gráficos PNG.

RF39 - Gerar relatório técnico em HTML e Markdown.

RF40 - Gerar log da execução.

RF41 - Disponibilizar comandos por CLI.

## 5. Requisitos não funcionais

RNF01 - Usar Python 3.11 ou superior.

RNF02 - Manter código simples, modular e didático.

RNF03 - Evitar dependências pesadas.

RNF04 - Não exigir internet para execução do MVP.

RNF05 - Não exigir GPU.

RNF06 - Ser executável por linha de comando.

RNF07 - Ter testes unitários para regras principais.

RNF08 - Ter documentação em português brasileiro.

RNF09 - Gerar saídas reprodutíveis.

RNF10 - Manter configuração da execução salva em arquivo, junto com versão do
software, versão do Python, data e hora e hash SHA-256 da entrada.

RNF11 - Evitar linguagem que indique recomendação clínica, terapêutica ou experimental.

RNF12 - Usar nomes claros para funções, arquivos e campos de saída.

RNF13 - Usar type hints quando ajudarem a compreensão.

RNF14 - Separar validação, análise, filtros, visualização e relatório em módulos distintos.

## 6. Arquitetura

Arquitetura proposta em camadas:

```text
CLI
 |
 v
Configuração da execução
 |
 v
Leitura FASTA
 |
 v
Validação computacional
 |
 v
Análise de sequências
 |
 +--> Fita direta
 |
 +--> Fita reversa complementar
 |
 v
Busca PAM e extração de candidatos
 |
 v
Cálculo de características
 |
 v
Filtros heurísticos
 |
 v
CSV / JSON / gráficos / relatório / logs
```

Responsabilidades principais:

- `cli`: interface de linha de comando.
- `config`: parâmetros da execução.
- `io`: leitura de FASTA.
- `validation`: validação de entrada.
- `core`: operações centrais de sequência, PAM e scanner.
- `analysis`: features e filtros.
- `visualization`: gráficos.
- `reporting`: relatórios e arquivos de saída.
- `utils`: utilitários gerais.

## 7. Estrutura de pastas

Estrutura planejada:

```text
alvocas9/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── SPEC.md
├── ROADMAP.md
├── QUALITY_PLAN.md
├── data/
│   └── examples/
├── src/
│   └── alvocas9/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── io/
│       ├── validation/
│       ├── core/
│       ├── analysis/
│       ├── reporting/
│       ├── visualization/
│       └── utils/
├── tests/
├── docs/
└── scripts/
```

## 8. Dados de entrada

Entrada principal:

- Arquivo FASTA de DNA.

Exemplo:

```text
>gene_exemplo
ATGCGTACGTAGCTAGCTAGAGG
```

Configurações de entrada:

- Caminho do FASTA.
- Diretório de saída.
- PAM, padrão `NGG`.
- Posição do PAM, padrão `3linha` e único valor aceito.
- Tamanho do protospacer, padrão 20.
- GC mínimo, padrão 40%.
- GC máximo, padrão 60%.
- Limite de homopolímero, padrão 4.
- Modo `allow_n`.
- Tamanho mínimo de sequência.

## 9. Dados de saída

Estrutura esperada de saída:

```text
results/
├── tables/
│   ├── sequences_summary.csv
│   ├── candidates.csv
│   ├── candidates.bed
│   └── validation_summary.csv
├── json/
│   ├── validation.json
│   ├── candidates.json
│   └── run_config.json
├── figures/
│   ├── candidates_per_sequence.png
│   ├── gc_distribution_candidates.png
│   ├── filter_status_summary.png
│   └── candidate_density.png
├── reports/
│   ├── technical_report.html
│   └── technical_report.md
└── logs/
    └── pipeline.log
```

Campos obrigatórios em `candidates.csv`:

- `sequence_id`
- `strand`
- `protospacer_sequence_5to3`
- `pam_sequence_5to3`
- `protospacer_start_1based`
- `protospacer_end_1based`
- `pam_start_1based`
- `pam_end_1based`
- `cut_site_1based`
- `full_candidate_start_1based`
- `full_candidate_end_1based`
- `relative_position_percent`
- `target_length`
- `pam_pattern`
- `gc_percent`
- `n_count`
- `has_n`
- `max_homopolymer_run`
- `duplicate_exact_count_within_input`
- `warnings`
- `heuristic_score`
- `filter_status`

## 10. Regras de validação FASTA

Regras com erro, que interrompem a análise antes da busca de PAM:

- Arquivo inexistente.
- Caminho não é arquivo.
- Arquivo vazio.
- Linha de sequência antes do primeiro cabeçalho.
- Nenhum registro encontrado.
- Cabeçalho sem identificador.
- Identificador duplicado.
- Sequência vazia.
- Caracteres fora do conjunto permitido.

Regras com aviso, que não interrompem a análise:

- Sequência menor que o tamanho mínimo configurado.
- Presença de N quando `allow_n` estiver habilitado.
- Proporção de N igual ou superior ao limite configurado.

O tamanho mínimo é aviso, e não erro, porque uma sequência curta continua
analisável: ela apenas não produz candidatos quando não há bases suficientes
antes do PAM, situação já contabilizada nas estatísticas do scanner.

Caracteres permitidos:

- Modo padrão: A, C, G, T.
- Modo flexível: A, C, G, T, N.

Normalizações:

- Converter bases para maiúsculas.
- Ignorar linhas vazias.

O leitor FASTA **não** remove espaços, tabulações ou outros caracteres das
linhas de sequência. Eles são preservados de propósito, para que a validação
possa reportá-los como caracteres não permitidos, em vez de corrigir a
entrada em silêncio. Espaço e tabulação são exibidos nas mensagens como
`<espaco>` e `<tab>`.

## 11. Regras de busca PAM

Padrão inicial:

- SpCas9 com PAM `NGG`.

Interpretação de `NGG`:

- `N`: qualquer base aceita.
- `G`: guanina.
- `G`: guanina.

Busca:

- Percorrer a sequência com janela do tamanho do PAM.
- Permitir PAMs sobrepostos.
- Buscar na fita direta.
- Calcular reverso complementar e buscar na fita reversa complementar.
- Validar padrão PAM antes de executar.

Posição do PAM:

- O protospacer é sempre extraído a 5' do PAM, premissa válida para SpCas9.
- O parâmetro `pam_position` aceita apenas `3linha`. Qualquer outro valor é
  recusado com mensagem explicando a limitação.
- A premissa fica declarada na interface, e não apenas na documentação, para
  que um padrão de sistema com PAM a 5', como o `TTTV` de Cas12a, não produza
  resultado silenciosamente sem sentido.

Códigos IUPAC planejados para PAM:

- Obrigatórios: A, C, G, T, N.
- Desejáveis: R, Y, S, W, K, M, B, D, H, V.

## 12. Regras de extração de candidatos

Para cada PAM encontrado:

- Definir `pam_start` como índice interno 0-based da fita analisada.
- Verificar se existem `target_length` bases antes do PAM.
- Se não houver bases suficientes, ignorar o PAM e registrar estatística.
- Extrair protospacer de `pam_start - target_length` até `pam_start - 1`.
- Informar protospacer sempre em orientação 5'->3' da fita analisada.
- Informar PAM sempre em orientação 5'->3' da fita analisada.
- Informar o sítio de corte previsto, mapeado para a sequência original.

Sítio de corte:

- Para SpCas9, o corte de dupla-fita ocorre cerca de 3 pares de base a 5' do
  PAM, isto é, entre as posições 17 e 18 de um protospacer de 20 nucleotídeos.
- O campo `cut_site_1based` informa a posição da base imediatamente anterior ao
  corte, na sequência original. O corte ocorre entre essa posição e a seguinte.
- Na fita direta, a posição é `pam_start_1based - 4`. Na fita reversa
  complementar, o PAM aparece em coordenadas menores, e a posição é
  `pam_end_1based + 3`.
- O campo fica vazio quando a posição cairia fora da sequência.
- O valor é uma premissa do modelo, válida para sistemas com PAM a 3', e não
  uma medição feita pelo pipeline.

Coordenadas:

- Saídas sempre 1-based inclusivas.
- Fita direta: coordenadas derivadas diretamente da sequência original.
- Fita reversa complementar: coordenadas mapeadas de volta para a sequência original.

Mapeamento da fita reversa:

Para intervalo 0-based `[start, end)` no reverso complementar:

```text
start_original_1based = original_length - end + 1
end_original_1based = original_length - start
```

## 13. Regras de filtros

Filtros padrão:

- GC mínimo: 40%.
- GC máximo: 60%.
- Candidato com N deve ser reprovado ou receber alerta, conforme configuração.
- Homopolímero maior que 4 deve gerar alerta.
- Protospacer duplicado exatamente dentro da entrada deve gerar alerta.

Status permitidos:

- `aprovado nos filtros básicos`
- `requer cautela`
- `reprovado nos filtros básicos`

Linguagem dos relatórios.

A verificação é automatizada e atua sobre **frases afirmativas** completas. O
gerador recusa escrever o relatório se o texto produzido contiver qualquer uma
delas, conforme `FORBIDDEN_REPORT_TERMS` em `reporting/report_generator.py`:

- `guia recomendado`
- `guia validado`
- `alvo seguro`
- `alvo recomendado`
- `aplicação clínica`
- `uso terapêutico`
- `eficiência garantida`
- `pronto para uso experimental`

A verificação é por frase, e não por palavra isolada, porque o próprio texto
obrigatório de limitação contém as palavras "clínica" e "terapêutica" ao negar
essas aplicações. Bloquear palavras isoladas impediria o relatório de declarar
suas próprias limitações.

Orientação de redação, aplicada pelo autor e não verificável por software: ao
descrever candidatos, evitar os adjetivos "seguro", "eficiente", "recomendado"
e "validado", bem como os qualificadores "clínico" e "terapêutico". Os termos
preferidos estão em `docs/LIMITACOES_ETICAS_E_TECNICAS.md`.

Score heurístico:

- Começar em 100.
- Subtrair 20 se GC% estiver fora da faixa configurada.
- Subtrair 25 se houver N.
- Subtrair 10 se homopolímero máximo for maior que o limite configurado.
- Subtrair 20 se duplicata exata for maior que 1.
- Limitar entre 0 e 100.

O score não prediz eficiência real de edição.

Ordenação e apresentação:

- Os candidatos são ordenados por score decrescente antes da escrita.
- Empates são resolvidos por identificador da sequência, fita e posição
  inicial, para que a ordem seja determinística.
- A tabela do relatório técnico mostra no máximo 50 candidatos, com nota
  indicando o total. As tabelas CSV e JSON permanecem completas.
- A ordenação serve para leitura. Ela não estabelece preferência biológica
  entre os candidatos.

## 14. Limitações técnicas, biológicas e éticas

Limitações técnicas:

- Não executa alinhamento genômico completo.
- Não faz BLAST completo.
- Não analisa off-target com mismatches.
- Não usa anotação genômica.
- Não usa contexto cromossômico.
- Não usa dados de expressão gênica.
- Não estima eficiência real.

Limitações biológicas:

- A presença de PAM e protospacer não garante atividade biológica.
- GC% é apenas uma característica simples.
- Homopolímeros e duplicatas são heurísticas básicas.
- A análise não substitui ferramentas especializadas.
- A análise não substitui revisão de especialistas.

Limitações éticas:

- Não usar o software para decisão clínica.
- Não usar o software para planejamento terapêutico.
- Não usar o software como protocolo experimental.
- Não afirmar que candidatos são seguros ou eficientes.
- Declarar sempre que os resultados são triagem computacional inicial.

Texto obrigatório de limitação:

"Os resultados apresentados representam uma triagem computacional inicial baseada em padrões de sequência. Os candidatos identificados não constituem recomendação experimental, clínica ou terapêutica. A seleção real de guias CRISPR-Cas9 exige análises adicionais, incluindo avaliação de off-target em genoma de referência, contexto biológico, validação experimental e revisão especializada."
