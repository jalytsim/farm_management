/*!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.8-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: qrcode
-- ------------------------------------------------------
-- Server version	10.11.8-MariaDB-0ubuntu0.23.10.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Solar`
--

DROP TABLE IF EXISTS `Solar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Solar` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `latitude` varchar(20) NOT NULL,
  `longitude` varchar(20) NOT NULL,
  `timestamp` datetime NOT NULL,
  `uv_index` float DEFAULT NULL,
  `downward_short_wave_radiation_flux` float DEFAULT NULL,
  `source` varchar(100) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `date_created` datetime DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Solar`
--

LOCK TABLES `Solar` WRITE;
/*!40000 ALTER TABLE `Solar` DISABLE KEYS */;
/*!40000 ALTER TABLE `Solar` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Weather`
--

DROP TABLE IF EXISTS `Weather`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Weather` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `latitude` varchar(20) NOT NULL,
  `longitude` varchar(20) NOT NULL,
  `timestamp` datetime NOT NULL,
  `air_temperature` float DEFAULT NULL,
  `air_temperature_80m` float DEFAULT NULL,
  `air_temperature_100m` float DEFAULT NULL,
  `air_temperature_1000hpa` float DEFAULT NULL,
  `air_temperature_800hpa` float DEFAULT NULL,
  `air_temperature_500hpa` float DEFAULT NULL,
  `air_temperature_200hpa` float DEFAULT NULL,
  `pressure` float DEFAULT NULL,
  `cloud_cover` float DEFAULT NULL,
  `current_direction` float DEFAULT NULL,
  `current_speed` float DEFAULT NULL,
  `gust` float DEFAULT NULL,
  `humidity` float DEFAULT NULL,
  `ice_cover` float DEFAULT NULL,
  `precipitation` float DEFAULT NULL,
  `snow_depth` float DEFAULT NULL,
  `sea_level` float DEFAULT NULL,
  `swell_direction` float DEFAULT NULL,
  `swell_height` float DEFAULT NULL,
  `swell_period` float DEFAULT NULL,
  `secondary_swell_direction` float DEFAULT NULL,
  `secondary_swell_height` float DEFAULT NULL,
  `secondary_swell_period` float DEFAULT NULL,
  `visibility` float DEFAULT NULL,
  `water_temperature` float DEFAULT NULL,
  `wave_direction` float DEFAULT NULL,
  `wave_height` float DEFAULT NULL,
  `wave_period` float DEFAULT NULL,
  `wind_wave_direction` float DEFAULT NULL,
  `wind_wave_height` float DEFAULT NULL,
  `wind_wave_period` float DEFAULT NULL,
  `wind_direction` float DEFAULT NULL,
  `wind_direction_20m` float DEFAULT NULL,
  `wind_direction_30m` float DEFAULT NULL,
  `wind_direction_40m` float DEFAULT NULL,
  `wind_direction_50m` float DEFAULT NULL,
  `wind_direction_80m` float DEFAULT NULL,
  `wind_direction_100m` float DEFAULT NULL,
  `wind_direction_1000hpa` float DEFAULT NULL,
  `wind_direction_800hpa` float DEFAULT NULL,
  `wind_direction_500hpa` float DEFAULT NULL,
  `wind_direction_200hpa` float DEFAULT NULL,
  `wind_speed` float DEFAULT NULL,
  `wind_speed_20m` float DEFAULT NULL,
  `wind_speed_30m` float DEFAULT NULL,
  `wind_speed_40m` float DEFAULT NULL,
  `wind_speed_50m` float DEFAULT NULL,
  `wind_speed_80m` float DEFAULT NULL,
  `wind_speed_100m` float DEFAULT NULL,
  `wind_speed_1000hpa` float DEFAULT NULL,
  `wind_speed_800hpa` float DEFAULT NULL,
  `wind_speed_500hpa` float DEFAULT NULL,
  `wind_speed_200hpa` float DEFAULT NULL,
  `date_created` datetime DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Weather`
--

LOCK TABLES `Weather` WRITE;
/*!40000 ALTER TABLE `Weather` DISABLE KEYS */;
/*!40000 ALTER TABLE `Weather` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `crop`
--

DROP TABLE IF EXISTS `crop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `crop` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `weight` float NOT NULL,
  `category_id` int(11) NOT NULL,
  `date_created` datetime DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `modified_by` int(11) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `fk_crop_modified_by` (`modified_by`),
  KEY `fk_crop_created_by` (`created_by`),
  CONSTRAINT `crop_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `producecategory` (`id`),
  CONSTRAINT `fk_category_id` FOREIGN KEY (`category_id`) REFERENCES `producecategory` (`id`),
  CONSTRAINT `fk_crop_created_by` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_crop_modified_by` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `crop`
--

LOCK TABLES `crop` WRITE;
/*!40000 ALTER TABLE `crop` DISABLE KEYS */;
INSERT INTO `crop` VALUES
(1,'Cocoa',1,1,'2024-06-11 09:17:49','2024-06-11 09:17:49',NULL,NULL),
(2,'Coffee Robusta',1,2,'2024-06-11 09:18:10','2024-06-11 09:18:10',NULL,NULL),
(3,'Coffee Arabica',1,3,'2024-06-11 09:18:29','2024-06-11 09:18:29',NULL,NULL),
(4,'Oil Palm',2,4,'2024-06-11 09:18:43','2024-06-11 09:18:43',NULL,NULL),
(5,'Soya Bean',1,5,'2024-06-11 09:19:00','2024-06-11 09:19:00',NULL,NULL),
(6,'Rubber',3,6,'2024-06-11 09:19:23','2024-06-11 09:19:23',NULL,NULL),
(7,'Hass Avocado',1,4,'2024-06-21 11:51:47','2024-06-21 11:51:47',NULL,NULL);
/*!40000 ALTER TABLE `crop` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `district`
--

DROP TABLE IF EXISTS `district`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `district` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `region` varchar(255) NOT NULL,
  `date_created` datetime DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `modified_by` int(11) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_district_modified_by` (`modified_by`),
  KEY `fk_district_created_by` (`created_by`),
  CONSTRAINT `fk_district_created_by` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_district_modified_by` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `district`
--

LOCK TABLES `district` WRITE;
/*!40000 ALTER TABLE `district` DISABLE KEYS */;
INSERT INTO `district` VALUES
(1,'Buikwe','Central','2024-06-11 09:01:59','2024-06-11 09:01:59',NULL,NULL),
(2,'Mpigi','Central','2024-06-11 09:02:09','2024-06-11 09:02:09',NULL,NULL),
(3,'Wakiso','Central','2024-06-11 09:02:21','2024-06-11 09:02:21',NULL,NULL),
(4,'Luweero','Central','2024-06-11 09:02:33','2024-06-11 09:02:33',NULL,NULL),
(5,'Masaka','Central','2024-06-11 09:02:47','2024-06-11 09:02:47',NULL,NULL),
(6,'Kalangala','Central','2024-06-11 09:03:02','2024-06-11 09:03:02',NULL,NULL),
(7,'Mbarara','West','2024-06-11 09:03:19','2024-06-11 09:03:19',NULL,NULL),
(8,'Mbale','East','2024-06-11 09:03:29','2024-06-11 09:03:29',NULL,NULL),
(9,'Kabarole ','West','2024-06-24 14:06:44','2024-06-24 14:06:44',NULL,NULL),
(10,'Gulu','North','2024-06-25 08:54:53','2024-06-25 08:54:53',NULL,NULL),
(11,'Lira','North','2024-06-25 08:55:03','2024-06-25 08:55:03',NULL,NULL),
(12,'Jinja','East','2024-06-25 08:55:19','2024-06-25 08:55:19',NULL,NULL),
(13,'Mayuge','East','2024-06-25 08:55:38','2024-06-25 08:55:38',NULL,NULL),
(14,'Bukomansimbi','Central','2024-06-25 08:55:55','2024-06-25 08:55:55',NULL,NULL),
(15,'Bugiri','East','2024-07-18 12:03:03','2024-07-18 12:03:03',NULL,NULL),
(16,'Masindi','West','2024-07-18 12:03:33','2024-07-18 12:03:33',NULL,NULL),
(17,'Bundibugyo','West','2024-07-19 17:18:06','2024-07-19 17:18:06',NULL,NULL);
/*!40000 ALTER TABLE `district` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `farm`
--

DROP TABLE IF EXISTS `farm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `farm` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `farm_id` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `subcounty` varchar(255) NOT NULL,
  `farmergroup_id` int(11) NOT NULL,
  `district_id` int(11) NOT NULL,
  `geolocation` varchar(255) NOT NULL,
  `date_created` datetime DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `phonenumber` varchar(20) DEFAULT NULL,
  `phonenumber2` varchar(20) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `farm`
--

LOCK TABLES `farm` WRITE;
/*!40000 ALTER TABLE `farm` DISABLE KEYS */;
INSERT INTO `farm` VALUES
(1,'B0001','Isiah Namanya','1',1,1,'0.38551,33.3421','2024-06-11 09:08:19','2024-07-14 01:26:50',NULL,NULL,3,NULL),
(3,'WAK0002','Lwetutte Brian','Busukuma',3,3,'0.545614,32.579339','2024-06-21 11:50:52','2024-07-14 01:26:50','256783130358','256756411682',3,NULL),
(5,'KBRL001','Jackus Munihera','Karangura',4,9,'0.658541,30.156032','2024-06-24 14:22:52','2024-07-14 01:26:50','25674123456','25675123456',3,NULL),
(6,'KBRL004','John Mugisha','Karangura',4,9,'0.69297,30.180577','2024-06-25 10:18:54','2024-07-14 01:26:50','','',3,NULL),
(7,'KBRL003','Daniel Maate','Karangura',4,9,'0.69391,30.180621','2024-06-25 10:26:38','2024-07-14 01:26:50','','',3,NULL),
(8,'KBRL002','Musoki Faibe','Karangura',4,9,'0.658917,30.156655','2024-06-25 10:28:22','2024-07-14 01:26:50','','',3,NULL),
(9,'BUIK002','Bwebale Badru','Ngoogwe',1,1,'0.257593,32.923496','2024-06-25 19:52:04','2024-07-14 01:26:50','','',3,NULL),
(10,'BUIK003','Mafuko Muzamiru','Ngoogwe',1,1,'0.234431,32.910984','2024-06-25 20:01:21','2024-07-14 01:26:50','256755976395','',3,NULL),
(13,'BUNDI02','Biira Jolly','',4,17,'0.700031,30.065901','2024-07-27 13:33:30','2024-07-29 19:47:47','','256772954040',9,9),
(14,'BUNDI01','Biira Safina','Bundibugyo T.C',4,17,'0.711227,30.068870','2024-07-29 19:19:51','2024-07-29 19:19:51','256787227508','',9,9),
(15,'BUNDI03','Mahanda David','Bundibugyo T.C',4,17,'0.699054,30.066693','2024-07-29 19:31:07','2024-07-29 19:31:07','256785184424','',9,9),
(16,'BUNDI04','Masereka Ibrahim','Bundibugyo T.C',4,17,'0.698725,30.066361','2024-07-29 19:40:17','2024-07-29 19:40:17','256789238888','',9,9),
(17,'WAK0003','Nomena TSIMIJALY','Test ',3,7,'1341548,131310.','2024-08-19 15:06:23','2024-08-19 15:06:23','0344776318','',2,2);
/*!40000 ALTER TABLE `farm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `farmdata`
--

DROP TABLE IF EXISTS `farmdata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `farmdata` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `farm_id` varchar(50) NOT NULL,
  `crop_id` int(11) NOT NULL,
  `land_type` varchar(255) NOT NULL,
  `tilled_land_size` float NOT NULL,
  `planting_date` date NOT NULL,
  `season` int(11) NOT NULL,
  `quality` varchar(255) NOT NULL,
  `quantity` int(11) NOT NULL,
  `harvest_date` date NOT NULL,
  `expected_yield` float NOT NULL,
  `actual_yield` float NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT current_timestamp(),
  `channel_partner` varchar(255) NOT NULL,
  `destination_country` varchar(255) NOT NULL,
  `customer_name` varchar(255) NOT NULL,
  `date_created` datetime DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_by` int(11) DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `farmdata`
--

LOCK TABLES `farmdata` WRITE;
/*!40000 ALTER TABLE `farmdata` DISABLE KEYS */;
INSERT INTO `farmdata` VALUES
(1,'B0001',1,'Titled',2,'2024-06-11',1,'1',2000,'2024-06-29',2000,1800,'2024-10-29 12:21:00','Sasakawa','Italy','AgroPlus','2024-06-11 09:23:06','2024-07-14 07:08:12',3,NULL),
(2,'WAK0002',7,'Titled',2,'2024-02-01',2,'1',2,'2024-08-29',3,2,'2024-08-30 20:03:00','Sasakawa','Italy','AgroPlus','2024-06-21 12:03:51','2024-07-14 07:08:13',3,NULL);
/*!40000 ALTER TABLE `farmdata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `farmergroup`
--

DROP TABLE IF EXISTS `farmergroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `farmergroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `date_created` datetime DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `modified_by` int(11) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_farmergroup_modified_by` (`modified_by`),
  KEY `fk_farmergroup_created_by` (`created_by`),
  CONSTRAINT `fk_farmergroup_created_by` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_farmergroup_modified_by` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `farmergroup`
--

LOCK TABLES `farmergroup` WRITE;
/*!40000 ALTER TABLE `farmergroup` DISABLE KEYS */;
INSERT INTO `farmergroup` VALUES
(1,'Buikwe Cocoa','Sasakawa Cocoa Farmers','2024-06-11 09:00:27','2024-06-11 09:00:27',NULL,NULL),
(2,'Mpigi Cocoa Farmers','Mpigi Cocoa Farmers','2024-06-11 09:01:11','2024-06-11 09:01:11',NULL,NULL),
(3,'HFZ Kabumba','Hungerfree Coop','2024-06-11 10:22:44','2024-06-11 10:22:44',NULL,NULL),
(4,'AbanyaRwenzori Coop','Rwenzori Subregion-Arabica Coffee','2024-06-24 14:06:03','2024-06-24 14:06:03',NULL,NULL),
(5,'Kasudde Farmers Coop','Cocoa farmers-Masulita','2024-07-18 12:02:07','2024-07-18 12:02:07',NULL,NULL);
/*!40000 ALTER TABLE `farmergroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forest`
--

DROP TABLE IF EXISTS `forest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `forest` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `tree_type` varchar(255) NOT NULL,
  `date_created` datetime DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_by` int(11) DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_forest_created_by` (`created_by`),
  KEY `fk_forest_modified_by` (`modified_by`),
  CONSTRAINT `fk_forest_created_by` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_forest_modified_by` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forest`
--

LOCK TABLES `forest` WRITE;
/*!40000 ALTER TABLE `forest` DISABLE KEYS */;
INSERT INTO `forest` VALUES
(1,'Mulimbwa-Namawaata','','2024-06-11 09:32:39','2024-07-31 16:07:36',8,8),
(2,'Mulimbwa-Adjacent','','2024-06-21 07:25:55','2024-07-14 01:25:33',8,NULL),
(4,'Bweyogerere-Eucalyptus-Bypass','','2024-06-21 08:09:27','2024-07-14 01:25:33',8,NULL),
(5,'Eucalyptus- SmallNBypass','','2024-06-21 08:22:21','2024-07-14 01:25:33',8,NULL);
/*!40000 ALTER TABLE `forest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `point`
--

DROP TABLE IF EXISTS `point`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `point` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `longitude` float NOT NULL,
  `latitude` float NOT NULL,
  `owner_type` enum('forest','farmer') NOT NULL,
  `forest_id` int(11) DEFAULT NULL,
  `farmer_id` varchar(50) DEFAULT NULL,
  `district_id` int(11) NOT NULL,
  `date_created` datetime DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_by` int(11) DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  `tree_id` int(11) DEFAULT NULL,
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
  CONSTRAINT `CONSTRAINT_1` CHECK (`owner_type` = _utf8mb4'forest' and `forest_id` is not null and `farmer_id` is null or `owner_type` = _utf8mb4'farmer' and `farmer_id` is not null and `forest_id` is null)
) ENGINE=InnoDB AUTO_INCREMENT=215 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `point`
--

LOCK TABLES `point` WRITE;
/*!40000 ALTER TABLE `point` DISABLE KEYS */;
INSERT INTO `point` VALUES
(2,32.5866,0.545164,'forest',1,NULL,3,'2024-06-20 19:30:27','2024-07-14 01:16:23',8,NULL,NULL),
(3,32.5883,0.544809,'forest',1,NULL,3,'2024-06-20 19:32:45','2024-07-14 01:16:23',8,NULL,NULL),
(4,32.5902,0.5437,'forest',1,NULL,3,'2024-06-20 19:33:31','2024-07-14 01:16:23',8,NULL,NULL),
(5,32.5906,0.542582,'forest',1,NULL,3,'2024-06-20 19:34:23','2024-07-14 01:16:23',8,NULL,NULL),
(6,32.5903,0.542391,'forest',1,NULL,3,'2024-06-20 19:36:24','2024-07-14 01:16:23',8,NULL,NULL),
(7,32.5901,0.542102,'forest',1,NULL,3,'2024-06-20 19:37:18','2024-07-14 01:16:23',8,NULL,NULL),
(8,32.5891,0.541376,'forest',1,NULL,3,'2024-06-20 19:38:04','2024-07-14 01:16:23',8,NULL,NULL),
(9,32.5881,0.540543,'forest',1,NULL,3,'2024-06-20 19:38:54','2024-07-14 01:16:23',8,NULL,NULL),
(11,32.5867,0.540862,'forest',1,NULL,3,'2024-06-20 19:44:06','2024-07-14 01:16:23',8,NULL,NULL),
(12,32.5864,0.541312,'forest',1,NULL,3,'2024-06-20 19:44:48','2024-07-14 01:16:23',8,NULL,NULL),
(13,32.5869,0.542019,'forest',1,NULL,3,'2024-06-20 19:45:24','2024-07-14 01:16:23',8,NULL,NULL),
(14,32.5863,0.541702,'forest',1,NULL,3,'2024-06-20 19:46:20','2024-07-14 01:16:23',8,NULL,NULL),
(15,32.5857,0.542453,'forest',1,NULL,3,'2024-06-20 19:47:22','2024-07-14 01:16:23',8,NULL,NULL),
(16,32.5861,0.54514,'forest',1,NULL,3,'2024-06-20 19:47:58','2024-07-14 01:16:23',8,NULL,NULL),
(17,32.5866,0.545118,'forest',1,NULL,3,'2024-06-20 19:48:37','2024-07-14 01:16:23',8,NULL,NULL),
(18,32.5889,0.54519,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(19,32.5889,0.545424,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(20,32.5891,0.545861,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(21,32.59,0.545409,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(22,32.5901,0.545245,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(23,32.5904,0.545663,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(24,32.5907,0.545458,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(25,32.5906,0.545196,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(26,32.5911,0.54479,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(27,32.5912,0.544532,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(28,32.5912,0.544332,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(29,32.5915,0.54422,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(30,32.5912,0.543855,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(31,32.5915,0.543857,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(32,32.592,0.543428,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(33,32.5917,0.542925,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(34,32.5912,0.542902,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(35,32.591,0.542433,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),
(85,32.6505,0.361753,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),
(86,32.6515,0.361352,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),
(87,32.6521,0.361054,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),
(88,32.6521,0.36098,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),
(89,32.6517,0.361107,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),
(90,32.6516,0.361494,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),
(91,32.6515,0.361352,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),
(92,32.6511,0.360711,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),
(93,32.6509,0.361618,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),
(94,32.651,0.361575,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),
(95,32.6515,0.360818,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:17:50',8,NULL,NULL),
(96,32.6512,0.361183,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:17:50',8,NULL,NULL),
(97,32.6527,0.361116,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:17:50',8,NULL,NULL),
(98,32.6524,0.36114,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:17:50',8,NULL,NULL),
(99,32.6508,0.36126,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:17:50',8,NULL,NULL),
(100,32.6508,0.361496,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:17:50',8,NULL,NULL),
(101,32.651,0.358072,'forest',5,NULL,3,'2024-06-21 08:22:40','2024-07-14 01:17:50',8,NULL,NULL),
(102,32.6512,0.357922,'forest',5,NULL,3,'2024-06-21 08:22:40','2024-07-14 01:17:50',8,NULL,NULL),
(103,32.6511,0.358134,'forest',5,NULL,3,'2024-06-21 08:22:40','2024-07-14 01:17:50',8,NULL,NULL),
(104,32.651,0.358383,'forest',5,NULL,3,'2024-06-21 08:22:40','2024-07-14 01:17:50',8,NULL,NULL),
(105,32.6511,0.358306,'forest',5,NULL,3,'2024-06-21 08:22:40','2024-07-14 01:17:50',8,NULL,NULL),
(107,32.5793,0.545614,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),
(108,32.5784,0.54517,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),
(109,32.5782,0.545209,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),
(110,32.5783,0.545404,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),
(111,32.5785,0.545677,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),
(112,32.5786,0.545716,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),
(113,32.5788,0.545826,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),
(114,32.5787,0.54592,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),
(115,32.5791,0.546061,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),
(130,30.156,0.658541,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-07-14 01:19:27',3,NULL,NULL),
(131,30.1562,0.658456,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-07-14 01:19:27',3,NULL,NULL),
(132,30.156,0.658593,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-07-14 01:19:27',3,NULL,NULL),
(133,30.1558,0.658688,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-07-14 01:19:27',3,NULL,NULL),
(134,30.1561,0.658704,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-07-14 01:19:27',3,NULL,NULL),
(135,30.1563,0.658752,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-07-14 01:19:27',3,NULL,NULL),
(136,30.1562,0.658716,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-07-14 01:19:27',3,NULL,NULL),
(148,30.1806,0.69297,'farmer',NULL,'KBRL004',9,'2024-06-25 10:24:22','2024-07-14 01:19:27',3,NULL,NULL),
(149,30.1806,0.693008,'farmer',NULL,'KBRL004',9,'2024-06-25 10:24:22','2024-07-14 01:19:27',3,NULL,NULL),
(150,30.1804,0.692953,'farmer',NULL,'KBRL004',9,'2024-06-25 10:24:22','2024-07-14 01:19:27',3,NULL,NULL),
(151,30.1804,0.69315,'farmer',NULL,'KBRL004',9,'2024-06-25 10:24:22','2024-07-14 01:19:27',3,NULL,NULL),
(152,30.1806,0.69391,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-07-14 01:19:27',3,NULL,NULL),
(153,30.1804,0.69349,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-07-14 01:19:27',3,NULL,NULL),
(154,30.1804,0.693545,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-07-14 01:19:27',3,NULL,NULL),
(155,30.1804,0.693627,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-07-14 01:19:27',3,NULL,NULL),
(156,30.1803,0.693974,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-07-14 01:19:27',3,NULL,NULL),
(157,30.1803,0.693925,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-07-14 01:19:27',3,NULL,NULL),
(158,30.1567,0.658917,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),
(159,30.157,0.659031,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),
(160,30.1574,0.659111,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),
(161,30.1574,0.659114,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),
(162,30.1574,0.659137,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),
(163,30.1573,0.659337,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),
(164,30.1572,0.659258,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),
(165,30.1572,0.659292,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),
(166,32.9105,0.219132,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),
(167,32.9131,0.233018,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),
(168,32.9203,0.24262,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),
(169,32.9262,0.2573,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),
(170,32.9094,0.221496,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),
(171,32.9447,0.288372,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),
(172,32.9093,0.219703,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),
(173,32.9149,0.23157,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),
(174,32.9106,0.233658,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-07-14 01:19:27',3,NULL,NULL),
(175,32.9116,0.233934,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-07-14 01:19:27',3,NULL,NULL),
(176,32.9121,0.234962,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-07-14 01:19:27',3,NULL,NULL),
(177,32.9129,0.237516,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-07-14 01:19:27',3,NULL,NULL),
(178,32.9134,0.238388,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-07-14 01:19:27',3,NULL,NULL),
(179,32.9116,0.23444,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-07-14 01:19:27',3,NULL,NULL),
(182,30.0659,0.700031,'farmer',NULL,'BUNDI02',17,'2024-07-29 18:53:09','2024-07-29 18:53:09',9,9,NULL),
(189,30.0666,0.699696,'farmer',NULL,'BUNDI02',17,'2024-07-29 19:08:13','2024-07-29 19:08:13',9,9,NULL),
(190,30.0669,0.699661,'farmer',NULL,'BUNDI02',17,'2024-07-29 19:08:44','2024-07-29 19:08:44',9,9,NULL),
(191,30.067,0.699572,'farmer',NULL,'BUNDI02',17,'2024-07-29 19:09:25','2024-07-29 19:09:25',9,9,NULL),
(192,30.0673,0.699575,'farmer',NULL,'BUNDI02',17,'2024-07-29 19:09:57','2024-07-29 19:09:57',9,9,NULL),
(193,30.0669,0.699178,'farmer',NULL,'BUNDI02',17,'2024-07-29 19:10:27','2024-07-29 19:10:27',9,9,NULL),
(194,30.0689,0.711227,'farmer',NULL,'BUNDI01',17,'2024-07-29 19:25:01','2024-07-29 19:25:01',9,9,NULL),
(195,30.0689,0.711227,'farmer',NULL,'BUNDI01',17,'2024-07-29 19:25:19','2024-07-29 19:25:19',NULL,NULL,NULL),
(196,30.0658,0.700271,'farmer',NULL,'BUNDI01',17,'2024-07-29 19:25:19','2024-07-29 19:25:19',NULL,NULL,NULL),
(197,30.0656,0.700325,'farmer',NULL,'BUNDI01',17,'2024-07-29 19:25:19','2024-07-29 19:25:19',NULL,NULL,NULL),
(198,30.0658,0.699831,'farmer',NULL,'BUNDI01',17,'2024-07-29 19:25:19','2024-07-29 19:25:19',NULL,NULL,NULL),
(199,30.0659,0.700003,'farmer',NULL,'BUNDI01',17,'2024-07-29 19:25:19','2024-07-29 19:25:19',NULL,NULL,NULL),
(200,30.0675,0.709981,'farmer',NULL,'BUNDI01',17,'2024-07-29 19:25:19','2024-07-29 19:25:19',NULL,NULL,NULL),
(201,30.0667,0.699054,'farmer',NULL,'BUNDI03',17,'2024-07-29 19:32:05','2024-07-29 19:32:05',9,9,NULL),
(202,30.0667,0.699054,'farmer',NULL,'BUNDI03',17,'2024-07-29 19:38:17','2024-07-29 19:38:17',NULL,NULL,NULL),
(203,30.0662,0.699098,'farmer',NULL,'BUNDI03',17,'2024-07-29 19:38:17','2024-07-29 19:38:17',NULL,NULL,NULL),
(204,30.0666,0.699111,'farmer',NULL,'BUNDI03',17,'2024-07-29 19:38:17','2024-07-29 19:38:17',NULL,NULL,NULL),
(205,30.0663,0.698876,'farmer',NULL,'BUNDI03',17,'2024-07-29 19:38:17','2024-07-29 19:38:17',NULL,NULL,NULL),
(206,30.0662,0.698528,'farmer',NULL,'BUNDI03',17,'2024-07-29 19:38:17','2024-07-29 19:38:17',NULL,NULL,NULL),
(207,30.0667,0.698645,'farmer',NULL,'BUNDI03',17,'2024-07-29 19:38:17','2024-07-29 19:38:17',NULL,NULL,NULL),
(208,30.0664,0.698725,'farmer',NULL,'BUNDI04',17,'2024-07-29 19:46:33','2024-07-29 19:46:33',9,9,NULL),
(209,30.0664,0.698725,'farmer',NULL,'BUNDI04',17,'2024-07-29 19:46:47','2024-07-29 19:46:47',NULL,NULL,NULL),
(210,30.0674,0.6987,'farmer',NULL,'BUNDI04',17,'2024-07-29 19:46:47','2024-07-29 19:46:47',NULL,NULL,NULL),
(211,30.0654,0.698851,'farmer',NULL,'BUNDI04',17,'2024-07-29 19:46:47','2024-07-29 19:46:47',NULL,NULL,NULL),
(212,30.0653,0.698262,'farmer',NULL,'BUNDI04',17,'2024-07-29 19:46:47','2024-07-29 19:46:47',NULL,NULL,NULL),
(213,30.0652,0.698278,'farmer',NULL,'BUNDI04',17,'2024-07-29 19:46:47','2024-07-29 19:46:47',NULL,NULL,NULL),
(214,30.0618,0.678898,'farmer',NULL,'BUNDI04',17,'2024-07-29 19:46:47','2024-07-29 19:46:47',NULL,NULL,NULL);
/*!40000 ALTER TABLE `point` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producecategory`
--

DROP TABLE IF EXISTS `producecategory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `producecategory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `grade` int(11) NOT NULL,
  `date_created` datetime DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `modified_by` int(11) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_modified_by` (`modified_by`),
  KEY `fk_created_by` (`created_by`),
  CONSTRAINT `fk_created_by` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_modified_by` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producecategory`
--

LOCK TABLES `producecategory` WRITE;
/*!40000 ALTER TABLE `producecategory` DISABLE KEYS */;
INSERT INTO `producecategory` VALUES
(1,'Cocoa',1,'2024-06-11 09:14:53','2024-06-11 09:14:53',NULL,NULL),
(2,'Coffee Robusta',1,'2024-06-11 09:15:10','2024-06-11 09:15:10',NULL,NULL),
(3,'Coffee Arabica',1,'2024-06-11 09:15:21','2024-06-11 09:15:21',NULL,NULL),
(4,'Palm Oil',2,'2024-06-11 09:15:38','2024-06-11 09:15:38',NULL,NULL),
(5,'Soya Bean',3,'2024-06-11 09:15:50','2024-06-11 09:15:50',NULL,NULL),
(6,'Rubber',1,'2024-06-11 09:16:24','2024-06-11 09:16:24',NULL,NULL);
/*!40000 ALTER TABLE `producecategory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `soildata`
--

DROP TABLE IF EXISTS `soildata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `soildata` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `district_id` int(11) NOT NULL,
  `internal_id` int(11) NOT NULL,
  `device` varchar(255) NOT NULL,
  `owner` varchar(255) NOT NULL,
  `nitrogen` float NOT NULL,
  `phosphorus` float NOT NULL,
  `potassium` float NOT NULL,
  `ph` float NOT NULL,
  `temperature` float NOT NULL,
  `humidity` float NOT NULL,
  `conductivity` float NOT NULL,
  `signal_level` float NOT NULL,
  `date` date NOT NULL,
  `date_created` datetime DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_by` int(11) DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `district_id` (`district_id`),
  KEY `fk_soildata_created_by` (`created_by`),
  KEY `fk_soildata_modified_by` (`modified_by`),
  CONSTRAINT `fk_soildata_created_by` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_soildata_district_id` FOREIGN KEY (`district_id`) REFERENCES `district` (`id`),
  CONSTRAINT `fk_soildata_modified_by` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`),
  CONSTRAINT `soildata_ibfk_1` FOREIGN KEY (`district_id`) REFERENCES `district` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `soildata`
--

LOCK TABLES `soildata` WRITE;
/*!40000 ALTER TABLE `soildata` DISABLE KEYS */;
/*!40000 ALTER TABLE `soildata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tree`
--

DROP TABLE IF EXISTS `tree`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tree` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `forest_id` int(11) NOT NULL,
  `point_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `height` float NOT NULL,
  `diameter` float NOT NULL,
  `date_planted` date NOT NULL,
  `date_cut` date DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  `date_created` datetime DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `forest_id` (`forest_id`),
  KEY `point_id` (`point_id`),
  KEY `created_by` (`created_by`),
  KEY `modified_by` (`modified_by`),
  CONSTRAINT `tree_ibfk_1` FOREIGN KEY (`forest_id`) REFERENCES `forest` (`id`),
  CONSTRAINT `tree_ibfk_2` FOREIGN KEY (`point_id`) REFERENCES `point` (`id`),
  CONSTRAINT `tree_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`),
  CONSTRAINT `tree_ibfk_4` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tree`
--

LOCK TABLES `tree` WRITE;
/*!40000 ALTER TABLE `tree` DISABLE KEYS */;
/*!40000 ALTER TABLE `tree` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(150) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(150) NOT NULL,
  `phonenumber` varchar(20) DEFAULT NULL,
  `user_type` varchar(50) NOT NULL,
  `is_admin` tinyint(1) DEFAULT 0,
  `date_created` datetime DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `id_start` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES
(2,'Admin','admin@admin.admin','pbkdf2:sha256:600000$us9tk0a4zUPQBs8f$06f2ace9bba750792ab34515795ebc53a5fce96d450c9fac0f23ab90e14effb5','0303030303','admin',1,'2024-06-11 08:03:32','2024-06-11 08:03:32',NULL),
(3,'sasakawa1','sasakawa1@agriyields.com','pbkdf2:sha256:600000$zQFb0iorZfRBdryr$cfc389cd12727383093280f9a2ba14f23f210427e17d076b5fe563a53bd04e4d','25678123456','farmer',0,'2024-06-11 09:04:36','2024-06-11 09:04:36',NULL),
(6,'brian','lwetutb@agriyields.com','pbkdf2:sha256:600000$cTRyZKoIYutjZTJ2$362c2fd768417acee8518367b294f72c92580b286a0827040293777b7ac9887c','256783130358','admin',1,'2024-06-11 09:29:11','2024-06-11 09:29:11',NULL),
(8,'theo@agriyields.com','theo@agriyields.com','pbkdf2:sha256:600000$mLUrCNtvYpofxGIh$e8937ad25e22bb2fd724e1829c2d48d2c6ffd5c42ab16526e730c3386eb40edc','256703123456','forest',0,'2024-06-11 19:43:18','2024-06-11 19:43:18',NULL),
(9,'bahati','bahati@agriyields.com','pbkdf2:sha256:600000$PGbJErsb3epKf0rN$208bbb5893bb089a3e0adfeb62fea4442b6085bdbde8932bbc7c2589e24f7339','256772621397','farmer',0,'2024-06-24 13:34:21','2024-06-24 13:34:21',NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-31  2:00:01
