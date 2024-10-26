import cv2
import mediapipe as mp
from pynput.keyboard import Controller as KeyboardController, Key
import time

# Inicializar el módulo de manos de Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Entrada de la cámara web
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

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

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("No se pudo capturar un fotograma de la cámara.")
            continue

        # Voltear la imagen horizontalmente
        image = cv2.flip(image, 1)
        height, width, _ = image.shape

        # Convertir la imagen a RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        # Convertir la imagen de nuevo a BGR
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        action_text = "Centrado"
        hand_positions = {}

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
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
                    action_text = "Mover a la derecha (Mano izquierda más alta)"
                    
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
                    action_text = "Mover a la izquierda (Mano derecha más alta)"
                    
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

        else:
            # Si no se detectan manos, resetea el estado
            if is_pressed:
                keyboard.release(Key.left) if last_action == "Izquierda" else keyboard.release(Key.right)
                is_pressed = False

        # Mostrar imagen
        cv2.imshow("Volante Virtual", image)

        if cv2.waitKey(10) & 0xFF == 27:  # Presionar 'ESC' para salir
            break

cap.release()
cv2.destroyAllWindows()
