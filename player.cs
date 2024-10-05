using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class player : MonoBehaviour
{
    public float speed = 5.0f;
    public float turnSpeed = 50.0f;
    public float resetDistance = 10.0f; 
    public float uprightForce = 10.0f; // Fuerza para enderezar el carro
    public float accelerationSensitivity = 2.0f;  // para versión móvil

    public int lives = 3;
    public int points = 0;
    public Text pointsText; 
    public Text livesText; 

    public AudioSource accelerationSound;
    public AudioSource decelerationSound; // AudioSource para el sonido de desaceleración
    public AudioSource backgroundMusic; // AudioSource para el sonido de fondo

    private Vector3 initialPosition;
    private Rigidbody rb;

    private float currentSpeed = 0.0f;
    private bool useGestures = false; // Variable para controlar el modo de entrada
    public bool useAccelerometer;  //  Variable para controlar si se usa el acelerómetro en móvil

    void Start()
    {
        rb = GetComponent<Rigidbody>();
        initialPosition = transform.position;
        pointsText = GameObject.Find("Text_puntos").GetComponent<Text>();
        livesText = GameObject.Find("Text_vidas").GetComponent<Text>();
        UpdateUI();

        // Iniciar el sonido de fondo
        backgroundMusic.Play();

        // Detección automática de la plataforma
        if (Application.platform == RuntimePlatform.Android || Application.platform == RuntimePlatform.IPhonePlayer)
        {
            // Si está en móvil, se activa el uso del acelerómetro
            useAccelerometer = true;
        }
        else
        {
            // Si no está en móvil, desactivamos el acelerómetro
            useAccelerometer = false;
        }
    }

    void Update()
    {
        float horizontalInput = 0.0f;
        float verticalInput = 0.0f;

        // Alternar entre el control por teclado y el control por gestos
        if (Input.GetKeyDown(KeyCode.G))
        {
            useGestures = !useGestures; // Cambiar el modo de entrada
            Debug.Log("Modo de entrada cambiado a: " + (useGestures ? "Gestos" : "Teclado"));
        }

#if UNITY_EDITOR
        if (!useGestures)
        {
            // Control con teclas
            horizontalInput = Input.GetAxis("Horizontal");
            verticalInput = Input.GetAxis("Vertical");

            if (Input.GetKey(KeyCode.E))
            {
                transform.Rotate(Vector3.up * turnSpeed * Time.deltaTime);
            }
        }
#else
        // Caso 3: Móvil con acelerómetro
        if (useAccelerometer)
        {
            // Control con acelerómetro
            horizontalInput = Input.acceleration.x;
            // Ajusta verticalInput para hacer que 45 grados sea el punto neutral.
            float adjustedVertical = Input.acceleration.y - Mathf.Sin(Mathf.Deg2Rad * -45.0f);
            verticalInput = Mathf.Clamp(adjustedVertical * accelerationSensitivity, -1.0f, 1.0f);
        }
        else if (useGestures)
        {
            // Caso 4: PC/Móvil con gestos
            // Aquí iría tu lógica de detección de gestos fuera del editor
            horizontalInput = Input.GetAxis("Mouse X");  // Ejemplo de gesto basado en mouse
            verticalInput = Input.GetAxis("Mouse Y");
        }
        else
        {
            // Control con teclas (móvil/PC sin gestos ni acelerómetro)
            horizontalInput = Input.GetAxis("Horizontal");
            verticalInput = Input.GetAxis("Vertical");
        }
#endif

        float rotationAmount = horizontalInput * turnSpeed * Time.deltaTime;
        transform.Rotate(Vector3.up * rotationAmount);

        currentSpeed += verticalInput * speed * Time.deltaTime;
        currentSpeed = Mathf.Clamp(currentSpeed, -speed, speed);

        transform.Translate(Vector3.forward * currentSpeed * Time.deltaTime);

        if (currentSpeed > 0.1f)
        {
            // Reproducir el sonido de aceleración
            if (!accelerationSound.isPlaying)
            {
                accelerationSound.Play();
            }

            // Detener el sonido de desaceleración si está reproduciéndose
            if (decelerationSound.isPlaying)
            {
                decelerationSound.Stop();
            }
        }
        else if (currentSpeed < -0.1f)
        {
            // Reproducir el sonido de desaceleración
            if (!decelerationSound.isPlaying)
            {
                decelerationSound.Play();
            }

            // Detener el sonido de aceleración si está reproduciéndose
            if (accelerationSound.isPlaying)
            {
                accelerationSound.Stop();
            }
        }
        else
        {
            // Detener ambos sonidos si no hay aceleración ni desaceleración
            accelerationSound.Stop();
            decelerationSound.Stop();
        }

        if (transform.position.y < -50.0f)
        {
            ResetCarPosition();
            currentSpeed = 0.0f;
            lives--;
            UpdateUI();
        }

        if (IsCarFlipped())
        {
            RightCar();
        }

         if (Input.GetKeyDown(KeyCode.Escape))
         {
          // Presionó la tecla "Esc", cargamos la escena inicial
             SceneManager.LoadScene("MainMenu");
         }
    }

    void RightCar()
    {
        rb.AddForce(Vector3.up * uprightForce, ForceMode.Impulse);
    }

    bool IsCarFlipped()
    {
        return Vector3.Angle(Vector3.up, transform.up) > 90.0f;
    }

    void UpdateUI()
    {
        pointsText.text = "Puntos: " + points;
        livesText.text = "Vidas: " + lives;
    }

    void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.CompareTag("ObjetoColision"))
        {
            points -= 10;
            UpdateUI();

            if (points < 0)
            {
                points = 0;
            }

            if (points == 0)
            {
                if (lives > 0)
                {
                    lives--;
                    points = 100;
                }
                UpdateUI();

                if (lives <= 0)
                {
                    Debug.Log("Perdiste");
                }
                else
                {
                    ResetCarPosition();
                    currentSpeed = 0.0f;
                }
            }
        }
    }

    void ResetCarPosition()
    {
        transform.position = initialPosition;
        transform.rotation = Quaternion.identity;
    }
}
