-- CREATE TABLE farmdata (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     farm_id VARCHAR(50) NOT NULL,
--     crop_id INT NOT NULL,
--     land_type VARCHAR(255) NOT NULL,
--     tilled_land_size FLOAT NOT NULL,
--     planting_date DATE NOT NULL,
--     season INT NOT NULL,
--     quality VARCHAR(255) NOT NULL,
--     quantity INT NOT NULL,
--     harvest_date DATE NOT NULL,
--     expected_yield FLOAT NOT NULL,
--     actual_yield FLOAT NOT NULL,
--     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
--     channel_partner VARCHAR(255) NOT NULL,
--     destination_country VARCHAR(255) NOT NULL,
--     customer_name VARCHAR(255) NOT NULL,
--     date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
--     date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--     modified_by INT,
--     created_by INT,
--     FOREIGN KEY (farm_id) REFERENCES farm(farm_id) ON DELETE CASCADE,
--     FOREIGN KEY (crop_id) REFERENCES crop(id) ON DELETE CASCADE,
--     FOREIGN KEY (modified_by) REFERENCES user(id),
--     FOREIGN KEY (created_by) REFERENCES user(id)
-- -- );
-- CREATE TABLE farm (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     farm_id VARCHAR(50) NOT NULL,
--     name VARCHAR(255) NOT NULL,
--     subcounty VARCHAR(255) NOT NULL,
--     farmergroup_id INT NOT NULL,
--     district_id INT NOT NULL,
--     geolocation VARCHAR(255) NOT NULL,
--     phonenumber VARCHAR(20),
--     phonenumber2 VARCHAR(20),
--     date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
--     date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--     modified_by INT,
--     created_by INT,
--     FOREIGN KEY (farmergroup_id) REFERENCES farmergroup(id),
--     FOREIGN KEY (district_id) REFERENCES district(id),
--     FOREIGN KEY (modified_by) REFERENCES user(id),
--     FOREIGN KEY (created_by) REFERENCES user(id)
-- );
CREATE TABLE irrigation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crop_id INT NOT NULL,
    farm_id INT NOT NULL,
    irrigation_date DATE NOT NULL,
    water_applied FLOAT NOT NULL,  -- Amount of water applied in mm
    method VARCHAR(100) NOT NULL,  -- drip, sprinkler, flood, etc.
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    modified_by INT,
    created_by INT,
    FOREIGN KEY (crop_id) REFERENCES crop(id) ON DELETE CASCADE,
    FOREIGN KEY (farm_id) REFERENCES farm(id) ON DELETE CASCADE,
    FOREIGN KEY (modified_by) REFERENCES user(id),
    FOREIGN KEY (created_by) REFERENCES user(id)
);
CREATE TABLE cropcoefficient (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crop_id INT NOT NULL,
    stage VARCHAR(50) NOT NULL,  -- initial, mid-season, late-season, etc.
    kc_value FLOAT NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    modified_by INT,
    created_by INT,
    FOREIGN KEY (crop_id) REFERENCES crop(id) ON DELETE CASCADE,
    FOREIGN KEY (modified_by) REFERENCES user(id),
    FOREIGN KEY (created_by) REFERENCES user(id)
);
CREATE TABLE grade (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crop_id INT NOT NULL,
    grade_value VARCHAR(50) NOT NULL,
    description TEXT,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    modified_by INT,
    created_by INT,
    FOREIGN KEY (crop_id) REFERENCES crop(id) ON DELETE CASCADE,
    FOREIGN KEY (modified_by) REFERENCES user(id),
    FOREIGN KEY (created_by) REFERENCES user(id)
);
CREATE TABLE crop (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    weight FLOAT NOT NULL,
    category_id INT,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    modified_by INT,
    created_by INT,
    FOREIGN KEY (category_id) REFERENCES producecategory(id) ON DELETE CASCADE,
    FOREIGN KEY (modified_by) REFERENCES user(id),
    FOREIGN KEY (created_by) REFERENCES user(id)
);
-- CREATE TABLE producecategory (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     name VARCHAR(255) NOT NULL,
--     date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
--     date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--     modified_by INT,
--     created_by INT
-- );
-- CREATE TABLE user (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     username VARCHAR(150) NOT NULL UNIQUE,
--     email VARCHAR(150) NOT NULL UNIQUE,
--     password VARCHAR(150) NOT NULL,
--     phonenumber VARCHAR(20),
--     user_type VARCHAR(50) NOT NULL,
--     is_admin BOOLEAN DEFAULT FALSE,
--     date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
--     date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--     id_start VARCHAR(10)
-- );


ALTER TABLE crop 
MODIFY name VARCHAR(255) NOT NULL,
MODIFY weight FLOAT NOT NULL;

