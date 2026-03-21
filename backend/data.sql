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
(10, 'Admin', 'admin','admin', 'admin@example.com', 'scrypt:32768:8:1$uh1IGF90LTfiEraD$58161931e2e2f229cd8b59b2d63820a2c50000b35faf63a0b54aa3225c6d5f74e3dbd89495fd0d011f5aa3a2cf7e89b4a22e24f923a6bd45074cefe125e2fb33', 'ADMIN'),
(11, 'Adrian', 'Cabello', 'adrcabmar', 'adrcabmar@example.com', 'scrypt:32768:8:1$uh1IGF90LTfiEraD$58161931e2e2f229cd8b59b2d63820a2c50000b35faf63a0b54aa3225c6d5f74e3dbd89495fd0d011f5aa3a2cf7e89b4a22e24f923a6bd45074cefe125e2fb33', 'PROP_MASCOTA');

INSERT IGNORE INTO clinicas (id, nombre, direccion, telefono, propietario_id) VALUES
(1, 'Clínica 1', 'Calle Veterinario 1', '954123456', 4),
(2, 'Clínica 2', 'Calle Veterinario 2', '915123456', 5),
(3, 'Clínica 3', 'Calle Veterinario 3', '934123456', 6);

INSERT IGNORE INTO habitaciones_hotel (id, nombre, descripcion, reservable, url_imagen, tamaño, tipo, clinica_id) VALUES
(1, 'White Savannah', 'Una habitación espaciosa inspirada en las vastas llanuras africanas, con decoración en tonos beige y blanco. Equipada con rascadores de altura, plataformas elevadas y escondites perfectos para gatos activos que necesitan espacio para correr y trepar. Incluye zona de juegos con juguetes interactivos y área de descanso con vista panorámica.', TRUE, "https://loveurdog.co.uk/wp-content/uploads/2024/11/Love-Ur-Dog-Hotel-Stays.jpg", 'MEDIANO', 'PERRO', 1),
(2, 'Hello Kitty', 'Habitación temática adorable con decoración rosa y blanco inspirada en el icónico personaje. Ideal para gatos tranquilos o mascotas pequeñas que disfrutan de un ambiente suave y acogedor. Cuenta con camas suaves con forma de lazo, juguetes de felpa y escondites acolchados. Ambiente relajante con iluminación tenue.', TRUE, "https://cooperspets.co.za/wp-content/uploads/2025/02/coopers-pet-hotel_cat-room_051-2048x1536.webp", 'ACOGEDOR', 'GATO', 2),
(3, 'Blue sky', 'Habitación luminosa con temática celestial que recrea la sensación de estar en las nubes. Paredes en tonos azul cielo con nubes decorativas y luces LED que simulan estrellas por la noche. Perfecta para aves o mascotas que disfrutan de espacios abiertos y bien iluminados. Incluye perchas a diferentes alturas y área de observación.', TRUE, "https://www.tiendanimal.es/on/demandware.static/-/Sites-kiwoko-master-catalog/default/dw1a777718/images/large/c5f967be789a455494bfb96202fe1f41.jpg", 'KING_SIZE', 'PAJARO', 1),
(4, 'Hamtaro house', 'Un hogar en miniatura diseñado específicamente para roedores y mascotas pequeñas. Inspirado en el mundo de los hámsters, cuenta con túneles interconectados, ruedas de ejercicio, áreas de anidación con material suave y dispensadores de comida interactivos. Ambiente seguro y estimulante para que las mascotas pequeñas exploren y jueguen. house', TRUE, "https://m.media-amazon.com/images/I/71YwKyZ-seL._AC_UF1000,1000_QL80_.jpg", 'MEDIANO', 'HAMSTER', 3);

INSERT IGNORE INTO mascotas (id, nombre, cumpleaños, tipo, dueño_id) VALUES
(1, 'Roco', '2020-01-01', 'PERRO', 1),
(2, 'Misifú', '2019-05-15', 'GATO', 2),
(3, 'Lorito', '2021-03-10', 'PAJARO', 11),
(4, 'Saturnino', '2023-03-10', 'HAMSTER', 3);

