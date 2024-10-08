
DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `district`;
DROP TABLE IF EXISTS `producecategory`;
DROP TABLE IF EXISTS `farmergroup`;
DROP TABLE IF EXISTS `crop`;
DROP TABLE IF EXISTS `farm`;
DROP TABLE IF EXISTS `forest`;
DROP TABLE IF EXISTS `point`;
DROP TABLE IF EXISTS `farmdata`;
DROP TABLE IF EXISTS `soildata`;
DROP TABLE IF EXISTS `tree`;

CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(150) COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(150) COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(150) COLLATE utf8mb4_general_ci NOT NULL,
  `phonenumber` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `user_type` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `is_admin` tinyint(1) DEFAULT '0',
  `date_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `date_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
);
CREATE TABLE `district` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `region` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `date_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `date_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `modified_by` int DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_district_modified_by` (`modified_by`),
  KEY `fk_district_created_by` (`created_by`),
  CONSTRAINT `fk_district_created_by` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_district_modified_by` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`)
);
CREATE TABLE `producecategory` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `grade` int NOT NULL,
  `date_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `date_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
); 
CREATE TABLE `farmergroup` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `description` text COLLATE utf8mb4_general_ci,
  `date_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `date_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `modified_by` int DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_farmergroup_modified_by` (`modified_by`),
  KEY `fk_farmergroup_created_by` (`created_by`),
  CONSTRAINT `fk_farmergroup_created_by` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_farmergroup_modified_by` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`)
);
CREATE TABLE `crop` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `weight` float NOT NULL,
  `category_id` int NOT NULL,
  `date_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `date_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `modified_by` int DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `fk_crop_modified_by` (`modified_by`),
  KEY `fk_crop_created_by` (`created_by`),
  CONSTRAINT `crop_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `producecategory` (`id`),
  CONSTRAINT `fk_category_id` FOREIGN KEY (`category_id`) REFERENCES `producecategory` (`id`),
  CONSTRAINT `fk_crop_created_by` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_crop_modified_by` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`)
);

CREATE TABLE `farm` (
  `id` int NOT NULL AUTO_INCREMENT,
  `farm_id` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `subcounty` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `farmergroup_id` int NOT NULL,
  `district_id` int NOT NULL,
  `geolocation` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `date_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `date_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `phonenumber` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `phonenumber2` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `modified_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `farm_id` (`farm_id`),
  KEY `farmergroup_id` (`farmergroup_id`),
  KEY `district_id` (`district_id`),
  KEY `fk_farm_created_by` (`created_by`),
  KEY `fk_farm_modified_by` (`modified_by`),
  CONSTRAINT `farm_ibfk_1` FOREIGN KEY (`farmergroup_id`) REFERENCES `farmergroup` (`id`),
  CONSTRAINT `farm_ibfk_2` FOREIGN KEY (`district_id`) REFERENCES `district` (`id`),
  CONSTRAINT `fk_farm_created_by` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_farm_district_id` FOREIGN KEY (`district_id`) REFERENCES `district` (`id`),
  CONSTRAINT `fk_farm_farmergroup_id` FOREIGN KEY (`farmergroup_id`) REFERENCES `farmergroup` (`id`),
  CONSTRAINT `fk_farm_modified_by` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`)
); 

