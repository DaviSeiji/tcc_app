from werkzeug.security import generate_password_hash, check_password_hash
from utils.db import supabase

class Usuario:
    def __init__(self, id=None, nome=None, email=None, senha=None):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha

    # ----------------------------
    # SALVAR NOVO USUÁRIO
    # ----------------------------
    def salvar(self):
        try:
            response = supabase.table("usuarios").insert({
                "nome": self.nome,
                "email": self.email,
                "senha": self.senha
            }).execute()

            if response.data:
                self.id = response.data[0]["id"]
                return self.id
        except Exception as e:
            print(f"❌ Erro ao salvar usuário: {e}")
            return None

    # ----------------------------
    # BUSCAR POR EMAIL
    # ----------------------------
    @staticmethod
    def buscar_por_email(email):
        try:
            response = supabase.table("usuarios").select("*").eq("email", email).execute()
            data = response.data
            if data and len(data) > 0:
                row = data[0]
                return Usuario(row["id"], row["nome"], row["email"], row["senha"])
        except Exception as e:
            print(f"❌ Erro ao buscar usuário por email: {e}")
        return None

    # ----------------------------
    # HASH E VERIFICAÇÃO DE SENHA
    # ----------------------------
    def set_password(self, senha):
        self.senha = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha, senha)

    @staticmethod
    def autenticar(email, senha):
        usuario = Usuario.buscar_por_email(email)
        if usuario and check_password_hash(usuario.senha, senha):
            return usuario
        return None
