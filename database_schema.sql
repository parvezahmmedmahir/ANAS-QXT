-- QUANTUM X PRO - COMPLETE DATABASE SCHEMA
-- Copy this entire file and run it in your Supabase SQL Editor

-- 1. Device Fingerprints Table - Deep hardware tracking
CREATE TABLE IF NOT EXISTS device_fingerprints (
    id SERIAL PRIMARY KEY,
    device_id TEXT UNIQUE NOT NULL,
    license_key TEXT,
    browser_fingerprint TEXT,
    canvas_fingerprint TEXT,
    webgl_renderer TEXT,
    screen_resolution TEXT,
    hardware_cores INTEGER,
    device_memory INTEGER,
    platform TEXT,
    language TEXT,
    timezone TEXT,
    plugins TEXT,
    fonts TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. IP Geolocation Table - Network & Location tracking
CREATE TABLE IF NOT EXISTS ip_geolocation (
    id SERIAL PRIMARY KEY,
    device_id TEXT NOT NULL,
    license_key TEXT,
    ip_address TEXT,
    country TEXT,
    region TEXT,
    city TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    isp TEXT,
    organization TEXT,
    timezone_geo TEXT,
    postal_code TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Browser Telemetry Table - Real-time browser data
CREATE TABLE IF NOT EXISTS browser_telemetry (
    id SERIAL PRIMARY KEY,
    device_id TEXT NOT NULL,
    license_key TEXT,
    browser_name TEXT,
    browser_version TEXT,
    os_name TEXT,
    os_version TEXT,
    is_mobile BOOLEAN,
    is_tablet BOOLEAN,
    screen_width INTEGER,
    screen_height INTEGER,
    color_depth INTEGER,
    pixel_ratio DECIMAL(3, 2),
    touch_support BOOLEAN,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Network Information Table - Connection tracking
CREATE TABLE IF NOT EXISTS network_info (
    id SERIAL PRIMARY KEY,
    device_id TEXT NOT NULL,
    license_key TEXT,
    connection_type TEXT,
    effective_type TEXT,
    downlink DECIMAL(5, 2),
    rtt INTEGER,
    save_data BOOLEAN,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Auto-Login Cache Table - For instant recognition
CREATE TABLE IF NOT EXISTS auto_login_cache (
    device_id TEXT PRIMARY KEY,
    license_key TEXT NOT NULL,
    last_ip TEXT,
    last_fingerprint TEXT,
    trust_score INTEGER DEFAULT 100,
    last_verified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    auto_login_enabled BOOLEAN DEFAULT TRUE,
    expiry_date TIMESTAMP
);

-- Create indexes for ultra-fast lookups
CREATE INDEX IF NOT EXISTS idx_sessions_device ON user_sessions(device_id);
CREATE INDEX IF NOT EXISTS idx_sessions_key ON user_sessions(license_key);
CREATE INDEX IF NOT EXISTS idx_sessions_timestamp ON user_sessions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_activity_device ON user_activity(device_id);
CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON user_activity(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_fingerprints_device ON device_fingerprints(device_id);
CREATE INDEX IF NOT EXISTS idx_fingerprints_key ON device_fingerprints(license_key);
CREATE INDEX IF NOT EXISTS idx_geo_device ON ip_geolocation(device_id);
CREATE INDEX IF NOT EXISTS idx_geo_ip ON ip_geolocation(ip_address);
CREATE INDEX IF NOT EXISTS idx_telemetry_device ON browser_telemetry(device_id);
CREATE INDEX IF NOT EXISTS idx_network_device ON network_info(device_id);
CREATE INDEX IF NOT EXISTS idx_autologin_device ON auto_login_cache(device_id);
CREATE INDEX IF NOT EXISTS idx_autologin_key ON auto_login_cache(license_key);

-- Comments for documentation
COMMENT ON TABLE device_fingerprints IS 'Comprehensive hardware fingerprints for device recognition';
COMMENT ON TABLE ip_geolocation IS 'User location and network provider tracking';
COMMENT ON TABLE browser_telemetry IS 'Real-time browser and OS information';
COMMENT ON TABLE network_info IS 'Network connection quality and type';
COMMENT ON TABLE auto_login_cache IS 'Enables instant auto-login for recognized valid devices';
