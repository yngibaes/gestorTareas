CREATE DATABASE GestionTareas;
USE GestionTareas;
CREATE TABLE Tareas (
    idTareas INT AUTO_INCREMENT PRIMARY KEY,
    nombreTar VARCHAR(200) NOT NULL,
    fechaInicio DATE,
    fechaFin DATE,
    estadoTar VARCHAR(45),
    fkUsuario INT
);

CREATE TABLE Usuario (
    idUsuario INT AUTO_INCREMENT PRIMARY KEY,
    nombreUsu VARCHAR(30) NOT NULL,
    apellidoUsu VARCHAR(30) NOT NULL,
    emailUsu VARCHAR(45) NOT NULL,
    usuarioUsu VARCHAR(45) NOT NULL,
    contraUsu VARCHAR(255) NOT NULL,
    rolUsu VARCHAR(15) NOT NULL
);

ALTER TABLE Tareas
ADD FOREIGN KEY (fkUsuario) REFERENCES Usuario(idUsuario);
DEFAULT CHARACTER SET = 'utf8mb4';