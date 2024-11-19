using UnityEngine;

public class AutoRotation : MonoBehaviour
{
    public float rotationSpeed = 50f; // Velocidad de rotación

    void Update()
    {
        // Rota el objeto continuamente alrededor del eje Y
        transform.Rotate(Vector3.up, rotationSpeed * Time.deltaTime);
    }
}

