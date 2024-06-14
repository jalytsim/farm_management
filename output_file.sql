-- MariaDB dump 10.19  Distrib 10.11.6-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: qrcode
-- ------------------------------------------------------
-- Server version	10.11.6-MariaDB-0ubuntu0.23.10.2

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
-- Table structure for table `crop`
--

DROP TABLE IF EXISTS `crop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `crop` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `weight` float DEFAULT NULL,
  `category_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `crop_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `producecategory` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `crop`
--

LOCK TABLES `crop` WRITE;
/*!40000 ALTER TABLE `crop` DISABLE KEYS */;
INSERT INTO `crop` VALUES
(1,'Maize',50,1),
(2,'Beans',10,2),
(3,'Coffee',25,3),
(4,'Cassava',30,4),
(5,'Rice',20,5),
(6,'Bananas',15,6),
(7,'Coffee Arabica',25,1),
(8,'Coffee Robusta',20,2),
(9,'Tea',25,4),
(10,'Soybean',20,3),
(11,'Cocoa',2,1),
(12,'Oil Palm',3,7);
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
  `name` varchar(255) DEFAULT NULL,
  `region` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=126 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `district`
--

LOCK TABLES `district` WRITE;
/*!40000 ALTER TABLE `district` DISABLE KEYS */;
INSERT INTO `district` VALUES
(1,'Abim','North'),
(2,'Adjumani','North'),
(3,'Agago','North'),
(4,'Alebtong','North'),
(5,'Amolatar','North'),
(6,'Amudat','East'),
(7,'Amuria','East'),
(8,'Amuru','North'),
(9,'Apac','North'),
(10,'Arua','North'),
(11,'Budaka','East'),
(12,'Bududa','East'),
(13,'Bugiri','East'),
(14,'Bugweri','East'),
(15,'Buikwe','Central'),
(16,'Bukedea','East'),
(17,'Bukomansimbi','Central'),
(18,'Bukwo','East'),
(19,'Bulambuli','East'),
(20,'Buliisa','West'),
(21,'Bundibugyo','West'),
(22,'Bunyangabu','West'),
(23,'Bushenyi','West'),
(24,'Busia','East'),
(25,'Butaleja','East'),
(26,'Butambala','Central'),
(27,'Butebo','East'),
(28,'Buvuma','Central'),
(29,'Buyende','East'),
(30,'Dokolo','North'),
(31,'Gomba','Central'),
(32,'Gulu','North'),
(33,'Hoima','West'),
(34,'Ibanda','West'),
(35,'Iganga','East'),
(36,'Isingiro','West'),
(37,'Jinja','East'),
(38,'Kaabong','North'),
(39,'Kabale','West'),
(40,'Kabarole','West'),
(41,'Kaberamaido','East'),
(42,'Kagadi','West'),
(43,'Kagwara','West'),
(44,'Kalaki','East'),
(45,'Kalangala','Central'),
(46,'Kaliro','East'),
(47,'Kalungu','Central'),
(48,'Kampala','Central'),
(49,'Kamuli','East'),
(50,'Kamwenge','West'),
(51,'Kanungu','West'),
(52,'Kapchorwa','East'),
(53,'Kapelebyong','East'),
(54,'Kasese','West'),
(55,'Katakwi','East'),
(56,'Katerera','West'),
(57,'Kayunga','Central'),
(58,'Kibaale','West'),
(59,'Kiboga','Central'),
(60,'Kibuku','East'),
(61,'Kiruhura','West'),
(62,'Kiryandongo','West'),
(63,'Kisoro','West'),
(64,'Kitagwenda','West'),
(65,'Kitgum','North'),
(66,'Koboko','West'),
(67,'Kole','North'),
(68,'Kotido','North'),
(69,'Kumi','East'),
(70,'Kwania','East'),
(71,'Kween','East'),
(72,'Kyankwanzi','Central'),
(73,'Kyegegwa','West'),
(74,'Kyenjojo','West'),
(75,'Kyotera','Central'),
(76,'Lamwo','North'),
(77,'Lira','North'),
(78,'Luuka','East'),
(79,'Luwero','Central'),
(80,'Lwengo','Central'),
(81,'Lyantonde','Central'),
(82,'Manafwa','East'),
(83,'Maracha','West'),
(84,'Masaka','Central'),
(85,'Masindi','West'),
(86,'Mayuge','East'),
(87,'Mbale','East'),
(88,'Mbarara','West'),
(89,'Mitooma','West'),
(90,'Mityana','Central'),
(91,'Moroto','North'),
(92,'Moyo','North'),
(93,'Mpigi','Central'),
(94,'Mubende','Central'),
(95,'Mukono','Central'),
(96,'Nakapiripirit','North'),
(97,'Nakaseke','Central'),
(98,'Nakasongola','Central'),
(99,'Namayingo','East'),
(100,'Namisindwa','East'),
(101,'Namutumba','East'),
(102,'Napak','North'),
(103,'Nebbi','West'),
(104,'Ngora','East'),
(105,'Ntoroko','West'),
(106,'Ntungamo','West'),
(107,'Nwoya','North'),
(108,'Otuke','North'),
(109,'Oyam','North'),
(110,'Pader','North'),
(111,'Pallisa','East'),
(112,'Rakai','Central'),
(113,'Rubanda','West'),
(114,'Rubirizi','West'),
(115,'Rukiga','West'),
(116,'Rukungiri','West'),
(117,'Sembabule','Central'),
(118,'Serere','East'),
(119,'Sheema','West'),
(120,'Sironko','East'),
(121,'Soroti','East'),
(122,'Tororo','East'),
(123,'Wakiso','Central'),
(124,'Yumbe','West'),
(125,'Zombo','West');
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
  `name` varchar(255) DEFAULT NULL,
  `subcounty` varchar(255) DEFAULT NULL,
  `farmergroup_id` int(11) DEFAULT NULL,
  `district_id` int(11) DEFAULT NULL,
  `geolocation` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `district_id` (`district_id`),
  KEY `farmergroup_id` (`farmergroup_id`),
  CONSTRAINT `farm_ibfk_1` FOREIGN KEY (`district_id`) REFERENCES `district` (`id`),
  CONSTRAINT `farm_ibfk_2` FOREIGN KEY (`farmergroup_id`) REFERENCES `farmergroup` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=135 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `farm`
--

LOCK TABLES `farm` WRITE;
/*!40000 ALTER TABLE `farm` DISABLE KEYS */;
INSERT INTO `farm` VALUES
(1,'John Doe Farm','Kawempe',1,1,'0.3163,32.5822'),
(2,'Jane Smith Farm','Gulu',2,2,'2.7809,32.2995'),
(3,'Peter Kato Farm','Mbale',3,3,'1.0647,34.1797'),
(4,'Sarah Nalubega Farm','Makindye',1,4,'0.2986,32.6235'),
(5,'David Omondi Farm','Nwoya',2,5,'2.6249,31.3952'),
(6,'Grace Nakato Farm','Bubulo',3,6,'1.0722,34.1691'),
(7,'Joseph Ssempala Farm','Rubaga',1,7,'0.2947,32.5521'),
(8,'Mercy Auma Farm','Pader',2,8,'2.7687,33.2428'),
(9,'Andrew Wabwire Farm','Manafwa',3,9,'1.1714,34.3447'),
(10,'Harriet Namutebi Farm','Nakawa',1,10,'0.3153,32.6153'),
(11,'Emmanuel Ojok Farm','Lira',2,11,'2.2481,32.8997'),
(12,'Joyce Nakazibwe Farm','Sironko',3,12,'1.2236,34.3874'),
(13,'Richard Kizza Farm','Nansana',1,13,'0.3652,32.5274'),
(14,'Sarah Nambooze Farm','Kitgum',2,14,'3.3017,32.8737'),
(15,'Godfrey Sserwadda Farm','Kapchorwa',3,15,'1.3962,34.4507'),
(16,'Mary Nalule Farm','Wakiso',1,16,'0.4054,32.4594'),
(17,'Isaac Ongom Farm','Amuru',2,17,'2.8231,31.4344'),
(18,'Agnes Atim Farm','Bududa',3,18,'1.0614,34.3294'),
(19,'Charles Odoi Farm','Kira',1,19,'0.3673,32.6159'),
(20,'Florence Nakimera Farm','Adjumani',2,20,'3.3812,31.7989'),
(21,'Alice Achieng Farm','Apac',1,21,'1.9730,32.5380'),
(22,'Brian Musisi Farm','Bukedea',2,22,'1.3494,34.0636'),
(23,'Catherine Namubiru Farm','Bushenyi',3,23,'0.5854,30.2160'),
(24,'Daniel Odongo Farm','Busia',1,24,'0.4544,34.0735'),
(25,'Eunice Nakato Farm','Buwenge',2,25,'0.4582,33.2142'),
(26,'Francis Ssempijja Farm','Entebbe',3,26,'0.0527,32.4463'),
(27,'Grace Nakayenga Farm','Fort Portal',1,27,'0.6711,30.2755'),
(28,'Henry Kiwanuka Farm','Hoima',2,28,'1.4356,31.3586'),
(29,'Irene Nankya Farm','Iganga',3,29,'0.6093,33.4862'),
(30,'Josephine Nabukenya Farm','Isingiro',1,30,'0.7587,30.9399'),
(31,'Kenneth Odhiambo Farm','Jinja',1,31,'0.4244,33.2041'),
(32,'Lilian Nalwanga Farm','Kabale',2,32,'1.2504,29.9857'),
(33,'Moses Ochieng Farm','Kabarole',3,33,'0.6107,30.2778'),
(34,'Nancy Nantume Farm','Kabingo',1,34,'0.0836,32.4789'),
(35,'Oscar Okoth Farm','Kabwohe',2,35,'0.8084,30.8014'),
(36,'Patricia Namutebi Farm','Kajansi',3,36,'0.1519,32.5078'),
(37,'Quincy Odongo Farm','Kaliro',1,37,'0.9031,33.5097'),
(38,'Rebecca Nakato Farm','Kamuli',2,38,'0.9479,33.1197'),
(39,'Stephen Ssemwogerere Farm','Kanungu',3,39,'0.9574,29.7980'),
(40,'Teresa Nakabugo Farm','Kapchorwa',1,40,'1.3696,34.4027'),
(41,'Umar Ssebunya Farm','Kasese',2,41,'0.1830,30.0665'),
(42,'Violet Namutebi Farm','Katakwi',3,42,'1.8910,33.9756'),
(43,'William Odoi Farm','Kayunga',1,43,'0.7021,32.8874'),
(44,'Xavier Ouma Farm','Kibaale',2,44,'0.8830,31.3970'),
(45,'Yusuf Ssebadduka Farm','Kiboga',3,45,'0.7880,31.0886'),
(46,'Zainabu Nansubuga Farm','Kisoro',1,46,'1.3521,29.6935'),
(47,'Abdul Nsereko Farm','Kitagata',2,47,'0.6346,30.2557'),
(48,'Betty Nandawula Farm','Kitgum',3,48,'3.2783,32.8842'),
(49,'Charles Okello Farm','Koboko',1,49,'3.4114,30.9601'),
(50,'Dorothy Nakyobe Farm','Kotido',2,50,'3.0132,34.1336'),
(51,'Alice Aol Farm','Kumi',1,51,'1.4583,33.9365'),
(52,'Brian Okoth Farm','Kyenjojo',2,52,'0.6239,30.6206'),
(53,'Catherine Nambi Farm','Lira',3,53,'2.2358,32.9090'),
(54,'Daniel Opolot Farm','Luwero',1,54,'0.8499,32.4737'),
(55,'Eunice Nabadda Farm','Lwengo',2,55,'0.4168,31.4114'),
(56,'Francis Ongom Farm','Masaka',3,56,'0.3153,31.7133'),
(57,'Grace Nakitende Farm','Masindi',1,57,'1.6736,31.7092'),
(58,'Henry Owor Farm','Mayuge',2,58,'0.4603,33.4621'),
(59,'Irene Nakanjako Farm','Mbale',3,59,'1.0647,34.1797'),
(60,'Josephine Namatovu Farm','Mbarara',1,60,'0.6098,30.6485'),
(61,'Kenneth Odeke Farm','Mitooma',2,61,'0.6166,30.0763'),
(62,'Lilian Auma Farm','Moroto',3,62,'2.4956,34.6751'),
(63,'Moses Okello Farm','Moyo',1,63,'3.6333,31.7167'),
(64,'Nancy Nabayego Farm','Mpigi',2,64,'0.2254,32.3133'),
(65,'Oscar Otema Farm','Mubende',3,65,'0.5901,31.3904'),
(66,'Patricia Nakazibwe Farm','Mukono',1,66,'0.3536,32.7554'),
(67,'Quincy Ojok Farm','Nakapiripirit',2,67,'1.8262,34.7172'),
(68,'Rebecca Nabirye Farm','Nakaseke',3,68,'0.7519,32.3631'),
(69,'Stephen Sserwadda Farm','Nakasongola',1,69,'1.3084,32.4587'),
(70,'Teresa Nalubega Farm','Nebbi',2,70,'2.4758,31.0993'),
(71,'Umar Okello Farm','Ngora',3,71,'1.4314,33.7065'),
(72,'Violet Nakyobe Farm','Ntoroko',1,72,'1.0386,30.4329'),
(73,'William Ogenrwot Farm','Ntungamo',2,73,'0.8769,30.2707'),
(74,'Xavier Odong Farm','Pakwach',3,74,'2.4544,31.4704'),
(75,'Yusuf Ssekandi Farm','Pallisa',1,75,'1.1455,33.7092'),
(76,'John Doe Farm','Kawempe',1,76,'0.3163,32.5822'),
(77,'Jane Smith Farm','Gulu',2,77,'2.7809,32.2995'),
(78,'Peter Kato Farm','Mbale',3,78,'1.0647,34.1797'),
(79,'Sarah Nalubega Farm','Makindye',1,79,'0.2986,32.6235'),
(80,'David Omondi Farm','Nwoya',2,80,'2.6249,31.3952'),
(81,'Grace Nakato Farm','Bubulo',3,81,'1.0722,34.1691'),
(82,'Joseph Ssempala Farm','Rubaga',1,82,'0.2947,32.5521'),
(83,'Mercy Auma Farm','Pader',2,83,'2.7687,33.2428'),
(84,'Andrew Wabwire Farm','Manafwa',3,84,'1.1714,34.3447'),
(85,'Harriet Namutebi Farm','Nakawa',1,85,'0.3153,32.6153'),
(86,'Emmanuel Ojok Farm','Lira',2,86,'2.2481,32.8997'),
(87,'Joyce Nakazibwe Farm','Sironko',3,87,'1.2236,34.3874'),
(88,'Richard Kizza Farm','Nansana',1,88,'0.3652,32.5274'),
(89,'Sarah Nambooze Farm','Kitgum',2,89,'3.3017,32.8737'),
(90,'Godfrey Sserwadda Farm','Kapchorwa',3,90,'1.3962,34.4507'),
(91,'Mary Nalule Farm','Wakiso',1,91,'0.4054,32.4594'),
(92,'Isaac Ongom Farm','Amuru',2,92,'2.8231,31.4344'),
(93,'Agnes Atim Farm','Bududa',3,93,'1.0614,34.3294'),
(94,'Charles Odoi Farm','Kira',1,94,'0.3673,32.6159'),
(95,'Florence Nakimera Farm','Adjumani',2,97,'3.3812,31.7989'),
(96,'Alice Achieng Farm','Apac',1,98,'1.9730,32.5380'),
(97,'Brian Musisi Farm','Bukedea',2,99,'1.3494,34.0636'),
(98,'Catherine Namubiru Farm','Bushenyi',3,100,'0.5854,30.2160'),
(99,'Daniel Odongo Farm','Busia',1,101,'0.4544,34.0735'),
(100,'Eunice Nakato Farm','Buwenge',2,102,'0.4582,33.2142'),
(101,'Francis Ssempijja Farm','Entebbe',3,103,'0.0527,32.4463'),
(102,'Grace Nakayenga Farm','Fort Portal',1,104,'0.6711,30.2755'),
(103,'Henry Kiwanuka Farm','Hoima',2,105,'1.4356,31.3586'),
(104,'Irene Nankya Farm','Iganga',3,106,'0.6093,33.4862'),
(105,'Josephine Nabukenya Farm','Isingiro',1,107,'0.7587,30.9399'),
(106,'Kenneth Odhiambo Farm','Jinja',1,108,'0.4244,33.2041'),
(107,'Lilian Nalwanga Farm','Kabale',2,109,'1.2504,29.9857'),
(108,'Moses Ochieng Farm','Kabarole',3,110,'0.6107,30.2778'),
(109,'Nancy Nantume Farm','Kabingo',1,111,'0.0836,32.4789'),
(110,'Oscar Okoth Farm','Kabwohe',2,112,'0.8084,30.8014'),
(111,'Patricia Namutebi Farm','Kajansi',3,113,'0.1519,32.5078'),
(112,'Quincy Odongo Farm','Kaliro',1,114,'0.9031,33.5097'),
(113,'Rebecca Nakato Farm','Kamuli',2,115,'0.9479,33.1197'),
(114,'Stephen Ssemwogerere Farm','Kanungu',3,116,'0.9574,29.7980'),
(115,'Teresa Nakabugo Farm','Kapchorwa',1,117,'1.3696,34.4027'),
(116,'Umar Ssebunya Farm','Kasese',2,118,'0.1830,30.0665'),
(117,'Violet Namutebi Farm','Katakwi',3,119,'1.8910,33.9756'),
(118,'William Odoi Farm','Kayunga',1,120,'0.7021,32.8874'),
(119,'Xavier Ouma Farm','Kibaale',2,121,'0.8830,31.3970'),
(120,'Yusuf Ssebadduka Farm','Kiboga',3,122,'0.7880,31.0886'),
(121,'Zainabu Nansubuga Farm','Kisoro',1,123,'1.3521,29.6935'),
(122,'Abdul Nsereko Farm','Kitagata',2,124,'0.6346,30.2557'),
(123,'Betty Nandawula Farm','Kitgum',3,125,'3.2783,32.8842'),
(124,'Godfrey Lutwama','Mbale',1,87,'1.0799005,34.1554209'),
(125,'Busingye Joshua','Masaka',2,84,'-0.4855154,31.493016'),
(126,'Wanyama Esperito','Bushenyi',3,23,'-0.5432572,30.1846092'),
(127,'Tea farmer','Nebbi',2,84,'2.4697,31.1028'),
(128,'Soybean Esperito','Ntungamo',3,23,'-0.8794,30.2647'),
(133,'Wharton Aldrick','1',2,3,'122.212'),
(134,'test','test',1,1,'it should be q geolocation');
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
  `farm_id` int(11) DEFAULT NULL,
  `crop_id` int(11) DEFAULT NULL,
  `tilled_land_size` float DEFAULT NULL,
  `planting_date` date DEFAULT NULL,
  `season` int(11) DEFAULT NULL,
  `quality` varchar(255) DEFAULT NULL,
  `quantity` int(11) DEFAULT NULL,
  `harvest_date` date DEFAULT NULL,
  `expected_yield` float DEFAULT NULL,
  `actual_yield` float DEFAULT NULL,
  `timestamp` timestamp NULL DEFAULT NULL,
  `channel_partner` varchar(255) DEFAULT NULL,
  `destination_country` varchar(255) DEFAULT NULL,
  `customer_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `farm_id` (`farm_id`),
  KEY `crop_id` (`crop_id`),
  CONSTRAINT `farmdata_ibfk_1` FOREIGN KEY (`farm_id`) REFERENCES `farm` (`id`),
  CONSTRAINT `farmdata_ibfk_2` FOREIGN KEY (`crop_id`) REFERENCES `crop` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=282 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `farmdata`
