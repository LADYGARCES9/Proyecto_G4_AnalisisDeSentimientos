import smtplib
from email.mime.text import MIMEText

def enviar_alerta(mensaje):
    remitente = "tu_correo@gmail.com"
    destinatario = "equipo@empresa.com"
    password = "CLAVE_GENERADA_APP"  # usar clave segura

    msg = MIMEText(mensaje)
    msg["Subject"] = "⚠️ Alerta de Reseñas Negativas"
    msg["From"] = remitente
    msg["To"] = destinatario

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())

# Ejemplo: disparar alerta
porcentaje_negativo = 0.45
if porcentaje_negativo > 0.3:
    enviar_alerta(f"Se detectó un {porcentaje_negativo*100:.2f}% de reseñas negativas en la última hora 🚨")
