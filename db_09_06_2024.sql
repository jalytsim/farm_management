
DROP TABLE IF EXISTS crop;

CREATE TABLE crop (
  id int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  weight float DEFAULT NULL,
  category_id int DEFAULT NULL,
  PRIMARY KEY (id),
  KEY category_id (category_id),
  CONSTRAINT crop_ibfk_1 FOREIGN KEY (category_id) REFERENCES producecategory (id)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO crop (id, name, weight, category_id) VALUES (1,'Maize',50,1);
INSERT INTO crop (id, name, weight, category_id) VALUES (2,'Beans',10,2);
INSERT INTO crop (id, name, weight, category_id) VALUES (3,'Coffee',25,3);
INSERT INTO crop (id, name, weight, category_id) VALUES (4,'Cassava',30,4);
INSERT INTO crop (id, name, weight, category_id) VALUES (5,'Rice',20,5);
INSERT INTO crop (id, name, weight, category_id) VALUES (6,'Bananas',15,6);

DROP TABLE IF EXISTS district;
CREATE TABLE district (
  id int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  region varchar(255) DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=126 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


INSERT INTO district (id, name, region) VALUES (1,'Abim','North');
INSERT INTO district (id, name, region) VALUES (2,'Adjumani','North');
INSERT INTO district (id, name, region) VALUES (3,'Agago','North');
INSERT INTO district (id, name, region) VALUES (4,'Alebtong','North');
INSERT INTO district (id, name, region) VALUES (5,'Amolatar','North');
INSERT INTO district (id, name, region) VALUES (6,'Amudat','East');
INSERT INTO district (id, name, region) VALUES (7,'Amuria','East');
INSERT INTO district (id, name, region) VALUES (8,'Amuru','North');
INSERT INTO district (id, name, region) VALUES (9,'Apac','North');
INSERT INTO district (id, name, region) VALUES (10,'Arua','North');
INSERT INTO district (id, name, region) VALUES (11,'Budaka','East');
INSERT INTO district (id, name, region) VALUES (12,'Bududa','East');
INSERT INTO district (id, name, region) VALUES (13,'Bugiri','East');
INSERT INTO district (id, name, region) VALUES (14,'Bugweri','East');
INSERT INTO district (id, name, region) VALUES (15,'Buikwe','Central');
INSERT INTO district (id, name, region) VALUES (16,'Bukedea','East');
INSERT INTO district (id, name, region) VALUES (17,'Bukomansimbi','Central');
INSERT INTO district (id, name, region) VALUES (18,'Bukwo','East');
INSERT INTO district (id, name, region) VALUES (19,'Bulambuli','East');
INSERT INTO district (id, name, region) VALUES (20,'Buliisa','West');
INSERT INTO district (id, name, region) VALUES (21,'Bundibugyo','West');
INSERT INTO district (id, name, region) VALUES (22,'Bunyangabu','West');
INSERT INTO district (id, name, region) VALUES (23,'Bushenyi','West');
INSERT INTO district (id, name, region) VALUES (24,'Busia','East');
INSERT INTO district (id, name, region) VALUES (25,'Butaleja','East');
INSERT INTO district (id, name, region) VALUES (26,'Butambala','Central');
INSERT INTO district (id, name, region) VALUES (27,'Butebo','East');
INSERT INTO district (id, name, region) VALUES (28,'Buvuma','Central');
INSERT INTO district (id, name, region) VALUES (29,'Buyende','East');
INSERT INTO district (id, name, region) VALUES (30,'Dokolo','North');
INSERT INTO district (id, name, region) VALUES (31,'Gomba','Central');
INSERT INTO district (id, name, region) VALUES (32,'Gulu','North');
INSERT INTO district (id, name, region) VALUES (33,'Hoima','West');
INSERT INTO district (id, name, region) VALUES (34,'Ibanda','West');
INSERT INTO district (id, name, region) VALUES (35,'Iganga','East');
INSERT INTO district (id, name, region) VALUES (36,'Isingiro','West');
INSERT INTO district (id, name, region) VALUES (37,'Jinja','East');
INSERT INTO district (id, name, region) VALUES (38,'Kaabong','North');
INSERT INTO district (id, name, region) VALUES (39,'Kabale','West');
INSERT INTO district (id, name, region) VALUES (40,'Kabarole','West');
INSERT INTO district (id, name, region) VALUES (41,'Kaberamaido','East');
INSERT INTO district (id, name, region) VALUES (42,'Kagadi','West');
INSERT INTO district (id, name, region) VALUES (43,'Kagwara','West');
INSERT INTO district (id, name, region) VALUES (44,'Kalaki','East');
INSERT INTO district (id, name, region) VALUES (45,'Kalangala','Central');
INSERT INTO district (id, name, region) VALUES (46,'Kaliro','East');
INSERT INTO district (id, name, region) VALUES (47,'Kalungu','Central');
INSERT INTO district (id, name, region) VALUES (48,'Kampala','Central');
INSERT INTO district (id, name, region) VALUES (49,'Kamuli','East');
INSERT INTO district (id, name, region) VALUES (50,'Kamwenge','West');
INSERT INTO district (id, name, region) VALUES (51,'Kanungu','West');
INSERT INTO district (id, name, region) VALUES (52,'Kapchorwa','East');
INSERT INTO district (id, name, region) VALUES (53,'Kapelebyong','East');
INSERT INTO district (id, name, region) VALUES (54,'Kasese','West');
INSERT INTO district (id, name, region) VALUES (55,'Katakwi','East');
INSERT INTO district (id, name, region) VALUES (56,'Katerera','West');
INSERT INTO district (id, name, region) VALUES (57,'Kayunga','Central');
INSERT INTO district (id, name, region) VALUES (58,'Kibaale','West');
INSERT INTO district (id, name, region) VALUES (59,'Kiboga','Central');
INSERT INTO district (id, name, region) VALUES (60,'Kibuku','East');
INSERT INTO district (id, name, region) VALUES (61,'Kiruhura','West');
INSERT INTO district (id, name, region) VALUES (62,'Kiryandongo','West');
INSERT INTO district (id, name, region) VALUES (63,'Kisoro','West');
INSERT INTO district (id, name, region) VALUES (64,'Kitagwenda','West');
INSERT INTO district (id, name, region) VALUES (65,'Kitgum','North');
INSERT INTO district (id, name, region) VALUES (66,'Koboko','West');
INSERT INTO district (id, name, region) VALUES (67,'Kole','North');
INSERT INTO district (id, name, region) VALUES (68,'Kotido','North');
INSERT INTO district (id, name, region) VALUES (69,'Kumi','East');
INSERT INTO district (id, name, region) VALUES (70,'Kwania','East');
INSERT INTO district (id, name, region) VALUES (71,'Kween','East');
INSERT INTO district (id, name, region) VALUES (72,'Kyankwanzi','Central');
INSERT INTO district (id, name, region) VALUES (73,'Kyegegwa','West');
INSERT INTO district (id, name, region) VALUES (74,'Kyenjojo','West');
INSERT INTO district (id, name, region) VALUES (75,'Kyotera','Central');
INSERT INTO district (id, name, region) VALUES (76,'Lamwo','North');
INSERT INTO district (id, name, region) VALUES (77,'Lira','North');
INSERT INTO district (id, name, region) VALUES (78,'Luuka','East');
INSERT INTO district (id, name, region) VALUES (79,'Luwero','Central');
INSERT INTO district (id, name, region) VALUES (80,'Lwengo','Central');
INSERT INTO district (id, name, region) VALUES (81,'Lyantonde','Central');
INSERT INTO district (id, name, region) VALUES (82,'Manafwa','East');
INSERT INTO district (id, name, region) VALUES (83,'Maracha','West');
INSERT INTO district (id, name, region) VALUES (84,'Masaka','Central');
INSERT INTO district (id, name, region) VALUES (85,'Masindi','West');
INSERT INTO district (id, name, region) VALUES (86,'Mayuge','East');
INSERT INTO district (id, name, region) VALUES (87,'Mbale','East');
INSERT INTO district (id, name, region) VALUES (88,'Mbarara','West');
INSERT INTO district (id, name, region) VALUES (89,'Mitooma','West');
INSERT INTO district (id, name, region) VALUES (90,'Mityana','Central');
INSERT INTO district (id, name, region) VALUES (91,'Moroto','North');
INSERT INTO district (id, name, region) VALUES (92,'Moyo','North');
INSERT INTO district (id, name, region) VALUES (93,'Mpigi','Central');
INSERT INTO district (id, name, region) VALUES (94,'Mubende','Central');
INSERT INTO district (id, name, region) VALUES (95,'Mukono','Central');
INSERT INTO district (id, name, region) VALUES (96,'Nakapiripirit','North');
INSERT INTO district (id, name, region) VALUES (97,'Nakaseke','Central');
INSERT INTO district (id, name, region) VALUES (98,'Nakasongola','Central');
INSERT INTO district (id, name, region) VALUES (99,'Namayingo','East');
INSERT INTO district (id, name, region) VALUES (100,'Namisindwa','East');
INSERT INTO district (id, name, region) VALUES (101,'Namutumba','East');
INSERT INTO district (id, name, region) VALUES (102,'Napak','North');
INSERT INTO district (id, name, region) VALUES (103,'Nebbi','West');
INSERT INTO district (id, name, region) VALUES (104,'Ngora','East');
INSERT INTO district (id, name, region) VALUES (105,'Ntoroko','West');
INSERT INTO district (id, name, region) VALUES (106,'Ntungamo','West');
INSERT INTO district (id, name, region) VALUES (107,'Nwoya','North');
INSERT INTO district (id, name, region) VALUES (108,'Otuke','North');
INSERT INTO district (id, name, region) VALUES (109,'Oyam','North');
INSERT INTO district (id, name, region) VALUES (110,'Pader','North');
INSERT INTO district (id, name, region) VALUES (111,'Pallisa','East');
INSERT INTO district (id, name, region) VALUES (112,'Rakai','Central');
INSERT INTO district (id, name, region) VALUES (113,'Rubanda','West');
INSERT INTO district (id, name, region) VALUES (114,'Rubirizi','West');
INSERT INTO district (id, name, region) VALUES (115,'Rukiga','West');
INSERT INTO district (id, name, region) VALUES (116,'Rukungiri','West');
INSERT INTO district (id, name, region) VALUES (117,'Sembabule','Central');
INSERT INTO district (id, name, region) VALUES (118,'Serere','East');
INSERT INTO district (id, name, region) VALUES (119,'Sheema','West');
INSERT INTO district (id, name, region) VALUES (120,'Sironko','East');
INSERT INTO district (id, name, region) VALUES (121,'Soroti','East');
INSERT INTO district (id, name, region) VALUES (122,'Tororo','East');
INSERT INTO district (id, name, region) VALUES (123,'Wakiso','Central');
INSERT INTO district (id, name, region) VALUES (124,'Yumbe','West');
INSERT INTO district (id, name, region) VALUES (125,'Zombo','West');

DROP TABLE IF EXISTS farm;

CREATE TABLE farm (
  id int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  subcounty varchar(255) DEFAULT NULL,
  farmergroup_id int DEFAULT NULL,
  district_id int DEFAULT NULL,
  geolocation varchar(255) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY district_id (district_id),
  KEY farmergroup_id (farmergroup_id),
  CONSTRAINT farm_ibfk_1 FOREIGN KEY (district_id) REFERENCES district (id),
  CONSTRAINT farm_ibfk_2 FOREIGN KEY (farmergroup_id) REFERENCES farmergroup (id)
) ENGINE=InnoDB AUTO_INCREMENT=76 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (1,'John Doe Farm','Kawempe',1,1,'0.3163,32.5822');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (2,'Jane Smith Farm','Gulu',2,2,'2.7809,32.2995');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (3,'Peter Kato Farm','Mbale',3,3,'1.0647,34.1797');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (4,'Sarah Nalubega Farm','Makindye',1,4,'0.2986,32.6235');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (5,'David Omondi Farm','Nwoya',2,5,'2.6249,31.3952');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (6,'Grace Nakato Farm','Bubulo',3,6,'1.0722,34.1691');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (7,'Joseph Ssempala Farm','Rubaga',1,7,'0.2947,32.5521');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (8,'Mercy Auma Farm','Pader',2,8,'2.7687,33.2428');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (9,'Andrew Wabwire Farm','Manafwa',3,9,'1.1714,34.3447');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (10,'Harriet Namutebi Farm','Nakawa',1,10,'0.3153,32.6153');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (11,'Emmanuel Ojok Farm','Lira',2,11,'2.2481,32.8997');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (12,'Joyce Nakazibwe Farm','Sironko',3,12,'1.2236,34.3874');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (13,'Richard Kizza Farm','Nansana',1,13,'0.3652,32.5274');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (14,'Sarah Nambooze Farm','Kitgum',2,14,'3.3017,32.8737');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (15,'Godfrey Sserwadda Farm','Kapchorwa',3,15,'1.3962,34.4507');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (16,'Mary Nalule Farm','Wakiso',1,16,'0.4054,32.4594');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (17,'Isaac Ongom Farm','Amuru',2,17,'2.8231,31.4344');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (18,'Agnes Atim Farm','Bududa',3,18,'1.0614,34.3294');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (19,'Charles Odoi Farm','Kira',1,19,'0.3673,32.6159');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (20,'Florence Nakimera Farm','Adjumani',2,20,'3.3812,31.7989');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (21,'Alice Achieng Farm','Apac',1,21,'1.9730,32.5380');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (22,'Brian Musisi Farm','Bukedea',2,22,'1.3494,34.0636');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (23,'Catherine Namubiru Farm','Bushenyi',3,23,'0.5854,30.2160');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (24,'Daniel Odongo Farm','Busia',1,24,'0.4544,34.0735');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (25,'Eunice Nakato Farm','Buwenge',2,25,'0.4582,33.2142');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (26,'Francis Ssempijja Farm','Entebbe',3,26,'0.0527,32.4463');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (27,'Grace Nakayenga Farm','Fort Portal',1,27,'0.6711,30.2755');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (28,'Henry Kiwanuka Farm','Hoima',2,28,'1.4356,31.3586');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (29,'Irene Nankya Farm','Iganga',3,29,'0.6093,33.4862');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (30,'Josephine Nabukenya Farm','Isingiro',1,30,'0.7587,30.9399');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (31,'Kenneth Odhiambo Farm','Jinja',1,31,'0.4244,33.2041');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (32,'Lilian Nalwanga Farm','Kabale',2,32,'1.2504,29.9857');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (33,'Moses Ochieng Farm','Kabarole',3,33,'0.6107,30.2778');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (34,'Nancy Nantume Farm','Kabingo',1,34,'0.0836,32.4789');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (35,'Oscar Okoth Farm','Kabwohe',2,35,'0.8084,30.8014');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (36,'Patricia Namutebi Farm','Kajansi',3,36,'0.1519,32.5078');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (37,'Quincy Odongo Farm','Kaliro',1,37,'0.9031,33.5097');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (38,'Rebecca Nakato Farm','Kamuli',2,38,'0.9479,33.1197');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (39,'Stephen Ssemwogerere Farm','Kanungu',3,39,'0.9574,29.7980');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (40,'Teresa Nakabugo Farm','Kapchorwa',1,40,'1.3696,34.4027');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (41,'Umar Ssebunya Farm','Kasese',2,41,'0.1830,30.0665');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (42,'Violet Namutebi Farm','Katakwi',3,42,'1.8910,33.9756');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (43,'William Odoi Farm','Kayunga',1,43,'0.7021,32.8874');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (44,'Xavier Ouma Farm','Kibaale',2,44,'0.8830,31.3970');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (45,'Yusuf Ssebadduka Farm','Kiboga',3,45,'0.7880,31.0886');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (46,'Zainabu Nansubuga Farm','Kisoro',1,46,'1.3521,29.6935');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (47,'Abdul Nsereko Farm','Kitagata',2,47,'0.6346,30.2557');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (48,'Betty Nandawula Farm','Kitgum',3,48,'3.2783,32.8842');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (49,'Charles Okello Farm','Koboko',1,49,'3.4114,30.9601');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (50,'Dorothy Nakyobe Farm','Kotido',2,50,'3.0132,34.1336');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (51,'Alice Aol Farm','Kumi',1,51,'1.4583,33.9365');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (52,'Brian Okoth Farm','Kyenjojo',2,52,'0.6239,30.6206');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (53,'Catherine Nambi Farm','Lira',3,53,'2.2358,32.9090');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (54,'Daniel Opolot Farm','Luwero',1,54,'0.8499,32.4737');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (55,'Eunice Nabadda Farm','Lwengo',2,55,'0.4168,31.4114');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (56,'Francis Ongom Farm','Masaka',3,56,'0.3153,31.7133');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (57,'Grace Nakitende Farm','Masindi',1,57,'1.6736,31.7092');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (58,'Henry Owor Farm','Mayuge',2,58,'0.4603,33.4621');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (59,'Irene Nakanjako Farm','Mbale',3,59,'1.0647,34.1797');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (60,'Josephine Namatovu Farm','Mbarara',1,60,'0.6098,30.6485');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (61,'Kenneth Odeke Farm','Mitooma',2,61,'0.6166,30.0763');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (62,'Lilian Auma Farm','Moroto',3,62,'2.4956,34.6751');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (63,'Moses Okello Farm','Moyo',1,63,'3.6333,31.7167');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (64,'Nancy Nabayego Farm','Mpigi',2,64,'0.2254,32.3133');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (65,'Oscar Otema Farm','Mubende',3,65,'0.5901,31.3904');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (66,'Patricia Nakazibwe Farm','Mukono',1,66,'0.3536,32.7554');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (67,'Quincy Ojok Farm','Nakapiripirit',2,67,'1.8262,34.7172');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (68,'Rebecca Nabirye Farm','Nakaseke',3,68,'0.7519,32.3631');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (69,'Stephen Sserwadda Farm','Nakasongola',1,69,'1.3084,32.4587');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (70,'Teresa Nalubega Farm','Nebbi',2,70,'2.4758,31.0993');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (71,'Umar Okello Farm','Ngora',3,71,'1.4314,33.7065');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (72,'Violet Nakyobe Farm','Ntoroko',1,72,'1.0386,30.4329');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (73,'William Ogenrwot Farm','Ntungamo',2,73,'0.8769,30.2707');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (74,'Xavier Odong Farm','Pakwach',3,74,'2.4544,31.4704');
INSERT INTO farm (id, name, subcounty, farmergroup_id, district_id, geolocation) VALUES (75,'Yusuf Ssekandi Farm','Pallisa',1,75,'1.1455,33.7092');

DROP TABLE IF EXISTS farmdata;

CREATE TABLE farmdata (
  id int NOT NULL AUTO_INCREMENT,
  farm_id int DEFAULT NULL,
  crop_id int DEFAULT NULL,
  tilled_land_size float DEFAULT NULL,
  planting_date date DEFAULT NULL,
  season int DEFAULT NULL,
  quality varchar(255) DEFAULT NULL,
  quantity int DEFAULT NULL,
  harvest_date date DEFAULT NULL,
  expected_yield float DEFAULT NULL,
  actual_yield float DEFAULT NULL,
  `timestamp` timestamp NULL DEFAULT NULL,
  channel_partner varchar(255) DEFAULT NULL,
  destination_country varchar(255) DEFAULT NULL,
  customer_name varchar(255) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY farm_id (farm_id),
  KEY crop_id (crop_id),
  CONSTRAINT farmdata_ibfk_1 FOREIGN KEY (farm_id) REFERENCES farm (id),
  CONSTRAINT farmdata_ibfk_2 FOREIGN KEY (crop_id) REFERENCES crop (id)
) ENGINE=InnoDB AUTO_INCREMENT=159 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (1,1,1,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500,2300,'2023-07-15 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (2,1,2,1,'2023-03-20',1,'Fair',50,'2023-07-20',500,480,'2023-07-20 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (3,2,3,0.5,'2023-04-01',1,'Good',20,'2023-09-01',500,480,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (4,2,4,1,'2023-04-05',1,'Good',30,'2023-09-05',900,880,'2023-09-05 12:00:00','Uganda Organic Harvest','Uganda','Masaka Agro Enterprises');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (5,3,5,0.8,'2023-04-10',1,'Fair',40,'2023-09-10',800,780,'2023-09-10 12:00:00','Jinja Farms Ltd','Uganda','Mbarara Agro Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (6,3,6,0.3,'2023-04-15',1,'Excellent',15,'2023-09-15',225,220,'2023-09-15 12:00:00','Uganda Green Fields','Uganda','Lira Organic Farmers');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (7,4,1,2,'2023-03-15',1,'Good',80,'2023-07-15',2000,1900,'2023-07-15 12:00:00','Kasese AgriPro','Uganda','Entebbe Produce Group');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (8,4,2,0.8,'2023-03-20',1,'Fair',40,'2023-07-20',400,380,'2023-07-20 12:00:00','Uganda Harvesters','Uganda','Soroti Agri Enterprise');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (9,5,3,0.4,'2023-04-01',1,'Good',15,'2023-09-01',375,370,'2023-09-01 12:00:00','Kabale Farm Solutions','Uganda','Gulu Farmers Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (10,5,4,0.7,'2023-04-05',1,'Good',25,'2023-09-05',750,740,'2023-09-05 12:00:00','Mbale Agri Ltd','Uganda','Hoima Organic');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (11,6,5,0.6,'2023-04-10',1,'Fair',30,'2023-09-10',600,580,'2023-09-10 12:00:00','Uganda Agro Services','Uganda','Mityana Produce Group');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (12,6,6,0.2,'2023-04-15',1,'Excellent',10,'2023-09-15',150,140,'2023-09-15 12:00:00','Jinja Fields','Uganda','Kasese Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (13,7,1,1.5,'2023-03-15',1,'Good',60,'2023-07-15',1500,1400,'2023-07-15 12:00:00','Uganda Harvest Group','Uganda','Kabale Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (14,7,2,0.5,'2023-03-20',1,'Fair',25,'2023-07-20',250,240,'2023-07-20 12:00:00','Gulu Agri Solutions','Uganda','Mbale Organic');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (15,8,3,0.3,'2023-04-01',1,'Good',10,'2023-09-01',250,240,'2023-09-01 12:00:00','Lira Farms','Uganda','Masaka Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (16,8,4,0.6,'2023-04-05',1,'Good',20,'2023-09-05',600,590,'2023-09-05 12:00:00','Kabale AgriPro','Uganda','Jinja Organic');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (17,9,5,0.5,'2023-04-10',1,'Fair',25,'2023-09-10',500,490,'2023-09-10 12:00:00','Uganda Green Harvest','Uganda','Mbarara Agri Enterprise');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (18,9,6,0.2,'2023-04-15',1,'Excellent',10,'2023-09-15',100,90,'2023-09-15 12:00:00','Hoima Agro Solutions','Uganda','Kasese Farmers Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (19,10,1,1,'2023-03-15',1,'Good',40,'2023-07-15',1000,950,'2023-07-15 12:00:00','Entebbe Agri Ltd','Uganda','Masindi Harvesters');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (20,10,2,0.4,'2023-03-20',1,'Fair',20,'2023-07-20',200,190,'2023-07-20 12:00:00','Gulu Fields','Uganda','Mbale Agro Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (21,11,3,0.2,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 12:00:00','Mityana Farms','Uganda','Kabale Agri Group');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (22,11,4,0.4,'2023-04-05',1,'Good',10,'2023-09-05',300,290,'2023-09-05 12:00:00','Kasese AgroPro','Uganda','Gulu Organic Farmers');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (23,12,5,0.3,'2023-04-10',1,'Fair',15,'2023-09-10',300,290,'2023-09-10 12:00:00','Mbale Harvest Group','Uganda','Mityana Agri Enterprise');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (24,12,6,0.1,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 12:00:00','Masaka Agri Solutions','Uganda','Masindi Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (25,13,1,0.5,'2023-03-15',1,'Good',20,'2023-07-15',500,480,'2023-07-15 12:00:00','Kabale Green Fields','Uganda','Lira Harvest Group');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (26,13,2,0.2,'2023-03-20',1,'Fair',10,'2023-07-20',100,90,'2023-07-20 12:00:00','Mbarara AgriPro','Uganda','Entebbe Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (27,14,3,0.1,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 12:00:00','Gulu Harvesters','Uganda','Mbarara Harvesters');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (28,14,4,0.2,'2023-04-05',1,'Good',5,'2023-09-05',150,140,'2023-09-05 12:00:00','Masaka Fields','Uganda','Hoima Agri Enterprise');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (29,15,5,0.2,'2023-04-10',1,'Fair',10,'2023-09-10',100,90,'2023-09-10 12:00:00','Mbale AgroPro','Uganda','Masindi Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (30,15,6,0.1,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 12:00:00','Mityana Harvesters','Uganda','Entebbe Harvest Group');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (31,16,1,0.3,'2023-03-15',1,'Good',12,'2023-07-15',300,290,'2023-07-15 12:00:00','Masindi AgroPro','Uganda','Mityana Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (32,16,2,0.1,'2023-03-20',1,'Fair',6,'2023-07-20',60,50,'2023-07-20 12:00:00','Kabale Fields','Uganda','Jinja Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (33,17,3,0.05,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 12:00:00','Mbarara Agri Group','Uganda','Masaka Harvesters');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (34,17,4,0.1,'2023-04-05',1,'Good',3,'2023-09-05',30,25,'2023-09-05 12:00:00','Mbale Agro Solutions','Uganda','Kabale Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (35,18,5,0.1,'2023-04-10',1,'Fair',5,'2023-09-10',50,40,'2023-09-10 12:00:00','Masindi Harvest Group','Uganda','Kasese Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (36,18,6,0.05,'2023-04-15',1,'Excellent',2,'2023-09-15',20,15,'2023-09-15 12:00:00','Mityana AgroPro','Uganda','Lira Harvesters');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (37,19,1,0.2,'2023-03-15',1,'Good',8,'2023-07-15',200,190,'2023-07-15 12:00:00','Mbarara Agro Group','Uganda','Mbale Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (38,19,2,0.1,'2023-03-20',1,'Fair',4,'2023-07-20',40,30,'2023-07-20 12:00:00','Jinja Agri Solutions','Uganda','Mbarara Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (39,20,3,0.05,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 12:00:00','Masaka AgroPro','Uganda','Masindi Harvesters');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (40,20,4,0.1,'2023-04-05',1,'Good',3,'2023-09-05',30,25,'2023-09-05 12:00:00','Kabale Agro Solutions','Uganda','Kasese Agri Group');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (41,1,1,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500,2300,'2023-07-15 12:00:00','Mityana Agri Group','Uganda','Gulu Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (42,1,2,1,'2023-03-20',1,'Fair',50,'2023-07-20',500,480,'2023-07-20 12:00:00','Masindi Agro Solutions','Uganda','Mbale Harvesters');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (43,2,3,0.5,'2023-04-01',1,'Good',20,'2023-09-01',500,480,'2023-09-01 12:00:00','Kasese Agro Group','Uganda','Entebbe Harvest Group');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (44,2,4,1,'2023-04-05',1,'Good',30,'2023-09-05',900,880,'2023-09-05 12:00:00','Mbarara Agro Solutions','Uganda','Jinja Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (45,3,5,0.8,'2023-04-10',1,'Fair',40,'2023-09-10',800,780,'2023-09-10 12:00:00','Mbale Agro Group','Uganda','Mbarara Harvesters');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (46,3,6,0.3,'2023-04-15',1,'Excellent',15,'2023-09-15',225,220,'2023-09-15 12:00:00','Mityana Agro Solutions','Uganda','Masaka Harvesters');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (47,4,1,2,'2023-03-15',1,'Good',80,'2023-07-15',2000,1900,'2023-07-15 12:00:00','Masaka Agro Group','Uganda','Kabale Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (48,4,2,0.8,'2023-03-20',1,'Fair',40,'2023-07-20',400,380,'2023-07-20 12:00:00','Kabale Agro Group','Uganda','Mbarara Harvesters');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (49,5,3,0.4,'2023-04-01',1,'Good',15,'2023-09-01',375,370,'2023-09-01 12:00:00','Mbarara AgroPro','Uganda','Masaka Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (50,5,4,0.7,'2023-04-05',1,'Good',25,'2023-09-05',750,740,'2023-09-05 12:00:00','Mbale Agro Solutions','Uganda','Masindi Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (51,6,5,0.6,'2023-04-10',1,'Fair',30,'2023-09-10',600,580,'2023-09-10 12:00:00','Masaka Agro Solutions','Uganda','Mbarara Harvesters');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (52,6,6,0.2,'2023-04-15',1,'Excellent',10,'2023-09-15',150,140,'2023-09-15 12:00:00','Mityana AgroPro','Uganda','Kasese Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (53,7,1,1.5,'2023-03-15',1,'Good',60,'2023-07-15',1500,1400,'2023-07-15 12:00:00','Masindi Agro Solutions','Uganda','Entebbe Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (54,7,2,0.5,'2023-03-20',1,'Fair',25,'2023-07-20',250,240,'2023-07-20 12:00:00','Kasese Agro Solutions','Uganda','Mityana Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (55,8,3,0.3,'2023-04-01',1,'Good',10,'2023-09-01',250,240,'2023-09-01 12:00:00','Mbarara Agro Solutions','Uganda','Masaka Agri Group');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (56,8,4,0.6,'2023-04-05',1,'Good',20,'2023-09-05',600,590,'2023-09-05 12:00:00','Mbale AgroPro','Uganda','Jinja Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (57,9,5,0.5,'2023-04-10',1,'Fair',25,'2023-09-10',500,490,'2023-09-10 12:00:00','Masindi AgroPro','Uganda','Mbarara Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (58,9,6,0.2,'2023-04-15',1,'Excellent',10,'2023-09-15',100,90,'2023-09-15 12:00:00','Kasese Agro Group','Uganda','Masaka Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (59,10,1,1,'2023-03-15',1,'Good',40,'2023-07-15',1000,950,'2023-07-15 12:00:00','Mityana AgroPro','Uganda','Kabale Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (60,10,2,0.4,'2023-03-20',1,'Fair',20,'2023-07-20',200,190,'2023-07-20 12:00:00','Masaka AgroPro','Uganda','Mbarara Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (61,11,3,0.2,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 12:00:00','Mbarara Agro Solutions','Uganda','Kasese Agri Group');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (62,11,4,0.4,'2023-04-05',1,'Good',10,'2023-09-05',300,290,'2023-09-05 12:00:00','Mbale Agro Solutions','Uganda','Masindi Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (63,12,5,0.3,'2023-04-10',1,'Fair',15,'2023-09-10',300,290,'2023-09-10 12:00:00','Masaka Agro Solutions','Uganda','Mbarara Agri Group');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (64,12,6,0.1,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 12:00:00','Mityana AgroPro','Uganda','Masaka Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (65,13,1,0.5,'2023-03-15',1,'Good',20,'2023-07-15',500,480,'2023-07-15 12:00:00','Masindi AgroPro','Uganda','Jinja Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (66,13,2,0.2,'2023-03-20',1,'Fair',10,'2023-07-20',100,90,'2023-07-20 12:00:00','Kasese Agro Group','Uganda','Mbarara Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (67,14,3,0.1,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 12:00:00','Mbarara Agro Solutions','Uganda','Kasese Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (68,14,4,0.2,'2023-04-05',1,'Good',5,'2023-09-05',150,140,'2023-09-05 12:00:00','Mbale Agro Solutions','Uganda','Masaka Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (69,15,5,0.2,'2023-04-10',1,'Fair',10,'2023-09-10',100,90,'2023-09-10 12:00:00','Masaka Agro Solutions','Uganda','Mbarara Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (70,15,6,0.1,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 12:00:00','Mityana AgroPro','Uganda','Kabale Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (71,16,1,0.3,'2023-03-15',1,'Good',12,'2023-07-15',300,290,'2023-07-15 12:00:00','Masaka AgroPro','Uganda','Mbarara Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (72,16,2,0.1,'2023-03-20',1,'Fair',6,'2023-07-20',60,50,'2023-07-20 12:00:00','Mbarara Agro Solutions','Uganda','Kasese Agri Group');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (73,17,3,0.05,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 12:00:00','Mbale Agro Solutions','Uganda','Masindi Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (74,17,4,0.1,'2023-04-05',1,'Good',3,'2023-09-05',30,25,'2023-09-05 12:00:00','Masaka Agro Solutions','Uganda','Mbarara Agri Group');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (75,18,5,0.1,'2023-04-10',1,'Fair',5,'2023-09-10',50,40,'2023-09-10 12:00:00','Mityana AgroPro','Uganda','Masaka Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (76,18,6,0.05,'2023-04-15',1,'Excellent',2,'2023-09-15',20,15,'2023-09-15 12:00:00','Masindi AgroPro','Uganda','Jinja Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (77,19,1,0.2,'2023-03-15',1,'Good',8,'2023-07-15',200,190,'2023-07-15 12:00:00','Kasese Agro Group','Uganda','Mbarara Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (78,19,2,0.1,'2023-03-20',1,'Fair',4,'2023-07-20',40,30,'2023-07-20 12:00:00','Mbarara Agro Solutions','Uganda','Kasese Agri Coop');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (79,20,3,0.05,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 12:00:00','Mbale Agro Solutions','Uganda','Masaka Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (80,20,4,0.1,'2023-04-05',1,'Good',3,'2023-09-05',30,25,'2023-09-05 12:00:00','Masaka Agro Solutions','Uganda','Mbarara Agri Solutions');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (81,11,1,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500,2300,'2023-07-15 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (82,21,2,1,'2023-03-20',1,'Fair',50,'2023-07-20',500,480,'2023-07-20 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (83,32,3,0.5,'2023-04-01',1,'Good',20,'2023-09-01',500,480,'2023-09-01 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (84,42,4,1,'2023-04-05',1,'Good',30,'2023-09-05',900,880,'2023-09-05 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (85,53,5,0.84,'2023-04-10',1,'Fair',40,'2023-09-10',800,780,'2023-09-10 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (86,13,6,0.289,'2023-04-15',1,'Excellent',15,'2023-09-15',225,220,'2023-09-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (87,24,1,2,'2023-03-15',1,'Good',80,'2023-07-15',2000,1900,'2023-07-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (88,34,2,0.84,'2023-03-20',1,'Fair',40,'2023-07-20',400,380,'2023-07-20 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (89,43,3,0.42,'2023-04-01',1,'Good',15,'2023-09-01',375,370,'2023-09-01 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (90,52,4,0.659,'2023-04-05',1,'Good',25,'2023-09-05',750,740,'2023-09-05 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (91,11,5,0.579,'2023-04-10',1,'Fair',30,'2023-09-10',600,580,'2023-09-10 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (92,12,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',150,140,'2023-09-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (93,22,1,1.5,'2023-03-15',1,'Good',60,'2023-07-15',1500,1400,'2023-07-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (94,33,2,0.5,'2023-03-20',1,'Fair',25,'2023-07-20',250,240,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (95,43,3,0.289,'2023-04-01',1,'Good',10,'2023-09-01',250,240,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (96,53,4,0.579,'2023-04-05',1,'Good',20,'2023-09-05',600,590,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (97,14,5,0.5,'2023-04-10',1,'Fair',25,'2023-09-10',500,490,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (98,25,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',100,90,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (99,16,1,1,'2023-03-15',1,'Good',40,'2023-07-15',1000,950,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (100,17,2,0.4222,'2023-03-20',1,'Fair',20,'2023-07-20',200,190,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (101,38,3,0.200111,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (102,19,4,0.400022,'2023-04-05',1,'Good',10,'2023-09-05',300,290,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (103,10,5,0.29,'2023-04-10',1,'Fair',15,'2023-09-10',300,290,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (104,15,6,0.100555,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (105,41,1,0.5,'2023-03-15',1,'Good',20,'2023-07-15',500,480,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (106,72,2,0.200111,'2023-03-20',1,'Fair',10,'2023-07-20',100,90,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (107,52,3,0.155,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (108,13,4,0.21,'2023-04-05',1,'Good',5,'2023-09-05',150,140,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (109,14,5,0.21,'2023-04-10',1,'Fair',10,'2023-09-10',100,90,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (110,15,6,0.155,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (111,16,1,0.289,'2023-03-15',1,'Good',12,'2023-07-15',300,290,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (112,17,2,0.155,'2023-03-20',1,'Fair',6,'2023-07-20',60,50,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (113,18,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (114,19,4,0.155,'2023-04-05',1,'Good',3,'2023-09-05',30,25,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (115,20,5,0.155,'2023-04-10',1,'Fair',5,'2023-09-10',50,40,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (116,21,6,0.0775,'2023-04-15',1,'Excellent',2,'2023-09-15',20,15,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (117,22,1,0.21,'2023-03-15',1,'Good',8,'2023-07-15',200,190,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (118,38,2,0.155,'2023-03-20',1,'Fair',4,'2023-07-20',40,30,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (119,39,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (120,40,1,2.5,'2023-03-15',1,'Good',100,'2023-07-15',2500,2300,'2023-07-15 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (121,41,2,1,'2023-03-20',1,'Fair',50,'2023-07-20',500,480,'2023-07-20 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (122,42,3,0.5,'2023-04-01',1,'Good',20,'2023-09-01',500,480,'2023-09-01 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (123,43,4,1,'2023-04-05',1,'Good',30,'2023-09-05',900,880,'2023-09-05 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (124,44,5,0.84,'2023-04-10',1,'Fair',40,'2023-09-10',800,780,'2023-09-10 12:00:00','Agro Supplies Ltd','Uganda','Jinja Farms Ltd');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (125,45,6,0.289,'2023-04-15',1,'Excellent',15,'2023-09-15',225,220,'2023-09-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (126,46,1,2,'2023-03-15',1,'Good',80,'2023-07-15',2000,1900,'2023-07-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (127,47,2,0.84,'2023-03-20',1,'Fair',40,'2023-07-20',400,380,'2023-07-20 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (128,48,3,0.42,'2023-04-01',1,'Good',15,'2023-09-01',375,370,'2023-09-01 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (129,49,4,0.659,'2023-04-05',1,'Good',25,'2023-09-05',750,740,'2023-09-05 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (130,50,5,0.579,'2023-04-10',1,'Fair',30,'2023-09-10',600,580,'2023-09-10 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (131,51,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',150,140,'2023-09-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (132,52,1,1.5,'2023-03-15',1,'Good',60,'2023-07-15',1500,1400,'2023-07-15 12:00:00','Uganda AgriTech Solutions','Uganda','Kampala Agro Farms');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (133,53,2,0.5,'2023-03-20',1,'Fair',25,'2023-07-20',250,240,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (134,54,3,0.289,'2023-04-01',1,'Good',10,'2023-09-01',250,240,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (135,55,4,0.579,'2023-04-05',1,'Good',20,'2023-09-05',600,590,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (136,56,5,0.5,'2023-04-10',1,'Fair',25,'2023-09-10',500,490,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (137,57,6,0.21,'2023-04-15',1,'Excellent',10,'2023-09-15',100,90,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (138,58,1,1,'2023-03-15',1,'Good',40,'2023-07-15',1000,950,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (139,59,2,0.4222,'2023-03-20',1,'Fair',20,'2023-07-20',200,190,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (140,60,3,0.200111,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (141,61,4,0.400022,'2023-04-05',1,'Good',10,'2023-09-05',300,290,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (142,62,5,0.29,'2023-04-10',1,'Fair',15,'2023-09-10',300,290,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (143,63,6,0.100555,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (144,64,1,0.5,'2023-03-15',1,'Good',20,'2023-07-15',500,480,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (145,65,2,0.200111,'2023-03-20',1,'Fair',10,'2023-07-20',100,90,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (146,66,3,0.155,'2023-04-01',1,'Good',5,'2023-09-01',125,120,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (147,67,4,0.21,'2023-04-05',1,'Good',5,'2023-09-05',150,140,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (148,68,5,0.21,'2023-04-10',1,'Fair',10,'2023-09-10',100,90,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (149,69,6,0.155,'2023-04-15',1,'Excellent',5,'2023-09-15',50,40,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (150,70,1,0.289,'2023-03-15',1,'Good',12,'2023-07-15',300,290,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (151,72,2,0.155,'2023-03-20',1,'Fair',6,'2023-07-20',60,50,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (152,73,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (153,74,4,0.155,'2023-04-05',1,'Good',3,'2023-09-05',30,25,'2023-09-05 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (154,30,5,0.155,'2023-04-10',1,'Fair',5,'2023-09-10',50,40,'2023-09-10 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (155,31,6,0.0775,'2023-04-15',1,'Excellent',2,'2023-09-15',20,15,'2023-09-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (156,32,1,0.21,'2023-03-15',1,'Good',8,'2023-07-15',200,190,'2023-07-15 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (157,33,2,0.155,'2023-03-20',1,'Fair',4,'2023-07-20',40,30,'2023-07-20 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');
INSERT INTO farmdata (id, farm_id, crop_id, tilled_land_size, planting_date, season, quality, quantity, harvest_date, expected_yield, actual_yield, timestamp, channel_partner, destination_country, customer_name) VALUES (158,34,3,0.0775,'2023-04-01',1,'Good',2,'2023-09-01',50,40,'2023-09-01 12:00:00','Kampala Agri Solutions','Uganda','Mbale Farms Co.');


DROP TABLE IF EXISTS farmergroup;

CREATE TABLE farmergroup (
  id int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (id)
) ;

INSERT INTO farmergroup (id, name, description) VALUES (1,'Farmers Cooperative Society','A cooperative society of farmers');
INSERT INTO farmergroup (id, name, description) VALUES (2,'Women Farmers Association','An association of women farmers');
INSERT INTO farmergroup (id, name, description) VALUES (3,'Young Farmers Group','A group of young farmers');

DROP TABLE IF EXISTS forest;

CREATE TABLE forest (
  id int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (id)
) ;

INSERT INTO forest (id, name) VALUES (1,'Forest 1');
INSERT INTO forest (id, name) VALUES (2,'Pine Forest');


DROP TABLE IF EXISTS point;

CREATE TABLE `point` (
  id int NOT NULL AUTO_INCREMENT,
  longitude float DEFAULT NULL,
  latitude float DEFAULT NULL,
  owner_type enum('forest','farmer') NOT NULL,
  forest_id int DEFAULT NULL,
  farmer_id int DEFAULT NULL,
  district_id int DEFAULT NULL,
  PRIMARY KEY (id),
  KEY district_id (district_id),
  KEY forest_id (forest_id),
  KEY farmer_id (farmer_id),
  CONSTRAINT point_ibfk_1 FOREIGN KEY (district_id) REFERENCES district (id),
  CONSTRAINT point_ibfk_2 FOREIGN KEY (forest_id) REFERENCES forest (id),
  CONSTRAINT point_ibfk_3 FOREIGN KEY (farmer_id) REFERENCES farm (id),
  CONSTRAINT point_chk_1 CHECK ((((`owner_type` = _utf8mb4'forest') and (`forest_id` is not null) and (`farmer_id` is null)) or ((`owner_type` = _utf8mb4'farmer') and (`farmer_id` is not null) and (`forest_id` is null))))
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (1,0.361753,32.6505,'forest',1,NULL,NULL);
INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (2,0.361352,32.6515,'forest',1,NULL,NULL);
INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (3,0.361054,32.6521,'forest',1,NULL,NULL);
INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (4,0.36098,32.6521,'forest',1,NULL,NULL);
INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (5,0.361107,32.6517,'forest',1,NULL,NULL);
INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (6,0.361494,32.6516,'forest',1,NULL,NULL);
INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (7,0.361352,32.6515,'forest',1,NULL,NULL);
INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (8,0.360711,32.6511,'forest',1,NULL,NULL);
INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (9,0.361618,32.6509,'forest',1,NULL,NULL);
INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (10,0.361575,32.651,'forest',1,NULL,NULL);
INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (11,0.360818,32.6515,'forest',1,NULL,NULL);
INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (12,0.361183,32.6512,'forest',1,NULL,NULL);
INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (13,0.361116,32.6527,'forest',1,NULL,NULL);
INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (14,0.36114,32.6524,'forest',1,NULL,NULL);
INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (15,0.36126,32.6508,'forest',1,NULL,NULL);
INSERT INTO point (id, longitude, latitude, owner_type, forest_id, farmer_id, district_id) VALUES (16,0.361496,32.6508,'forest',1,NULL,NULL);


DROP TABLE IF EXISTS producecategory;

CREATE TABLE producecategory (
  id int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  grade int DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


INSERT INTO producecategory (id, name, grade) VALUES (1,'Maize',1);
INSERT INTO producecategory (id, name, grade) VALUES (2,'Beans',2);
INSERT INTO producecategory (id, name, grade) VALUES (3,'Coffee',3);
INSERT INTO producecategory (id, name, grade) VALUES (4,'Cassava',1);
INSERT INTO producecategory (id, name, grade) VALUES (5,'Rice',2);
INSERT INTO producecategory (id, name, grade) VALUES (6,'Bananas',3);

DROP TABLE IF EXISTS soildata;

CREATE TABLE soildata (
  id int NOT NULL AUTO_INCREMENT,
  district_id int DEFAULT NULL,
  internal_id int DEFAULT NULL,
  device varchar(255) DEFAULT NULL,
  `owner` varchar(255) DEFAULT NULL,
  nitrogen float DEFAULT NULL,
  phosphorus float DEFAULT NULL,
  potassium float DEFAULT NULL,
  ph float DEFAULT NULL,
  temperature float DEFAULT NULL,
  humidity float DEFAULT NULL,
  conductivity float DEFAULT NULL,
  signal_level float DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (id),
  KEY district_id (district_id),
  CONSTRAINT soildata_ibfk_1 FOREIGN KEY (district_id) REFERENCES district (id)
);

INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (1,1,1001,'Device1','Owner1',0.6,0.3,0.4,6.5,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (2,1,1002,'Device2','Owner2',0.4,0.2,0.5,6.8,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (3,1,1003,'Device3','Owner3',0.5,0.4,0.3,6.2,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (4,2,1004,'Device4','Owner4',0.7,0.5,0.4,6.6,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (5,2,1005,'Device5','Owner5',0.5,0.3,0.6,6.9,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (6,2,1006,'Device6','Owner6',0.6,0.4,0.5,6.3,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (7,3,1007,'Device7','Owner7',0.8,0.6,0.4,6.7,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (8,3,1008,'Device8','Owner8',0.4,0.3,0.7,7,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (9,3,1009,'Device9','Owner9',0.7,0.5,0.6,6.4,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (10,4,1010,'Device10','Owner10',0.5,0.4,0.3,6.8,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (11,4,1011,'Device11','Owner11',0.6,0.3,0.5,7.1,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (12,4,1012,'Device12','Owner12',0.8,0.7,0.6,6.5,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (13,5,1013,'Device13','Owner13',0.9,0.8,0.4,6.9,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (14,5,1014,'Device14','Owner14',0.6,0.5,0.7,7.2,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (15,5,1015,'Device15','Owner15',0.7,0.6,0.6,6.6,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (16,6,1016,'Device16','Owner16',0.5,0.4,0.3,7,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (17,6,1017,'Device17','Owner17',0.6,0.5,0.5,7.3,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (18,6,1018,'Device18','Owner18',0.8,0.7,0.6,6.7,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (19,7,1019,'Device19','Owner19',0.9,0.8,0.4,7.1,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (20,7,1020,'Device20','Owner20',0.6,0.5,0.8,7.4,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (21,7,1021,'Device21','Owner21',0.7,0.6,0.7,6.8,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (22,8,1022,'Device22','Owner22',0.5,0.4,0.4,7.2,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (23,8,1023,'Device23','Owner23',0.6,0.5,0.6,7.5,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (24,8,1024,'Device24','Owner24',0.8,0.7,0.5,6.9,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (25,9,1025,'Device25','Owner25',0.9,0.8,0.3,7.3,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (26,9,1026,'Device26','Owner26',0.6,0.5,0.9,7.6,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (27,9,1027,'Device27','Owner27',0.7,0.6,0.8,7,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (28,10,1028,'Device28','Owner28',0.5,0.4,0.5,7.4,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (29,10,1029,'Device29','Owner29',0.6,0.5,0.7,7.7,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (30,10,1030,'Device30','Owner30',0.8,0.7,0.4,7.1,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (31,11,1031,'Device31','Owner31',0.9,0.8,0.6,7.5,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (32,11,1032,'Device32','Owner32',0.6,0.5,0.8,7.8,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (33,11,1033,'Device33','Owner33',0.7,0.6,0.7,7.2,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (34,12,1034,'Device34','Owner34',0.5,0.4,0.4,7.6,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (35,12,1035,'Device35','Owner35',0.6,0.5,0.6,7.9,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (36,12,1036,'Device36','Owner36',0.8,0.7,0.5,7.3,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (37,13,1037,'Device37','Owner37',0.9,0.8,0.3,7.7,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (38,13,1038,'Device38','Owner38',0.6,0.5,0.9,8,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (39,13,1039,'Device39','Owner39',0.7,0.6,0.8,7.4,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (40,14,1040,'Device40','Owner40',0.5,0.4,0.5,7.8,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (41,14,1041,'Device41','Owner41',0.6,0.5,0.7,8.1,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (42,14,1042,'Device42','Owner42',0.8,0.7,0.4,7.5,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (43,15,1043,'Device43','Owner43',0.9,0.8,0.6,7.9,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (44,15,1044,'Device44','Owner44',0.6,0.5,0.8,8.2,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (45,15,1045,'Device45','Owner45',0.7,0.6,0.7,7.6,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (46,16,1046,'Device46','Owner46',0.5,0.4,0.4,8,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (47,16,1047,'Device47','Owner47',0.6,0.5,0.6,8.3,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (48,16,1048,'Device48','Owner48',0.8,0.7,0.5,7.7,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (49,17,1049,'Device49','Owner49',0.9,0.8,0.3,8.1,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (50,17,1050,'Device50','Owner50',0.6,0.5,0.9,8.4,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (51,18,1051,'Device51','Owner51',0.7,0.6,0.5,7.8,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (52,18,1052,'Device52','Owner52',0.8,0.7,0.7,8.1,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (53,18,1053,'Device53','Owner53',0.5,0.4,0.6,7.5,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (54,19,1054,'Device54','Owner54',0.9,0.8,0.4,8.2,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (55,19,1055,'Device55','Owner55',0.6,0.5,0.8,8.5,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (56,19,1056,'Device56','Owner56',0.7,0.6,0.7,7.9,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (57,20,1057,'Device57','Owner57',0.5,0.4,0.5,8.3,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (58,20,1058,'Device58','Owner58',0.6,0.5,0.7,8.6,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (59,20,1059,'Device59','Owner59',0.8,0.7,0.6,8,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (60,21,1060,'Device60','Owner60',0.9,0.8,0.3,8.4,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (61,21,1061,'Device61','Owner61',0.6,0.5,0.9,8.7,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (62,21,1062,'Device62','Owner62',0.7,0.6,0.8,8.1,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (63,22,1063,'Device63','Owner63',0.5,0.4,0.4,8.5,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (64,22,1064,'Device64','Owner64',0.6,0.5,0.6,8.8,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (65,22,1065,'Device65','Owner65',0.8,0.7,0.5,8.2,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (66,23,1066,'Device66','Owner66',0.9,0.8,0.6,8.6,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (67,23,1067,'Device67','Owner67',0.6,0.5,0.8,8.9,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (68,23,1068,'Device68','Owner68',0.7,0.6,0.7,8.3,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (69,24,1069,'Device69','Owner69',0.5,0.4,0.5,8.7,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (70,24,1070,'Device70','Owner70',0.6,0.5,0.7,9,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (71,24,1071,'Device71','Owner71',0.8,0.7,0.4,8.4,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (72,25,1072,'Device72','Owner72',0.9,0.8,0.6,8.8,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (73,25,1073,'Device73','Owner73',0.6,0.5,0.8,9.1,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (74,25,1074,'Device74','Owner74',0.7,0.6,0.7,8.5,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (75,26,1075,'Device75','Owner75',0.5,0.4,0.4,8.9,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (76,26,1076,'Device76','Owner76',0.6,0.5,0.6,9.2,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (77,26,1077,'Device77','Owner77',0.8,0.7,0.5,8.6,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (78,27,1078,'Device78','Owner78',0.9,0.8,0.3,9,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (79,27,1079,'Device79','Owner79',0.6,0.5,0.9,9.3,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (80,27,1080,'Device80','Owner80',0.7,0.6,0.8,8.7,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (81,28,1081,'Device81','Owner81',0.5,0.4,0.5,9.1,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (82,28,1082,'Device82','Owner82',0.6,0.5,0.7,9.4,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (83,28,1083,'Device83','Owner83',0.8,0.7,0.4,8.8,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (84,29,1084,'Device84','Owner84',0.9,0.8,0.6,9.2,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (85,29,1085,'Device85','Owner85',0.6,0.5,0.8,9.5,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (86,29,1086,'Device86','Owner86',0.7,0.6,0.7,8.9,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (87,30,1087,'Device87','Owner87',0.5,0.4,0.4,9.3,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (88,31,1090,'Device90','Owner90',0.9,0.8,0.6,9.4,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (89,31,1091,'Device91','Owner91',0.6,0.5,0.8,9.7,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (90,31,1092,'Device92','Owner92',0.7,0.6,0.7,9.1,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (91,32,1093,'Device93','Owner93',0.5,0.4,0.5,9.5,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (92,32,1094,'Device94','Owner94',0.6,0.5,0.7,9.8,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (93,32,1095,'Device95','Owner95',0.8,0.7,0.6,9.2,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (94,33,1096,'Device96','Owner96',0.9,0.8,0.3,9.6,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (95,33,1097,'Device97','Owner97',0.6,0.5,0.9,9.9,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (96,33,1098,'Device98','Owner98',0.7,0.6,0.8,9.3,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (97,34,1099,'Device99','Owner99',0.5,0.4,0.4,9.7,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (98,34,1100,'Device100','Owner100',0.6,0.5,0.6,10,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (99,34,1101,'Device101','Owner101',0.8,0.7,0.5,9.4,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (100,35,1102,'Device102','Owner102',0.9,0.8,0.6,9.8,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (101,35,1103,'Device103','Owner103',0.6,0.5,0.8,10.1,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (102,35,1104,'Device104','Owner104',0.7,0.6,0.7,9.5,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (103,36,1105,'Device105','Owner105',0.5,0.4,0.5,9.9,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (104,36,1106,'Device106','Owner106',0.6,0.5,0.7,10.2,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (105,36,1107,'Device107','Owner107',0.8,0.7,0.6,9.6,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (106,37,1108,'Device108','Owner108',0.9,0.8,0.3,10,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (107,37,1109,'Device109','Owner109',0.6,0.5,0.9,10.3,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (108,37,1110,'Device110','Owner110',0.7,0.6,0.8,9.7,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (109,38,1111,'Device111','Owner111',0.5,0.4,0.4,10.1,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (110,38,1112,'Device112','Owner112',0.6,0.5,0.6,10.4,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (111,38,1113,'Device113','Owner113',0.8,0.7,0.5,9.8,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (112,39,1114,'Device114','Owner114',0.9,0.8,0.6,10.2,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (113,39,1115,'Device115','Owner115',0.6,0.5,0.8,10.5,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (114,39,1116,'Device116','Owner116',0.7,0.6,0.7,9.9,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (115,40,1117,'Device117','Owner117',0.5,0.4,0.5,10.3,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (116,40,1118,'Device118','Owner118',0.6,0.5,0.7,10.6,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (117,40,1119,'Device119','Owner119',0.8,0.7,0.6,10,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (118,41,1120,'Device120','Owner120',0.9,0.8,0.3,10.4,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (119,41,1121,'Device121','Owner121',0.6,0.5,0.9,10.7,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (120,41,1122,'Device122','Owner122',0.7,0.6,0.8,10.1,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (121,42,1123,'Device123','Owner123',0.5,0.4,0.4,10.5,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (122,42,1124,'Device124','Owner124',0.6,0.5,0.6,10.8,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (123,42,1125,'Device125','Owner125',0.8,0.7,0.5,10.2,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (124,43,1126,'Device126','Owner126',0.9,0.8,0.6,10.6,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (125,43,1127,'Device127','Owner127',0.6,0.5,0.8,10.9,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (126,43,1128,'Device128','Owner128',0.7,0.6,0.7,10.3,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (127,44,1129,'Device129','Owner129',0.5,0.4,0.5,10.7,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (128,44,1130,'Device130','Owner130',0.6,0.5,0.7,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (129,44,1131,'Device131','Owner131',0.8,0.7,0.6,10.4,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (130,45,1132,'Device132','Owner132',0.9,0.8,0.3,10.8,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (131,45,1133,'Device133','Owner133',0.6,0.5,0.9,11.1,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (132,45,1134,'Device134','Owner134',0.7,0.6,0.8,10.5,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (133,46,1135,'Device135','Owner135',0.5,0.4,0.4,10.9,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (134,46,1136,'Device136','Owner136',0.6,0.5,0.6,11.2,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (135,46,1137,'Device137','Owner137',0.8,0.7,0.5,10.6,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (136,47,1138,'Device138','Owner138',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (137,47,1139,'Device139','Owner139',0.6,0.5,0.8,11.3,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (138,47,1140,'Device140','Owner140',0.7,0.6,0.7,10.7,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (139,48,1141,'Device141','Owner141',0.5,0.4,0.5,11.1,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (140,48,1142,'Device142','Owner142',0.6,0.5,0.7,11.4,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (141,48,1143,'Device143','Owner143',0.8,0.7,0.6,10.8,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (142,49,1144,'Device144','Owner144',0.9,0.8,0.3,11.2,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (143,49,1145,'Device145','Owner145',0.6,0.5,0.9,11.5,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (144,49,1146,'Device146','Owner146',0.7,0.6,0.8,10.9,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (145,50,1147,'Device147','Owner147',0.5,0.4,0.4,11.3,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (146,50,1148,'Device148','Owner148',0.6,0.5,0.6,11.6,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (147,50,1149,'Device149','Owner149',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (148,51,1150,'Device150','Owner150',0.9,0.8,0.6,11.4,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (149,52,1151,'Device151','Owner151',0.7,0.6,0.7,11.7,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (150,52,1152,'Device152','Owner152',0.8,0.7,0.6,11.1,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (151,52,1153,'Device153','Owner153',0.5,0.4,0.5,11.5,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (152,53,1154,'Device154','Owner154',0.6,0.5,0.7,11.8,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (153,53,1155,'Device155','Owner155',0.8,0.7,0.6,11.2,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (154,53,1156,'Device156','Owner156',0.9,0.8,0.5,11.6,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (155,54,1157,'Device157','Owner157',0.6,0.5,0.8,11.9,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (156,54,1158,'Device158','Owner158',0.7,0.6,0.7,11.3,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (157,54,1159,'Device159','Owner159',0.5,0.4,0.5,11.7,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (158,55,1160,'Device160','Owner160',0.6,0.5,0.7,12,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (159,55,1161,'Device161','Owner161',0.8,0.7,0.6,11.4,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (160,55,1162,'Device162','Owner162',0.9,0.8,0.5,11.8,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (161,56,1163,'Device163','Owner163',0.6,0.5,0.8,12.1,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (162,56,1164,'Device164','Owner164',0.7,0.6,0.7,11.5,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (163,56,1165,'Device165','Owner165',0.5,0.4,0.5,11.9,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (164,57,1166,'Device166','Owner166',0.6,0.5,0.7,12.2,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (165,57,1167,'Device167','Owner167',0.8,0.7,0.6,11.6,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (166,57,1168,'Device168','Owner168',0.9,0.8,0.5,12,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (167,58,1169,'Device169','Owner169',0.6,0.5,0.8,12.3,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (168,58,1170,'Device170','Owner170',0.7,0.6,0.7,11.7,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (169,58,1171,'Device171','Owner171',0.5,0.4,0.5,12.1,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (170,59,1172,'Device172','Owner172',0.6,0.5,0.7,12.4,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (171,59,1173,'Device173','Owner173',0.8,0.7,0.6,11.8,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (172,59,1174,'Device174','Owner174',0.9,0.8,0.5,12.2,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (173,60,1175,'Device175','Owner175',0.6,0.5,0.8,12.5,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (174,60,1176,'Device176','Owner176',0.7,0.6,0.7,11.9,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (175,60,1177,'Device177','Owner177',0.5,0.4,0.5,12.3,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (176,61,1178,'Device178','Owner178',0.6,0.5,0.7,12.6,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (177,61,1179,'Device179','Owner179',0.8,0.7,0.6,12,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (178,61,1180,'Device180','Owner180',0.9,0.8,0.5,12.4,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (179,62,1181,'Device181','Owner181',0.6,0.5,0.8,12.7,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (180,62,1182,'Device182','Owner182',0.7,0.6,0.7,12.1,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (181,62,1183,'Device183','Owner183',0.5,0.4,0.5,12.5,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (182,63,1184,'Device184','Owner184',0.6,0.5,0.7,12.8,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (183,63,1185,'Device185','Owner185',0.8,0.7,0.6,12.2,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (184,63,1186,'Device186','Owner186',0.9,0.8,0.5,12.6,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (185,64,1187,'Device187','Owner187',0.6,0.5,0.8,12.9,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (186,64,1188,'Device188','Owner188',0.7,0.6,0.7,12.3,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (187,64,1189,'Device189','Owner189',0.5,0.4,0.5,12.7,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (188,65,1190,'Device190','Owner190',0.6,0.5,0.7,13,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (189,65,1191,'Device191','Owner191',0.8,0.7,0.6,12.4,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (190,65,1192,'Device192','Owner192',0.9,0.8,0.5,12.8,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (191,66,1193,'Device193','Owner193',0.6,0.5,0.8,13.1,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (192,66,1194,'Device194','Owner194',0.7,0.6,0.7,12.5,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (193,66,1195,'Device195','Owner195',0.5,0.4,0.5,12.9,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (194,67,1196,'Device196','Owner196',0.6,0.5,0.7,13.2,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (195,67,1197,'Device197','Owner197',0.8,0.7,0.6,12.6,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (196,67,1198,'Device198','Owner198',0.9,0.8,0.5,13,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (197,68,1199,'Device199','Owner199',0.6,0.5,0.8,13.3,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (198,68,1200,'Device200','Owner200',0.7,0.6,0.7,12.7,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (199,69,1201,'Device201','Owner201',0.5,0.4,0.5,13.1,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (200,69,1202,'Device202','Owner202',0.6,0.5,0.6,13.4,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (201,69,1203,'Device203','Owner203',0.8,0.7,0.5,12.8,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (202,70,1204,'Device204','Owner204',0.9,0.8,0.6,13.2,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (203,70,1205,'Device205','Owner205',0.6,0.5,0.8,13.5,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (204,70,1206,'Device206','Owner206',0.7,0.6,0.7,12.9,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (205,71,1207,'Device207','Owner207',0.5,0.4,0.5,13.3,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (206,71,1208,'Device208','Owner208',0.6,0.5,0.6,13.6,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (207,71,1209,'Device209','Owner209',0.8,0.7,0.5,13,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (208,72,1210,'Device210','Owner210',0.9,0.8,0.6,13.4,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (209,72,1211,'Device211','Owner211',0.6,0.5,0.8,13.7,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (210,72,1212,'Device212','Owner212',0.7,0.6,0.7,13.1,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (211,73,1213,'Device213','Owner213',0.5,0.4,0.5,13.5,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (212,73,1214,'Device214','Owner214',0.6,0.5,0.6,13.8,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (213,73,1215,'Device215','Owner215',0.8,0.7,0.5,13.2,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (214,74,1216,'Device216','Owner216',0.9,0.8,0.6,13.6,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (215,74,1217,'Device217','Owner217',0.6,0.5,0.8,13.9,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (216,74,1218,'Device218','Owner218',0.7,0.6,0.7,13.3,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (217,75,1219,'Device219','Owner219',0.5,0.4,0.5,13.7,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (218,75,1220,'Device220','Owner220',0.6,0.5,0.6,14,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (219,75,1221,'Device221','Owner221',0.8,0.7,0.5,13.4,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (220,76,1222,'Device222','Owner222',0.9,0.8,0.6,13.8,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (221,76,1223,'Device223','Owner223',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (222,76,1224,'Device224','Owner224',0.7,0.6,0.7,13.5,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (223,77,1225,'Device225','Owner225',0.5,0.4,0.5,13.9,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (224,77,1226,'Device226','Owner226',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (225,77,1227,'Device227','Owner227',0.8,0.7,0.5,13.6,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (226,78,1228,'Device228','Owner228',0.9,0.8,0.6,14,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (227,78,1229,'Device229','Owner229',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (228,78,1230,'Device230','Owner230',0.7,0.6,0.7,13.7,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (229,79,1231,'Device231','Owner231',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (230,79,1232,'Device232','Owner232',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (231,79,1233,'Device233','Owner233',0.8,0.7,0.5,13.8,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (232,80,1234,'Device234','Owner234',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (233,80,1235,'Device235','Owner235',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (234,80,1236,'Device236','Owner236',0.7,0.6,0.7,13.9,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (235,81,1237,'Device237','Owner237',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (236,81,1238,'Device238','Owner238',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (237,81,1239,'Device239','Owner239',0.8,0.7,0.5,14,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (238,82,1240,'Device240','Owner240',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (239,82,1241,'Device241','Owner241',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (240,82,1242,'Device242','Owner242',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (241,83,1243,'Device243','Owner243',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (242,83,1244,'Device244','Owner244',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (243,83,1245,'Device245','Owner245',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (244,84,1246,'Device246','Owner246',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (245,84,1247,'Device247','Owner247',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (246,84,1248,'Device248','Owner248',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (247,85,1249,'Device249','Owner249',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (248,85,1250,'Device250','Owner250',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (249,85,1251,'Device251','Owner251',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (250,86,1252,'Device252','Owner252',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (251,86,1253,'Device253','Owner253',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (252,86,1254,'Device254','Owner254',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (253,87,1255,'Device255','Owner255',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (254,87,1256,'Device256','Owner256',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (255,87,1257,'Device257','Owner257',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (256,88,1258,'Device258','Owner258',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (257,88,1259,'Device259','Owner259',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (258,88,1260,'Device260','Owner260',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (259,89,1261,'Device261','Owner261',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (260,89,1262,'Device262','Owner262',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (261,89,1263,'Device263','Owner263',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (262,90,1264,'Device264','Owner264',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (263,90,1265,'Device265','Owner265',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (264,90,1266,'Device266','Owner266',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (265,91,1267,'Device267','Owner267',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (266,91,1268,'Device268','Owner268',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (267,91,1269,'Device269','Owner269',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (268,92,1270,'Device270','Owner270',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (269,92,1271,'Device271','Owner271',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (270,92,1272,'Device272','Owner272',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (271,93,1273,'Device273','Owner273',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (272,93,1274,'Device274','Owner274',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (273,93,1275,'Device275','Owner275',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (274,94,1276,'Device276','Owner276',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (275,94,1277,'Device277','Owner277',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (276,94,1278,'Device278','Owner278',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (277,95,1279,'Device279','Owner279',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (278,95,1280,'Device280','Owner280',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (279,95,1281,'Device281','Owner281',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (280,96,1282,'Device282','Owner282',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (281,96,1283,'Device283','Owner283',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (282,96,1284,'Device284','Owner284',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (283,97,1285,'Device285','Owner285',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (284,97,1286,'Device286','Owner286',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (285,97,1287,'Device287','Owner287',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (286,98,1288,'Device288','Owner288',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (287,98,1289,'Device289','Owner289',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (288,98,1290,'Device290','Owner290',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (289,99,1291,'Device291','Owner291',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (290,99,1292,'Device292','Owner292',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (291,99,1293,'Device293','Owner293',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (292,100,1294,'Device294','Owner294',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (293,100,1295,'Device295','Owner295',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (294,100,1296,'Device296','Owner296',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (295,101,1297,'Device297','Owner297',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (296,101,1298,'Device298','Owner298',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (297,101,1299,'Device299','Owner299',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (298,102,1300,'Device300','Owner300',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (299,102,1301,'Device301','Owner301',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (300,102,1302,'Device302','Owner302',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (301,103,1303,'Device303','Owner303',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (302,103,1304,'Device304','Owner304',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (303,103,1305,'Device305','Owner305',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (304,104,1306,'Device306','Owner306',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (305,104,1307,'Device307','Owner307',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (306,104,1308,'Device308','Owner308',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (307,105,1309,'Device309','Owner309',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (308,105,1310,'Device310','Owner310',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (309,105,1311,'Device311','Owner311',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (310,106,1312,'Device312','Owner312',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (311,106,1313,'Device313','Owner313',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (312,106,1314,'Device314','Owner314',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (313,107,1315,'Device315','Owner315',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (314,107,1316,'Device316','Owner316',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (315,107,1317,'Device317','Owner317',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (316,108,1318,'Device318','Owner318',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (317,108,1319,'Device319','Owner319',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (318,108,1320,'Device320','Owner320',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (319,109,1321,'Device321','Owner321',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (320,109,1322,'Device322','Owner322',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (321,109,1323,'Device323','Owner323',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (322,110,1324,'Device324','Owner324',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (323,110,1325,'Device325','Owner325',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (324,110,1326,'Device326','Owner326',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (325,111,1327,'Device327','Owner327',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (326,111,1328,'Device328','Owner328',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (327,111,1329,'Device329','Owner329',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (328,112,1330,'Device330','Owner330',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (329,112,1331,'Device331','Owner331',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (330,112,1332,'Device332','Owner332',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (331,113,1333,'Device333','Owner333',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (332,113,1334,'Device334','Owner334',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (333,113,1335,'Device335','Owner335',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (334,114,1336,'Device336','Owner336',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (335,114,1337,'Device337','Owner337',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (336,114,1338,'Device338','Owner338',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (337,115,1339,'Device339','Owner339',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (338,115,1340,'Device340','Owner340',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (339,115,1341,'Device341','Owner341',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (340,116,1342,'Device342','Owner342',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (341,116,1343,'Device343','Owner343',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (342,116,1344,'Device344','Owner344',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (343,117,1345,'Device345','Owner345',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (344,117,1346,'Device346','Owner346',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (345,117,1347,'Device347','Owner347',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (346,118,1348,'Device348','Owner348',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (347,118,1349,'Device349','Owner349',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (348,118,1350,'Device350','Owner350',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (349,119,1351,'Device351','Owner351',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (350,119,1352,'Device352','Owner352',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (351,119,1353,'Device353','Owner353',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (352,120,1354,'Device354','Owner354',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (353,120,1355,'Device355','Owner355',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (354,120,1356,'Device356','Owner356',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (355,121,1357,'Device357','Owner357',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (356,121,1358,'Device358','Owner358',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (357,121,1359,'Device359','Owner359',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (358,122,1360,'Device360','Owner360',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (359,122,1361,'Device361','Owner361',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (360,122,1362,'Device362','Owner362',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (361,123,1363,'Device363','Owner363',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (362,123,1364,'Device364','Owner364',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (363,123,1365,'Device365','Owner365',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (364,124,1366,'Device366','Owner366',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (365,124,1367,'Device367','Owner367',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (366,124,1368,'Device368','Owner368',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (367,125,1369,'Device369','Owner369',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (368,125,1370,'Device370','Owner370',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (369,125,1371,'Device371','Owner371',0.8,0.7,0.5,11,24,57,90,-73,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (370,16,1372,'Device372','Owner372',0.9,0.8,0.6,11,25,60,100,-70,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (371,16,1373,'Device373','Owner373',0.6,0.5,0.8,11,26,62,110,-68,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (372,12,1374,'Device374','Owner374',0.7,0.6,0.7,11,24.5,58,95,-72,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (373,12,1375,'Device375','Owner375',0.5,0.4,0.5,11,25.5,61,105,-69,'2024-02-01');
INSERT INTO soildata (id, district_id, internal_id, device, owner, nitrogen, phosphorus, potassium, ph, temperature, humidity, conductivity, signal_level, date) VALUES (374,12,1376,'Device376','Owner376',0.6,0.5,0.6,11,26.5,63,115,-67,'2024-02-01');

DROP TABLE IF EXISTS user;
CREATE TABLE `user` (
  id int NOT NULL AUTO_INCREMENT,
  username varchar(150) NOT NULL,
  email varchar(150) NOT NULL,
  `password` varchar(150) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY username (username),
  UNIQUE KEY email (email)
);

INSERT INTO user (id, username, email, password) VALUES (1,'test','test@gmail.com','$5$rounds=535000$oURh/oAV39V4uKwG$lDLn2b/XaOgwtcjxTjtQ6SZkM9b6Qgp8QRx9kQbsjDC');
INSERT INTO user (id, username, email, password) VALUES (2,'brian','brian@gmail.com','pbkdf2:sha256:600000$8sReL4dHK82vojQg$0db10c580717ddaae0e1fdaf25086903c32970af0ab4827ec258f24d0ac34fb0');
INSERT INTO user (id, username, email, password) VALUES (3,'nomena','nomenatsimijaly@gmail.com','pbkdf2:sha256:600000$2jx7brRgdrye3R06$fc947efd719423051921a68fc6e694453bc9021c36c36cbace8dbb77312a0044');

