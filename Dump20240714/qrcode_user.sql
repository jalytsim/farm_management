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
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (2,'Admin','admin@admin.admin','pbkdf2:sha256:600000$us9tk0a4zUPQBs8f$06f2ace9bba750792ab34515795ebc53a5fce96d450c9fac0f23ab90e14effb5','0303030303','admin',1,'2024-06-11 08:03:32','2024-06-11 08:03:32'),(3,'sasakawa1','sasakawa1@agriyields.com','pbkdf2:sha256:600000$zQFb0iorZfRBdryr$cfc389cd12727383093280f9a2ba14f23f210427e17d076b5fe563a53bd04e4d','25678123456','farmer',0,'2024-06-11 09:04:36','2024-06-11 09:04:36'),(4,'sasakawa2','sasakawa2@agriyields.com','pbkdf2:sha256:600000$6M2tFAyX2JeNUZaj$4e11ba6e82153b9f21a88f9161718aa1337956f460f71ff26eb3766e7a590a6c','25678654321','farmer',0,'2024-06-11 09:05:13','2024-06-11 09:05:13'),(5,'sasakawa3','sasakawa3@agriyields.com','pbkdf2:sha256:600000$pQInTYpAXjrI33ec$91b504e360d3531803c2b7da12a91230516f630cc3706824cde9709e5437c6b8','25675654321','farmer',0,'2024-06-11 09:05:43','2024-06-11 09:05:43'),(6,'brian','lwetutb@agriyields.com','pbkdf2:sha256:600000$cTRyZKoIYutjZTJ2$362c2fd768417acee8518367b294f72c92580b286a0827040293777b7ac9887c','256783130358','admin',1,'2024-06-11 09:29:11','2024-06-11 09:29:11'),(8,'theo@agriyields.com','theo@agriyields.com','pbkdf2:sha256:600000$mLUrCNtvYpofxGIh$e8937ad25e22bb2fd724e1829c2d48d2c6ffd5c42ab16526e730c3386eb40edc','256703123456','forest',0,'2024-06-11 19:43:18','2024-06-11 19:43:18'),(9,'bahati','bahati@agriyields.com','pbkdf2:sha256:600000$PGbJErsb3epKf0rN$208bbb5893bb089a3e0adfeb62fea4442b6085bdbde8932bbc7c2589e24f7339','256772621397','farmer',0,'2024-06-24 13:34:21','2024-06-24 13:34:21');
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

-- Dump completed on 2024-07-14  7:21:13
