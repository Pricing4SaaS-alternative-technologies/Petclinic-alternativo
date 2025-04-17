-- Insert data into usuarios table
INSERT IGNORE INTO usuarios (id, first_name,last_name, username, email, password, type) VALUES
(1, 'Daniel','Benito','danbenhid', 'danbenhid@example.com', 'scrypt:32768:8:1$uh1IGF90LTfiEraD$58161931e2e2f229cd8b59b2d63820a2c50000b35faf63a0b54aa3225c6d5f74e3dbd89495fd0d011f5aa3a2cf7e89b4a22e24f923a6bd45074cefe125e2fb33', 'PROP_MASCOTA'),
(2, 'Fernando', 'De Celis','ferdehur', 'ferdehur@example.com', 'scrypt:32768:8:1$uh1IGF90LTfiEraD$58161931e2e2f229cd8b59b2d63820a2c50000b35faf63a0b54aa3225c6d5f74e3dbd89495fd0d011f5aa3a2cf7e89b4a22e24f923a6bd45074cefe125e2fb33', 'PROP_MASCOTA'),
(3, 'Pablo', 'Castellanos','pabcascom', 'pabcascom@example.com', 'scrypt:32768:8:1$uh1IGF90LTfiEraD$58161931e2e2f229cd8b59b2d63820a2c50000b35faf63a0b54aa3225c6d5f74e3dbd89495fd0d011f5aa3a2cf7e89b4a22e24f923a6bd45074cefe125e2fb33', 'PROP_MASCOTA');

INSERT IGNORE INTO props_mascotas (id, direccion, telefono) VALUES
(1, 'Calle Falsa 123', '123456789'),
(2, 'Avenida Siempre Viva 742', '987654321'),
(3, 'Boulevard de los Sueños Rotos 456', '456789123');