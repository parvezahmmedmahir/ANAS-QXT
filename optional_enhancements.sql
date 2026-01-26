-- QUANTUM X PRO - OPTIONAL ENHANCEMENTS
-- Add features from previous system while keeping current security

-- 1. Add Foreign Key Constraints for Data Integrity
-- This ensures that if a license is deleted, all related sessions and activity are also deleted

DO $$ 
BEGIN
    -- Add foreign key to user_sessions if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_user_sessions_license'
    ) THEN
        ALTER TABLE user_sessions 
        ADD CONSTRAINT fk_user_sessions_license 
        FOREIGN KEY (license_key) REFERENCES licenses(key_code) ON DELETE CASCADE;
        RAISE NOTICE 'Added foreign key constraint to user_sessions';
    END IF;

    -- Add foreign key to user_activity if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_user_activity_license'
    ) THEN
        ALTER TABLE user_activity 
        ADD CONSTRAINT fk_user_activity_license 
        FOREIGN KEY (license_key) REFERENCES licenses(key_code) ON DELETE CASCADE;
        RAISE NOTICE 'Added foreign key constraint to user_activity';
    END IF;
END $$;

-- 2. Add Additional Performance Indices
CREATE INDEX IF NOT EXISTS idx_sessions_device_id ON user_sessions(device_id);
CREATE INDEX IF NOT EXISTS idx_sessions_login_time ON user_sessions(login_time DESC);
CREATE INDEX IF NOT EXISTS idx_activity_license_key ON user_activity(license_key);
CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON user_activity(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_licenses_last_access ON licenses(last_access_date DESC);

-- 3. Add Enhanced User Activity Columns (if not exist)
DO $$ 
BEGIN
    -- Add scrolls column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_activity' AND column_name='scrolls'
    ) THEN
        ALTER TABLE user_activity ADD COLUMN scrolls INTEGER DEFAULT 0;
        RAISE NOTICE 'Added scrolls column to user_activity';
    END IF;

    -- Add key_presses column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_activity' AND column_name='key_presses'
    ) THEN
        ALTER TABLE user_activity ADD COLUMN key_presses INTEGER DEFAULT 0;
        RAISE NOTICE 'Added key_presses column to user_activity';
    END IF;

    -- Add session_duration column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_activity' AND column_name='session_duration'
    ) THEN
        ALTER TABLE user_activity ADD COLUMN session_duration INTEGER DEFAULT 0;
        RAISE NOTICE 'Added session_duration column to user_activity';
    END IF;

    -- Add page_title column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='user_activity' AND column_name='page_title'
    ) THEN
        ALTER TABLE user_activity ADD COLUMN page_title TEXT;
        RAISE NOTICE 'Added page_title column to user_activity';
    END IF;
END $$;

-- 4. Create a View for Easy License Monitoring
CREATE OR REPLACE VIEW license_overview AS
SELECT 
    l.key_code,
    l.category,
    l.status,
    l.device_id,
    l.ip_address,
    l.usage_count,
    l.activation_date,
    l.last_access_date,
    l.expiry_date,
    l.expiry_date < CURRENT_TIMESTAMP as is_expired,
    (SELECT COUNT(*) FROM user_sessions WHERE license_key = l.key_code) as total_sessions,
    (SELECT MAX(login_time) FROM user_sessions WHERE license_key = l.key_code) as last_session
FROM licenses l
ORDER BY l.last_access_date DESC NULLS LAST;

-- 5. Create a View for User Activity Summary
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT 
    license_key,
    device_id,
    COUNT(*) as activity_reports,
    SUM(mouse_movements) as total_mouse_movements,
    SUM(clicks) as total_clicks,
    SUM(COALESCE(scrolls, 0)) as total_scrolls,
    SUM(COALESCE(key_presses, 0)) as total_key_presses,
    SUM(COALESCE(session_duration, 0)) as total_session_time,
    MAX(timestamp) as last_activity
FROM user_activity
GROUP BY license_key, device_id
ORDER BY last_activity DESC;

-- 6. Create Function to Clean Old Sessions (Optional Maintenance)
CREATE OR REPLACE FUNCTION cleanup_old_sessions(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions 
    WHERE login_time < CURRENT_TIMESTAMP - (days_to_keep || ' days')::INTERVAL;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 7. Create Function to Get License Statistics
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

-- Display Results
SELECT '✅ Enhancement script completed successfully!' as status;

-- Show current statistics
SELECT * FROM get_license_stats();

-- Show license overview (top 10)
SELECT 
    key_code,
    status,
    device_id IS NOT NULL as has_device,
    usage_count,
    total_sessions,
    last_session
FROM license_overview
LIMIT 10;

-- Comments for documentation
COMMENT ON VIEW license_overview IS 'Comprehensive view of all licenses with session counts and status';
COMMENT ON VIEW user_activity_summary IS 'Aggregated user activity metrics per license and device';
COMMENT ON FUNCTION cleanup_old_sessions IS 'Removes user session records older than specified days (default 90)';
COMMENT ON FUNCTION get_license_stats IS 'Returns overall license system statistics';
