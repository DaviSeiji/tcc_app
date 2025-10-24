from utils.db import supabase

# ----------------------------
# Classe Cirurgia
# ----------------------------
class Cirurgia:
    def __init__(self, usuario_id, tipo, plano, duracao_prevista=None, duracao_real=None, status='pendente', id=None):
        self.id = id
        self.usuario_id = usuario_id
        self.tipo = tipo
        self.plano = plano
        self.duracao_prevista = duracao_prevista
        self.duracao_real = duracao_real
        self.status = status

    def salvar(self):
        if self.id is None:
            # Inserir nova cirurgia
            data = {
                "usuario_id": self.usuario_id,
                "tipo": self.tipo,
                "plano": self.plano,
                "duracao_prevista": self.duracao_prevista,
                "duracao_real": self.duracao_real,
                "status": self.status
            }
            res = supabase.table("cirurgias").insert(data).execute()
            if res.data and len(res.data) > 0:
                self.id = res.data[0]["id"]
        else:
            # Atualizar existente
            data = {
                "tipo": self.tipo,
                "plano": self.plano,
                "duracao_prevista": self.duracao_prevista,
                "duracao_real": self.duracao_real,
                "status": self.status
            }
            supabase.table("cirurgias").update(data).eq("id", self.id).execute()
        return self.id

    def excluir(self):
        # Excluir características
        supabase.table("cirurgia_caracteristicas").delete().eq("cirurgia_id", self.id).execute()
        # Excluir cirurgia
        supabase.table("cirurgias").delete().eq("id", self.id).execute()

    @staticmethod
    def listar_por_usuario(usuario_id):
        res = supabase.table("cirurgias").select("*").eq("usuario_id", usuario_id).execute()
        cirurgias = []
        if res.data:
            for row in res.data:
                cirurgias.append(Cirurgia(
                    usuario_id=row["usuario_id"],
                    tipo=row["tipo"],
                    plano=row["plano"],
                    duracao_prevista=row.get("duracao_prevista"),
                    duracao_real=row.get("duracao_real"),
                    status=row.get("status", "pendente"),
                    id=row["id"]
                ))
        return cirurgias

    @staticmethod
    def buscar_por_id(cirurgia_id):
        res = supabase.table("cirurgias").select("*").eq("id", cirurgia_id).execute()
        if res.data and len(res.data) > 0:
            row = res.data[0]
            return Cirurgia(
                usuario_id=row["usuario_id"],
                tipo=row["tipo"],
                plano=row["plano"],
                duracao_prevista=row.get("duracao_prevista"),
                duracao_real=row.get("duracao_real"),
                status=row.get("status", "pendente"),
                id=row["id"]
            )
        return None


# ----------------------------
# Classe CirurgiaCaracteristicas
# ----------------------------
class CirurgiaCaracteristicas:
    def __init__(self, cirurgia_id, opdur=None, sex=None, bmi=None, asa=None, emop=None, department=None,
                 optype=None, approach=None, position=None, ane_type=None, preop_htn=None, preop_dm=None,
                 preop_pft=None, preop_hb=None, preop_plt=None, preop_pt=None, preop_aptt=None,
                 preop_na=None, preop_k=None, preop_glucose=None, preop_alb=None, preop_got=None,
                 preop_gpt=None, preop_bun=None, preop_cr=None, faixa_etaria=None, id=None):
        self.id = id
        self.cirurgia_id = cirurgia_id
        self.opdur = opdur
        self.sex = sex
        self.bmi = bmi
        self.asa = asa
        self.emop = emop
        self.department = department
        self.optype = optype
        self.approach = approach
        self.position = position
        self.ane_type = ane_type
        self.preop_htn = preop_htn
        self.preop_dm = preop_dm
        self.preop_pft = preop_pft
        self.preop_hb = preop_hb
        self.preop_plt = preop_plt
        self.preop_pt = preop_pt
        self.preop_aptt = preop_aptt
        self.preop_na = preop_na
        self.preop_k = preop_k
        self.preop_glucose = preop_glucose
        self.preop_alb = preop_alb
        self.preop_got = preop_got
        self.preop_gpt = preop_gpt
        self.preop_bun = preop_bun
        self.preop_cr = preop_cr
        self.faixa_etaria = faixa_etaria

    def salvar(self):
        data = {
            "cirurgia_id": self.cirurgia_id,
            "opdur": self.opdur,
            "sex": self.sex,
            "bmi": self.bmi,
            "asa": self.asa,
            "emop": self.emop,
            "department": self.department,
            "optype": self.optype,
            "approach": self.approach,
            "position": self.position,
            "ane_type": self.ane_type,
            "preop_htn": self.preop_htn,
            "preop_dm": self.preop_dm,
            "preop_pft": self.preop_pft,
            "preop_hb": self.preop_hb,
            "preop_plt": self.preop_plt,
            "preop_pt": self.preop_pt,
            "preop_aptt": self.preop_aptt,
            "preop_na": self.preop_na,
            "preop_k": self.preop_k,
            "preop_glucose": self.preop_glucose,
            "preop_alb": self.preop_alb,
            "preop_got": self.preop_got,
            "preop_gpt": self.preop_gpt,
            "preop_bun": self.preop_bun,
            "preop_cr": self.preop_cr,
            "faixa_etaria": self.faixa_etaria
        }

        if self.id is None:
            res = supabase.table("cirurgia_caracteristicas").insert(data).execute()
            if res.data and len(res.data) > 0:
                self.id = res.data[0]["id"]
        else:
            supabase.table("cirurgia_caracteristicas").update(data).eq("id", self.id).execute()

    def deletar(self):
        if self.id:
            supabase.table("cirurgia_caracteristicas").delete().eq("id", self.id).execute()

    @staticmethod
    def listar_por_cirurgia(cirurgia_id):
        res = supabase.table("cirurgia_caracteristicas").select("*").eq("cirurgia_id", cirurgia_id).execute()
        caracs = []
        if res.data:
            for row in res.data:
                caracs.append(CirurgiaCaracteristicas(
                    cirurgia_id=row["cirurgia_id"],
                    opdur=row.get("opdur"),
                    sex=row.get("sex"),
                    bmi=row.get("bmi"),
                    asa=row.get("asa"),
                    emop=row.get("emop"),
                    department=row.get("department"),
                    optype=row.get("optype"),
                    approach=row.get("approach"),
                    position=row.get("position"),
                    ane_type=row.get("ane_type"),
                    preop_htn=row.get("preop_htn"),
                    preop_dm=row.get("preop_dm"),
                    preop_pft=row.get("preop_pft"),
                    preop_hb=row.get("preop_hb"),
                    preop_plt=row.get("preop_plt"),
                    preop_pt=row.get("preop_pt"),
                    preop_aptt=row.get("preop_aptt"),
                    preop_na=row.get("preop_na"),
                    preop_k=row.get("preop_k"),
                    preop_glucose=row.get("preop_glucose"),
                    preop_alb=row.get("preop_alb"),
                    preop_got=row.get("preop_got"),
                    preop_gpt=row.get("preop_gpt"),
                    preop_bun=row.get("preop_bun"),
                    preop_cr=row.get("preop_cr"),
                    faixa_etaria=row.get("faixa_etaria"),
                    id=row["id"]
                ))
        return caracs
