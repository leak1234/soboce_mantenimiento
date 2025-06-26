-- Base de Datos: Sistema de Mantenimiento SOBOCE

-- Tabla: Usuario
CREATE TABLE Usuario (
    usuario_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    correo VARCHAR(100) UNIQUE,
    contraseña VARCHAR(255),
    rol VARCHAR(50),  -- técnico, supervisor, admin
    estado BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP
);

-- Tabla: Maquinaria
CREATE TABLE Maquinaria (
    maquinaria_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    descripcion TEXT,
    ubicacion VARCHAR(100),
    estado VARCHAR(50),
    fecha_registro DATE DEFAULT CURRENT_DATE
);

-- Tabla: Horometro
CREATE TABLE Horometro (
    horometro_id SERIAL PRIMARY KEY,
    maquinaria_id INT REFERENCES Maquinaria(maquinaria_id),
    fecha DATE DEFAULT CURRENT_DATE,
    horas_operacion DECIMAL(10,2)
);

-- Tabla: FrecuenciaMantenimiento
CREATE TABLE FrecuenciaMantenimiento (
    frecuencia_id SERIAL PRIMARY KEY,
    descripcion VARCHAR(100),
    intervalo_horas INT,
    intervalo_dias INT
);

-- Tabla: Mantenimiento
CREATE TABLE Mantenimiento (
    mantenimiento_id SERIAL PRIMARY KEY,
    maquinaria_id INT REFERENCES Maquinaria(maquinaria_id),
    tipo VARCHAR(50), -- preventivo, correctivo
    descripcion TEXT,
    fecha_programada DATE,
    frecuencia_id INT REFERENCES FrecuenciaMantenimiento(frecuencia_id),
    estado VARCHAR(50) DEFAULT 'pendiente'
);

-- Tabla: OrdenTrabajo
CREATE TABLE OrdenTrabajo (
    orden_id SERIAL PRIMARY KEY,
    mantenimiento_id INT REFERENCES Mantenimiento(mantenimiento_id),
    fecha_emision DATE DEFAULT CURRENT_DATE,
    tecnico_asignado INT REFERENCES Usuario(usuario_id),
    observaciones TEXT,
    estado VARCHAR(50) DEFAULT 'abierta'
);

-- Tabla: Proveedor
CREATE TABLE Proveedor (
    proveedor_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    direccion TEXT
);

-- Tabla: Repuesto
CREATE TABLE Repuesto (
    repuesto_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    descripcion TEXT,
    stock INT,
    unidad VARCHAR(50),
    proveedor_id INT REFERENCES Proveedor(proveedor_id)
);

-- Tabla: SolicitudRepuesto
CREATE TABLE SolicitudRepuesto (
    solicitud_id SERIAL PRIMARY KEY,
    fecha_solicitud DATE DEFAULT CURRENT_DATE,
    orden_id INT REFERENCES OrdenTrabajo(orden_id),
    estado VARCHAR(50) DEFAULT 'pendiente'
);

-- Tabla: DetalleSolicitud
CREATE TABLE DetalleSolicitud (
    detalle_id SERIAL PRIMARY KEY,
    solicitud_id INT REFERENCES SolicitudRepuesto(solicitud_id),
    repuesto_id INT REFERENCES Repuesto(repuesto_id),
    cantidad INT
);

-- Tabla: DetalleRepuesto
CREATE TABLE DetalleRepuesto (
    detalle_repuesto_id SERIAL PRIMARY KEY,
    mantenimiento_id INT REFERENCES Mantenimiento(mantenimiento_id),
    repuesto_id INT REFERENCES Repuesto(repuesto_id),
    cantidad_utilizada INT
);

-- Tabla: Notificacion
CREATE TABLE Notificacion (
    notificacion_id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES Usuario(usuario_id),
    mensaje TEXT,
    leido BOOLEAN DEFAULT FALSE,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: BitacoraSistema
CREATE TABLE BitacoraSistema (
    bitacora_id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES Usuario(usuario_id),
    accion TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Documento
CREATE TABLE Documento (
    documento_id SERIAL PRIMARY KEY,
    mantenimiento_id INT REFERENCES Mantenimiento(mantenimiento_id),
    nombre_archivo VARCHAR(255),
    ruta TEXT,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: HistorialMantenimiento
CREATE TABLE HistorialMantenimiento (
    historial_id SERIAL PRIMARY KEY,
    mantenimiento_id INT REFERENCES Mantenimiento(mantenimiento_id),
    fecha_ejecucion DATE,
    descripcion TEXT,
    tecnico_id INT REFERENCES Usuario(usuario_id)
);

-- Tabla: MantenimientoPredictivo
CREATE TABLE MantenimientoPredictivo (
    predictivo_id SERIAL PRIMARY KEY,
    maquinaria_id INT REFERENCES Maquinaria(maquinaria_id),
    fecha_analisis DATE,
    indicador VARCHAR(100),
    valor DECIMAL(10,2),
    alerta BOOLEAN DEFAULT FALSE,
    observaciones TEXT
);
