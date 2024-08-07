CREATE TABLE Weather (
    id INT AUTO_INCREMENT PRIMARY KEY,
    latitude VARCHAR(20) NOT NULL,
    longitude VARCHAR(20) NOT NULL,
    timestamp DATETIME NOT NULL,
    air_temperature FLOAT,
    air_temperature_80m FLOAT,
    air_temperature_100m FLOAT,
    air_temperature_1000hpa FLOAT,
    air_temperature_800hpa FLOAT,
    air_temperature_500hpa FLOAT,
    air_temperature_200hpa FLOAT,
    pressure FLOAT,
    cloud_cover FLOAT,
    current_direction FLOAT,
    current_speed FLOAT,
    gust FLOAT,
    humidity FLOAT,
    ice_cover FLOAT,
    precipitation FLOAT,
    snow_depth FLOAT,
    sea_level FLOAT,
    swell_direction FLOAT,
    swell_height FLOAT,
    swell_period FLOAT,
    secondary_swell_direction FLOAT,
    secondary_swell_height FLOAT,
    secondary_swell_period FLOAT,
    visibility FLOAT,
    water_temperature FLOAT,
    wave_direction FLOAT,
    wave_height FLOAT,
    wave_period FLOAT,
    wind_wave_direction FLOAT,
    wind_wave_height FLOAT,
    wind_wave_period FLOAT,
    wind_direction FLOAT,
    wind_direction_20m FLOAT,
    wind_direction_30m FLOAT,
    wind_direction_40m FLOAT,
    wind_direction_50m FLOAT,
    wind_direction_80m FLOAT,
    wind_direction_100m FLOAT,
    wind_direction_1000hpa FLOAT,
    wind_direction_800hpa FLOAT,
    wind_direction_500hpa FLOAT,
    wind_direction_200hpa FLOAT,
    wind_speed FLOAT,
    wind_speed_20m FLOAT,
    wind_speed_30m FLOAT,
    wind_speed_40m FLOAT,
    wind_speed_50m FLOAT,
    wind_speed_80m FLOAT,
    wind_speed_100m FLOAT,
    wind_speed_1000hpa FLOAT,
    wind_speed_800hpa FLOAT,
    wind_speed_500hpa FLOAT,
    wind_speed_200hpa FLOAT,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


-- solar
CREATE TABLE Solar (
    id INT AUTO_INCREMENT PRIMARY KEY,
    latitude VARCHAR(20) NOT NULL,
    longitude VARCHAR(20) NOT NULL,
    timestamp DATETIME NOT NULL,
    uv_index FLOAT,
    downward_short_wave_radiation_flux FLOAT,
    source VARCHAR(100),
    start_time DATETIME,
    end_time DATETIME,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
