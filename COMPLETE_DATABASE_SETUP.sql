-- ================================================================================
-- QUANTUM X PRO - COMPLETE DATABASE SETUP (ALL-IN-ONE)
-- Run this ONCE in Supabase SQL Editor to set up everything
-- ================================================================================

-- PART 1: ADD MISSING COLUMNS TO LICENSES TABLE
-- ================================================================================
DO $$ 
BEGIN
    -- Add ip_address column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='licenses' AND column_name='ip_address'
    ) THEN
        ALTER TABLE licenses ADD COLUMN ip_address TEXT;
        RAISE NOTICE 'Added ip_address column to licenses';
    END IF;

    -- Add user_agent column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='licenses' AND column_name='user_agent'
    ) THEN
        ALTER TABLE licenses ADD COLUMN user_agent TEXT;
        RAISE NOTICE 'Added user_agent column to licenses';
    END IF;

    -- Add country column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='licenses' AND column_name='country'
    ) THEN
        ALTER TABLE licenses ADD COLUMN country TEXT;
        RAISE NOTICE 'Added country column to licenses';
    END IF;

    -- Add city column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='licenses' AND column_name='city'
    ) THEN
        ALTER TABLE licenses ADD COLUMN city TEXT;
        RAISE NOTICE 'Added city column to licenses';
    END IF;

    -- Add timezone_geo column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='licenses' AND column_name='timezone_geo'
    ) THEN
        ALTER TABLE licenses ADD COLUMN timezone_geo TEXT;
        RAISE NOTICE 'Added timezone_geo column to licenses';
    END IF;

    -- Ensure status column has default value
    ALTER TABLE licenses ALTER COLUMN status SET DEFAULT 'PENDING';
    RAISE NOTICE 'Set default status to PENDING';
END $$;

-- PART 2: ADD GEOLOCATION COLUMNS TO USER_SESSIONS TABLE
-- ================================================================================
DO $$ 
BEGIN
    -- Add country column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='country'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN country TEXT;
        RAISE NOTICE 'Added country column to user_sessions';
    END IF;

    -- Add region column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='region'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN region TEXT;
        RAISE NOTICE 'Added region column to user_sessions';
    END IF;

    -- Add city column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='city'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN city TEXT;
        RAISE NOTICE 'Added city column to user_sessions';
    END IF;

    -- Add isp column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='isp'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN isp TEXT;
        RAISE NOTICE 'Added isp column to user_sessions';
    END IF;

    -- Add latitude column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='latitude'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN latitude DECIMAL(10, 8);
        RAISE NOTICE 'Added latitude column to user_sessions';
    END IF;

    -- Add longitude column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='longitude'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN longitude DECIMAL(11, 8);
        RAISE NOTICE 'Added longitude column to user_sessions';
    END IF;

    -- Add postal_code column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='postal_code'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN postal_code TEXT;
        RAISE NOTICE 'Added postal_code column to user_sessions';
    END IF;

    -- Add organization column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='organization'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN organization TEXT;
        RAISE NOTICE 'Added organization column to user_sessions';
    END IF;
END $$;

-- PART 3: SECURITY FIX - RESET IMPROPERLY ACTIVATED LICENSES
-- ================================================================================
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

-- Ensure all OWNER category licenses are marked as ACTIVE
UPDATE licenses 
SET status = 'ACTIVE',
    activation_date = COALESCE(activation_date, CURRENT_TIMESTAMP)
WHERE category = 'OWNER' AND status != 'BLOCKED';

-- PART 4: CREATE PERFORMANCE INDICES
-- ================================================================================
CREATE INDEX IF NOT EXISTS idx_licenses_device_id ON licenses(device_id);
CREATE INDEX IF NOT EXISTS idx_licenses_status ON licenses(status);
CREATE INDEX IF NOT EXISTS idx_licenses_category ON licenses(category);
CREATE INDEX IF NOT EXISTS idx_licenses_activation ON licenses(activation_date);
CREATE INDEX IF NOT EXISTS idx_licenses_expiry ON licenses(expiry_date);
CREATE INDEX IF NOT EXISTS idx_licenses_country ON licenses(country);

