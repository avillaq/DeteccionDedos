using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR;

public class FollowPlayer : MonoBehaviour
{
    public GameObject player;  // Referencia al jugador
    public float rotationSpeed = 2.0f; // Velocidad de rotación de la cámara
    [SerializeField] private Vector3 offset = new Vector3(0, 6, -7);  // Posición relativa de la cámara respecto al jugador, expuesto en el Inspector
    
    private bool isVR = false;

    void Start()
    {
        // Verificar si el dispositivo está en VR
        isVR = XRSettings.isDeviceActive;

        if (isVR)
        {
            // Si estamos en VR, deshabilitamos el script de seguimiento de cámara porque el XR Rig lo manejará
            this.enabled = false;
        }
    }

    void LateUpdate()
    {
        if (!isVR)
        {
            // Solo ejecutamos la lógica de cámara si no estamos en VR

            // Obtener la rotación horizontal del jugador
            float playerRotation = player.transform.eulerAngles.y;

            // Calcular la rotación para la cámara (girar horizontalmente con el jugador)
            Quaternion newRotation = Quaternion.Euler(0, playerRotation, 0);

            // Aplicar la rotación a la posición offset de la cámara
            Vector3 rotatedOffset = newRotation * offset;

            // Calcular la nueva posición de la cámara
            Vector3 newPosition = player.transform.position + rotatedOffset;

            // Interpolación suave para seguir al jugador
            transform.position = Vector3.Lerp(transform.position, newPosition, Time.deltaTime * rotationSpeed);

            // Mirar hacia el jugador desde la posición actual de la cámara
            transform.LookAt(player.transform.position);
        }
    }
}



