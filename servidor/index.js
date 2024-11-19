const express = require('express');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

let players = {}; // Almacenamos los jugadores conectados
let waitingForPlayers = []; // Lista de jugadores esperando
let maxPlayers = 2; // Define el número máximo de jugadores
let playerCount = 0; // Contador de jugadores

app.get('/', (req, res) => {
    res.send('Servidor en ejecución');
});

// Ruta para obtener la lista de jugadores
app.get('/getPlayers', (req, res) => {
    // Crear una nueva estructura que incluya el ID en los datos del jugador
    const playersWithID = Object.keys(players).map(playerID => {
        return {
            id: playerID,  // Usar socket.id como ID del jugador
            ...players[playerID]  // Agregar los demás datos del jugador (nombre, posición, etc.)
        };
    });
    res.json(playersWithID);  // Devolver los jugadores con su ID incluido
});

// Manejo de la conexión de un jugador
io.on('connection', (socket) => {
    console.log('Jugador conectado: ' + socket.id);

    const pID = `PlayerID${playerCount++}`;
    players[pID] = {
        socketId: socket.id
    };
    
    // Emitir la lista de jugadores a todos los clientes
    console.log("Datos del jugador:", JSON.stringify(players));
    // Enviar al jugador recién conectado su playerID
    socket.emit('assignPlayerID', pID);
    
    waitingForPlayers.push(pID);

    // Enviar mensaje a todos los clientes diciendo que hay un nuevo jugador
    io.emit('playerJoined', { players });

    // Si todos los jugadores están conectados, inicia el juego
    if (waitingForPlayers.length === maxPlayers) {
        console.log('Todos los jugadores están conectados. Iniciando la carrera...');
        io.emit('startRace', { message: '¡La carrera ha comenzado!' });

        // Enviar a todos los jugadores los datos para sincronizar la carrera
        //io.emit('initializePlayers', { players });
        io.emit('initialize', { players });

        // Limpiar la lista de jugadores esperando
        waitingForPlayers = [];
    } else {
        // Si no todos los jugadores están conectados, mandar un mensaje de espera
        socket.emit('waitingForPlayers', {
            message: `Esperando a otros jugadores... Quedan ${maxPlayers - waitingForPlayers.length} jugadores.`,
        });
    }

    

    // Recibir la actualización de la posición de un jugador
    socket.on('updatePosition', (data) => {
        console.log("Datos recibidos en updatePosition:", JSON.stringify(data));
        let playerID = null;
        const t_socket = socket.id;
        console.log('Jugador conectado: ' + t_socket);
        for (let id in players) {
            console.log("id",players[id].socketId);
            if (players[id].socketId === t_socket) {
                console.log("id dentro del bucle",id);
                playerID = id;
                // Actualizamos la posición en los ejes X, Y y Z
                if (data.x !== undefined) players[playerID].x = data.x;
                if (data.y !== undefined) players[playerID].y = data.y;
                if (data.z !== undefined) players[playerID].z = data.z;
        
                // Actualizamos la rotación en los ejes X, Y y Z
                if (data.rotationX !== undefined) players[playerID].rotationX = data.rotationX;
                if (data.rotationY !== undefined) players[playerID].rotationY = data.rotationY;
                if (data.rotationZ !== undefined) players[playerID].rotationZ = data.rotationZ;
        
                // Mostrar la posición y rotación en la consola para depuración
                console.log(`Posición de ${playerID}: x = ${players[playerID].x}, y = ${players[playerID].y}, z = ${players[playerID].z}`);
                console.log(`Rotación de ${playerID}: rotationX = ${players[playerID].rotationX}, rotationY = ${players[playerID].rotationY}, rotationZ = ${players[playerID].rotationZ}`);
        
                // Emitir la lista actualizada de jugadores a todos los clientes
                io.emit('updatePlayers', players);
            }
        }
    });

    // Manejar desconexión de un jugador
    socket.on('disconnect', (reason) => {
        console.log(`Jugador desconectado: ${socket.id}, Motivo: ${reason}`);
        delete players[pID];
        io.emit('updatePlayers', players); // Emitir la lista actualizada
    });
});

// Iniciar el servidor en el puerto 3020
server.listen(3020, '0.0.0.0', () => {
    console.log('Servidor ejecutándose en http://0.0.0.0:3020');
});

