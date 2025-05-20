
-- Usuarios
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('admin', 'cliente') NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Slices
CREATE TABLE slices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  name VARCHAR(100),
  description TEXT,
  status ENUM('creando', 'activo', 'error', 'eliminado') DEFAULT 'creando',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- VMs
CREATE TABLE vms (
  id INT AUTO_INCREMENT PRIMARY KEY,
  slice_id INT,
  name VARCHAR(100),
  cpu INT,
  ram INT,
  image_name VARCHAR(100),
  worker_ip VARCHAR(100),
  status ENUM('iniciando', 'activo', 'apagado', 'error'),
  FOREIGN KEY (slice_id) REFERENCES slices(id) ON DELETE CASCADE
);

-- Imágenes
CREATE TABLE images (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  path TEXT,
  owner_id INT,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Plantillas de topología
CREATE TABLE topologies (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  json_template TEXT,
  owner_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Workers
CREATE TABLE workers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  ip VARCHAR(100),
  cpu_total INT,
  ram_total INT,
  cpu_used INT DEFAULT 0,
  ram_used INT DEFAULT 0,
  status ENUM('activo', 'inactivo', 'error') DEFAULT 'activo'
);

-- Logs del sistema
CREATE TABLE event_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tipo ENUM('info', 'error', 'warning'),
  usuario VARCHAR(50),
  mensaje TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Métricas por VM
CREATE TABLE metrics (
  id INT AUTO_INCREMENT PRIMARY KEY,
  vm_id INT,
  cpu_usage FLOAT,
  ram_usage INT,
  disk_usage INT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (vm_id) REFERENCES vms(id) ON DELETE CASCADE
);
