import cv2
import mediapipe as mp
import threading
import time
import tkinter as tk
from tkinter import Toplevel
from PIL import Image, ImageTk
from pynput.keyboard import Key, Controller

# Inicialización de MediaPipe y controlador de teclado
mp_hands = mp.solutions.hands
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
keyboard = Controller()

# Variables globales
camera_running = False
last_distance = None
is_pressed = False
last_action = ""
press_start_time = 0
press_duration = 0
distance_threshold = 0.2  # Ajusta el umbral de detección de distancia

# Función para capturar y mostrar video de la cámara
def video_stream(window, stop_event, up_method, down_method):
    global camera_running, last_distance, is_pressed, last_action, press_start_time, press_duration

    cap = cv2.VideoCapture(0)
    
    with mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands, \
         mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        
        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print("No se pudo capturar el video.")
                break

            # Procesamiento y detección de gestos
            frame = cv2.flip(frame, 1)
            height, width, _ = frame.shape
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hand_results = hands.process(image_rgb)
            face_results = face_detection.process(image_rgb)

            action_text = "Centrado"
            hand_positions = {}

            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    # Posición del punto central en cada mano (índice 9)
                    hand_x, hand_y = hand_landmarks.landmark[9].x, hand_landmarks.landmark[9].y
                    hand_pixel = (int(hand_x * width), int(hand_y * height))

                    # Identificar si la mano es izquierda o derecha
                    handedness = "Derecha" if hand_landmarks.landmark[0].x < 0.5 else "Izquierda"
                    hand_positions[handedness] = (hand_x, hand_y)

                    # Dibujar un punto en el centro de cada mano
                    cv2.circle(frame, hand_pixel, 10, (255, 0, 0), -1)  # Punto azul para cada mano

                    # Dibujar la mano con conexiones
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                        connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2))

                # Si ambas manos están detectadas, comparar sus posiciones en el eje Y
                if "Derecha" in hand_positions and "Izquierda" in hand_positions:
                    right_y = hand_positions["Derecha"][1]
                    left_y = hand_positions["Izquierda"][1]

                    # Control del movimiento basado en la posición Y
                    if right_y < left_y:  # Mano derecha más arriba que la izquierda
                        if is_pressed and last_action != "Derecha":
                            # Liberar tecla izquierda antes de presionar derecha
                            keyboard.release(Key.left)
                            is_pressed = False
                        if not is_pressed:
                            keyboard.press(Key.right)
                            press_start_time = time.time()
                            is_pressed = True
                            last_action = "Derecha"
                        action_text = "Mover a la derecha (Mano izquierda mas alta)"
                        
                    elif left_y < right_y:  # Mano izquierda más arriba que la derecha
                        if is_pressed and last_action != "Izquierda":
                            # Liberar tecla derecha antes de presionar izquierda
                            keyboard.release(Key.right)
                            is_pressed = False
                        if not is_pressed:
                            keyboard.press(Key.left)
                            press_start_time = time.time()
                            is_pressed = True
                            last_action = "Izquierda"
                        action_text = "Mover a la izquierda (Mano derecha mas alta)"
                        
                    else:  # Ninguna mano está arriba
                        if is_pressed:
                            # Liberar tecla si ambas manos están centradas
                            keyboard.release(Key.left if last_action == "Izquierda" else Key.right)
                            press_duration = time.time() - press_start_time
                            is_pressed = False

                    # Mostrar el tiempo de presión
                    if last_action:  # Solo mostrar si hubo una acción
                        cv2.putText(frame, f"Tiempo {last_action}: {press_duration:.2f}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                    # Centro entre ambas manos
                    center_x = (hand_positions["Derecha"][0] + hand_positions["Izquierda"][0]) / 2
                    center_y = (hand_positions["Derecha"][1] + hand_positions["Izquierda"][1]) / 2
                    center_pixel = (int(center_x * width), int(center_y * height))

                    # Dibujar el punto central entre ambas manos
                    cv2.circle(frame, center_pixel, 10, (0, 255, 0), -1)  # Punto verde para el centro

                # Mostrar el texto de acción
                action_position = ((width - cv2.getTextSize(action_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0][0]) // 2, 140)
                cv2.putText(frame, action_text, action_position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Detección de la distancia de la cara y control de movimiento vertical
            if face_results.detections:
                for detection in face_results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    left = int(bbox.xmin * width)
                    top = int(bbox.ymin * height)
                    right = left + int(bbox.width * width)
                    bottom = top + int(bbox.height * height)
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                    current_distance = bbox.width * bbox.height
                    if last_distance is not None:
                        if current_distance > last_distance * (1 + distance_threshold):
                            if up_method == "Cabeza":
                                keyboard.press(Key.up)
                                keyboard.release(Key.down)
                                last_action = "Acercando"
                                action_text = "Acercando (Presionando tecla arriba)"
                        elif current_distance < last_distance * (1 - distance_threshold):
                            if down_method == "Cabeza":
                                keyboard.press(Key.down)
                                keyboard.release(Key.up)
                                last_action = "Alejando"
                                action_text = "Alejando (Presionando tecla abajo)"
                        else:
                            keyboard.release(Key.up)
                            keyboard.release(Key.down)
                    last_distance = current_distance

            # Lógica de gestos de manos para control de movimiento vertical
            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    finger_positions = [(lm.x, lm.y) for lm in hand_landmarks.landmark]

                    index_finger_tip = finger_positions[mp_hands.HandLandmark.INDEX_FINGER_TIP.value]
                    wrist = finger_positions[mp_hands.HandLandmark.WRIST.value]
                    
                    if index_finger_tip[1] > wrist[1]:
                        if up_method == "Mano":
                            keyboard.press(Key.up)
                            keyboard.release(Key.down)
                            last_action = "Acelerando"
                            action_text = "Acelerando (Presionando tecla arriba)"
                    elif index_finger_tip[1] < wrist[1]:
                        if down_method == "Mano":
                            keyboard.press(Key.down)
                            keyboard.release(Key.up)
                            last_action = "Desacelerando"
                            action_text = "Desacelerando (Presionando tecla abajo)"
                    else:
                        keyboard.release(Key.up)
                        keyboard.release(Key.down)

            # Convertir el frame para Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((640, 480), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(image=img)

            if window.winfo_exists():
                window.img_label.configure(image=img_tk)
                window.img_label.image = img_tk

            window.update()

    cap.release()
    camera_running = False

# Función para iniciar el hilo de la cámara
def run_virtual_tk(up_method, down_method, stop_event):
    global camera_running

    if camera_running:
        print("La cámara ya está en ejecución.")
        return

    camera_running = True

    # Crear la subventana
    sub_window = Toplevel()
    sub_window.title("Cámara Real")
    sub_window.geometry("640x480")

    # Crear un label para mostrar el video
    img_label = tk.Label(sub_window)
    img_label.pack()
    sub_window.img_label = img_label

    # Iniciar la captura de video en un hilo
    video_thread = threading.Thread(target=video_stream, args=(sub_window, stop_event, up_method, down_method))
    video_thread.start()

    def on_closing():
        stop_event.set()
        sub_window.destroy()

    sub_window.protocol("WM_DELETE_WINDOW", on_closing)
    video_thread.join()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal

    stop_event = threading.Event()
    up_method = "Cabeza"
    down_method = "Cabeza"

    camera_thread = threading.Thread(target=run_virtual_tk, args=(up_method, down_method, stop_event))
    camera_thread.start()

    time.sleep(10)
    stop_event.set()
    camera_thread.join()
    print("El hilo de la cámara ha finalizado.")
