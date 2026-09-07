package br.com.fiap.streamfiap.apresentacao;

import br.com.fiap.streamfiap.model.Conteudo;
import br.com.fiap.streamfiap.model.Usuario;

public class ReciboAluguel {

    public void imprimir(Usuario usuario, Conteudo conteudo, double valorPago) {
        System.out.println("==================================================");
        System.out.println("RECIBO STREAMFIAP");
        System.out.println("Usuario: " + usuario.getNome());
        System.out.println("Conteudo: " + conteudo.getTitulo());
        System.out.println("Valor pago: R$ " + valorPago);
        System.out.println("Creditos restantes: R$ " + usuario.getCreditos());
        System.out.println("Obrigado por usar o StreamFIAP!");
        System.out.println("==================================================");
    }
}
