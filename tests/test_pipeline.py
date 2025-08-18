from src.utils.generate_response import generate_response
from src.utils.alert_system import check_urgency

def test_generate_response():
assert generate_response("producto defectuoso", "negativo") == "Lamentamos la experiencia. Estamos trabajando en mejorar."
assert generate_response("excelente servicio", "positivo") == "¡Gracias por tu comentario positivo!"
assert generate_response("todo bien", "neutro") == "Gracias por tu opinión. ¡La tendremos en cuenta!"

def test_check_urgency():
print(">> Test de check_urgency")

class DummyRow:
    def __init__(self, review, sentiment):
        self.review = review
        self.sentiment = sentiment

    def __getitem__(self, key):
        return getattr(self, key)

# Este test solo verifica que no lanza errores y puede imprimir (si está implementado para hacerlo)
check_urgency(DummyRow("esto es urgente", "negativo"))