INSERT IGNORE INTO props_clinicas (id, telefono) VALUES
(4, '954123457'),
(5, '915123458'),
(6, '934123459');

INSERT IGNORE INTO props_mascotas (id, direccion, telefono, clinica_id) VALUES
(1, 'Calle Falsa 123', '123456789', 1),
(2, 'Avenida Siempre Viva 742', '987654321', 2),
(3, 'Boulevard de los Sueños Rotos 456', '456789123', 3),
(11, 'Calle Nueva 321', '321654987', 1);

INSERT IGNORE INTO veterinarios (id, especialidades, ciudad, clinica_id) VALUES
(7, '["DERMATOLOGIA", "OFTALMOLOGIA"]', 'Sevilla', 1),
(8, '["CIRUGIA", "MEDICINA_INTERNA"]', 'Sevilla', 2),
(9, '["DERMATOLOGIA", "REHABILITACION"]', 'Sevilla', 3);

INSERT IGNORE INTO visitas (id, fecha, descripcion, veterinario_id, mascota_id) VALUES
(1, '2023-10-01 10:00:00', 'Consulta general', 7, 1),
(2, '2023-10-02 11:00:00', 'Chequeo de salud', 8, 2),
(3, '2023-10-03 12:00:00', 'Vacunación', 9, 3);

INSERT IGNORE INTO adopciones (id, descripcion, adopcion_cerrada, fecha_creacion, mascota_id, dueño_nuevo_id, dueño_anterior_id) VALUES
(1, 'Adopción de Misifú', false, '2023-10-05 10:00:00', 2, null, 2),
(2, 'Adopción de Lorito', true, '2023-10-06 10:00:00', 3, 1, 3);

INSERT IGNORE INTO peticiones_adopcion (id, razon_adopcion, fecha_solicitud, solicitante_id, adopcion_id, estado_peticion) VALUES
(1, 'Me gustaria mucho cuidar del pequeñajo', '2023-11-05 12:00:00', 3, 1, 'PENDIENTE'),
(2, 'Ofrecemos una casa con espacios abiertos para que Lorito pueda volar sin angustias', '2023-10-06 14:00:00', 1, 2, 'APROBADA');

INSERT IGNORE INTO consultas (id, titulo, descripcion, estado_consulta, fecha_creacion, dueño_id, vet_id, mascota_id) VALUES
(1, 'Consulta sobre la salud de Roco', 'Roco lleva varios días malo.' , 'PENDIENTE', '2023-10-05 10:00:00', 1, null, 1),
(2, 'Consulta sobre la adopción de Misifú', '¿Cómo va la adopción?' , 'RESUELTA', '2023-10-05 10:00:00', 2, null, 2),
(3, 'Consulta sobre la vacunación de Lorito', '¿Es monodosis o hay que poner la vacuna más veces?' , 'CERRADA', '2023-10-05 10:00:00', 3, 9, 3);  -- el dueño id es 3 porque es anterior a la adopción

INSERT IGNORE INTO reservas (id, fecha_inicio, fecha_fin, habitacion_id, mascota_id) VALUES
(1, '2023-10-01', '2023-10-05', 1, 1),
(2, '2023-10-02', '2023-10-06', 2, 2),
(3, '2023-10-03', '2023-10-07', 3, 3),
(4, '2023-10-04', '2023-10-08', 4, 4);

INSERT IGNORE INTO respuesta_consulta (id, titulo, descripcion, fecha_creacion, consulta_id, vet_id) VALUES
(1, 'Respuesta a la consulta sobre la adopción de Misifú', 'La adopción está en proceso y debería completarse pronto.', '2023-10-07 14:30:00', 2, 7),
(2, 'Respuesta a la consulta sobre la vacunación de Lorito', 'La vacuna es monodosis, no es necesario repetirla.', '2023-10-08 09:15:00', 3, 9);