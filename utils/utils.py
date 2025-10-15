import joblib
import pandas as pd
from pathlib import Path

def prever_duracao(caracteristicas):
    """Recebe um dicionário com as características e retorna a previsão em minutos."""
    try:
        # Caminho do modelo
        model_path = Path("utils/models/lightGBM_model.pkl")

        # Carregar pipeline
        pipeline = joblib.load(model_path)

        features = [
            'sex','bmi','asa','emop','department','optype','approach','position',
            'ane_type','preop_htn','preop_dm','preop_pft','preop_hb','preop_plt',
            'preop_pt','preop_aptt','preop_na','preop_k','preop_glucose','preop_alb',
            'preop_got','preop_gpt','preop_bun','preop_cr','Faixa_Etaria'
        ]

        # Ajusta o nome da coluna para bater com o modelo
        carac_ajustada = caracteristicas.copy()
        carac_ajustada['Faixa_Etaria'] = carac_ajustada.pop('faixa_etaria', None)

        # Criar DataFrame com uma linha
        df = pd.DataFrame([carac_ajustada], columns=features)

        # Fazer a predição
        pred = pipeline.predict(df)[0]
        return round(float(pred), 2)
    except Exception as e:
        print(f"⚠️ Erro ao prever duração: {e}")
        return 177  # fallback padrão
