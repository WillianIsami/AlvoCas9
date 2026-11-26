# Relatório técnico de triagem in silico CRISPR-Cas9

**Projeto:** AlvoCas9

**Data e hora da execução:** 2026-11-26 17:01:15 -03

**Arquivo analisado:** `data\real\ADE2_scerevisiae.fasta`

## Configurações

| configuracao | valor |
| --- | --- |
| PAM | NGG |
| posição do PAM | 3linha (a 3' do protospacer) |
| target length | 20 |
| min GC | 40.0 |
| max GC | 60.0 |
| max homopolymer | 4 |
| allow N | False |

## Resumo das sequências

| ID | tamanho | GC% | número de N | status de validação |
| --- | --- | --- | --- | --- |
| ADE2_YOR128C | 1716 | 40.21 | 0 | válida |

## Resumo da validação

- Erros: 0
- Avisos: 0

| level | sequence_id | message |
| --- | --- | --- |
| info |  | Validação concluída sem erros. |

## Contexto técnico

CRISPR-Cas9 é um sistema molecular estudado em biotecnologia e bioinformática. Neste relatório, ele é tratado apenas como contexto computacional para busca de padrões em sequências de DNA.

PAM é uma pequena sequência adjacente ao possível alvo que, em sistemas Cas9, participa do reconhecimento da região. Para SpCas9, o padrão explorado neste MVP é NGG.

NGG significa que a primeira posição pode ser A, C, G ou T, seguida por duas bases G.

Um candidato in silico é uma sequência identificada por regra computacional. Ele representa um potencial sítio-alvo para triagem exploratória, sem validação experimental.

A análise é exploratória porque usa padrões de sequência e filtros básicos. Ela não substitui análise de off-target, contexto biológico, validação experimental ou revisão especializada.

## Resumo dos candidatos

- Total de candidatos: 140

### Candidatos por sequência

| sequence_id | quantidade |
| --- | --- |
| ADE2_YOR128C | 140 |

### Candidatos por fita

| strand | quantidade |
| --- | --- |
| + | 78 |
| - | 62 |

### Status dos filtros

| filter_status | quantidade |
| --- | --- |
| aprovado nos filtros básicos | 80 |
| requer cautela | 60 |

### Estatísticas de PAM

| sequence_id | pams_found_plus | pams_found_minus | pams_found_total | pams_skipped_insufficient_upstream_plus | pams_skipped_insufficient_upstream_minus | pams_skipped_insufficient_upstream_total |
| --- | --- | --- | --- | --- | --- | --- |
| ADE2_YOR128C | 80 | 62 | 142 | 2 | 0 | 2 |

### Métricas gerais

| métrica | valor |
| --- | --- |
| total de candidatos | 140 |
| sequências com candidatos | 1 |
| candidatos na fita + | 78 |
| candidatos na fita - | 62 |

## Tabela de candidatos

A tabela mostra os 50 candidatos de maior score heuristico, de um total de 140. A listagem completa está em tables/candidates.csv e em json/candidates.json.

| sequence_id | strand | protospacer_sequence_5to3 | pam_sequence_5to3 | protospacer_start_1based | protospacer_end_1based | pam_start_1based | pam_end_1based | cut_site_1based | full_candidate_start_1based | full_candidate_end_1based | relative_position_percent | target_length | pam_pattern | gc_percent | n_count | has_n | max_homopolymer_run | duplicate_exact_count_within_input | warnings | heuristic_score | filter_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADE2_YOR128C | + | ACAGTTGGTATATTAGGAGG | GGG | 13 | 32 | 33 | 35 | 29 | 13 | 35 | 1.4 | 20 | NGG | 40.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | ATTGGGACGTATGATTGTTG | AGG | 39 | 58 | 59 | 61 | 55 | 39 | 61 | 2.9 | 20 | NGG | 40.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | TGATTGTTGAGGCAGCAAAC | AGG | 50 | 69 | 70 | 72 | 66 | 50 | 72 | 3.6 | 20 | NGG | 45.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | AACTCCAATGACCACGTTAA | TGG | 130 | 149 | 150 | 152 | 146 | 130 | 152 | 8.2 | 20 | NGG | 40.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | AGTTACCCAAAGTGTTCCTG | TGG | 357 | 376 | 377 | 379 | 373 | 357 | 379 | 21.4 | 20 | NGG | 45.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | GAGACGTCCCTATTGAATGT | TGG | 391 | 410 | 411 | 413 | 407 | 391 | 413 | 23.4 | 20 | NGG | 45.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | TTCCATTCGTCTTGAAGTCG | AGG | 428 | 447 | 448 | 450 | 444 | 428 | 450 | 25.6 | 20 | NGG | 45.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | CGTCTTGAAGTCGAGGACTT | TGG | 435 | 454 | 455 | 457 | 451 | 435 | 457 | 26.0 | 20 | NGG | 50.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | TCGAGGACTTTGGCATACGA | TGG | 445 | 464 | 465 | 467 | 461 | 445 | 467 | 26.6 | 20 | NGG | 50.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | ACTTTGGCATACGATGGAAG | AGG | 451 | 470 | 471 | 473 | 467 | 451 | 473 | 26.9 | 20 | NGG | 45.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | GGAAATGATTCCGGAAGCTT | TGG | 495 | 514 | 515 | 517 | 511 | 495 | 517 | 29.5 | 20 | NGG | 45.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | GGAAGCTTTGGAAGTACTGA | AGG | 507 | 526 | 527 | 529 | 523 | 507 | 529 | 30.2 | 20 | NGG | 45.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | TTATGCGCCTGCTAGAGTTC | CGG | 666 | 685 | 686 | 688 | 682 | 666 | 688 | 39.5 | 20 | NGG | 50.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | TCCGGACTCCGTTCAACTTA | AGG | 684 | 703 | 704 | 706 | 700 | 684 | 706 | 40.5 | 20 | NGG | 50.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | TCAACTTAAGGCGAAGTTGT | TGG | 696 | 715 | 716 | 718 | 712 | 696 | 718 | 41.2 | 20 | NGG | 40.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | ATCAAATCTTTTCCCGGTTG | TGG | 730 | 749 | 750 | 752 | 746 | 730 | 752 | 43.2 | 20 | NGG | 40.0 | 0 | False | 4 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | TTTCCCGGTTGTGGTATATT | TGG | 739 | 758 | 759 | 761 | 755 | 739 | 761 | 43.7 | 20 | NGG | 40.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | CGGTTGTGGTATATTTGGTG | TGG | 744 | 763 | 764 | 766 | 760 | 744 | 766 | 44.0 | 20 | NGG | 45.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | AGAAACTTGCGAAAGAGCAT | TGG | 996 | 1015 | 1016 | 1018 | 1012 | 996 | 1018 | 58.7 | 20 | NGG | 40.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | GAAAGAGCATTGGCGACTCC | AGG | 1006 | 1025 | 1026 | 1028 | 1022 | 1006 | 1028 | 59.3 | 20 | NGG | 55.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | GGTTCCTCAGTGTACTTATA | TGG | 1027 | 1046 | 1047 | 1049 | 1043 | 1027 | 1049 | 60.5 | 20 | NGG | 40.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | TATTATTGCCTCCAGTATGG | CGG | 1089 | 1108 | 1109 | 1111 | 1105 | 1089 | 1111 | 64.1 | 20 | NGG | 40.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | GTATGGCGGAATGTGAACAA | AGG | 1103 | 1122 | 1123 | 1125 | 1119 | 1103 | 1125 | 64.9 | 20 | NGG | 45.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | CAAAGGCTGAACTACATTAC | AGG | 1120 | 1139 | 1140 | 1142 | 1136 | 1120 | 1142 | 65.9 | 20 | NGG | 40.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | AATCTCTGTCGCTCAAAAGT | TGG | 1164 | 1183 | 1184 | 1186 | 1180 | 1164 | 1186 | 68.5 | 20 | NGG | 40.0 | 0 | False | 4 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | TGTCGCTCAAAAGTTGGACT | TGG | 1170 | 1189 | 1190 | 1192 | 1186 | 1170 | 1192 | 68.8 | 20 | NGG | 45.0 | 0 | False | 4 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | AAAGTTGGACTTGGAAGCAA | TGG | 1179 | 1198 | 1199 | 1201 | 1195 | 1179 | 1201 | 69.3 | 20 | NGG | 40.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | GGAAGCAATGGTCAAACCAT | TGG | 1191 | 1210 | 1211 | 1213 | 1207 | 1191 | 1213 | 70.0 | 20 | NGG | 45.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | GCAATGGTCAAACCATTGGT | TGG | 1195 | 1214 | 1215 | 1217 | 1211 | 1195 | 1217 | 70.3 | 20 | NGG | 45.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | ACCATTGGTTGGAATCATCA | TGG | 1206 | 1225 | 1226 | 1228 | 1222 | 1206 | 1228 | 70.9 | 20 | NGG | 40.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | CCATTGGTTGGAATCATCAT | GGG | 1207 | 1226 | 1227 | 1229 | 1223 | 1207 | 1229 | 71.0 | 20 | NGG | 40.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | GGGATCAGACTCTGACTTGC | CGG | 1227 | 1246 | 1247 | 1249 | 1243 | 1227 | 1249 | 72.1 | 20 | NGG | 55.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | GGTAATGTCTGCCGCATGTG | CGG | 1248 | 1267 | 1268 | 1270 | 1264 | 1248 | 1270 | 73.4 | 20 | NGG | 55.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | CTGCTCATAGAACTCCACAT | AGG | 1313 | 1332 | 1333 | 1335 | 1329 | 1313 | 1335 | 77.2 | 20 | NGG | 45.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | GCTATTTCCGCAAGCAAGCG | TGG | 1348 | 1367 | 1368 | 1370 | 1364 | 1348 | 1370 | 79.2 | 20 | NGG | 55.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | AAAACAATTATCGCTGGAGC | TGG | 1375 | 1394 | 1395 | 1397 | 1391 | 1375 | 1397 | 80.8 | 20 | NGG | 40.0 | 0 | False | 4 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | ACAATTATCGCTGGAGCTGG | TGG | 1378 | 1397 | 1398 | 1400 | 1394 | 1378 | 1400 | 80.9 | 20 | NGG | 50.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | CAATTATCGCTGGAGCTGGT | GGG | 1379 | 1398 | 1399 | 1401 | 1395 | 1379 | 1401 | 81.0 | 20 | NGG | 50.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | AATTATCGCTGGAGCTGGTG | GGG | 1380 | 1399 | 1400 | 1402 | 1396 | 1380 | 1402 | 81.1 | 20 | NGG | 50.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | GGCTGCTCACTTGCCAGGTA | TGG | 1401 | 1420 | 1421 | 1423 | 1417 | 1401 | 1423 | 82.3 | 20 | NGG | 60.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | TGCTCACTTGCCAGGTATGG | TGG | 1404 | 1423 | 1424 | 1426 | 1420 | 1404 | 1426 | 82.5 | 20 | NGG | 55.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | ATGACACCACTTCCTGTCAT | CGG | 1432 | 1451 | 1452 | 1454 | 1448 | 1432 | 1454 | 84.1 | 20 | NGG | 45.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | GTCATCGGTGTGCCCGTAAA | AGG | 1447 | 1466 | 1467 | 1469 | 1463 | 1447 | 1469 | 85.0 | 20 | NGG | 55.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | TCAATTGTGCAAATGCCTAG | AGG | 1501 | 1520 | 1521 | 1523 | 1517 | 1501 | 1523 | 88.1 | 20 | NGG | 40.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | TAGTACGAACGCTGCGCTGT | TGG | 1554 | 1573 | 1574 | 1576 | 1570 | 1554 | 1576 | 91.2 | 20 | NGG | 55.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | + | CTGTTGGCTGTCAGACTGCT | TGG | 1570 | 1589 | 1590 | 1592 | 1586 | 1570 | 1592 | 92.1 | 20 | NGG | 55.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | - | GAGTTGCTTATTTGTTTGGC | AGG | 115 | 134 | 112 | 114 | 117 | 112 | 134 | 7.2 | 20 | NGG | 40.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | - | GGAGCCATTAACGTGGTCAT | TGG | 137 | 156 | 134 | 136 | 139 | 134 | 156 | 8.4 | 20 | NGG | 50.0 | 0 | False | 2 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | - | TGGAAAAGGAGCCATTAACG | TGG | 144 | 163 | 141 | 143 | 146 | 141 | 163 | 8.9 | 20 | NGG | 45.0 | 0 | False | 4 | 1 |  | 100 | aprovado nos filtros básicos |
| ADE2_YOR128C | - | TTGTTCCACAGGAACACTTT | GGG | 365 | 384 | 362 | 364 | 367 | 362 | 384 | 21.7 | 20 | NGG | 40.0 | 0 | False | 3 | 1 |  | 100 | aprovado nos filtros básicos |

A coluna `cut_site_1based` indica a posição da base imediatamente anterior ao
corte previsto, na sequência original. O corte ocorre entre essa posição e a
seguinte. É uma premissa do modelo para SpCas9, que corta cerca de 3 pares de
base antes do PAM, e não uma medição.

A coluna `relative_position_percent` indica onde o ponto médio do candidato
está na sequência, em porcentagem. É uma indicação de posição, não um critério
de qualidade, e não entra no score.

## Gráficos

![Candidatos por sequência](../figures/candidates_per_sequence.png)

![Distribuição de GC nos candidatos](../figures/gc_distribution_candidates.png)

![Resumo dos status dos filtros](../figures/filter_status_summary.png)

![Distribuição dos candidatos ao longo da sequência](../figures/candidate_density.png)

## Interpretação conservadora

Os resultados devem ser interpretados como triagem exploratória. Os filtros básicos organizam candidatos in silico por critérios computacionais simples, como faixa de GC, presença de N, homopolímeros e duplicação exata no conjunto de entrada. O score heurístico serve apenas para priorização didática e rastreável dentro do relatório.

## Limitações técnicas, biológicas e éticas

Os resultados apresentados representam uma triagem computacional inicial baseada em padrões de sequência. Os candidatos identificados não constituem recomendação experimental, clínica ou terapêutica. A seleção real de guias CRISPR-Cas9 exige análises adicionais, incluindo avaliação de off-target em genoma de referência, contexto biológico, validação experimental e revisão especializada.

Limitações adicionais:

- O pipeline não executa análise completa de off-target em genoma de referência.
- O pipeline não considera contexto cromossômico, expressão gênica, cromatina ou anotação funcional.
- A presença de PAM não confirma atividade biológica.
- Os filtros básicos não substituem ferramentas especializadas nem revisão por especialistas.
- O relatório não deve ser usado como protocolo experimental.

## Arquivos gerados

- `tables/sequences_summary.csv`
- `tables/candidates.csv`
- `tables/validation_summary.csv`
- `tables/candidates.bed`
- `json/validation.json`
- `json/candidates.json`
- `json/run_config.json`
- `figures/candidates_per_sequence.png`
- `figures/gc_distribution_candidates.png`
- `figures/filter_status_summary.png`
- `figures/candidate_density.png`
- `reports/technical_report.html`
- `reports/technical_report.md`
- `logs/pipeline.log`
