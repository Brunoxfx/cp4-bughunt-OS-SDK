# Revisão integral do Checkpoint 4

**Data:** 07/09/2026. **Código auditado:** `07005dba7651d1d007a39e6cccfa0dc41f0f3e91`.

Fonte: as seis páginas de `CHECKPOINT 4.pdf`, que está na pasta superior ao repositório. SHA-256 do PDF: `BC0D91C37C39CEBEB9BB48BB7B24EABF1446CF8D814B7858B6515DD0D37159CE`.

**Resultado:** a implementação local passou na revisão do contrato e nos testes renovados com H2. A entrega acadêmica ainda tem pendências de identificação, revisão pessoal das reflexões, Oracle, Eclipse, GitHub e Teams. Esta revisão não representa uma nota atribuída pelo professor.

## O que foi realmente feito

- Preservado o projeto original no primeiro commit `7aae6cb`.
- Aplicados 12 commits de bugs e 6 commits de Clean Code, separados e numerados.
- Mantidos os endpoints, a hierarquia de conteúdos, a persistência via repositories e as regras de negócio no model.
- Adicionada uma única classe de produção, `ReciboAluguel`, para separar a apresentação do recibo.
- Preenchidas as tabelas do README, com sintoma, causa, correção, conceito e os commits correspondentes.
- Escritas seis respostas de reflexão, cada uma com sete linhas explícitas e referências ao código real.
- Preparados testes diretos em Java e testes HTTP, sem adicionar dependências à aplicação.
- Compilado, empacotado e executado o JAR com H2.

O `pom.xml`, o template original e o `application.properties` têm um único conteúdo ao longo dos 20 commits auditados. Portanto, não foram acrescentadas bibliotecas/frameworks ao projeto nem substituídos os placeholders de credenciais no histórico. Os 18 commits de correção/refatoração contêm somente arquivos de produção Java; documentação e evidências ficaram em commit separado.

## Conferência de todas as seções do PDF

| Seção do PDF | Exigência e resultado |
|---|---|
| 1. O Problema Real | Corrigir o MVP existente para cumprir o contrato: atendido nos cenários locais verificados. |
| 2. O que você recebeu | Estrutura original preservada: `Conteudo`, subclasses, `Promocionavel`, `Usuario`, repositories, controllers e exceções. Oracle continua configurado no arquivo original; a execução autenticada nele está pendente. |
| 3. Contrato da API | Preços, promoções, duração, consultas, cadastro de usuário e as quatro regras de aluguel passaram nos testes renovados. A matriz detalhada aparece abaixo. |
| 4. A caça / Regras do jogo | Há 12 correções e 6 ajustes, sem reescrita do projeto ou novas dependências. Revisão do código não encontrou condições por título/ID para favorecer exemplos. Os commits são individuais e o README documenta os achados. |
| 5. Como rodar e testar | Java 17 confirmado, build limpo aprovado, JAR iniciado e endpoints conferidos. O exemplo do PDF também foi executado com curl. A importação/play no Eclipse e a configuração local do Oracle ainda não foram realizadas. |
| 6. O ciclo da caça | Preservadas evidências originais, retestes por correção e execução final. Bugs bloqueados pelo cadastro foram examinados diretamente no model e retestados pela API depois. Não foi inventada uma reprodução HTTP original quando ela estava bloqueada. |
| 7. Entrega / Penalidades | Histórico individual e configuração sem credenciais reais atendidos. README tem conteúdo técnico, mas identificação incompleta. Repositório público e envio do link ainda pendentes; não se pode marcar a entrega como pronta. |
| 8. Troubleshooting | Compilação com JDK correto, dependências resolvidas e porta local isolada nos testes. Driver Oracle está nas dependências. A porta 1521 do servidor respondeu; não foram testados login/schema. Nenhuma tabela Oracle foi removida ou alterada. |
| 9. Checklist final | Código, configuração versionada, histórico e contrato em H2 conferidos. Mantidos desmarcados: integrantes, Oracle, Eclipse, publicação e envio. |
| 10. O que está sendo avaliado | As evidências cobrem bugs, Clean Code, documentação e contrato local. Identificação/reflexões do grupo e entrega externa precisam ser concluídas; a pontuação permanece a critério do professor. |

## Resultados renovados do contrato

