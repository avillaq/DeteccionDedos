import cv2
import threading
import time
import tkinter as tk
from tkinter import Toplevel
from PIL import Image, ImageTk

# Variable global para el estado de la cámara
camera_running = False

# Función para capturar y mostrar video de la cámara
def video_stream(window, stop_event):
    global camera_running
    cap = cv2.VideoCapture(0)

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print("No se pudo capturar el video.")
            break
        
        # Convertir el frame de BGR a RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convertir el frame a imagen de Pillow
        img = Image.fromarray(frame)
        img = img.resize((640, 480), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(image=img)

        # Verificar si la ventana aún está abierta antes de actualizar
        if window.winfo_exists():
            window.img_label.configure(image=img_tk)
            window.img_label.image = img_tk  # Mantener una referencia

        # Actualizar la ventana
        window.update()

    cap.release()
    camera_running = False  # Actualizar el estado al cerrar el hilo

# Función para iniciar el hilo de la cámara
def run_virtual_tk(up_method, down_method, stop_event):
    global camera_running

    if camera_running:
        print("La cámara ya está en ejecución.")
        return  # No iniciar la cámara si ya está corriendo

    camera_running = True
    print(f"Iniciando control de la cámara con método: {up_method} y {down_method}.")

    # Crear la subventana
    sub_window = Toplevel()
    sub_window.title("Cámara Real")
    sub_window.geometry("640x480")

    # Crear un label para mostrar el video
    img_label = tk.Label(sub_window)
    img_label.pack()

    # Asignar el label a la ventana
    sub_window.img_label = img_label

    # Iniciar la captura de video en un hilo
    video_thread = threading.Thread(target=video_stream, args=(sub_window, stop_event))
    video_thread.start()

    # Función para manejar el cierre de la ventana
    def on_closing():
        stop_event.set()  # Detener el hilo
        sub_window.destroy()  # Cerrar la subventana

    # Asignar el manejador de cierre
    sub_window.protocol("WM_DELETE_WINDOW", on_closing)

    # Esperar hasta que se detenga el evento
    video_thread.join()  # Esperar a que el hilo de video termine antes de salir

# Aquí puedes definir otras funciones relevantes para tu aplicación

# Si necesitas ejecutar este archivo directamente, puedes agregar un bloque como este:
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal, si no la necesitas

    stop_event = threading.Event()
    up_method = "Cabeza"  # Cambia esto según lo que necesites
    down_method = "Cabeza"  # Cambia esto según lo que necesites

    camera_thread = threading.Thread(target=run_virtual_steering, args=(up_method, down_method, stop_event))
    camera_thread.start()

    # Simula un tiempo de espera para demostrar que el hilo está funcionando
    time.sleep(10)

    # Detener la cámara después de un tiempo
    stop_event.set()
    camera_thread.join()
    print("El hilo de la cámara ha finalizado.")
