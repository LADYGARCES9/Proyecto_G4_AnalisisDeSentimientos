from src.utils.generate_response import generate_response
from src.utils.alert_system import check_urgency
import pandas as pd

def test_generate_response():
    assert generate_response("producto defectuoso", "negativo") == "Lamentamos la experiencia. Estamos trabajando en mejorar."
    assert generate_response("excelente servicio", "positivo") == "¡Gracias por tu comentario positivo!"
    assert generate_response("todo bien", "neutro") == "Gracias por tu opinión. ¡La tendremos en cuenta!"

def test_check_urgency():
    row = pd.Series({'review': 'esto es urgente', 'sentiment': 'negativo'})
    result = check_urgency(row)
    assert isinstance(result, dict)
    assert result['alert'] is True
    assert 'urgente' in result['reason']
