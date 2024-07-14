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
-- Table structure for table `farmdata`
--

DROP TABLE IF EXISTS `farmdata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `farmdata`
--

LOCK TABLES `farmdata` WRITE;
/*!40000 ALTER TABLE `farmdata` DISABLE KEYS */;
INSERT INTO `farmdata` VALUES (1,'B0001',1,'Titled',2,'2024-06-11',1,'1',2000,'2024-06-29',2000,1800,'2024-10-29 12:21:00','Sasakawa','Italy','AgroPlus','2024-06-11 09:23:06','2024-07-14 07:08:12',3,NULL),(2,'WAK0002',7,'Titled',2,'2024-02-01',2,'1',2,'2024-08-29',3,2,'2024-08-30 20:03:00','Sasakawa','Italy','AgroPlus','2024-06-21 12:03:51','2024-07-14 07:08:13',3,NULL);
/*!40000 ALTER TABLE `farmdata` ENABLE KEYS */;
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
