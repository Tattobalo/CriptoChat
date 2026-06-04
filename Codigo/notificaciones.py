import smtplib
from email.mime.text import MIMEText

def enviar_notificacion_correo(correo_destino, destinatario_name):
    """Envía un correo electrónico avisando que hay un nuevo mensaje criptográfico."""
    remitente = "cryptovault.sistema@gmail.com"
    asunto = "Tienes un nuevo mensaje secreto en CryptoVault"
    cuerpo = f"Hola {destinatario_name},\n\nAlguien te ha dejado un mensaje cifrado en la plataforma CryptoVault. Por seguridad, el contenido únicamente puede ser visualizado e iniciado sesión dentro de la aplicación local.\n\nSaludos,\nEquipo de Seguridad Informática."
    
    msg = MIMEText(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = remitente
    msg['To'] = correo_destino

    print(f"\n[NOTIFICACIÓN] Intentando enviar correo de alerta a: {correo_destino}...")
    
    # NOTA: Para producción real, descomentar este bloque configurando una cuenta SMTP real
    # try:
    #     with smtplib.SMTP_SSL('smtp.gmail.com', 465) as servidor:
    #         servidor.login(remitente, "TU_CONTRASEÑA_DE_APLICACION")
    #         servidor.sendmail(remitente, correo_destino, msg.as_string())
    #     print("[NOTIFICACIÓN] ¡Correo enviado con éxito!")
    # except Exception as e:
    #     print(f"[NOTIFICACIÓN] No se pudo enviar el correo real (Simulado en consola): {e}")
    
    print(f"[NOTIFICACIÓN SIMULADA] Mensaje enviado a la cola de correo para: {destinatario_name} ({correo_destino})")