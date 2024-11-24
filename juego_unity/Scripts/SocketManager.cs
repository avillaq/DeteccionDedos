using UnityEngine;
using UnityEngine.UI;
using System;
using System.Collections.Generic;
using SocketIOClient;
using System.Collections.Concurrent;
using System.Linq;

public class SocketManager : MonoBehaviour
{
    public GameObject carPrefab_local_az;
    public GameObject carPrefab_local_ro;
    public GameObject carPrefab_local_am;
    public GameObject carPrefab_az;
    public GameObject carPrefab_ro;
    public GameObject carPrefab_am;
    public InputField playerNameInput;
    private string playerName = "Player";
    private SocketIOClient.SocketIO socket;
    private Queue<Action> actionsToExecute = new Queue<Action>();
    private Dictionary<string, GameObject> players = new Dictionary<string, GameObject>();
    private float lastSentTime;

    private readonly ConcurrentQueue<Action> mainThreadActions = new ConcurrentQueue<Action>();
    private string id_local = "";
    private float post_count = 0f;
    private string color_local  = "azul";
    /*
    async void Start()
    {
        var uri = new Uri("http://localhost:3020");

        try
        {
            socket = new SocketIOClient.SocketIO(uri, new SocketIOOptions
            {
                Query = new Dictionary<string, string> { { "token", "UNITY" } },
                Transport = SocketIOClient.Transport.TransportProtocol.WebSocket
            });

            socket.OnConnected += OnConnect;
            socket.OnDisconnected += OnDisconnect;
            socket.OnError += OnError;

            socket.On("assignPlayerID", OnAssignPlayerID);
            socket.On("waitingForPlayers", WaitingForPlayers);
            socket.On("startRace", StartRace);
            socket.On("initialize", OnInitializePlayers);
            socket.On("updatePlayers", OnUpdatePlayers);

            Debug.Log("Intentando conectar al servidor...");
            await socket.ConnectAsync();
            Debug.Log("Conexión exitosa.");
        }
        catch (Exception ex)
        {
            Debug.LogError($"Error al intentar conectar: {ex.Message}");
        }
    }
    */
    public async void ConnectToServer(string networkIP, string color_auto)
    {
        var uri = new Uri($"http://{networkIP}");
        color_local = color_auto;
        try
        {
            socket = new SocketIOClient.SocketIO(uri, new SocketIOOptions
            {
                Query = new Dictionary<string, string> { { "token", "UNITY" } },
                Transport = SocketIOClient.Transport.TransportProtocol.WebSocket
            });

            socket.OnConnected += OnConnect;
            socket.OnDisconnected += OnDisconnect;
            socket.OnError += OnError;

            socket.On("assignPlayerID", OnAssignPlayerID);
            socket.On("waitingForPlayers", WaitingForPlayers);
            socket.On("initialize", OnInitializePlayers);
            socket.On("updatePlayers", OnUpdatePlayers);

            Debug.Log("Intentando conectar al servidor...");
            await socket.ConnectAsync();
            Debug.Log("Conexión exitosa.");
        }
        catch (Exception ex)
        {
            Debug.LogError($"Error al intentar conectar: {ex.Message}");
        }
    }

    // Recibir mensaje que estamos esperando jugadores
    private void WaitingForPlayers(SocketIOClient.SocketIOResponse response)
    {
        Debug.Log("Esperando");
    }

    private void OnConnect(object sender, EventArgs e)
    {
        try
        {
            Debug.Log("Conectado al servidor exitosamente.");
            /*
            // Asignar un nombre fijo para el jugador, si no se necesita input del jugador
            string playerName = "Player";  // O cualquier otro nombre fijo que prefieras

            // Emite los eventos a traves del socket
            socket.EmitAsync("playerJoined", new { name = playerName });
            socket.EmitAsync("initialize", new { });*/
        }
        catch (Exception ex)
        {
            // Si ocurre algun error, se captura y se muestra en el log de errores
            Debug.LogError($"Error en OnConnect: {ex.Message}");
        }
    }

    private void OnDisconnect(object sender, string reason)
    {
        Debug.LogWarning($"Desconectado del servidor: {reason}");
    }

    private void OnError(object sender, string error)
    {
        Debug.LogError($"Error de conexión: {error}");
    }

    private void OnAssignPlayerID(SocketIOClient.SocketIOResponse response)
    {
        try
        {
            string playerID = response.GetValue<string>(); // Esto directamente obtiene el valor de tipo string
            Debug.Log("Tu PlayerID es: " + playerID);
            // Asignar el ID a una variable local para usarlo mas adelante
            id_local = playerID;

            // Emitir el color del auto al servidor
            socket.EmitAsync("updateColor", new
            {
                playerID = id_local,  // Enviar el PlayerID
                color_car = color_local // Enviar el color seleccionado
            });
        }
        catch (Exception ex)
        {
            Debug.LogError($"Error al manejar 'assignPlayerID': {ex.Message}");
        }
    }

    private void OnInitializePlayers(SocketIOClient.SocketIOResponse response)
    {
        Debug.Log("Inicializando jugadores...");

        // Extraer el contenido bajo la clave "players"
        var playersRoot = response.GetValue<Dictionary<string, Dictionary<string, PlayerData>>>();
        if (playersRoot == null || !playersRoot.TryGetValue("players", out var playersData))
        {
            Debug.LogError("Los datos de los jugadores están vacíos o son nulos.");
            return;
        }

        Debug.Log("Encolando la acción de creación/actualización de jugadores...");
        
        EnqueueAction(() =>
        {
            Debug.Log("Ejecutando la acción en el hilo principal...");
            foreach (var player in playersData)
            {
                Debug.Log($"Player Key: {player.Key}, Player Value: {player.Value}");
                CreateOrUpdatePlayer(player.Key, player.Value,0);
            }
        });
    }



