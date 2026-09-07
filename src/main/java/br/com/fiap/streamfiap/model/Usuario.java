package br.com.fiap.streamfiap.model;

import br.com.fiap.streamfiap.exception.ClassificacaoIndicativaException;
import br.com.fiap.streamfiap.exception.ConteudoIndisponivelException;
import br.com.fiap.streamfiap.exception.CreditosInsuficientesException;
import jakarta.persistence.*;

@Entity
@Table(name = "usuarios")
public class Usuario {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String nome;
    private int idade;
    private double creditos;

    public Usuario() {
    }

    public Usuario(String nome, int idade, double creditos) {
        this.nome = nome;
        this.idade = idade;
        setCreditos(creditos);
    }

    public boolean temCreditosSuficientes(double preco) {
        return Double.isFinite(preco) && preco >= 0 && this.creditos >= preco;
    }

    public void debitarCreditos(double valor) {
        if (!Double.isFinite(valor) || valor < 0) {
            throw new IllegalArgumentException("O valor do débito deve ser finito e não negativo");
        }
        if (!temCreditosSuficientes(valor)) {
            throw new CreditosInsuficientesException("Créditos insuficientes para debitar " + valor);
        }
        // adiciona o valor aos créditos do usuário
        setCreditos(this.creditos - valor);
    }

    public Usuario alugar(Conteudo conteudo) {
        if (!conteudo.isDisponivel()) {
            throw new ConteudoIndisponivelException(conteudo.getTitulo() + " não está disponível para aluguel");
        }
        if (this.idade < conteudo.getClassificacaoEtaria()) {
            throw new ClassificacaoIndicativaException("Usuário de " + this.idade
                    + " anos não pode assistir a " + conteudo.getTitulo()
                    + " (classificação " + conteudo.getClassificacaoEtaria() + " anos)");
        }

        double precoAluguel = conteudo.calcularPrecoAluguel();

        if (!temCreditosSuficientes(precoAluguel)) {
            throw new CreditosInsuficientesException("Créditos insuficientes para alugar " + conteudo.getTitulo());
        }

        debitarCreditos(precoAluguel);
        conteudo.setDisponivel(false);

        return this;
    }

    // Getters e Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getNome() { return nome; }
    public void setNome(String nome) { this.nome = nome; }

    public int getIdade() { return idade; }
    public void setIdade(int idade) { this.idade = idade; }

    public double getCreditos() { return creditos; }
    public void setCreditos(double creditos) {
        if (!Double.isFinite(creditos) || creditos < 0) {
            throw new IllegalArgumentException("Os créditos devem ser finitos e não negativos");
        }
        this.creditos = creditos;
    }
}
