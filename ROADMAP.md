# ROADMAP - AlvoCas9

## Princípios de implementação

- Implementar primeiro o núcleo mínimo testável.
- Evitar complexidade desnecessária.
- Escrever testes junto com cada módulo.
- Garantir que cada etapa seja compreensível e verificável.
- Não tratar resultados como recomendação experimental, clínica ou terapêutica.
- Manter documentação atualizada durante o desenvolvimento.

## Fase 0 - Planejamento

Objetivo:

Definir escopo, requisitos, arquitetura, regras de validação, regras de análise e plano de qualidade antes da implementação.

Entregáveis:

- `SPEC.md`
- `ROADMAP.md`
- `QUALITY_PLAN.md`

Critérios de aceite:

- Escopo e fora de escopo estão explícitos.
- Requisitos funcionais e não funcionais estão definidos.
- Regras de coordenadas estão documentadas.
- Limitações técnicas, biológicas e éticas estão registradas.
- Não há promessa de uso clínico, terapêutico ou experimental.

## Fase 1 - Estrutura do projeto

Objetivo:

Criar a base do repositório e preparar o pacote Python.

Entregáveis:

- `pyproject.toml`
- `README.md` inicial.
- Estrutura `src/alvocas9`.
- Estrutura `tests`.
- Estrutura `data/examples`.
- Arquivos base `__init__.py` e `__main__.py`.

Ordem recomendada:

1. Criar estrutura de pastas.
2. Criar configuração de pacote.
3. Criar arquivos FASTA de exemplo.
4. Criar comando mínimo de CLI ainda sem pipeline completo.

Critérios de aceite:

- O pacote pode ser importado.
- A CLI responde a `python -m alvocas9 --help`.
- Os exemplos FASTA estão disponíveis.
- Nenhuma lógica biológica complexa foi implementada ainda.

## Fase 2 - Leitura e validação FASTA

Objetivo:

Implementar leitura de FASTA e validação computacional da entrada.

Entregáveis:

- Leitor FASTA.
- Validador de DNA.
- Testes de leitura.
- Testes de validação.

Ordem recomendada:

1. Implementar leitura simples de registros FASTA.
2. Normalizar sequências para maiúsculas.
3. Implementar validações de arquivo.
4. Implementar validações de registro.
5. Diferenciar erros e avisos.
6. Criar comando `validate`.

Critérios de aceite:

- FASTA válido é aceito.
- Arquivo inexistente é rejeitado.
- Arquivo vazio é rejeitado.
- Cabeçalho sem identificador é rejeitado.
- Identificador duplicado é rejeitado.
- Sequência vazia é rejeitada.
- Caracteres inválidos são rejeitados.
- N é rejeitado por padrão.
- N é aceito com modo flexível e gera aviso.

## Fase 3 - Utilitários de sequência e PAM

Objetivo:

Implementar funções básicas de sequência e interpretação de PAM.

Entregáveis:

- Função de reverso complementar.
- Função de GC%.
- Função de maior homopolímero.
- Validador de padrão PAM.
- Função de correspondência PAM.
- Testes unitários.

Ordem recomendada:

1. Implementar complemento A-T e C-G.
2. Preservar N no reverso complementar.
3. Calcular GC%.
4. Calcular homopolímeros.
5. Implementar suporte IUPAC para PAM.
6. Testar `NGG` e casos com sobreposição.

Critérios de aceite:

- `ACGTN` gera reverso complementar correto.
- GC% é calculado com denominador claro.
- Homopolímero máximo é calculado corretamente.
- `NGG` reconhece AGG, CGG, GGG e TGG.
- Padrão PAM inválido gera erro.

## Fase 4 - Scanner de candidatos

Objetivo:

Localizar PAMs nas duas fitas e extrair protospacers com coordenadas corretas.

Entregáveis:

- Scanner da fita direta.
- Scanner da fita reversa complementar.
- Estatísticas de PAMs encontrados.
- Estatísticas de PAMs ignorados.
- Testes específicos de coordenadas.

Ordem recomendada:

1. Implementar busca na fita direta.
2. Extrair protospacer antes do PAM.
3. Converter coordenadas para 1-based inclusivo.
4. Ignorar PAM sem upstream suficiente.
5. Implementar busca no reverso complementar.
6. Mapear coordenadas da fita reversa para a sequência original.
7. Escrever testes pequenos com coordenadas calculáveis manualmente.

Critérios de aceite:

