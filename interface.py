import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess  # Para ejecutar archivos locales
import webbrowser  # Para abrir URLs
from camara_openCV import run_virtual_steering 
from camara_tk import run_virtual_tk 
from styles import apply_styles

# -*- coding: utf-8 -*-
# Rutas del juego Unity
unity_exe_path = r"E:\personal\UNSA\2023-2\DSPJ\proyecto\ejec\gamV.exe"  # Para el juego local
unity_web_url = "https://juego_unity.com"

# Variables globales para controlar el estado de la cámara y el hilo
camera_thread = None
camera_thread_tk = None
stop_event = threading.Event()  # Evento para detener el hilo
stop_event_tk = threading.Event()  # Evento para detener el hilo camra tk

def get_control_methods():
    up_method = up_control_method.get()
    down_method = down_control_method.get()
    print("Método de control seleccionado para arriba:", up_method)
    print("Método de control seleccionado para abajo:", down_method)
    return up_method, down_method

def get_sensitivity_and_distance():
    steering_sensitivity = sensitivity_value.get()
    distance_threshold = distance_value.get()
    print("Sensibilidad seleccionada:", steering_sensitivity)
    print("Umbral de distancia seleccionado:", distance_threshold)
    return steering_sensitivity, distance_threshold

def open_unity_game():
    # Comprobamos si es un juego local o en web y lo ejecutamos
    try:
        if unity_exe_path:  # Si se especificó un archivo ejecutable
            subprocess.Popen(unity_exe_path)
        elif unity_web_url:  # Si es una URL de WebGL
            webbrowser.open(unity_web_url)
        else:
            messagebox.showinfo("Juego Unity", "No se especificó una ruta o URL para el juego.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el juego: {e}")

# Funciones para mostrar u ocultar los frames
def toggle_camera():
    if camera_var.get():
        camera_frame.grid(row=0, column=0, padx=5, pady=5, sticky="n")
    else:
        camera_frame.grid_forget()

def toggle_camera_tk():
    if camera_var_tk.get():
        camera_frame_tk.grid(row=0, column=1, padx=5, pady=5, sticky="n")
    else:
        camera_frame_tk.grid_forget()

def toggle_unity_game():
    if unity_var.get():
        unity_frame.grid(row=0, column=2, padx=5, pady=5, sticky="n")
    else:
        unity_frame.grid_forget()

def toggle_settings():
    if settings_var.get():
        settings_frame.grid(row=0, column=3, padx=5, pady=5, sticky="n")
    else:
        settings_frame.grid_forget()


def start_camera_thread():
    global camera_thread,  stop_event
    print("La cámara ya está en ejecución.")

    try:
        up_method, down_method = get_control_methods()
        steering_sensitivity, distance_threshold = get_sensitivity_and_distance()

        stop_event = threading.Event()
        camera_thread = threading.Thread(target=run_virtual_steering, args=(up_method, down_method, stop_event, steering_sensitivity, distance_threshold))
        camera_thread.start()
        print("Hilo de cámara iniciado.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo iniciar la cámara: {e}")

def stop_camera_thread():
    global camera_thread_tk , stop_event
    stop_event.set() 
    print("Hilo de cámara detenido.")

def start_camera_tk_thread():
    global camera_thread_tk,  stop_event_tk
    print("La cámara tk ya está en ejecución.")

    try:
        up_method, down_method = get_control_methods()
        
        stop_event = threading.Event()
        camera_thread_tk = threading.Thread(target=run_virtual_tk, args=(up_method, down_method, stop_event))
        camera_thread_tk.start()
        print("Hilo de cámara tk iniciado.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo iniciar la cámara tk: {e}")

def stop_camera_tk_thread():
    global camera_thread , stop_event
    stop_event.set() 
    print("Hilo de cámara tk detenido.")

# Función para actualizar la etiqueta de sensibilidad
def update_sensitivity_label(value):
    value = float(value)
    sensitivity_value.set(value)
    sensitivity_label.config(text=f"Sensibilidad: {value:.2f}")

# Función para actualizar la etiqueta de distancia
def update_distance_label(value):
    value = float(value)
    distance_value.set(value)
    distance_label.config(text=f"Distancia: {value:.2f}")

def on_closing():
    stop_camera_thread()  # Detener el hilo de la cámara
    root.destroy()  # Cerrar la ventana



