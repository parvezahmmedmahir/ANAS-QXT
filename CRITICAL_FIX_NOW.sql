-- ================================================================================
-- CRITICAL FIX - RUN THIS IMMEDIATELY IN SUPABASE
-- This fixes the PENDING license bypass and missing geolocation data
-- ================================================================================

-- STEP 1: Reset all improperly activated PENDING licenses
-- ================================================================================
UPDATE licenses 
SET device_id = NULL,
    activation_date = NULL,
    last_access_date = NULL,
    usage_count = 0
WHERE status = 'PENDING' 
  AND device_id IS NOT NULL;

-- Show how many were reset
SELECT 
    'RESET PENDING LICENSES' as action,
    COUNT(*) as affected_rows
FROM licenses 
WHERE status = 'PENDING' AND device_id IS NULL;

-- STEP 2: Add missing geolocation columns to user_sessions
-- ================================================================================
DO $$ 
BEGIN
    -- Add country
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='country'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN country TEXT;
        RAISE NOTICE 'Added country column';
    END IF;

    -- Add region
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='region'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN region TEXT;
        RAISE NOTICE 'Added region column';
    END IF;

    -- Add city
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='city'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN city TEXT;
        RAISE NOTICE 'Added city column';
    END IF;

    -- Add isp
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='isp'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN isp TEXT;
        RAISE NOTICE 'Added isp column';
    END IF;

    -- Add latitude
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='latitude'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN latitude DECIMAL(10, 8);
        RAISE NOTICE 'Added latitude column';
    END IF;

    -- Add longitude
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='longitude'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN longitude DECIMAL(11, 8);
        RAISE NOTICE 'Added longitude column';
    END IF;

    -- Add postal_code
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='postal_code'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN postal_code TEXT;
        RAISE NOTICE 'Added postal_code column';
    END IF;

    -- Add organization
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='organization'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN organization TEXT;
        RAISE NOTICE 'Added organization column';
    END IF;
END $$;

-- STEP 3: Add missing columns to licenses table
-- ================================================================================
DO $$ 
BEGIN
    -- Add country
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='licenses' AND column_name='country'
    ) THEN
        ALTER TABLE licenses ADD COLUMN country TEXT;
        RAISE NOTICE 'Added country to licenses';
    END IF;

    -- Add city
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='licenses' AND column_name='city'
    ) THEN
        ALTER TABLE licenses ADD COLUMN city TEXT;
        RAISE NOTICE 'Added city to licenses';
    END IF;

    -- Add timezone_geo
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='licenses' AND column_name='timezone_geo'
    ) THEN
        ALTER TABLE licenses ADD COLUMN timezone_geo TEXT;
        RAISE NOTICE 'Added timezone_geo to licenses';
    END IF;
END $$;

-- STEP 4: Verify the fix
-- ================================================================================
-- Check for PENDING licenses with device_id (should be 0)
SELECT 
    'PENDING licenses with device_id (SHOULD BE 0)' as check_name,
    COUNT(*) as count
FROM licenses 
WHERE status = 'PENDING' AND device_id IS NOT NULL;

-- Check user_sessions columns
SELECT 
    'user_sessions has geolocation columns' as check_name,
    COUNT(*) as column_count
FROM information_schema.columns 
WHERE table_name='user_sessions' 
  AND column_name IN ('country', 'region', 'city', 'isp', 'latitude', 'longitude');

-- Show current license states
SELECT 
    status,
    COUNT(*) as total,
    COUNT(CASE WHEN device_id IS NOT NULL THEN 1 END) as with_device,
    COUNT(CASE WHEN activation_date IS NOT NULL THEN 1 END) as activated
FROM licenses
GROUP BY status;

-- ================================================================================
-- CRITICAL FIX COMPLETE
-- ================================================================================
SELECT '✅ CRITICAL FIX APPLIED SUCCESSFULLY!' as result;
SELECT 'Users with PENDING licenses must re-enter their license key to activate' as note;
SELECT 'Geolocation data will now be collected on next login' as note2;
