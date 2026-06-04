import sqlite3
import hashlib
import os

class BaseDatos:
    def __init__(self, nombre_db="datos_sistema.db"):
        self.nombre_db = nombre_db
        self.conectar()
        self.crear_tablas()

    def conectar(self):
        self.conexion = sqlite3.connect(self.nombre_db)
        self.cursor = self.conexion.cursor()

    def crear_tablas(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY,
            password_hash BLOB NOT NULL,
            salt BLOB NOT NULL,
            correo TEXT NOT NULL
        )
        """)
        
        # Agregamos la columna llave_aes_cifrada para la persistencia real
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_anonimo TEXT NOT NULL,
            emisor TEXT NOT NULL,
            destinatario TEXT NOT NULL,
            texto_cifrado BLOB NOT NULL,
            iv BLOB NOT NULL,
            hash_integridad TEXT NOT NULL,
            llave_aes_cifrada BLOB NOT NULL,
            id_referencia INTEGER DEFAULT NULL,
            FOREIGN KEY(destinatario) REFERENCES usuarios(username),
            FOREIGN KEY(emisor) REFERENCES usuarios(username),
            FOREIGN KEY(id_referencia) REFERENCES mensajes(id)
        )
        """)
        self.conexion.commit()

    def registrar_usuario(self, username, password, correo):
        try:
            salt = os.urandom(16)
            hash_f = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            self.cursor.execute(
                "INSERT INTO usuarios (username, password_hash, salt, correo) VALUES (?, ?, ?, ?)",
                (username, hash_f, salt, correo)
            )
            self.conexion.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def verificar_usuario(self, username, password):
        self.cursor.execute("SELECT password_hash, salt FROM usuarios WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        if not row:
            return False
        hash_guardado, salt = row
        hash_nuevo = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return hash_guardado == hash_nuevo

    def obtener_usuarios(self):
        self.cursor.execute("SELECT username FROM usuarios")
        return [row[0] for row in self.cursor.fetchall()]

    def obtener_correo(self, username):
        self.cursor.execute("SELECT correo FROM usuarios WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def insertar_mensaje(self, emisor, destinatario, texto_cifrado, iv, hash_integridad, llave_aes_cifrada, id_referencia=None):
        import random
        import string
        
        if id_referencia:
            self.cursor.execute("SELECT codigo_anonimo FROM mensajes WHERE id = ?", (id_referencia,))
            row = self.cursor.fetchone()
            codigo = row[0] if row else "MSG-UNK"
        else:
            caracteres = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            codigo = f"MSG-{caracteres}"
        
        # ORDEN ESTRICTO: texto_cifrado, iv, hash_integridad, llave_aes_cifrada, id_referencia
        self.cursor.execute("""
            INSERT INTO mensajes (codigo_anonimo, emisor, destinatario, texto_cifrado, iv, hash_integridad, llave_aes_cifrada, id_referencia) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (codigo, emisor, destinatario, texto_cifrado, iv, hash_integridad, llave_aes_cifrada, id_referencia))
        self.conexion.commit()

    def obtener_detalle_mensaje(self, id_mensaje):
        """Recupera los metadatos de control interno del mensaje original."""
        self.cursor.execute("""
            SELECT texto_cifrado, iv, hash_integridad, emisor, destinatario, codigo_anonimo, llave_aes_cifrada, id_referencia 
            FROM mensajes WHERE id = ?
        """, (id_mensaje,))
        return self.cursor.fetchone()

    def obtener_hilo_completo(self, id_raiz):
        """Recupera el mensaje raíz y todas sus respuestas ordenadas por ID."""
        self.cursor.execute("""
            SELECT id, texto_cifrado, iv, hash_integridad, emisor, destinatario, llave_aes_cifrada, id_referencia 
            FROM mensajes 
            WHERE id = ? OR id_referencia = ?
            ORDER BY id ASC
        """, (id_raiz, id_raiz))
        return self.cursor.fetchall()

    def obtener_mensajes_publicos(self):
        query = """
        SELECT r.id, r.codigo_anonimo, 
               (SELECT COUNT(*) FROM mensajes WHERE id_referencia = r.id) as total_respuestas,
               r.texto_cifrado
        FROM mensajes r
        WHERE r.id_referencia IS NULL
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def cerrar(self):
        self.conexion.close()