    private void OnUpdatePlayers(SocketIOClient.SocketIOResponse response)
    {
        EnqueueAction(() =>
        {
            var playersData = response.GetValue<Dictionary<string, PlayerData>>();
            if (playersData != null && playersData.Count > 0)
            {
                foreach (var player in playersData)
                {
                    CreateOrUpdatePlayer(player.Key, player.Value, 1);
                }
            }
            else
            {
                Debug.Log("playersData está vacío o es nulo.");
            }
        });
    }
  
    private void CreateOrUpdatePlayer(string playerId, PlayerData playerData, int estado)
    {
        Debug.Log($"playerId = {playerId} - id_local = {id_local}");
        if(estado == 1)
        {
            // Si el jugador ya existe y es diferente del jugador local, actualizamos su posicion y rotacion
            if (players.ContainsKey(playerId))
            {
                if(playerId != id_local)
                {
                var existingPlayer = players[playerId];
                existingPlayer.transform.position = new Vector3(playerData.x, playerData.y, playerData.z);
                existingPlayer.transform.rotation = Quaternion.Euler(playerData.rotationX, playerData.rotationY, playerData.rotationZ);
                Debug.Log($"Jugador de create {playerId}: Posición = {existingPlayer.transform.position}, Rotación = {existingPlayer.transform.rotation.eulerAngles}");
                }
            }
        }
       if(estado == 0)  // estado para crear autosjugadores
       {

            // Crear un nuevo GameObject independiente para el nuevo jugador
            GameObject newPlayer = null; 
            if (playerId == id_local)
            {   
                switch (color_local)
                {
                    case "azul":
                        newPlayer = Instantiate(carPrefab_local_az);
                        Debug.Log($"Instanciando prefab local {id_local} en color azul");
                        break;
                    case "rojo":
                        newPlayer = Instantiate(carPrefab_local_ro);
                        Debug.Log($"Instanciando prefab local {id_local} en color rojo");
                        break;
                    case "amarillo":
                        newPlayer = Instantiate(carPrefab_local_am);
                        Debug.Log($"Instanciando prefab local {id_local} en color amarillo");
                        break;
                    default:
                        Debug.LogWarning($"Color local desconocido: {color_local}");
                        break;
                }
                
            }
            else
            {
             switch (playerData.color_car)
                {
                    case "azul":
                        newPlayer = Instantiate(carPrefab_az);
                        Debug.Log($"Instanciando prefab otro jugador en color azul");
                        break;
                    case "rojo":
                        newPlayer = Instantiate(carPrefab_ro);
                        Debug.Log($"Instanciando prefab otro jugador en color rojo");
                        break;
                    case "amarillo":
                        newPlayer = Instantiate(carPrefab_am);
                        Debug.Log($"Instanciando prefab otro jugador en color amarillo");
                        break;
                    default:
                        Debug.LogWarning($"Color desconocido: {playerData.color_car}");
                        break;
                }
            }


            Vector3 initialPosition = newPlayer.transform.position;
            newPlayer.transform.position = new Vector3(initialPosition.x + post_count, initialPosition.y, initialPosition.z);
            players.Add(playerId, newPlayer);
            Debug.Log($"Nuevo jugador {playerId} post_count = {post_count} creado: Posición = {newPlayer.transform.position}, Rotación = {newPlayer.transform.rotation.eulerAngles}, Escala = {newPlayer.transform.localScale}");
            // Asignar una camara especifica al nuevo jugador
            Camera playerCamera = newPlayer.GetComponentInChildren<Camera>();
            if (playerCamera != null)
            {
                playerCamera.enabled = true;
            }
            post_count -= 10;  // Decrementa post_count en 10
        }
    }

    void Update()
    {
        while (mainThreadActions.TryDequeue(out var action))
        {
            action?.Invoke();
        }
    }

    void EnqueueAction(Action action)
    {
        mainThreadActions.Enqueue(action);
    }

    public void UpdatePosition(float x, float y, float z, float rotationX, float rotationY, float rotationZ)
    {
        // Convertimos los datos a un objeto JSON o similar para enviar la posicion y rotacion
        var positionData = new
        {
            x = x,
            y = y,
            z = z,
            rotationX = rotationX,
            rotationY = rotationY,
            rotationZ = rotationZ
        };

        // Enviar los datos al servidor mediante el socket
        socket.EmitAsync("updatePosition", positionData);
 
    }

    public void DisconnectSocket()
    {
        if (socket != null)
        {
            Debug.Log("Desconectando del servidor...");
            socket.DisconnectAsync();
        }
        else
        {
            Debug.LogWarning("El socket no está inicializado, no se puede desconectar.");
        }
    }

    void OnApplicationQuit()
    {
        DisconnectSocket();
    }

    [Serializable]
    public class PlayerData
    {
        public float x { get; set; }
        public float y { get; set; }
        public float z { get; set; }
        public float scaleX { get; set; }
        public float scaleY { get; set; }
        public float scaleZ { get; set; }
        public float rotationX { get; set; }  
        public float rotationY { get; set; }
        public float rotationZ { get; set; }
        public string color_car { get; set; }
    }
}