CREATE TABLE `forest` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `date_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `date_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_by` int DEFAULT NULL,
  `modified_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_forest_created_by` (`created_by`),
  KEY `fk_forest_modified_by` (`modified_by`),
  CONSTRAINT `fk_forest_created_by` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_forest_modified_by` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`)
);

CREATE TABLE `point` (
  `id` int NOT NULL AUTO_INCREMENT,
  `longitude` float NOT NULL,
  `latitude` float NOT NULL,
  `owner_type` enum('forest','farmer') COLLATE utf8mb4_general_ci NOT NULL,
  `forest_id` int DEFAULT NULL,
  `farmer_id` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `district_id` int NOT NULL,
  `date_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `date_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_by` int DEFAULT NULL,
  `modified_by` int DEFAULT NULL,
  `tree_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `forest_id` (`forest_id`),
  KEY `farmer_id` (`farmer_id`),
  KEY `district_id` (`district_id`),
  KEY `fk_point_created_by` (`created_by`),
  KEY `fk_point_modified_by` (`modified_by`),
  CONSTRAINT `fk_point_created_by` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_point_district_id` FOREIGN KEY (`district_id`) REFERENCES `district` (`id`),
  CONSTRAINT `fk_point_forest_id` FOREIGN KEY (`forest_id`) REFERENCES `forest` (`id`),
  CONSTRAINT `fk_point_modified_by` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`),
  CONSTRAINT `point_ibfk_1` FOREIGN KEY (`forest_id`) REFERENCES `forest` (`id`),
  CONSTRAINT `point_ibfk_2` FOREIGN KEY (`farmer_id`) REFERENCES `farm` (`farm_id`),
  CONSTRAINT `point_ibfk_3` FOREIGN KEY (`district_id`) REFERENCES `district` (`id`),
  CONSTRAINT `CONSTRAINT_1` CHECK ((((`owner_type` = _utf8mb4'forest') and (`forest_id` is not null) and (`farmer_id` is null)) or ((`owner_type` = _utf8mb4'farmer') and (`farmer_id` is not null) and (`forest_id` is null))))
);
CREATE TABLE `farmdata` (
  `id` int NOT NULL AUTO_INCREMENT,
  `farm_id` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `crop_id` int NOT NULL,
  `land_type` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `tilled_land_size` float NOT NULL,
  `planting_date` date NOT NULL,
  `season` int NOT NULL,
  `quality` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `quantity` int NOT NULL,
  `harvest_date` date NOT NULL,
  `expected_yield` float NOT NULL,
  `actual_yield` float NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `channel_partner` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `destination_country` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `customer_name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `date_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `date_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_by` int DEFAULT NULL,
  `modified_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `farm_id` (`farm_id`),
  KEY `crop_id` (`crop_id`),
  KEY `fk_farmdata_created_by` (`created_by`),
  KEY `fk_farmdata_modified_by` (`modified_by`),
  CONSTRAINT `farmdata_ibfk_1` FOREIGN KEY (`farm_id`) REFERENCES `farm` (`farm_id`),
  CONSTRAINT `farmdata_ibfk_2` FOREIGN KEY (`crop_id`) REFERENCES `crop` (`id`),
  CONSTRAINT `fk_farmdata_created_by` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_farmdata_crop_id` FOREIGN KEY (`crop_id`) REFERENCES `crop` (`id`),
  CONSTRAINT `fk_farmdata_farm_id` FOREIGN KEY (`farm_id`) REFERENCES `farm` (`farm_id`),
  CONSTRAINT `fk_farmdata_modified_by` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`)
);


