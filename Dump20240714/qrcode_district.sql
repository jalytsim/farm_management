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
-- Table structure for table `district`
--

DROP TABLE IF EXISTS `district`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `district`
--

LOCK TABLES `district` WRITE;
/*!40000 ALTER TABLE `district` DISABLE KEYS */;
INSERT INTO `district` VALUES (1,'Buikwe','Central','2024-06-11 09:01:59','2024-06-11 09:01:59',NULL,NULL),(2,'Mpigi','Central','2024-06-11 09:02:09','2024-06-11 09:02:09',NULL,NULL),(3,'Wakiso','Central','2024-06-11 09:02:21','2024-06-11 09:02:21',NULL,NULL),(4,'Luweero','Central','2024-06-11 09:02:33','2024-06-11 09:02:33',NULL,NULL),(5,'Masaka','Central','2024-06-11 09:02:47','2024-06-11 09:02:47',NULL,NULL),(6,'Kalangala','Central','2024-06-11 09:03:02','2024-06-11 09:03:02',NULL,NULL),(7,'Mbarara','West','2024-06-11 09:03:19','2024-06-11 09:03:19',NULL,NULL),(8,'Mbale','East','2024-06-11 09:03:29','2024-06-11 09:03:29',NULL,NULL),(9,'Kabarole ','West','2024-06-24 14:06:44','2024-06-24 14:06:44',NULL,NULL),(10,'Gulu','North','2024-06-25 08:54:53','2024-06-25 08:54:53',NULL,NULL),(11,'Lira','North','2024-06-25 08:55:03','2024-06-25 08:55:03',NULL,NULL),(12,'Jinja','East','2024-06-25 08:55:19','2024-06-25 08:55:19',NULL,NULL),(13,'Mayuge','East','2024-06-25 08:55:38','2024-06-25 08:55:38',NULL,NULL),(14,'Bukomansimbi','Central','2024-06-25 08:55:55','2024-06-25 08:55:55',NULL,NULL);
/*!40000 ALTER TABLE `district` ENABLE KEYS */;
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
