import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
import io
from notificaciones import enviar_notificacion_correo

class InterfazApp:
    def __init__(self, root, modulo_cripto, base_datos):
        self.root = root
        self.root.title("CryptoVault - Buzon Secreto de Mensajes y Fotos Anonimas")
        self.root.geometry("1000x680")
        self.root.resizable(False, False)
        
        self.cripto = modulo_cripto
        self.db = base_datos
        self.usuario_actual = None
        self.id_mensaje_seleccionado = None

        self.bg_color = "#f8f9fa"
        self.accent_color = "#2c3e50"
        self.root.configure(bg=self.bg_color)

        self.crear_componentes()
        self.actualizar_vista()

    def crear_componentes(self):
        # --- BARRA SUPERIOR DE AUTENTICACIÓN ---
        self.auth_frame = tk.LabelFrame(self.root, text=" Control de Acceso / Autenticacion ", font=("Arial", 10, "bold"), bg=self.bg_color, padx=10, pady=5)
        self.auth_frame.pack(fill="x", padx=15, pady=10)

        self.lbl_user = tk.Label(self.auth_frame, text="Usuario:", bg=self.bg_color, font=("Arial", 9))
        self.lbl_user.grid(row=0, column=0, padx=2, sticky="e")
        self.entry_user = tk.Entry(self.auth_frame, width=10, font=("Arial", 9))
        self.entry_user.grid(row=0, column=1, padx=4)

        self.lbl_pass = tk.Label(self.auth_frame, text="Contrasena:", bg=self.bg_color, font=("Arial", 9))
        self.lbl_pass.grid(row=0, column=2, padx=2, sticky="e")
        self.entry_pass = tk.Entry(self.auth_frame, width=10, show="*", font=("Arial", 9))
        self.entry_pass.grid(row=0, column=3, padx=4)

        self.lbl_correo = tk.Label(self.auth_frame, text="Correo:", bg=self.bg_color, font=("Arial", 9))
        self.lbl_correo.grid(row=0, column=4, padx=2, sticky="e")
        self.entry_correo = tk.Entry(self.auth_frame, width=14, font=("Arial", 9))
        self.entry_correo.grid(row=0, column=5, padx=4)

        self.btn_login = tk.Button(self.auth_frame, text="Iniciar Sesion", font=("Arial", 9, "bold"), bg="#34495e", fg="white", command=self.iniciar_sesion, padx=8)
        self.btn_login.grid(row=0, column=6, padx=4)

        self.btn_registro = tk.Button(self.auth_frame, text="Registrarse", font=("Arial", 9), bg="#7f8c8d", fg="white", command=self.registrar_usuario, padx=8)
        self.btn_registro.grid(row=0, column=7, padx=4)

        self.lbl_sesion_info = tk.Label(self.auth_frame, text="MODO PUBLICO", font=("Arial", 9, "bold"), fg="white", bg="#7f8c8d", padx=10, pady=3, width=22)
        self.lbl_sesion_info.grid(row=0, column=8, padx=10, sticky="w")

        # --- PANEL PRINCIPAL ---
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # --- PANEL IZQUIERDO: FORMULARIO ---
        self.left_frame = tk.LabelFrame(main_frame, text=" Enviar Nuevo Contenido Anonimo ", font=("Arial", 11, "bold"), bg=self.bg_color, padx=10, pady=10)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.lbl_combo_desc = tk.Label(self.left_frame, text="Destinatario (Receptor Oculto):", font=("Arial", 10), bg=self.bg_color)
        self.lbl_combo_desc.pack(anchor="w", pady=(5, 2))
        self.combo_destinatarios = ttk.Combobox(self.left_frame, state="readonly", font=("Arial", 10))
        self.combo_destinatarios.pack(fill="x", pady=(0, 10))

        self.lbl_txt_area = tk.Label(self.left_frame, text="Contenido del Mensaje Secreto:", font=("Arial", 10), bg=self.bg_color)
        self.lbl_txt_area.pack(anchor="w", pady=(5, 2))
        self.txt_mensaje_nuevo = tk.Text(self.left_frame, font=("Arial", 10), height=8, width=35)
        self.txt_mensaje_nuevo.pack(fill="both", expand=True, pady=(0, 10))

        self.btn_adjuntar_img = tk.Button(
            self.left_frame, text="Adjuntar y Cifrar Imagen (.png, .jpg)", font=("Arial", 9, "bold"),
            bg="#d35400", fg="white", bd=0, pady=5, command=self.guardar_imagen
        )
        self.btn_adjuntar_img.pack(fill="x", pady=(0, 10))

        self.btn_enviar = tk.Button(
            self.left_frame, text="Cifrar Texto e Inyectar al Buzon", font=("Arial", 10, "bold"),
            bg="#27ae60", fg="white", bd=0, pady=8, command=self.guardar_mensaje
        )
        self.btn_enviar.pack(fill="x")

        # --- PANEL DERECHO: BUZÓN ---
        right_frame = tk.Frame(main_frame, bg=self.bg_color)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        lbl_lista = tk.LabelFrame(right_frame, text=" Buzon del Sistema (Modo Anonimo) ", font=("Arial", 11, "bold"), bg=self.bg_color, padx=5, pady=5)
        lbl_lista.pack(fill="both", expand=True, pady=(0, 10))

        self.lista_mensajes = ttk.Treeview(lbl_lista, columns=("ID", "Codigo", "Respuestas", "Contenido Cifrado"), show="headings", height=8)
        self.lista_mensajes.heading("ID", text="ID")
        self.lista_mensajes.heading("Codigo", text="Codigo")
        self.lista_mensajes.heading("Respuestas", text="Respuestas")
        self.lista_mensajes.heading("Contenido Cifrado", text="Contenido (Hexadecimal Base de Datos)")
        self.lista_mensajes.column("ID", width=35, anchor="center")
        self.lista_mensajes.column("Codigo", width=80, anchor="center")
        self.lista_mensajes.column("Respuestas", width=90, anchor="center")
        self.lista_mensajes.column("Contenido Cifrado", width=250)
        self.lista_mensajes.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(lbl_lista, orient="vertical", command=self.lista_mensajes.yview)
        self.lista_mensajes.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.lista_mensajes.bind("<<TreeviewSelect>>", self.leer_mensaje)

        # --- VISOR INFERIOR ---
        self.lbl_visor = tk.LabelFrame(right_frame, text=" Visualizador, Integridad e Hilado ", font=("Arial", 11, "bold"), bg=self.bg_color, padx=10, pady=5)
        self.lbl_visor.pack(fill="x", pady=(5, 0))

        self.lbl_status = tk.Label(self.lbl_visor, text="Seleccione un registro anonimo para procesar", font=("Arial", 9, "bold"), bg="#d6dbdf", fg="#566573", pady=5)
        self.lbl_status.pack(fill="x", pady=(0, 5))

        tk.Label(self.lbl_visor, text="Mensaje Descifrado:", font=("Arial", 10), bg=self.bg_color).pack(anchor="w")
        self.txt_descifrado = tk.Text(self.lbl_visor, font=("Arial", 10, "bold"), height=5, bg="#ebf5fb", state="disabled")
        self.txt_descifrado.pack(fill="x", pady=(0, 5))

        self.btn_responder = tk.Button(
            self.lbl_visor, text="Responder de Forma Anonima a este Mensaje", font=("Arial", 9, "bold"),
            bg="#2980b9", fg="white", bd=0, pady=5, state="disabled", command=self.activar_modo_respuesta
        )
        self.btn_responder.pack(fill="x")

    def registrar_usuario(self):
        user = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        correo = self.entry_correo.get().strip()
        if not user or not password or not correo:
            messagebox.showwarning("Campos incompletos", "Complete los campos para registrarse.")
            return
        if self.db.registrar_usuario(user, password, correo):
            messagebox.showinfo("Exito", f"Usuario '{user}' registrado.")
            self.entry_pass.delete(0, tk.END)
            self.entry_correo.delete(0, tk.END)
            self.actualizar_vista()
        else:
            messagebox.showerror("Error", "Usuario ya existente.")

    def iniciar_sesion(self):
        if self.usuario_actual:
            self.usuario_actual = None
            self.btn_login.config(text="Iniciar Sesion", bg="#34495e")
            self.entry_user.config(state="normal")
            self.entry_pass.config(state="normal")
            self.entry_correo.config(state="normal")
            self.btn_registro.config(state="normal")
            self.lbl_sesion_info.config(text="MODO PUBLICO", bg="#7f8c8d")
            self.cancelar_modo_respuesta()
            self.actualizar_vista()
            self.limpiar_visor()
            return

        user = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        if not user or not password:
            messagebox.showwarning("Campos vacios", "Introduzca usuario y contraseña.")
            return

        if self.db.verificar_usuario(user, password):
            self.usuario_actual = user
            messagebox.showinfo("Bienvenido", f"Sesion activa: {user}")
            self.entry_pass.delete(0, tk.END)
            self.entry_user.config(state="disabled")
            self.entry_pass.config(state="disabled")
            self.entry_correo.config(state="disabled")
            self.btn_registro.config(state="disabled")
            self.btn_login.config(text="Cerrar Sesion", bg="#c0392b")
            self.lbl_sesion_info.config(text=f"CONECTADO: {self.usuario_actual.upper()}", bg="#27ae60")
            self.actualizar_vista()
            self.limpiar_visor()
        else:
            messagebox.showerror("Fallo", "Credenciales incorrectas.")

    def determinar_contexto_envio(self):
        if self.id_mensaje_seleccionado and not self.combo_destinatarios.winfo_viewable():
            texto_cifrado, iv, hash_guardado, emisor_orig, dest_orig, cod, llave_cif, id_ref = self.db.obtener_detalle_mensaje(self.id_mensaje_seleccionado)
            destinatario_final = emisor_orig if self.usuario_actual == dest_orig else dest_orig
            ref_id = self.id_mensaje_seleccionado
        else:
            destinatario_final = self.combo_destinatarios.get()
            ref_id = None
        return destinatario_final, ref_id

    def guardar_mensaje(self):
        texto = self.txt_mensaje_nuevo.get("1.0", tk.END).strip()
        if not texto:
            return

        destinatario_final, ref_id = self.determinar_contexto_envio()
        if not destinatario_final:
            messagebox.showwarning("Incompleto", "Seleccione un destinatario.")
            return
        if self.usuario_actual == destinatario_final:
            messagebox.showwarning("Error", "No puedes enviarte mensajes a ti mismo.")
            return

        datos_preparados = f"TXT:{texto}"
        self.inyectar_cripto_sistema(datos_preparados, destinatario_final, ref_id, es_binario=False)

    def guardar_imagen(self):
        destinatario_final, ref_id = self.determinar_contexto_envio()
        if not destinatario_final:
            messagebox.showwarning("Incompleto", "Seleccione un destinatario de la lista.")
            return
        if self.usuario_actual == destinatario_final:
            messagebox.showwarning("Error", "No puedes enviarte archivos a ti mismo.")
            return

        ruta_foto = filedialog.askopenfilename(filetypes=[("Imagenes", "*.png *.jpg *.jpeg")])
        if not ruta_foto:
            return

        try:
            with open(ruta_foto, "rb") as f:
                bytes_raw_foto = f.read()
            
            payload_binario = b"IMG:" + bytes_raw_foto
            self.inyectar_cripto_sistema(payload_binario, destinatario_final, ref_id, es_binario=True)
        except Exception as e:
            messagebox.showerror("Error de Archivo", f"No se pudo leer la foto: {e}")

    def inyectar_cripto_sistema(self, datos, destinatario, ref_id, es_binario=False):
        try:
            emisor_actual = self.usuario_actual if self.usuario_actual else "Anonimo"
            llave_aes = self.cripto.generar_llave_aes_volatil()
            llave_cifrada_rsa = self.cripto.cifrar_llave_con_rsa(llave_aes)

            bytes_a_cifrar = datos if es_binario else datos.encode('utf-8')
            texto_cifrado, iv = self.cripto.cifrar_aes_bytes_compat(bytes_a_cifrar, llave_aes)
            hash_int = self.cripto.calcular_hash(bytes_a_cifrar)

            self.db.insertar_mensaje(emisor_actual, destinatario, texto_cifrado, iv, hash_int, llave_cifrada_rsa, ref_id)
            
            correo_dest = self.db.obtener_correo(destinatario)
            if correo_dest:
                enviar_notificacion_correo(correo_dest, destinatario)

            messagebox.showinfo("Exito", "Contenido protegido e inyectado al buzón.")
            self.txt_mensaje_nuevo.delete("1.0", tk.END)
            self.cancelar_modo_respuesta()
            self.actualizar_vista()
        except Exception as e:
            messagebox.showerror("Fallo Criptografico", f"Error: {e}")

    def activar_modo_respuesta(self):
        if not self.id_mensaje_seleccionado:
            return
        texto_cifrado, iv, hash_guardado, emisor_orig, dest_orig, cod, llave_cif, id_ref = self.db.obtener_detalle_mensaje(self.id_mensaje_seleccionado)
        self.left_frame.config(text=f" Continuar conversacion en {cod} ")
        self.lbl_combo_desc.pack_forget()
        self.combo_destinatarios.pack_forget()
        self.btn_adjuntar_img.config(text="Responder adjuntando una Imagen")
        self.btn_enviar.config(text="Enviar Respuesta de Texto Cifrada", bg="#2980b9")

    def cancelar_modo_respuesta(self):
        self.id_mensaje_seleccionado = None
        self.left_frame.config(text=" Enviar Nuevo Mensaje Anonimo ")
        self.lbl_combo_desc.pack(anchor="w", before=self.txt_mensaje_nuevo, pady=(5, 2))
        self.combo_destinatarios.pack(fill="x", before=self.txt_mensaje_nuevo, pady=(0, 10))
        self.btn_adjuntar_img.config(text="Adjuntar y Cifrar Imagen (.png, .jpg)")
        self.btn_enviar.config(text="Cifrar Texto e Inyectar al Buzon", bg="#27ae60")
        self.btn_responder.config(state="disabled")

    def actualizar_vista(self):
        usuarios = self.db.obtener_usuarios()
        if self.usuario_actual in usuarios:
            usuarios.remove(self.usuario_actual)
        self.combo_destinatarios['values'] = usuarios
        
        for item in self.lista_mensajes.get_children():
            self.lista_mensajes.delete(item)
            
        mensajes_raiz = self.db.obtener_mensajes_publicos()
        for msg in mensajes_raiz:
            id_m, codigo, num_respuestas, bits_cifrados = msg
            contenido_visual = f"Hex: {bits_cifrados.hex()[:35]}..."
            self.lista_mensajes.insert("", tk.END, values=(id_m, codigo, num_respuestas, contenido_visual))

    def leer_mensaje(self, event):
        seleccion = self.lista_mensajes.selection()
        if not seleccion:
            return

        item = self.lista_mensajes.item(seleccion[0])
        id_mensaje_raiz = item["values"][0]
        self.id_mensaje_seleccionado = id_mensaje_raiz

        texto_cifrado, iv, hash_guardado, emisor_raiz, destinatario_raiz, codigo_raiz, llave_cif_raiz, id_ref = self.db.obtener_detalle_mensaje(id_mensaje_raiz)

        if not self.usuario_actual:
            self.lbl_status.config(text="MODO ANONIMO: Contenido protegido. Inicie sesion.", bg="#7f8c8d", fg="white")
            self.txt_descifrado.config(state="normal")
            self.txt_descifrado.delete("1.0", tk.END)
            self.txt_descifrado.insert(tk.END, "[SISTEMA BLOQUEADO - INICIE SESION]")
            self.txt_descifrado.config(state="disabled")
            self.btn_responder.config(state="disabled")
            return

        if self.usuario_actual != emisor_raiz and self.usuario_actual != destinatario_raiz:
            self.lbl_status.config(text="RESTRICCION DE PRIVACIDAD: No participas en este hilo.", bg="#d35400", fg="white")
            self.txt_descifrado.config(state="normal")
            self.txt_descifrado.delete("1.0", tk.END)
            self.txt_descifrado.insert(tk.END, "[Privilegios criptograficos insuficientes]")
            self.txt_descifrado.config(state="disabled")
            self.btn_responder.config(state="disabled")
            return

        try:
            hilo = self.db.obtener_hilo_completo(id_mensaje_raiz)
            conversacion_textual = ""
            
            for msg in hilo:
                id_m, t_cifrado, v_iv, h_guardado, em, dest, ll_cifrada, ref = msg
                
                llave_aes_recuperada = self.cripto.descifrar_llave_con_rsa(ll_cifrada)
                bytes_descifrados = self.cripto.descifrar_aes_raw(t_cifrado, v_iv, llave_aes_recuperada)
                
                if em == self.usuario_actual:
                    header = "Enviado por ti:\n"
                else:
                    header = f"Respuesta de '{destinatario_raiz}':\n" if self.usuario_actual == emisor_raiz else "Mensaje Recibido de: [ANONIMO PARA TI]\n"

                if bytes_descifrados.startswith(b"IMG:"):
                    conversacion_textual += f"{header}[Archivo de Imagen Adjunto - Desplegado en ventana flotante]\n{'-'*60}\n"
                    if id_m == id_mensaje_raiz or (self.lista_mensajes.focus() and hilo[-1][0] == id_m):
                        self.crear_ventana_imagen_emergente(bytes_descifrados[4:])
                else:
                    texto_plano = bytes_descifrados.decode('utf-8')[4:]
                    conversacion_textual += f"{header}{texto_plano}\n{'-'*60}\n"

            self.txt_descifrado.config(state="normal")
            self.txt_descifrado.delete("1.0", tk.END)
            self.txt_descifrado.insert(tk.END, conversacion_textual)
            self.txt_descifrado.config(state="disabled")

            self.lbl_status.config(text=f"CONVERSACION ACTIVA ({codigo_raiz}) | Historial hibrido descifrado.", bg="#2ecc71", fg="white")
            self.btn_responder.config(state="normal")
        except Exception as e:
            self.lbl_status.config(text=f"Error al descifrar el flujo del canal: {e}", bg="#e74c3c", fg="white")

    def crear_ventana_imagen_emergente(self, bytes_foto):
        try:
            ventanita = tk.Toplevel(self.root)
            ventanita.title("CryptoVault Viewer - Imagen Descifrada Seguro")
            
            img_stream = Image.open(io.BytesIO(bytes_foto))
            img_stream.thumbnail((450, 450))
            
            render_foto = ImageTk.PhotoImage(img_stream)
            lbl = tk.Label(ventanita, image=render_foto, bg="#2c3e50", padx=10, pady=10)
            lbl.image = render_foto
            lbl.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Visor Error", f"No se pudo renderizar la imagen: {e}")

    def limpiar_visor(self):
        self.lbl_status.config(text="Seleccione un registro anonimo para procesar", bg="#d6dbdf", fg="#566573")
        self.txt_descifrado.config(state="normal")
        self.txt_descifrado.delete("1.0", tk.END)
        self.txt_descifrado.config(state="disabled")
        self.btn_responder.config(state="disabled")