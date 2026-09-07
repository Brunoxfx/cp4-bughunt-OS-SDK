import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/** Inspecao somente de leitura antes de executar a API no Oracle do grupo. */
public class OraclePreflight {
    public static void main(String[] args) {
        String usuario = System.getenv("SPRING_DATASOURCE_USERNAME");
        String senha = System.getenv("SPRING_DATASOURCE_PASSWORD");
        if (usuario == null || usuario.isBlank() || senha == null || senha.isBlank()) {
            System.err.println("Credenciais locais ausentes; nenhuma conexao foi tentada.");
            System.exit(2);
        }
        DriverManager.setLoginTimeout(15);
        try (Connection conexao = DriverManager.getConnection(
                "jdbc:oracle:thin:@oracle.fiap.com.br:1521:ORCL", usuario, senha)) {
            if (conexao.getMetaData().getDatabaseMajorVersion() < 12) {
                throw new IllegalStateException("Oracle anterior a 12c: revisar suporte a IDENTITY.");
            }
            int tabelas = 0;
            try (PreparedStatement consulta = conexao.prepareStatement(
                    "SELECT COUNT(*) FROM user_tables WHERE table_name IN (?, ?)")) {
                consulta.setString(1, "CONTEUDOS");
                consulta.setString(2, "USUARIOS");
                try (ResultSet resultado = consulta.executeQuery()) {
                    resultado.next();
                    tabelas = resultado.getInt(1);
                }
            }
            if (tabelas == 0) {
                System.out.println("update");
            } else if (tabelas == 2) {
                try (PreparedStatement consulta = conexao.prepareStatement(
                        "SELECT COUNT(*) FROM user_tab_identity_cols "
                        + "WHERE table_name IN (?, ?) AND column_name = ?")) {
                    consulta.setString(1, "CONTEUDOS");
                    consulta.setString(2, "USUARIOS");
                    consulta.setString(3, "ID");
                    try (ResultSet resultado = consulta.executeQuery()) {
                        resultado.next();
                        if (resultado.getInt(1) != 2) {
                            throw new IllegalStateException("Tabelas existentes sem os dois IDs IDENTITY; revisar o schema antes de iniciar.");
                        }
                    }
                }
                System.out.println("validate");
            } else {
                throw new IllegalStateException("Schema parcial: somente uma das tabelas existe; revisar antes de iniciar.");
            }
        } catch (SQLException erro) {
            // Codigo suficiente para diagnosticar sem expor usuario, senha ou detalhes do schema.
            System.err.println("Falha na verificacao Oracle. Codigo ORA: " + erro.getErrorCode());
            System.exit(1);
        } catch (IllegalStateException erro) {
            System.err.println(erro.getMessage());
            System.exit(1);
        }
    }
}