CREATE TABLE `soildata` (
  `id` int NOT NULL AUTO_INCREMENT,
  `district_id` int NOT NULL,
  `internal_id` int NOT NULL,
  `device` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `owner` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `nitrogen` float NOT NULL,
  `phosphorus` float NOT NULL,
  `potassium` float NOT NULL,
  `ph` float NOT NULL,
  `temperature` float NOT NULL,
  `humidity` float NOT NULL,
  `conductivity` float NOT NULL,
  `signal_level` float NOT NULL,
  `date` date NOT NULL,
  `date_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `date_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_by` int DEFAULT NULL,
  `modified_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `district_id` (`district_id`),
  KEY `fk_soildata_created_by` (`created_by`),
  KEY `fk_soildata_modified_by` (`modified_by`),
  CONSTRAINT `fk_soildata_created_by` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_soildata_district_id` FOREIGN KEY (`district_id`) REFERENCES `district` (`id`),
  CONSTRAINT `fk_soildata_modified_by` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`),
  CONSTRAINT `soildata_ibfk_1` FOREIGN KEY (`district_id`) REFERENCES `district` (`id`)
);
CREATE TABLE `tree` (
  `id` int NOT NULL AUTO_INCREMENT,
  `forest_id` int NOT NULL,
  `point_id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `height` float NOT NULL,
  `diameter` float NOT NULL,
  `date_planted` date NOT NULL,
  `date_cut` date DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `modified_by` int DEFAULT NULL,
  `date_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `date_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `forest_id` (`forest_id`),
  KEY `point_id` (`point_id`),
  KEY `created_by` (`created_by`),
  KEY `modified_by` (`modified_by`),
  CONSTRAINT `tree_ibfk_1` FOREIGN KEY (`forest_id`) REFERENCES `forest` (`id`),
  CONSTRAINT `tree_ibfk_2` FOREIGN KEY (`point_id`) REFERENCES `point` (`id`),
  CONSTRAINT `tree_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `tree_ibfk_4` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`)
);


INSERT INTO `user` VALUES (2,'Admin','admin@admin.admin','pbkdf2:sha256:600000$us9tk0a4zUPQBs8f$06f2ace9bba750792ab34515795ebc53a5fce96d450c9fac0f23ab90e14effb5','0303030303','admin',1,'2024-06-11 08:03:32','2024-06-11 08:03:32'),(3,'sasakawa1','sasakawa1@agriyields.com','pbkdf2:sha256:600000$zQFb0iorZfRBdryr$cfc389cd12727383093280f9a2ba14f23f210427e17d076b5fe563a53bd04e4d','25678123456','farmer',0,'2024-06-11 09:04:36','2024-06-11 09:04:36'),(4,'sasakawa2','sasakawa2@agriyields.com','pbkdf2:sha256:600000$6M2tFAyX2JeNUZaj$4e11ba6e82153b9f21a88f9161718aa1337956f460f71ff26eb3766e7a590a6c','25678654321','farmer',0,'2024-06-11 09:05:13','2024-06-11 09:05:13'),(5,'sasakawa3','sasakawa3@agriyields.com','pbkdf2:sha256:600000$pQInTYpAXjrI33ec$91b504e360d3531803c2b7da12a91230516f630cc3706824cde9709e5437c6b8','25675654321','farmer',0,'2024-06-11 09:05:43','2024-06-11 09:05:43'),(6,'brian','lwetutb@agriyields.com','pbkdf2:sha256:600000$cTRyZKoIYutjZTJ2$362c2fd768417acee8518367b294f72c92580b286a0827040293777b7ac9887c','256783130358','admin',1,'2024-06-11 09:29:11','2024-06-11 09:29:11'),(8,'theo@agriyields.com','theo@agriyields.com','pbkdf2:sha256:600000$mLUrCNtvYpofxGIh$e8937ad25e22bb2fd724e1829c2d48d2c6ffd5c42ab16526e730c3386eb40edc','256703123456','forest',0,'2024-06-11 19:43:18','2024-06-11 19:43:18'),(9,'bahati','bahati@agriyields.com','pbkdf2:sha256:600000$PGbJErsb3epKf0rN$208bbb5893bb089a3e0adfeb62fea4442b6085bdbde8932bbc7c2589e24f7339','256772621397','farmer',0,'2024-06-24 13:34:21','2024-06-24 13:34:21');
INSERT INTO `district` VALUES (1,'Buikwe','Central','2024-06-11 09:01:59','2024-06-11 09:01:59',NULL,NULL),(2,'Mpigi','Central','2024-06-11 09:02:09','2024-06-11 09:02:09',NULL,NULL),(3,'Wakiso','Central','2024-06-11 09:02:21','2024-06-11 09:02:21',NULL,NULL),(4,'Luweero','Central','2024-06-11 09:02:33','2024-06-11 09:02:33',NULL,NULL),(5,'Masaka','Central','2024-06-11 09:02:47','2024-06-11 09:02:47',NULL,NULL),(6,'Kalangala','Central','2024-06-11 09:03:02','2024-06-11 09:03:02',NULL,NULL),(7,'Mbarara','West','2024-06-11 09:03:19','2024-06-11 09:03:19',NULL,NULL),(8,'Mbale','East','2024-06-11 09:03:29','2024-06-11 09:03:29',NULL,NULL),(9,'Kabarole ','West','2024-06-24 14:06:44','2024-06-24 14:06:44',NULL,NULL),(10,'Gulu','North','2024-06-25 08:54:53','2024-06-25 08:54:53',NULL,NULL),(11,'Lira','North','2024-06-25 08:55:03','2024-06-25 08:55:03',NULL,NULL),(12,'Jinja','East','2024-06-25 08:55:19','2024-06-25 08:55:19',NULL,NULL),(13,'Mayuge','East','2024-06-25 08:55:38','2024-06-25 08:55:38',NULL,NULL),(14,'Bukomansimbi','Central','2024-06-25 08:55:55','2024-06-25 08:55:55',NULL,NULL);
INSERT INTO `producecategory` VALUES (1,'Cocoa',1,'2024-06-11 09:14:53','2024-06-11 09:14:53'),(2,'Coffee Robusta',1,'2024-06-11 09:15:10','2024-06-11 09:15:10'),(3,'Coffee Arabica',1,'2024-06-11 09:15:21','2024-06-11 09:15:21'),(4,'Palm Oil',2,'2024-06-11 09:15:38','2024-06-11 09:15:38'),(5,'Soya Bean',3,'2024-06-11 09:15:50','2024-06-11 09:15:50'),(6,'Rubber',1,'2024-06-11 09:16:24','2024-06-11 09:16:24');
INSERT INTO `farmergroup` VALUES (1,'Buikwe Cocoa','Sasakawa Cocoa Farmers','2024-06-11 09:00:27','2024-06-11 09:00:27',NULL,NULL),(2,'Mpigi Cocoa Farmers','Mpigi Cocoa Farmers','2024-06-11 09:01:11','2024-06-11 09:01:11',NULL,NULL),(3,'HFZ Kabumba','Hungerfree Coop','2024-06-11 10:22:44','2024-06-11 10:22:44',NULL,NULL),(4,'AbanyaRwenzori Coop','Rwenzori Subregion-Arabica Coffee','2024-06-24 14:06:03','2024-06-24 14:06:03',NULL,NULL);
INSERT INTO `crop` VALUES (1,'Cocoa',1,1,'2024-06-11 09:17:49','2024-06-11 09:17:49',NULL,NULL),(2,'Coffee Robusta',1,2,'2024-06-11 09:18:10','2024-06-11 09:18:10',NULL,NULL),(3,'Coffee Arabica',1,3,'2024-06-11 09:18:29','2024-06-11 09:18:29',NULL,NULL),(4,'Oil Palm',2,4,'2024-06-11 09:18:43','2024-06-11 09:18:43',NULL,NULL),(5,'Soya Bean',1,5,'2024-06-11 09:19:00','2024-06-11 09:19:00',NULL,NULL),(6,'Rubber',3,6,'2024-06-11 09:19:23','2024-06-11 09:19:23',NULL,NULL),(7,'Hass Avocado',1,4,'2024-06-21 11:51:47','2024-06-21 11:51:47',NULL,NULL);
INSERT INTO `farm` VALUES (1,'B0001','Isiah Namanya','1',1,1,'0.38551,33.3421','2024-06-11 09:08:19','2024-06-11 09:08:19',NULL,NULL,NULL,NULL),(3,'WAK0002','Lwetutte Brian','Busukuma',3,3,'0.545614,32.579339','2024-06-21 11:50:52','2024-06-21 11:50:52','256783130358','256756411682',NULL,NULL),(5,'KBRL001','Jackus Munihera','Karangura',4,9,'0.658541,30.156032','2024-06-24 14:22:52','2024-06-24 14:22:52','25674123456','25675123456',NULL,NULL),(6,'KBRL004','John Mugisha','Karangura',4,9,'0.69297,30.180577','2024-06-25 10:18:54','2024-06-25 10:18:54','','',NULL,NULL),(7,'KBRL003','Daniel Maate','Karangura',4,9,'0.69391,30.180621','2024-06-25 10:26:38','2024-06-25 10:26:38','','',NULL,NULL),(8,'KBRL002','Musoki Faibe','Karangura',4,9,'0.658917,30.156655','2024-06-25 10:28:22','2024-06-25 10:28:22','','',NULL,NULL),(9,'BUIK002','Bwebale Badru','Ngoogwe',1,1,'0.257593,32.923496','2024-06-25 19:52:04','2024-06-25 19:52:04','','',NULL,NULL),(10,'BUIK003','Mafuko Muzamiru','Ngoogwe',1,1,'0.234431,32.910984','2024-06-25 20:01:21','2024-06-25 20:01:21','256755976395','',NULL,NULL);
INSERT INTO `forest` VALUES (1,'Mulimbwa-Namawaata','2024-06-11 09:32:39','2024-06-11 09:32:39',NULL,NULL),(2,'Mulimbwa-Adjacent','2024-06-21 07:25:55','2024-06-21 07:25:55',NULL,NULL),(4,'Bweyogerere-Eucalyptus-Bypass','2024-06-21 08:09:27','2024-06-21 08:09:27',NULL,NULL),(5,'Eucalyptus- SmallNBypass','2024-06-21 08:22:21','2024-06-21 08:22:21',NULL,NULL);
INSERT INTO `farmdata` VALUES (1,'B0001',1,'Titled',2,'2024-06-11',1,'1',2000,'2024-06-29',2000,1800,'2024-10-29 12:21:00','Sasakawa','Italy','AgroPlus','2024-06-11 09:23:06','2024-06-11 09:23:06',NULL,NULL),(2,'WAK0002',7,'Titled',2,'2024-02-01',2,'1',2,'2024-08-29',3,2,'2024-08-30 20:03:00','Sasakawa','Italy','AgroPlus','2024-06-21 12:03:51','2024-06-21 12:03:51',NULL,NULL);
INSERT INTO `point` VALUES (2,32.5866,0.545164,'forest',1,NULL,3,'2024-06-20 19:30:27','2024-06-20 19:30:27',NULL,NULL,NULL),(3,32.5883,0.544809,'forest',1,NULL,3,'2024-06-20 19:32:45','2024-06-20 19:32:45',NULL,NULL,NULL),(4,32.5902,0.5437,'forest',1,NULL,3,'2024-06-20 19:33:31','2024-06-20 19:33:31',NULL,NULL,NULL),(5,32.5906,0.542582,'forest',1,NULL,3,'2024-06-20 19:34:23','2024-06-20 19:34:23',NULL,NULL,NULL),(6,32.5903,0.542391,'forest',1,NULL,3,'2024-06-20 19:36:24','2024-06-20 19:36:24',NULL,NULL,NULL),(7,32.5901,0.542102,'forest',1,NULL,3,'2024-06-20 19:37:18','2024-06-20 19:37:18',NULL,NULL,NULL),(8,32.5891,0.541376,'forest',1,NULL,3,'2024-06-20 19:38:04','2024-06-20 19:38:04',NULL,NULL,NULL),(9,32.5881,0.540543,'forest',1,NULL,3,'2024-06-20 19:38:54','2024-06-20 19:38:54',NULL,NULL,NULL),(11,32.5867,0.540862,'forest',1,NULL,3,'2024-06-20 19:44:06','2024-06-20 19:44:06',NULL,NULL,NULL),(12,32.5864,0.541312,'forest',1,NULL,3,'2024-06-20 19:44:48','2024-06-20 19:44:48',NULL,NULL,NULL),(13,32.5869,0.542019,'forest',1,NULL,3,'2024-06-20 19:45:24','2024-06-20 19:45:24',NULL,NULL,NULL),(14,32.5863,0.541702,'forest',1,NULL,3,'2024-06-20 19:46:20','2024-06-20 19:46:20',NULL,NULL,NULL),(15,32.5857,0.542453,'forest',1,NULL,3,'2024-06-20 19:47:22','2024-06-20 19:47:22',NULL,NULL,NULL),(16,32.5861,0.54514,'forest',1,NULL,3,'2024-06-20 19:47:58','2024-06-20 19:47:58',NULL,NULL,NULL),(17,32.5866,0.545118,'forest',1,NULL,3,'2024-06-20 19:48:37','2024-06-20 19:48:37',NULL,NULL,NULL),(18,32.5889,0.54519,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(19,32.5889,0.545424,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(20,32.5891,0.545861,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(21,32.59,0.545409,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(22,32.5901,0.545245,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(23,32.5904,0.545663,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(24,32.5907,0.545458,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(25,32.5906,0.545196,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(26,32.5911,0.54479,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(27,32.5912,0.544532,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(28,32.5912,0.544332,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(29,32.5915,0.54422,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(30,32.5912,0.543855,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(31,32.5915,0.543857,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(32,32.592,0.543428,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(33,32.5917,0.542925,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(34,32.5912,0.542902,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(35,32.591,0.542433,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-06-21 07:48:51',NULL,NULL,NULL),(85,32.6505,0.361753,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(86,32.6515,0.361352,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(87,32.6521,0.361054,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(88,32.6521,0.36098,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(89,32.6517,0.361107,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(90,32.6516,0.361494,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(91,32.6515,0.361352,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(92,32.6511,0.360711,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(93,32.6509,0.361618,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(94,32.651,0.361575,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(95,32.6515,0.360818,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(96,32.6512,0.361183,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(97,32.6527,0.361116,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(98,32.6524,0.36114,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(99,32.6508,0.36126,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(100,32.6508,0.361496,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-06-21 08:17:06',NULL,NULL,NULL),(101,32.651,0.358072,'forest',5,NULL,3,'2024-06-21 08:22:40','2024-06-21 08:22:40',NULL,NULL,NULL),(102,32.6512,0.357922,'forest',5,NULL,3,'2024-06-21 08:22:40','2024-06-21 08:22:40',NULL,NULL,NULL),(103,32.6511,0.358134,'forest',5,NULL,3,'2024-06-21 08:22:40','2024-06-21 08:22:40',NULL,NULL,NULL),(104,32.651,0.358383,'forest',5,NULL,3,'2024-06-21 08:22:40','2024-06-21 08:22:40',NULL,NULL,NULL),(105,32.6511,0.358306,'forest',5,NULL,3,'2024-06-21 08:22:40','2024-06-21 08:22:40',NULL,NULL,NULL),(107,32.5793,0.545614,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-06-21 12:11:40',NULL,NULL,NULL),(108,32.5784,0.54517,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-06-21 12:11:40',NULL,NULL,NULL),(109,32.5782,0.545209,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-06-21 12:11:40',NULL,NULL,NULL),(110,32.5783,0.545404,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-06-21 12:11:40',NULL,NULL,NULL),(111,32.5785,0.545677,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-06-21 12:11:40',NULL,NULL,NULL),(112,32.5786,0.545716,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-06-21 12:11:40',NULL,NULL,NULL),(113,32.5788,0.545826,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-06-21 12:11:40',NULL,NULL,NULL),(114,32.5787,0.54592,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-06-21 12:11:40',NULL,NULL,NULL),(115,32.5791,0.546061,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-06-21 12:11:40',NULL,NULL,NULL),(130,30.156,0.658541,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-06-25 10:10:35',NULL,NULL,NULL),(131,30.1562,0.658456,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-06-25 10:10:35',NULL,NULL,NULL),(132,30.156,0.658593,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-06-25 10:10:35',NULL,NULL,NULL),(133,30.1558,0.658688,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-06-25 10:10:35',NULL,NULL,NULL),(134,30.1561,0.658704,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-06-25 10:10:35',NULL,NULL,NULL),(135,30.1563,0.658752,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-06-25 10:10:35',NULL,NULL,NULL),(136,30.1562,0.658716,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-06-25 10:10:35',NULL,NULL,NULL),(148,30.1806,0.69297,'farmer',NULL,'KBRL004',9,'2024-06-25 10:24:22','2024-06-25 10:24:22',NULL,NULL,NULL),(149,30.1806,0.693008,'farmer',NULL,'KBRL004',9,'2024-06-25 10:24:22','2024-06-25 10:24:22',NULL,NULL,NULL),(150,30.1804,0.692953,'farmer',NULL,'KBRL004',9,'2024-06-25 10:24:22','2024-06-25 10:24:22',NULL,NULL,NULL),(151,30.1804,0.69315,'farmer',NULL,'KBRL004',9,'2024-06-25 10:24:22','2024-06-25 10:24:22',NULL,NULL,NULL),(152,30.1806,0.69391,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-06-25 10:28:49',NULL,NULL,NULL),(153,30.1804,0.69349,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-06-25 10:28:49',NULL,NULL,NULL),(154,30.1804,0.693545,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-06-25 10:28:49',NULL,NULL,NULL),(155,30.1804,0.693627,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-06-25 10:28:49',NULL,NULL,NULL),(156,30.1803,0.693974,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-06-25 10:28:49',NULL,NULL,NULL),(157,30.1803,0.693925,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-06-25 10:28:49',NULL,NULL,NULL),(158,30.1567,0.658917,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-06-25 10:29:03',NULL,NULL,NULL),(159,30.157,0.659031,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-06-25 10:29:03',NULL,NULL,NULL),(160,30.1574,0.659111,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-06-25 10:29:03',NULL,NULL,NULL),(161,30.1574,0.659114,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-06-25 10:29:03',NULL,NULL,NULL),(162,30.1574,0.659137,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-06-25 10:29:03',NULL,NULL,NULL),(163,30.1573,0.659337,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-06-25 10:29:03',NULL,NULL,NULL),(164,30.1572,0.659258,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-06-25 10:29:03',NULL,NULL,NULL),(165,30.1572,0.659292,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-06-25 10:29:03',NULL,NULL,NULL),(166,32.9105,0.219132,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-06-25 20:08:41',NULL,NULL,NULL),(167,32.9131,0.233018,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-06-25 20:08:41',NULL,NULL,NULL),(168,32.9203,0.24262,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-06-25 20:08:41',NULL,NULL,NULL),(169,32.9262,0.2573,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-06-25 20:08:41',NULL,NULL,NULL),(170,32.9094,0.221496,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-06-25 20:08:41',NULL,NULL,NULL),(171,32.9447,0.288372,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-06-25 20:08:41',NULL,NULL,NULL),(172,32.9093,0.219703,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-06-25 20:08:41',NULL,NULL,NULL),(173,32.9149,0.23157,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-06-25 20:08:41',NULL,NULL,NULL),(174,32.9106,0.233658,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-06-25 20:09:04',NULL,NULL,NULL),(175,32.9116,0.233934,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-06-25 20:09:04',NULL,NULL,NULL),(176,32.9121,0.234962,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-06-25 20:09:04',NULL,NULL,NULL),(177,32.9129,0.237516,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-06-25 20:09:04',NULL,NULL,NULL),(178,32.9134,0.238388,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-06-25 20:09:04',NULL,NULL,NULL),(179,32.9116,0.23444,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-06-25 20:09:04',NULL,NULL,NULL);

INSERT INTO `district` VALUES (1,'Buikwe','Central','2024-06-11 09:01:59','2024-06-11 09:01:59',NULL,NULL),(2,'Mpigi','Central','2024-06-11 09:02:09','2024-06-11 09:02:09',NULL,NULL),(3,'Wakiso','Central','2024-06-11 09:02:21','2024-06-11 09:02:21',NULL,NULL),(4,'Luweero','Central','2024-06-11 09:02:33','2024-06-11 09:02:33',NULL,NULL),(5,'Masaka','Central','2024-06-11 09:02:47','2024-06-11 09:02:47',NULL,NULL),(6,'Kalangala','Central','2024-06-11 09:03:02','2024-06-11 09:03:02',NULL,NULL),(7,'Mbarara','West','2024-06-11 09:03:19','2024-06-11 09:03:19',NULL,NULL),(8,'Mbale','East','2024-06-11 09:03:29','2024-06-11 09:03:29',NULL,NULL),(9,'Kabarole ','West','2024-06-24 14:06:44','2024-06-24 14:06:44',NULL,NULL),(10,'Gulu','North','2024-06-25 08:54:53','2024-06-25 08:54:53',NULL,NULL),(11,'Lira','North','2024-06-25 08:55:03','2024-06-25 08:55:03',NULL,NULL),(12,'Jinja','East','2024-06-25 08:55:19','2024-06-25 08:55:19',NULL,NULL),(13,'Mayuge','East','2024-06-25 08:55:38','2024-06-25 08:55:38',NULL,NULL),(14,'Bukomansimbi','Central','2024-06-25 08:55:55','2024-06-25 08:55:55',NULL,NULL);
ON DUPLICATE KEY UPDATE


INSERT INTO `district` (`id`, `name`, `region`)
VALUES (1,'Abim','North'),(2,'Adjumani','North'),(3,'Agago','North'),(4,'Alebtong','North'),(5,'Amolatar','North'),(6,'Amudat','East'),(7,'Amuria','East'),(8,'Amuru','North'),(9,'Apac','North'),(10,'Arua','North'),(11,'Budaka','East'),(12,'Bududa','East'),(13,'Bugiri','East'),(14,'Bugweri','East'),(15,'Buikwe','Central'),(16,'Bukedea','East'),(17,'Bukomansimbi','Central'),(18,'Bukwo','East'),(19,'Bulambuli','East'),(20,'Buliisa','West'),(21,'Bundibugyo','West'),(22,'Bunyangabu','West'),(23,'Bushenyi','West'),(24,'Busia','East'),(25,'Butaleja','East'),(26,'Butambala','Central'),(27,'Butebo','East'),(28,'Buvuma','Central'),(29,'Buyende','East'),(30,'Dokolo','North'),(31,'Gomba','Central'),(32,'Gulu','North'),(33,'Hoima','West'),(34,'Ibanda','West'),(35,'Iganga','East'),(36,'Isingiro','West'),(37,'Jinja','East'),(38,'Kaabong','North'),(39,'Kabale','West'),(40,'Kabarole','West'),(41,'Kaberamaido','East'),(42,'Kagadi','West'),(43,'Kagwara','West'),(44,'Kalaki','East'),(45,'Kalangala','Central'),(46,'Kaliro','East'),(47,'Kalungu','Central'),(48,'Kampala','Central'),(49,'Kamuli','East'),(50,'Kamwenge','West'),(51,'Kanungu','West'),(52,'Kapchorwa','East'),(53,'Kapelebyong','East'),(54,'Kasese','West'),(55,'Katakwi','East'),(56,'Katerera','West'),(57,'Kayunga','Central'),(58,'Kibaale','West'),(59,'Kiboga','Central'),(60,'Kibuku','East'),(61,'Kiruhura','West'),(62,'Kiryandongo','West'),(63,'Kisoro','West'),(64,'Kitagwenda','West'),(65,'Kitgum','North'),(66,'Koboko','West'),(67,'Kole','North'),(68,'Kotido','North'),(69,'Kumi','East'),(70,'Kwania','East'),(71,'Kween','East'),(72,'Kyankwanzi','Central'),(73,'Kyegegwa','West'),(74,'Kyenjojo','West'),(75,'Kyotera','Central'),(76,'Lamwo','North'),(77,'Lira','North'),(78,'Luuka','East'),(79,'Luwero','Central'),(80,'Lwengo','Central'),(81,'Lyantonde','Central'),(82,'Manafwa','East'),(83,'Maracha','West'),(84,'Masaka','Central'),(85,'Masindi','West'),(86,'Mayuge','East'),(87,'Mbale','East'),(88,'Mbarara','West'),(89,'Mitooma','West'),(90,'Mityana','Central'),(91,'Moroto','North'),(92,'Moyo','North'),(93,'Mpigi','Central'),(94,'Mubende','Central'),(95,'Mukono','Central'),(96,'Nakapiripirit','North'),(97,'Nakaseke','Central'),(98,'Nakasongola','Central'),(99,'Namayingo','East'),(100,'Namisindwa','East'),(101,'Namutumba','East'),(102,'Napak','North'),(103,'Nebbi','West'),(104,'Ngora','East'),(105,'Ntoroko','West'),(106,'Ntungamo','West'),(107,'Nwoya','North'),(108,'Otuke','North'),(109,'Oyam','North'),(110,'Pader','North'),(111,'Pallisa','East'),(112,'Rakai','Central'),(113,'Rubanda','West'),(114,'Rubirizi','West'),(115,'Rukiga','West'),(116,'Rukungiri','West'),(117,'Sembabule','Central'),(118,'Serere','East'),(119,'Sheema','West'),(120,'Sironko','East'),(121,'Soroti','East'),(122,'Tororo','East'),(123,'Wakiso','Central'),(124,'Yumbe','West'),(125,'Zombo','West') 
AS new_district
ON DUPLICATE KEY UPDATE 
`name` = new_district.name,
`region` = new_district.region;

0 row(s) affected, 6 warning(s): 1287
 'VALUES function' 
 is deprecated and will be removed in a future release. Please use an alias 
 (INSERT INTO ... VALUES (...) AS alias) and replace VALUES(col)
  in the ON DUPLICATE KEY UPDATE clause with alias.col instead 1287 'VALUES function' 
  is deprecated and will be removed in a future release. Please use an alias 
  (INSERT INTO ... VALUES (...) AS alias) and replace VALUES(col) in the ON DUPLICATE KEY UPDATE
   clause with alias.col instead 1287 'VALUES function' is deprecated and will be removed in 
   a future release. Please use an alias (INSERT INTO ... VALUES (...) AS alias) and replace VALUES(col) 
   in the ON DUPLICATE KEY UPDATE clause with alias.col instead 1287 'VALUES function' is deprecated and will be removed in a future release. Please use an alias (INSERT INTO ... VALUES (...) AS alias) and replace VALUES(col) in the ON DUPLICATE KEY UPDATE clause with alias.col instead 1287 'VALUES function' is deprecated and will be removed in a future release. Please use an alias (INSERT INTO ... VALUES (...) AS alias) and replace VALUES(col) in the ON DUPLICATE KEY UPDATE clause with alias.col instead 1287 'VALUES function' is deprecated and will be removed in a future release. Please use an alias (INSERT INTO ... VALUES (...) AS alias) and replace VALUES(col) in the ON DUPLICATE KEY UPDATE clause with alias.col instead Records: 14  Duplicates: 0  Warnings: 6


UPDATE `qrcode`.`user` SET `id_start` = 'SASA2' WHERE (`id` = '4');
