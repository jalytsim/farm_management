DROP TABLE IF EXISTS farmData;
DROP TABLE IF EXISTS farm;
DROP TABLE IF EXISTS crop;
DROP TABLE IF EXISTS soilData;
DROP TABLE IF EXISTS produceCategory;
DROP TABLE IF EXISTS farmergroup;
DROP TABLE IF EXISTS district;

DROP TABLE IF EXISTS user;
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS district (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    region VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS farmergroup (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    description TEXT
);

CREATE TABLE IF NOT EXISTS produceCategory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    grade INT
);

CREATE TABLE IF NOT EXISTS soilData (
    id INT AUTO_INCREMENT PRIMARY KEY,
    district_id INT,
    internal_id INT,
    device VARCHAR(255),
    owner VARCHAR(255),
    nitrogen FLOAT,
    phosphorus FLOAT,
    potassium FLOAT,
    ph FLOAT,
    temperature FLOAT,
    humidity FLOAT,
    conductivity FLOAT,
    signal_level FLOAT,
    date DATE,
    FOREIGN KEY (district_id) REFERENCES district(id)
);

CREATE TABLE IF NOT EXISTS crop (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    weight FLOAT,
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES produceCategory(id)
);

CREATE TABLE IF NOT EXISTS farm (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    subcounty VARCHAR(255),
    farmergroup_id INT,
    district_id INT,
    geolocation VARCHAR(255),
    FOREIGN KEY (district_id) REFERENCES district(id),
    FOREIGN KEY (farmergroup_id) REFERENCES farmergroup(id)
);

CREATE TABLE IF NOT EXISTS farmData (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT,
    crop_id INT,
    tilled_land_size FLOAT,
    planting_date DATE,
    season INT,
    quality VARCHAR(255),
    quantity INT,
    harvest_date DATE,
    expected_yield FLOAT,
    actual_yield FLOAT,
    timestamp TIMESTAMP,
    channel_partner VARCHAR(255),
    destination_country VARCHAR(255),
    customer_name VARCHAR(255),
    FOREIGN KEY (farm_id) REFERENCES farm(id),
    FOREIGN KEY (crop_id) REFERENCES crop(id)
);

DROP TABLE IF EXISTS point;

CREATE TABLE IF NOT EXISTS point (
    id INT AUTO_INCREMENT PRIMARY KEY,
    longitude FLOAT,
    latitude FLOAT,
    owner_type ENUM('forest', 'farmer') NOT NULL,
    forest_id INT,
    farmer_id INT,
    district_id INT,
    FOREIGN KEY (district_id) REFERENCES district(id),
    FOREIGN KEY (forest_id) REFERENCES forest(id),
    FOREIGN KEY (farmer_id) REFERENCES farm(id),
    CHECK (
        (owner_type = 'forest' AND forest_id IS NOT NULL AND farmer_id IS NULL) OR
        (owner_type = 'farmer' AND farmer_id IS NOT NULL AND forest_id IS NULL)
    )
);

DROP TABLE IF EXISTS forest;

