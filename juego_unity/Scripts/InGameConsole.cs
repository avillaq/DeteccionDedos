using UnityEngine;
using System.Collections.Generic;

public class InGameConsole : MonoBehaviour
{
    private List<string> logMessages = new List<string>();
    private bool showConsole = true;
    private Vector2 scrollPosition;

    void OnEnable()
    {
        logMessages.Clear();  // Limpiar la lista de mensajes al habilitar el componente
        Application.logMessageReceived += HandleLog;
    }

    void OnDisable()
    {
        Application.logMessageReceived -= HandleLog;
    }

    private void HandleLog(string logString, string stackTrace, LogType type)
    {
        logMessages.Add(logString);
        if (logMessages.Count > 100)  // Limitar a 100 mensajes para evitar sobrecarga
        {
            logMessages.RemoveAt(0);
        }
    }

    void OnGUI()
    {
        if (showConsole)
        {
            GUI.backgroundColor = Color.black;
            scrollPosition = GUILayout.BeginScrollView(scrollPosition, GUILayout.Width(500), GUILayout.Height(300));
            foreach (string log in logMessages)
            {
                GUILayout.Label(log);
            }
            GUILayout.EndScrollView();
        }

        if (GUILayout.Button("Mostrar/Ocultar Consola", GUILayout.Width(150)))
        {
            showConsole = !showConsole;
        }
    }
}

