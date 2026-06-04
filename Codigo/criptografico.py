import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import os

class ModuloCriptografico:
    def __init__(self):
        ruta_privada = "clave_privada.pem"
        ruta_publica = "clave_publica.pem"
        
        # Si las llaves ya existen en tu carpeta, las cargamos de forma permanente
        if os.path.exists(ruta_privada) and os.path.exists(ruta_publica):
            with open(ruta_privada, "rb") as key_file:
                self.private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None
                )
            self.public_key = self.private_key.public_key()
        else:
            # Si es la primera vez que se ejecuta, las creamos y las escribimos en disco
            self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            self.public_key = self.private_key.public_key()
            
            # Guardar la clave privada en el disco duro de tu Fedora
            with open(ruta_privada, "wb") as f:
                f.write(self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            # Guardar la clave pública en el disco duro de tu Fedora
            with open(ruta_publica, "wb") as f:
                f.write(self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))

    def calcular_hash(self, datos: bytes) -> str:
        """Genera un hash SHA-256 para comprobar la integridad de los datos."""
        hash_object = hashlib.sha256(datos)
        return hash_object.hexdigest()

    def generar_llave_aes_volatil(self) -> bytes:
        """Genera una clave simétrica temporal para un mensaje específico."""
        return os.urandom(32)

    # --- CONFIDENCIALIDAD SIMÉTRICA (AES) ---
    def cifrar_aes(self, texto_plano: str, llave_aes: bytes) -> tuple:
        """Cifra datos usando AES en modo CBC con una llave específica."""
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(llave_aes), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        datos = texto_plano.encode('utf-8')
        padding_len = 16 - (len(datos) % 16)
        datos += bytes([padding_len] * padding_len)
        
        texto_cifrado = encryptor.update(datos) + encryptor.finalize()
        return texto_cifrado, iv

    def descifrar_aes(self, texto_cifrado: bytes, iv: bytes, llave_aes: bytes) -> str:
        """Descifra datos usando AES en modo CBC con una llave específica."""
        cipher = Cipher(algorithms.AES(llave_aes), modes.CBC(iv))
        decryptor = cipher.decryptor()
        datos_padded = decryptor.update(texto_cifrado) + decryptor.finalize()
        
        padding_len = datos_padded[-1]
        if padding_len < 1 or padding_len > 16:
            raise ValueError("Padding inválido")
        datos = datos_padded[:-padding_len]
        return datos.decode('utf-8')

    # --- PROTECCIÓN ASIMÉTRICA (RSA) ---
    def cifrar_llave_con_rsa(self, llave_aes: bytes) -> bytes:
        """Cifra la llave simétrica AES usando la llave pública RSA."""
        llave_cifrada = self.public_key.encrypt(
            llave_aes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return llave_cifrada

    def descifrar_llave_con_rsa(self, llave_aes_cifrada: bytes) -> bytes:
        """Descifra la llave simétrica AES usando la llave privada RSA."""
        llave_descifrada = self.private_key.decrypt(
            llave_aes_cifrada,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return llave_descifrada
    
    def cifrar_aes_bytes_compat(self, datos_bytes: bytes, llave_aes: bytes) -> tuple:
        """Cifra flujos binarios crudos sin forzar encoding de texto."""
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(llave_aes), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        padding_len = 16 - (len(datos_bytes) % 16)
        datos_bytes += bytes([padding_len] * padding_len)
        return encryptor.update(datos_bytes) + encryptor.finalize(), iv

    def descifrar_aes_raw(self, texto_cifrado: bytes, iv: bytes, llave_aes: bytes) -> bytes:
        """Descifra flujos binarios crudos manteniendo los bytes intactos."""
        cipher = Cipher(algorithms.AES(llave_aes), modes.CBC(iv))
        decryptor = cipher.decryptor()
        datos_padded = decryptor.update(texto_cifrado) + decryptor.finalize()
        padding_len = datos_padded[-1]
        return datos_padded[:-padding_len]