CREATE TABLE IF NOT EXISTS forest (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

INSERT INTO forest (name) VALUES ('Forest 1');
INSERT INTO point (longitude, latitude, owner_type, forest_id, farmer_id) VALUES
(0.3617533, 32.650461, 'forest', 1, NULL),
(0.361352, 32.651511, 'forest', 1, NULL),
(0.361054, 32.652137, 'forest', 1, NULL),
(0.36098, 32.652074, 'forest', 1, NULL),
(0.361107, 32.651695, 'forest', 1, NULL),
(0.361494, 32.651609, 'forest', 1, NULL),
(0.361352, 32.651511, 'forest', 1, NULL),
(0.360711, 32.651087, 'forest', 1, NULL),
(0.361618, 32.650872, 'forest', 1, NULL),
(0.361575, 32.651043, 'forest', 1, NULL),
(0.360818, 32.651515, 'forest', 1, NULL),
(0.361183, 32.651237, 'forest', 1, NULL),
(0.361116, 32.65267, 'forest', 1, NULL),
(0.36114, 32.652351, 'forest', 1, NULL),
(0.36126, 32.650847, 'forest', 1, NULL),
(0.361496, 32.650783, 'forest', 1, NULL);

LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\ugandaDistrict.csv'
INTO TABLE district
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(name, region);

INSERT INTO produceCategory (name, grade) VALUES
('Maize', 1),
('Beans', 2),
('Coffee', 3),
('Cassava', 1),
('Rice', 2),
('Bananas', 3);

INSERT INTO farmergroup (name, description) VALUES
('Farmers Cooperative Society', 'A cooperative society of farmers'),
('Women Farmers Association', 'An association of women farmers'),
('Young Farmers Group', 'A group of young farmers');

INSERT INTO farm (name, subcounty, farmergroup_id, district_id, geolocation) VALUES
('John Doe Farm', 'Kawempe', 1, 1, '0.3163,32.5822'),
('Jane Smith Farm', 'Gulu', 2, 2, '2.7809,32.2995'),
('Peter Kato Farm', 'Mbale', 3, 3, '1.0647,34.1797'),
('Sarah Nalubega Farm', 'Makindye', 1, 4, '0.2986,32.6235'),
('David Omondi Farm', 'Nwoya', 2, 5, '2.6249,31.3952'),
('Grace Nakato Farm', 'Bubulo', 3, 6, '1.0722,34.1691'),
('Joseph Ssempala Farm', 'Rubaga', 1, 7, '0.2947,32.5521'),
('Mercy Auma Farm', 'Pader', 2, 8, '2.7687,33.2428'),
('Andrew Wabwire Farm', 'Manafwa', 3, 9, '1.1714,34.3447'),
('Harriet Namutebi Farm', 'Nakawa', 1, 10, '0.3153,32.6153'),
('Emmanuel Ojok Farm', 'Lira', 2, 11, '2.2481,32.8997'),
('Joyce Nakazibwe Farm', 'Sironko', 3, 12, '1.2236,34.3874'),
('Richard Kizza Farm', 'Nansana', 1, 13, '0.3652,32.5274'),
('Sarah Nambooze Farm', 'Kitgum', 2, 14, '3.3017,32.8737'),
('Godfrey Sserwadda Farm', 'Kapchorwa', 3, 15, '1.3962,34.4507'),
('Mary Nalule Farm', 'Wakiso', 1, 16, '0.4054,32.4594'),
('Isaac Ongom Farm', 'Amuru', 2, 17, '2.8231,31.4344'),
('Agnes Atim Farm', 'Bududa', 3, 18, '1.0614,34.3294'),
('Charles Odoi Farm', 'Kira', 1, 19, '0.3673,32.6159'),
('Florence Nakimera Farm', 'Adjumani', 2, 20, '3.3812,31.7989'),
('Alice Achieng Farm', 'Apac', 1, 21, '1.9730,32.5380'),
('Brian Musisi Farm', 'Bukedea', 2, 22, '1.3494,34.0636'),
('Catherine Namubiru Farm', 'Bushenyi', 3, 23, '0.5854,30.2160'),
('Daniel Odongo Farm', 'Busia', 1, 24, '0.4544,34.0735'),
('Eunice Nakato Farm', 'Buwenge', 2, 25, '0.4582,33.2142'),
('Francis Ssempijja Farm', 'Entebbe', 3, 26, '0.0527,32.4463'),
('Grace Nakayenga Farm', 'Fort Portal', 1, 27, '0.6711,30.2755'),
('Henry Kiwanuka Farm', 'Hoima', 2, 28, '1.4356,31.3586'),
('Irene Nankya Farm', 'Iganga', 3, 29, '0.6093,33.4862'),
('Josephine Nabukenya Farm', 'Isingiro', 1, 30, '0.7587,30.9399'),
('Kenneth Odhiambo Farm', 'Jinja', 1, 31, '0.4244,33.2041'),
('Lilian Nalwanga Farm', 'Kabale', 2, 32, '1.2504,29.9857'),
('Moses Ochieng Farm', 'Kabarole', 3, 33, '0.6107,30.2778'),
('Nancy Nantume Farm', 'Kabingo', 1, 34, '0.0836,32.4789'),
('Oscar Okoth Farm', 'Kabwohe', 2, 35, '0.8084,30.8014'),
('Patricia Namutebi Farm', 'Kajansi', 3, 36, '0.1519,32.5078'),
('Quincy Odongo Farm', 'Kaliro', 1, 37, '0.9031,33.5097'),
('Rebecca Nakato Farm', 'Kamuli', 2, 38, '0.9479,33.1197'),
('Stephen Ssemwogerere Farm', 'Kanungu', 3, 39, '0.9574,29.7980'),
('Teresa Nakabugo Farm', 'Kapchorwa', 1, 40, '1.3696,34.4027'),
('Umar Ssebunya Farm', 'Kasese', 2, 41, '0.1830,30.0665'),
('Violet Namutebi Farm', 'Katakwi', 3, 42, '1.8910,33.9756'),
('William Odoi Farm', 'Kayunga', 1, 43, '0.7021,32.8874'),
('Xavier Ouma Farm', 'Kibaale', 2, 44, '0.8830,31.3970'),
('Yusuf Ssebadduka Farm', 'Kiboga', 3, 45, '0.7880,31.0886'),
('Zainabu Nansubuga Farm', 'Kisoro', 1, 46, '1.3521,29.6935'),
('Abdul Nsereko Farm', 'Kitagata', 2, 47, '0.6346,30.2557'),
('Betty Nandawula Farm', 'Kitgum', 3, 48, '3.2783,32.8842'),
('Charles Okello Farm', 'Koboko', 1, 49, '3.4114,30.9601'),
('Dorothy Nakyobe Farm', 'Kotido', 2, 50, '3.0132,34.1336'),
('Alice Aol Farm', 'Kumi', 1, 51, '1.4583,33.9365'),
('Brian Okoth Farm', 'Kyenjojo', 2, 52, '0.6239,30.6206'),
('Catherine Nambi Farm', 'Lira', 3, 53, '2.2358,32.9090'),
('Daniel Opolot Farm', 'Luwero', 1, 54, '0.8499,32.4737'),
('Eunice Nabadda Farm', 'Lwengo', 2, 55, '0.4168,31.4114'),
('Francis Ongom Farm', 'Masaka', 3, 56, '0.3153,31.7133'),
('Grace Nakitende Farm', 'Masindi', 1, 57, '1.6736,31.7092'),
('Henry Owor Farm', 'Mayuge', 2, 58, '0.4603,33.4621'),
('Irene Nakanjako Farm', 'Mbale', 3, 59, '1.0647,34.1797'),
('Josephine Namatovu Farm', 'Mbarara', 1, 60, '0.6098,30.6485'),
('Kenneth Odeke Farm', 'Mitooma', 2, 61, '0.6166,30.0763'),
('Lilian Auma Farm', 'Moroto', 3, 62, '2.4956,34.6751'),
('Moses Okello Farm', 'Moyo', 1, 63, '3.6333,31.7167'),
('Nancy Nabayego Farm', 'Mpigi', 2, 64, '0.2254,32.3133'),
('Oscar Otema Farm', 'Mubende', 3, 65, '0.5901,31.3904'),
('Patricia Nakazibwe Farm', 'Mukono', 1, 66, '0.3536,32.7554'),
('Quincy Ojok Farm', 'Nakapiripirit', 2, 67, '1.8262,34.7172'),
('Rebecca Nabirye Farm', 'Nakaseke', 3, 68, '0.7519,32.3631'),
('Stephen Sserwadda Farm', 'Nakasongola', 1, 69, '1.3084,32.4587'),
('Teresa Nalubega Farm', 'Nebbi', 2, 70, '2.4758,31.0993'),
('Umar Okello Farm', 'Ngora', 3, 71, '1.4314,33.7065'),
('Violet Nakyobe Farm', 'Ntoroko', 1, 72, '1.0386,30.4329'),
('William Ogenrwot Farm', 'Ntungamo', 2, 73, '0.8769,30.2707'),
('Xavier Odong Farm', 'Pakwach', 3, 74, '2.4544,31.4704'),
('Yusuf Ssekandi Farm', 'Pallisa', 1, 75, '1.1455,33.7092');



INSERT INTO farm (name, subcounty, farmergroup_id, district_id, geolocation) VALUES
('John Doe Farm', 'Kawempe', 1, 76, '0.3163,32.5822'),
('Jane Smith Farm', 'Gulu', 2, 77, '2.7809,32.2995'),
('Peter Kato Farm', 'Mbale', 3, 78, '1.0647,34.1797'),
('Sarah Nalubega Farm', 'Makindye', 1, 79, '0.2986,32.6235'),
('David Omondi Farm', 'Nwoya', 2, 80, '2.6249,31.3952'),
('Grace Nakato Farm', 'Bubulo', 3, 81, '1.0722,34.1691'),
('Joseph Ssempala Farm', 'Rubaga', 1, 82, '0.2947,32.5521'),
('Mercy Auma Farm', 'Pader', 2, 83, '2.7687,33.2428'),
('Andrew Wabwire Farm', 'Manafwa', 3,84 , '1.1714,34.3447'),
('Harriet Namutebi Farm', 'Nakawa', 1, 85, '0.3153,32.6153'),
('Emmanuel Ojok Farm', 'Lira', 2, 86, '2.2481,32.8997'),
('Joyce Nakazibwe Farm', 'Sironko', 3, 87, '1.2236,34.3874'),
('Richard Kizza Farm', 'Nansana', 1, 88, '0.3652,32.5274'),
('Sarah Nambooze Farm', 'Kitgum', 2, 89, '3.3017,32.8737'),
('Godfrey Sserwadda Farm', 'Kapchorwa', 3, 90, '1.3962,34.4507'),
('Mary Nalule Farm', 'Wakiso', 1, 91, '0.4054,32.4594'),
('Isaac Ongom Farm', 'Amuru', 2, 92, '2.8231,31.4344'),
('Agnes Atim Farm', 'Bududa', 3, 93, '1.0614,34.3294'),
('Charles Odoi Farm', 'Kira', 1, 94, '0.3673,32.6159'),
('Florence Nakimera Farm', 'Adjumani', 2, 97, '3.3812,31.7989'),
('Alice Achieng Farm', 'Apac', 1, 98, '1.9730,32.5380'),
('Brian Musisi Farm', 'Bukedea', 2, 99, '1.3494,34.0636'),
('Catherine Namubiru Farm', 'Bushenyi', 3, 100, '0.5854,30.2160'),
('Daniel Odongo Farm', 'Busia', 1, 101, '0.4544,34.0735'),
('Eunice Nakato Farm', 'Buwenge', 2, 102, '0.4582,33.2142'),
('Francis Ssempijja Farm', 'Entebbe', 3, 103, '0.0527,32.4463'),
('Grace Nakayenga Farm', 'Fort Portal', 1, 104, '0.6711,30.2755'),
('Henry Kiwanuka Farm', 'Hoima', 2, 105, '1.4356,31.3586'),
('Irene Nankya Farm', 'Iganga', 3, 106, '0.6093,33.4862'),
('Josephine Nabukenya Farm', 'Isingiro', 1, 107, '0.7587,30.9399'),
('Kenneth Odhiambo Farm', 'Jinja', 1, 108, '0.4244,33.2041'),
('Lilian Nalwanga Farm', 'Kabale', 2, 109, '1.2504,29.9857'),
('Moses Ochieng Farm', 'Kabarole', 3, 110, '0.6107,30.2778'),
('Nancy Nantume Farm', 'Kabingo', 1, 111, '0.0836,32.4789'),
('Oscar Okoth Farm', 'Kabwohe', 2, 112, '0.8084,30.8014'),
('Patricia Namutebi Farm', 'Kajansi', 3, 113, '0.1519,32.5078'),
('Quincy Odongo Farm', 'Kaliro', 1, 114, '0.9031,33.5097'),
('Rebecca Nakato Farm', 'Kamuli', 2, 115, '0.9479,33.1197'),
('Stephen Ssemwogerere Farm', 'Kanungu', 3, 116, '0.9574,29.7980'),
('Teresa Nakabugo Farm', 'Kapchorwa', 1, 117, '1.3696,34.4027'),
('Umar Ssebunya Farm', 'Kasese', 2, 118, '0.1830,30.0665'),
('Violet Namutebi Farm', 'Katakwi', 3, 119, '1.8910,33.9756'),
('William Odoi Farm', 'Kayunga', 1, 120, '0.7021,32.8874'),
('Xavier Ouma Farm', 'Kibaale', 2, 121, '0.8830,31.3970'),
('Yusuf Ssebadduka Farm', 'Kiboga', 3, 122, '0.7880,31.0886'),
('Zainabu Nansubuga Farm', 'Kisoro', 1, 123, '1.3521,29.6935'),
('Abdul Nsereko Farm', 'Kitagata', 2, 124, '0.6346,30.2557'),
('Betty Nandawula Farm', 'Kitgum', 3, 125, '3.2783,32.8842');


INSERT INTO crop (name, weight, category_id) VALUES
('Maize', 50.0, 1),
('Beans', 10.0, 2),
('Coffee', 25.0, 3),
('Cassava', 30.0, 4),
('Rice', 20.0, 5),
('Bananas', 15.0, 6),
('Coffee Arabica', 25.0, 1),
('Coffee Robusta', 20.0, 2),
('Tea', 25.0, 4),
('Soybean', 20.0, 3);

INSERT INTO farm (name, subcounty, farmergroup_id, district_id, geolocation) VALUES
('Tea farmer', 'Nebbi', 2, 84, '2.4697,31.1028'),
('Soybean Esperito', 'Ntungamo', 3, 23, '-0.8794,30.2647');

INSERT INTO farmdata (farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES
(124, 7, 2.5, '2023-03-15', 1, 'Good', 100, '2023-07-15', 2500.0, 2300.0, '2023-07-15 12:00:00', 'Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(125, 8, 1.0, '2023-03-20', 1, 'Excellent', 50, '2023-07-20', 500.0, 480.0, '2023-07-20 12:00:00', 'Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(126, 7, 3.5, '2023-03-15', 1, 'Good', 100, '2023-07-15', 2500.0, 2300.0, '2023-07-15 12:00:00', 'Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(126, 8, 1.5, '2023-03-15', 1, 'Good', 50, '2023-07-15', 2500.0, 2300.0, '2023-07-15 12:00:00', 'Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd');
INSERT INTO farmdata (farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES
(127, 9, 5.5, '2023-03-15', 1, 'Good', 100, '2023-07-15', 2500.0, 2300.0, '2023-07-15 12:00:00', 'Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(127, 9, 4.0, '2023-03-20', 1, 'Excellent', 50, '2023-07-20', 500.0, 480.0, '2023-07-20 12:00:00', 'Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(128, 10, 2.5, '2023-03-15', 1, 'Good', 100, '2023-07-15', 2500.0, 2300.0, '2023-07-15 12:00:00', 'Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(128, 10, 3.5, '2023-03-15', 1, 'Good', 50, '2023-07-15', 2500.0, 2300.0, '2023-07-15 12:00:00', 'Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd');


INSERT INTO produceCategory (name, grade) VALUES
('Coffee Arabica', 5),
('Coffee Robusta', 4);

INSERT INTO farmData (farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name)
VALUES
(11,1,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500.0,2300.0,'2023-07-15 12:00:00', 'Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(21,2,1.0,'2023-03-20',1,'Fair',50,'2023-07-20',500.0,480.0,'2023-07-20 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(32,3,0.5,'2023-04-01',1,'Good',20,'2023-09-01',500.0,480.0,'2023-09-01 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
-- Sample data for farmData
INSERT INTO farmData (farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp) VALUES
(1, 1, 2.5, '2023-03-15', 1, 'Good', 100, '2023-07-15', 2500.0, 2300.0, '2023-07-15 12:00:00'),
(1, 2, 1.0, '2023-03-20', 1, 'Fair', 50, '2023-07-20', 500.0, 480.0, '2023-07-20 12:00:00'),
(2, 3, 0.5, '2023-04-01', 1, 'Good', 20, '2023-09-01', 500.0, 480.0, '2023-09-01 12:00:00'),
(2, 4, 1.0, '2023-04-05', 1, 'Good', 30, '2023-09-05', 900.0, 880.0, '2023-09-05 12:00:00'),
(3, 5, 0.8, '2023-04-10', 1, 'Fair', 40, '2023-09-10', 800.0, 780.0, '2023-09-10 12:00:00'),
(3, 6, 0.3, '2023-04-15', 1, 'Excellent', 15, '2023-09-15', 225.0, 220.0, '2023-09-15 12:00:00'),
(4, 1, 2.0, '2023-03-15', 1, 'Good', 80, '2023-07-15', 2000.0, 1900.0, '2023-07-15 12:00:00'),
(4, 2, 0.8, '2023-03-20', 1, 'Fair', 40, '2023-07-20', 400.0, 380.0, '2023-07-20 12:00:00'),
(5, 3, 0.4, '2023-04-01', 1, 'Good', 15, '2023-09-01', 375.0, 370.0, '2023-09-01 12:00:00'),
(5, 4, 0.7, '2023-04-05', 1, 'Good', 25, '2023-09-05', 750.0, 740.0, '2023-09-05 12:00:00'),
(6, 5, 0.6, '2023-04-10', 1, 'Fair', 30, '2023-09-10', 600.0, 580.0, '2023-09-10 12:00:00'),
(6, 6, 0.2, '2023-04-15', 1, 'Excellent', 10, '2023-09-15', 150.0, 140.0, '2023-09-15 12:00:00'),
(7, 1, 1.5, '2023-03-15', 1, 'Good', 60, '2023-07-15', 1500.0, 1400.0, '2023-07-15 12:00:00'),
(7, 2, 0.5, '2023-03-20', 1, 'Fair', 25, '2023-07-20', 250.0, 240.0, '2023-07-20 12:00:00'),
(8, 3, 0.3, '2023-04-01', 1, 'Good', 10, '2023-09-01', 250.0, 240.0, '2023-09-01 12:00:00'),
(8, 4, 0.6, '2023-04-05', 1, 'Good', 20, '2023-09-05', 600.0, 590.0, '2023-09-05 12:00:00'),
(9, 5, 0.5, '2023-04-10', 1, 'Fair', 25, '2023-09-10', 500.0, 490.0, '2023-09-10 12:00:00'),
(9, 6, 0.2, '2023-04-15', 1, 'Excellent', 10, '2023-09-15', 100.0, 90.0, '2023-09-15 12:00:00'),
(10, 1, 1.0, '2023-03-15', 1, 'Good', 40, '2023-07-15', 1000.0, 950.0, '2023-07-15 12:00:00'),
(10, 2, 0.4, '2023-03-20', 1, 'Fair', 20, '2023-07-20', 200.0, 190.0, '2023-07-20 12:00:00'),
(11, 3, 0.2, '2023-04-01', 1, 'Good', 5, '2023-09-01', 125.0, 120.0, '2023-09-01 12:00:00'),
(11, 4, 0.4, '2023-04-05', 1, 'Good', 10, '2023-09-05', 300.0, 290.0, '2023-09-05 12:00:00'),
(12, 5, 0.3, '2023-04-10', 1, 'Fair', 15, '2023-09-10', 300.0, 290.0, '2023-09-10 12:00:00'),
(12, 6, 0.1, '2023-04-15', 1, 'Excellent', 5, '2023-09-15', 50.0, 40.0, '2023-09-15 12:00:00'),
(13, 1, 0.5, '2023-03-15', 1, 'Good', 20, '2023-07-15', 500.0, 480.0, '2023-07-15 12:00:00'),
(13, 2, 0.2, '2023-03-20', 1, 'Fair', 10, '2023-07-20', 100.0, 90.0, '2023-07-20 12:00:00'),
(14, 3, 0.1, '2023-04-01', 1, 'Good', 5, '2023-09-01', 125.0, 120.0, '2023-09-01 12:00:00'),
(14, 4, 0.2, '2023-04-05', 1, 'Good', 5, '2023-09-05', 150.0, 140.0, '2023-09-05 12:00:00'),
(15, 5, 0.2, '2023-04-10', 1, 'Fair', 10, '2023-09-10', 100.0, 90.0, '2023-09-10 12:00:00'),
(15, 6, 0.1, '2023-04-15', 1, 'Excellent', 5, '2023-09-15', 50.0, 40.0, '2023-09-15 12:00:00'),
(16, 1, 0.3, '2023-03-15', 1, 'Good', 12, '2023-07-15', 300.0, 290.0, '2023-07-15 12:00:00'),
(16, 2, 0.1, '2023-03-20', 1, 'Fair', 6, '2023-07-20', 60.0, 50.0, '2023-07-20 12:00:00'),
(17, 3, 0.05, '2023-04-01', 1, 'Good', 2, '2023-09-01', 50.0, 40.0, '2023-09-01 12:00:00'),
(17, 4, 0.1, '2023-04-05', 1, 'Good', 3, '2023-09-05', 30.0, 25.0, '2023-09-05 12:00:00'),
(18, 5, 0.1, '2023-04-10', 1, 'Fair', 5, '2023-09-10', 50.0, 40.0, '2023-09-10 12:00:00'),
(18, 6, 0.05, '2023-04-15', 1, 'Excellent', 2, '2023-09-15', 20.0, 15.0, '2023-09-15 12:00:00'),
(19, 1, 0.2, '2023-03-15', 1, 'Good', 8, '2023-07-15', 200.0, 190.0, '2023-07-15 12:00:00'),
(19, 2, 0.1, '2023-03-20', 1, 'Fair', 4, '2023-07-20', 40.0, 30.0, '2023-07-20 12:00:00'),
(20, 3, 0.05, '2023-04-01', 1, 'Good', 2, '2023-09-01', 50.0, 40.0, '2023-09-01 12:00:00'),
(20, 4, 0.1, '2023-04-05', 1, 'Good', 3, '2023-09-05', 30.0, 25.0, '2023-09-05 12:00:00');

INSERT INTO farmData (farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp) VALUES
(1, 1, 2.5, '2023-03-15', 1, 'Good', 100, '2023-07-15', 2500.0, 2300.0, '2023-07-15 12:00:00'),
(1, 2, 1.0, '2023-03-20', 1, 'Fair', 50, '2023-07-20', 500.0, 480.0, '2023-07-20 12:00:00'),
(2, 3, 0.5, '2023-04-01', 1, 'Good', 20, '2023-09-01', 500.0, 480.0, '2023-09-01 12:00:00'),
(2, 4, 1.0, '2023-04-05', 1, 'Good', 30, '2023-09-05', 900.0, 880.0, '2023-09-05 12:00:00'),
(3, 5, 0.8, '2023-04-10', 1, 'Fair', 40, '2023-09-10', 800.0, 780.0, '2023-09-10 12:00:00'),
(3, 6, 0.3, '2023-04-15', 1, 'Excellent', 15, '2023-09-15', 225.0, 220.0, '2023-09-15 12:00:00'),
(4, 1, 2.0, '2023-03-15', 1, 'Good', 80, '2023-07-15', 2000.0, 1900.0, '2023-07-15 12:00:00'),
(4, 2, 0.8, '2023-03-20', 1, 'Fair', 40, '2023-07-20', 400.0, 380.0, '2023-07-20 12:00:00'),
(5, 3, 0.4, '2023-04-01', 1, 'Good', 15, '2023-09-01', 375.0, 370.0, '2023-09-01 12:00:00'),
(5, 4, 0.7, '2023-04-05', 1, 'Good', 25, '2023-09-05', 750.0, 740.0, '2023-09-05 12:00:00'),
(6, 5, 0.6, '2023-04-10', 1, 'Fair', 30, '2023-09-10', 600.0, 580.0, '2023-09-10 12:00:00'),
(6, 6, 0.2, '2023-04-15', 1, 'Excellent', 10, '2023-09-15', 150.0, 140.0, '2023-09-15 12:00:00'),
(7, 1, 1.5, '2023-03-15', 1, 'Good', 60, '2023-07-15', 1500.0, 1400.0, '2023-07-15 12:00:00'),
(7, 2, 0.5, '2023-03-20', 1, 'Fair', 25, '2023-07-20', 250.0, 240.0, '2023-07-20 12:00:00'),
(8, 3, 0.3, '2023-04-01', 1, 'Good', 10, '2023-09-01', 250.0, 240.0, '2023-09-01 12:00:00'),
(8, 4, 0.6, '2023-04-05', 1, 'Good', 20, '2023-09-05', 600.0, 590.0, '2023-09-05 12:00:00'),
(9, 5, 0.5, '2023-04-10', 1, 'Fair', 25, '2023-09-10', 500.0, 490.0, '2023-09-10 12:00:00'),
(9, 6, 0.2, '2023-04-15', 1, 'Excellent', 10, '2023-09-15', 100.0, 90.0, '2023-09-15 12:00:00'),
(10, 1, 1.0, '2023-03-15', 1, 'Good', 40, '2023-07-15', 1000.0, 950.0, '2023-07-15 12:00:00'),
(10, 2, 0.4, '2023-03-20', 1, 'Fair', 20, '2023-07-20', 200.0, 190.0, '2023-07-20 12:00:00'),
(11, 3, 0.2, '2023-04-01', 1, 'Good', 5, '2023-09-01', 125.0, 120.0, '2023-09-01 12:00:00'),
(11, 4, 0.4, '2023-04-05', 1, 'Good', 10, '2023-09-05', 300.0, 290.0, '2023-09-05 12:00:00'),
(12, 5, 0.3, '2023-04-10', 1, 'Fair', 15, '2023-09-10', 300.0, 290.0, '2023-09-10 12:00:00'),
(12, 6, 0.1, '2023-04-15', 1, 'Excellent', 5, '2023-09-15', 50.0, 40.0, '2023-09-15 12:00:00'),
(13, 1, 0.5, '2023-03-15', 1, 'Good', 20, '2023-07-15', 500.0, 480.0, '2023-07-15 12:00:00'),
(13, 2, 0.2, '2023-03-20', 1, 'Fair', 10, '2023-07-20', 100.0, 90.0, '2023-07-20 12:00:00'),
(14, 3, 0.1, '2023-04-01', 1, 'Good', 5, '2023-09-01', 125.0, 120.0, '2023-09-01 12:00:00'),
(14, 4, 0.2, '2023-04-05', 1, 'Good', 5, '2023-09-05', 150.0, 140.0, '2023-09-05 12:00:00'),
(15, 5, 0.2, '2023-04-10', 1, 'Fair', 10, '2023-09-10', 100.0, 90.0, '2023-09-10 12:00:00'),
(15, 6, 0.1, '2023-04-15', 1, 'Excellent', 5, '2023-09-15', 50.0, 40.0, '2023-09-15 12:00:00'),
(16, 1, 0.3, '2023-03-15', 1, 'Good', 12, '2023-07-15', 300.0, 290.0, '2023-07-15 12:00:00'),
(16, 2, 0.1, '2023-03-20', 1, 'Fair', 6, '2023-07-20', 60.0, 50.0, '2023-07-20 12:00:00'),
(17, 3, 0.05, '2023-04-01', 1, 'Good', 2, '2023-09-01', 50.0, 40.0, '2023-09-01 12:00:00'),
(17, 4, 0.1, '2023-04-05', 1, 'Good', 3, '2023-09-05', 30.0, 25.0, '2023-09-05 12:00:00'),
(18, 5, 0.1, '2023-04-10', 1, 'Fair', 5, '2023-09-10', 50.0, 40.0, '2023-09-10 12:00:00'),
(18, 6, 0.05, '2023-04-15', 1, 'Excellent', 2, '2023-09-15', 20.0, 15.0, '2023-09-15 12:00:00'),
(19, 1, 0.2, '2023-03-15', 1, 'Good', 8, '2023-07-15', 200.0, 190.0, '2023-07-15 12:00:00'),
(19, 2, 0.1, '2023-03-20', 1, 'Fair', 4, '2023-07-20', 40.0, 30.0, '2023-07-20 12:00:00'),
(20, 3, 0.05, '2023-04-01', 1, 'Good', 2, '2023-09-01', 50.0, 40.0, '2023-09-01 12:00:00'),
(20, 4, 0.1, '2023-04-05', 1, 'Good', 3, '2023-09-05', 30.0, 25.0, '2023-09-05 12:00:00');
INSERT INTO farmData (farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name)
VALUES
(11,1,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500.0,2300.0,'2023-07-15 12:00:00', 'Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(21,2,1.0,'2023-03-20',1,'Fair',50,'2023-07-20',500.0,480.0,'2023-07-20 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(32,3,0.5,'2023-04-01',1,'Good',20,'2023-09-01',500.0,480.0,'2023-09-01 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(42,4,1.0,'2023-04-05',1,'Good',30,'2023-09-05',900.0,880.0,'2023-09-05 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(53,5,0.84,'2023-04-10',1,'Fair',40,'2023-09-10',800.0,780.0,'2023-09-10 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(13,6,0.289,'2023-04-15',1,'Excellent',15,'2023-09-15',225.0,220.0,'2023-09-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(24,1,2.0,'2023-03-15',1,'Good',80,'2023-07-15',2000.0,1900.0,'2023-07-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(34,2,0.84,'2023-03-20',1,'Fair',40,'2023-07-20',400.0,380.0,'2023-07-20 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(43,3,0.42,'2023-04-01',1,'Good',15,'2023-09-01',375.0,370.0,'2023-09-01 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(52,4,0.659,'2023-04-05',1,'Good',25,'2023-09-05',750.0,740.0,'2023-09-05 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(11,5,0.579,'2023-04-10',1,'Fair',30,'2023-09-10',600.0,580.0,'2023-09-10 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(12,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',150.0,140.0,'2023-09-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(22,1,1.5,'2023-03-15',1,'Good',60,'2023-07-15',1500.0,1400.0,'2023-07-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(33,2,0.5,'2023-03-20',1,'Fair',25,'2023-07-20',250.0,240.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(43,3,0.289,'2023-04-01',1,'Good',10,'2023-09-01',250.0,240.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(53,4,0.579,'2023-04-05',1,'Good',20,'2023-09-05',600.0,590.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(14,5,0.5,'2023-04-10',1,'Fair',25,'2023-09-10',500.0,490.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(25,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',100.0,90.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(16,1,1.0,'2023-03-15',1,'Good',40,'2023-07-15',1000.0,950.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(17,2,0.4222,'2023-03-20',1,'Fair',20,'2023-07-20',200.0,190.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(38,3,0.200111,'2023-04-01',1,'Good',5,'2023-09-01',125.0,120.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(19,4,0.4000222,'2023-04-05',1,'Good',10,'2023-09-05',300.0,290.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(10,5,0.29,'2023-04-10',1,'Fair',15,'2023-09-10',300.0,290.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(15,6,0.100555,'2023-04-15',1,'Excellent',5,'2023-09-15',50.0,40.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(41,1,0.5,'2023-03-15',1,'Good',20,'2023-07-15',500.0,480.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(72,2,0.200111,'2023-03-20',1,'Fair',10,'2023-07-20',100.0,90.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(52,3,0.155,'2023-04-01',1,'Good',5,'2023-09-01',125.0,120.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(13,4,0.21,'2023-04-05',1,'Good',5,'2023-09-05',150.0,140.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(14,5,0.21,'2023-04-10',1,'Fair',10,'2023-09-10',100.0,90.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(15,6,0.155,'2023-04-15',1,'Excellent',5,'2023-09-15',50.0,40.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(16,1,0.289,'2023-03-15',1,'Good',12,'2023-07-15',300.0,290.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(17,2,0.155,'2023-03-20',1,'Fair',6,'2023-07-20',60.0,50.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(18,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50.0,40.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(19,4,0.155,'2023-04-05',1,'Good',3,'2023-09-05',30.0,25.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(20,5,0.155,'2023-04-10',1,'Fair',5,'2023-09-10',50.0,40.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(21,6,0.0775,'2023-04-15',1,'Excellent',2,'2023-09-15',20.0,15.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(22,1,0.21,'2023-03-15',1,'Good',8,'2023-07-15',200.0,190.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(38,2,0.155,'2023-03-20',1,'Fair',4,'2023-07-20',40.0,30.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(39,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50.0,40.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmData (farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name)
VALUES
(40,1,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500.0,2300.0,'2023-07-15 12:00:00', 'Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(41,2,1.0,'2023-03-20',1,'Fair',50,'2023-07-20',500.0,480.0,'2023-07-20 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(42,3,0.5,'2023-04-01',1,'Good',20,'2023-09-01',500.0,480.0,'2023-09-01 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(43,4,1.0,'2023-04-05',1,'Good',30,'2023-09-05',900.0,880.0,'2023-09-05 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(44,5,0.84,'2023-04-10',1,'Fair',40,'2023-09-10',800.0,780.0,'2023-09-10 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(45,6,0.289,'2023-04-15',1,'Excellent',15,'2023-09-15',225.0,220.0,'2023-09-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(46,1,2.0,'2023-03-15',1,'Good',80,'2023-07-15',2000.0,1900.0,'2023-07-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(47,2,0.84,'2023-03-20',1,'Fair',40,'2023-07-20',400.0,380.0,'2023-07-20 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(48,3,0.42,'2023-04-01',1,'Good',15,'2023-09-01',375.0,370.0,'2023-09-01 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(49,4,0.659,'2023-04-05',1,'Good',25,'2023-09-05',750.0,740.0,'2023-09-05 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(50,5,0.579,'2023-04-10',1,'Fair',30,'2023-09-10',600.0,580.0,'2023-09-10 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(51,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',150.0,140.0,'2023-09-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(52,1,1.5,'2023-03-15',1,'Good',60,'2023-07-15',1500.0,1400.0,'2023-07-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(53,2,0.5,'2023-03-20',1,'Fair',25,'2023-07-20',250.0,240.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(54,3,0.289,'2023-04-01',1,'Good',10,'2023-09-01',250.0,240.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(55,4,0.579,'2023-04-05',1,'Good',20,'2023-09-05',600.0,590.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(56,5,0.5,'2023-04-10',1,'Fair',25,'2023-09-10',500.0,490.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(57,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',100.0,90.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(58,1,1.0,'2023-03-15',1,'Good',40,'2023-07-15',1000.0,950.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(59,2,0.4222,'2023-03-20',1,'Fair',20,'2023-07-20',200.0,190.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(60,3,0.200111,'2023-04-01',1,'Good',5,'2023-09-01',125.0,120.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(61,4,0.4000222,'2023-04-05',1,'Good',10,'2023-09-05',300.0,290.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(62,5,0.29,'2023-04-10',1,'Fair',15,'2023-09-10',300.0,290.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(63,6,0.100555,'2023-04-15',1,'Excellent',5,'2023-09-15',50.0,40.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(64,1,0.5,'2023-03-15',1,'Good',20,'2023-07-15',500.0,480.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(65,2,0.200111,'2023-03-20',1,'Fair',10,'2023-07-20',100.0,90.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(66,3,0.155,'2023-04-01',1,'Good',5,'2023-09-01',125.0,120.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(67,4,0.21,'2023-04-05',1,'Good',5,'2023-09-05',150.0,140.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(68,5,0.21,'2023-04-10',1,'Fair',10,'2023-09-10',100.0,90.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(69,6,0.155,'2023-04-15',1,'Excellent',5,'2023-09-15',50.0,40.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(70,1,0.289,'2023-03-15',1,'Good',12,'2023-07-15',300.0,290.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(72,2,0.155,'2023-03-20',1,'Fair',6,'2023-07-20',60.0,50.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(73,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50.0,40.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(74,4,0.155,'2023-04-05',1,'Good',3,'2023-09-05',30.0,25.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(30,5,0.155,'2023-04-10',1,'Fair',5,'2023-09-10',50.0,40.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(31,6,0.0775,'2023-04-15',1,'Excellent',2,'2023-09-15',20.0,15.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(32,1,0.21,'2023-03-15',1,'Good',8,'2023-07-15',200.0,190.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(33,2,0.155,'2023-03-20',1,'Fair',4,'2023-07-20',40.0,30.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(34,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50.0,40.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');




INSERT INTO farmdata (farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name)
VALUES
(75,1,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500.0,2300.0,'2023-07-15 12:00:00', 'Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(76,2,1.0,'2023-03-20',1,'Fair',50,'2023-07-20',500.0,480.0,'2023-07-20 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(77,3,0.5,'2023-04-01',1,'Good',20,'2023-09-01',500.0,480.0,'2023-09-01 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(78,4,1.0,'2023-04-05',1,'Good',30,'2023-09-05',900.0,880.0,'2023-09-05 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(79,5,0.84,'2023-04-10',1,'Fair',40,'2023-09-10',800.0,780.0,'2023-09-10 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(80,6,0.289,'2023-04-15',1,'Excellent',15,'2023-09-15',225.0,220.0,'2023-09-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(81,1,2.0,'2023-03-15',1,'Good',80,'2023-07-15',2000.0,1900.0,'2023-07-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(82,2,0.84,'2023-03-20',1,'Fair',40,'2023-07-20',400.0,380.0,'2023-07-20 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(83,3,0.42,'2023-04-01',1,'Good',15,'2023-09-01',375.0,370.0,'2023-09-01 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(84,4,0.659,'2023-04-05',1,'Good',25,'2023-09-05',750.0,740.0,'2023-09-05 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(85,5,0.579,'2023-04-10',1,'Fair',30,'2023-09-10',600.0,580.0,'2023-09-10 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(86,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',150.0,140.0,'2023-09-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(87,1,1.5,'2023-03-15',1,'Good',60,'2023-07-15',1500.0,1400.0,'2023-07-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(88,2,0.5,'2023-03-20',1,'Fair',25,'2023-07-20',250.0,240.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(89,3,0.289,'2023-04-01',1,'Good',10,'2023-09-01',250.0,240.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(90,4,0.579,'2023-04-05',1,'Good',20,'2023-09-05',600.0,590.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(91,5,0.5,'2023-04-10',1,'Fair',25,'2023-09-10',500.0,490.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(92,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',100.0,90.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(93,1,1.0,'2023-03-15',1,'Good',40,'2023-07-15',1000.0,950.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(94,2,0.4222,'2023-03-20',1,'Fair',20,'2023-07-20',200.0,190.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(95,3,0.200111,'2023-04-01',1,'Good',5,'2023-09-01',125.0,120.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(96,4,0.4000222,'2023-04-05',1,'Good',10,'2023-09-05',300.0,290.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(97,5,0.29,'2023-04-10',1,'Fair',15,'2023-09-10',300.0,290.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(98,6,0.100555,'2023-04-15',1,'Excellent',5,'2023-09-15',50.0,40.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(99,1,0.5,'2023-03-15',1,'Good',20,'2023-07-15',500.0,480.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(100,2,0.200111,'2023-03-20',1,'Fair',10,'2023-07-20',100.0,90.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(101,3,0.155,'2023-04-01',1,'Good',5,'2023-09-01',125.0,120.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(102,4,0.21,'2023-04-05',1,'Good',5,'2023-09-05',150.0,140.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(103,5,0.21,'2023-04-10',1,'Fair',10,'2023-09-10',100.0,90.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(104,6,0.155,'2023-04-15',1,'Excellent',5,'2023-09-15',50.0,40.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(105,1,0.289,'2023-03-15',1,'Good',12,'2023-07-15',300.0,290.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(106,2,0.155,'2023-03-20',1,'Fair',6,'2023-07-20',60.0,50.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(107,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50.0,40.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(108,4,0.155,'2023-04-05',1,'Good',3,'2023-09-05',30.0,25.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(109,5,0.155,'2023-04-10',1,'Fair',5,'2023-09-10',50.0,40.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(110,6,0.0775,'2023-04-15',1,'Excellent',2,'2023-09-15',20.0,15.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(111,1,0.21,'2023-03-15',1,'Good',8,'2023-07-15',200.0,190.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(112,2,0.155,'2023-03-20',1,'Fair',4,'2023-07-20',40.0,30.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(113,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50.0,40.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');


INSERT INTO farmdata (farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name)
VALUES
(114,1,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500.0,2300.0,'2023-07-15 12:00:00', 'Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(115,2,1.0,'2023-03-20',1,'Fair',50,'2023-07-20',500.0,480.0,'2023-07-20 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(116,3,0.5,'2023-04-01',1,'Good',20,'2023-09-01',500.0,480.0,'2023-09-01 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(117,4,1.0,'2023-04-05',1,'Good',30,'2023-09-05',900.0,880.0,'2023-09-05 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(118,5,0.84,'2023-04-10',1,'Fair',40,'2023-09-10',800.0,780.0,'2023-09-10 12:00:00','Agro Supplies Ltd', 'Uganda', 'Jinja Farms Ltd'),
(119,6,0.289,'2023-04-15',1,'Excellent',15,'2023-09-15',225.0,220.0,'2023-09-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(120,1,2.0,'2023-03-15',1,'Good',80,'2023-07-15',2000.0,1900.0,'2023-07-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(121,2,0.84,'2023-03-20',1,'Fair',40,'2023-07-20',400.0,380.0,'2023-07-20 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(122,3,0.42,'2023-04-01',1,'Good',15,'2023-09-01',375.0,370.0,'2023-09-01 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(123,4,0.659,'2023-04-05',1,'Good',25,'2023-09-05',750.0,740.0,'2023-09-05 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(124,5,0.579,'2023-04-10',1,'Fair',30,'2023-09-10',600.0,580.0,'2023-09-10 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(125,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',150.0,140.0,'2023-09-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(126,1,1.5,'2023-03-15',1,'Good',60,'2023-07-15',1500.0,1400.0,'2023-07-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(80,2,0.5,'2023-03-20',1,'Fair',25,'2023-07-20',250.0,240.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(82,3,0.289,'2023-04-01',1,'Good',10,'2023-09-01',250.0,240.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(83,4,0.579,'2023-04-05',1,'Good',20,'2023-09-05',600.0,590.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(84,5,0.5,'2023-04-10',1,'Fair',25,'2023-09-10',500.0,490.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(85,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',100.0,90.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(86,1,1.0,'2023-03-15',1,'Good',40,'2023-07-15',1000.0,950.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(87,2,0.4222,'2023-03-20',1,'Fair',20,'2023-07-20',200.0,190.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(88,3,0.200111,'2023-04-01',1,'Good',5,'2023-09-01',125.0,120.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(89,4,0.4000222,'2023-04-05',1,'Good',10,'2023-09-05',300.0,290.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(90,5,0.29,'2023-04-10',1,'Fair',15,'2023-09-10',300.0,290.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(92,6,0.100555,'2023-04-15',1,'Excellent',5,'2023-09-15',50.0,40.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(83,1,0.5,'2023-03-15',1,'Good',20,'2023-07-15',500.0,480.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(94,2,0.200111,'2023-03-20',1,'Fair',10,'2023-07-20',100.0,90.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(95,3,0.155,'2023-04-01',1,'Good',5,'2023-09-01',125.0,120.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(96,4,0.21,'2023-04-05',1,'Good',5,'2023-09-05',150.0,140.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(97,5,0.21,'2023-04-10',1,'Fair',10,'2023-09-10',100.0,90.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(98,6,0.155,'2023-04-15',1,'Excellent',5,'2023-09-15',50.0,40.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(99,1,0.289,'2023-03-15',1,'Good',12,'2023-07-15',300.0,290.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(100,2,0.155,'2023-03-20',1,'Fair',6,'2023-07-20',60.0,50.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(101,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50.0,40.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(102,4,0.155,'2023-04-05',1,'Good',3,'2023-09-05',30.0,25.0,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(103,5,0.155,'2023-04-10',1,'Fair',5,'2023-09-10',50.0,40.0,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(104,6,0.0775,'2023-04-15',1,'Excellent',2,'2023-09-15',20.0,15.0,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(105,1,0.21,'2023-03-15',1,'Good',8,'2023-07-15',200.0,190.0,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(106,2,0.155,'2023-03-20',1,'Fair',4,'2023-07-20',40.0,30.0,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(107,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50.0,40.0,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');


UPDATE farmData
SET 
    channel_partner = 'Agro Supplies Ltd',
    destination_country = 'Uganda',
    customer_name = 'Jinja Farms Ltd'
WHERE id = 1;

-- Mettre à jour l'enregistrement 2
UPDATE farmData
SET 
    channel_partner = 'Uganda AgriTech Solutions',
    destination_country = 'Uganda',
    customer_name = 'Kampala Agro Farms'
WHERE id = 2;

-- Mettre à jour l'enregistrement 3
UPDATE farmData
SET 
    channel_partner = 'Kampala Agri Solutions',
    destination_country = 'Uganda',
    customer_name = 'Mbale Farms Co.'
WHERE id = 3;

-- Mettre à jour l'enregistrement 4
UPDATE farmData
SET 
    channel_partner = 'Uganda Organic Harvest',
    destination_country = 'Uganda',
    customer_name = 'Masaka Agro Enterprises'
WHERE id = 4;

-- Mettre à jour l'enregistrement 5
UPDATE farmData
SET 
    channel_partner = 'Jinja Farms Ltd',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Agro Coop'
WHERE id = 5;

-- Mettre à jour l'enregistrement 6
UPDATE farmData
SET 
    channel_partner = 'Uganda Green Fields',
    destination_country = 'Uganda',
    customer_name = 'Lira Organic Farmers'
WHERE id = 6;

-- Mettre à jour l'enregistrement 7
UPDATE farmData
SET 
    channel_partner = 'Kasese AgriPro',
    destination_country = 'Uganda',
    customer_name = 'Entebbe Produce Group'
WHERE id = 7;

-- Mettre à jour l'enregistrement 8
UPDATE farmData
SET 
    channel_partner = 'Uganda Harvesters',
    destination_country = 'Uganda',
    customer_name = 'Soroti Agri Enterprise'
WHERE id = 8;

-- Mettre à jour l'enregistrement 9
UPDATE farmData
SET 
    channel_partner = 'Kabale Farm Solutions',
    destination_country = 'Uganda',
    customer_name = 'Gulu Farmers Coop'
WHERE id = 9;

-- Mettre à jour l'enregistrement 10
UPDATE farmData
SET 
    channel_partner = 'Mbale Agri Ltd',
    destination_country = 'Uganda',
    customer_name = 'Hoima Organic'
WHERE id = 10;

-- Mettre à jour l'enregistrement 11
UPDATE farmData
SET 
    channel_partner = 'Uganda Agro Services',
    destination_country = 'Uganda',
    customer_name = 'Mityana Produce Group'
WHERE id = 11;

-- Mettre à jour l'enregistrement 12
UPDATE farmData
SET 
    channel_partner = 'Jinja Fields',
    destination_country = 'Uganda',
    customer_name = 'Kasese Agri Coop'
WHERE id = 12;

-- Mettre à jour l'enregistrement 13
UPDATE farmData
SET 
    channel_partner = 'Uganda Harvest Group',
    destination_country = 'Uganda',
    customer_name = 'Kabale Farms'
WHERE id = 13;

-- Mettre à jour l'enregistrement 14
UPDATE farmData
SET 
    channel_partner = 'Gulu Agri Solutions',
    destination_country = 'Uganda',
    customer_name = 'Mbale Organic'
WHERE id = 14;

-- Mettre à jour l'enregistrement 15
UPDATE farmData
SET 
    channel_partner = 'Lira Farms',
    destination_country = 'Uganda',
    customer_name = 'Masaka Agri Coop'
WHERE id = 15;

-- Mettre à jour l'enregistrement 16
UPDATE farmData
SET 
    channel_partner = 'Kabale AgriPro',
    destination_country = 'Uganda',
    customer_name = 'Jinja Organic'
WHERE id = 16;

-- Mettre à jour l'enregistrement 17
UPDATE farmData
SET 
    channel_partner = 'Uganda Green Harvest',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Agri Enterprise'
WHERE id = 17;

-- Mettre à jour l'enregistrement 18
UPDATE farmData
SET 
    channel_partner = 'Hoima Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Kasese Farmers Coop'
WHERE id = 18;

-- Mettre à jour l'enregistrement 19
UPDATE farmData
SET 
    channel_partner = 'Entebbe Agri Ltd',
    destination_country = 'Uganda',
    customer_name = 'Masindi Harvesters'
WHERE id = 19;

-- Mettre à jour l'enregistrement 20
UPDATE farmData
SET 
    channel_partner = 'Gulu Fields',
    destination_country = 'Uganda',
    customer_name = 'Mbale Agro Coop'
WHERE id = 20;

-- Mettre à jour l'enregistrement 21
UPDATE farmData
SET 
    channel_partner = 'Mityana Farms',
    destination_country = 'Uganda',
    customer_name = 'Kabale Agri Group'
WHERE id = 21;

-- Mettre à jour l'enregistrement 22
UPDATE farmData
SET 
    channel_partner = 'Kasese AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Gulu Organic Farmers'
WHERE id = 22;

-- Mettre à jour l'enregistrement 23
UPDATE farmData
SET 
    channel_partner = 'Mbale Harvest Group',
    destination_country = 'Uganda',
    customer_name = 'Mityana Agri Enterprise'
WHERE id = 23;

-- Mettre à jour l'enregistrement 24
UPDATE farmData
SET 
    channel_partner = 'Masaka Agri Solutions',
    destination_country = 'Uganda',
    customer_name = 'Masindi Agri Coop'
WHERE id = 24;

-- Mettre à jour l'enregistrement 25
UPDATE farmData
SET 
    channel_partner = 'Kabale Green Fields',
    destination_country = 'Uganda',
    customer_name = 'Lira Harvest Group'
WHERE id = 25;

-- Mettre à jour l'enregistrement 26
UPDATE farmData
SET 
    channel_partner = 'Mbarara AgriPro',
    destination_country = 'Uganda',
    customer_name = 'Entebbe Agri Coop'
WHERE id = 26;

-- Mettre à jour l'enregistrement 27
UPDATE farmData
SET 
    channel_partner = 'Gulu Harvesters',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Harvesters'
WHERE id = 27;

-- Mettre à jour l'enregistrement 28
UPDATE farmData
SET 
    channel_partner = 'Masaka Fields',
    destination_country = 'Uganda',
    customer_name = 'Hoima Agri Enterprise'
WHERE id = 28;

-- Mettre à jour l'enregistrement 29
UPDATE farmData
SET 
    channel_partner = 'Mbale AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Masindi Agri Solutions'
WHERE id = 29;

-- Mettre à jour l'enregistrement 30
UPDATE farmData
SET 
    channel_partner = 'Mityana Harvesters',
    destination_country = 'Uganda',
    customer_name = 'Entebbe Harvest Group'
WHERE id = 30;

-- Mettre à jour l'enregistrement 31
UPDATE farmData
SET 
    channel_partner = 'Masindi AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Mityana Agri Coop'
WHERE id = 31;

-- Mettre à jour l'enregistrement 32
UPDATE farmData
SET 
    channel_partner = 'Kabale Fields',
    destination_country = 'Uganda',
    customer_name = 'Jinja Agri Solutions'
WHERE id = 32;

-- Mettre à jour l'enregistrement 33
UPDATE farmData
SET 
    channel_partner = 'Mbarara Agri Group',
    destination_country = 'Uganda',
    customer_name = 'Masaka Harvesters'
WHERE id = 33;

-- Mettre à jour l'enregistrement 34
UPDATE farmData
SET 
    channel_partner = 'Mbale Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Kabale Agri Solutions'
WHERE id = 34;

-- Mettre à jour l'enregistrement 35
UPDATE farmData
SET 
    channel_partner = 'Masindi Harvest Group',
    destination_country = 'Uganda',
    customer_name = 'Kasese Agri Coop'
WHERE id = 35;

-- Mettre à jour l'enregistrement 36
UPDATE farmData
SET 
    channel_partner = 'Mityana AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Lira Harvesters'
WHERE id = 36;

-- Mettre à jour l'enregistrement 37
UPDATE farmData
SET 
    channel_partner = 'Mbarara Agro Group',
    destination_country = 'Uganda',
    customer_name = 'Mbale Agri Coop'
WHERE id = 37;

-- Mettre à jour l'enregistrement 38
UPDATE farmData
SET 
    channel_partner = 'Jinja Agri Solutions',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Agri Coop'
WHERE id = 38;

-- Mettre à jour l'enregistrement 39
UPDATE farmData
SET 
    channel_partner = 'Masaka AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Masindi Harvesters'
WHERE id = 39;

-- Mettre à jour l'enregistrement 40
UPDATE farmData
SET 
    channel_partner = 'Kabale Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Kasese Agri Group'
WHERE id = 40;

-- Mettre à jour l'enregistrement 41
UPDATE farmData
SET 
    channel_partner = 'Mityana Agri Group',
    destination_country = 'Uganda',
    customer_name = 'Gulu Agri Solutions'
WHERE id = 41;

-- Mettre à jour l'enregistrement 42
UPDATE farmData
SET 
    channel_partner = 'Masindi Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Mbale Harvesters'
WHERE id = 42;

-- Mettre à jour l'enregistrement 43
UPDATE farmData
SET 
    channel_partner = 'Kasese Agro Group',
    destination_country = 'Uganda',
    customer_name = 'Entebbe Harvest Group'
WHERE id = 43;

-- Mettre à jour l'enregistrement 44
UPDATE farmData
SET 
    channel_partner = 'Mbarara Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Jinja Agri Coop'
WHERE id = 44;

-- Mettre à jour l'enregistrement 45
UPDATE farmData
SET 
    channel_partner = 'Mbale Agro Group',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Harvesters'
WHERE id = 45;

-- Mettre à jour l'enregistrement 46
UPDATE farmData
SET 
    channel_partner = 'Mityana Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Masaka Harvesters'
WHERE id = 46;

-- Mettre à jour l'enregistrement 47
UPDATE farmData
SET 
    channel_partner = 'Masaka Agro Group',
    destination_country = 'Uganda',
    customer_name = 'Kabale Agri Coop'
WHERE id = 47;

-- Mettre à jour l'enregistrement 48
UPDATE farmData
SET 
    channel_partner = 'Kabale Agro Group',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Harvesters'
WHERE id = 48;

-- Mettre à jour l'enregistrement 49
UPDATE farmData
SET 
    channel_partner = 'Mbarara AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Masaka Agri Solutions'
WHERE id = 49;

-- Mettre à jour l'enregistrement 50
UPDATE farmData
SET 
    channel_partner = 'Mbale Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Masindi Agri Coop'
WHERE id = 50;

-- Mettre à jour l'enregistrement 51
UPDATE farmData
SET 
    channel_partner = 'Masaka Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Harvesters'
WHERE id = 51;

-- Mettre à jour l'enregistrement 52
UPDATE farmData
SET 
    channel_partner = 'Mityana AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Kasese Agri Solutions'
WHERE id = 52;

-- Mettre à jour l'enregistrement 53
UPDATE farmData
SET 
    channel_partner = 'Masindi Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Entebbe Agri Coop'
WHERE id = 53;

-- Mettre à jour l'enregistrement 54
UPDATE farmData
SET 
    channel_partner = 'Kasese Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Mityana Agri Coop'
WHERE id = 54;

-- Mettre à jour l'enregistrement 55
UPDATE farmData
SET 
    channel_partner = 'Mbarara Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Masaka Agri Group'
WHERE id = 55;

-- Mettre à jour l'enregistrement 56
UPDATE farmData
SET 
    channel_partner = 'Mbale AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Jinja Agri Coop'
WHERE id = 56;

-- Mettre à jour l'enregistrement 57
UPDATE farmData
SET 
    channel_partner = 'Masindi AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Agri Solutions'
WHERE id = 57;

-- Mettre à jour l'enregistrement 58
UPDATE farmData
SET 
    channel_partner = 'Kasese Agro Group',
    destination_country = 'Uganda',
    customer_name = 'Masaka Agri Solutions'
WHERE id = 58;

-- Mettre à jour l'enregistrement 59
UPDATE farmData
SET 
    channel_partner = 'Mityana AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Kabale Agri Coop'
WHERE id = 59;

-- Mettre à jour l'enregistrement 60
UPDATE farmData
SET 
    channel_partner = 'Masaka AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Agri Solutions'
WHERE id = 60;

-- Mettre à jour l'enregistrement 61
UPDATE farmData
SET 
    channel_partner = 'Mbarara Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Kasese Agri Group'
WHERE id = 61;

-- Mettre à jour l'enregistrement 62
UPDATE farmData
SET 
    channel_partner = 'Mbale Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Masindi Agri Coop'
WHERE id = 62;

-- Mettre à jour l'enregistrement 63
UPDATE farmData
SET 
    channel_partner = 'Masaka Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Agri Group'
WHERE id = 63;

-- Mettre à jour l'enregistrement 64
UPDATE farmData
SET 
    channel_partner = 'Mityana AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Masaka Agri Coop'
WHERE id = 64;

-- Mettre à jour l'enregistrement 65
UPDATE farmData
SET 
    channel_partner = 'Masindi AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Jinja Agri Coop'
WHERE id = 65;

-- Mettre à jour l'enregistrement 66
UPDATE farmData
SET 
    channel_partner = 'Kasese Agro Group',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Agri Solutions'
WHERE id = 66;

-- Mettre à jour l'enregistrement 67
UPDATE farmData
SET 
    channel_partner = 'Mbarara Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Kasese Agri Coop'
WHERE id = 67;

-- Mettre à jour l'enregistrement 68
UPDATE farmData
SET 
    channel_partner = 'Mbale Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Masaka Agri Solutions'
WHERE id = 68;

-- Mettre à jour l'enregistrement 69
UPDATE farmData
SET 
    channel_partner = 'Masaka Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Agri Solutions'
WHERE id = 69;

-- Mettre à jour l'enregistrement 70
UPDATE farmData
SET 
    channel_partner = 'Mityana AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Kabale Agri Coop'
WHERE id = 70;

-- Mettre à jour l'enregistrement 71
UPDATE farmData
SET 
    channel_partner = 'Masaka AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Agri Solutions'
WHERE id = 71;

-- Mettre à jour l'enregistrement 72
UPDATE farmData
SET 
    channel_partner = 'Mbarara Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Kasese Agri Group'
WHERE id = 72;

-- Mettre à jour l'enregistrement 73
UPDATE farmData
SET 
    channel_partner = 'Mbale Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Masindi Agri Coop'
WHERE id = 73;

-- Mettre à jour l'enregistrement 74
UPDATE farmData
SET 
    channel_partner = 'Masaka Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Agri Group'
WHERE id = 74;

-- Mettre à jour l'enregistrement 75
UPDATE farmData
SET 
    channel_partner = 'Mityana AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Masaka Agri Coop'
WHERE id = 75;

-- Mettre à jour l'enregistrement 76
UPDATE farmData
SET 
    channel_partner = 'Masindi AgroPro',
    destination_country = 'Uganda',
    customer_name = 'Jinja Agri Coop'
WHERE id = 76;

-- Mettre à jour l'enregistrement 77
UPDATE farmData
SET 
    channel_partner = 'Kasese Agro Group',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Agri Solutions'
WHERE id = 77;

-- Mettre à jour l'enregistrement 78
UPDATE farmData
SET 
    channel_partner = 'Mbarara Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Kasese Agri Coop'
WHERE id = 78;

-- Mettre à jour l'enregistrement 79
UPDATE farmData
SET 
    channel_partner = 'Mbale Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Masaka Agri Solutions'
WHERE id = 79;

-- Mettre à jour l'enregistrement 80
UPDATE farmData
SET 
    channel_partner = 'Masaka Agro Solutions',
    destination_country = 'Uganda',
    customer_name = 'Mbarara Agri Solutions'
WHERE id = 80;


INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(1,1,1001,'Device1','Owner1',0.59999999999999997779,0.29999999999999998889,0.4000000000000000222,6.5,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(2,1,1002,'Device2','Owner2',0.4000000000000000222,0.2000000000000000111,0.5,6.7999999999999998223,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(3,1,1003,'Device3','Owner3',0.5,0.4000000000000000222,0.29999999999999998889,6.2000000000000001776,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(4,2,1004,'Device4','Owner4',0.69999999999999995559,0.5,0.4000000000000000222,6.5999999999999996447,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(5,2,1005,'Device5','Owner5',0.5,0.29999999999999998889,0.59999999999999997779,6.9000000000000003552,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(6,2,1006,'Device6','Owner6',0.59999999999999997779,0.4000000000000000222,0.5,6.2999999999999998223,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(7,3,1007,'Device7','Owner7',0.8000000000000000444,0.59999999999999997779,0.4000000000000000222,6.7000000000000001776,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(8,3,1008,'Device8','Owner8',0.4000000000000000222,0.29999999999999998889,0.69999999999999995559,7.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(9,3,1009,'Device9','Owner9',0.69999999999999995559,0.5,0.59999999999999997779,6.4000000000000003552,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(10,4,1010,'Device10','Owner10',0.5,0.4000000000000000222,0.29999999999999998889,6.7999999999999998223,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(11,4,1011,'Device11','Owner11',0.59999999999999997779,0.29999999999999998889,0.5,7.0999999999999996447,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(12,4,1012,'Device12','Owner12',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,6.5,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(13,5,1013,'Device13','Owner13',0.9000000000000000222,0.8000000000000000444,0.4000000000000000222,6.9000000000000003552,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(14,5,1014,'Device14','Owner14',0.59999999999999997779,0.5,0.69999999999999995559,7.2000000000000001776,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(15,5,1015,'Device15','Owner15',0.69999999999999995559,0.59999999999999997779,0.59999999999999997779,6.5999999999999996447,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(16,6,1016,'Device16','Owner16',0.5,0.4000000000000000222,0.29999999999999998889,7.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(17,6,1017,'Device17','Owner17',0.59999999999999997779,0.5,0.5,7.2999999999999998223,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(18,6,1018,'Device18','Owner18',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,6.7000000000000001776,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(19,7,1019,'Device19','Owner19',0.9000000000000000222,0.8000000000000000444,0.4000000000000000222,7.0999999999999996447,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(20,7,1020,'Device20','Owner20',0.59999999999999997779,0.5,0.8000000000000000444,7.4000000000000003552,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(21,7,1021,'Device21','Owner21',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,6.7999999999999998223,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(22,8,1022,'Device22','Owner22',0.5,0.4000000000000000222,0.4000000000000000222,7.2000000000000001776,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(23,8,1023,'Device23','Owner23',0.59999999999999997779,0.5,0.59999999999999997779,7.5,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(24,8,1024,'Device24','Owner24',0.8000000000000000444,0.69999999999999995559,0.5,6.9000000000000003552,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(25,9,1025,'Device25','Owner25',0.9000000000000000222,0.8000000000000000444,0.29999999999999998889,7.2999999999999998223,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(26,9,1026,'Device26','Owner26',0.59999999999999997779,0.5,0.9000000000000000222,7.5999999999999996447,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(27,9,1027,'Device27','Owner27',0.69999999999999995559,0.59999999999999997779,0.8000000000000000444,7.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(28,10,1028,'Device28','Owner28',0.5,0.4000000000000000222,0.5,7.4000000000000003552,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(29,10,1029,'Device29','Owner29',0.59999999999999997779,0.5,0.69999999999999995559,7.7000000000000001776,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(30,10,1030,'Device30','Owner30',0.8000000000000000444,0.69999999999999995559,0.4000000000000000222,7.0999999999999996447,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(31,11,1031,'Device31','Owner31',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,7.5,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(32,11,1032,'Device32','Owner32',0.59999999999999997779,0.5,0.8000000000000000444,7.7999999999999998223,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(33,11,1033,'Device33','Owner33',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,7.2000000000000001776,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(34,12,1034,'Device34','Owner34',0.5,0.4000000000000000222,0.4000000000000000222,7.5999999999999996447,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(35,12,1035,'Device35','Owner35',0.59999999999999997779,0.5,0.59999999999999997779,7.9000000000000003552,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(36,12,1036,'Device36','Owner36',0.8000000000000000444,0.69999999999999995559,0.5,7.2999999999999998223,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(37,13,1037,'Device37','Owner37',0.9000000000000000222,0.8000000000000000444,0.29999999999999998889,7.7000000000000001776,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(38,13,1038,'Device38','Owner38',0.59999999999999997779,0.5,0.9000000000000000222,8.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(39,13,1039,'Device39','Owner39',0.69999999999999995559,0.59999999999999997779,0.8000000000000000444,7.4000000000000003552,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(40,14,1040,'Device40','Owner40',0.5,0.4000000000000000222,0.5,7.7999999999999998223,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(41,14,1041,'Device41','Owner41',0.59999999999999997779,0.5,0.69999999999999995559,8.0999999999999996447,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(42,14,1042,'Device42','Owner42',0.8000000000000000444,0.69999999999999995559,0.4000000000000000222,7.5,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(43,15,1043,'Device43','Owner43',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,7.9000000000000003552,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(44,15,1044,'Device44','Owner44',0.59999999999999997779,0.5,0.8000000000000000444,8.1999999999999992894,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(45,15,1045,'Device45','Owner45',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,7.5999999999999996447,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(46,16,1046,'Device46','Owner46',0.5,0.4000000000000000222,0.4000000000000000222,8.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(47,16,1047,'Device47','Owner47',0.59999999999999997779,0.5,0.59999999999999997779,8.3000000000000007105,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(48,16,1048,'Device48','Owner48',0.8000000000000000444,0.69999999999999995559,0.5,7.7000000000000001776,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(49,17,1049,'Device49','Owner49',0.9000000000000000222,0.8000000000000000444,0.29999999999999998889,8.0999999999999996447,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(50,17,1050,'Device50','Owner50',0.59999999999999997779,0.5,0.9000000000000000222,8.4000000000000003552,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(51,18,1051,'Device51','Owner51',0.69999999999999995559,0.59999999999999997779,0.5,7.7999999999999998223,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(52,18,1052,'Device52','Owner52',0.8000000000000000444,0.69999999999999995559,0.69999999999999995559,8.0999999999999996447,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(53,18,1053,'Device53','Owner53',0.5,0.4000000000000000222,0.59999999999999997779,7.5,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(54,19,1054,'Device54','Owner54',0.9000000000000000222,0.8000000000000000444,0.4000000000000000222,8.1999999999999992894,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(55,19,1055,'Device55','Owner55',0.59999999999999997779,0.5,0.8000000000000000444,8.5,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(56,19,1056,'Device56','Owner56',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,7.9000000000000003552,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(57,20,1057,'Device57','Owner57',0.5,0.4000000000000000222,0.5,8.3000000000000007105,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(58,20,1058,'Device58','Owner58',0.59999999999999997779,0.5,0.69999999999999995559,8.5999999999999996447,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(59,20,1059,'Device59','Owner59',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,8.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(60,21,1060,'Device60','Owner60',0.9000000000000000222,0.8000000000000000444,0.29999999999999998889,8.4000000000000003552,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(61,21,1061,'Device61','Owner61',0.59999999999999997779,0.5,0.9000000000000000222,8.6999999999999992894,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(62,21,1062,'Device62','Owner62',0.69999999999999995559,0.59999999999999997779,0.8000000000000000444,8.0999999999999996447,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(63,22,1063,'Device63','Owner63',0.5,0.4000000000000000222,0.4000000000000000222,8.5,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(64,22,1064,'Device64','Owner64',0.59999999999999997779,0.5,0.59999999999999997779,8.8000000000000007105,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(65,22,1065,'Device65','Owner65',0.8000000000000000444,0.69999999999999995559,0.5,8.1999999999999992894,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(66,23,1066,'Device66','Owner66',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,8.5999999999999996447,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(67,23,1067,'Device67','Owner67',0.59999999999999997779,0.5,0.8000000000000000444,8.9000000000000003552,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(68,23,1068,'Device68','Owner68',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,8.3000000000000007105,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(69,24,1069,'Device69','Owner69',0.5,0.4000000000000000222,0.5,8.6999999999999992894,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(70,24,1070,'Device70','Owner70',0.59999999999999997779,0.5,0.69999999999999995559,9.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(71,24,1071,'Device71','Owner71',0.8000000000000000444,0.69999999999999995559,0.4000000000000000222,8.4000000000000003552,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(72,25,1072,'Device72','Owner72',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,8.8000000000000007105,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(73,25,1073,'Device73','Owner73',0.59999999999999997779,0.5,0.8000000000000000444,9.0999999999999996447,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(74,25,1074,'Device74','Owner74',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,8.5,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(75,26,1075,'Device75','Owner75',0.5,0.4000000000000000222,0.4000000000000000222,8.9000000000000003552,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(76,26,1076,'Device76','Owner76',0.59999999999999997779,0.5,0.59999999999999997779,9.1999999999999992894,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(77,26,1077,'Device77','Owner77',0.8000000000000000444,0.69999999999999995559,0.5,8.5999999999999996447,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(78,27,1078,'Device78','Owner78',0.9000000000000000222,0.8000000000000000444,0.29999999999999998889,9.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(79,27,1079,'Device79','Owner79',0.59999999999999997779,0.5,0.9000000000000000222,9.3000000000000007105,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(80,27,1080,'Device80','Owner80',0.69999999999999995559,0.59999999999999997779,0.8000000000000000444,8.6999999999999992894,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(81,28,1081,'Device81','Owner81',0.5,0.4000000000000000222,0.5,9.0999999999999996447,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(82,28,1082,'Device82','Owner82',0.59999999999999997779,0.5,0.69999999999999995559,9.4000000000000003552,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(83,28,1083,'Device83','Owner83',0.8000000000000000444,0.69999999999999995559,0.4000000000000000222,8.8000000000000007105,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(84,29,1084,'Device84','Owner84',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,9.1999999999999992894,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(85,29,1085,'Device85','Owner85',0.59999999999999997779,0.5,0.8000000000000000444,9.5,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(86,29,1086,'Device86','Owner86',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,8.9000000000000003552,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(87,30,1087,'Device87','Owner87',0.5,0.4000000000000000222,0.4000000000000000222,9.3000000000000007105,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(88,31,1090,'Device90','Owner90',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,9.4000000000000003552,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(89,31,1091,'Device91','Owner91',0.59999999999999997779,0.5,0.8000000000000000444,9.6999999999999992894,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(90,31,1092,'Device92','Owner92',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,9.0999999999999996447,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(91,32,1093,'Device93','Owner93',0.5,0.4000000000000000222,0.5,9.5,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(92,32,1094,'Device94','Owner94',0.59999999999999997779,0.5,0.69999999999999995559,9.8000000000000007105,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(93,32,1095,'Device95','Owner95',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,9.1999999999999992894,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(94,33,1096,'Device96','Owner96',0.9000000000000000222,0.8000000000000000444,0.29999999999999998889,9.5999999999999996447,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(95,33,1097,'Device97','Owner97',0.59999999999999997779,0.5,0.9000000000000000222,9.9000000000000003552,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(96,33,1098,'Device98','Owner98',0.69999999999999995559,0.59999999999999997779,0.8000000000000000444,9.3000000000000007105,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(97,34,1099,'Device99','Owner99',0.5,0.4000000000000000222,0.4000000000000000222,9.6999999999999992894,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(98,34,1100,'Device100','Owner100',0.59999999999999997779,0.5,0.59999999999999997779,10.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(99,34,1101,'Device101','Owner101',0.8000000000000000444,0.69999999999999995559,0.5,9.4000000000000003552,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(100,35,1102,'Device102','Owner102',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,9.8000000000000007105,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(101,35,1103,'Device103','Owner103',0.59999999999999997779,0.5,0.8000000000000000444,10.099999999999999644,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(102,35,1104,'Device104','Owner104',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,9.5,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(103,36,1105,'Device105','Owner105',0.5,0.4000000000000000222,0.5,9.9000000000000003552,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(104,36,1106,'Device106','Owner106',0.59999999999999997779,0.5,0.69999999999999995559,10.199999999999999289,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(105,36,1107,'Device107','Owner107',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,9.5999999999999996447,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(106,37,1108,'Device108','Owner108',0.9000000000000000222,0.8000000000000000444,0.29999999999999998889,10.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(107,37,1109,'Device109','Owner109',0.59999999999999997779,0.5,0.9000000000000000222,10.30000000000000071,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(108,37,1110,'Device110','Owner110',0.69999999999999995559,0.59999999999999997779,0.8000000000000000444,9.6999999999999992894,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(109,38,1111,'Device111','Owner111',0.5,0.4000000000000000222,0.4000000000000000222,10.099999999999999644,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(110,38,1112,'Device112','Owner112',0.59999999999999997779,0.5,0.59999999999999997779,10.400000000000000355,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(111,38,1113,'Device113','Owner113',0.8000000000000000444,0.69999999999999995559,0.5,9.8000000000000007105,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(112,39,1114,'Device114','Owner114',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,10.199999999999999289,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(113,39,1115,'Device115','Owner115',0.59999999999999997779,0.5,0.8000000000000000444,10.499999999999999999,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(114,39,1116,'Device116','Owner116',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,9.9000000000000003552,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(115,40,1117,'Device117','Owner117',0.5,0.4000000000000000222,0.5,10.30000000000000071,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(116,40,1118,'Device118','Owner118',0.59999999999999997779,0.5,0.69999999999999995559,10.599999999999999644,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(117,40,1119,'Device119','Owner119',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,10.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(118,41,1120,'Device120','Owner120',0.9000000000000000222,0.8000000000000000444,0.29999999999999998889,10.400000000000000355,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(119,41,1121,'Device121','Owner121',0.59999999999999997779,0.5,0.9000000000000000222,10.699999999999999289,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(120,41,1122,'Device122','Owner122',0.69999999999999995559,0.59999999999999997779,0.8000000000000000444,10.099999999999999644,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(121,42,1123,'Device123','Owner123',0.5,0.4000000000000000222,0.4000000000000000222,10.499999999999999999,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(122,42,1124,'Device124','Owner124',0.59999999999999997779,0.5,0.59999999999999997779,10.80000000000000071,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(123,42,1125,'Device125','Owner125',0.8000000000000000444,0.69999999999999995559,0.5,10.199999999999999289,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(124,43,1126,'Device126','Owner126',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,10.599999999999999644,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(125,43,1127,'Device127','Owner127',0.59999999999999997779,0.5,0.8000000000000000444,10.900000000000000354,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(126,43,1128,'Device128','Owner128',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,10.30000000000000071,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(127,44,1129,'Device129','Owner129',0.5,0.4000000000000000222,0.5,10.699999999999999289,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(128,44,1130,'Device130','Owner130',0.59999999999999997779,0.5,0.69999999999999995559,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(129,44,1131,'Device131','Owner131',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,10.400000000000000355,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(130,45,1132,'Device132','Owner132',0.9000000000000000222,0.8000000000000000444,0.29999999999999998889,10.80000000000000071,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(131,45,1133,'Device133','Owner133',0.59999999999999997779,0.5,0.9000000000000000222,11.099999999999999644,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(132,45,1134,'Device134','Owner134',0.69999999999999995559,0.59999999999999997779,0.8000000000000000444,10.499999999999999999,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(133,46,1135,'Device135','Owner135',0.5,0.4000000000000000222,0.4000000000000000222,10.900000000000000354,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(134,46,1136,'Device136','Owner136',0.59999999999999997779,0.5,0.59999999999999997779,11.199999999999999289,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(135,46,1137,'Device137','Owner137',0.8000000000000000444,0.69999999999999995559,0.5,10.599999999999999644,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(136,47,1138,'Device138','Owner138',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(137,47,1139,'Device139','Owner139',0.59999999999999997779,0.5,0.8000000000000000444,11.30000000000000071,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(138,47,1140,'Device140','Owner140',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,10.699999999999999289,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(139,48,1141,'Device141','Owner141',0.5,0.4000000000000000222,0.5,11.099999999999999644,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(140,48,1142,'Device142','Owner142',0.59999999999999997779,0.5,0.69999999999999995559,11.400000000000000355,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(141,48,1143,'Device143','Owner143',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,10.80000000000000071,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(142,49,1144,'Device144','Owner144',0.9000000000000000222,0.8000000000000000444,0.29999999999999998889,11.199999999999999289,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(143,49,1145,'Device145','Owner145',0.59999999999999997779,0.5,0.9000000000000000222,11.499999999999999999,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(144,49,1146,'Device146','Owner146',0.69999999999999995559,0.59999999999999997779,0.8000000000000000444,10.900000000000000354,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(145,50,1147,'Device147','Owner147',0.5,0.4000000000000000222,0.4000000000000000222,11.30000000000000071,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(146,50,1148,'Device148','Owner148',0.59999999999999997779,0.5,0.59999999999999997779,11.599999999999999645,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(147,50,1149,'Device149','Owner149',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(148,51,1150,'Device150','Owner150',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.400000000000000355,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(149,52,1151,'Device151','Owner151',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.699999999999999289,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(150,52,1152,'Device152','Owner152',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,11.099999999999999644,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(151,52,1153,'Device153','Owner153',0.5,0.4000000000000000222,0.5,11.499999999999999999,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(152,53,1154,'Device154','Owner154',0.59999999999999997779,0.5,0.69999999999999995559,11.80000000000000071,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(153,53,1155,'Device155','Owner155',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,11.199999999999999289,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(154,53,1156,'Device156','Owner156',0.9000000000000000222,0.8000000000000000444,0.5,11.599999999999999645,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(155,54,1157,'Device157','Owner157',0.59999999999999997779,0.5,0.8000000000000000444,11.900000000000000355,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(156,54,1158,'Device158','Owner158',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.30000000000000071,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(157,54,1159,'Device159','Owner159',0.5,0.4000000000000000222,0.5,11.699999999999999289,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(158,55,1160,'Device160','Owner160',0.59999999999999997779,0.5,0.69999999999999995559,12.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(159,55,1161,'Device161','Owner161',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,11.400000000000000355,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(160,55,1162,'Device162','Owner162',0.9000000000000000222,0.8000000000000000444,0.5,11.80000000000000071,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(161,56,1163,'Device163','Owner163',0.59999999999999997779,0.5,0.8000000000000000444,12.099999999999999644,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(162,56,1164,'Device164','Owner164',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.499999999999999999,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(163,56,1165,'Device165','Owner165',0.5,0.4000000000000000222,0.5,11.900000000000000355,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(164,57,1166,'Device166','Owner166',0.59999999999999997779,0.5,0.69999999999999995559,12.199999999999999289,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(165,57,1167,'Device167','Owner167',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,11.599999999999999645,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(166,57,1168,'Device168','Owner168',0.9000000000000000222,0.8000000000000000444,0.5,12.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(167,58,1169,'Device169','Owner169',0.59999999999999997779,0.5,0.8000000000000000444,12.30000000000000071,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(168,58,1170,'Device170','Owner170',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.699999999999999289,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(169,58,1171,'Device171','Owner171',0.5,0.4000000000000000222,0.5,12.099999999999999644,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(170,59,1172,'Device172','Owner172',0.59999999999999997779,0.5,0.69999999999999995559,12.400000000000000355,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(171,59,1173,'Device173','Owner173',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,11.80000000000000071,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(172,59,1174,'Device174','Owner174',0.9000000000000000222,0.8000000000000000444,0.5,12.199999999999999289,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(173,60,1175,'Device175','Owner175',0.59999999999999997779,0.5,0.8000000000000000444,12.5,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(174,60,1176,'Device176','Owner176',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.900000000000000355,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(175,60,1177,'Device177','Owner177',0.5,0.4000000000000000222,0.5,12.30000000000000071,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(176,61,1178,'Device178','Owner178',0.59999999999999997779,0.5,0.69999999999999995559,12.599999999999999644,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(177,61,1179,'Device179','Owner179',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,12.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(178,61,1180,'Device180','Owner180',0.9000000000000000222,0.8000000000000000444,0.5,12.400000000000000355,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(179,62,1181,'Device181','Owner181',0.59999999999999997779,0.5,0.8000000000000000444,12.699999999999999289,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(180,62,1182,'Device182','Owner182',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,12.099999999999999644,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(181,62,1183,'Device183','Owner183',0.5,0.4000000000000000222,0.5,12.5,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(182,63,1184,'Device184','Owner184',0.59999999999999997779,0.5,0.69999999999999995559,12.80000000000000071,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(183,63,1185,'Device185','Owner185',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,12.199999999999999289,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(184,63,1186,'Device186','Owner186',0.9000000000000000222,0.8000000000000000444,0.5,12.599999999999999644,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(185,64,1187,'Device187','Owner187',0.59999999999999997779,0.5,0.8000000000000000444,12.900000000000000355,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(186,64,1188,'Device188','Owner188',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,12.30000000000000071,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(187,64,1189,'Device189','Owner189',0.5,0.4000000000000000222,0.5,12.699999999999999289,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(188,65,1190,'Device190','Owner190',0.59999999999999997779,0.5,0.69999999999999995559,13.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(189,65,1191,'Device191','Owner191',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,12.400000000000000355,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(190,65,1192,'Device192','Owner192',0.9000000000000000222,0.8000000000000000444,0.5,12.80000000000000071,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(191,66,1193,'Device193','Owner193',0.59999999999999997779,0.5,0.8000000000000000444,13.099999999999999644,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(192,66,1194,'Device194','Owner194',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,12.5,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(193,66,1195,'Device195','Owner195',0.5,0.4000000000000000222,0.5,12.900000000000000355,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(194,67,1196,'Device196','Owner196',0.59999999999999997779,0.5,0.69999999999999995559,13.199999999999999289,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(195,67,1197,'Device197','Owner197',0.8000000000000000444,0.69999999999999995559,0.59999999999999997779,12.599999999999999644,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(196,67,1198,'Device198','Owner198',0.9000000000000000222,0.8000000000000000444,0.5,13.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(197,68,1199,'Device199','Owner199',0.59999999999999997779,0.5,0.8000000000000000444,13.30000000000000071,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(198,68,1200,'Device200','Owner200',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,12.699999999999999289,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(199,69,1201,'Device201','Owner201',0.5,0.4000000000000000222,0.5,13.099999999999999644,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(200,69,1202,'Device202','Owner202',0.59999999999999997779,0.5,0.59999999999999997779,13.400000000000000354,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(201,69,1203,'Device203','Owner203',0.8000000000000000444,0.69999999999999995559,0.5,12.80000000000000071,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(202,70,1204,'Device204','Owner204',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,13.199999999999999289,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(203,70,1205,'Device205','Owner205',0.59999999999999997779,0.5,0.8000000000000000444,13.5,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(204,70,1206,'Device206','Owner206',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,12.900000000000000355,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(205,71,1207,'Device207','Owner207',0.5,0.4000000000000000222,0.5,13.30000000000000071,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(206,71,1208,'Device208','Owner208',0.59999999999999997779,0.5,0.59999999999999997779,13.599999999999999644,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(207,71,1209,'Device209','Owner209',0.8000000000000000444,0.69999999999999995559,0.5,13.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(208,72,1210,'Device210','Owner210',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,13.400000000000000354,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(209,72,1211,'Device211','Owner211',0.59999999999999997779,0.5,0.8000000000000000444,13.699999999999999289,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(210,72,1212,'Device212','Owner212',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,13.099999999999999644,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(211,73,1213,'Device213','Owner213',0.5,0.4000000000000000222,0.5,13.5,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(212,73,1214,'Device214','Owner214',0.59999999999999997779,0.5,0.59999999999999997779,13.80000000000000071,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(213,73,1215,'Device215','Owner215',0.8000000000000000444,0.69999999999999995559,0.5,13.199999999999999289,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(214,74,1216,'Device216','Owner216',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,13.599999999999999644,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(215,74,1217,'Device217','Owner217',0.59999999999999997779,0.5,0.8000000000000000444,13.900000000000000355,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(216,74,1218,'Device218','Owner218',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,13.30000000000000071,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(217,75,1219,'Device219','Owner219',0.5,0.4000000000000000222,0.5,13.699999999999999289,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(218,75,1220,'Device220','Owner220',0.59999999999999997779,0.5,0.59999999999999997779,14.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(219,75,1221,'Device221','Owner221',0.8000000000000000444,0.69999999999999995559,0.5,13.400000000000000354,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(220,76,1222,'Device222','Owner222',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,13.80000000000000071,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(221,76,1223,'Device223','Owner223',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(222,76,1224,'Device224','Owner224',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,13.5,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(223,77,1225,'Device225','Owner225',0.5,0.4000000000000000222,0.5,13.900000000000000355,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(224,77,1226,'Device226','Owner226',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(225,77,1227,'Device227','Owner227',0.8000000000000000444,0.69999999999999995559,0.5,13.599999999999999644,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(226,78,1228,'Device228','Owner228',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,14.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(227,78,1229,'Device229','Owner229',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(228,78,1230,'Device230','Owner230',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,13.699999999999999289,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(229,79,1231,'Device231','Owner231',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(230,79,1232,'Device232','Owner232',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(231,79,1233,'Device233','Owner233',0.8000000000000000444,0.69999999999999995559,0.5,13.80000000000000071,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(232,80,1234,'Device234','Owner234',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(233,80,1235,'Device235','Owner235',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(234,80,1236,'Device236','Owner236',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,13.900000000000000355,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(235,81,1237,'Device237','Owner237',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(236,81,1238,'Device238','Owner238',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(237,81,1239,'Device239','Owner239',0.8000000000000000444,0.69999999999999995559,0.5,14.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(238,82,1240,'Device240','Owner240',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(239,82,1241,'Device241','Owner241',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(240,82,1242,'Device242','Owner242',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(241,83,1243,'Device243','Owner243',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(242,83,1244,'Device244','Owner244',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(243,83,1245,'Device245','Owner245',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(244,84,1246,'Device246','Owner246',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(245,84,1247,'Device247','Owner247',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(246,84,1248,'Device248','Owner248',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(247,85,1249,'Device249','Owner249',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(248,85,1250,'Device250','Owner250',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(249,85,1251,'Device251','Owner251',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(250,86,1252,'Device252','Owner252',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(251,86,1253,'Device253','Owner253',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(252,86,1254,'Device254','Owner254',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(253,87,1255,'Device255','Owner255',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(254,87,1256,'Device256','Owner256',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(255,87,1257,'Device257','Owner257',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(256,88,1258,'Device258','Owner258',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(257,88,1259,'Device259','Owner259',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(258,88,1260,'Device260','Owner260',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(259,89,1261,'Device261','Owner261',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(260,89,1262,'Device262','Owner262',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(261,89,1263,'Device263','Owner263',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(262,90,1264,'Device264','Owner264',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(263,90,1265,'Device265','Owner265',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(264,90,1266,'Device266','Owner266',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(265,91,1267,'Device267','Owner267',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(266,91,1268,'Device268','Owner268',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(267,91,1269,'Device269','Owner269',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(268,92,1270,'Device270','Owner270',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(269,92,1271,'Device271','Owner271',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(270,92,1272,'Device272','Owner272',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(271,93,1273,'Device273','Owner273',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(272,93,1274,'Device274','Owner274',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(273,93,1275,'Device275','Owner275',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(274,94,1276,'Device276','Owner276',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(275,94,1277,'Device277','Owner277',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(276,94,1278,'Device278','Owner278',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(277,95,1279,'Device279','Owner279',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(278,95,1280,'Device280','Owner280',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(279,95,1281,'Device281','Owner281',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(280,96,1282,'Device282','Owner282',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(281,96,1283,'Device283','Owner283',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(282,96,1284,'Device284','Owner284',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(283,97,1285,'Device285','Owner285',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(284,97,1286,'Device286','Owner286',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(285,97,1287,'Device287','Owner287',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(286,98,1288,'Device288','Owner288',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(287,98,1289,'Device289','Owner289',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(288,98,1290,'Device290','Owner290',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(289,99,1291,'Device291','Owner291',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(290,99,1292,'Device292','Owner292',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(291,99,1293,'Device293','Owner293',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(292,100,1294,'Device294','Owner294',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(293,100,1295,'Device295','Owner295',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(294,100,1296,'Device296','Owner296',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(295,101,1297,'Device297','Owner297',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(296,101,1298,'Device298','Owner298',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(297,101,1299,'Device299','Owner299',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(298,102,1300,'Device300','Owner300',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(299,102,1301,'Device301','Owner301',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(300,102,1302,'Device302','Owner302',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(301,103,1303,'Device303','Owner303',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(302,103,1304,'Device304','Owner304',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(303,103,1305,'Device305','Owner305',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(304,104,1306,'Device306','Owner306',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(305,104,1307,'Device307','Owner307',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(306,104,1308,'Device308','Owner308',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(307,105,1309,'Device309','Owner309',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(308,105,1310,'Device310','Owner310',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(309,105,1311,'Device311','Owner311',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(310,106,1312,'Device312','Owner312',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(311,106,1313,'Device313','Owner313',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(312,106,1314,'Device314','Owner314',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(313,107,1315,'Device315','Owner315',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(314,107,1316,'Device316','Owner316',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(315,107,1317,'Device317','Owner317',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(316,108,1318,'Device318','Owner318',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(317,108,1319,'Device319','Owner319',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(318,108,1320,'Device320','Owner320',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(319,109,1321,'Device321','Owner321',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(320,109,1322,'Device322','Owner322',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(321,109,1323,'Device323','Owner323',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(322,110,1324,'Device324','Owner324',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(323,110,1325,'Device325','Owner325',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(324,110,1326,'Device326','Owner326',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(325,111,1327,'Device327','Owner327',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(326,111,1328,'Device328','Owner328',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(327,111,1329,'Device329','Owner329',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(328,112,1330,'Device330','Owner330',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(329,112,1331,'Device331','Owner331',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(330,112,1332,'Device332','Owner332',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(331,113,1333,'Device333','Owner333',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(332,113,1334,'Device334','Owner334',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(333,113,1335,'Device335','Owner335',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(334,114,1336,'Device336','Owner336',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(335,114,1337,'Device337','Owner337',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(336,114,1338,'Device338','Owner338',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(337,115,1339,'Device339','Owner339',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(338,115,1340,'Device340','Owner340',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(339,115,1341,'Device341','Owner341',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(340,116,1342,'Device342','Owner342',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(341,116,1343,'Device343','Owner343',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(342,116,1344,'Device344','Owner344',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(343,117,1345,'Device345','Owner345',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(344,117,1346,'Device346','Owner346',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(345,117,1347,'Device347','Owner347',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(346,118,1348,'Device348','Owner348',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(347,118,1349,'Device349','Owner349',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(348,118,1350,'Device350','Owner350',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(349,119,1351,'Device351','Owner351',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(350,119,1352,'Device352','Owner352',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(351,119,1353,'Device353','Owner353',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(352,120,1354,'Device354','Owner354',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(353,120,1355,'Device355','Owner355',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(354,120,1356,'Device356','Owner356',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(355,121,1357,'Device357','Owner357',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(356,121,1358,'Device358','Owner358',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(357,121,1359,'Device359','Owner359',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(358,122,1360,'Device360','Owner360',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(359,122,1361,'Device361','Owner361',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(360,122,1362,'Device362','Owner362',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(361,123,1363,'Device363','Owner363',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(362,123,1364,'Device364','Owner364',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(363,123,1365,'Device365','Owner365',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(364,124,1366,'Device366','Owner366',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(365,124,1367,'Device367','Owner367',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(366,124,1368,'Device368','Owner368',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(367,125,1369,'Device369','Owner369',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(368,125,1370,'Device370','Owner370',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(369,125,1371,'Device371','Owner371',0.8000000000000000444,0.69999999999999995559,0.5,11.0,24.0,57.0,90.0,-73.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(370,16,1372,'Device372','Owner372',0.9000000000000000222,0.8000000000000000444,0.59999999999999997779,11.0,25.0,60.0,100.0,-70.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(371,16,1373,'Device373','Owner373',0.59999999999999997779,0.5,0.8000000000000000444,11.0,26.0,62.0,110.0,-68.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(372,12,1374,'Device374','Owner374',0.69999999999999995559,0.59999999999999997779,0.69999999999999995559,11.0,24.5,58.0,95.0,-72.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(373,12,1375,'Device375','Owner375',0.5,0.4000000000000000222,0.5,11.0,25.499999999999999999,61.0,105.0,-69.0,'2024-02-01');
INSERT INTO soilData (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES(374,12,1376,'Device376','Owner376',0.59999999999999997779,0.5,0.59999999999999997779,11.0,26.5,63.0,115.0,-67.0,'2024-02-01');



