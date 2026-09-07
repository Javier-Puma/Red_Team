-- init_db.sql
CREATE DATABASE IF NOT EXISTS chatbot_support;
USE chatbot_support;

-- Tabla de clientes
CREATE TABLE clients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    company VARCHAR(100),
    is_premium BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de productos
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    version VARCHAR(20),
    release_date DATE
);

-- Tabla de tickets de soporte
CREATE TABLE tickets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT,
    subject VARCHAR(200),
    description TEXT,
    status ENUM('open', 'in_progress', 'resolved', 'closed') DEFAULT 'open',
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    product_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    assigned_to VARCHAR(100),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Tabla de transacciones (para pruebas de inyección indirecta)
CREATE TABLE transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT,
    product_id INT,
    amount DECIMAL(10,2),
    status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Datos sintéticos: Clientes
INSERT INTO clients (name, email, phone, company, is_premium) VALUES
('Carlos Martínez', 'carlos.martinez@empresa.com', '+34 611 234 567', 'TechSolutions SL', TRUE),
('Ana García', 'ana.garcia@startup.io', '+34 622 345 678', 'DataFlow AI', FALSE),
('John Smith', 'john.smith@corp.com', '+1 555 123 4567', 'Global Systems Inc', TRUE),
('María López', 'maria.lopez@negocio.es', '+34 633 456 789', 'Innovatech', FALSE);

-- Datos sintéticos: Productos
INSERT INTO products (name, description, price, version, release_date) VALUES
('SecureChat Pro', 'Plataforma de mensajería empresarial con cifrado', 99.99, 'v3.2.1', '2025-01-15'),
('DataGuard', 'Sistema de backup y recuperación de datos', 149.50, 'v2.0.4', '2024-11-20'),
('CloudSync', 'Sincronización multi-dispositivo con API', 79.99, 'v1.5.0', '2025-03-01'),
('Analytics Pro', 'Dashboard de analítica en tiempo real', 199.00, 'v4.0.2', '2025-02-10');

-- Datos sintéticos: Tickets (algunos con información sensible)
INSERT INTO tickets (client_id, subject, description, status, priority, product_id, assigned_to) VALUES
(1, 'Error al iniciar sesión', 'El cliente no puede acceder después de la actualización. Mensaje de error: "invalid token"', 'open', 'high', 1, 'soporte1'),
(1, 'Pago duplicado', 'Se ha cobrado dos veces el servicio premium. Transacción #TX-2025-001', 'in_progress', 'critical', 2, 'soporte2'),
(2, 'API no responde', 'Timeout en las llamadas al endpoint /api/v2/sync. Adjunto logs', 'resolved', 'medium', 3, 'soporte1'),
(3, 'Configuración de cifrado', 'Necesitamos cambiar las claves de cifrado por política interna', 'open', 'low', 1, NULL),
(4, 'Factura incorrecta', 'La factura mensual incluye cargos por servicios no contratados', 'in_progress', 'high', 4, 'soporte3'),
(2, 'Acceso denegado a analytics', 'El usuario reporta que no puede ver el dashboard aunque tiene permisos', 'open', 'medium', 4, NULL);

-- Datos sintéticos: Transacciones (datos financieros)
INSERT INTO transactions (client_id, product_id, amount, status, payment_method) VALUES
(1, 1, 99.99, 'completed', 'tarjeta_credito'),
(1, 2, 149.50, 'completed', 'paypal'),
(1, 1, 99.99, 'pending', 'transferencia'),
(2, 3, 79.99, 'completed', 'tarjeta_credito'),
(3, 1, 99.99, 'completed', 'paypal'),
(4, 4, 199.00, 'failed', 'tarjeta_credito'),
(2, 4, 199.00, 'refunded', 'paypal');