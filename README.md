# Checkpoint 4 — Bug Hunt StreamFIAP

API de aluguel de conteúdos corrigida a partir do projeto recebido, mantendo Spring Boot, Spring Data JPA, os endpoints e as dependências originais.

Repositório público: [Brunoxfx/cp4-bughunt-OS-SDK](https://github.com/Brunoxfx/cp4-bughunt-OS-SDK).

## Identificação

**Grupo:** OS-SDK.

| Integrante | RM | Turma |
|---|---|---|
| Bruno Anselmo da Silva | 566521 | 2CCPG |
| Fernando de Almeida Godoi | 564820 | 2CCPG |
| Gabriel Ber Soares | 563520 | 2CCPG |
| Guilherme de Freitas Salgado | 562494 | 2CCPG |
| Vinicius Ribeiro Dias | 566468 | 2CCPG |

| Campo | Resultado |
|---|---|
| **Total de bugs corrigidos** | **12 / 12** |
| **Total de ajustes de Clean Code** | **6 / 6** |

## Parte 1 — Bugs encontrados

As linhas da causa raiz se referem ao **estado original**, commit `7aae6cb`, antes das alterações. Os caminhos abreviados da tabela partem de `src/main/java/br/com/fiap/streamfiap/`. A numeração acompanha o registro da análise e os commits `fix: bugNN`.

| # | Sintoma observado (o que fiz/vi) | Causa raiz (arquivo e linha aproximada) | Correção aplicada | Conceito da disciplina |
|---|---|---|---|---|
| bug01 | `GET /api/conteudos/999999999` respondeu HTTP 200 sem corpo, apesar de o conteúdo não existir. | `controller/ConteudoController.java:32–39`: `catch (Exception)` vazio engolia a exceção e retornava `null`. | Removido o `try/catch`, permitindo que a exceção chegue ao handler existente. Reteste: HTTP 404 e mensagem em `erro`. Commit `1dccb57`. | Propagação e tratamento centralizado de exceções, Aula 11. |
| bug02 | Depois de cadastrar ficção e drama, a busca por `FICCAO` devolveu uma lista vazia. | `controller/ConteudoController.java:45–51`: comparava referências de `String` com `==`. | Adotado `ConteudoRepository.findByCategoria(categoria)`. Reteste: somente a categoria solicitada; categoria inexistente retorna `[]`. Commit `4bb2ddb`. | Igualdade de objetos e consulta derivada com Spring Data JPA, Aula 13. |
| bug03 | No teste direto, o menor de 12 anos recebeu uma exceção checked. A revisão mostrou ausência de handler para ela; a reprodução HTTP inicial ficou bloqueada pelo cadastro de usuário (bug09). | `exception/ClassificacaoIndicativaException.java:3` e `exception/GlobalExceptionHandler.java:11–27`: exceção checked sem mapeamento da regra para HTTP. | A exceção passou a estender `RuntimeException`; foram removidos os `throws` desnecessários e incluído handler 422 com a mensagem original. Após bug09, teste HTTP confirmou classificação e idade na resposta, sem débito. Commit `611bbd8`. | Checked versus unchecked e tradução de exceções de negócio, Aula 11. |
| bug04 | Filme com duração zero foi salvo com HTTP 201. Construtor e setter também aceitaram duração inválida em Java. | `model/Conteudo.java:27,55`: atribuição direta, sem validação. | A duração passou a ser validada no setter, reutilizado pelo construtor. `IllegalArgumentException` e erros de desserialização passaram a retornar HTTP 400 com mensagem clara. Reteste: zero e negativo recusados nos três tipos e sem persistência. Commit `27e6967`. | Encapsulamento, construtores, setters e exceções, Aulas 3, 4 e 11. |
| bug05 | O documentário retornou R$ 9,90 no model e na consulta de preço promocional. | `model/Documentario.java:6–20`: faltava sobrescrever o método; herdava R$ 9,90 de `Conteudo`. | Sobrescrito `calcularPrecoAluguel()` com retorno zero, sem implementar `Promocionavel`. Reteste: ambos os preços iguais a zero. Commit `939a357`. | Herança, sobrescrita, abstração e interface, Aulas 6–9. |
| bug06 | Filme comum retornou R$ 11,88 na promoção; o de estreia havia retornado R$ 17,88 na análise inicial. | `model/Filme.java:25`: multiplicação por `1.2` aumentava o preço em 20%. | Aplicado o fator `0.8`, posteriormente expresso pela constante de desconto. Reteste: R$ 7,92 e R$ 11,92; um preço arbitrário de R$ 37,00 resulta em R$ 29,60. Commit `654faae`. | Implementação correta do contrato de uma interface, Aula 9. |
| bug07 | Cadastro de série retornou título e categoria nulos, duração e classificação zero, disponibilidade falsa, mesmo enviando os campos corretamente. | `model/Serie.java:14–16`: o construtor só preenchia temporadas; não chamava o construtor completo de `Conteudo`. O controller também não repassava disponibilidade. | Acrescentada disponibilidade ao construtor, com chamada a `super(...)` e encaminhamento do campo do JSON. Reteste: todos os campos preservados na resposta e no GET, com disponibilidade verdadeira e falsa. Commit `1e1c41b`. | Construtores, encadeamento com `super` e herança, Aulas 4 e 6. |
| bug08 | Série de cinco temporadas retornou R$ 9,90 no cálculo polimórfico e aproximadamente R$ 7,92 na promoção. | `model/Serie.java:19`: `calcularPrecoAluguel(double desconto)` era sobrecarga, não sobrescrita do método sem parâmetros. | Corrigida a assinatura para o método sem parâmetros, com `@Override`. Reteste: cinco temporadas custam R$ 24,50/R$ 19,60; duas custam R$ 9,80/R$ 7,84. Commit `cd624cd`. | Sobrescrita versus sobrecarga e polimorfismo, Aula 7. |
| bug09 | `POST /api/usuarios` respondeu HTTP 500; o log indicou que o identificador deveria ser atribuído antes de persistir. | `model/Usuario.java:11–12`: havia `@Id`, mas não uma estratégia de geração. | Adicionado `@GeneratedValue(strategy = GenerationType.IDENTITY)`, seguindo o mapeamento já usado por `Conteudo`. Reteste: HTTP 201, IDs distintos gerados pelo banco e ID enviado pelo cliente ignorado. Commit `42b26c1`. | Identidade da entidade e persistência JPA, Aula 13. |
| bug10 | `new Usuario("Nome preservado", 20, 100).getNome()` retornou `null`. Após corrigir bug09, a resposta HTTP também expunha o nome nulo. | `model/Usuario.java:22`: `nome = nome` atribuía o parâmetro a ele mesmo. | Corrigida a atribuição para `this.nome = nome`. Reteste: nome correto no construtor, no POST e no GET persistido. Commit `4116a1c`. | Estado do objeto, parâmetros, atributos e `this`, Aulas 1 e 4. |
| bug11 | O model considerava insuficiente um saldo de 100 para preço 9,90. No teste original com saldo zero, o aluguel conseguiu deixar o saldo em -9,90. | `model/Usuario.java:24,28,31–33,75`: comparação invertida e ausência de proteção nos caminhos de alteração de créditos. | Corrigida a comparação para saldo maior ou igual ao preço. Valores finitos e não negativos passaram a ser validados no construtor/setter/débito, com bloqueio de débito acima do saldo. Retestes: insuficiência 422, saldo exato permitido, débito correto e documentário grátis com saldo zero. Commit `82bdee5`. | Regras no model, encapsulamento, construtores e exceções, Aulas 2–4 e 11. |
| bug12 | No teste direto original, o usuário alugou um filme marcado como indisponível; nenhum erro de indisponibilidade foi lançado. | `model/Usuario.java:36–50`: não verificava `isDisponivel()` antes do aluguel. | Adicionada a verificação de disponibilidade antes de idade, preço e débito, com lançamento de `ConteudoIndisponivelException`. Reteste: HTTP 409 inclusive para documentário gratuito, sem alterar saldo ou conteúdo. Commit `5df7d29`. | Associação entre objetos e proteção das regras de negócio, Aulas 2, 5 e 11. |

Os bugs se bloqueavam entre si: a ausência de ID impedia testar aluguéis pela API; a comparação de créditos podia mascarar a falta da verificação de disponibilidade. Por isso, foram usados testes diretos do model e retestes HTTP depois de remover cada bloqueio. Uma exceção ser checked, por si só, não obriga o Spring a retornar 500: a ausência do handler era o motivo de a mensagem de classificação não chegar ao cliente.

## Parte 2 — Ajustes de Clean Code

| # | Onde estava | Qual princípio/boas práticas era violado | O que eu mudei |
|---|---|---|---|
| clean01 | `model/Usuario.java`, método `alugar` | Nomes sem intenção explícita (`c` e `p`). | Renomeados para `conteudo` e `precoAluguel`, com débitos e recusas revalidados. Commit `7ab80e8`. |
| clean02 | `model/Conteudo.java` e cadastros de `ConteudoController` | Campo público permitia contornar a proteção do objeto. | `duracaoMinutos` passou a ser privado, com acesso por getter nos controllers. Mantidos o setter validado e o campo JSON existente. Commit `6f40878`. |
| clean03 | `Conteudo`, `Filme`, `Serie` e `Promocionavel` | Números de regras comerciais espalhados e sem nomes. | Criadas constantes para preço-base, acréscimo de estreia, preço por temporada e desconto, com os mesmos preços confirmados nos testes. Commit `df8f7df`. |
| clean04 | `model/Usuario.java`, bloco de `System.out.println` | Mistura de regra de negócio com apresentação do recibo. | Extraída a classe simples `apresentacao/ReciboAluguel`; o controller solicita a impressão após salvar. O model não imprime recibos. Commit `2f331a9`. |
| clean05 | Final de `controller/ConteudoController.java` | Código morto e protótipo comentado dificultavam entender a regra vigente. | Removidos `calcularDescontoAntigo` e o trecho abandonado de cupons. O histórico Git preserva a versão anterior. Commit `77aa886`. |
| clean06 | `Usuario`, `Serie` e `Conteudo` | Comentário dizia que o débito adicionava créditos; outros apenas repetiam o código. | Removidos o comentário incorreto e os comentários redundantes de getters, construtor e preço. Preservada a documentação útil da interface. Commit `ee3a704`. |

## Parte 3 — Perguntas de reflexão

### 1. Injeção de dependência (Aula 13)

`ConteudoController` recebe um `ConteudoRepository` pelo campo anotado com `@Autowired`.<br>
Esse repository é uma interface, então `new ConteudoRepository()` nem seria uma construção válida em Java.<br>
Ao iniciar a aplicação, o Spring Data cria uma implementação em forma de proxy e a registra como bean.<br>
Como no `ProdutoRepository` da Aula 13, esse objeto é conectado à persistência, incluindo o `EntityManager` e as transações dos métodos do repository.<br>
O Spring localiza um bean compatível com o tipo do campo e o injeta no controller que também gerencia.<br>
Criar manualmente uma classe qualquer com `new` não configura automaticamente essa infraestrutura nem processa `@Autowired`.<br>
Isso é diferente de `ReciboAluguel`, uma classe simples sem dependências do Spring, que pode ser criada normalmente com `new`.

### 2. JDBC vs Spring Data JPA (Aulas 12 e 13)

No `ProdutoDAO` da Aula 12, precisamos obter a `Connection`, preparar o SQL com `?`, preencher parâmetros e ler o `ResultSet`.<br>
Também precisamos transformar cada linha em objeto e fechar os recursos corretamente, por exemplo com `try-with-resources`.<br>
Neste projeto, `ConteudoRepository` estende `JpaRepository`, que já oferece operações como `save`, `findById` e `findAll`.<br>
O JPA/Hibernate cuida do mapeamento das entidades e da geração das operações de persistência; o Spring Data fornece a implementação do repository.<br>
Em `findByCategoria`, o Spring Data interpreta o nome do método e a propriedade `categoria` para construir a consulta.<br>
Isso substituiu o filtro com `==` do controller e evitou carregar todo o catálogo para filtrar na aplicação.<br>
JDBC continua útil quando precisamos controlar diretamente um SQL específico, recursos do banco ou processamento que não se encaixa bem no mapeamento de entidades.

### 3. Exceções checked vs unchecked (Aula 11)

Uma classe que estende `Exception`, sem estender `RuntimeException`, é checked: o compilador exige capturar ou declarar sua propagação.<br>
Por isso, a versão original de `Usuario.alugar` e de `AluguelController.alugar` declarava `throws ClassificacaoIndicativaException`.<br>
Como `EstoqueInsuficienteException` da Aula 11, nossa exceção de negócio estende `RuntimeException` e pode propagar sem essa declaração.<br>
Trocar a superclasse por `RuntimeException` não faz a mensagem aparecer automaticamente na resposta HTTP.<br>
O passo decisivo foi acrescentar `@ExceptionHandler(ClassificacaoIndicativaException.class)` ao `GlobalExceptionHandler`.<br>
Esse método retorna HTTP 422 com `erro` igual à mensagem que informa idade, título e classificação.<br>
O teste com usuário de 12 anos e conteúdo de classificação 14 confirmou essa resposta e mostrou que o saldo continuou intacto.

### 4. Sobrescrita vs sobrecarga (Aula 7)

`Conteudo` declara `calcularPrecoAluguel()` sem parâmetros.<br>
A série declarava `calcularPrecoAluguel(double desconto)`, que tem uma lista de parâmetros diferente.<br>
Isso cria uma sobrecarga: dois métodos com o mesmo nome, mas assinaturas diferentes, e o compilador aceita os dois.<br>
Quando `Usuario.alugar` chamava o método sem argumentos, a série herdava o cálculo de R$ 9,90 de `Conteudo`.<br>
Corrigimos a série para implementar `calcularPrecoAluguel()` com `@Override` e multiplicar R$ 4,90 pelas temporadas.<br>
Se `@Override` estivesse no método antigo, o compilador acusaria que aquele método não sobrescrevia o da superclasse.<br>
O teste por uma referência do tipo `Conteudo` confirmou R$ 24,50 para cinco temporadas e R$ 9,80 para duas.

### 5. Onde blindar o objeto? (Aulas 3, 4 e 13)

A duração é validada em `Conteudo.setDuracaoMinutos`, reutilizado pelo construtor, seguindo a proteção do estado ensinada nas Aulas 3 e 4.<br>
Isso protege tanto a criação feita pelo controller quanto as alterações realizadas pelo setter durante o recebimento do JSON.<br>
Créditos negativos ou não finitos são recusados em `Usuario.setCreditos`, também chamado pelo construtor.<br>
`debitarCreditos` precisa verificar adicionalmente o valor solicitado e o saldo, porque validar o saldo inicial não impede um débito posterior inválido.<br>
`Usuario.alugar` verifica disponibilidade, classificação e saldo antes de alterar o objeto associado ou debitar.<br>
Os campos nulos da série eram causados por ignorar os dados recebidos: a chamada correta a `super(...)` passou a inicializá-los.<br>
Isso não significa uma regra geral contra qualquer campo nulo: esta correção preserva os campos recebidos e as validações pedidas, mantendo o construtor vazio exigido pela infraestrutura JPA.

### 6. Abstração e interface (Aulas 8 e 9)

`Conteudo` é a base abstrata da hierarquia e reúne estado, identificação JPA e comportamentos compartilhados dos conteúdos.<br>
Filme, série e documentário são conteúdos, por isso herdam dessa classe, que não pode ser instanciada diretamente.<br>
`Promocionavel` define outra capacidade: aplicar o desconto contratado, sem carregar o estado de uma entidade.<br>
Atualmente apenas filme e série implementam essa interface, e o documentário continua gratuito sem participar dela.<br>
Se a regra do negócio mudasse, acrescentaríamos `implements Promocionavel` e o método `aplicarPromocao` em `Documentario`, além dos testes.<br>
`Conteudo.calcularPrecoPromocional` já consulta essa capacidade com `instanceof`, então não exigiria um novo caso específico, nem mudança no endpoint.<br>
Enquanto o preço normal do documentário continuar zero, qualquer desconto continuará resultando em zero; uma cobrança nova exigiria também alterar explicitamente seu cálculo de aluguel.

## Parte 4 — Considerações sobre as correções

A principal dificuldade foi distinguir bugs de suas consequências: a falha de geração do ID bloqueava a API de aluguel, e a comparação de créditos escondia outros erros. Os testes foram repetidos após corrigir essas dependências. Foram preservados os preços normais no aluguel e o endpoint separado de promoção, sem criar regras específicas para títulos dos exemplos.

## Resultados da validação

A compilação e o empacotamento foram concluídos com Java 17 e Maven. O JAR foi iniciado com H2, mantendo o `pom.xml` e as dependências originais.

| Verificação | Resultado |
|---|---|
| Compilação e empacotamento | BUILD SUCCESS |
| Inicialização do JAR com H2 | Aprovada |
| Testes diretos do model | 40 verificações aprovadas |
| Cenários HTTP da API | 13 grupos aprovados |
| Registros da execução | 133 registros, nenhuma falha |

Os registros incluem requisições, respostas e resultados de testes; não correspondem a 133 testes independentes. As evidências abrangem o ambiente H2, sem validação autenticada no Oracle FIAP ou confirmação de execução pelo Eclipse.

Evidências: [comportamento original](verificacao/evidencias/original.json), [validação após as correções](verificacao/evidencias/conferencia-aulas-2026-09-07.json) e [resultados por correção](verificacao/evidencias/por-correcao.json).