| Verificação | Resultado confirmado em H2 |
|---|---|
| Filme comum | Preço normal 9,90; promocional 7,92. |
| Filme de estreia | Preço normal 14,90; promocional 11,92. |
| Série com cinco temporadas | Preço normal 24,50; promocional 19,60. |
| Série com duas temporadas | Preço normal 9,80; promocional 7,84. |
| Documentário | Preço zero; não implementa `Promocionavel`; aluguel disponível permitido com saldo zero. |
| Duração zero/negativa | HTTP 400 com mensagem, nos três tipos de conteúdo, sem aumentar o catálogo. Construtor/setter também verificados. |
| Corpo inválido | Duração nula ou textual recusada, sem persistência. |
| Conteúdo inexistente | HTTP 404 com mensagem, inclusive na consulta promocional. |
| Categoria | Apenas a categoria pedida; categoria sem registros retorna lista vazia. |
| Série cadastrada | Campos herdados e disponibilidade preservados na resposta e no GET. |
| Usuário cadastrado | IDs gerados e distintos; nome preservado no POST e GET. IDs externos não são adotados no cadastro. |
| Créditos negativos | Cadastro/setter recusam saldo negativo; débito inválido ou acima do saldo é impedido. |
| Conteúdo indisponível | HTTP 409, sem alteração persistida, inclusive documentário. |
| Classificação indicativa | Menor de 12 anos para classificação 14: HTTP 422 e mensagem explicativa, sem débito. Idade igual à classificação é aceita. |
| Créditos insuficientes | Saldo zero ou 9,89 para filme de 9,90: HTTP 422, sem alterar saldo/disponibilidade. |
| Aluguel válido | HTTP 200, débito pelo preço normal e saldo persistido correto. Saldo exatamente suficiente pode chegar a zero. |
| Repetir aluguel | Segunda tentativa sobre conteúdo já alugado retorna 409, sem novo débito. |

## Comandos e evidências desta revisão

Foi executado com Java 17:

```powershell
mvn -B clean verify dependency:build-classpath -Dmdep.outputFile=target/classpath.txt
python verificacao/verificar.py all --label revisao-2026-09-07 --jar
```

- **Build limpo:** `BUILD SUCCESS`, sem reutilizar o JAR anterior. [Log Maven](evidencias/revisao-2026-09-07-maven.log).
- **Model:** 40 verificações aprovadas, em oito grupos diretos Java.
- **HTTP:** 13 grupos aprovados; 112 requisições e 133 registros totais, sem falha na suíte. [Resultados completos](evidencias/revisao-2026-09-07.json).
- **curl:** nove requisições complementares em outro H2 temporário, incluindo o JSON de Matrix do PDF, desconto, aluguel, GET de persistência, duração inválida e `/api/conteudos/999`. Todas passaram. [Resultados curl](evidencias/revisao-2026-09-07-curl.json).
- **Histórico e README:** 12 bugs, 6 ajustes, seis reflexões com sete linhas, células técnicas preenchidas e hashes de commits válidos. [Conferência estrutural](evidencias/revisao-2026-09-07-historico.json).
- **Oracle:** conexão TCP com `oracle.fiap.com.br:1521` estabelecida; credenciais ausentes no ambiente do processo. Isso confirma acesso à porta, não autenticação ou funcionamento da aplicação com Oracle. [Resultado da conexão](evidencias/revisao-2026-09-07-oracle.json).

O Maven informa `No tests to run` porque os testes próprios são executados pelo script, não pelo Surefire/JUnit. O build ainda emite um aviso de API depreciada no handler; isso não impediu compilação ou execução. Não foi encontrada uma nova falha do contrato que exigisse alterar o código de produção nesta revisão.

## O que não foi feito e o que falta

| Pendência | Situação real / próximo passo |
|---|---|
| Nome do grupo, nomes, RMs e turmas | Continuam como `A preencher`, conforme escolha anterior. Informar os dados para completar a identificação. |
| Reflexões com palavras do grupo | Os textos existem e foram revisados tecnicamente; os integrantes ainda precisam revisar e expressar sua própria compreensão. |
| Oracle FIAP | Rede respondeu, mas não houve autenticação nem teste de tabelas, IDs ou persistência. Configurar credenciais somente localmente e repetir o roteiro no schema do grupo. |
| Eclipse | Não foi feita uma sessão de importação Maven e play. Maven/Java e JAR foram validados; isso não comprova execução pelo Eclipse. |
| GitHub público | Nenhum remote está configurado neste repositório; nenhuma publicação foi feita nesta sessão. Faltam nome do grupo e acesso ao GitHub para criar `cp4-bughunt-<nome-do-grupo>` e publicar o histórico. |
| Teams | Nenhum link foi enviado; a entrega depende da publicação e do envio pelo grupo. |

Os testes desta revisão não usaram o Oracle e encerraram seus processos Java temporários. As evidências da implementação anterior foram preservadas; esta rodada foi salva com nomes distintos.
