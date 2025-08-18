def check_urgency(row):
    review = row["review"].lower()
    urgent_keywords = ["urgente", "reembolso", "devuelvan", "demanda", "legal", "fraude"]
    for word in urgent_keywords:
        if word in review:
            return {
                "alert": True,
                "reason": f"Palabra clave urgente detectada: '{word}'"
            }
    return {"alert": False}
