-- Drop tables if they exist
DROP TABLE IF EXISTS point;
DROP TABLE IF EXISTS farmdata;
DROP TABLE IF EXISTS farm;
DROP TABLE IF EXISTS crop;
DROP TABLE IF EXISTS soildata;
DROP TABLE IF EXISTS producecategory;
DROP TABLE IF EXISTS farmergroup;
DROP TABLE IF EXISTS forest;
DROP TABLE IF EXISTS district;
DROP TABLE IF EXISTS user;

-- Create tables if they do not exist
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(150) NOT NULL,
    phonenumber VARCHAR(20),
    user_type VARCHAR(50) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS district (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    region VARCHAR(255) NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS farmergroup (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS producecategory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    grade INT NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS soildata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    district_id INT NOT NULL,
    internal_id INT NOT NULL,
    device VARCHAR(255) NOT NULL,
    owner VARCHAR(255) NOT NULL,
    nitrogen FLOAT NOT NULL,
    phosphorus FLOAT NOT NULL,
    potassium FLOAT NOT NULL,
    ph FLOAT NOT NULL,
    temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    conductivity FLOAT NOT NULL,
    signal_level FLOAT NOT NULL,
    date DATE NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (district_id) REFERENCES district (id)
);

CREATE TABLE IF NOT EXISTS crop (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    weight FLOAT NOT NULL,
    category_id INT NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES producecategory (id)
);

CREATE TABLE IF NOT EXISTS farm (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    subcounty VARCHAR(255) NOT NULL,
    farmergroup_id INT NOT NULL,
    district_id INT NOT NULL,
    geolocation VARCHAR(255) NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX (farm_id),  -- Adding a unique index for farm_id
    FOREIGN KEY (farmergroup_id) REFERENCES farmergroup (id),
    FOREIGN KEY (district_id) REFERENCES district (id)
);

CREATE TABLE IF NOT EXISTS farmdata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id VARCHAR(50) NOT NULL,
    crop_id INT NOT NULL,
    land_type VARCHAR(255) NOT NULL,
    tilled_land_size FLOAT NOT NULL,
    planting_date DATE NOT NULL,
    season INT NOT NULL,
    quality VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    harvest_date DATE NOT NULL,
    expected_yield FLOAT NOT NULL,
    actual_yield FLOAT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    channel_partner VARCHAR(255) NOT NULL,
    destination_country VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (farm_id) REFERENCES farm (farm_id),
    FOREIGN KEY (crop_id) REFERENCES crop (id)
);

CREATE TABLE IF NOT EXISTS forest (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS point (
    id INT AUTO_INCREMENT PRIMARY KEY,
    longitude FLOAT NOT NULL,
    latitude FLOAT NOT NULL,
    owner_type ENUM('forest', 'farmer') NOT NULL,
    forest_id INT,
    farmer_id VARCHAR(50),
    district_id INT NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (forest_id) REFERENCES forest (id),
    FOREIGN KEY (farmer_id) REFERENCES farm (farm_id),
    FOREIGN KEY (district_id) REFERENCES district (id),
    CHECK (
        (owner_type = 'forest' AND forest_id IS NOT NULL AND farmer_id IS NULL) OR 
        (owner_type = 'farmer' AND farmer_id IS NOT NULL AND forest_id IS NULL)
    )
);
