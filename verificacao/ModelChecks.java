import br.com.fiap.streamfiap.model.*;
import br.com.fiap.streamfiap.exception.*;

public class ModelChecks {
    private static int checks;

    private static void check(boolean condition, String description) {
        checks++;
        if (!condition) throw new AssertionError(description);
    }

    private static void near(double actual, double expected) {
        check(Math.abs(actual - expected) < 0.000001, "Esperado " + expected + ", recebido " + actual);
    }

    private static void invalid(Runnable action) {
        try {
            action.run();
        } catch (IllegalArgumentException expected) {
            check(expected.getMessage() != null && !expected.getMessage().isBlank(), "Mensagem de validacao");
            return;
        }
        throw new AssertionError("Operacao invalida aceita");
    }

    private static Filme filme(boolean disponivel) {
        return new Filme("Filme de verificacao", "FICCAO", 100, 14, disponivel, false);
    }

    private static void verify(String item) throws Exception {
        if (item.equals("bug03")) {
            Usuario menor = new Usuario("Menor", 12, 100);
            Filme conteudo = filme(true);
            try {
                menor.alugar(conteudo);
                throw new AssertionError("Menor conseguiu alugar");
            } catch (Exception exception) {
                check(exception instanceof ClassificacaoIndicativaException, "Tipo da excecao");
                check(exception instanceof RuntimeException, "Excecao de negocio deve ser unchecked");
                check(exception.getMessage().contains("14"), "Mensagem da classificacao");
            }
            near(menor.getCreditos(), 100);
            check(conteudo.isDisponivel(), "Falha nao altera disponibilidade");
        }
        if (item.equals("bug04")) {
            invalid(() -> new Filme("Teste", "FICCAO", 0, 0, true, false));
            invalid(() -> new Documentario("Teste", "CIENCIA", -1, 0, true, "Natureza"));
            Filme conteudo = filme(true);
            invalid(() -> conteudo.setDuracaoMinutos(-1));
            check(conteudo.getDuracaoMinutos() == 100, "Setter invalido preserva duracao");
            conteudo.setDuracaoMinutos(1);
            check(conteudo.getDuracaoMinutos() == 1, "Duracao minima valida");
        }
        if (item.equals("bug05")) {
            Conteudo documentario = new Documentario("Natureza", "CIENCIA", 50, 0, true, "Animais");
            near(documentario.calcularPrecoAluguel(), 0);
            near(documentario.calcularPrecoPromocional(), 0);
            check(!(documentario instanceof Promocionavel), "Documentario sem interface de promocao");
        }
        if (item.equals("bug06")) {
            Filme comum = filme(true);
            near(comum.calcularPrecoAluguel(), 9.9);
            near(comum.calcularPrecoPromocional(), 7.92);
            comum.setEstreia(true);
            near(comum.calcularPrecoAluguel(), 14.9);
            near(comum.calcularPrecoPromocional(), 11.92);
            near(comum.aplicarPromocao(37), 29.6);
        }
        if (item.equals("bug08")) {
            Serie serie = new Serie();
            serie.setNumeroTemporadas(5);
            Conteudo conteudo = serie;
            near(conteudo.calcularPrecoAluguel(), 24.5);
            near(conteudo.calcularPrecoPromocional(), 19.6);
            serie.setNumeroTemporadas(2);
            near(conteudo.calcularPrecoAluguel(), 9.8);
            near(conteudo.calcularPrecoPromocional(), 7.84);
        }
        if (item.equals("bug10")) {
            check("Nome preservado".equals(new Usuario("Nome preservado", 20, 100).getNome()), "Nome no construtor");
        }
        if (item.equals("bug11")) {
            Usuario usuario = new Usuario("Adulto", 20, 100);
            check(usuario.temCreditosSuficientes(9.9), "Saldo maior que preco");
            check(usuario.temCreditosSuficientes(100), "Saldo igual ao preco");
            check(!usuario.temCreditosSuficientes(101), "Saldo menor que preco");
            invalid(() -> new Usuario("Invalido", 20, -1));
            invalid(() -> usuario.setCreditos(-1));
            invalid(() -> usuario.setCreditos(Double.NaN));
            invalid(() -> usuario.debitarCreditos(-1));
            invalid(() -> usuario.debitarCreditos(Double.POSITIVE_INFINITY));
            try {
                usuario.debitarCreditos(101);
                throw new AssertionError("Debito excessivo aceito");
            } catch (CreditosInsuficientesException expected) { checks++; }
            near(usuario.getCreditos(), 100);
            usuario.debitarCreditos(100);
            near(usuario.getCreditos(), 0);
            usuario.debitarCreditos(0);
            near(usuario.getCreditos(), 0);
            Filme conteudo = filme(true);
            try {
                usuario.alugar(conteudo);
                throw new AssertionError("Aluguel sem saldo aceito");
            } catch (CreditosInsuficientesException expected) { checks++; }
            check(conteudo.isDisponivel(), "Falha preserva conteudo");
        }
        if (item.equals("bug12")) {
            Usuario usuario = new Usuario("Adulto", 20, 0);
            Filme conteudo = filme(false);
            try {
                usuario.alugar(conteudo);
                throw new AssertionError("Conteudo indisponivel alugado");
            } catch (ConteudoIndisponivelException expected) { checks++; }
            near(usuario.getCreditos(), 0);
            check(!conteudo.isDisponivel(), "Falha preserva indisponibilidade");
        }
    }

    public static void main(String[] args) throws Exception {
        for (String item : args) verify(item);
        System.out.println("MODEL OK: " + checks + " verificacoes");
    }
}
