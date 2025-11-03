from utils.db import supabase

# ----------------------------
# Classe Agenda
# ----------------------------
class Agenda:
    def __init__(self, cirurgia_id, sala_id, dia, hora, id=None):
        self.id = id
        self.cirurgia_id = cirurgia_id
        self.sala_id = sala_id
        self.dia = dia       # formato DATE (YYYY-MM-DD)
        self.hora = hora     # formato TIME (HH:MM:SS)

    def salvar(self):
        data = {
            "cirurgia_id": self.cirurgia_id,
            "sala_id": self.sala_id,
            "dia": self.dia,
            "hora": self.hora
        }

        if self.id is None:
            # Inserir novo agendamento
            res = supabase.table("agenda").insert(data).execute()
            if res.data and len(res.data) > 0:
                self.id = res.data[0]["id"]
        else:
            # Atualizar agendamento existente
            supabase.table("agenda").update(data).eq("id", self.id).execute()
        return self.id

    def excluir(self):
        if self.id is None:
            return
        supabase.table("agenda").delete().eq("id", self.id).execute()

    # ----------------------------
    # Métodos estáticos
    # ----------------------------
    @staticmethod
    def listar_todos():
        """Lista todos os agendamentos"""
        res = supabase.table("agenda").select("*").execute()
        agendas = []
        if res.data:
            for row in res.data:
                agendas.append(Agenda(
                    cirurgia_id=row["cirurgia_id"],
                    sala_id=row["sala_id"],
                    dia=row["dia"],
                    hora=row["hora"],
                    id=row["id"]
                ))
        return agendas

    @staticmethod
    def listar_por_sala(sala_id):
        """Lista todos os agendamentos de uma sala"""
        res = supabase.table("agenda").select("*").eq("sala_id", sala_id).execute()
        agendas = []
        if res.data:
            for row in res.data:
                agendas.append(Agenda(
                    cirurgia_id=row["cirurgia_id"],
                    sala_id=row["sala_id"],
                    dia=row["dia"],
                    hora=row["hora"],
                    id=row["id"]
                ))
        return agendas

    @staticmethod
    def listar_por_cirurgia(cirurgia_id):
        """Lista o agendamento de uma cirurgia específica"""
        res = supabase.table("agenda").select("*").eq("cirurgia_id", cirurgia_id).execute()
        agendas = []
        if res.data:
            for row in res.data:
                agendas.append(Agenda(
                    cirurgia_id=row["cirurgia_id"],
                    sala_id=row["sala_id"],
                    dia=row["dia"],
                    hora=row["hora"],
                    id=row["id"]
                ))
        return agendas

    @staticmethod
    def buscar_por_id(agenda_id):
        """Busca um agendamento específico"""
        res = supabase.table("agenda").select("*").eq("id", agenda_id).single().execute()
        if res.data:
            row = res.data
            return Agenda(
                cirurgia_id=row["cirurgia_id"],
                sala_id=row["sala_id"],
                dia=row["dia"],
                hora=row["hora"],
                id=row["id"]
            )
        return None

    @staticmethod
    def listar_por_usuario(usuario_id):
        """
        Lista todos os agendamentos associados às salas de um determinado usuário.
        Faz join lógico via a tabela 'salas'.
        """
        # Primeiro, buscar todas as salas do usuário
        res_salas = supabase.table("salas").select("id").eq("usuario_id", usuario_id).execute()
        if not res_salas.data:
            return []

        sala_ids = [s["id"] for s in res_salas.data]

        # Buscar agendamentos dessas salas
        res = supabase.table("agenda").select("*").in_("sala_id", sala_ids).execute()
        agendas = []
        if res.data:
            for row in res.data:
                agendas.append(Agenda(
                    cirurgia_id=row["cirurgia_id"],
                    sala_id=row["sala_id"],
                    dia=row["dia"],
                    hora=row["hora"],
                    id=row["id"]
                ))
        return agendas
