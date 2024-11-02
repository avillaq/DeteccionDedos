import cv2
import mediapipe as mp
from pynput.keyboard import Controller as KeyboardController, Key
import time
import threading

stop_event = threading.Event()

def run_virtual_steering(up_method, down_method, stop_event):
    
    try:
        # Inicializar el módulo de manos de Mediapipe
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        mp_face_detection = mp.solutions.face_detection

        # Entrada de la cámara web
        global cap
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("Error: No se pudo abrir la cámara.")
            return  # O lanza una excepción si prefieres
        #cap.set(cv2.CAP_PROP_EXPOSURE, -2) 
        #cap.set(cv2.CAP_PROP_FPS, 15)  # Prueba reducir la tasa de fotogramas
        keyboard = KeyboardController()

        # Variables para el seguimiento de la posición del volante
        steering_sensitivity = 0.5
        previous_angle = 0
        angle_threshold = 0.05

        # Variables para controlar la presión de las teclas
        is_pressed = False
        press_start_time = 0
        last_action = None
        press_duration = 0

        # Variables para el control de movimiento basado en distancia de la cara
        last_distance = None
        distance_threshold = 5

        with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands, \
            mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
            
            while not stop_event.is_set():
                success, image = cap.read()
                if not success:
                    print("No se pudo capturar un fotograma de la cámara.")
                    break

                # Voltear la imagen horizontalmente
                image = cv2.flip(image, 1)
                height, width, _ = image.shape

                # Convertir la imagen a RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                hand_results = hands.process(image_rgb)
                hand2_results = hands.process(image_rgb)
                face_results = face_detection.process(image_rgb)

                # Convertir la imagen de nuevo a BGR
                image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

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
                        cv2.circle(image, hand_pixel, 10, (255, 0, 0), -1)  # Punto azul para cada mano

                        # Dibujar la mano con conexiones
                        mp_drawing.draw_landmarks(
                            image,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2))

                    # Si ambas manos están detectadas, comparar sus posiciones en el eje Y
                    if "Derecha" in hand_positions and "Izquierda" in hand_positions:
                        right_y = hand_positions["Derecha"][1]
                        left_y = hand_positions["Izquierda"][1]

                        # Control del movimiento basado en la posición Y
                        tolerancia = 0.2
                        
                        if right_y < left_y - tolerancia:  # Mano derecha mas arriba que la izquierda
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
                            
                        elif left_y < right_y - tolerancia:  # Mano izquierda mas arriba que la derecha
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
                            cv2.putText(image, f"Tiempo {last_action}: {press_duration:.2f}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                        # Centro entre ambas manos
                        center_x = (hand_positions["Derecha"][0] + hand_positions["Izquierda"][0]) / 2
                        center_y = (hand_positions["Derecha"][1] + hand_positions["Izquierda"][1]) / 2
                        center_pixel = (int(center_x * width), int(center_y * height))

                        # Dibujar el punto central entre ambas manos
                        cv2.circle(image, center_pixel, 10, (0, 255, 0), -1)  # Punto verde para el centro

                    # Mostrar el texto de acción
                    action_position = ((width - cv2.getTextSize(action_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0][0]) // 2, 140)
                    cv2.putText(image, action_text, action_position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                

                # Detección de la distancia de la cara y control de movimiento vertical
                if face_results.detections:
                    for detection in face_results.detections:
                        # Dibujar la caja de la cara
                        bbox = detection.location_data.relative_bounding_box
                        left = int(bbox.xmin * width)
                        top = int(bbox.ymin * height)
                        right = left + int(bbox.width * width)
                        bottom = top + int(bbox.height * height)
                        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)

                        # Calcular la distancia de la cara
                        current_distance = bbox.width * bbox.height  # Área de la caja de la cara como medida de cercanía

                        if last_distance is not None:
                            if current_distance > last_distance * (1 + distance_threshold):  # Acercarse a la cámara
                                if up_method == "Cabeza":
                                    keyboard.press(Key.up)
                                    keyboard.release(Key.down)
                                    last_action = "Acercando"
                                    action_text = "Acercando (Presionando tecla arriba)"
                                elif up_method == "Mano":
                                    # Lógica para las manos, si se desea, puede incluirse aquí
                                    pass  # Reemplaza con la lógica deseada

                            elif current_distance < last_distance * (1 - distance_threshold):  # Alejarse de la cámara
                                if down_method == "Cabeza":
                                    keyboard.press(Key.down)
                                    keyboard.release(Key.up)
                                    last_action = "Alejando"
                                    action_text = "Alejando (Presionando tecla abajo)"
                                elif down_method == "Mano":
                                    # Lógica para las manos, si se desea, puede incluirse aquí
                                    pass  # Reemplaza con la lógica deseada

                            else:
                                keyboard.release(Key.up)
                                keyboard.release(Key.down)

                        last_distance = current_distance

                # Detección de manos
                if hand2_results.multi_hand_landmarks:
                    for hand_landmarks in hand2_results.multi_hand_landmarks:
                        # Calcular la posición de la mano (puedes ajustar estos valores)
                        finger_positions = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
                        
                        # Suponemos que el gesto de puño es cuando el dedo índice está completamente abajo
                        if finger_positions[mp_hands.HandLandmark.INDEX_FINGER_TIP.value][1] > finger_positions[mp_hands.HandLandmark.WRIST.value][1]:  # Puño
                            if up_method == "Mano":  # Solo si se seleccionó control con la mano
                                keyboard.press(Key.up)  # Acelerar
                                keyboard.release(Key.down)
                                last_action = "Acelerando"
                                action_text = "Acelerando (Presionando tecla arriba)"
                        elif finger_positions[mp_hands.HandLandmark.INDEX_FINGER_TIP.value][1] < finger_positions[mp_hands.HandLandmark.WRIST.value][1]:  # Mano extendida
                            if down_method == "Mano":  # Solo si se seleccionó control con la mano
                                keyboard.press(Key.down)  # Desacelerar
                                keyboard.release(Key.up)
                                last_action = "Desacelerando"
                                action_text = "Desacelerando (Presionando tecla abajo)"
                        else:
                            keyboard.release(Key.up)
                            keyboard.release(Key.down)

                else:
                    # Si no se detectan manos ni cara, resetear el estado
                    if is_pressed:
                        keyboard.release(Key.left) if last_action == "Izquierda" else keyboard.release(Key.right)
                        is_pressed = False
                    cv2.putText(image, "Camara no detectada", (10, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Mostrar imagen
                cv2.imshow("Volante Virtual", image)

                if cv2.getWindowProperty("Volante Virtual", cv2.WND_PROP_VISIBLE) < 1:  # Ventana cerrada
                    
                    print("cerraste la ventana")
                    close_camera()
                    break  # Sale del bucle de inmediato
                    

                if cv2.waitKey(10) & 0xFF == 27:  # ESC presionado
                    close_camera()
                    print("cerraste con ESC")
                    break  # Sale del bucle de inmediato

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Recursos liberados y ventanas cerradas.")
    time.sleep(0.1) 

def close_camera():
    global cap, stop_event

    if cap is not None and cap.isOpened():
        cap.release()  # Libera la cámara
        print("Cámara liberada.")

    cv2.destroyAllWindows()  # Cierra todas las ventanas de OpenCV
    print("Ventanas de OpenCV cerradas.")
    
    # Verifica si el evento existe antes de detener el hilo
    if stop_event is not None:
        stop_event.set()  # Detiene el hilo
        print("Hilo de cámara detenido.")
    
    # Reset variables
    cap = None
