-- Run this in your Supabase SQL Editor

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'member', -- 'admin' or 'member'
    allowed_tools TEXT[] DEFAULT ARRAY['Dashboard'], -- Array of Tool names
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Insert an initial admin user (Password: admin123)
-- Hash generated via SHA-256 for this example
INSERT INTO users (email, password_hash, role, allowed_tools)
VALUES (
    'admin@trikon.com', 
    '240be518fabd2724ddb6f0403f350914e06bc10c7c81794081c9745b417e3391', 
    'admin', 
    ARRAY['Dashboard', 'Business Card', 'Welcome Aboard', 'ID Card', 'Settings']
);
