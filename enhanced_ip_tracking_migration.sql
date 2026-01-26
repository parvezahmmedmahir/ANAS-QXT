-- QUANTUM X PRO - ENHANCED IP TRACKING UPDATE
-- Adds comprehensive geolocation tracking to match previous system quality

-- Step 1: Add enhanced geolocation columns to user_sessions table
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

    -- Add organization column (ISP organization)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_sessions' AND column_name='organization'
    ) THEN
        ALTER TABLE user_sessions ADD COLUMN organization TEXT;
        RAISE NOTICE 'Added organization column to user_sessions';
    END IF;
END $$;

-- Step 2: Add enhanced geolocation columns to licenses table for quick reference
DO $$ 
BEGIN
    -- Add country to licenses (last known country)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='licenses' AND column_name='country'
    ) THEN
        ALTER TABLE licenses ADD COLUMN country TEXT;
        RAISE NOTICE 'Added country column to licenses';
    END IF;

    -- Add city to licenses (last known city)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='licenses' AND column_name='city'
    ) THEN
        ALTER TABLE licenses ADD COLUMN city TEXT;
        RAISE NOTICE 'Added city column to licenses';
    END IF;

    -- Add timezone to licenses
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='licenses' AND column_name='timezone_geo'
    ) THEN
        ALTER TABLE licenses ADD COLUMN timezone_geo TEXT;
        RAISE NOTICE 'Added timezone_geo column to licenses';
    END IF;
END $$;

-- Step 3: Create indices for geolocation queries
CREATE INDEX IF NOT EXISTS idx_sessions_country ON user_sessions(country);
CREATE INDEX IF NOT EXISTS idx_sessions_city ON user_sessions(city);
CREATE INDEX IF NOT EXISTS idx_sessions_ip ON user_sessions(ip_address);
CREATE INDEX IF NOT EXISTS idx_licenses_country ON licenses(country);

-- Step 4: Create view for geographic distribution
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

-- Step 5: Create view for detailed user location tracking
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

-- Step 6: Create function to detect suspicious activity (multiple countries)
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

-- Display summary
SELECT '✅ Enhanced IP tracking migration completed!' as status;

-- Show geographic distribution
SELECT * FROM geographic_distribution LIMIT 10;

-- Check for suspicious activity in last 24 hours
SELECT * FROM detect_suspicious_logins(24);

-- Comments
COMMENT ON VIEW geographic_distribution IS 'Shows user distribution by country';
COMMENT ON VIEW user_location_tracking IS 'Detailed location tracking for all user sessions';
COMMENT ON FUNCTION detect_suspicious_logins IS 'Detects potential license sharing by identifying logins from multiple countries or devices';
