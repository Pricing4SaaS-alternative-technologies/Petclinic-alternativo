-- Insert data into usuarios table
INSERT IGNORE INTO usuarios (id, nombre, apellidos, usuario, email, contraseña, tipo_usuario) VALUES
(1, 'Daniel','Benito','danbenhid', 'danbenhid@example.com', 'scrypt:32768:8:1$uh1IGF90LTfiEraD$58161931e2e2f229cd8b59b2d63820a2c50000b35faf63a0b54aa3225c6d5f74e3dbd89495fd0d011f5aa3a2cf7e89b4a22e24f923a6bd45074cefe125e2fb33', 'PROP_MASCOTA'),
(2, 'Fernando', 'De Celis','ferdehur', 'ferdehur@example.com', 'scrypt:32768:8:1$uh1IGF90LTfiEraD$58161931e2e2f229cd8b59b2d63820a2c50000b35faf63a0b54aa3225c6d5f74e3dbd89495fd0d011f5aa3a2cf7e89b4a22e24f923a6bd45074cefe125e2fb33', 'PROP_MASCOTA'),
(3, 'Pablo', 'Castellanos','pabcascom', 'pabcascom@example.com', 'scrypt:32768:8:1$uh1IGF90LTfiEraD$58161931e2e2f229cd8b59b2d63820a2c50000b35faf63a0b54aa3225c6d5f74e3dbd89495fd0d011f5aa3a2cf7e89b4a22e24f923a6bd45074cefe125e2fb33', 'PROP_MASCOTA'),
(4, 'Javier','Manrique','javmanriq', 'javmanriq@example.com', 'scrypt:32768:8:1$uh1IGF90LTfiEraD$58161931e2e2f229cd8b59b2d63820a2c50000b35faf63a0b54aa3225c6d5f74e3dbd89495fd0d011f5aa3a2cf7e89b4a22e24f923a6bd45074cefe125e2fb33', 'PROP_CLINICA'),
(5, 'Miguel', 'Hernández','mighersan1', 'mighersan1@example.com', 'scrypt:32768:8:1$uh1IGF90LTfiEraD$58161931e2e2f229cd8b59b2d63820a2c50000b35faf63a0b54aa3225c6d5f74e3dbd89495fd0d011f5aa3a2cf7e89b4a22e24f923a6bd45074cefe125e2fb33', 'PROP_CLINICA'),
(6, 'Gonzalo', 'Navas','gonnavrem', 'gonnavrem@example.com', 'scrypt:32768:8:1$uh1IGF90LTfiEraD$58161931e2e2f229cd8b59b2d63820a2c50000b35faf63a0b54aa3225c6d5f74e3dbd89495fd0d011f5aa3a2cf7e89b4a22e24f923a6bd45074cefe125e2fb33', 'PROP_CLINICA'),
(7, 'David', 'Godoy','davgodfer', 'davgodfer@example.com', 'scrypt:32768:8:1$uh1IGF90LTfiEraD$58161931e2e2f229cd8b59b2d63820a2c50000b35faf63a0b54aa3225c6d5f74e3dbd89495fd0d011f5aa3a2cf7e89b4a22e24f923a6bd45074cefe125e2fb33', 'VETERINARIO'),
(8, 'Sergio', 'Pons','serponlop', 'seponlop@example.com', 'scrypt:32768:8:1$uh1IGF90LTfiEraD$58161931e2e2f229cd8b59b2d63820a2c50000b35faf63a0b54aa3225c6d5f74e3dbd89495fd0d011f5aa3a2cf7e89b4a22e24f923a6bd45074cefe125e2fb33', 'VETERINARIO'),
(9, 'Hector', 'Noguera','hecnoggon', 'hecnorgon@example.com', 'scrypt:32768:8:1$uh1IGF90LTfiEraD$58161931e2e2f229cd8b59b2d63820a2c50000b35faf63a0b54aa3225c6d5f74e3dbd89495fd0d011f5aa3a2cf7e89b4a22e24f923a6bd45074cefe125e2fb33', 'VETERINARIO'),
(10, 'Admin', 'admin','admin', 'admin@example.com', 'scrypt:32768:8:1$uh1IGF90LTfiEraD$58161931e2e2f229cd8b59b2d63820a2c50000b35faf63a0b54aa3225c6d5f74e3dbd89495fd0d011f5aa3a2cf7e89b4a22e24f923a6bd45074cefe125e2fb33', 'ADMIN');

