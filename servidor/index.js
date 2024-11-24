const express = require('express');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

let players = {}; // Almacenamos los jugadores conectados
let waitingForPlayers = []; // Lista de jugadores esperando
let maxPlayers = 2; // Define el numero maximo de jugadores
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
            ...players[playerID]  // Agregar los demas datos del jugador (nombre, posicion, etc.)
        };
    });
    res.json(playersWithID);  // Devolver los jugadores con su ID incluido
});

// Manejo de la conexion de un jugador
io.on('connection', (socket) => {
    console.log('Jugador conectado: ' + socket.id);

    const pID = `PlayerID${playerCount++}`;
    players[pID] = {
        socketId: socket.id,
        color_car: "azul", 
    };
    
    // Emitir la lista de jugadores a todos los clientes
    console.log("Datos del jugador:", JSON.stringify(players));
    // Enviar al jugador recien conectado su playerID
    socket.emit('assignPlayerID', pID);

    socket.on('updateColor', (data) => {
        const { playerID, color_car } = data;

        if (players[playerID]) {
            players[playerID].color_car = color_car;
            console.log(`Color actualizado para ${playerID}: ${color_car}`);

        } else {
            console.log(`Jugador no encontrado: ${playerID}`);
        }
    });

    waitingForPlayers.push(pID);

    // Si todos los jugadores estan conectados, inicia el juego
    if (waitingForPlayers.length === maxPlayers) {
        console.log('Todos los jugadores están conectados. Iniciando la carrera...');

        // Enviar a todos los jugadores los datos para sincronizar la carrera
        io.emit('initialize', { players });

        // Limpiar la lista de jugadores esperando
        waitingForPlayers = [];
    } else {
        // Si no todos los jugadores estan conectados, mandar un mensaje de espera
        socket.emit('waitingForPlayers', {
            message: `Esperando a otros jugadores... Quedan ${maxPlayers - waitingForPlayers.length} jugadores.`,
        });
    }

    // Recibir la actualizacion de la posicion de un jugador
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
                // Actualizamos la posicion en los ejes X, Y y Z
                if (data.x !== undefined) players[playerID].x = data.x;
                if (data.y !== undefined) players[playerID].y = data.y;
                if (data.z !== undefined) players[playerID].z = data.z;
        
                // Actualizamos la rotacion en los ejes X, Y y Z
                if (data.rotationX !== undefined) players[playerID].rotationX = data.rotationX;
                if (data.rotationY !== undefined) players[playerID].rotationY = data.rotationY;
                if (data.rotationZ !== undefined) players[playerID].rotationZ = data.rotationZ;
        
                // Mostrar la posicion y rotacion en la consola para depuracion
                console.log(`Posición de ${playerID}: x = ${players[playerID].x}, y = ${players[playerID].y}, z = ${players[playerID].z}`);
                console.log(`Rotación de ${playerID}: rotationX = ${players[playerID].rotationX}, rotationY = ${players[playerID].rotationY}, rotationZ = ${players[playerID].rotationZ}`);
        
                // Emitir la lista actualizada de jugadores a todos los clientes
                io.emit('updatePlayers', players);
            }
        }
    });

    // Manejar desconexion de un jugador
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