# Función para hacer que un frame sea arrastrable
def make_draggable(widget):
    widget.bind("<Button-1>", on_start_drag)
    widget.bind("<B1-Motion>", on_drag)

def on_start_drag(event):
    widget = event.widget
    widget.startX = event.x
    widget.startY = event.y

def on_drag(event):
    widget = event.widget
    x = widget.winfo_x() - widget.startX + event.x
    y = widget.winfo_y() - widget.startY + event.y
    widget.place(x=x, y=y)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Ventana de Control")
root.geometry("900x600")

apply_styles() 

# Variables de control para los Checkbuttons
camera_var_tk = tk.BooleanVar(value=True)
camera_var = tk.BooleanVar(value=True)
unity_var = tk.BooleanVar(value=True)
settings_var = tk.BooleanVar(value=True)

# Crear los frames para cada sección utilizando solo `grid`
camera_frame_tk = ttk.Frame(root, style='TFrame')
ttk.Label(camera_frame_tk, text="Cámara (Volante Virtual Tk)", 
          style='TLabel').grid(row=0, column=0, padx=5, pady=5)
ttk.Button(camera_frame_tk, text="Iniciar Cámara", 
           command=start_camera_tk_thread, style='TButton').grid(row=1, column=0, padx=5, pady=5)

camera_frame = ttk.Frame(root, style='TFrame')
ttk.Label(camera_frame, text="Cámara (Volante Virtual OpenCV)", 
          style='TLabel').grid(row=0, column=0, padx=5, pady=5)
ttk.Button(camera_frame, text="Iniciar Cámara", command=start_camera_thread, 
           style='TButton').grid(row=1, column=0, padx=5, pady=5)

unity_frame = ttk.Frame(root, style='TFrame')
ttk.Label(unity_frame, text="Juego Unity", style='TLabel').grid(row=0, column=0, padx=5, pady=5)
ttk.Button(unity_frame, text="Abrir Juego Unity", command=open_unity_game, 
           style='TButton').grid(row=1, column=0, padx=5, pady=5)

settings_frame = ttk.Frame(root, style='TFrame')
ttk.Label(settings_frame, text="Opciones de Configuración", 
          style='TLabel').grid(row=0, column=0, columnspan=2, padx=5, pady=5)

# Ajuste de sensibilidad
ttk.Label(settings_frame, text="Ajuste de Sensibilidad:", 
          style='TLabel').grid(row=1, column=0, columnspan=2, pady=5)
sensitivity_value = tk.DoubleVar(value=0.5)  # Valor por defecto 0.5
sensitivity_scale = ttk.Scale(settings_frame, from_=0, to=1, orient="horizontal", style='TScale', command=update_sensitivity_label, variable=sensitivity_value)
sensitivity_scale.grid(row=2, column=0, columnspan=2, pady=5)
sensitivity_label = ttk.Label(settings_frame, text=f"Sensibilidad: {sensitivity_value.get():.2f}", style='TLabel')
sensitivity_label.grid(row=2, column=2, padx=5)

# Umbral de distancia
ttk.Label(settings_frame, text="Umbral de Distancia:", 
          style='TLabel').grid(row=3, column=0, columnspan=2, pady=5)
distance_value = tk.DoubleVar(value=0.3)  # Valor por defecto 0.3
distance_scale = ttk.Scale(settings_frame, from_=0.1, to=1, orient="horizontal", style='TScale', command=update_distance_label, variable=distance_value)
distance_scale.grid(row=4, column=0, columnspan=2, pady=5)
distance_label = ttk.Label(settings_frame, text=f"Distancia: {distance_value.get():.2f}", style='TLabel')
distance_label.grid(row=4, column=2, padx=5)

# Configuración de teclas direccionales
ttk.Label(settings_frame, text="Teclas Direccionales:", 
          style='TLabel').grid(row=5, column=0, columnspan=2, pady=5)

# Control para flecha arriba
ttk.Label(settings_frame, text="Arriba:", 
          style='TLabel').grid(row=6, column=0, columnspan=2, pady=5)
up_control_method = tk.StringVar(value="Cabeza")
ttk.Radiobutton(settings_frame, text="Con la mano", 
                variable=up_control_method, value="Mano", style='TRadiobutton').grid(row=7, column=0, pady=5)
