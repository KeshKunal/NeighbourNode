-- 01_initial_schema.sql

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE transaction_status AS ENUM (
    'available',
    'pending_approval',
    'reserved',
    'active',
    'overdue',
    'returned',
    'cancelled'
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name TEXT NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    building TEXT,
    unit TEXT,
    telegram_chat_id TEXT UNIQUE,
    rating DECIMAL(3, 2) DEFAULT 5.00,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_rating ON users(rating DESC);

CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    condition TEXT,
    location_hint TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    current_status transaction_status DEFAULT 'available',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_items_owner_id ON items(owner_id);
CREATE INDEX idx_items_name ON items(name);
CREATE INDEX idx_items_category ON items(category);
CREATE INDEX idx_items_status ON items(current_status);

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_id UUID NOT NULL REFERENCES items(id) ON DELETE RESTRICT,
    borrower_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    requested_start TIMESTAMP WITH TIME ZONE NOT NULL,
    requested_end TIMESTAMP WITH TIME ZONE NOT NULL,
    approved_start TIMESTAMP WITH TIME ZONE,
    approved_end TIMESTAMP WITH TIME ZONE,
    status transaction_status NOT NULL DEFAULT 'pending_approval',
    calendar_event_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_transactions_item_id ON transactions(item_id);
CREATE INDEX idx_transactions_borrower_id ON transactions(borrower_id);
CREATE INDEX idx_transactions_owner_id ON transactions(owner_id);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_warden ON transactions(status, requested_end);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    sender_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    channel TEXT NOT NULL, -- e.g., 'telegram'
    direction TEXT NOT NULL, -- e.g., 'inbound', 'outbound'
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_transaction_id ON messages(transaction_id);
CREATE INDEX idx_messages_sender_user_id ON messages(sender_user_id);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES transactions(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    status TEXT NOT NULL, -- e.g., 'queued', 'sent', 'failed'
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_transaction_id ON notifications(transaction_id);
CREATE INDEX idx_notifications_status ON notifications(status);
