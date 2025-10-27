from utils.db import supabase

# ----------------------------
# Classe Sala
# ----------------------------
class Sala:
    def __init__(self, usuario_id, nome,
                 horario_seg_inicio, horario_seg_fim,
                 horario_sab_inicio, horario_sab_fim,
                 horario_dom_inicio, horario_dom_fim,
                 id=None):
        self.id = id
        self.usuario_id = usuario_id
        self.nome = nome
        self.horario_seg_inicio = horario_seg_inicio
        self.horario_seg_fim = horario_seg_fim
        self.horario_sab_inicio = horario_sab_inicio
        self.horario_sab_fim = horario_sab_fim
        self.horario_dom_inicio = horario_dom_inicio
        self.horario_dom_fim = horario_dom_fim

    def salvar(self):
        data = {
            "usuario_id": self.usuario_id,
            "nome": self.nome,
            "horario_seg_inicio": self.horario_seg_inicio,
            "horario_seg_fim": self.horario_seg_fim,
            "horario_sab_inicio": self.horario_sab_inicio,
            "horario_sab_fim": self.horario_sab_fim,
            "horario_dom_inicio": self.horario_dom_inicio,
            "horario_dom_fim": self.horario_dom_fim
        }

        if self.id is None:
            # Inserir nova sala
            res = supabase.table("salas").insert(data).execute()
            if res.data and len(res.data) > 0:
                self.id = res.data[0]["id"]
        else:
            # Atualizar sala existente
            supabase.table("salas").update(data).eq("id", self.id).execute()
        return self.id

    def excluir(self):
        if self.id is None:
            return
        supabase.table("salas").delete().eq("id", self.id).execute()

    @staticmethod
    def listar_por_usuario(usuario_id):
        res = supabase.table("salas").select("*").eq("usuario_id", usuario_id).execute()
        salas = []
        if res.data:
            for row in res.data:
                salas.append(Sala(
                    usuario_id=row["usuario_id"],
                    nome=row["nome"],
                    horario_seg_inicio=row["horario_seg_inicio"],
                    horario_seg_fim=row["horario_seg_fim"],
                    horario_sab_inicio=row["horario_sab_inicio"],
                    horario_sab_fim=row["horario_sab_fim"],
                    horario_dom_inicio=row["horario_dom_inicio"],
                    horario_dom_fim=row["horario_dom_fim"],
                    id=row["id"]
                ))
        return salas

    @staticmethod
    def buscar_por_id(sala_id):
        res = supabase.table("salas").select("*").eq("id", sala_id).single().execute()
        if res.data:
            row = res.data
            return Sala(
                usuario_id=row["usuario_id"],
                nome=row["nome"],
                horario_seg_inicio=row["horario_seg_inicio"],
                horario_seg_fim=row["horario_seg_fim"],
                horario_sab_inicio=row["horario_sab_inicio"],
                horario_sab_fim=row["horario_sab_fim"],
                horario_dom_inicio=row["horario_dom_inicio"],
                horario_dom_fim=row["horario_dom_fim"],
                id=row["id"]
            )
        return None
