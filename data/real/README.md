# Sequência pública curada

Este diretório contém a sequência biológica real usada para avaliar o pipeline
além dos arquivos sintéticos de exemplo. A procedência está registrada em
detalhe para que a execução possa ser repetida e conferida por terceiros.

## ADE2_scerevisiae.fasta

### O que é

Sequência genômica do gene **ADE2** (*fosforribosilaminoimidazol
carboxilase*) de *Saccharomyces cerevisiae*, linhagem de referência S288C. O
identificador sistemático do gene é **YOR128C**.

### Por que este gene foi escolhido

- **É o alvo canônico de CRISPR-Cas9 em levedura.** A interrupção do ADE2
  bloqueia a via de biossíntese de adenina e faz a colônia acumular um pigmento
  vermelho, o que torna o resultado da edição visível a olho nu. Por isso o gene
  é amplamente usado como controle em trabalhos de edição genômica em levedura.
- **É organismo modelo.** Evita a discussão ética que uma sequência humana
  traria, sem perder relevância para o tema.
- **Tem tamanho adequado.** Com 1.716 pares de base, produz um número de
  candidatos grande o bastante para análise estatística e pequeno o bastante
  para que o relatório continue legível.
- **É um gene sem íntrons**, então a sequência genômica corresponde
  integralmente à região codificante, o que simplifica a interpretação.

### Procedência

| Campo | Valor |
| --- | --- |
| Fonte | Ensembl REST API |
| URL | `https://rest.ensembl.org/sequence/id/YOR128C?type=genomic;content-type=text/x-fasta` |
| Ensembl release | 116 |
| Assembly | R64-1-1 |
| Localização | cromossomo XV, posições 564476 a 566191 |
| Fita | menos (`-1`); a sequência foi entregue já na orientação codificante |
| Data de acesso | 17 de novembro de 2026 |
| Tamanho | 1.716 pares de base |
| Alfabeto | apenas A, C, G e T, sem bases ambíguas |
| GC | 40,21% |

### Integridade

| Item | SHA-256 |
| --- | --- |
| Arquivo como baixado | `0fa229b2de0430c34889d876ef9d92194473692a07f3a08eb41721f1f818934e` |
| Sequência, sem cabeçalho | `e8a7e4e218061b7b19f7d3551a5b411817e21f0fb3bc1c7e1c35fee27c68ba34` |
| Arquivo versionado aqui | `f0cc9a30b55337c975228bfcbf0a371954cc4b55f3eb12c6b78746ead23318c0` |

A **sequência** versionada é byte a byte idêntica à baixada. A única alteração
foi no cabeçalho FASTA: o original era
`>YOR128C. chromosome:R64-1-1:XV:564476:566191:-1`, e foi reescrito para
incluir o nome do gene, o organismo e a procedência de forma legível. O hash da
sequência sem cabeçalho permite confirmar que nada no conteúdo mudou.

### Verificações feitas antes de versionar

Além da validação pelo próprio pipeline, que não encontrou erros nem avisos:

- o tamanho confere com o intervalo de coordenadas informado: 566191 − 564476 + 1 = 1.716;
- o tamanho é múltiplo de três, correspondendo a 572 códons;
- o primeiro códon é `ATG`, de início;
- o último códon é `TAA`, de parada;
- **não há nenhum códon de parada interno**, o que confirma que a sequência está
  completa, na fase correta e na orientação correta;
- o número de códons corresponde à proteína ADE2 anotada, de 571 aminoácidos
  mais o códon de parada.

A ausência de códons de parada internos é a verificação mais informativa: uma
sequência truncada, deslocada de fase ou invertida quase certamente
apresentaria pelo menos um.

### Como obter novamente

```bash
curl -o ADE2_original.fasta \
  "https://rest.ensembl.org/sequence/id/YOR128C?type=genomic;content-type=text/x-fasta"
```

Conferir que o SHA-256 da sequência, desconsiderando o cabeçalho, é o registrado
acima. O conteúdo pode mudar em releases futuras do Ensembl se a anotação do
gene for revisada; por isso o release e o assembly estão registrados.

### Termos de uso

Os dados de genoma distribuídos pelo Ensembl são de uso livre, inclusive para
fins acadêmicos. O genoma de referência de *S. cerevisiae* S288C é mantido pelo
*Saccharomyces* Genome Database e distribuído publicamente.

### Aviso de escopo

A presença desta sequência real não altera o escopo do projeto. Os candidatos
identificados continuam sendo candidatos in silico, resultado de triagem
computacional exploratória, sem nenhuma recomendação experimental, clínica ou
terapêutica.
