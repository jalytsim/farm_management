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
  `owner_type` enum('forest','farmer','tree') NOT NULL,
  `owner_id` varchar(50) DEFAULT NULL,
  `district_id` int(11) DEFAULT NULL,
  `date_created` datetime DEFAULT current_timestamp(),
  `date_updated` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `modified_by` int(11) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_point_longitude_latitude` (`longitude`,`latitude`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `point`
--

LOCK TABLES `point` WRITE;
/*!40000 ALTER TABLE `point` DISABLE KEYS */;
INSERT INTO `point` VALUES
(1,32.3239,0.81476,'farmer','WAK0002',NULL,'2024-09-02 05:20:03','2024-09-02 05:20:03',2,2),
(2,32.4256,0.283792,'farmer','WAK0002',NULL,'2024-09-02 05:20:03','2024-09-02 05:20:03',2,2),
(3,33.1809,0.772661,'farmer','WAK0002',NULL,'2024-09-02 05:20:04','2024-09-02 05:20:04',2,2),
(4,32.5355,1.09671,'farmer','WAK0002',NULL,'2024-09-02 05:20:04','2024-09-02 05:20:04',2,2),
(5,32.5822,1.08024,'farmer','WAK0002',NULL,'2024-09-02 05:20:04','2024-09-02 05:20:04',2,2),
(6,32.3239,0.81476,'farmer','WAK0002',NULL,'2024-09-02 05:20:05','2024-09-02 05:20:05',2,2),
(7,30.0659,0.700594,'farmer','BUNDI02',NULL,'2024-09-02 14:35:34','2024-09-02 14:35:34',9,9),
(8,30.0663,0.700025,'farmer','BUNDI02',NULL,'2024-09-02 14:35:35','2024-09-02 14:35:35',9,9),
(9,30.0659,0.699908,'farmer','BUNDI02',NULL,'2024-09-02 14:35:35','2024-09-02 14:35:35',9,9),
(10,30.0661,0.699682,'farmer','BUNDI02',NULL,'2024-09-02 14:35:35','2024-09-02 14:35:35',9,9),
(11,30.0639,0.699276,'farmer','BUNDI02',NULL,'2024-09-02 14:35:36','2024-09-02 14:35:36',9,9),
(12,30.0659,0.700594,'farmer','BUNDI02',NULL,'2024-09-02 14:35:36','2024-09-02 14:35:36',9,9),
(13,30.0687,0.711353,'farmer','BUNDI01',NULL,'2024-09-02 14:43:36','2024-09-02 14:43:36',9,9),
(14,30.069,0.711492,'farmer','BUNDI01',NULL,'2024-09-02 14:43:37','2024-09-02 14:43:37',9,9),
(15,30.0691,0.711243,'farmer','BUNDI01',NULL,'2024-09-02 14:43:37','2024-09-02 14:43:37',9,9),
(16,30.0688,0.711048,'farmer','BUNDI01',NULL,'2024-09-02 14:43:38','2024-09-02 14:43:38',9,9),
(17,30.0685,0.711122,'farmer','BUNDI01',NULL,'2024-09-02 14:43:38','2024-09-02 14:43:38',9,9),
(18,30.0686,0.711314,'farmer','BUNDI01',NULL,'2024-09-02 14:43:39','2024-09-02 14:43:39',9,9),
(19,30.0687,0.711353,'farmer','BUNDI01',NULL,'2024-09-02 14:43:39','2024-09-02 14:43:39',9,9);
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

-- Dump completed on 2024-09-09  2:00:02
