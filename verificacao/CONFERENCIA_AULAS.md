# Conferência das aulas e do Checkpoint 4

Revisão em 07/09/2026. Fonte principal: `CHECKPOINT 4.pdf`, seis páginas, recebido na pasta `projeto`. Material complementar: os 11 PDFs da pasta `Downloads/java` (105 páginas no total). As páginas abaixo são as páginas dos PDFs, contadas a partir de 1. Os materiais do professor não foram copiados para o repositório.

## Relação com o código entregue

| Material recebido | Páginas usadas como referência | Aplicação no StreamFIAP |
|---|---|---|
| Aula 1 — Fundamentos de OO: Classes e Objetos | 1–2, 10 | Estado pertence à instância; `this.nome = nome` corrige bug10. Nomes descritivos em clean01. Artefatos de compilação fora do Git. |
| Aula 2 — Métodos e Comportamentos | 1–2 | Métodos expressam ações e protegem o estado: `debitarCreditos` e `alugar`, bugs11/12. |
| Aula 3 — Protegendo o Sistema: Encapsulamento | 1–2, 4–5 | Duração privada, getter para leitura e setter validado, bug04/clean02. Mantidos os setters públicos necessários ao contrato JSON existente. |
| Aula 4 — Construtores | 1–2, 4–5 | Construção reutiliza validações; `this` distingue atributo de parâmetro. Construtores vazios do JPA preservados. |
| Aula 5 — Quando os Objetos Conversam: Relacionamentos | 1–2, 6 | `Usuario.alugar(Conteudo)` usa a referência ao conteúdo para consultar e alterar seu estado. É uma colaboração por parâmetro; não foi criada uma associação persistente nova. |
| Aula 6 — A Árvore Genealógica: Herança | 1–3 | `Serie` encaminha todos os atributos herdados ao construtor com `super(...)`, bug07. |
| Aula 07 — Muitas Formas: Polimorfismo de Sobrescrita | 1–2, 7 | Assinatura idêntica e `@Override` no preço da série; chamada através de `Conteudo` despacha para a subclasse, bug08. |
| Aula 8 — O Molde Invisível: Classes Abstratas | 1–4 | `Conteudo` permanece abstrata, com estado e métodos concretos compartilhados; documentário especializa o preço, bug05. |
| Aula 9 — O Contrato de Comportamento: Interfaces | 1–2, 5 | `Promocionavel` representa a capacidade de desconto; somente filme e série a implementam. Constantes com significado em clean03. |
| Aula 11 — Quando Dá Errado: Tratamento de Exceções | 1–3, 6 | Exceções de negócio específicas, mensagem clara e validação antes da alteração; remoção do catch vazio e mapeamento de classificação, bugs01/03/11/12. |
| Aula 12 — Conectando ao Banco Oracle (JDBC) | 4–8, 10–12, 16 | Persistência separada do model, SQL parametrizado e fechamento de recursos. `IDENTITY` no exemplo Oracle 12c+. Aplicação desses cuidados na inspeção auxiliar `OraclePreflight.java`; repositories JPA originais preservados. |

As aulas 10 e 13 não estão nessa pasta. As reflexões sobre Spring Data JPA e injeção de dependência respondem ao template recebido e descrevem o código do projeto; não são atribuídas a uma leitura da Aula 13 ausente.

Os exemplos das aulas orientam as correções; os requisitos da atividade continuam sendo os do checkpoint. Os exercícios independentes de FiapRide, ProdutoDAO e Bug Hunt JDBC não fazem parte da entrega StreamFIAP. Não foram acrescentados DAOs, novas bibliotecas ou novas regras de preço. Também não se copiou a afirmação imprecisa da Aula 8 de que métodos abstratos de classes seriam implicitamente públicos: em Java, o modificador de acesso precisa ser considerado separadamente.

## Reconferência do PDF da atividade

| Parte do checkpoint | Conferência e situação |
|---|---|
| Página 1: estrutura e preços | Models, controllers, repositories e handler preservados. Filme 9,90/14,90; série 4,90 por temporada; documentário zero. Promoção de 20% somente para filme e série. |
| Página 2: cadastros, consultas e aluguel | Cobertos pelos testes Java e HTTP: duração inválida, categoria, ID/nome, indisponibilidade, classificação, saldo e débito. Oracle continua pendente. |
| Página 3: mudanças mínimas e commits | 12 correções e 6 ajustes em commits individuais; POM original. Nenhuma regra condicionada aos títulos dos exemplos. |
| Páginas 3–4: execução e persistência | Java 17/Maven e H2 executados novamente: 40 verificações do model e 13 grupos HTTP aprovados, 133 registros sem falhas. Modo Oracle preparado com inspeção de schema e teste após reiniciar a API, ainda sem execução autenticada. O grupo informou que o Eclipse não está instalado neste computador. |
| Páginas 4–5: GitHub e README | Grupo OS-SDK, cinco integrantes/RMs e turma 2CCPG preenchidos. Repositório público renomeado; tabelas e seis reflexões presentes. |
| Páginas 5–6: credenciais e checklist | `SEU_RM`/`SUA_SENHA` permanecem no arquivo versionado. Usuário informou que ainda não tem a senha Oracle. Entrega no Teams e revisão pessoal das reflexões pelo grupo não confirmadas. |

## Limites da conclusão

A verificação H2 demonstra o comportamento local, mas não comprova autenticação, compatibilidade de schema ou persistência no Oracle FIAP. Compilar com Maven também não comprova que o Eclipse foi importado e iniciado corretamente. Esses itens permanecem explicitamente abertos no README até haver evidência real.

O auxiliar Oracle não apaga tabelas ou dados. Quando o schema já contém as duas tabelas, a aplicação usa `validate`. Se a inspeção detectar schema parcial ou identidade incompatível, interrompe antes de iniciar a API. A correção de um schema preexistente depende da leitura do erro e da identificação dos dados, sem apagar trabalhos de outras atividades.
