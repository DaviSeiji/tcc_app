import sqlite3
from pathlib import Path
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../database/banco_cirurgias.db')


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
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if self.id is None:
            cursor.execute("""
                INSERT INTO cirurgias (usuario_id, tipo, plano, duracao_prevista, duracao_real, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.usuario_id, self.tipo, self.plano, self.duracao_prevista, self.duracao_real, self.status))
            self.id = cursor.lastrowid 
        else:
            cursor.execute("""
                UPDATE cirurgias
                SET tipo=?, plano=?, duracao_prevista=?, duracao_real=?, status=?
                WHERE id=?
            """, (self.tipo, self.plano, self.duracao_prevista, self.duracao_real, self.status, self.id))
        conn.commit()
        conn.close()
        return self.id 


    def excluir(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Excluir características antes
        cursor.execute("DELETE FROM cirurgia_caracteristicas WHERE cirurgia_id=?", (self.id,))
        # Excluir a cirurgia
        cursor.execute("DELETE FROM cirurgias WHERE id=?", (self.id,))
        conn.commit()
        conn.close()

    @staticmethod
    def listar_por_usuario(usuario_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, tipo, plano, duracao_prevista, duracao_real, status FROM cirurgias WHERE usuario_id=?", (usuario_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Cirurgia(usuario_id, tipo, plano, duracao_prevista, duracao_real, status, id=row[0])
                for row in rows for tipo, plano, duracao_prevista, duracao_real, status in [row[1:]]]

    @staticmethod
    def buscar_por_id(cirurgia_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT usuario_id, tipo, plano, duracao_prevista, duracao_real, status FROM cirurgias WHERE id=?", (cirurgia_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Cirurgia(row[0], row[1], row[2], row[3], row[4], row[5], id=cirurgia_id)
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

    @staticmethod
    def conectar():
        return sqlite3.connect(DB_PATH)

    def salvar(self):
        conn = self.conectar()
        cursor = conn.cursor()
        if self.id is None:
            cursor.execute("""
                INSERT INTO cirurgia_caracteristicas (
                    cirurgia_id, opdur, sex, bmi, asa, emop, department, optype, approach, position, ane_type,
                    preop_htn, preop_dm, preop_pft, preop_hb, preop_plt, preop_pt, preop_aptt, preop_na,
                    preop_k, preop_glucose, preop_alb, preop_got, preop_gpt, preop_bun, preop_cr, faixa_etaria
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                self.cirurgia_id, self.opdur, self.sex, self.bmi, self.asa, self.emop, self.department,
                self.optype, self.approach, self.position, self.ane_type, self.preop_htn, self.preop_dm,
                self.preop_pft, self.preop_hb, self.preop_plt, self.preop_pt, self.preop_aptt, self.preop_na,
                self.preop_k, self.preop_glucose, self.preop_alb, self.preop_got, self.preop_gpt,
                self.preop_bun, self.preop_cr, self.faixa_etaria
            ))
            self.id = cursor.lastrowid
        else:
            cursor.execute("""
                UPDATE cirurgia_caracteristicas SET
                    opdur=?, sex=?, bmi=?, asa=?, emop=?, department=?, optype=?, approach=?, position=?, ane_type=?,
                    preop_htn=?, preop_dm=?, preop_pft=?, preop_hb=?, preop_plt=?, preop_pt=?, preop_aptt=?, preop_na=?,
                    preop_k=?, preop_glucose=?, preop_alb=?, preop_got=?, preop_gpt=?, preop_bun=?, preop_cr=?, faixa_etaria=?
                WHERE id=?
            """, (
                self.opdur, self.sex, self.bmi, self.asa, self.emop, self.department,
                self.optype, self.approach, self.position, self.ane_type, self.preop_htn, self.preop_dm,
                self.preop_pft, self.preop_hb, self.preop_plt, self.preop_pt, self.preop_aptt, self.preop_na,
                self.preop_k, self.preop_glucose, self.preop_alb, self.preop_got, self.preop_gpt,
                self.preop_bun, self.preop_cr, self.faixa_etaria, self.id
            ))
        conn.commit()
        conn.close()

    def deletar(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cirurgia_caracteristicas WHERE id=?", (self.id,))
        conn.commit()
        conn.close()

    @staticmethod
    def listar_por_cirurgia(cirurgia_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cirurgia_caracteristicas WHERE cirurgia_id=?", (cirurgia_id,))
        rows = cursor.fetchall()
        conn.close()
        return [CirurgiaCaracteristicas(
                    cirurgia_id=row[1], opdur=row[2], sex=row[3], bmi=row[4], asa=row[5], emop=row[6],
                    department=row[7], optype=row[8], approach=row[9], position=row[10], ane_type=row[11],
                    preop_htn=row[12], preop_dm=row[13], preop_pft=row[14], preop_hb=row[15], preop_plt=row[16],
                    preop_pt=row[17], preop_aptt=row[18], preop_na=row[19], preop_k=row[20], preop_glucose=row[21],
                    preop_alb=row[22], preop_got=row[23], preop_gpt=row[24], preop_bun=row[25], preop_cr=row[26],
                    faixa_etaria=row[27], id=row[0]
                ) for row in rows]


