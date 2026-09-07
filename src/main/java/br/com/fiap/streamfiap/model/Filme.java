package br.com.fiap.streamfiap.model;

import jakarta.persistence.Entity;

@Entity
public class Filme extends Conteudo implements Promocionavel {

    private static final double ACRESCIMO_ESTREIA = 5.00;

    private boolean estreia;

    public Filme() {
    }

    public Filme(String titulo, String categoria, int duracaoMinutos, int classificacaoEtaria, boolean disponivel, boolean estreia) {
        super(titulo, categoria, duracaoMinutos, classificacaoEtaria, disponivel);
        this.estreia = estreia;
    }

    @Override
    public double calcularPrecoAluguel() {
        return PRECO_BASE_ALUGUEL + (estreia ? ACRESCIMO_ESTREIA : 0.0);
    }

    @Override
    public double aplicarPromocao(double preco) {
        return preco * (1 - DESCONTO_PROMOCIONAL);
    }

    public boolean isEstreia() { return estreia; }
    public void setEstreia(boolean estreia) { this.estreia = estreia; }
}
