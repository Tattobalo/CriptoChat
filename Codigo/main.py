import tkinter as tk
from criptografico import ModuloCriptografico
from base_datos import BaseDatos
from interfaz import InterfazApp

def iniciar_sistema():
    # 1. Inicializar la raíz de la interfaz gráfica (Tkinter)
    root = tk.Tk()
    
    # 2. Inicializar los componentes lógicos del sistema
    try:
        modulo_cripto = ModuloCriptografico()
        base_datos = BaseDatos()
        
        # 3. Inyectar las dependencias lógicas dentro de la interfaz
        app = InterfazApp(root, modulo_cripto, base_datos)
        
        # Asegurar el cierre limpio de la base de datos al cerrar la ventana
        def on_closing():
            base_datos.cerrar()
            root.destroy()
            
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 4. Lanzar el bucle principal de la aplicación
        root.mainloop()
        
    except Exception as e:
        print(f"Error crítico al iniciar el sistema CryptoVault: {e}")

if __name__ == "__main__":
    iniciar_sistema()