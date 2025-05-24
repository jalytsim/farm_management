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
