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
-- Table structure for table `point`
--

DROP TABLE IF EXISTS `point`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=180 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `point`
--

LOCK TABLES `point` WRITE;
/*!40000 ALTER TABLE `point` DISABLE KEYS */;
INSERT INTO `point` VALUES (2,32.5866,0.545164,'forest',1,NULL,3,'2024-06-20 19:30:27','2024-07-14 01:16:23',8,NULL,NULL),(3,32.5883,0.544809,'forest',1,NULL,3,'2024-06-20 19:32:45','2024-07-14 01:16:23',8,NULL,NULL),(4,32.5902,0.5437,'forest',1,NULL,3,'2024-06-20 19:33:31','2024-07-14 01:16:23',8,NULL,NULL),(5,32.5906,0.542582,'forest',1,NULL,3,'2024-06-20 19:34:23','2024-07-14 01:16:23',8,NULL,NULL),(6,32.5903,0.542391,'forest',1,NULL,3,'2024-06-20 19:36:24','2024-07-14 01:16:23',8,NULL,NULL),(7,32.5901,0.542102,'forest',1,NULL,3,'2024-06-20 19:37:18','2024-07-14 01:16:23',8,NULL,NULL),(8,32.5891,0.541376,'forest',1,NULL,3,'2024-06-20 19:38:04','2024-07-14 01:16:23',8,NULL,NULL),(9,32.5881,0.540543,'forest',1,NULL,3,'2024-06-20 19:38:54','2024-07-14 01:16:23',8,NULL,NULL),(11,32.5867,0.540862,'forest',1,NULL,3,'2024-06-20 19:44:06','2024-07-14 01:16:23',8,NULL,NULL),(12,32.5864,0.541312,'forest',1,NULL,3,'2024-06-20 19:44:48','2024-07-14 01:16:23',8,NULL,NULL),(13,32.5869,0.542019,'forest',1,NULL,3,'2024-06-20 19:45:24','2024-07-14 01:16:23',8,NULL,NULL),(14,32.5863,0.541702,'forest',1,NULL,3,'2024-06-20 19:46:20','2024-07-14 01:16:23',8,NULL,NULL),(15,32.5857,0.542453,'forest',1,NULL,3,'2024-06-20 19:47:22','2024-07-14 01:16:23',8,NULL,NULL),(16,32.5861,0.54514,'forest',1,NULL,3,'2024-06-20 19:47:58','2024-07-14 01:16:23',8,NULL,NULL),(17,32.5866,0.545118,'forest',1,NULL,3,'2024-06-20 19:48:37','2024-07-14 01:16:23',8,NULL,NULL),(18,32.5889,0.54519,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(19,32.5889,0.545424,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(20,32.5891,0.545861,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(21,32.59,0.545409,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(22,32.5901,0.545245,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(23,32.5904,0.545663,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(24,32.5907,0.545458,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(25,32.5906,0.545196,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(26,32.5911,0.54479,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(27,32.5912,0.544532,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(28,32.5912,0.544332,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(29,32.5915,0.54422,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(30,32.5912,0.543855,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(31,32.5915,0.543857,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(32,32.592,0.543428,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(33,32.5917,0.542925,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(34,32.5912,0.542902,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(35,32.591,0.542433,'forest',2,NULL,3,'2024-06-21 07:48:51','2024-07-14 01:16:23',8,NULL,NULL),(85,32.6505,0.361753,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),(86,32.6515,0.361352,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),(87,32.6521,0.361054,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),(88,32.6521,0.36098,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),(89,32.6517,0.361107,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),(90,32.6516,0.361494,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),(91,32.6515,0.361352,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),(92,32.6511,0.360711,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),(93,32.6509,0.361618,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),(94,32.651,0.361575,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:16:23',8,NULL,NULL),(95,32.6515,0.360818,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:17:50',8,NULL,NULL),(96,32.6512,0.361183,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:17:50',8,NULL,NULL),(97,32.6527,0.361116,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:17:50',8,NULL,NULL),(98,32.6524,0.36114,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:17:50',8,NULL,NULL),(99,32.6508,0.36126,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:17:50',8,NULL,NULL),(100,32.6508,0.361496,'forest',4,NULL,3,'2024-06-21 08:17:06','2024-07-14 01:17:50',8,NULL,NULL),(101,32.651,0.358072,'forest',5,NULL,3,'2024-06-21 08:22:40','2024-07-14 01:17:50',8,NULL,NULL),(102,32.6512,0.357922,'forest',5,NULL,3,'2024-06-21 08:22:40','2024-07-14 01:17:50',8,NULL,NULL),(103,32.6511,0.358134,'forest',5,NULL,3,'2024-06-21 08:22:40','2024-07-14 01:17:50',8,NULL,NULL),(104,32.651,0.358383,'forest',5,NULL,3,'2024-06-21 08:22:40','2024-07-14 01:17:50',8,NULL,NULL),(105,32.6511,0.358306,'forest',5,NULL,3,'2024-06-21 08:22:40','2024-07-14 01:17:50',8,NULL,NULL),(107,32.5793,0.545614,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),(108,32.5784,0.54517,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),(109,32.5782,0.545209,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),(110,32.5783,0.545404,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),(111,32.5785,0.545677,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),(112,32.5786,0.545716,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),(113,32.5788,0.545826,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),(114,32.5787,0.54592,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),(115,32.5791,0.546061,'farmer',NULL,'WAK0002',3,'2024-06-21 12:11:40','2024-07-14 01:19:27',3,NULL,NULL),(130,30.156,0.658541,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-07-14 01:19:27',3,NULL,NULL),(131,30.1562,0.658456,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-07-14 01:19:27',3,NULL,NULL),(132,30.156,0.658593,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-07-14 01:19:27',3,NULL,NULL),(133,30.1558,0.658688,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-07-14 01:19:27',3,NULL,NULL),(134,30.1561,0.658704,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-07-14 01:19:27',3,NULL,NULL),(135,30.1563,0.658752,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-07-14 01:19:27',3,NULL,NULL),(136,30.1562,0.658716,'farmer',NULL,'KBRL001',9,'2024-06-25 10:10:35','2024-07-14 01:19:27',3,NULL,NULL),(148,30.1806,0.69297,'farmer',NULL,'KBRL004',9,'2024-06-25 10:24:22','2024-07-14 01:19:27',3,NULL,NULL),(149,30.1806,0.693008,'farmer',NULL,'KBRL004',9,'2024-06-25 10:24:22','2024-07-14 01:19:27',3,NULL,NULL),(150,30.1804,0.692953,'farmer',NULL,'KBRL004',9,'2024-06-25 10:24:22','2024-07-14 01:19:27',3,NULL,NULL),(151,30.1804,0.69315,'farmer',NULL,'KBRL004',9,'2024-06-25 10:24:22','2024-07-14 01:19:27',3,NULL,NULL),(152,30.1806,0.69391,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-07-14 01:19:27',3,NULL,NULL),(153,30.1804,0.69349,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-07-14 01:19:27',3,NULL,NULL),(154,30.1804,0.693545,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-07-14 01:19:27',3,NULL,NULL),(155,30.1804,0.693627,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-07-14 01:19:27',3,NULL,NULL),(156,30.1803,0.693974,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-07-14 01:19:27',3,NULL,NULL),(157,30.1803,0.693925,'farmer',NULL,'KBRL003',9,'2024-06-25 10:28:49','2024-07-14 01:19:27',3,NULL,NULL),(158,30.1567,0.658917,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),(159,30.157,0.659031,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),(160,30.1574,0.659111,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),(161,30.1574,0.659114,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),(162,30.1574,0.659137,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),(163,30.1573,0.659337,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),(164,30.1572,0.659258,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),(165,30.1572,0.659292,'farmer',NULL,'KBRL002',9,'2024-06-25 10:29:03','2024-07-14 01:19:27',3,NULL,NULL),(166,32.9105,0.219132,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),(167,32.9131,0.233018,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),(168,32.9203,0.24262,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),(169,32.9262,0.2573,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),(170,32.9094,0.221496,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),(171,32.9447,0.288372,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),(172,32.9093,0.219703,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),(173,32.9149,0.23157,'farmer',NULL,'BUIK002',1,'2024-06-25 20:08:41','2024-07-14 01:19:27',3,NULL,NULL),(174,32.9106,0.233658,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-07-14 01:19:27',3,NULL,NULL),(175,32.9116,0.233934,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-07-14 01:19:27',3,NULL,NULL),(176,32.9121,0.234962,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-07-14 01:19:27',3,NULL,NULL),(177,32.9129,0.237516,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-07-14 01:19:27',3,NULL,NULL),(178,32.9134,0.238388,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-07-14 01:19:27',3,NULL,NULL),(179,32.9116,0.23444,'farmer',NULL,'BUIK003',1,'2024-06-25 20:09:04','2024-07-14 01:19:27',3,NULL,NULL);
/*!40000 ALTER TABLE `point` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-07-14  7:21:14