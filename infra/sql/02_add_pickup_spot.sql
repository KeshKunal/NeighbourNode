-- 02_add_pickup_spot.sql
-- Adds pickup_spot column to transactions table (requested by Nimish)

ALTER TABLE transactions
ADD COLUMN IF NOT EXISTS pickup_spot TEXT;
