import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "banco_cirurgias.db"

class Sala:
    def __init__(self, usuario_id, nome, horario_seg=None, horario_sab=None, horario_dom=None, id=None):
        self.id = id
        self.usuario_id = usuario_id
        self.nome = nome
        self.horario_seg = horario_seg
        self.horario_sab = horario_sab
        self.horario_dom = horario_dom

    def salvar(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        if self.id is None:
            cursor.execute("""
                INSERT INTO salas (usuario_id, nome, horario_seg, horario_sab, horario_dom)
                VALUES (?, ?, ?, ?, ?)
            """, (self.usuario_id, self.nome, self.horario_seg, self.horario_sab, self.horario_dom))
            self.id = cursor.lastrowid
        else:
            cursor.execute("""
                UPDATE salas
                SET nome=?, horario_seg=?, horario_sab=?, horario_dom=?
                WHERE id=?
            """, (self.nome, self.horario_seg, self.horario_sab, self.horario_dom, self.id))
        conn.commit()
        conn.close()

    def excluir(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM salas WHERE id=?", (self.id,))
        conn.commit()
        conn.close()

    @staticmethod
    def listar_por_usuario(usuario_id):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, horario_seg, horario_sab, horario_dom FROM salas WHERE usuario_id=?", (usuario_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Sala(usuario_id, nome=row[1], horario_seg=row[2], horario_sab=row[3], horario_dom=row[4], id=row[0])
                for row in rows]

    @staticmethod
    def buscar_por_id(sala_id):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT usuario_id, nome, horario_seg, horario_sab, horario_dom FROM salas WHERE id=?", (sala_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Sala(row[0], nome=row[1], horario_seg=row[2], horario_sab=row[3], horario_dom=row[4], id=sala_id)
        return None
