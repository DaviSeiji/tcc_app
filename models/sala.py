from utils.db import supabase

class Sala:
    def __init__(self, usuario_id, nome, horario_seg=None, horario_sab=None, horario_dom=None, id=None):
        self.id = id
        self.usuario_id = usuario_id
        self.nome = nome
        self.horario_seg = horario_seg
        self.horario_sab = horario_sab
        self.horario_dom = horario_dom

    def salvar(self):
        data = {
            "usuario_id": self.usuario_id,
            "nome": self.nome,
            "horario_seg": self.horario_seg,
            "horario_sab": self.horario_sab,
            "horario_dom": self.horario_dom
        }

        if self.id is None:
            response = supabase.table("salas").insert(data).execute()
            if response.error:
                raise Exception(f"Erro ao salvar sala: {response.error.message}")
            self.id = response.data[0]["id"]
        else:
            response = supabase.table("salas").update(data).eq("id", self.id).execute()
            if response.error:
                raise Exception(f"Erro ao atualizar sala: {response.error.message}")

    def excluir(self):
        if self.id is None:
            return
        response = supabase.table("salas").delete().eq("id", self.id).execute()
        if response.error:
            raise Exception(f"Erro ao excluir sala: {response.error.message}")

    @staticmethod
    def listar_por_usuario(usuario_id):
        response = supabase.table("salas").select("*").eq("usuario_id", usuario_id).execute()
        if response.error:
            raise Exception(f"Erro ao listar salas: {response.error.message}")
        return [Sala(
                    usuario_id=row["usuario_id"],
                    nome=row["nome"],
                    horario_seg=row.get("horario_seg"),
                    horario_sab=row.get("horario_sab"),
                    horario_dom=row.get("horario_dom"),
                    id=row["id"]
                ) for row in response.data]

    @staticmethod
    def buscar_por_id(sala_id):
        response = supabase.table("salas").select("*").eq("id", sala_id).single().execute()
        if response.error:
            return None
        row = response.data
        if row:
            return Sala(
                usuario_id=row["usuario_id"],
                nome=row["nome"],
                horario_seg=row.get("horario_seg"),
                horario_sab=row.get("horario_sab"),
                horario_dom=row.get("horario_dom"),
                id=row["id"]
            )
        return None
