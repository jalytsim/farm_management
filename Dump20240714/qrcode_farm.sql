CREATE DATABASE  IF NOT EXISTS `qrcode` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `qrcode`;
-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: qrcode
-- ------------------------------------------------------
-- Server version	8.0.36

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `farm`
--

DROP TABLE IF EXISTS `farm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `farm`
--

LOCK TABLES `farm` WRITE;
/*!40000 ALTER TABLE `farm` DISABLE KEYS */;
INSERT INTO `farm` VALUES (1,'B0001','Isiah Namanya','1',1,1,'0.38551,33.3421','2024-06-11 09:08:19','2024-07-14 01:26:50',NULL,NULL,3,NULL),(3,'WAK0002','Lwetutte Brian','Busukuma',3,3,'0.545614,32.579339','2024-06-21 11:50:52','2024-07-14 01:26:50','256783130358','256756411682',3,NULL),(5,'KBRL001','Jackus Munihera','Karangura',4,9,'0.658541,30.156032','2024-06-24 14:22:52','2024-07-14 01:26:50','25674123456','25675123456',3,NULL),(6,'KBRL004','John Mugisha','Karangura',4,9,'0.69297,30.180577','2024-06-25 10:18:54','2024-07-14 01:26:50','','',3,NULL),(7,'KBRL003','Daniel Maate','Karangura',4,9,'0.69391,30.180621','2024-06-25 10:26:38','2024-07-14 01:26:50','','',3,NULL),(8,'KBRL002','Musoki Faibe','Karangura',4,9,'0.658917,30.156655','2024-06-25 10:28:22','2024-07-14 01:26:50','','',3,NULL),(9,'BUIK002','Bwebale Badru','Ngoogwe',1,1,'0.257593,32.923496','2024-06-25 19:52:04','2024-07-14 01:26:50','','',3,NULL),(10,'BUIK003','Mafuko Muzamiru','Ngoogwe',1,1,'0.234431,32.910984','2024-06-25 20:01:21','2024-07-14 01:26:50','256755976395','',3,NULL);
/*!40000 ALTER TABLE `farm` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-07-14  7:21:13
