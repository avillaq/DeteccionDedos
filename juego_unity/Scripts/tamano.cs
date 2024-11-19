using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class tamano : MonoBehaviour
{
    public Text textPuntos;
    public Text textVidas;

    void Start()
    {
        // Obtener las dimensiones del mundo (en unidades del mundo)
        float worldWidth = Camera.main.orthographicSize * 2f * Camera.main.aspect;
        float worldHeight = Camera.main.orthographicSize * 2f;

        // Convertir 2 cm a unidades del mundo (ajustar según sea necesario)
        float marginInWorldUnits = 5 * 0.1f; // Suponiendo que 1 unidad del mundo es aproximadamente 1 metro

        // Calcular la posición vertical deseada con un margen superior de 5 cm desde el borde superior
        float yPos = worldHeight / 50 - marginInWorldUnits * 50;

        // Calcular el tamaño del texto en función del ancho del mundo
        float textSizeMultiplier = worldWidth / 15f; // Reduje el tamaño del texto a 15 unidades para dar más espacio

        // Ajustar el ancho del texto
        float textWidth = textPuntos.rectTransform.rect.width * textSizeMultiplier;

        // Ajustar la posición de textPuntos en la esquina superior derecha
        RectTransform rectTransformPuntos = textPuntos.rectTransform;
        rectTransformPuntos.anchoredPosition = new Vector2(worldWidth / 2 - textWidth, yPos);

        // Ajustar la posición de textVidas en la esquina superior izquierda
        RectTransform rectTransformVidas = textVidas.rectTransform;
        rectTransformVidas.anchoredPosition = new Vector2(-worldWidth / 2 + textWidth, yPos);
    }

    void Update()
    {
        // Puedes realizar actualizaciones adicionales en Update si es necesario
    }
}
