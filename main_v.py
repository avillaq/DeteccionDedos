import cv2
import mediapipe as mp
from pynput.keyboard import Controller as KeyboardController, Key
import time

# Initialize Mediapipe hands module
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# For webcam input:
cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Usa DirectShow como backend en lugar de MSMF

keyboard = KeyboardController()

# Variables para el seguimiento de la posición del volante
steering_sensitivity = 0.5  # Sensibilidad del giro
center_position = 0  # Centro del volante
previous_angle = 0  # Último ángulo calculado

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
    
    while cap.isOpened():
        # Read a frame from the camera
        success, image = cap.read()
        if not success:
            print("Unable to capture a frame from the camera.")
            continue

        # Flip the image horizontally
        image = cv2.flip(image, 1)

        # Convert image to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image with Mediapipe hands
        results = hands.process(image_rgb)

        # Convert image back to BGR
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            # Si hay al menos una mano detectada, obtenemos las posiciones de los puntos
            for hand_landmarks in results.multi_hand_landmarks:
                handLandmarks = [[landmark.x, landmark.y] for landmark in hand_landmarks.landmark]

                # Posición de las dos manos en el eje X
                hand_x_position = handLandmarks[9][0]  # Usamos el punto 9 como referencia del centro de la mano

                # Calculamos el ángulo del "volante" basado en la posición relativa al centro de la pantalla
                # (hand_x_position es un valor entre 0 y 1)
                current_angle = (hand_x_position - 0.5) * 2 * steering_sensitivity

                # Comparamos el ángulo actual con el anterior para mover el volante
                if current_angle < previous_angle - 0.1:  # Si el ángulo es menor, movemos a la izquierda
                    keyboard.press(Key.right)
                    time.sleep(0.1)
                    keyboard.release(Key.right)
                    action_text = "Move right"
                elif current_angle > previous_angle + 0.1:  # Si el ángulo es mayor, movemos a la derecha
                    keyboard.press(Key.left)
                    time.sleep(0.1)
                    keyboard.release(Key.left)
                    action_text = "Move left"
                else:
                    action_text = "Centered"

                previous_angle = current_angle

                # Dibujamos los puntos clave en la mano
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2))

            # Mostramos el ángulo calculado y la acción
            height, width, _ = image.shape
            action_position = ((width - cv2.getTextSize(action_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0][0]) // 2, 140)
            cv2.putText(image, action_text, action_position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Display the image
        cv2.imshow("Virtual Steering Wheel", image)

        # Break the loop if 'Esc' key is pressed
        if cv2.waitKey(5) & 0xFF == 27:
            break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
