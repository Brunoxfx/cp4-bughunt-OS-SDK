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
| bug01 | `GET /api/conteudos/999999999` respondeu HTTP 200 sem corpo, apesar de o conteúdo não existir. | `controller/ConteudoController.java:32–39`: `catch (Exception)` vazio engolia a exceção e retornava `null`. | Remover o `try/catch` e deixar a exceção chegar ao handler existente. Reteste: HTTP 404 e mensagem em `erro`. Commit `1dccb57`. | Propagação e tratamento centralizado de exceções, Aula 11. |
| bug02 | Depois de cadastrar ficção e drama, a busca por `FICCAO` devolveu uma lista vazia. | `controller/ConteudoController.java:45–51`: comparava referências de `String` com `==`. | Usar `ConteudoRepository.findByCategoria(categoria)`. Reteste: somente a categoria solicitada; categoria inexistente retorna `[]`. Commit `4bb2ddb`. | Igualdade de objetos e consulta derivada com Spring Data JPA, Aula 13. |
| bug03 | No teste direto, o menor de 12 anos recebeu uma exceção checked. A revisão mostrou ausência de handler para ela; a reprodução HTTP inicial ficou bloqueada pelo cadastro de usuário (bug09). | `exception/ClassificacaoIndicativaException.java:3` e `exception/GlobalExceptionHandler.java:11–27`: exceção checked sem mapeamento da regra para HTTP. | Estender `RuntimeException`, remover `throws` desnecessários e incluir handler 422 com a mensagem original. Após bug09, teste HTTP confirmou classificação e idade na resposta, sem débito. Commit `611bbd8`. | Checked versus unchecked e tradução de exceções de negócio, Aula 11. |
| bug04 | Filme com duração zero foi salvo com HTTP 201. Construtor e setter também aceitaram duração inválida em Java. | `model/Conteudo.java:27,55`: atribuição direta, sem validação. | Validar duração positiva no setter e reutilizá-lo no construtor. Tratar `IllegalArgumentException` e erros de desserialização como HTTP 400 com mensagem clara. Reteste: zero e negativo recusados nos três tipos e sem persistência. Commit `27e6967`. | Encapsulamento, construtores, setters e exceções, Aulas 3, 4 e 11. |
| bug05 | O documentário retornou R$ 9,90 no model e na consulta de preço promocional. | `model/Documentario.java:6–20`: faltava sobrescrever o método; herdava R$ 9,90 de `Conteudo`. | Sobrescrever `calcularPrecoAluguel()` retornando zero, sem implementar `Promocionavel`. Reteste: ambos os preços iguais a zero. Commit `939a357`. | Herança, sobrescrita, abstração e interface, Aulas 6–9. |
| bug06 | Filme comum retornou R$ 11,88 na promoção; o de estreia havia retornado R$ 17,88 na análise inicial. | `model/Filme.java:25`: multiplicação por `1.2` aumentava o preço em 20%. | Aplicar fator `0.8`, posteriormente expresso pela constante de desconto. Reteste: R$ 7,92 e R$ 11,92; um preço arbitrário de R$ 37,00 resulta em R$ 29,60. Commit `654faae`. | Implementação correta do contrato de uma interface, Aula 9. |
| bug07 | Cadastro de série retornou título e categoria nulos, duração e classificação zero, disponibilidade falsa, mesmo enviando os campos corretamente. | `model/Serie.java:14–16`: o construtor só preenchia temporadas; não chamava o construtor completo de `Conteudo`. O controller também não repassava disponibilidade. | Acrescentar disponibilidade ao construtor, chamar `super(...)` e encaminhar o campo do JSON. Reteste: todos os campos preservados na resposta e no GET, com disponibilidade verdadeira e falsa. Commit `1e1c41b`. | Construtores, encadeamento com `super` e herança, Aulas 4 e 6. |
| bug08 | Série de cinco temporadas retornou R$ 9,90 no cálculo polimórfico e aproximadamente R$ 7,92 na promoção. | `model/Serie.java:19`: `calcularPrecoAluguel(double desconto)` era sobrecarga, não sobrescrita do método sem parâmetros. | Usar a assinatura sem parâmetros e `@Override`. Reteste: cinco temporadas custam R$ 24,50/R$ 19,60; duas custam R$ 9,80/R$ 7,84. Commit `cd624cd`. | Sobrescrita versus sobrecarga e polimorfismo, Aula 7. |
| bug09 | `POST /api/usuarios` respondeu HTTP 500; o log indicou que o identificador deveria ser atribuído antes de persistir. | `model/Usuario.java:11–12`: havia `@Id`, mas não uma estratégia de geração. | Adicionar `@GeneratedValue(strategy = GenerationType.IDENTITY)`, seguindo o mapeamento já usado por `Conteudo`. Reteste: HTTP 201, IDs distintos gerados pelo banco e ID enviado pelo cliente ignorado. Commit `42b26c1`. | Identidade da entidade e persistência JPA, Aula 13. |
| bug10 | `new Usuario("Nome preservado", 20, 100).getNome()` retornou `null`. Após corrigir bug09, a resposta HTTP também expunha o nome nulo. | `model/Usuario.java:22`: `nome = nome` atribuía o parâmetro a ele mesmo. | Usar `this.nome = nome`. Reteste: nome correto no construtor, no POST e no GET persistido. Commit `4116a1c`. | Estado do objeto, parâmetros, atributos e `this`, Aulas 1 e 4. |
| bug11 | O model considerava insuficiente um saldo de 100 para preço 9,90. No teste original com saldo zero, o aluguel conseguiu deixar o saldo em -9,90. | `model/Usuario.java:24,28,31–33,75`: comparação invertida e ausência de proteção nos caminhos de alteração de créditos. | Comparar saldo maior ou igual ao preço; validar valores finitos e não negativos no construtor/setter/débito; impedir débito acima do saldo. Retestes: insuficiência 422, saldo exato permitido, débito correto e documentário grátis com saldo zero. Commit `82bdee5`. | Regras no model, encapsulamento, construtores e exceções, Aulas 2–4 e 11. |
| bug12 | No teste direto original, o usuário alugou um filme marcado como indisponível; nenhum erro de indisponibilidade foi lançado. | `model/Usuario.java:36–50`: não verificava `isDisponivel()` antes do aluguel. | Verificar disponibilidade antes de idade, preço e débito; lançar `ConteudoIndisponivelException`. Reteste: HTTP 409 inclusive para documentário gratuito, sem alterar saldo ou conteúdo. Commit `5df7d29`. | Associação entre objetos e proteção das regras de negócio, Aulas 2, 5 e 11. |