--

LOCK TABLES `farmdata` WRITE;
/*!40000 ALTER TABLE `farmdata` DISABLE KEYS */;
INSERT INTO `farmdata` VALUES
(1,1,1,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500,2300,'2023-07-15 09:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(2,1,2,1,'2023-03-20',1,'Fair',50,'2023-07-20',500,480,'2023-07-20 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(3,2,3,0.5,'2023-04-01',1,'Good',20,'2023-09-01',500,480,'2023-09-01 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(5,3,5,0.8,'2023-04-10',1,'Fair',40,'2023-09-10',800,780,'2023-09-10 09:00:00','Jinja Farms Ltd','Uganda','Mbarara Agro Coop'),
(6,3,6,0.3,'2023-04-15',1,'Excellent',15,'2023-09-15',225,220,'2023-09-15 09:00:00','Uganda Green Fields','Uganda','Lira Organic Farmers'),
(7,4,1,2,'2023-03-15',1,'Good',80,'2023-07-15',2000,1900,'2023-07-15 09:00:00','Kasese AgriPro','Uganda','Entebbe Produce Group'),
(8,4,2,0.8,'2023-03-20',1,'Fair',40,'2023-07-20',400,380,'2023-07-20 09:00:00','Uganda Harvesters','Uganda','Soroti Agri Enterprise'),
(9,5,3,0.4,'2023-04-01',1,'Good',15,'2023-09-01',375,370,'2023-09-01 09:00:00','Kabale Farm Solutions','Uganda','Gulu Farmers Coop'),
(10,5,4,0.7,'2023-04-05',1,'Good',25,'2023-09-05',750,740,'2023-09-05 09:00:00','Mbale Agri Ltd','Uganda','Hoima Organic'),
(11,6,5,0.6,'2023-04-10',1,'Fair',30,'2023-09-10',600,580,'2023-09-10 09:00:00','Uganda Agro Services','Uganda','Mityana Produce Group'),
(12,6,6,0.2,'2023-04-15',1,'Excellent',10,'2023-09-15',150,140,'2023-09-15 09:00:00','Jinja Fields','Uganda','Kasese Agri Coop'),
(13,7,1,1.5,'2023-03-15',1,'Good',60,'2023-07-15',1500,1400,'2023-07-15 09:00:00','Uganda Harvest Group','Uganda','Kabale Farms'),
(14,7,2,0.5,'2023-03-20',1,'Fair',25,'2023-07-20',250,240,'2023-07-20 09:00:00','Gulu Agri Solutions','Uganda','Mbale Organic'),
(15,8,3,0.3,'2023-04-01',1,'Good',10,'2023-09-01',250,240,'2023-09-01 09:00:00','Lira Farms','Uganda','Masaka Agri Coop'),
(16,8,4,0.6,'2023-04-05',1,'Good',20,'2023-09-05',600,590,'2023-09-05 09:00:00','Kabale AgriPro','Uganda','Jinja Organic'),
(17,9,5,0.5,'2023-04-10',1,'Fair',25,'2023-09-10',500,490,'2023-09-10 09:00:00','Uganda Green Harvest','Uganda','Mbarara Agri Enterprise'),
(18,9,6,0.2,'2023-04-15',1,'Excellent',10,'2023-09-15',100,90,'2023-09-15 09:00:00','Hoima Agro Solutions','Uganda','Kasese Farmers Coop'),
(19,10,1,1,'2023-03-15',1,'Good',40,'2023-07-15',1000,950,'2023-07-15 09:00:00','Entebbe Agri Ltd','Uganda','Masindi Harvesters'),
(20,10,2,0.4,'2023-03-20',1,'Fair',20,'2023-07-20',200,190,'2023-07-20 09:00:00','Gulu Fields','Uganda','Mbale Agro Coop'),
(21,11,3,0.2,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 09:00:00','Mityana Farms','Uganda','Kabale Agri Group'),
(22,11,4,0.4,'2023-04-05',1,'Good',10,'2023-09-05',300,290,'2023-09-05 09:00:00','Kasese AgroPro','Uganda','Gulu Organic Farmers'),
(23,12,5,0.3,'2023-04-10',1,'Fair',15,'2023-09-10',300,290,'2023-09-10 09:00:00','Mbale Harvest Group','Uganda','Mityana Agri Enterprise'),
(24,12,6,0.1,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 09:00:00','Masaka Agri Solutions','Uganda','Masindi Agri Coop'),
(25,13,1,0.5,'2023-03-15',1,'Good',20,'2023-07-15',500,480,'2023-07-15 09:00:00','Kabale Green Fields','Uganda','Lira Harvest Group'),
(26,13,2,0.2,'2023-03-20',1,'Fair',10,'2023-07-20',100,90,'2023-07-20 09:00:00','Mbarara AgriPro','Uganda','Entebbe Agri Coop'),
(27,14,3,0.1,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 09:00:00','Gulu Harvesters','Uganda','Mbarara Harvesters'),
(28,14,4,0.2,'2023-04-05',1,'Good',5,'2023-09-05',150,140,'2023-09-05 09:00:00','Masaka Fields','Uganda','Hoima Agri Enterprise'),
(29,15,5,0.2,'2023-04-10',1,'Fair',10,'2023-09-10',100,90,'2023-09-10 09:00:00','Mbale AgroPro','Uganda','Masindi Agri Solutions'),
(30,15,6,0.1,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 09:00:00','Mityana Harvesters','Uganda','Entebbe Harvest Group'),
(31,16,1,0.3,'2023-03-15',1,'Good',12,'2023-07-15',300,290,'2023-07-15 09:00:00','Masindi AgroPro','Uganda','Mityana Agri Coop'),
(32,16,2,0.1,'2023-03-20',1,'Fair',6,'2023-07-20',60,50,'2023-07-20 09:00:00','Kabale Fields','Uganda','Jinja Agri Solutions'),
(33,17,3,0.05,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 09:00:00','Mbarara Agri Group','Uganda','Masaka Harvesters'),
(34,17,4,0.1,'2023-04-05',1,'Good',3,'2023-09-05',30,25,'2023-09-05 09:00:00','Mbale Agro Solutions','Uganda','Kabale Agri Solutions'),
(35,18,5,0.1,'2023-04-10',1,'Fair',5,'2023-09-10',50,40,'2023-09-10 09:00:00','Masindi Harvest Group','Uganda','Kasese Agri Coop'),
(36,18,6,0.05,'2023-04-15',1,'Excellent',2,'2023-09-15',20,15,'2023-09-15 09:00:00','Mityana AgroPro','Uganda','Lira Harvesters'),
(37,19,1,0.2,'2023-03-15',1,'Good',8,'2023-07-15',200,190,'2023-07-15 09:00:00','Mbarara Agro Group','Uganda','Mbale Agri Coop'),
(38,19,2,0.1,'2023-03-20',1,'Fair',4,'2023-07-20',40,30,'2023-07-20 09:00:00','Jinja Agri Solutions','Uganda','Mbarara Agri Coop'),
(39,20,3,0.05,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 09:00:00','Masaka AgroPro','Uganda','Masindi Harvesters'),
(40,20,4,0.1,'2023-04-05',1,'Good',3,'2023-09-05',30,25,'2023-09-05 09:00:00','Kabale Agro Solutions','Uganda','Kasese Agri Group'),
(41,1,1,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500,2300,'2023-07-15 09:00:00','Mityana Agri Group','Uganda','Gulu Agri Solutions'),
(42,1,2,1,'2023-03-20',1,'Fair',50,'2023-07-20',500,480,'2023-07-20 09:00:00','Masindi Agro Solutions','Uganda','Mbale Harvesters'),
(43,2,3,0.5,'2023-04-01',1,'Good',20,'2023-09-01',500,480,'2023-09-01 09:00:00','Kasese Agro Group','Uganda','Entebbe Harvest Group'),
(44,2,4,1,'2023-04-05',1,'Good',30,'2023-09-05',900,880,'2023-09-05 09:00:00','Mbarara Agro Solutions','Uganda','Jinja Agri Coop'),
(45,3,5,0.8,'2023-04-10',1,'Fair',40,'2023-09-10',800,780,'2023-09-10 09:00:00','Mbale Agro Group','Uganda','Mbarara Harvesters'),
(46,3,6,0.3,'2023-04-15',1,'Excellent',15,'2023-09-15',225,220,'2023-09-15 09:00:00','Mityana Agro Solutions','Uganda','Masaka Harvesters'),
(47,4,1,2,'2023-03-15',1,'Good',80,'2023-07-15',2000,1900,'2023-07-15 09:00:00','Masaka Agro Group','Uganda','Kabale Agri Coop'),
(48,4,2,0.8,'2023-03-20',1,'Fair',40,'2023-07-20',400,380,'2023-07-20 09:00:00','Kabale Agro Group','Uganda','Mbarara Harvesters'),
(49,5,3,0.4,'2023-04-01',1,'Good',15,'2023-09-01',375,370,'2023-09-01 09:00:00','Mbarara AgroPro','Uganda','Masaka Agri Solutions'),
(50,5,4,0.7,'2023-04-05',1,'Good',25,'2023-09-05',750,740,'2023-09-05 09:00:00','Mbale Agro Solutions','Uganda','Masindi Agri Coop'),
(51,6,5,0.6,'2023-04-10',1,'Fair',30,'2023-09-10',600,580,'2023-09-10 09:00:00','Masaka Agro Solutions','Uganda','Mbarara Harvesters'),
(52,6,6,0.2,'2023-04-15',1,'Excellent',10,'2023-09-15',150,140,'2023-09-15 09:00:00','Mityana AgroPro','Uganda','Kasese Agri Solutions'),
(53,7,1,1.5,'2023-03-15',1,'Good',60,'2023-07-15',1500,1400,'2023-07-15 09:00:00','Masindi Agro Solutions','Uganda','Entebbe Agri Coop'),
(54,7,2,0.5,'2023-03-20',1,'Fair',25,'2023-07-20',250,240,'2023-07-20 09:00:00','Kasese Agro Solutions','Uganda','Mityana Agri Coop'),
(55,8,3,0.3,'2023-04-01',1,'Good',10,'2023-09-01',250,240,'2023-09-01 09:00:00','Mbarara Agro Solutions','Uganda','Masaka Agri Group'),
(56,8,4,0.6,'2023-04-05',1,'Good',20,'2023-09-05',600,590,'2023-09-05 09:00:00','Mbale AgroPro','Uganda','Jinja Agri Coop'),
(57,9,5,0.5,'2023-04-10',1,'Fair',25,'2023-09-10',500,490,'2023-09-10 09:00:00','Masindi AgroPro','Uganda','Mbarara Agri Solutions'),
(58,9,6,0.2,'2023-04-15',1,'Excellent',10,'2023-09-15',100,90,'2023-09-15 09:00:00','Kasese Agro Group','Uganda','Masaka Agri Solutions'),
(59,10,1,1,'2023-03-15',1,'Good',40,'2023-07-15',1000,950,'2023-07-15 09:00:00','Mityana AgroPro','Uganda','Kabale Agri Coop'),
(60,10,2,0.4,'2023-03-20',1,'Fair',20,'2023-07-20',200,190,'2023-07-20 09:00:00','Masaka AgroPro','Uganda','Mbarara Agri Solutions'),
(61,11,3,0.2,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 09:00:00','Mbarara Agro Solutions','Uganda','Kasese Agri Group'),
(62,11,4,0.4,'2023-04-05',1,'Good',10,'2023-09-05',300,290,'2023-09-05 09:00:00','Mbale Agro Solutions','Uganda','Masindi Agri Coop'),
(63,12,5,0.3,'2023-04-10',1,'Fair',15,'2023-09-10',300,290,'2023-09-10 09:00:00','Masaka Agro Solutions','Uganda','Mbarara Agri Group'),
(64,12,6,0.1,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 09:00:00','Mityana AgroPro','Uganda','Masaka Agri Coop'),
(65,13,1,0.5,'2023-03-15',1,'Good',20,'2023-07-15',500,480,'2023-07-15 09:00:00','Masindi AgroPro','Uganda','Jinja Agri Coop'),
(66,13,2,0.2,'2023-03-20',1,'Fair',10,'2023-07-20',100,90,'2023-07-20 09:00:00','Kasese Agro Group','Uganda','Mbarara Agri Solutions'),
(67,14,3,0.1,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 09:00:00','Mbarara Agro Solutions','Uganda','Kasese Agri Coop'),
(68,14,4,0.2,'2023-04-05',1,'Good',5,'2023-09-05',150,140,'2023-09-05 09:00:00','Mbale Agro Solutions','Uganda','Masaka Agri Solutions'),
(69,15,5,0.2,'2023-04-10',1,'Fair',10,'2023-09-10',100,90,'2023-09-10 09:00:00','Masaka Agro Solutions','Uganda','Mbarara Agri Solutions'),
(70,15,6,0.1,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 09:00:00','Mityana AgroPro','Uganda','Kabale Agri Coop'),
(71,16,1,0.3,'2023-03-15',1,'Good',12,'2023-07-15',300,290,'2023-07-15 09:00:00','Masaka AgroPro','Uganda','Mbarara Agri Solutions'),
(72,16,2,0.1,'2023-03-20',1,'Fair',6,'2023-07-20',60,50,'2023-07-20 09:00:00','Mbarara Agro Solutions','Uganda','Kasese Agri Group'),
(73,17,3,0.05,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 09:00:00','Mbale Agro Solutions','Uganda','Masindi Agri Coop'),
(74,17,4,0.1,'2023-04-05',1,'Good',3,'2023-09-05',30,25,'2023-09-05 09:00:00','Masaka Agro Solutions','Uganda','Mbarara Agri Group'),
(75,18,5,0.1,'2023-04-10',1,'Fair',5,'2023-09-10',50,40,'2023-09-10 09:00:00','Mityana AgroPro','Uganda','Masaka Agri Coop'),
(76,18,6,0.05,'2023-04-15',1,'Excellent',2,'2023-09-15',20,15,'2023-09-15 09:00:00','Masindi AgroPro','Uganda','Jinja Agri Coop'),
(77,19,1,0.2,'2023-03-15',1,'Good',8,'2023-07-15',200,190,'2023-07-15 09:00:00','Kasese Agro Group','Uganda','Mbarara Agri Solutions'),
(78,19,2,0.1,'2023-03-20',1,'Fair',4,'2023-07-20',40,30,'2023-07-20 09:00:00','Mbarara Agro Solutions','Uganda','Kasese Agri Coop'),
(79,20,3,0.05,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 09:00:00','Mbale Agro Solutions','Uganda','Masaka Agri Solutions'),
(80,20,4,0.1,'2023-04-05',1,'Good',3,'2023-09-05',30,25,'2023-09-05 09:00:00','Masaka Agro Solutions','Uganda','Mbarara Agri Solutions'),
(81,11,1,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500,2300,'2023-07-15 09:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(82,21,2,1,'2023-03-20',1,'Fair',50,'2023-07-20',500,480,'2023-07-20 09:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(83,32,3,0.5,'2023-04-01',1,'Good',20,'2023-09-01',500,480,'2023-09-01 09:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(84,42,4,1,'2023-04-05',1,'Good',30,'2023-09-05',900,880,'2023-09-05 09:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(85,53,5,0.84,'2023-04-10',1,'Fair',40,'2023-09-10',800,780,'2023-09-10 09:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(86,13,6,0.289,'2023-04-15',1,'Excellent',15,'2023-09-15',225,220,'2023-09-15 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(87,24,1,2,'2023-03-15',1,'Good',80,'2023-07-15',2000,1900,'2023-07-15 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(88,34,2,0.84,'2023-03-20',1,'Fair',40,'2023-07-20',400,380,'2023-07-20 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(89,43,3,0.42,'2023-04-01',1,'Good',15,'2023-09-01',375,370,'2023-09-01 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(90,52,4,0.659,'2023-04-05',1,'Good',25,'2023-09-05',750,740,'2023-09-05 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(91,11,5,0.579,'2023-04-10',1,'Fair',30,'2023-09-10',600,580,'2023-09-10 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(92,12,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',150,140,'2023-09-15 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(93,22,1,1.5,'2023-03-15',1,'Good',60,'2023-07-15',1500,1400,'2023-07-15 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(94,33,2,0.5,'2023-03-20',1,'Fair',25,'2023-07-20',250,240,'2023-07-20 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(95,43,3,0.289,'2023-04-01',1,'Good',10,'2023-09-01',250,240,'2023-09-01 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(96,53,4,0.579,'2023-04-05',1,'Good',20,'2023-09-05',600,590,'2023-09-05 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(97,14,5,0.5,'2023-04-10',1,'Fair',25,'2023-09-10',500,490,'2023-09-10 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(98,25,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',100,90,'2023-09-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(99,16,1,1,'2023-03-15',1,'Good',40,'2023-07-15',1000,950,'2023-07-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(100,17,2,0.4222,'2023-03-20',1,'Fair',20,'2023-07-20',200,190,'2023-07-20 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(101,38,3,0.200111,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(102,19,4,0.400022,'2023-04-05',1,'Good',10,'2023-09-05',300,290,'2023-09-05 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(103,10,5,0.29,'2023-04-10',1,'Fair',15,'2023-09-10',300,290,'2023-09-10 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(104,15,6,0.100555,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(105,41,1,0.5,'2023-03-15',1,'Good',20,'2023-07-15',500,480,'2023-07-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(106,72,2,0.200111,'2023-03-20',1,'Fair',10,'2023-07-20',100,90,'2023-07-20 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(107,52,3,0.155,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(108,13,4,0.21,'2023-04-05',1,'Good',5,'2023-09-05',150,140,'2023-09-05 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(109,14,5,0.21,'2023-04-10',1,'Fair',10,'2023-09-10',100,90,'2023-09-10 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(110,15,6,0.155,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(111,16,1,0.289,'2023-03-15',1,'Good',12,'2023-07-15',300,290,'2023-07-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(112,17,2,0.155,'2023-03-20',1,'Fair',6,'2023-07-20',60,50,'2023-07-20 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(113,18,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(114,19,4,0.155,'2023-04-05',1,'Good',3,'2023-09-05',30,25,'2023-09-05 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(115,20,5,0.155,'2023-04-10',1,'Fair',5,'2023-09-10',50,40,'2023-09-10 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(116,21,6,0.0775,'2023-04-15',1,'Excellent',2,'2023-09-15',20,15,'2023-09-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(117,22,1,0.21,'2023-03-15',1,'Good',8,'2023-07-15',200,190,'2023-07-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(118,38,2,0.155,'2023-03-20',1,'Fair',4,'2023-07-20',40,30,'2023-07-20 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(119,39,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(120,40,1,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500,2300,'2023-07-15 09:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(121,41,2,1,'2023-03-20',1,'Fair',50,'2023-07-20',500,480,'2023-07-20 09:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(122,42,3,0.5,'2023-04-01',1,'Good',20,'2023-09-01',500,480,'2023-09-01 09:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(123,43,4,1,'2023-04-05',1,'Good',30,'2023-09-05',900,880,'2023-09-05 09:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(124,44,5,0.84,'2023-04-10',1,'Fair',40,'2023-09-10',800,780,'2023-09-10 09:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(125,45,6,0.289,'2023-04-15',1,'Excellent',15,'2023-09-15',225,220,'2023-09-15 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(126,46,1,2,'2023-03-15',1,'Good',80,'2023-07-15',2000,1900,'2023-07-15 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(127,47,2,0.84,'2023-03-20',1,'Fair',40,'2023-07-20',400,380,'2023-07-20 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(128,48,3,0.42,'2023-04-01',1,'Good',15,'2023-09-01',375,370,'2023-09-01 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(129,49,4,0.659,'2023-04-05',1,'Good',25,'2023-09-05',750,740,'2023-09-05 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(130,50,5,0.579,'2023-04-10',1,'Fair',30,'2023-09-10',600,580,'2023-09-10 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(131,51,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',150,140,'2023-09-15 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(132,52,1,1.5,'2023-03-15',1,'Good',60,'2023-07-15',1500,1400,'2023-07-15 09:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(133,53,2,0.5,'2023-03-20',1,'Fair',25,'2023-07-20',250,240,'2023-07-20 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(134,54,3,0.289,'2023-04-01',1,'Good',10,'2023-09-01',250,240,'2023-09-01 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(135,55,4,0.579,'2023-04-05',1,'Good',20,'2023-09-05',600,590,'2023-09-05 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(136,56,5,0.5,'2023-04-10',1,'Fair',25,'2023-09-10',500,490,'2023-09-10 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(137,57,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',100,90,'2023-09-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(138,58,1,1,'2023-03-15',1,'Good',40,'2023-07-15',1000,950,'2023-07-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(139,59,2,0.4222,'2023-03-20',1,'Fair',20,'2023-07-20',200,190,'2023-07-20 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(140,60,3,0.200111,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(141,61,4,0.400022,'2023-04-05',1,'Good',10,'2023-09-05',300,290,'2023-09-05 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(142,62,5,0.29,'2023-04-10',1,'Fair',15,'2023-09-10',300,290,'2023-09-10 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(143,63,6,0.100555,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(144,64,1,0.5,'2023-03-15',1,'Good',20,'2023-07-15',500,480,'2023-07-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(145,65,2,0.200111,'2023-03-20',1,'Fair',10,'2023-07-20',100,90,'2023-07-20 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(146,66,3,0.155,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(147,67,4,0.21,'2023-04-05',1,'Good',5,'2023-09-05',150,140,'2023-09-05 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(148,68,5,0.21,'2023-04-10',1,'Fair',10,'2023-09-10',100,90,'2023-09-10 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(149,69,6,0.155,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(150,70,1,0.289,'2023-03-15',1,'Good',12,'2023-07-15',300,290,'2023-07-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(151,72,2,0.155,'2023-03-20',1,'Fair',6,'2023-07-20',60,50,'2023-07-20 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(152,73,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(153,74,4,0.155,'2023-04-05',1,'Good',3,'2023-09-05',30,25,'2023-09-05 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(154,30,5,0.155,'2023-04-10',1,'Fair',5,'2023-09-10',50,40,'2023-09-10 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(155,31,6,0.0775,'2023-04-15',1,'Excellent',2,'2023-09-15',20,15,'2023-09-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(156,32,1,0.21,'2023-03-15',1,'Good',8,'2023-07-15',200,190,'2023-07-15 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(157,33,2,0.155,'2023-03-20',1,'Fair',4,'2023-07-20',40,30,'2023-07-20 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(158,34,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 09:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(159,75,1,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500,2300,'2023-07-15 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(160,76,2,1,'2023-03-20',1,'Fair',50,'2023-07-20',500,480,'2023-07-20 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(161,77,3,0.5,'2023-04-01',1,'Good',20,'2023-09-01',500,480,'2023-09-01 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(162,78,4,1,'2023-04-05',1,'Good',30,'2023-09-05',900,880,'2023-09-05 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(163,79,5,0.84,'2023-04-10',1,'Fair',40,'2023-09-10',800,780,'2023-09-10 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(164,80,6,0.289,'2023-04-15',1,'Excellent',15,'2023-09-15',225,220,'2023-09-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(165,81,1,2,'2023-03-15',1,'Good',80,'2023-07-15',2000,1900,'2023-07-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(166,82,2,0.84,'2023-03-20',1,'Fair',40,'2023-07-20',400,380,'2023-07-20 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(167,83,3,0.42,'2023-04-01',1,'Good',15,'2023-09-01',375,370,'2023-09-01 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(168,84,4,0.659,'2023-04-05',1,'Good',25,'2023-09-05',750,740,'2023-09-05 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(169,85,5,0.579,'2023-04-10',1,'Fair',30,'2023-09-10',600,580,'2023-09-10 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(170,86,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',150,140,'2023-09-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(171,87,1,1.5,'2023-03-15',1,'Good',60,'2023-07-15',1500,1400,'2023-07-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(172,88,2,0.5,'2023-03-20',1,'Fair',25,'2023-07-20',250,240,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(173,89,3,0.289,'2023-04-01',1,'Good',10,'2023-09-01',250,240,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(174,90,4,0.579,'2023-04-05',1,'Good',20,'2023-09-05',600,590,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(175,91,5,0.5,'2023-04-10',1,'Fair',25,'2023-09-10',500,490,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(176,92,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',100,90,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(177,93,1,1,'2023-03-15',1,'Good',40,'2023-07-15',1000,950,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(178,94,2,0.4222,'2023-03-20',1,'Fair',20,'2023-07-20',200,190,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(179,95,3,0.200111,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(180,96,4,0.400022,'2023-04-05',1,'Good',10,'2023-09-05',300,290,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(181,97,5,0.29,'2023-04-10',1,'Fair',15,'2023-09-10',300,290,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(182,98,6,0.100555,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(183,99,1,0.5,'2023-03-15',1,'Good',20,'2023-07-15',500,480,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(184,100,2,0.200111,'2023-03-20',1,'Fair',10,'2023-07-20',100,90,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(185,101,3,0.155,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(186,102,4,0.21,'2023-04-05',1,'Good',5,'2023-09-05',150,140,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(187,103,5,0.21,'2023-04-10',1,'Fair',10,'2023-09-10',100,90,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(188,104,6,0.155,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(189,105,1,0.289,'2023-03-15',1,'Good',12,'2023-07-15',300,290,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(190,106,2,0.155,'2023-03-20',1,'Fair',6,'2023-07-20',60,50,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(191,107,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(192,108,4,0.155,'2023-04-05',1,'Good',3,'2023-09-05',30,25,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(193,109,5,0.155,'2023-04-10',1,'Fair',5,'2023-09-10',50,40,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(194,110,6,0.0775,'2023-04-15',1,'Excellent',2,'2023-09-15',20,15,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(195,111,1,0.21,'2023-03-15',1,'Good',8,'2023-07-15',200,190,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(196,112,2,0.155,'2023-03-20',1,'Fair',4,'2023-07-20',40,30,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(197,113,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(237,114,1,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500,2300,'2023-07-15 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(238,115,2,1,'2023-03-20',1,'Fair',50,'2023-07-20',500,480,'2023-07-20 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(239,116,3,0.5,'2023-04-01',1,'Good',20,'2023-09-01',500,480,'2023-09-01 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(240,117,4,1,'2023-04-05',1,'Good',30,'2023-09-05',900,880,'2023-09-05 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(241,118,5,0.84,'2023-04-10',1,'Fair',40,'2023-09-10',800,780,'2023-09-10 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(242,119,6,0.289,'2023-04-15',1,'Excellent',15,'2023-09-15',225,220,'2023-09-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(243,120,1,2,'2023-03-15',1,'Good',80,'2023-07-15',2000,1900,'2023-07-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(244,121,2,0.84,'2023-03-20',1,'Fair',40,'2023-07-20',400,380,'2023-07-20 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(245,122,3,0.42,'2023-04-01',1,'Good',15,'2023-09-01',375,370,'2023-09-01 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(246,123,4,0.659,'2023-04-05',1,'Good',25,'2023-09-05',750,740,'2023-09-05 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms'),
(247,80,2,0.5,'2023-03-20',1,'Fair',25,'2023-07-20',250,240,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(248,82,3,0.289,'2023-04-01',1,'Good',10,'2023-09-01',250,240,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(249,83,4,0.579,'2023-04-05',1,'Good',20,'2023-09-05',600,590,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(250,84,5,0.5,'2023-04-10',1,'Fair',25,'2023-09-10',500,490,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(251,85,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',100,90,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(252,86,1,1,'2023-03-15',1,'Good',40,'2023-07-15',1000,950,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(253,87,2,0.4222,'2023-03-20',1,'Fair',20,'2023-07-20',200,190,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(254,88,3,0.200111,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(255,89,4,0.400022,'2023-04-05',1,'Good',10,'2023-09-05',300,290,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(256,90,5,0.29,'2023-04-10',1,'Fair',15,'2023-09-10',300,290,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(257,92,6,0.100555,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(258,83,1,0.5,'2023-03-15',1,'Good',20,'2023-07-15',500,480,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(259,94,2,0.200111,'2023-03-20',1,'Fair',10,'2023-07-20',100,90,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(260,95,3,0.155,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(261,96,4,0.21,'2023-04-05',1,'Good',5,'2023-09-05',150,140,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(262,97,5,0.21,'2023-04-10',1,'Fair',10,'2023-09-10',100,90,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(263,98,6,0.155,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(264,99,1,0.289,'2023-03-15',1,'Good',12,'2023-07-15',300,290,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(265,100,2,0.155,'2023-03-20',1,'Fair',6,'2023-07-20',60,50,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(266,101,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(267,102,4,0.155,'2023-04-05',1,'Good',3,'2023-09-05',30,25,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(268,103,5,0.155,'2023-04-10',1,'Fair',5,'2023-09-10',50,40,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(269,104,6,0.0775,'2023-04-15',1,'Excellent',2,'2023-09-15',20,15,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(270,105,1,0.21,'2023-03-15',1,'Good',8,'2023-07-15',200,190,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(271,106,2,0.155,'2023-03-20',1,'Fair',4,'2023-07-20',40,30,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(272,107,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.'),
(273,124,7,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500,2300,'2023-07-15 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(274,125,8,1,'2023-03-20',1,'Excellent',50,'2023-07-20',500,480,'2023-07-20 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(275,126,7,3.5,'2023-03-15',1,'Good',100,'2023-07-15',2500,2300,'2023-07-15 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(276,126,8,1.5,'2023-03-15',1,'Good',50,'2023-07-15',2500,2300,'2023-07-15 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(277,127,9,5.5,'2023-03-15',1,'Good',100,'2023-07-15',2500,2300,'2023-07-15 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(278,127,9,4,'2023-03-20',1,'Excellent',50,'2023-07-20',500,480,'2023-07-20 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(279,128,10,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500,2300,'2023-07-15 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(280,128,10,3.5,'2023-03-15',1,'Good',50,'2023-07-15',2500,2300,'2023-07-15 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd'),
(281,1,1,12,'2024-06-14',1,'fair',50,'2024-06-05',32,3,'2024-06-14 17:06:00','ok','Uganda','OK');
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
  `name` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `farmergroup`
--

LOCK TABLES `farmergroup` WRITE;
/*!40000 ALTER TABLE `farmergroup` DISABLE KEYS */;
INSERT INTO `farmergroup` VALUES
(1,'Farmers Cooperative Society','A cooperative society of farmers'),
(2,'Women Farmers Association','An association of women farmers'),
(3,'Young Farmers Group','A group of young farmers'),
(4,'HFZ Farmer Group','Ntebetebe Bweyogerere');
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
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forest`
--

LOCK TABLES `forest` WRITE;
/*!40000 ALTER TABLE `forest` DISABLE KEYS */;
INSERT INTO `forest` VALUES
(1,'Forest 1'),
(2,'Pine Forest'),
(3,'Small forest'),
(4,'Mw.Mulimba Forest Reserve');
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
  `longitude` float DEFAULT NULL,
  `latitude` float DEFAULT NULL,
  `owner_type` enum('forest','farmer') NOT NULL,
  `forest_id` int(11) DEFAULT NULL,
  `farmer_id` int(11) DEFAULT NULL,
  `district_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `district_id` (`district_id`),
  KEY `forest_id` (`forest_id`),
  KEY `farmer_id` (`farmer_id`),
  CONSTRAINT `point_ibfk_1` FOREIGN KEY (`district_id`) REFERENCES `district` (`id`),
  CONSTRAINT `point_ibfk_2` FOREIGN KEY (`forest_id`) REFERENCES `forest` (`id`),
  CONSTRAINT `point_ibfk_3` FOREIGN KEY (`farmer_id`) REFERENCES `farm` (`id`),
  CONSTRAINT `CONSTRAINT_1` CHECK (`owner_type` = 'forest' and `forest_id` is not null and `farmer_id` is null or `owner_type` = 'farmer' and `farmer_id` is not null and `forest_id` is null)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `point`
--

LOCK TABLES `point` WRITE;
/*!40000 ALTER TABLE `point` DISABLE KEYS */;
INSERT INTO `point` VALUES
(1,0.361753,32.6505,'forest',1,NULL,NULL),
(2,0.361352,32.6515,'forest',1,NULL,NULL),
(3,0.361054,32.6521,'forest',1,NULL,NULL),
(4,0.36098,32.6521,'forest',1,NULL,NULL),
(5,0.361107,32.6517,'forest',1,NULL,NULL),
(6,0.361494,32.6516,'forest',1,NULL,NULL),
(7,0.361352,32.6515,'forest',1,NULL,NULL),
(8,0.360711,32.6511,'forest',1,NULL,NULL),
(9,0.361618,32.6509,'forest',1,NULL,NULL),
(10,0.361575,32.651,'forest',1,NULL,NULL),
(11,0.360818,32.6515,'forest',1,NULL,NULL),
(12,0.361183,32.6512,'forest',1,NULL,NULL),
(13,0.361116,32.6527,'forest',1,NULL,NULL),
(14,0.36114,32.6524,'forest',1,NULL,NULL),
(15,0.36126,32.6508,'forest',1,NULL,NULL),
(16,0.361496,32.6508,'forest',1,NULL,NULL);
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
  `name` varchar(255) DEFAULT NULL,
  `grade` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producecategory`
--

LOCK TABLES `producecategory` WRITE;
/*!40000 ALTER TABLE `producecategory` DISABLE KEYS */;
INSERT INTO `producecategory` VALUES
(1,'Maize',1),
(2,'Beans',2),
(3,'Coffee',3),
(4,'Cassava',1),
(5,'Rice',2),
(6,'Bananas',3),
(7,'Coffee Arabica',5),
(8,'Coffee Robusta',4),
(9,'Soybean',5),
(10,'Tea',4);
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
  `district_id` int(11) DEFAULT NULL,
  `internal_id` int(11) DEFAULT NULL,
  `device` varchar(255) DEFAULT NULL,
  `owner` varchar(255) DEFAULT NULL,
  `nitrogen` float DEFAULT NULL,
  `phosphorus` float DEFAULT NULL,
  `potassium` float DEFAULT NULL,
  `ph` float DEFAULT NULL,
  `temperature` float DEFAULT NULL,
  `humidity` float DEFAULT NULL,
  `conductivity` float DEFAULT NULL,
  `signal_level` float DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `district_id` (`district_id`),
  CONSTRAINT `soildata_ibfk_1` FOREIGN KEY (`district_id`) REFERENCES `district` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=375 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `soildata`
--

LOCK TABLES `soildata` WRITE;
/*!40000 ALTER TABLE `soildata` DISABLE KEYS */;
INSERT INTO `soildata` VALUES
(1,1,1001,'Device1','Owner1',0.6,0.3,0.4,6.5,25,60,100,-70,'2024-02-01'),
(2,1,1002,'Device2','Owner2',0.4,0.2,0.5,6.8,26,62,110,-68,'2024-02-01'),
(3,1,1003,'Device3','Owner3',0.5,0.4,0.3,6.2,24.5,58,95,-72,'2024-02-01'),
(4,2,1004,'Device4','Owner4',0.7,0.5,0.4,6.6,25.5,61,105,-69,'2024-02-01'),
(5,2,1005,'Device5','Owner5',0.5,0.3,0.6,6.9,26.5,63,115,-67,'2024-02-01'),
(6,2,1006,'Device6','Owner6',0.6,0.4,0.5,6.3,24,57,90,-73,'2024-02-01'),
(7,3,1007,'Device7','Owner7',0.8,0.6,0.4,6.7,25,60,100,-70,'2024-02-01'),
(8,3,1008,'Device8','Owner8',0.4,0.3,0.7,7,26,62,110,-68,'2024-02-01'),
(9,3,1009,'Device9','Owner9',0.7,0.5,0.6,6.4,24.5,58,95,-72,'2024-02-01'),
(10,4,1010,'Device10','Owner10',0.5,0.4,0.3,6.8,25.5,61,105,-69,'2024-02-01'),
(11,4,1011,'Device11','Owner11',0.6,0.3,0.5,7.1,26.5,63,115,-67,'2024-02-01'),
(12,4,1012,'Device12','Owner12',0.8,0.7,0.6,6.5,24,57,90,-73,'2024-02-01'),
(13,5,1013,'Device13','Owner13',0.9,0.8,0.4,6.9,25,60,100,-70,'2024-02-01'),
(14,5,1014,'Device14','Owner14',0.6,0.5,0.7,7.2,26,62,110,-68,'2024-02-01'),
(15,5,1015,'Device15','Owner15',0.7,0.6,0.6,6.6,24.5,58,95,-72,'2024-02-01'),
(16,6,1016,'Device16','Owner16',0.5,0.4,0.3,7,25.5,61,105,-69,'2024-02-01'),
(17,6,1017,'Device17','Owner17',0.6,0.5,0.5,7.3,26.5,63,115,-67,'2024-02-01'),
(18,6,1018,'Device18','Owner18',0.8,0.7,0.6,6.7,24,57,90,-73,'2024-02-01'),
(19,7,1019,'Device19','Owner19',0.9,0.8,0.4,7.1,25,60,100,-70,'2024-02-01'),
(20,7,1020,'Device20','Owner20',0.6,0.5,0.8,7.4,26,62,110,-68,'2024-02-01'),
(21,7,1021,'Device21','Owner21',0.7,0.6,0.7,6.8,24.5,58,95,-72,'2024-02-01'),
(22,8,1022,'Device22','Owner22',0.5,0.4,0.4,7.2,25.5,61,105,-69,'2024-02-01'),
(23,8,1023,'Device23','Owner23',0.6,0.5,0.6,7.5,26.5,63,115,-67,'2024-02-01'),
(24,8,1024,'Device24','Owner24',0.8,0.7,0.5,6.9,24,57,90,-73,'2024-02-01'),
(25,9,1025,'Device25','Owner25',0.9,0.8,0.3,7.3,25,60,100,-70,'2024-02-01'),
(26,9,1026,'Device26','Owner26',0.6,0.5,0.9,7.6,26,62,110,-68,'2024-02-01'),
(27,9,1027,'Device27','Owner27',0.7,0.6,0.8,7,24.5,58,95,-72,'2024-02-01'),
(28,10,1028,'Device28','Owner28',0.5,0.4,0.5,7.4,25.5,61,105,-69,'2024-02-01'),
(29,10,1029,'Device29','Owner29',0.6,0.5,0.7,7.7,26.5,63,115,-67,'2024-02-01'),
(30,10,1030,'Device30','Owner30',0.8,0.7,0.4,7.1,24,57,90,-73,'2024-02-01'),
(31,11,1031,'Device31','Owner31',0.9,0.8,0.6,7.5,25,60,100,-70,'2024-02-01'),
(32,11,1032,'Device32','Owner32',0.6,0.5,0.8,7.8,26,62,110,-68,'2024-02-01'),
(33,11,1033,'Device33','Owner33',0.7,0.6,0.7,7.2,24.5,58,95,-72,'2024-02-01'),
(34,12,1034,'Device34','Owner34',0.5,0.4,0.4,7.6,25.5,61,105,-69,'2024-02-01'),
(35,12,1035,'Device35','Owner35',0.6,0.5,0.6,7.9,26.5,63,115,-67,'2024-02-01'),
(36,12,1036,'Device36','Owner36',0.8,0.7,0.5,7.3,24,57,90,-73,'2024-02-01'),
(37,13,1037,'Device37','Owner37',0.9,0.8,0.3,7.7,25,60,100,-70,'2024-02-01'),
(38,13,1038,'Device38','Owner38',0.6,0.5,0.9,8,26,62,110,-68,'2024-02-01'),
(39,13,1039,'Device39','Owner39',0.7,0.6,0.8,7.4,24.5,58,95,-72,'2024-02-01'),
(40,14,1040,'Device40','Owner40',0.5,0.4,0.5,7.8,25.5,61,105,-69,'2024-02-01'),
(41,14,1041,'Device41','Owner41',0.6,0.5,0.7,8.1,26.5,63,115,-67,'2024-02-01'),
(42,14,1042,'Device42','Owner42',0.8,0.7,0.4,7.5,24,57,90,-73,'2024-02-01'),
(43,15,1043,'Device43','Owner43',0.9,0.8,0.6,7.9,25,60,100,-70,'2024-02-01'),
(44,15,1044,'Device44','Owner44',0.6,0.5,0.8,8.2,26,62,110,-68,'2024-02-01'),
(45,15,1045,'Device45','Owner45',0.7,0.6,0.7,7.6,24.5,58,95,-72,'2024-02-01'),
(46,16,1046,'Device46','Owner46',0.5,0.4,0.4,8,25.5,61,105,-69,'2024-02-01'),
(47,16,1047,'Device47','Owner47',0.6,0.5,0.6,8.3,26.5,63,115,-67,'2024-02-01'),
(48,16,1048,'Device48','Owner48',0.8,0.7,0.5,7.7,24,57,90,-73,'2024-02-01'),
(49,17,1049,'Device49','Owner49',0.9,0.8,0.3,8.1,25,60,100,-70,'2024-02-01'),
(50,17,1050,'Device50','Owner50',0.6,0.5,0.9,8.4,26,62,110,-68,'2024-02-01'),
(51,18,1051,'Device51','Owner51',0.7,0.6,0.5,7.8,25.5,61,105,-69,'2024-02-01'),
(52,18,1052,'Device52','Owner52',0.8,0.7,0.7,8.1,26.5,63,115,-67,'2024-02-01'),
(53,18,1053,'Device53','Owner53',0.5,0.4,0.6,7.5,24,57,90,-73,'2024-02-01'),
(54,19,1054,'Device54','Owner54',0.9,0.8,0.4,8.2,25,60,100,-70,'2024-02-01'),
(55,19,1055,'Device55','Owner55',0.6,0.5,0.8,8.5,26,62,110,-68,'2024-02-01'),
(56,19,1056,'Device56','Owner56',0.7,0.6,0.7,7.9,24.5,58,95,-72,'2024-02-01'),
(57,20,1057,'Device57','Owner57',0.5,0.4,0.5,8.3,25.5,61,105,-69,'2024-02-01'),
(58,20,1058,'Device58','Owner58',0.6,0.5,0.7,8.6,26.5,63,115,-67,'2024-02-01'),
(59,20,1059,'Device59','Owner59',0.8,0.7,0.6,8,24,57,90,-73,'2024-02-01'),
(60,21,1060,'Device60','Owner60',0.9,0.8,0.3,8.4,25,60,100,-70,'2024-02-01'),
(61,21,1061,'Device61','Owner61',0.6,0.5,0.9,8.7,26,62,110,-68,'2024-02-01'),
(62,21,1062,'Device62','Owner62',0.7,0.6,0.8,8.1,24.5,58,95,-72,'2024-02-01'),
(63,22,1063,'Device63','Owner63',0.5,0.4,0.4,8.5,25.5,61,105,-69,'2024-02-01'),
(64,22,1064,'Device64','Owner64',0.6,0.5,0.6,8.8,26.5,63,115,-67,'2024-02-01'),
(65,22,1065,'Device65','Owner65',0.8,0.7,0.5,8.2,24,57,90,-73,'2024-02-01'),
(66,23,1066,'Device66','Owner66',0.9,0.8,0.6,8.6,25,60,100,-70,'2024-02-01'),
(67,23,1067,'Device67','Owner67',0.6,0.5,0.8,8.9,26,62,110,-68,'2024-02-01'),
(68,23,1068,'Device68','Owner68',0.7,0.6,0.7,8.3,24.5,58,95,-72,'2024-02-01'),
(69,24,1069,'Device69','Owner69',0.5,0.4,0.5,8.7,25.5,61,105,-69,'2024-02-01'),
(70,24,1070,'Device70','Owner70',0.6,0.5,0.7,9,26.5,63,115,-67,'2024-02-01'),
(71,24,1071,'Device71','Owner71',0.8,0.7,0.4,8.4,24,57,90,-73,'2024-02-01'),
(72,25,1072,'Device72','Owner72',0.9,0.8,0.6,8.8,25,60,100,-70,'2024-02-01'),
(73,25,1073,'Device73','Owner73',0.6,0.5,0.8,9.1,26,62,110,-68,'2024-02-01'),
(74,25,1074,'Device74','Owner74',0.7,0.6,0.7,8.5,24.5,58,95,-72,'2024-02-01'),
(75,26,1075,'Device75','Owner75',0.5,0.4,0.4,8.9,25.5,61,105,-69,'2024-02-01'),
(76,26,1076,'Device76','Owner76',0.6,0.5,0.6,9.2,26.5,63,115,-67,'2024-02-01'),
(77,26,1077,'Device77','Owner77',0.8,0.7,0.5,8.6,24,57,90,-73,'2024-02-01'),
(78,27,1078,'Device78','Owner78',0.9,0.8,0.3,9,25,60,100,-70,'2024-02-01'),
(79,27,1079,'Device79','Owner79',0.6,0.5,0.9,9.3,26,62,110,-68,'2024-02-01'),
(80,27,1080,'Device80','Owner80',0.7,0.6,0.8,8.7,24.5,58,95,-72,'2024-02-01'),
(81,28,1081,'Device81','Owner81',0.5,0.4,0.5,9.1,25.5,61,105,-69,'2024-02-01'),
(82,28,1082,'Device82','Owner82',0.6,0.5,0.7,9.4,26.5,63,115,-67,'2024-02-01'),
(83,28,1083,'Device83','Owner83',0.8,0.7,0.4,8.8,24,57,90,-73,'2024-02-01'),
(84,29,1084,'Device84','Owner84',0.9,0.8,0.6,9.2,25,60,100,-70,'2024-02-01'),
(85,29,1085,'Device85','Owner85',0.6,0.5,0.8,9.5,26,62,110,-68,'2024-02-01'),
(86,29,1086,'Device86','Owner86',0.7,0.6,0.7,8.9,24.5,58,95,-72,'2024-02-01'),
(87,30,1087,'Device87','Owner87',0.5,0.4,0.4,9.3,25.5,61,105,-69,'2024-02-01'),
(88,31,1090,'Device90','Owner90',0.9,0.8,0.6,9.4,25,60,100,-70,'2024-02-01'),
(89,31,1091,'Device91','Owner91',0.6,0.5,0.8,9.7,26,62,110,-68,'2024-02-01'),
(90,31,1092,'Device92','Owner92',0.7,0.6,0.7,9.1,24.5,58,95,-72,'2024-02-01'),
(91,32,1093,'Device93','Owner93',0.5,0.4,0.5,9.5,25.5,61,105,-69,'2024-02-01'),
(92,32,1094,'Device94','Owner94',0.6,0.5,0.7,9.8,26.5,63,115,-67,'2024-02-01'),
(93,32,1095,'Device95','Owner95',0.8,0.7,0.6,9.2,24,57,90,-73,'2024-02-01'),
(94,33,1096,'Device96','Owner96',0.9,0.8,0.3,9.6,25,60,100,-70,'2024-02-01'),
(95,33,1097,'Device97','Owner97',0.6,0.5,0.9,9.9,26,62,110,-68,'2024-02-01'),
(96,33,1098,'Device98','Owner98',0.7,0.6,0.8,9.3,24.5,58,95,-72,'2024-02-01'),
(97,34,1099,'Device99','Owner99',0.5,0.4,0.4,9.7,25.5,61,105,-69,'2024-02-01'),
(98,34,1100,'Device100','Owner100',0.6,0.5,0.6,10,26.5,63,115,-67,'2024-02-01'),
(99,34,1101,'Device101','Owner101',0.8,0.7,0.5,9.4,24,57,90,-73,'2024-02-01'),
(100,35,1102,'Device102','Owner102',0.9,0.8,0.6,9.8,25,60,100,-70,'2024-02-01'),
(101,35,1103,'Device103','Owner103',0.6,0.5,0.8,10.1,26,62,110,-68,'2024-02-01'),
(102,35,1104,'Device104','Owner104',0.7,0.6,0.7,9.5,24.5,58,95,-72,'2024-02-01'),
(103,36,1105,'Device105','Owner105',0.5,0.4,0.5,9.9,25.5,61,105,-69,'2024-02-01'),
(104,36,1106,'Device106','Owner106',0.6,0.5,0.7,10.2,26.5,63,115,-67,'2024-02-01'),
(105,36,1107,'Device107','Owner107',0.8,0.7,0.6,9.6,24,57,90,-73,'2024-02-01'),
(106,37,1108,'Device108','Owner108',0.9,0.8,0.3,10,25,60,100,-70,'2024-02-01'),
(107,37,1109,'Device109','Owner109',0.6,0.5,0.9,10.3,26,62,110,-68,'2024-02-01'),
(108,37,1110,'Device110','Owner110',0.7,0.6,0.8,9.7,24.5,58,95,-72,'2024-02-01'),
(109,38,1111,'Device111','Owner111',0.5,0.4,0.4,10.1,25.5,61,105,-69,'2024-02-01'),
(110,38,1112,'Device112','Owner112',0.6,0.5,0.6,10.4,26.5,63,115,-67,'2024-02-01'),
(111,38,1113,'Device113','Owner113',0.8,0.7,0.5,9.8,24,57,90,-73,'2024-02-01'),
(112,39,1114,'Device114','Owner114',0.9,0.8,0.6,10.2,25,60,100,-70,'2024-02-01'),
(113,39,1115,'Device115','Owner115',0.6,0.5,0.8,10.5,26,62,110,-68,'2024-02-01'),
(114,39,1116,'Device116','Owner116',0.7,0.6,0.7,9.9,24.5,58,95,-72,'2024-02-01'),
(115,40,1117,'Device117','Owner117',0.5,0.4,0.5,10.3,25.5,61,105,-69,'2024-02-01'),
(116,40,1118,'Device118','Owner118',0.6,0.5,0.7,10.6,26.5,63,115,-67,'2024-02-01'),
(117,40,1119,'Device119','Owner119',0.8,0.7,0.6,10,24,57,90,-73,'2024-02-01'),
(118,41,1120,'Device120','Owner120',0.9,0.8,0.3,10.4,25,60,100,-70,'2024-02-01'),
(119,41,1121,'Device121','Owner121',0.6,0.5,0.9,10.7,26,62,110,-68,'2024-02-01'),
(120,41,1122,'Device122','Owner122',0.7,0.6,0.8,10.1,24.5,58,95,-72,'2024-02-01'),
(121,42,1123,'Device123','Owner123',0.5,0.4,0.4,10.5,25.5,61,105,-69,'2024-02-01'),
(122,42,1124,'Device124','Owner124',0.6,0.5,0.6,10.8,26.5,63,115,-67,'2024-02-01'),
(123,42,1125,'Device125','Owner125',0.8,0.7,0.5,10.2,24,57,90,-73,'2024-02-01'),
(124,43,1126,'Device126','Owner126',0.9,0.8,0.6,10.6,25,60,100,-70,'2024-02-01'),
(125,43,1127,'Device127','Owner127',0.6,0.5,0.8,10.9,26,62,110,-68,'2024-02-01'),
(126,43,1128,'Device128','Owner128',0.7,0.6,0.7,10.3,24.5,58,95,-72,'2024-02-01'),
(127,44,1129,'Device129','Owner129',0.5,0.4,0.5,10.7,25.5,61,105,-69,'2024-02-01'),
(128,44,1130,'Device130','Owner130',0.6,0.5,0.7,11,26.5,63,115,-67,'2024-02-01'),
(129,44,1131,'Device131','Owner131',0.8,0.7,0.6,10.4,24,57,90,-73,'2024-02-01'),
(130,45,1132,'Device132','Owner132',0.9,0.8,0.3,10.8,25,60,100,-70,'2024-02-01'),
(131,45,1133,'Device133','Owner133',0.6,0.5,0.9,11.1,26,62,110,-68,'2024-02-01'),
(132,45,1134,'Device134','Owner134',0.7,0.6,0.8,10.5,24.5,58,95,-72,'2024-02-01'),
(133,46,1135,'Device135','Owner135',0.5,0.4,0.4,10.9,25.5,61,105,-69,'2024-02-01'),
(134,46,1136,'Device136','Owner136',0.6,0.5,0.6,11.2,26.5,63,115,-67,'2024-02-01'),
(135,46,1137,'Device137','Owner137',0.8,0.7,0.5,10.6,24,57,90,-73,'2024-02-01'),
(136,47,1138,'Device138','Owner138',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(137,47,1139,'Device139','Owner139',0.6,0.5,0.8,11.3,26,62,110,-68,'2024-02-01'),
(138,47,1140,'Device140','Owner140',0.7,0.6,0.7,10.7,24.5,58,95,-72,'2024-02-01'),
(139,48,1141,'Device141','Owner141',0.5,0.4,0.5,11.1,25.5,61,105,-69,'2024-02-01'),
(140,48,1142,'Device142','Owner142',0.6,0.5,0.7,11.4,26.5,63,115,-67,'2024-02-01'),
(141,48,1143,'Device143','Owner143',0.8,0.7,0.6,10.8,24,57,90,-73,'2024-02-01'),
(142,49,1144,'Device144','Owner144',0.9,0.8,0.3,11.2,25,60,100,-70,'2024-02-01'),
(143,49,1145,'Device145','Owner145',0.6,0.5,0.9,11.5,26,62,110,-68,'2024-02-01'),
(144,49,1146,'Device146','Owner146',0.7,0.6,0.8,10.9,24.5,58,95,-72,'2024-02-01'),
(145,50,1147,'Device147','Owner147',0.5,0.4,0.4,11.3,25.5,61,105,-69,'2024-02-01'),
(146,50,1148,'Device148','Owner148',0.6,0.5,0.6,11.6,26.5,63,115,-67,'2024-02-01'),
(147,50,1149,'Device149','Owner149',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(148,51,1150,'Device150','Owner150',0.9,0.8,0.6,11.4,25,60,100,-70,'2024-02-01'),
(149,52,1151,'Device151','Owner151',0.7,0.6,0.7,11.7,26,62,110,-68,'2024-02-01'),
(150,52,1152,'Device152','Owner152',0.8,0.7,0.6,11.1,24.5,58,95,-72,'2024-02-01'),
(151,52,1153,'Device153','Owner153',0.5,0.4,0.5,11.5,25.5,61,105,-69,'2024-02-01'),
(152,53,1154,'Device154','Owner154',0.6,0.5,0.7,11.8,26.5,63,115,-67,'2024-02-01'),
(153,53,1155,'Device155','Owner155',0.8,0.7,0.6,11.2,24,57,90,-73,'2024-02-01'),
(154,53,1156,'Device156','Owner156',0.9,0.8,0.5,11.6,25,60,100,-70,'2024-02-01'),
(155,54,1157,'Device157','Owner157',0.6,0.5,0.8,11.9,26,62,110,-68,'2024-02-01'),
(156,54,1158,'Device158','Owner158',0.7,0.6,0.7,11.3,24.5,58,95,-72,'2024-02-01'),
(157,54,1159,'Device159','Owner159',0.5,0.4,0.5,11.7,25.5,61,105,-69,'2024-02-01'),
(158,55,1160,'Device160','Owner160',0.6,0.5,0.7,12,26.5,63,115,-67,'2024-02-01'),
(159,55,1161,'Device161','Owner161',0.8,0.7,0.6,11.4,24,57,90,-73,'2024-02-01'),
(160,55,1162,'Device162','Owner162',0.9,0.8,0.5,11.8,25,60,100,-70,'2024-02-01'),
(161,56,1163,'Device163','Owner163',0.6,0.5,0.8,12.1,26,62,110,-68,'2024-02-01'),
(162,56,1164,'Device164','Owner164',0.7,0.6,0.7,11.5,24.5,58,95,-72,'2024-02-01'),
(163,56,1165,'Device165','Owner165',0.5,0.4,0.5,11.9,25.5,61,105,-69,'2024-02-01'),
(164,57,1166,'Device166','Owner166',0.6,0.5,0.7,12.2,26.5,63,115,-67,'2024-02-01'),
(165,57,1167,'Device167','Owner167',0.8,0.7,0.6,11.6,24,57,90,-73,'2024-02-01'),
(166,57,1168,'Device168','Owner168',0.9,0.8,0.5,12,25,60,100,-70,'2024-02-01'),
(167,58,1169,'Device169','Owner169',0.6,0.5,0.8,12.3,26,62,110,-68,'2024-02-01'),
(168,58,1170,'Device170','Owner170',0.7,0.6,0.7,11.7,24.5,58,95,-72,'2024-02-01'),
(169,58,1171,'Device171','Owner171',0.5,0.4,0.5,12.1,25.5,61,105,-69,'2024-02-01'),
(170,59,1172,'Device172','Owner172',0.6,0.5,0.7,12.4,26.5,63,115,-67,'2024-02-01'),
(171,59,1173,'Device173','Owner173',0.8,0.7,0.6,11.8,24,57,90,-73,'2024-02-01'),
(172,59,1174,'Device174','Owner174',0.9,0.8,0.5,12.2,25,60,100,-70,'2024-02-01'),
(173,60,1175,'Device175','Owner175',0.6,0.5,0.8,12.5,26,62,110,-68,'2024-02-01'),
(174,60,1176,'Device176','Owner176',0.7,0.6,0.7,11.9,24.5,58,95,-72,'2024-02-01'),
(175,60,1177,'Device177','Owner177',0.5,0.4,0.5,12.3,25.5,61,105,-69,'2024-02-01'),
(176,61,1178,'Device178','Owner178',0.6,0.5,0.7,12.6,26.5,63,115,-67,'2024-02-01'),
(177,61,1179,'Device179','Owner179',0.8,0.7,0.6,12,24,57,90,-73,'2024-02-01'),
(178,61,1180,'Device180','Owner180',0.9,0.8,0.5,12.4,25,60,100,-70,'2024-02-01'),
(179,62,1181,'Device181','Owner181',0.6,0.5,0.8,12.7,26,62,110,-68,'2024-02-01'),
(180,62,1182,'Device182','Owner182',0.7,0.6,0.7,12.1,24.5,58,95,-72,'2024-02-01'),
(181,62,1183,'Device183','Owner183',0.5,0.4,0.5,12.5,25.5,61,105,-69,'2024-02-01'),
(182,63,1184,'Device184','Owner184',0.6,0.5,0.7,12.8,26.5,63,115,-67,'2024-02-01'),
(183,63,1185,'Device185','Owner185',0.8,0.7,0.6,12.2,24,57,90,-73,'2024-02-01'),
(184,63,1186,'Device186','Owner186',0.9,0.8,0.5,12.6,25,60,100,-70,'2024-02-01'),
(185,64,1187,'Device187','Owner187',0.6,0.5,0.8,12.9,26,62,110,-68,'2024-02-01'),
(186,64,1188,'Device188','Owner188',0.7,0.6,0.7,12.3,24.5,58,95,-72,'2024-02-01'),
(187,64,1189,'Device189','Owner189',0.5,0.4,0.5,12.7,25.5,61,105,-69,'2024-02-01'),
(188,65,1190,'Device190','Owner190',0.6,0.5,0.7,13,26.5,63,115,-67,'2024-02-01'),
(189,65,1191,'Device191','Owner191',0.8,0.7,0.6,12.4,24,57,90,-73,'2024-02-01'),
(190,65,1192,'Device192','Owner192',0.9,0.8,0.5,12.8,25,60,100,-70,'2024-02-01'),
(191,66,1193,'Device193','Owner193',0.6,0.5,0.8,13.1,26,62,110,-68,'2024-02-01'),
(192,66,1194,'Device194','Owner194',0.7,0.6,0.7,12.5,24.5,58,95,-72,'2024-02-01'),
(193,66,1195,'Device195','Owner195',0.5,0.4,0.5,12.9,25.5,61,105,-69,'2024-02-01'),
(194,67,1196,'Device196','Owner196',0.6,0.5,0.7,13.2,26.5,63,115,-67,'2024-02-01'),
(195,67,1197,'Device197','Owner197',0.8,0.7,0.6,12.6,24,57,90,-73,'2024-02-01'),
(196,67,1198,'Device198','Owner198',0.9,0.8,0.5,13,25,60,100,-70,'2024-02-01'),
(197,68,1199,'Device199','Owner199',0.6,0.5,0.8,13.3,26,62,110,-68,'2024-02-01'),
(198,68,1200,'Device200','Owner200',0.7,0.6,0.7,12.7,24.5,58,95,-72,'2024-02-01'),
(199,69,1201,'Device201','Owner201',0.5,0.4,0.5,13.1,25.5,61,105,-69,'2024-02-01'),
(200,69,1202,'Device202','Owner202',0.6,0.5,0.6,13.4,26.5,63,115,-67,'2024-02-01'),
(201,69,1203,'Device203','Owner203',0.8,0.7,0.5,12.8,24,57,90,-73,'2024-02-01'),
(202,70,1204,'Device204','Owner204',0.9,0.8,0.6,13.2,25,60,100,-70,'2024-02-01'),
(203,70,1205,'Device205','Owner205',0.6,0.5,0.8,13.5,26,62,110,-68,'2024-02-01'),
(204,70,1206,'Device206','Owner206',0.7,0.6,0.7,12.9,24.5,58,95,-72,'2024-02-01'),
(205,71,1207,'Device207','Owner207',0.5,0.4,0.5,13.3,25.5,61,105,-69,'2024-02-01'),
(206,71,1208,'Device208','Owner208',0.6,0.5,0.6,13.6,26.5,63,115,-67,'2024-02-01'),
(207,71,1209,'Device209','Owner209',0.8,0.7,0.5,13,24,57,90,-73,'2024-02-01'),
(208,72,1210,'Device210','Owner210',0.9,0.8,0.6,13.4,25,60,100,-70,'2024-02-01'),
(209,72,1211,'Device211','Owner211',0.6,0.5,0.8,13.7,26,62,110,-68,'2024-02-01'),
(210,72,1212,'Device212','Owner212',0.7,0.6,0.7,13.1,24.5,58,95,-72,'2024-02-01'),
(211,73,1213,'Device213','Owner213',0.5,0.4,0.5,13.5,25.5,61,105,-69,'2024-02-01'),
(212,73,1214,'Device214','Owner214',0.6,0.5,0.6,13.8,26.5,63,115,-67,'2024-02-01'),
(213,73,1215,'Device215','Owner215',0.8,0.7,0.5,13.2,24,57,90,-73,'2024-02-01'),
(214,74,1216,'Device216','Owner216',0.9,0.8,0.6,13.6,25,60,100,-70,'2024-02-01'),
(215,74,1217,'Device217','Owner217',0.6,0.5,0.8,13.9,26,62,110,-68,'2024-02-01'),
(216,74,1218,'Device218','Owner218',0.7,0.6,0.7,13.3,24.5,58,95,-72,'2024-02-01'),
(217,75,1219,'Device219','Owner219',0.5,0.4,0.5,13.7,25.5,61,105,-69,'2024-02-01'),
(218,75,1220,'Device220','Owner220',0.6,0.5,0.6,14,26.5,63,115,-67,'2024-02-01'),
(219,75,1221,'Device221','Owner221',0.8,0.7,0.5,13.4,24,57,90,-73,'2024-02-01'),
(220,76,1222,'Device222','Owner222',0.9,0.8,0.6,13.8,25,60,100,-70,'2024-02-01'),
(221,76,1223,'Device223','Owner223',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(222,76,1224,'Device224','Owner224',0.7,0.6,0.7,13.5,24.5,58,95,-72,'2024-02-01'),
(223,77,1225,'Device225','Owner225',0.5,0.4,0.5,13.9,25.5,61,105,-69,'2024-02-01'),
(224,77,1226,'Device226','Owner226',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(225,77,1227,'Device227','Owner227',0.8,0.7,0.5,13.6,24,57,90,-73,'2024-02-01'),
(226,78,1228,'Device228','Owner228',0.9,0.8,0.6,14,25,60,100,-70,'2024-02-01'),
(227,78,1229,'Device229','Owner229',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(228,78,1230,'Device230','Owner230',0.7,0.6,0.7,13.7,24.5,58,95,-72,'2024-02-01'),
(229,79,1231,'Device231','Owner231',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(230,79,1232,'Device232','Owner232',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(231,79,1233,'Device233','Owner233',0.8,0.7,0.5,13.8,24,57,90,-73,'2024-02-01'),
(232,80,1234,'Device234','Owner234',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(233,80,1235,'Device235','Owner235',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(234,80,1236,'Device236','Owner236',0.7,0.6,0.7,13.9,24.5,58,95,-72,'2024-02-01'),
(235,81,1237,'Device237','Owner237',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(236,81,1238,'Device238','Owner238',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(237,81,1239,'Device239','Owner239',0.8,0.7,0.5,14,24,57,90,-73,'2024-02-01'),
(238,82,1240,'Device240','Owner240',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(239,82,1241,'Device241','Owner241',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(240,82,1242,'Device242','Owner242',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(241,83,1243,'Device243','Owner243',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(242,83,1244,'Device244','Owner244',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(243,83,1245,'Device245','Owner245',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(244,84,1246,'Device246','Owner246',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(245,84,1247,'Device247','Owner247',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(246,84,1248,'Device248','Owner248',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(247,85,1249,'Device249','Owner249',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(248,85,1250,'Device250','Owner250',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(249,85,1251,'Device251','Owner251',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(250,86,1252,'Device252','Owner252',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(251,86,1253,'Device253','Owner253',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(252,86,1254,'Device254','Owner254',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(253,87,1255,'Device255','Owner255',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(254,87,1256,'Device256','Owner256',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(255,87,1257,'Device257','Owner257',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(256,88,1258,'Device258','Owner258',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(257,88,1259,'Device259','Owner259',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(258,88,1260,'Device260','Owner260',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(259,89,1261,'Device261','Owner261',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(260,89,1262,'Device262','Owner262',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(261,89,1263,'Device263','Owner263',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(262,90,1264,'Device264','Owner264',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(263,90,1265,'Device265','Owner265',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(264,90,1266,'Device266','Owner266',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(265,91,1267,'Device267','Owner267',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(266,91,1268,'Device268','Owner268',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(267,91,1269,'Device269','Owner269',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(268,92,1270,'Device270','Owner270',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(269,92,1271,'Device271','Owner271',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(270,92,1272,'Device272','Owner272',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(271,93,1273,'Device273','Owner273',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(272,93,1274,'Device274','Owner274',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(273,93,1275,'Device275','Owner275',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(274,94,1276,'Device276','Owner276',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(275,94,1277,'Device277','Owner277',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(276,94,1278,'Device278','Owner278',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(277,95,1279,'Device279','Owner279',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(278,95,1280,'Device280','Owner280',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(279,95,1281,'Device281','Owner281',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(280,96,1282,'Device282','Owner282',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(281,96,1283,'Device283','Owner283',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(282,96,1284,'Device284','Owner284',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(283,97,1285,'Device285','Owner285',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(284,97,1286,'Device286','Owner286',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(285,97,1287,'Device287','Owner287',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(286,98,1288,'Device288','Owner288',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(287,98,1289,'Device289','Owner289',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(288,98,1290,'Device290','Owner290',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(289,99,1291,'Device291','Owner291',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(290,99,1292,'Device292','Owner292',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(291,99,1293,'Device293','Owner293',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(292,100,1294,'Device294','Owner294',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(293,100,1295,'Device295','Owner295',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(294,100,1296,'Device296','Owner296',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(295,101,1297,'Device297','Owner297',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(296,101,1298,'Device298','Owner298',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(297,101,1299,'Device299','Owner299',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(298,102,1300,'Device300','Owner300',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(299,102,1301,'Device301','Owner301',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(300,102,1302,'Device302','Owner302',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(301,103,1303,'Device303','Owner303',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(302,103,1304,'Device304','Owner304',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(303,103,1305,'Device305','Owner305',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(304,104,1306,'Device306','Owner306',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(305,104,1307,'Device307','Owner307',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(306,104,1308,'Device308','Owner308',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(307,105,1309,'Device309','Owner309',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(308,105,1310,'Device310','Owner310',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(309,105,1311,'Device311','Owner311',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(310,106,1312,'Device312','Owner312',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(311,106,1313,'Device313','Owner313',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(312,106,1314,'Device314','Owner314',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(313,107,1315,'Device315','Owner315',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(314,107,1316,'Device316','Owner316',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(315,107,1317,'Device317','Owner317',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(316,108,1318,'Device318','Owner318',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(317,108,1319,'Device319','Owner319',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(318,108,1320,'Device320','Owner320',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(319,109,1321,'Device321','Owner321',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(320,109,1322,'Device322','Owner322',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(321,109,1323,'Device323','Owner323',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(322,110,1324,'Device324','Owner324',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(323,110,1325,'Device325','Owner325',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(324,110,1326,'Device326','Owner326',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(325,111,1327,'Device327','Owner327',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(326,111,1328,'Device328','Owner328',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(327,111,1329,'Device329','Owner329',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(328,112,1330,'Device330','Owner330',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(329,112,1331,'Device331','Owner331',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(330,112,1332,'Device332','Owner332',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(331,113,1333,'Device333','Owner333',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(332,113,1334,'Device334','Owner334',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(333,113,1335,'Device335','Owner335',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(334,114,1336,'Device336','Owner336',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(335,114,1337,'Device337','Owner337',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(336,114,1338,'Device338','Owner338',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(337,115,1339,'Device339','Owner339',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(338,115,1340,'Device340','Owner340',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(339,115,1341,'Device341','Owner341',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(340,116,1342,'Device342','Owner342',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(341,116,1343,'Device343','Owner343',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(342,116,1344,'Device344','Owner344',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(343,117,1345,'Device345','Owner345',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(344,117,1346,'Device346','Owner346',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(345,117,1347,'Device347','Owner347',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(346,118,1348,'Device348','Owner348',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(347,118,1349,'Device349','Owner349',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(348,118,1350,'Device350','Owner350',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(349,119,1351,'Device351','Owner351',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(350,119,1352,'Device352','Owner352',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(351,119,1353,'Device353','Owner353',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(352,120,1354,'Device354','Owner354',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(353,120,1355,'Device355','Owner355',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(354,120,1356,'Device356','Owner356',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(355,121,1357,'Device357','Owner357',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(356,121,1358,'Device358','Owner358',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(357,121,1359,'Device359','Owner359',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(358,122,1360,'Device360','Owner360',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(359,122,1361,'Device361','Owner361',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(360,122,1362,'Device362','Owner362',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(361,123,1363,'Device363','Owner363',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(362,123,1364,'Device364','Owner364',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(363,123,1365,'Device365','Owner365',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(364,124,1366,'Device366','Owner366',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(365,124,1367,'Device367','Owner367',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(366,124,1368,'Device368','Owner368',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(367,125,1369,'Device369','Owner369',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(368,125,1370,'Device370','Owner370',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01'),
(369,125,1371,'Device371','Owner371',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01'),
(370,16,1372,'Device372','Owner372',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01'),
(371,16,1373,'Device373','Owner373',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01'),
(372,12,1374,'Device374','Owner374',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01'),
(373,12,1375,'Device375','Owner375',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01'),
(374,12,1376,'Device376','Owner376',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES
(2,'Admin','admin@admin.admin','pbkdf2:sha256:600000$us9tk0a4zUPQBs8f$06f2ace9bba750792ab34515795ebc53a5fce96d450c9fac0f23ab90e14effb5','0303030303','admin',1),
(3,'sasakawa1','sasakawa@agriyields.com','pbkdf2:sha256:600000$r0UgnJ4CsgYN4aLf$6a8419cd98bc35cb75c65296fd429224566d83546cbe3fbeadf00513e30e7987','25678123456','farmer',0),
(4,'sasakawa2','sasakawa2@agriyields.com','pbkdf2:sha256:600000$Tmcux0RqTrN5zp8X$fbe3541775decbac4b202e2ae053f6f1a4eb694c0a82ed529366fb9471463993','0756321567','farmer',0),
(5,'sasakawa3','sasakawa3@agriyields.com','pbkdf2:sha256:600000$4B971ALhpVzQkwx1$5cc0d10b3602b353187f9c06473af3c08ff693133152ddba462d03fb2fc2a67e','074532890','farmer',0);
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

-- Dump completed on 2024-06-11  0:18:47