INSERT IGNORE INTO clinicas (id, nombre, direccion, telefono, plan, propietario_id) VALUES
(1, 'Clínica 1', 'Calle Veterinario 1', '954123456', 'BASIC', 4),
(2, 'Clínica 2', 'Calle Veterinario 2', '915123456', 'GOLD', 5),
(3, 'Clínica 3', 'Calle Veterinario 3', '934123456', 'PREMIUM', 6);

INSERT IGNORE INTO habitaciones_hotel (id, tamaño, tipo, clinica_id) VALUES
(1, 20, 'PERRO', 1),
(2, 30, 'GATO', 2),
(3, 35, 'PAJARO', 3);

INSERT IGNORE INTO mascotas (id, nombre, cumpleaños, tipo, dueño_id) VALUES
(1, 'Roco', '2020-01-01', 'PERRO', 1),
(2, 'Misifú', '2019-05-15', 'GATO', 2),
(3, 'Lorito', '2021-03-10', 'PAJARO', 3);

INSERT IGNORE INTO props_clinicas (id) VALUES
(1),
(2),
(3);

INSERT IGNORE INTO props_mascotas (id, direccion, telefono, clinica_id) VALUES
(1, 'Calle Falsa 123', '123456789', 1),
(2, 'Avenida Siempre Viva 742', '987654321', 2),
(3, 'Boulevard de los Sueños Rotos 456', '456789123', 3);

INSERT IGNORE INTO veterinarios (id, especialidades, ciudad, clinica_id) VALUES
(1, '["DERMATOLOGIA", "OFTALMOLOGIA"]', 'Sevilla', 1),
(2, '["CIRUGIA", "MEDICINA_INTERNA"]', 'Sevilla', 2),
(3, '["DERMATOLOGIA", "REHABILITACION"]', 'Sevilla', 3);

INSERT IGNORE INTO visitas (id, fecha, descripcion, veterinario_id, mascota_id) VALUES
(1, '2023-10-01 10:00:00', 'Consulta general', 1, 1),
(2, '2023-10-02 11:00:00', 'Chequeo de salud', 2, 2),
(3, '2023-10-03 12:00:00', 'Vacunación', 3, 3);

INSERT IGNORE INTO adopciones (id, descripcion, estado_adopcion, mascota_id, dueño_nuevo_id, dueño_anterior_id) VALUES
(1, 'Adopción de Misifú', 'PENDIENTE', 2, null, 2),
(2, 'Adopción de Lorito', 'APROBADA', 3, 1, 3);

INSERT IGNORE INTO consultas (id, titulo, descripcion, comentario_clinica, estado_consulta, dueño_id, vet_id, mascota_id) VALUES
(1, 'Consulta sobre la salud de Roco', 'Roco lleva varios días malo.' , TRUE, 'PENDIENTE', 1, null, 1),
(2, 'Consulta sobre la adopción de Misifú', '¿Cómo va la adopción?' , TRUE, 'RESUELTA', 2, null, 2),
(3, 'Consulta sobre la vacunación de Lorito', '¿Es monodosis o hay que poner la vacuna más veces?' , FALSE, 'CERRADA', 3, 3, 3);

INSERT IGNORE INTO reservas (id, fecha_inicio, fecha_fin, habitacion_id, mascota_id) VALUES
(1, '2023-10-01', '2023-10-05', 1, 1),
(2, '2023-10-02', '2023-10-06', 2, 2),
(3, '2023-10-03', '2023-10-07', 3, 3);