Os bugs se bloqueavam entre si: a ausência de ID impedia testar aluguéis pela API; a comparação de créditos podia mascarar a falta da verificação de disponibilidade. Por isso, foram usados testes diretos do model e retestes HTTP depois de remover cada bloqueio. Uma exceção ser checked, por si só, não obriga o Spring a retornar 500: a ausência do handler era o motivo de a mensagem de classificação não chegar ao cliente.

## Parte 2 — Ajustes de Clean Code

| # | Onde estava | Qual princípio/boas práticas era violado | O que eu mudei |
|---|---|---|---|
| clean01 | `model/Usuario.java`, método `alugar` | Nomes sem intenção explícita (`c` e `p`). | Renomear para `conteudo` e `precoAluguel`. Revalidar débitos e recusas. Commit `7ab80e8`. |
| clean02 | `model/Conteudo.java` e cadastros de `ConteudoController` | Campo público permitia contornar a proteção do objeto. | Tornar `duracaoMinutos` privado e usar getter nos controllers. Manter setter validado e o campo JSON existente. Commit `6f40878`. |
| clean03 | `Conteudo`, `Filme`, `Serie` e `Promocionavel` | Números de regras comerciais espalhados e sem nomes. | Criar constantes para preço-base, acréscimo de estreia, preço por temporada e desconto. Confirmar os mesmos preços. Commit `df8f7df`. |
| clean04 | `model/Usuario.java`, bloco de `System.out.println` | Mistura de regra de negócio com apresentação do recibo. | Extrair uma classe simples `apresentacao/ReciboAluguel`; o controller solicita a impressão após salvar. O model não imprime recibos. Commit `2f331a9`. |
| clean05 | Final de `controller/ConteudoController.java` | Código morto e protótipo comentado dificultavam entender a regra vigente. | Remover `calcularDescontoAntigo` e o trecho abandonado de cupons. O histórico Git preserva a versão anterior. Commit `77aa886`. |
| clean06 | `Usuario`, `Serie` e `Conteudo` | Comentário dizia que o débito adicionava créditos; outros apenas repetiam o código. | Remover o comentário incorreto e os comentários redundantes de getters, construtor e preço. Preservar a documentação útil da interface. Commit `ee3a704`. |

