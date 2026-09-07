"""Verifica o checkpoint usando apenas Java e a biblioteca padrao do Python."""
import argparse
import getpass
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
import warnings

sys.stdout.reconfigure(encoding="utf-8")
ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "pom.xml").is_file())
OUT = ROOT / "target" / "verificacao"
JAVA_HOME = Path(os.environ["JAVA_HOME"])
CLASSPATH = str(ROOT / "target" / "classes") + os.pathsep + (ROOT / "target" / "classpath.txt").read_text().strip()
MODELS = ["bug03", "bug04", "bug05", "bug06", "bug08", "bug10", "bug11", "bug12"]
parser = argparse.ArgumentParser()
parser.add_argument("items", nargs="*", default=["all"])
parser.add_argument("--label", default="verificacao")
parser.add_argument("--compile", action="store_true")
parser.add_argument("--jar", action="store_true", help="Executa a API a partir do JAR empacotado")
parser.add_argument("--oracle", action="store_true", help="Pede credenciais locais e testa no Oracle FIAP; cria dados de teste persistentes")
parser.add_argument("--oracle-env", action="store_true", help="Com --oracle, usa credenciais fornecidas no ambiente do processo")
args = parser.parse_args()
if args.oracle_env and not args.oracle:
    parser.error("--oracle-env exige --oracle")
ITEMS = [f"bug{i:02}" for i in range(1, 13)] + ["contrato"] if "all" in args.items else args.items
if any(item not in [f"bug{i:02}" for i in range(1, 13)] + ["contrato"] for item in ITEMS):
    parser.error("Item desconhecido; use all, bug01 a bug12 ou contrato")
if Path(args.label).name != args.label or args.label in (".", ".."):
    parser.error("O label deve ser somente um nome de arquivo")
OUT.mkdir(parents=True, exist_ok=True)
records = []
prefix = "CP4_" + uuid.uuid4().hex[:12] + "_" if args.oracle else ""
created_contents = set()
created_users = set()
child_env = os.environ.copy()
ddl_mode = "create-drop"
if args.oracle:
    if not args.oracle_env and not sys.stdin.isatty():
        parser.error("Execute --oracle em um terminal interativo para digitar a senha oculta")
    print("Oracle FIAP: esta execucao cria dados de teste persistentes identificados por " + prefix)
    print("Tabelas existentes serao apenas validadas; nenhum dado existente sera apagado.")
    if args.oracle_env:
        if not all(child_env.get(key, "").strip() for key in ("SPRING_DATASOURCE_USERNAME", "SPRING_DATASOURCE_PASSWORD")):
            parser.error("Credenciais ausentes no ambiente; nenhuma conexao foi tentada")
    else:
        try:
            child_env["SPRING_DATASOURCE_USERNAME"] = input("Usuario Oracle fornecido pela FIAP: ").strip()
            with warnings.catch_warnings():
                warnings.simplefilter("error", getpass.GetPassWarning)
                child_env["SPRING_DATASOURCE_PASSWORD"] = getpass.getpass("Senha Oracle (oculta): ")
        except (EOFError, KeyboardInterrupt, getpass.GetPassWarning):
            parser.error("Entrada cancelada ou terminal sem suporte a senha oculta; nenhuma conexao foi tentada")
    subprocess.run([str(JAVA_HOME / "bin" / "javac.exe"), "--release", "17", "-encoding", "UTF-8", "-d", str(OUT), str(Path(__file__).with_name("OraclePreflight.java"))], check=True)
    probe = subprocess.run([str(JAVA_HOME / "bin" / "java.exe"), "-cp", str(OUT) + os.pathsep + CLASSPATH, "OraclePreflight"], env=child_env, capture_output=True, text=True)
    if probe.returncode:
        print(probe.stderr.strip())
        sys.exit(probe.returncode)
    ddl_mode = probe.stdout.strip()
    if ddl_mode not in ("update", "validate"):
        raise RuntimeError("Resposta inesperada da inspecao Oracle; API nao iniciada")

def record(case, status, body):
    records.append({"caso": case, "status": status, "resposta": body})

if args.compile:
    source_files = list((ROOT / "src" / "main" / "java").rglob("*.java"))
    subprocess.run([str(JAVA_HOME / "bin" / "javac.exe"), "--release", "17", "-parameters", "-encoding", "UTF-8", "-cp", CLASSPATH, "-d", str(ROOT / "target" / "classes"), *map(str, source_files)], check=True)
