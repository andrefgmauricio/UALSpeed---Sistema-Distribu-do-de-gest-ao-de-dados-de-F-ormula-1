CREATE DATABASE IF NOT EXISTS ualspeed;
USE ualspeed;


CREATE TABLE IF NOT EXISTS equipas(
    id INT ANTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    nacionalidade VARCHAR(50)
);


CREATE TABLE IF NOT EXISTS pilotos(
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    numero INT NOT NULL UNIQUE,
    nacionalidade VARCHAR(50),
    equipa_id INT,
    FOREIGN KEY (equipa_id) REFERENCES equipas(id) ON DELETE SET NULL
);



CREATE TABLE IF NOT EXISTS telemetria (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    piloto_id INT NOT NULL,
    velocidade INT NOT NULL,
    rpm INT NOT NULL,
    posicao_pista INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (piloto_id) REFERENCES pilotos(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXIST resultados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    piloto_id INT NOT NULL,
    voltas_completas INT DEFAULT 0,
    melhor_volta TIME,
    tempo_total VARCHAR(50),
    pontos_ganhos INT DEFAULT 0,
    FOREIGN KEY (piloto_id) REFERENCES piloto(id) ON DELETE CASCADE
);