- Candidato da fita `+` tem coordenadas corretas.
- Candidato da fita `-` tem coordenadas corretas na sequência original.
- Protospacer da fita `-` é exibido em orientação 5'->3' da fita analisada.
- PAMs sem bases suficientes antes são ignorados e contabilizados.
- Teste de regressão cobre o mapeamento da fita reversa.

## Fase 5 - Features e filtros heurísticos

Objetivo:

Calcular características dos candidatos e aplicar filtros simples.

Entregáveis:

- Resumo das sequências.
- Features por candidato.
- Filtros heurísticos.
- Score heurístico.
- Testes de features e filtros.

Ordem recomendada:

1. Calcular GC% do candidato.
2. Calcular N e `has_n`.
3. Calcular homopolímero máximo.
4. Calcular duplicata exata.
5. Implementar status dos filtros.
6. Implementar score.
7. Testar penalidades individualmente.

Critérios de aceite:

- GC fora da faixa aplica penalidade.
- N aplica penalidade.
- Homopolímero acima do limite gera alerta e penalidade.
- Duplicata exata gera alerta e penalidade.
- Score fica entre 0 e 100.
- Status não usa termos proibidos.

## Fase 6 - Saídas e relatórios

Objetivo:

Gerar todos os artefatos de saída do MVP.

Entregáveis:

- `sequences_summary.csv`
- `candidates.csv`
- `validation_summary.csv`
- `validation.json`
- `candidates.json`
- `run_config.json`
- Gráficos PNG.
- Relatório HTML.
- Relatório Markdown.
- Log.

Ordem recomendada:

1. Criar diretórios de saída.
2. Escrever CSV.
3. Escrever JSON.
4. Gerar gráficos.
5. Gerar relatório Markdown.
6. Gerar relatório HTML.
7. Gerar log.
8. Testar existência e conteúdo mínimo dos arquivos.

Critérios de aceite:

- Todos os arquivos esperados são gerados.
- `candidates.csv` possui todas as colunas obrigatórias.
- `run_config.json` registra parâmetros usados.
- Relatório contém configurações, validação, candidatos, gráficos e limitações.
- Log contém início, parâmetros principais e conclusão.

## Fase 7 - CLI completa

Objetivo:

Consolidar comandos de uso do pipeline.

Entregáveis:

- `python -m alvocas9 validate`
- `python -m alvocas9 analyze`
- Ajuda de CLI.
- Testes de CLI.

Ordem recomendada:

1. Definir argumentos obrigatórios.
2. Definir argumentos opcionais.
3. Conectar comando `validate` ao validador.
4. Conectar comando `analyze` ao pipeline completo.
5. Definir códigos de saída.

Critérios de aceite:

- `validate` retorna sucesso para FASTA válido.
- `validate` retorna erro para FASTA inválido.
- `analyze` gera resultados para exemplo válido.
- Parâmetros configuráveis alteram a execução.

## Fase 8 - Documentação técnica

Objetivo:

Criar documentação suficiente para instalar, executar, entender e manter o pipeline.

Entregáveis:

- Glossário.
- Explicação técnica do pipeline.
- Arquitetura.
- Manual do usuário.
- Limitações éticas e técnicas.
- Referências base.

Ordem recomendada:

1. Escrever explicação técnica módulo a módulo.
2. Escrever manual de uso.
3. Escrever arquitetura do pipeline.
4. Escrever limitações.
5. Escrever glossário.
6. Listar referências base.

Critérios de aceite:

- Documentação está em português brasileiro.
- Documentação explica DNA, FASTA, CRISPR, Cas9, PAM, protospacer e off-target.
- Documentação explica o que o pipeline faz e não faz.
- Documentação evita tom publicitário.
- Limitações são explícitas.

## Fase 9 - Verificação final

Objetivo:

Confirmar que o projeto está executável, testado e documentado.

Entregáveis:

- Execução de testes.
- Execução de exemplo.
- Checklist final.

Ordem recomendada:

1. Rodar `python -m pytest`.
2. Rodar exemplo simples.
3. Conferir arquivos gerados.
4. Abrir relatório HTML.
5. Conferir cabeçalho de `candidates.csv`.
6. Conferir log.
7. Revisar README.
8. Revisar documentação.
9. Atualizar checklist.

Critérios de aceite:

- Testes passam.
- Exemplo roda sem erro.
- Todos os arquivos esperados existem.
- Relatório contém gráficos e texto obrigatório de limitação.
- Candidatos usam coordenadas 1-based inclusivas.
- Nenhum texto apresenta o sistema como ferramenta clínica.