-- 2. Set default value and update mechanism for `date_created` and `date_updated`
ALTER TABLE crop 
MODIFY date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
MODIFY date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- 3. Add foreign key constraints for `category_id`, `modified_by`, and `created_by`
ALTER TABLE crop 
ADD CONSTRAINT fk_category_id 
    FOREIGN KEY (category_id) REFERENCES producecategory(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_modified_by 
    FOREIGN KEY (modified_by) REFERENCES user(id),
ADD CONSTRAINT fk_created_by 
    FOREIGN KEY (created_by) REFERENCES user(id);



-- Aty ndray ny maso

CREATE TABLE store (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    district VARCHAR(255) NOT NULL,
    store_type VARCHAR(50) NOT NULL DEFAULT 'agricultural',
    status BOOLEAN DEFAULT TRUE,
    phone_number VARCHAR(20),
    email VARCHAR(255),
    owner_id INT,
    farm_id INT,
    inventory_count INT DEFAULT 0,
    sales_count INT DEFAULT 0,
    revenue FLOAT DEFAULT 0.0,
    last_stock_update DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    modified_by INT,
    FOREIGN KEY (owner_id) REFERENCES user(id) ON DELETE SET NULL,
    FOREIGN KEY (farm_id) REFERENCES farm(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES user(id) ON DELETE SET NULL,
    FOREIGN KEY (modified_by) REFERENCES user(id) ON DELETE SET NULL
);

CREATE TABLE product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    stock INT DEFAULT 0,
    store_id INT NOT NULL,
    FOREIGN KEY (store_id) REFERENCES store(id) ON DELETE CASCADE
);


-- ################ATO NDRAY###############################
CREATE TABLE `featureprice` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `feature_name` VARCHAR(100) NOT NULL UNIQUE,
    `price` FLOAT NOT NULL
);


CREATE TABLE `paidfeatureaccess` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT,
    `guest_phone_number` VARCHAR(20),
    `feature_name` VARCHAR(100) NOT NULL,
    `txn_id` VARCHAR(100) NOT NULL UNIQUE,
    `payment_status` VARCHAR(50) DEFAULT 'pending',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `access_expires_at` DATETIME DEFAULT NULL,
    `usage_left` INT DEFAULT NULL,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE SET NULL
);

ALTER TABLE featureprice
ADD COLUMN duration_days INT NULL AFTER price,
ADD COLUMN usage_limit INT NULL AFTER duration_days;



CREATE TABLE eudr_statements (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Identifiants
    internal_reference_number VARCHAR(255) NOT NULL,
    dds_identifier VARCHAR(255) UNIQUE,
    verification_number VARCHAR(255),

    -- Informations générales
    activity_type VARCHAR(50),
    border_cross_country VARCHAR(10),
    country_of_activity VARCHAR(100),
    comment TEXT,
    geo_location_confidential BOOLEAN DEFAULT FALSE,

    -- Informations opérateur
    operator_identifier_type VARCHAR(100),
    operator_identifier_value VARCHAR(255),
    operator_name VARCHAR(255),
    operator_country VARCHAR(100),
    operator_address VARCHAR(255),
    operator_email VARCHAR(255),
    operator_phone VARCHAR(50),

    -- Informations produit
    description_of_goods VARCHAR(255),
    hs_heading VARCHAR(50),
    scientific_name VARCHAR(255),
    common_name VARCHAR(255),

    -- Mesures du produit
    volume FLOAT,
    net_weight FLOAT,
    supplementary_unit VARCHAR(50),
    supplementary_unit_qualifier VARCHAR(50),

    -- Producteurs (GeoJSON ou base64 encodé)
    producers_json LONGTEXT,

    -- Logs de dernière réponse (optionnel)
    last_response_code INT,
    last_response_text LONGTEXT,

    -- Dates de création et de mise à jour
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);




-- 1️⃣ Création de la nouvelle table farmreport
CREATE TABLE farmreport (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    project_area VARCHAR(255),
    country_deforestation_risk_level VARCHAR(255),
    radd_alert VARCHAR(255),
    tree_cover_loss VARCHAR(255),
    forest_cover_2020 VARCHAR(255),
    eudr_compliance_assessment VARCHAR(255),
    protected_area_status VARCHAR(255),
    cover_extent_summary_b64 LONGTEXT,
    tree_cover_drivers VARCHAR(255),
    cover_extent_area VARCHAR(255),
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_farmreport_farm FOREIGN KEY (farm_id)
        REFERENCES farm(id)
        ON DELETE CASCADE
);

-- 2️⃣ (Optionnel) Si tu veux t’assurer que chaque ferme n’a qu’un seul rapport :
ALTER TABLE farmreport
ADD UNIQUE KEY unique_farm_report (farm_id);

CREATE TABLE certificate (
    id INT AUTO_INCREMENT PRIMARY KEY,
    certificate_id VARCHAR(100) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    certificate_type VARCHAR(50) NOT NULL,
    total_farms INT NOT NULL,
    compliant_100_count INT DEFAULT 0,
    likely_compliant_count INT DEFAULT 0,
    not_compliant_count INT DEFAULT 0,
    compliant_100_percent FLOAT DEFAULT 0.0,
    likely_compliant_percent FLOAT DEFAULT 0.0,
    not_compliant_percent FLOAT DEFAULT 0.0,
    overall_compliance_rate FLOAT DEFAULT 0.0,
    title VARCHAR(255) NOT NULL,
    issue_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_until DATETIME NOT NULL,
    pdf_data_base64 LONGTEXT,
    qr_code_data TEXT,
    status VARCHAR(50) DEFAULT 'active',
    download_count INT DEFAULT 0,
    last_downloaded DATETIME,
    ip_address VARCHAR(50),
    user_agent VARCHAR(255),
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    modified_by INT,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES user(id) ON DELETE SET NULL,
    FOREIGN KEY (modified_by) REFERENCES user(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_certificate_id (certificate_id),
    INDEX idx_status (status),
    INDEX idx_issue_date (issue_date),
    INDEX idx_certificate_type (certificate_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
