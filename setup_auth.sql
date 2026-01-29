-- 1. Create the Users Table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'member', -- 'admin' or 'member'
    allowed_tools TEXT[] DEFAULT ARRAY['Dashboard'], 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Insert the Admin User (Password: admin123)
-- Hash: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
INSERT INTO users (email, password_hash, role, allowed_tools)
VALUES (
    'admin@trikon.com', 
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 
    'admin', 
    ARRAY['Dashboard', 'Business Card', 'Welcome Aboard', 'ID Card', 'Settings']
)
ON CONFLICT (email) 
DO UPDATE SET 
    password_hash = EXCLUDED.password_hash,
    allowed_tools = EXCLUDED.allowed_tools,
    role = EXCLUDED.role;

-- 3. Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 4. Policy: Allow Login (Select access for everyone)
DROP POLICY IF EXISTS "Allow public read" ON users;
CREATE POLICY "Allow public read"
ON users FOR SELECT
TO anon
USING (true);

-- 5. Policy: Allow Registration/Admin Creation (Insert access for everyone)
DROP POLICY IF EXISTS "Allow public insert" ON users;
CREATE POLICY "Allow public insert"
ON users FOR INSERT
TO anon
WITH CHECK (true);

-- 6. Policy: Allow Updates (Optional, for admin panel updates)
DROP POLICY IF EXISTS "Allow public update" ON users;
CREATE POLICY "Allow public update"
ON users FOR UPDATE
TO anon
USING (true);
