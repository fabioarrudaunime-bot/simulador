from flask import Flask, request, session, redirect, Response
from supabase import create_client
import mimetypes
import os

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY", "troque_essa_chave_por_uma_grande")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

BUCKET = "Simulador_web"
CURSO_SIMULADOR = "Tomografia 2.0 + Simulador"


def aluno_autorizado(email):
    resp = (
        supabase.table("alunos_autorizados")
        .select("*")
        .eq("email", email.lower())
        .eq("curso", CURSO_SIMULADOR)
        .execute()
    )

    return len(resp.data) > 0


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if aluno_autorizado(email):
            session["email"] = email
            return redirect("/simulador/index.html")

        return """
        <h2>Acesso negado</h2>
        <p>Email não autorizado para Tomografia 2.0 + Simulador.</p>
        <a href="/">Voltar</a>
        """, 403

    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Expert Radiologia</title>
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #0b1220;
                color: white;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }

            .card {
                background: #111827;
                padding: 35px;
                border-radius: 16px;
                width: 360px;
                text-align: center;
                border: 1px solid #334155;
            }

            input {
                width: 100%;
                padding: 12px;
                margin-top: 10px;
                border-radius: 8px;
                border: none;
                font-size: 16px;
            }

            button {
                margin-top: 20px;
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 8px;
                background: #1f4e79;
                color: white;
                font-size: 16px;
                cursor: pointer;
            }

            button:hover {
                background: #2563eb;
            }

            p {
                color: #cbd5e1;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Expert Radiologia</h2>
            <p>Acesse o simulador de Tomografia 2.0</p>

            <form method="post">
                <input name="email" type="email" placeholder="Email usado na compra" required>
                <button type="submit">Entrar</button>
            </form>
        </div>
    </body>
    </html>
    """


@app.route("/simulador/")
def simulador_index_barra():
    return redirect("/simulador/index.html")


@app.route("/simulador/<path:arquivo>")
def servir_simulador(arquivo):
    email = session.get("email")

    if not email:
        return redirect("/")

    if not aluno_autorizado(email):
        return "Acesso negado.", 403

    caminho_storage = arquivo

    try:
        dados = supabase.storage.from_(BUCKET).download(caminho_storage)
    except Exception:
        return f"Arquivo não encontrado: {caminho_storage}", 404

    mimetype, _ = mimetypes.guess_type(arquivo)

    if not mimetype:
        mimetype = "application/octet-stream"

    return Response(dados, mimetype=mimetype)


@app.route("/sair")
def sair():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
