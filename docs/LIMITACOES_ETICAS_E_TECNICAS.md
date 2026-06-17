# Limitações éticas e técnicas do AlvoCas9

Este documento deve ser lido antes de qualquer uso, demonstração ou apresentação pública do projeto.

## Texto obrigatório

Os resultados apresentados representam uma triagem computacional inicial baseada em padrões de sequência. Os candidatos identificados não constituem recomendação experimental, clínica ou terapêutica. A seleção real de guias CRISPR-Cas9 exige análises adicionais, incluindo avaliação de off-target em genoma de referência, contexto biológico, validação experimental e revisão especializada.

## Não é ferramenta clínica

O AlvoCas9 não deve ser usado para diagnóstico, decisão médica, planejamento terapêutico ou qualquer aplicação clínica.

Motivo:

- não há validação clínica;
- não há avaliação de paciente;
- não há regulação;
- não há validação experimental;
- não há análise genômica completa.

Forma correta de apresentar:

"O AlvoCas9 é um pipeline acadêmico de triagem exploratória in silico."

## Não é protocolo experimental

O projeto não define etapas de laboratório, síntese, clonagem, transfecção, cultura celular ou ensaio experimental.

Motivo:

- o escopo é computacional;
- não há validação em bancada;
- não há controle experimental;
- não há recomendação de execução prática.

Forma correta de apresentar:

"O software gera resultados computacionais que precisariam de análises adicionais antes de qualquer estudo experimental."

## Não faz off-target genômico completo

O pipeline não compara candidatos contra um genoma de referência completo.

Ele também não avalia:

- mismatches;
- inserções ou deleções;
- regiões repetitivas do genoma;
- localização cromossômica;
- anotação funcional;
- genes próximos;
- contexto regulatório.

Consequência:

Não se pode afirmar especificidade genômica dos candidatos.

## Não garante eficiência

O score heurístico não prediz eficiência real de edição.

Ele considera apenas:

- GC%;
- presença de N;
- homopolímero;
- duplicação exata dentro da entrada.

Essas regras são úteis para organizar a saída, mas não representam modelo biológico completo.

## Não substitui ferramentas especializadas

Ferramentas como CRISPOR e CHOPCHOP possuem recursos mais amplos, bancos de dados, scoring específico e integrações genômicas.

O AlvoCas9 tem objetivo didático:

- entender o fluxo de um pipeline;
- validar FASTA;
- procurar PAM;
- calcular características simples;
- gerar resultados reprodutíveis.

## Não substitui validação experimental

Mesmo que um candidato passe nos filtros básicos, isso não significa que ele funcione em laboratório.

Validação real exigiria:

- análise de off-target;
- avaliação de contexto biológico;
- revisão especializada;
- testes experimentais;
- critérios regulatórios, quando aplicável.

## Termos recomendados

Use:

- candidato in silico;
- potencial sítio-alvo;
- triagem exploratória;
- filtros básicos;
- requer cautela;
- reprovado nos filtros básicos.

Evite:

- seguro;
- eficiente;
- recomendado;
- validado;
- clínico;
- terapêutico.

## Limitação metodológica central

O AlvoCas9 responde a uma pergunta computacional restrita:

"Dada uma sequência FASTA, quais regiões possuem um PAM compatível com a configuração e bases suficientes para extrair um protospacer?"

Ele não responde:

- se o candidato funcionaria em célula;
- se seria específico em um genoma;
- se teria aplicação médica;
- se seria adequado a um experimento real.

## Como apresentar essa limitação

Fala sugerida:

"A limitação não é uma falha escondida; ela é uma decisão metodológica. O objetivo do AlvoCas9 é construir um pipeline computacional compreensível, testável e reprodutível para triagem inicial."
