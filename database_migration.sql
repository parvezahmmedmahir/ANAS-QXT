-- QUANTUM X PRO - DATABASE MIGRATION SCRIPT
-- Run this in your Supabase SQL Editor to fix the license validation system

-- Step 1: Add missing columns to licenses table if they don't exist
DO $$ 
BEGIN
    -- Add ip_address column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='licenses' AND column_name='ip_address'
    ) THEN
        ALTER TABLE licenses ADD COLUMN ip_address TEXT;
        RAISE NOTICE 'Added ip_address column to licenses table';
    END IF;

    -- Add user_agent column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='licenses' AND column_name='user_agent'
    ) THEN
        ALTER TABLE licenses ADD COLUMN user_agent TEXT;
        RAISE NOTICE 'Added user_agent column to licenses table';
    END IF;

    -- Ensure status column has default value
    ALTER TABLE licenses ALTER COLUMN status SET DEFAULT 'PENDING';
    RAISE NOTICE 'Set default status to PENDING';
END $$;

-- Step 2: CRITICAL SECURITY FIX - Reset all licenses without proper activation
-- This ensures that ONLY licenses with valid activation data can auto-login

UPDATE licenses 
SET status = 'PENDING', 
    device_id = NULL,
    ip_address = NULL,
    user_agent = NULL,
    activation_date = NULL,
    last_access_date = NULL,
    usage_count = 0
WHERE status IS NULL 
   OR status = ''
   OR (status != 'BLOCKED' AND activation_date IS NULL AND category != 'OWNER');

-- Step 3: Ensure all OWNER category licenses are marked as ACTIVE
UPDATE licenses 
SET status = 'ACTIVE',
    activation_date = COALESCE(activation_date, CURRENT_TIMESTAMP)
WHERE category = 'OWNER' AND status != 'BLOCKED';

-- Step 4: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_licenses_device_id ON licenses(device_id);
CREATE INDEX IF NOT EXISTS idx_licenses_status ON licenses(status);
CREATE INDEX IF NOT EXISTS idx_licenses_category ON licenses(category);
CREATE INDEX IF NOT EXISTS idx_licenses_activation ON licenses(activation_date);

-- Step 5: Add timezone, resolution, and platform columns to user_sessions if missing
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='timezone'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN timezone TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='resolution'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN resolution TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='platform'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN platform TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='login_time'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- Step 6: Display summary of license states
SELECT 
    status,
    category,
    COUNT(*) as count,
    COUNT(CASE WHEN device_id IS NOT NULL THEN 1 END) as with_device,
    COUNT(CASE WHEN activation_date IS NOT NULL THEN 1 END) as activated
FROM licenses
GROUP BY status, category
ORDER BY status, category;

-- Step 7: Show licenses that need manual activation
SELECT 
    key_code,
    category,
    status,
    device_id,
    activation_date,
    expiry_date
FROM licenses
WHERE status = 'PENDING'
ORDER BY category, key_code;
