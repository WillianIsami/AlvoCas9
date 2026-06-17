# Glossário do AlvoCas9

**Adenina (A):** base nitrogenada do DNA. No FASTA, é representada pela letra `A`.

**Alvo:** região de interesse em uma sequência. No AlvoCas9, o termo deve ser entendido como potencial sítio-alvo computacional.

**Bioinformática:** área que aplica computação à análise de dados biológicos.

**Biotecnologia in silico:** análise biotecnológica feita por métodos computacionais, sem experimento direto.

**Candidato in silico:** sequência identificada por regra computacional. Não representa validação experimental.

**Cas9:** proteína associada ao sistema CRISPR. No projeto, é usada apenas como referência conceitual para a busca por PAM.

**Citosina (C):** base nitrogenada do DNA, representada por `C`.

**Conteúdo GC:** porcentagem de bases `G` e `C` em uma sequência.

**Coordenada 1-based inclusiva:** forma de coordenada em que a primeira base é posição 1 e o fim do intervalo está incluído.

**CRISPR:** sistema biológico relacionado ao reconhecimento de sequências. No projeto, é contexto para triagem computacional.

**DNA:** ácido desoxirribonucleico, molécula que armazena informação genética.

**FASTA:** formato textual para representar sequências biológicas. Cada registro começa com `>`.

**Fita direta (`+`):** sequência exatamente como aparece no arquivo FASTA.

**Fita reversa complementar (`-`):** sequência obtida invertendo a original e trocando A por T, T por A, C por G e G por C.

**Filtro heurístico:** regra simples usada para classificar candidatos. Não é prova biológica.

**Gene:** região do DNA associada a uma função biológica.

**Genoma:** conjunto completo de material genético de um organismo.

**Guanina (G):** base nitrogenada do DNA, representada por `G`.

**Homopolímero:** repetição consecutiva da mesma base, como `AAAAA`.

**IUPAC:** conjunto de códigos usados para representar bases ou ambiguidades em sequências.

**N:** base desconhecida no FASTA. No padrão PAM, `N` significa coringa para A, C, G ou T.

**NGG:** padrão PAM em que a primeira posição pode ser A, C, G ou T, seguida por duas guaninas.

**Nucleotídeo:** unidade básica de DNA e RNA.

**Off-target:** região não pretendida que pode ser semelhante ao alvo.

**PAM:** *Protospacer Adjacent Motif*, sequência curta necessária para reconhecimento em determinados sistemas Cas.

**Pipeline:** sequência organizada de etapas computacionais.

**Potencial sítio-alvo:** região identificada computacionalmente como candidata inicial.

**Protospacer:** trecho de tamanho configurável extraído antes do PAM na orientação da fita analisada.

**RNA:** ácido ribonucleico. No projeto, aparece apenas em nível conceitual.

**RNA guia ou sgRNA:** molécula que, em sistemas CRISPR, orienta Cas9. O AlvoCas9 não projeta sgRNA validado.

**Score heurístico:** pontuação simples baseada em penalidades por GC, N, homopolímero e duplicação.

**Sequência biológica:** representação linear de DNA, RNA ou proteína.

**SpCas9:** Cas9 derivada de *Streptococcus pyogenes*, associada ao PAM `NGG`.

**Timina (T):** base nitrogenada do DNA, representada por `T`.

**Triagem exploratória:** análise inicial para organizar candidatos, sem conclusão experimental.

**Validação FASTA:** checagem computacional de formato, identificadores, caracteres e tamanho.