subprocess.run([str(JAVA_HOME / "bin" / "javac.exe"), "-encoding", "UTF-8", "-cp", CLASSPATH, "-d", str(OUT), str(Path(__file__).with_name("ModelChecks.java"))], check=True)
failed = []
for item in ITEMS:
    if item in MODELS:
        result = subprocess.run([str(JAVA_HOME / "bin" / "java.exe"), "-Dfile.encoding=UTF-8", "-cp", str(OUT) + os.pathsep + CLASSPATH, "ModelChecks", item], capture_output=True, text=True, encoding="utf-8", errors="replace")
        record(item + " model", result.returncode, result.stdout + result.stderr)
        if result.returncode: failed.append(item + " model")

with socket.socket() as reserve:
    reserve.bind(("127.0.0.1", 0))
    port = reserve.getsockname()[1]
base = f"http://127.0.0.1:{port}"
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def request(method, path, body=None):
    if args.oracle:
        path = path.replace("/999999999", "/-1")
        if path.startswith("/api/conteudos/categoria/"):
            path = path.replace("/categoria/", "/categoria/" + prefix)
        if method == "POST" and body is not None:
            body = dict(body)
            for field in ("titulo", "categoria", "nome"):
                if field in body:
                    body[field] = prefix + body[field]
            if "id" in body:
                body["id"] = -123
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(base + path, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        response = opener.open(req, timeout=10)
    except urllib.error.HTTPError as error:
        response = error
    raw = response.read().decode("utf-8")
    parsed = json.loads(raw) if raw else None
    if method == "POST" and response.code == 201:
        (created_users if path == "/api/usuarios" else created_contents).add(parsed["id"])
    evidence = parsed
    if args.oracle and path == "/api/conteudos" and isinstance(parsed, list):
        evidence = {"total": len(parsed), "dados_desta_execucao": [entry for entry in parsed if entry["id"] in created_contents]}
    record(method + " " + path, response.code, evidence)
    return response.code, parsed

def expect(condition, description):
    if not condition: raise AssertionError(description)

def content(kind="filme", **values):
    data = dict(titulo="Conteudo de teste", categoria="FICCAO", duracaoMinutos=120, classificacaoEtaria=14, disponivel=True)
    if kind == "filme": data["estreia"] = False
    if kind == "serie": data["numeroTemporadas"] = 5
    if kind == "documentario": data["tema"] = "Natureza"
    data.update(values)
    status, result = request("POST", "/api/conteudos/" + kind, data)
    expect(status == 201, f"Cadastro de {kind}: {status}, {result}")
    return result

def user(**values):
    data = dict(nome="Usuario de teste", idade=20, creditos=100)
    data.update(values)
    status, result = request("POST", "/api/usuarios", data)
    expect(status == 201, f"Cadastro de usuario: {status}, {result}")
    return result

def error_response(status, body, expected_status, message):
    expect(status == expected_status, f"Esperado HTTP {expected_status}, recebido {status}")
    expect(isinstance(body, dict) and isinstance(body.get("erro"), str) and message.casefold() in body["erro"].casefold(), f"Mensagem ausente: {body}")

def rent_check(creditos=100, idade=20, disponivel=True, kind="filme", expected_status=200, price=9.9, message="", **values):
    customer = user(creditos=creditos, idade=idade)
    movie = content(kind, disponivel=disponivel, **values)
    status, body = request("POST", f'/api/alugueis?usuarioId={customer["id"]}&conteudoId={movie["id"]}')
    if expected_status == 200:
        expect(status == 200, f"Aluguel valido: {status} {body}")
        expect(abs(body["creditos"] - (creditos - price)) < 1e-6, f"Debito incorreto: {body}")
    else: error_response(status, body, expected_status, message)
    status, persisted = request("GET", f'/api/usuarios/{customer["id"]}')
    expected_balance = creditos - price if expected_status == 200 else creditos
    expect(status == 200 and abs(persisted["creditos"] - expected_balance) < 1e-6, "Saldo persistido incorreto")
    status, persisted_content = request("GET", f'/api/conteudos/{movie["id"]}')
    expect(status == 200 and persisted_content["disponivel"] == (False if expected_status == 200 else disponivel), "Disponibilidade persistida incorreta")

def api_check(item):
    if item == "bug01":
        error_response(*request("GET", "/api/conteudos/999999999"), 404, "não encontrado")
    elif item == "bug02":
        first = content(categoria="FICCAO")
        content(categoria="DRAMA")
        status, body = request("GET", "/api/conteudos/categoria/FICCAO")
        expect(status == 200 and any(entry["id"] == first["id"] for entry in body) and all(entry["categoria"] == prefix + "FICCAO" for entry in body), "Filtro de categoria incorreto")
        status, body = request("GET", "/api/conteudos/categoria/INEXISTENTE")
        expect(status == 200 and body == [], "Categoria sem resultados")
    elif item == "bug04":
        kinds = ["filme", "documentario", "serie"] if "bug07" in ITEMS else ["filme", "documentario"]
        for kind in kinds:
            for duration in [0, -1]:
                before = request("GET", "/api/conteudos")[1]
                fields = {"numeroTemporadas": 5} if kind == "serie" else ({"estreia": False} if kind == "filme" else {"tema": "Natureza"})
                status, body = request("POST", "/api/conteudos/" + kind, dict(titulo="Invalido", categoria="TESTE", duracaoMinutos=duration, classificacaoEtaria=0, disponivel=True, **fields))
                error_response(status, body, 400, "duração")
                expect(len(request("GET", "/api/conteudos")[1]) == len(before), "Cadastro invalido foi salvo")
    elif item in ["bug05", "bug06", "bug08"]:
        cases = {"bug05": [("documentario", {}, 0)], "bug06": [("filme", {"estreia": False}, 7.92), ("filme", {"estreia": True}, 11.92)], "bug08": [("serie", {"numeroTemporadas": 5}, 19.6), ("serie", {"numeroTemporadas": 2}, 7.84)]}
        for kind, fields, expected_price in cases[item]:
            entry = content(kind, **fields)
            status, body = request("GET", f'/api/conteudos/{entry["id"]}/preco-promocional')
            expect(status == 200 and abs(body - expected_price) < 1e-6, f"Promocao: {body}, esperado {expected_price}")
    elif item == "bug07":
        for available in [True, False]:
            entry = content("serie", disponivel=available, titulo="Serie preservada", categoria="AVENTURA")
            status, persisted = request("GET", f'/api/conteudos/{entry["id"]}')
            for key, value in dict(titulo="Serie preservada", categoria="AVENTURA", duracaoMinutos=120, classificacaoEtaria=14, disponivel=available, numeroTemporadas=5).items():
                if key in ("titulo", "categoria"):
                    value = prefix + value
                expect(entry[key] == value and persisted[key] == value, "Serie perdeu " + key)
    elif item == "bug09":
        entry = user(id=999999)
        expect(isinstance(entry.get("id"), int) and entry["id"] > 0 and entry["id"] != (-123 if args.oracle else 999999), "ID nao gerado")
        expect(user()["id"] != entry["id"], "ID repetido")
        expect(request("GET", f'/api/usuarios/{entry["id"]}')[0] == 200, "Usuario nao persistido")
    elif item == "bug10":
        entry = user(nome="Nome persistido")
        status, persisted = request("GET", f'/api/usuarios/{entry["id"]}')
        expect(entry["nome"] == prefix + "Nome persistido" and persisted["nome"] == prefix + "Nome persistido", "Nome perdido")
    elif item == "bug11":
        error_response(*request("POST", "/api/usuarios", dict(nome="Saldo invalido", idade=20, creditos=-1)), 400, "créditos")
        rent_check(creditos=0, expected_status=422, message="Créditos insuficientes")
        rent_check(creditos=9.89, expected_status=422, message="Créditos insuficientes")
        rent_check(creditos=9.9)
        rent_check(creditos=100, estreia=True, price=14.9)
        rent_check(creditos=100, kind="serie", price=24.5)
        rent_check(creditos=100, kind="serie", numeroTemporadas=2, price=9.8)
        rent_check(creditos=0, kind="documentario", price=0)
        rent_check(idade=14)
    elif item == "bug12":
        rent_check(disponivel=False, expected_status=409, message="disponível")
        rent_check(disponivel=False, kind="documentario", price=0, expected_status=409, message="disponível")
    elif item == "bug03":
        if "bug09" not in ITEMS:
            record("bug03 API", "pendente", "Cadastro de usuario bloqueado pelo bug09; model verificado separadamente")
        else: rent_check(idade=12, expected_status=422, message="classificação")
    elif item == "contrato":
        error_response(*request("GET", "/api/conteudos/999999999/preco-promocional"), 404, "não encontrado")
        for kind in ["filme", "serie", "documentario"]:
            entry = content(kind, id=888888)
            expect(entry["id"] != (-123 if args.oracle else 888888), "Cadastro de conteudo aceitou ID externo")
        before = len(request("GET", "/api/conteudos")[1])
        for duration in [None, "invalida"]:
            status, body = request("POST", "/api/conteudos/filme", dict(titulo="Dados invalidos", categoria="TESTE", duracaoMinutos=duration, classificacaoEtaria=0, disponivel=True, estreia=False))
            error_response(status, body, 400, "")
        expect(len(request("GET", "/api/conteudos")[1]) == before, "Corpo invalido persistido")
        customer = user()
        movie = content()
        path = f'/api/alugueis?usuarioId={customer["id"]}&conteudoId={movie["id"]}'
        expect(request("POST", path)[0] == 200, "Primeiro aluguel valido")
        error_response(*request("POST", path), 409, "disponível")
        expect(abs(request("GET", f'/api/usuarios/{customer["id"]}')[1]["creditos"] - 90.1) < 1e-6, "Segundo aluguel debitou novamente")

def await_start(process, log):
    deadline = time.monotonic() + (120 if args.oracle else 45)
    while True:
        try:
            status, body = request("GET", "/api/conteudos")
            if status == 200 and isinstance(body, list):
                return body
        except (OSError, urllib.error.URLError):
            pass
        if process.poll() is not None or time.monotonic() > deadline:
            raise RuntimeError("API nao iniciou; consulte " + str(log.name))
        time.sleep(0.25)

def stop(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

with (OUT / (args.label + ".log")).open("w", encoding="utf-8") as log:
    app = ["-jar", str(ROOT / "target" / "streamfiap-0.0.1-SNAPSHOT.jar")] if args.jar else ["-cp", CLASSPATH, "br.com.fiap.streamfiap.StreamFiapApplication"]
    database = ["--spring.datasource.url=jdbc:oracle:thin:@oracle.fiap.com.br:1521:ORCL", "--spring.datasource.driverClassName=oracle.jdbc.OracleDriver", "--spring.jpa.show-sql=false", "--spring.jpa.properties.hibernate.hbm2ddl.halt_on_error=true"] if args.oracle else ["--spring.datasource.url=jdbc:h2:mem:checkpoint_verificacao", "--spring.datasource.driverClassName=org.h2.Driver", "--spring.datasource.username=sa", "--spring.datasource.password="]
    command = [str(JAVA_HOME / "bin" / "java.exe"), "-Dfile.encoding=UTF-8", *app, f"--server.port={port}", "--server.address=127.0.0.1", *database, "--spring.jpa.hibernate.ddl-auto=" + ddl_mode]
    process = subprocess.Popen(command, env=child_env, stdout=log, stderr=subprocess.STDOUT)
    try:
        initial_contents = await_start(process, log)
        for item in ITEMS:
            if item == "bug03" and "bug09" not in ITEMS:
                record("bug03 API resultado", "PENDENTE", "Depende da correcao do cadastro de usuario (bug09); model verificado")
                continue
            try:
                api_check(item)
                record(item + " API resultado", "OK", "Cenario verificado")
            except Exception as error:
                failed.append(item + " API")
                record(item + " API resultado", "FALHA", str(error))
        if args.oracle:
            saved_contents = request("GET", "/api/conteudos")[1]
            saved_users = {identifier: request("GET", f"/api/usuarios/{identifier}")[1] for identifier in created_users}
            stop(process)
            # A segunda inicializacao nunca altera a estrutura, inclusive em schema inicialmente vazio.
            command[-1] = "--spring.jpa.hibernate.ddl-auto=validate"
            process = subprocess.Popen(command, env=child_env, stdout=log, stderr=subprocess.STDOUT)
            restored = await_start(process, log)
            expect(sorted(restored, key=lambda row: row["id"]) == sorted(saved_contents, key=lambda row: row["id"]), "Conteudos alterados apos reiniciar Oracle")
            expect({row["id"]: row for row in restored if row["id"] not in created_contents} == {row["id"]: row for row in initial_contents}, "Dados anteriores a verificacao foram alterados")
            for identifier, saved_user in saved_users.items():
                expect(request("GET", f"/api/usuarios/{identifier}")[1] == saved_user, "Usuario alterado apos reiniciar Oracle")
            record("Oracle persistencia resultado", "OK", {"reinicio": True, "prefixo": prefix, "conteudos_criados": sorted(created_contents), "usuarios_criados": sorted(created_users)})
    except Exception as error:
        failed.append("execucao")
        record("execucao resultado", "FALHA", str(error))
    finally:
        stop(process)
        child_env.pop("SPRING_DATASOURCE_PASSWORD", None)
(OUT / (args.label + ".json")).write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
for row in records:
    if "model" in row["caso"] or "resultado" in row["caso"]: print(json.dumps(row, ensure_ascii=False))
print(f"Registros: {len(records)}; falhas: {len(failed)}; evidencia: target/verificacao/{args.label}.json")
sys.exit(1 if failed else 0)