## Parte 3 — Perguntas de reflexão

Textos preparados com base no código corrigido. **Cada integrante deve revisar as respostas e expressar sua própria compreensão antes de entregar.**

Conferidos com os PDFs fornecidos em `Downloads/java`: [relação entre as aulas e as correções](verificacao/CONFERENCIA_AULAS.md). A pasta contém as aulas 1–9, 11 e 12; não contém as aulas 10 e 13. As referências à Aula 13 abaixo seguem os temas e perguntas do checkpoint, sem afirmar que esse PDF foi consultado.

### 1. Injeção de dependência (Aula 13)

`ConteudoController` recebe um `ConteudoRepository` pelo campo anotado com `@Autowired`.<br>
Esse repository é uma interface, então `new ConteudoRepository()` nem seria uma construção válida em Java.<br>
Ao iniciar a aplicação, o Spring Data cria uma implementação em forma de proxy e a registra como bean.<br>
Esse objeto é conectado à infraestrutura de persistência, incluindo o `EntityManager` e o tratamento transacional dos métodos do repository.<br>
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

## Parte 4 — Espaço livre (opcional)

A principal dificuldade foi distinguir bugs de suas consequências: a falha de geração do ID bloqueava a API de aluguel, e a comparação de créditos escondia outros erros. Os testes foram repetidos após corrigir essas dependências. Foram preservados os preços normais no aluguel e o endpoint separado de promoção, sem criar regras específicas para títulos dos exemplos.

## Como executar

Requisitos: **JDK 17 ou superior e Maven**. O `pom.xml` original foi preservado, inclusive Spring Boot 4.1.1. O terminal usado na análise tinha Java 11 como padrão; foi selecionado o JDK 17 somente para os comandos deste projeto, sem alterar a configuração global.

Na raiz do repositório, com `JAVA_HOME` apontando para o JDK correto:

```powershell
java -version
mvn package
```

Para testar sem Oracle, mantendo o arquivo de configuração intacto:

```powershell
java -jar target/streamfiap-0.0.1-SNAPSHOT.jar --spring.datasource.url=jdbc:h2:mem:streamfiap --spring.datasource.driverClassName=org.h2.Driver --spring.datasource.username=sa --spring.datasource.password=
```

A API fica em `http://localhost:8080`. Os dados desse H2 são temporários e desaparecem ao encerrar o processo.

### Oracle FIAP e Eclipse

O arquivo versionado `src/main/resources/application.properties` continua exatamente com `SEU_RM` e `SUA_SENHA`. Configure os valores reais **somente na máquina**, por exemplo nas variáveis `SPRING_DATASOURCE_USERNAME` e `SPRING_DATASOURCE_PASSWORD` da configuração de execução. Não inclua credenciais reais em commits, screenshots ou logs de entrega.

No Eclipse, importe com **File → Import → Maven → Existing Maven Projects**, selecione esta pasta, configure um JDK 17 ou superior e execute `StreamFiapApplication`. Nas configurações de execução, informe as variáveis locais do Oracle. Para uma conferência temporária em H2 pelo Eclipse, use os mesmos argumentos `--spring.datasource.*` apresentados acima.

Confira a mensagem `Started StreamFiapApplication` e repita os cenários descritos em [verificacao/ROTEIRO.md](verificacao/ROTEIRO.md), anotando os IDs realmente retornados. Não apague tabelas ou dados preexistentes do schema para tentar resolver uma incompatibilidade: primeiro identifique sua origem. A geração de ID foi validada no H2; a compatibilidade com a versão e as tabelas existentes do Oracle do grupo ainda precisa ser conferida.

