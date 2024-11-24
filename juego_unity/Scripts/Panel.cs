using UnityEngine;
using UnityEngine.UI;

public class Panel : MonoBehaviour
{
    public GameObject mainMenuPanel;  // Panel del menu principal
    public GameObject optionsPanel;  // Panel de opciones
    public GameObject carSelectionPanel; // Panel para seleccionar autos
    public InputField networkInputField; // Campo para ingresar la red
    public SocketManager socketManager; // Referencia a SocketManager

    private string networkIP = "localhost"; // Valor por defecto
    private string color_auto = "azul"; 

    void Start()
    {
        // Mostrar el menu principal al iniciar
        ShowMainMenu();
    }

    public void play()
    {
        // Asegurate de que se haya ingresado una IP antes de intentar conectar
        networkIP = networkInputField.text;

        if (string.IsNullOrEmpty(networkIP))
        {
            Debug.LogError("No se ingresó una IP válida.");
            return;
        }

        if (socketManager != null)
        {
            Debug.Log($"Intentando conectar a {networkIP}");
            socketManager.ConnectToServer(networkIP,color_auto); // Pasar la IP al SocketManager
            mainMenuPanel.SetActive(false);
            optionsPanel.SetActive(false);
            carSelectionPanel.SetActive(false);
        }
        else
        {
            Debug.LogError("SocketManager no está configurado.");
        }
    }

    public void ShowMainMenu()
    {
        mainMenuPanel.SetActive(true);
        optionsPanel.SetActive(false);
        carSelectionPanel.SetActive(false);
    }

    public void ShowOptionsMenu()
    {
        mainMenuPanel.SetActive(false);
        carSelectionPanel.SetActive(false);
        optionsPanel.SetActive(true);
    }

    public void SaveNetworkSettings()
    {
        // Guarda la IP ingresada
        networkIP = networkInputField.text;
        Debug.Log($"IP guardada: {networkIP}");
    }

    public void ShowOptionsCarMenu()
    {
        mainMenuPanel.SetActive(false);
        optionsPanel.SetActive(false);
        carSelectionPanel.SetActive(true);
    }

    public void SetCarColor(Button clickedButton)
    {
        // Obtiene el texto del boton clicado y lo guarda en color_auto
        color_auto = clickedButton.GetComponentInChildren<Text>().text;
        Debug.Log($"Color seleccionado: {color_auto}");
        ShowMainMenu();
    }

    public void ExitGame()
    {
        Debug.Log("Saliendo del juego...");
        Application.Quit(); // Salir de la aplicacion
    }
}
