# Reprodução dos testes

Execute os comandos a partir da raiz do repositório, com Java 17 ou superior, Maven e Python 3 disponíveis. Nenhuma biblioteca Python adicional é necessária.

## Verificação automatizada em H2

```powershell
mvn package
mvn dependency:build-classpath -Dmdep.outputFile=target/classpath.txt
python verificacao/verificar.py all --label minha-verificacao --jar
```

Defina `JAVA_HOME` para o diretório do seu JDK antes de executar o script. Ele compila `ModelChecks.java` em `target/verificacao`, testa o model, inicia o JAR em uma porta local livre com H2 em memória, verifica a API e encerra o processo. Código de saída zero significa que todos os cenários passaram; saída diferente de zero indica falha.

O objetivo `dependency:build-classpath` é uma ferramenta Maven para listar as dependências já declaradas. Ele não adiciona bibliotecas à aplicação nem modifica o `pom.xml`. Os testes Java são executados explicitamente pelo script, sem JUnit.

As evidências da nova execução ficam em `target/verificacao/minha-verificacao.json` e `.log`. Essa pasta é ignorada pelo Git. Os JSONs em `verificacao/evidencias` são o registro da execução entregue, não devem ser confundidos com uma nova execução do grupo.

Para repetir apenas um cenário durante o desenvolvimento:

```powershell
python verificacao/verificar.py bug06 --label reteste-filme --compile
```

`--compile` usa `javac --release 17` sobre os fontes atuais; sem `--jar`, a API usa `target/classes`. Para testar a versão empacotada após mudar o código, execute novamente `mvn package` e use `--jar`. O cenário HTTP de classificação depende de usuários persistidos; execute `bug03 bug09` juntos ou prefira `all`.

## Roteiro manual com curl ou Postman

Inicie a aplicação como descrito no README. Use `Content-Type: application/json` nos POSTs. **Guarde os IDs retornados**, inclusive no Oracle; não suponha que começam em 1.

### 1. Conteúdos

Envie a `POST /api/conteudos/filme`:

```json
{"titulo":"Filme de verificacao","categoria":"FICCAO","duracaoMinutos":120,"classificacaoEtaria":14,"disponivel":true,"estreia":true}
```

Envie a `POST /api/conteudos/serie`:

```json
{"titulo":"Serie de verificacao","categoria":"FICCAO","duracaoMinutos":50,"classificacaoEtaria":14,"disponivel":true,"numeroTemporadas":5}
```

Envie a `POST /api/conteudos/documentario`:

```json
{"titulo":"Documentario de verificacao","categoria":"CIENCIA","duracaoMinutos":60,"classificacaoEtaria":0,"disponivel":false,"tema":"Natureza"}
```

Verifique HTTP 201, ID gerado e todos os campos na resposta; consulte `GET /api/conteudos/{id}` para confirmar persistência. Para cada tipo, repita com duração zero e negativa: deve responder HTTP 400, com `erro` explicando a duração, sem aumentar o catálogo. Compare os IDs da listagem antes e depois.

Consulte `GET /api/conteudos/{id}/preco-promocional`: estreia = 11,92; série de cinco temporadas = 19,60; documentário = 0. Cadastre também filme sem estreia e série de duas temporadas: preços promocionais 7,92 e 7,84. O preço normal é conferido pelo débito dos aluguéis e pelos testes Java.

Consulte `GET /api/conteudos/categoria/FICCAO`: somente ficção. Uma categoria sem registros deve retornar `[]`. Consulte um ID que realmente não existe: HTTP 404 com mensagem `Conteúdo não encontrado`, inclusive no endpoint promocional.

### 2. Usuários

Envie a `POST /api/usuarios`:

```json
{"nome":"Adulto de verificacao","idade":20,"creditos":100}
```

Repita para um adulto sem créditos e um usuário de 12 anos com 100 créditos. Confira HTTP 201, identificadores distintos e nomes preservados no POST e no `GET /api/usuarios/{id}`. Um cadastro com créditos negativos deve retornar HTTP 400 com mensagem clara.

### 3. Aluguéis

Chame `POST /api/alugueis?usuarioId=X&conteudoId=Y`, usando os IDs reais. Cadastre conteúdo disponível novo para cada aluguel válido: este projeto o marca como indisponível depois de alugado.

| Cenário | Resultado esperado | Conferência por GET |
|---|---|---|
| Adulto, 100 créditos, filme comum disponível | HTTP 200; saldo 90,10 | Saldo persistido e conteúdo indisponível |
| Adulto, 100 créditos, estreia disponível | HTTP 200; saldo 85,10 | Débito normal de 14,90, sem desconto automático |
| Adulto, 100 créditos, série com cinco temporadas | HTTP 200; saldo 75,50 | Débito de 24,50 |
| Adulto, 100 créditos, série com duas temporadas | HTTP 200; saldo 90,20 | Débito de 9,80 |
| Adulto, 9,90 créditos, filme comum | HTTP 200; saldo zero | Saldo exato é suficiente |
| Adulto, zero ou 9,89 créditos, filme comum | HTTP 422; mensagem de créditos insuficientes | Saldo e disponibilidade permanecem iguais |
| Usuário de 12 anos, conteúdo de classificação 14 | HTTP 422; mensagem com idade e classificação | Nenhum débito nem mudança de disponibilidade |
| Usuário de 14 anos, conteúdo de classificação 14 | HTTP 200 com saldo suficiente | Idade igual à classificação é permitida |
| Conteúdo indisponível, incluindo documentário | HTTP 409; mensagem de indisponibilidade | Nenhuma alteração persistida |
| Adulto sem créditos, documentário disponível | HTTP 200; saldo zero | Conteúdo passa a indisponível |
| Segundo aluguel do mesmo conteúdo | HTTP 409 | Não debita novamente |

Respostas de erro usam `{"erro":"mensagem"}`. Registre status, corpo, IDs e resultados dos GETs para documentar a execução no Oracle do grupo. Não inclua credenciais nas evidências.

## Execução original e limites da evidência

`original.json` registra o código anterior às correções. Algumas falhas HTTP ficaram bloqueadas pelo bug09; nesses casos o teste direto do model e a leitura do código localizaram a causa. `por-correcao.json` registra os retestes por etapa, e `final.json` registra o JAR corrigido: 40 verificações diretas do model e 13 grupos HTTP aprovados, em 133 registros.

Os resultados em H2 não certificam compatibilidade com o schema Oracle existente nem a execução pelo Eclipse. Faça essas duas conferências antes de marcar o checklist final do README.