Também está preparado um modo de teste para Oracle, usando apenas as dependências existentes e a biblioteca padrão do Python. Na raiz do projeto, em um terminal interativo com Java 17 e Python 3:

```powershell
mvn -B clean verify dependency:build-classpath "-Dmdep.outputFile=target/classpath.txt"
python verificacao/verificar.py all --jar --oracle --label oracle-final
```

O comando pede usuário e senha localmente, com a senha oculta. Primeiro executa uma inspeção JDBC somente de leitura: exige Oracle 12c ou superior e verifica as tabelas e os IDs automáticos. Se ambas as tabelas estiverem ausentes, permite sua criação pelo Hibernate; se ambas existirem com IDs `IDENTITY`, usa `validate`, sem modificar a estrutura. Schema parcial ou IDs incompatíveis interrompem a execução para revisão. A validação do Hibernate e os testes ainda podem revelar outras incompatibilidades.

Os testes cadastram dados com prefixo único `CP4_...`, alugam somente conteúdos criados nessa execução e mantêm esses registros no Oracle. Reiniciam a API para conferir a persistência de conteúdos e usuários e a conservação dos conteúdos anteriores. Execute sem outra pessoa modificando o catálogo ao mesmo tempo. As evidências e os logs ficam em `target/verificacao`, ignorado pelo Git; revise-os antes de compartilhar. **Modo Oracle preparado, mas ainda não executado: a senha não estava disponível em 07/09/2026.** O teste automatizado não substitui a conferência do play no Eclipse.

## Validação realizada

- Compilação e empacotamento Maven com Java 17: **BUILD SUCCESS**.
- Inicialização do JAR empacotado com H2: **confirmada**.
- Testes diretos do model: **40 verificações aprovadas**.
- API: **13 grupos de cenários aprovados**, abrangendo os 12 bugs e verificações complementares do contrato.
- Execução final: **133 registros de evidência, nenhuma falha**. Registros incluem requisições, resultados e saídas dos testes; não equivalem a 133 testes independentes.
- Os testes não dependem de JUnit nem alteram o `pom.xml`: Java e biblioteca padrão do Python. Por isso, `mvn test` isoladamente informa que não há testes; é necessário executar também o roteiro de verificação.

Evidências: [estado original](verificacao/evidencias/original.json), [execução final](verificacao/evidencias/final.json) e [resumo por correção](verificacao/evidencias/por-correcao.json). Essas execuções documentadas utilizaram H2 em memória. O verificador continua usando H2 por padrão; somente a opção explícita `--oracle` acessa o Oracle com as credenciais digitadas localmente.

## Checklist de entrega

Revisão integral do PDF e nova execução em 07/09/2026: [relatório de conferência](verificacao/REVISAO_CHECKPOINT4.md). O relatório distingue os testes locais aprovados das pendências externas.

- [x] Primeiro commit preserva o estado original recebido.
- [x] Doze commits `fix: bugNN`, um por correção.
- [x] Seis commits `refactor: cleanNN`, um por ajuste.
- [x] Dependências originais, sem bibliotecas ou frameworks adicionados.
- [x] `application.properties` versionado mantém `SEU_RM` e `SUA_SENHA`.
- [x] Tabelas dos achados e seis respostas de reflexão preenchidas.
- [x] Compilação, empacotamento e contrato testados com H2.
- [x] Preencher integrantes, RMs e turma.
- [x] Definir o nome do grupo: OS-SDK.
- [ ] Revisar as reflexões com as palavras e a compreensão do grupo.
- [ ] Validar conexão, persistência e contrato no Oracle FIAP.
- [ ] Instalar o Eclipse, importar como Maven e conferir o play sem erros de inicialização.
- [x] Publicar o projeto e o histórico no repositório **público** [Brunoxfx/cp4-bughunt-OS-SDK](https://github.com/Brunoxfx/cp4-bughunt-OS-SDK).
- [x] Adequar o nome do repositório ao padrão `cp4-bughunt-<nome-do-grupo>` exigido no PDF.
- [ ] Entregar o mesmo link no Teams para todos os integrantes.
