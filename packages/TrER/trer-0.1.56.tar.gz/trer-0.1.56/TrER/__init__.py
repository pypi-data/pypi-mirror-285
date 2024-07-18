import pandas as pd, numpy as np


def load_data(
    url="https://raw.githubusercontent.com/CausalML/TreatmentEffectRisk/main/data/behaghel.csv",
):
    data = pd.read_csv(url)
    return data


data = load_data()
