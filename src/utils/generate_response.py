def generate_response(review, sentiment):
    if sentiment == "positivo":
        return "¡Gracias por tu comentario positivo!"
    elif sentiment == "negativo":
        return "Lamentamos la experiencia. Estamos trabajando en mejorar."
    else:
        return "Gracias por tu opinión. ¡La tendremos en cuenta!"
