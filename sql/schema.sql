CREATE TABLE IF NOT EXISTS movimientos (
    id BIGSERIAL PRIMARY KEY,
    usuario_id TEXT NOT NULL,
    tipo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    cantidad NUMERIC(10, 2) NOT NULL,
    categoria TEXT NOT NULL,
    fecha DATE NOT NULL
);