CREATE INDEX IF NOT EXISTS idx_sessions_device_id ON user_sessions(device_id);
CREATE INDEX IF NOT EXISTS idx_sessions_license_key ON user_sessions(license_key);
CREATE INDEX IF NOT EXISTS idx_sessions_login_time ON user_sessions(login_time DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_country ON user_sessions(country);
CREATE INDEX IF NOT EXISTS idx_sessions_city ON user_sessions(city);
CREATE INDEX IF NOT EXISTS idx_sessions_ip ON user_sessions(ip_address);

-- PART 5: CREATE MONITORING VIEWS
-- ================================================================================

-- View: Geographic Distribution
CREATE OR REPLACE VIEW geographic_distribution AS
SELECT 
    country,
    COUNT(DISTINCT license_key) as unique_users,
    COUNT(*) as total_sessions,
    MAX(login_time) as last_access
FROM user_sessions
WHERE country IS NOT NULL AND country != 'Unknown'
GROUP BY country
ORDER BY unique_users DESC;

-- View: License Overview
CREATE OR REPLACE VIEW license_overview AS
SELECT 
    l.key_code,
    l.category,
    l.status,
    l.device_id,
    l.ip_address,
    l.country,
    l.city,
    l.usage_count,
    l.activation_date,
    l.last_access_date,
    l.expiry_date,
    l.expiry_date < CURRENT_TIMESTAMP as is_expired,
    (SELECT COUNT(*) FROM user_sessions WHERE license_key = l.key_code) as total_sessions,
    (SELECT MAX(login_time) FROM user_sessions WHERE license_key = l.key_code) as last_session
FROM licenses l
ORDER BY l.last_access_date DESC NULLS LAST;

-- View: User Location Tracking
CREATE OR REPLACE VIEW user_location_tracking AS
SELECT 
    us.license_key,
    us.device_id,
    us.ip_address,
    us.country,
    us.region,
    us.city,
    us.isp,
    us.timezone,
    us.latitude,
    us.longitude,
    us.login_time,
    l.status as license_status,
    l.category as license_category
FROM user_sessions us
LEFT JOIN licenses l ON us.license_key = l.key_code
ORDER BY us.login_time DESC;

-- PART 6: CREATE ADMIN FUNCTIONS
-- ================================================================================

-- Function: Detect Suspicious Logins (Multiple Countries/Devices)
CREATE OR REPLACE FUNCTION detect_suspicious_logins(hours_window INTEGER DEFAULT 24)
RETURNS TABLE (
    license_key TEXT,
    device_count BIGINT,
    country_count BIGINT,
    ip_count BIGINT,
    countries TEXT,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        us.license_key,
        COUNT(DISTINCT us.device_id) as device_count,
        COUNT(DISTINCT us.country) as country_count,
        COUNT(DISTINCT us.ip_address) as ip_count,
        STRING_AGG(DISTINCT us.country, ', ') as countries,
        MIN(us.login_time) as first_seen,
        MAX(us.login_time) as last_seen
    FROM user_sessions us
    WHERE us.login_time > CURRENT_TIMESTAMP - (hours_window || ' hours')::INTERVAL
    GROUP BY us.license_key
    HAVING COUNT(DISTINCT us.country) > 1 OR COUNT(DISTINCT us.device_id) > 1
    ORDER BY country_count DESC, device_count DESC;
END;
$$ LANGUAGE plpgsql;

-- Function: Get License Statistics
CREATE OR REPLACE FUNCTION get_license_stats()
RETURNS TABLE (
    total_licenses BIGINT,
    active_licenses BIGINT,
    pending_licenses BIGINT,
    blocked_licenses BIGINT,
    expired_licenses BIGINT,
    licenses_with_devices BIGINT,
    total_sessions BIGINT,
    active_today BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM licenses) as total_licenses,
        (SELECT COUNT(*) FROM licenses WHERE status = 'ACTIVE') as active_licenses,
        (SELECT COUNT(*) FROM licenses WHERE status = 'PENDING') as pending_licenses,
        (SELECT COUNT(*) FROM licenses WHERE status = 'BLOCKED') as blocked_licenses,
        (SELECT COUNT(*) FROM licenses WHERE expiry_date < CURRENT_TIMESTAMP) as expired_licenses,
        (SELECT COUNT(*) FROM licenses WHERE device_id IS NOT NULL) as licenses_with_devices,
        (SELECT COUNT(*) FROM user_sessions) as total_sessions,
        (SELECT COUNT(DISTINCT license_key) FROM user_sessions 
         WHERE login_time > CURRENT_TIMESTAMP - INTERVAL '1 day') as active_today;
END;
$$ LANGUAGE plpgsql;

-- Function: Auto-Expire Old Licenses
CREATE OR REPLACE FUNCTION auto_expire_licenses()
RETURNS INTEGER AS $$
DECLARE
    expired_count INTEGER;
BEGIN
    -- Block all expired licenses that are still ACTIVE
    UPDATE licenses 
    SET status = 'BLOCKED'
    WHERE expiry_date < CURRENT_TIMESTAMP 
    AND status = 'ACTIVE';
    
    GET DIAGNOSTICS expired_count = ROW_COUNT;
    RETURN expired_count;
END;
$$ LANGUAGE plpgsql;

-- PART 7: DISPLAY SUMMARY
-- ================================================================================
SELECT '✅ Database setup completed successfully!' as status;

-- Show current statistics
SELECT * FROM get_license_stats();

-- Show license overview (top 10)
SELECT 
    key_code,
    category,
    status,
    device_id IS NOT NULL as has_device,
    country,
    city,
    expiry_date,
    is_expired,
    usage_count,
    total_sessions
FROM license_overview
LIMIT 10;

-- Check for expired licenses
SELECT 
    key_code,
    category,
    status,
    expiry_date,
    last_access_date
FROM licenses
WHERE expiry_date < CURRENT_TIMESTAMP
AND status = 'ACTIVE'
ORDER BY expiry_date DESC;

-- Comments for documentation
COMMENT ON VIEW geographic_distribution IS 'Shows user distribution by country';
COMMENT ON VIEW license_overview IS 'Comprehensive view of all licenses with session counts and status';
COMMENT ON VIEW user_location_tracking IS 'Detailed location tracking for all user sessions';
COMMENT ON FUNCTION detect_suspicious_logins IS 'Detects potential license sharing by identifying logins from multiple countries or devices';
COMMENT ON FUNCTION get_license_stats IS 'Returns overall license system statistics';
COMMENT ON FUNCTION auto_expire_licenses IS 'Automatically blocks all expired licenses';

-- ================================================================================
-- SETUP COMPLETE!
-- ================================================================================
-- Your system now has:
-- ✅ All required database columns
-- ✅ Enhanced IP tracking (country, region, city, ISP, coordinates)
-- ✅ Security fixes (PENDING validation, activation_date checks)
-- ✅ Performance indices
-- ✅ Monitoring views
-- ✅ Admin functions
-- ✅ Automatic expiry enforcement
-- ================================================================================
