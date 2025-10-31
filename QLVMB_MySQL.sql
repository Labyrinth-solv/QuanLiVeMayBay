CREATE DATABASE  IF NOT EXISTS `pythonproject` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `pythonproject`;
-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: pythonproject
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `airline`
--

DROP TABLE IF EXISTS `airline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `airline` (
  `name` varchar(30) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `airline`
--

LOCK TABLES `airline` WRITE;
/*!40000 ALTER TABLE `airline` DISABLE KEYS */;
INSERT INTO `airline` VALUES ('China Eastern');
/*!40000 ALTER TABLE `airline` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `airline_staff`
--

DROP TABLE IF EXISTS `airline_staff`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `airline_staff` (
  `username` varchar(30) NOT NULL,
  `password` varchar(30) DEFAULT NULL,
  `first_name` varchar(30) DEFAULT NULL,
  `last_name` varchar(30) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `name` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`username`),
  KEY `name` (`name`),
  CONSTRAINT `airline_staff_ibfk_1` FOREIGN KEY (`name`) REFERENCES `airline` (`name`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `airline_staff`
--

LOCK TABLES `airline_staff` WRITE;
/*!40000 ALTER TABLE `airline_staff` DISABLE KEYS */;
INSERT INTO `airline_staff` VALUES ('mneedle','password','Manny','Needle','2000-12-09','China Eastern');
/*!40000 ALTER TABLE `airline_staff` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `airplane`
--

DROP TABLE IF EXISTS `airplane`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `airplane` (
  `name` varchar(30) NOT NULL,
  `ID` decimal(30,0) NOT NULL,
  `seats` decimal(5,0) DEFAULT NULL,
  PRIMARY KEY (`ID`,`name`),
  KEY `name` (`name`),
  CONSTRAINT `airplane_ibfk_1` FOREIGN KEY (`name`) REFERENCES `airline` (`name`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `airplane`
--

LOCK TABLES `airplane` WRITE;
/*!40000 ALTER TABLE `airplane` DISABLE KEYS */;
INSERT INTO `airplane` VALUES ('China Eastern',12345,50),('China Eastern',54321,100);
/*!40000 ALTER TABLE `airplane` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `airport`
--

DROP TABLE IF EXISTS `airport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `airport` (
  `name` varchar(30) NOT NULL,
  `city` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `airport`
--

LOCK TABLES `airport` WRITE;
/*!40000 ALTER TABLE `airport` DISABLE KEYS */;
INSERT INTO `airport` VALUES ('JFK','New York City'),('PVG','Shanghai');
/*!40000 ALTER TABLE `airport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer` (
  `email` varchar(30) NOT NULL,
  `name` varchar(30) DEFAULT NULL,
  `password` varchar(30) DEFAULT NULL,
  `building_number` decimal(30,0) DEFAULT NULL,
  `street` varchar(30) DEFAULT NULL,
  `city` varchar(30) DEFAULT NULL,
  `state` varchar(30) DEFAULT NULL,
  `phone_number` decimal(30,0) DEFAULT NULL,
  `passport_number` decimal(30,0) DEFAULT NULL,
  `passport_exp` date DEFAULT NULL,
  `passport_country` varchar(30) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  PRIMARY KEY (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer`
--

LOCK TABLES `customer` WRITE;
/*!40000 ALTER TABLE `customer` DISABLE KEYS */;
INSERT INTO `customer` VALUES ('email@123.com','Max Needle','password',123,'East 11th Street','New York','New York',1234567890,12345678,'2020-01-01','United States of America','2000-08-30'),('email@345.com','Matt Needle','password',345,'East 12th Street','New York','New York',1234567891,87654321,'2020-01-01','United States of America','1985-11-03');
/*!40000 ALTER TABLE `customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flight`
--

DROP TABLE IF EXISTS `flight`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flight` (
  `name` varchar(30) NOT NULL,
  `flight_number` decimal(30,0) NOT NULL,
  `dep_date_time` timestamp NOT NULL,
  `dep_airport` varchar(30) DEFAULT NULL,
  `arr_airport` varchar(30) DEFAULT NULL,
  `arr_date_time` timestamp NULL DEFAULT NULL,
  `base_price` decimal(6,2) DEFAULT NULL,
  `ID` decimal(30,0) DEFAULT NULL,
  `status` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`flight_number`,`name`,`dep_date_time`),
  KEY `name` (`name`),
  KEY `dep_airport` (`dep_airport`),
  KEY `arr_airport` (`arr_airport`),
  KEY `ID` (`ID`),
  CONSTRAINT `flight_ibfk_1` FOREIGN KEY (`name`) REFERENCES `airline` (`name`) ON DELETE CASCADE,
  CONSTRAINT `flight_ibfk_2` FOREIGN KEY (`dep_airport`) REFERENCES `airport` (`name`) ON DELETE CASCADE,
  CONSTRAINT `flight_ibfk_3` FOREIGN KEY (`arr_airport`) REFERENCES `airport` (`name`) ON DELETE SET NULL,
  CONSTRAINT `flight_ibfk_4` FOREIGN KEY (`ID`) REFERENCES `airplane` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flight`
--

LOCK TABLES `flight` WRITE;
/*!40000 ALTER TABLE `flight` DISABLE KEYS */;
INSERT INTO `flight` VALUES ('China Eastern',1234567890,'2020-10-11 03:00:00','JFK','PVG','2020-10-11 19:00:00',1000.00,12345,'on-time'),('China Eastern',1234567891,'2020-10-12 03:00:00','PVG','JFK','2020-10-12 19:00:00',1200.00,12345,'on-time'),('China Eastern',1234567892,'2020-10-14 03:00:00','JFK','PVG','2020-10-14 19:00:00',1200.00,54321,'delayed'),('China Eastern',1234567893,'2020-10-15 03:00:00','PVG','JFK','2020-10-15 19:00:00',1000.00,54321,'delayed');
/*!40000 ALTER TABLE `flight` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flight_ratings`
--

DROP TABLE IF EXISTS `flight_ratings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flight_ratings` (
  `rating_id` decimal(5,0) NOT NULL,
  `name` varchar(30) DEFAULT NULL,
  `flight_number` decimal(30,0) DEFAULT NULL,
  `rating` decimal(2,0) DEFAULT NULL,
  `comment` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`rating_id`),
  KEY `name` (`name`),
  KEY `flight_number` (`flight_number`),
  CONSTRAINT `flight_ratings_ibfk_1` FOREIGN KEY (`name`) REFERENCES `airline` (`name`) ON DELETE CASCADE,
  CONSTRAINT `flight_ratings_ibfk_2` FOREIGN KEY (`flight_number`) REFERENCES `flight` (`flight_number`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flight_ratings`
--

LOCK TABLES `flight_ratings` WRITE;
/*!40000 ALTER TABLE `flight_ratings` DISABLE KEYS */;
/*!40000 ALTER TABLE `flight_ratings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `monthly_spending`
--

DROP TABLE IF EXISTS `monthly_spending`;
/*!50001 DROP VIEW IF EXISTS `monthly_spending`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `monthly_spending` AS SELECT 
 1 AS `ID`,
 1 AS `email`,
 1 AS `name`,
 1 AS `flight_number`,
 1 AS `sold_price`,
 1 AS `card_type`,
 1 AS `card_number`,
 1 AS `name_on_card`,
 1 AS `exp_date`,
 1 AS `purchase_date_time`,
 1 AS `relative_month`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `phone_number`
--

DROP TABLE IF EXISTS `phone_number`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `phone_number` (
  `username` varchar(30) NOT NULL,
  `phone_number` decimal(30,0) NOT NULL,
  PRIMARY KEY (`username`,`phone_number`),
  CONSTRAINT `phone_number_ibfk_1` FOREIGN KEY (`username`) REFERENCES `airline_staff` (`username`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phone_number`
--

LOCK TABLES `phone_number` WRITE;
/*!40000 ALTER TABLE `phone_number` DISABLE KEYS */;
/*!40000 ALTER TABLE `phone_number` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ticket`
--

DROP TABLE IF EXISTS `ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticket` (
  `ID` decimal(30,0) NOT NULL,
  `email` varchar(30) DEFAULT NULL,
  `name` varchar(30) DEFAULT NULL,
  `flight_number` decimal(30,0) DEFAULT NULL,
  `sold_price` decimal(6,2) DEFAULT NULL,
  `card_type` varchar(30) DEFAULT NULL,
  `card_number` decimal(30,0) DEFAULT NULL,
  `name_on_card` varchar(30) DEFAULT NULL,
  `exp_date` date DEFAULT NULL,
  `purchase_date_time` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `email` (`email`),
  KEY `name` (`name`),
  KEY `flight_number` (`flight_number`),
  CONSTRAINT `ticket_ibfk_1` FOREIGN KEY (`email`) REFERENCES `customer` (`email`) ON DELETE SET NULL,
  CONSTRAINT `ticket_ibfk_2` FOREIGN KEY (`name`) REFERENCES `airline` (`name`) ON DELETE SET NULL,
  CONSTRAINT `ticket_ibfk_3` FOREIGN KEY (`flight_number`) REFERENCES `flight` (`flight_number`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ticket`
--

LOCK TABLES `ticket` WRITE;
/*!40000 ALTER TABLE `ticket` DISABLE KEYS */;
INSERT INTO `ticket` VALUES (13579,'email@123.com','China Eastern',1234567890,950.00,'credit',1234567887654321,'Max Needle','2025-01-05','2020-01-04 22:00:00'),(24680,'email@123.com','China Eastern',1234567891,1350.00,'debit',8765432112345678,'Max Needle','2024-05-06','2020-01-04 22:00:00');
/*!40000 ALTER TABLE `ticket` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Final view structure for view `monthly_spending`
--

/*!50001 DROP VIEW IF EXISTS `monthly_spending`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `monthly_spending` AS select `ticket`.`ID` AS `ID`,`ticket`.`email` AS `email`,`ticket`.`name` AS `name`,`ticket`.`flight_number` AS `flight_number`,`ticket`.`sold_price` AS `sold_price`,`ticket`.`card_type` AS `card_type`,`ticket`.`card_number` AS `card_number`,`ticket`.`name_on_card` AS `name_on_card`,`ticket`.`exp_date` AS `exp_date`,`ticket`.`purchase_date_time` AS `purchase_date_time`,month((curdate() - cast(`ticket`.`purchase_date_time` as date))) AS `relative_month` from `ticket` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-31 10:33:17
