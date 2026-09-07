package br.com.fiap.streamfiap.model;

import jakarta.persistence.Entity;

@Entity
public class Serie extends Conteudo implements Promocionavel {

    private static final double PRECO_POR_TEMPORADA = 4.90;

    private int numeroTemporadas;

    public Serie() {
    }

    // cria a série com os dados recebidos
    public Serie(String titulo, String categoria, int duracaoMinutos, int classificacaoEtaria, boolean disponivel, int numeroTemporadas) {
        super(titulo, categoria, duracaoMinutos, classificacaoEtaria, disponivel);
        this.numeroTemporadas = numeroTemporadas;
    }

    // preço da série: 4.90 por temporada
    @Override
    public double calcularPrecoAluguel() {
        return PRECO_POR_TEMPORADA * numeroTemporadas;
    }

    @Override
    public double aplicarPromocao(double preco) {
        return preco * (1 - DESCONTO_PROMOCIONAL);
    }

    public int getNumeroTemporadas() { return numeroTemporadas; }
    public void setNumeroTemporadas(int numeroTemporadas) { this.numeroTemporadas = numeroTemporadas; }
}