ttk.Radiobutton(settings_frame, text="Con la cabeza", 
                variable=up_control_method, value="Cabeza", style='TRadiobutton').grid(row=7, column=1, pady=5)

# Control para flecha abajo
ttk.Label(settings_frame, text="Abajo:", style='TLabel').grid(row=9, column=0, columnspan=2, pady=5)
down_control_method = tk.StringVar(value="Cabeza")
ttk.Radiobutton(settings_frame, text="Con la mano", 
                variable=down_control_method, value="Mano", style='TRadiobutton').grid(row=10, column=0, pady=5)
ttk.Radiobutton(settings_frame, text="Con la cabeza", 
                variable=down_control_method, value="Cabeza", style='TRadiobutton').grid(row=10, column=1, pady=5)

# Botón de guardar configuraciones que también muestra los valores seleccionados
ttk.Button(settings_frame, text="Guardar", 
           command=lambda: messagebox.showinfo("Guardado", f"Configuraciones guardadas:\nArriba: {up_control_method.get()}\nAbajo: {down_control_method.get()}\nSensibilidad: {sensitivity_value.get():.2f}\nDistancia: {distance_value.get():.2f}"), 
           style='TButton').grid(row=12, column=0, columnspan=2, pady=10)

def show_columns():
    clear_layout()
    camera_frame_tk.grid(row=0, column=0, padx=5, pady=5, sticky="n")
    camera_frame.grid(row=0, column=1, padx=5, pady=5, sticky="n")
    unity_frame.grid(row=0, column=2, padx=5, pady=5, sticky="n")
    settings_frame.grid(row=0, column=3, padx=5, pady=5, sticky="n")

def show_quadrants():
    clear_layout()
    camera_frame_tk.grid(row=0, column=0, padx=5, pady=5, sticky="n")
    camera_frame.grid(row=0, column=1, padx=5, pady=5, sticky="n")
    unity_frame.grid(row=1, column=0, padx=5, pady=5, sticky="n")
    settings_frame.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="n")

def show_rows():
    clear_layout()
    camera_frame_tk.grid(row=0, column=0, padx=5, pady=5, sticky="n")
    camera_frame.grid(row=1, column=0, padx=5, pady=5, sticky="n")
    unity_frame.grid(row=2, column=0, padx=5, pady=5, sticky="n")
    settings_frame.grid(row=3, column=0, padx=5, pady=5, sticky="n")

def clear_layout():
    camera_frame_tk.grid_forget()
    camera_frame.grid_forget()
    unity_frame.grid_forget()
    settings_frame.grid_forget()


# Empaquetar el settings_frame al final (modificar a grid)
show_quadrants()
# Hacer los frames arrastrables
make_draggable(camera_frame_tk)
make_draggable(camera_frame)
make_draggable(unity_frame)
make_draggable(settings_frame)

# Crear la barra de menú
menu_bar = tk.Menu(root)

# Crear el menú de opciones
menu_opciones = tk.Menu(menu_bar, tearoff=0)
menu_opciones.add_checkbutton(label="Cámara (Volante Virtual)", 
                              variable=camera_var, command=toggle_camera)
menu_opciones.add_checkbutton(label="Cámara tk (Volante Virtual)", 
                              variable=camera_var_tk, command=toggle_camera_tk)
menu_opciones.add_checkbutton(label="Juego Unity", 
                              variable=unity_var, command=toggle_unity_game)
menu_opciones.add_checkbutton(label="Opciones de Configuración", 
                              variable=settings_var, command=toggle_settings)
menu_opciones.add_separator()

# Crear el menú de vistas
menu_vistas = tk.Menu(menu_bar, tearoff=0)
menu_vistas.add_command(label="Ver en Columnas", command=show_columns)
menu_vistas.add_command(label="Ver en Cuadrantes", command=show_quadrants)
menu_vistas.add_command(label="Ver en Filas", command=show_rows)

# Agregar el menú de opciones a la barra de menú
menu_bar.add_cascade(label="Opciones", menu=menu_opciones)
menu_bar.add_cascade(label="Vistas", menu=menu_vistas)

# Configurar la barra de menú en la ventana principal
root.config(menu=menu_bar)



root.protocol("WM_DELETE_WINDOW", on_closing)

# Iniciar el bucle de la ventana de Tkinter
root.mainloop()
