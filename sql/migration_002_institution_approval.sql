-- Ejecutar UNA VEZ en bases PostgreSQL ya existentes (p. ej. Supabase SQL Editor).
-- Instituciones ya existentes quedan aprobadas; las nuevas filas usan default 'pending'.

ALTER TABLE institutions
    ADD COLUMN IF NOT EXISTS approval_status TEXT NOT NULL DEFAULT 'approved';

ALTER TABLE institutions
    ALTER COLUMN approval_status SET DEFAULT 'pending';

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS is_super_master BOOLEAN NOT NULL DEFAULT FALSE;

UPDATE users SET is_super_master = TRUE WHERE username = 'admin';
