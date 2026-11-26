# Resultados de referência

Saídas completas de uma execução real do pipeline, versionadas no repositório.

Existem por dois motivos. Primeiro, os números e as figuras apresentados sobre
o projeto precisam ter origem rastreável. Segundo, qualquer pessoa pode
comparar a própria execução com esta e confirmar que obteve o mesmo resultado,
o que é o teste prático de reprodutibilidade.

## ade2

Execução sobre o gene ADE2 de *Saccharomyces cerevisiae*, cuja procedência está
em `data/real/README.md`.

Comando que gerou este diretório, a partir da raiz do repositório:

```bash
python -m alvocas9 analyze --input data/real/ADE2_scerevisiae.fasta --output docs/resultados_referencia/ade2
```

Resultado:

| Grandeza | Valor |
| --- | --- |
| Sequências lidas | 1 |
| Erros e avisos de validação | 0 |
| PAMs encontrados | 142, sendo 80 na fita + e 62 na fita − |
| PAMs descartados por falta de bases a montante | 2 |
| Candidatos extraídos | 140 |
| Aprovados nos filtros básicos | 80 |
| Requer cautela | 60 |
| Reprovados nos filtros básicos | 0 |

A análise completa destes resultados está em
`docs/RESULTADO_SEQUENCIA_REAL.md`.

## Como conferir que sua execução bate com esta

O `json/run_config.json` registra a versão do AlvoCas9, a versão do Python, a
data e hora e o hash SHA-256 do arquivo de entrada. Compare o `input_sha256`
com o publicado em `data/real/README.md`: se forem iguais, a mesma sequência
foi usada.

O único campo que muda entre execuções é `executed_at`, junto com o carimbo de
data e hora dentro dos relatórios. Todo o resto é determinístico.

## Aviso

Estes arquivos são **gerados**, não editados à mão. Para atualizá-los, rode o
comando acima novamente. Alterar o conteúdo manualmente quebraria a
correspondência com o código e com a monografia.
