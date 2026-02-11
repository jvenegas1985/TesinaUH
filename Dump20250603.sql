CREATE DATABASE  IF NOT EXISTS `proyecto` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `proyecto`;
-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: proyecto
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
-- Table structure for table `administraciones_medicacion`
--

DROP TABLE IF EXISTS `administraciones_medicacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `administraciones_medicacion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `medicacion_id` int NOT NULL,
  `fecha` date NOT NULL,
  `hora_programada` time NOT NULL,
  `hora_administrada` time DEFAULT NULL,
  `administrado_por` int DEFAULT NULL,
  `estado` enum('pendiente','administrada','omitida','atrasada','rechazada') DEFAULT 'pendiente',
  `observaciones` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_admin_medicacion` (`medicacion_id`),
  KEY `fk_admin_usuario` (`administrado_por`),
  CONSTRAINT `fk_admin_medicacion` FOREIGN KEY (`medicacion_id`) REFERENCES `medicacion` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_admin_usuario` FOREIGN KEY (`administrado_por`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `administraciones_medicacion`
--

LOCK TABLES `administraciones_medicacion` WRITE;
/*!40000 ALTER TABLE `administraciones_medicacion` DISABLE KEYS */;
INSERT INTO `administraciones_medicacion` VALUES (15,27,'2026-02-10','10:23:00','09:29:51',5,'administrada','acepto medicamento','2026-02-10 15:29:30'),(16,28,'2026-02-10','10:43:00','09:58:46',5,'administrada','','2026-02-10 15:56:28');
/*!40000 ALTER TABLE `administraciones_medicacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `asignacion_camas`
--

DROP TABLE IF EXISTS `asignacion_camas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `asignacion_camas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cama_id` int NOT NULL,
  `residente_id` int NOT NULL,
  `fecha_asignacion` date NOT NULL,
  `fecha_liberacion` date DEFAULT NULL,
  `motivo` enum('Ingreso','Transferencia','Emergencia','Recuperacion') DEFAULT 'Ingreso',
  `observaciones` text,
  `asignado_por` int DEFAULT NULL,
  `estado` enum('Activa','Finalizada','Cancelada') DEFAULT 'Activa',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `asignado_por` (`asignado_por`),
  KEY `idx_residente` (`residente_id`),
  KEY `idx_cama` (`cama_id`),
  KEY `idx_fecha_asignacion` (`fecha_asignacion`),
  KEY `idx_estado` (`estado`),
  CONSTRAINT `asignacion_camas_ibfk_1` FOREIGN KEY (`cama_id`) REFERENCES `camas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `asignacion_camas_ibfk_2` FOREIGN KEY (`residente_id`) REFERENCES `residentes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `asignacion_camas_ibfk_3` FOREIGN KEY (`asignado_por`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `asignacion_camas`
--

LOCK TABLES `asignacion_camas` WRITE;
/*!40000 ALTER TABLE `asignacion_camas` DISABLE KEYS */;
INSERT INTO `asignacion_camas` VALUES (1,1,93,'2026-02-10',NULL,'Ingreso','',5,'Activa','2026-02-10 22:19:34');
/*!40000 ALTER TABLE `asignacion_camas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bitacora_pacientes`
--

DROP TABLE IF EXISTS `bitacora_pacientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bitacora_pacientes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `residente_id` int NOT NULL,
  `tipo` enum('medicacion','alimentacion','aseo','observacion','incidente','visita','actividad','salud') NOT NULL,
  `fecha_hora` datetime DEFAULT CURRENT_TIMESTAMP,
  `descripcion` text NOT NULL,
  `personal_id` int NOT NULL,
  `evidencia` varchar(255) DEFAULT NULL,
  `estado` enum('activo','modificado','eliminado') DEFAULT 'activo',
  `modificado_por` int DEFAULT NULL,
  `justificacion` text,
  PRIMARY KEY (`id`),
  KEY `residente_id` (`residente_id`),
  KEY `personal_id` (`personal_id`),
  KEY `modificado_por` (`modificado_por`),
  CONSTRAINT `bitacora_pacientes_ibfk_1` FOREIGN KEY (`residente_id`) REFERENCES `residentes` (`id`),
  CONSTRAINT `bitacora_pacientes_ibfk_2` FOREIGN KEY (`personal_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `bitacora_pacientes_ibfk_3` FOREIGN KEY (`modificado_por`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bitacora_pacientes`
--

LOCK TABLES `bitacora_pacientes` WRITE;
/*!40000 ALTER TABLE `bitacora_pacientes` DISABLE KEYS */;
INSERT INTO `bitacora_pacientes` VALUES (1,126,'visita','2026-02-10 09:23:08','familiare',5,NULL,'activo',NULL,NULL),(2,126,'medicacion','2026-02-10 09:58:46','Medicación administrada: anapril 20\nVía: oral\nHora programada: 10:43\nHora administrada: 09:58\nObservaciones: Ninguna',5,NULL,'activo',NULL,NULL),(3,126,'aseo','2026-02-10 09:59:37','baño a las 7 am',5,NULL,'activo',NULL,NULL),(4,126,'incidente','2026-02-10 10:00:33','caida leve',5,NULL,'activo',NULL,NULL),(5,126,'actividad','2026-02-10 10:00:58','recreativa con los demas residentes',5,NULL,'activo',NULL,NULL),(6,126,'salud','2026-02-10 10:01:16','toma signos',5,NULL,'modificado',5,'nuevo ajuste'),(7,126,'salud','2026-02-10 10:05:06','toma signos 85/125',5,NULL,'activo',NULL,NULL),(8,93,'medicacion','2026-02-10 11:39:45','dosis ananapril',5,NULL,'activo',NULL,NULL),(9,126,'salud','2026-02-10 11:54:49','REGISTRO DE HISTORIAL MÉDICO\nFecha: 2026-02-10\nDiagnóstico: AMOXIL\nObservaciones: SIN TOMA\nRegistrado por: Jeffry Venegas',5,NULL,'activo',NULL,NULL),(10,125,'salud','2026-02-10 11:56:43','REGISTRO DE HISTORIAL MÉDICO\nFecha: 2026-02-10\nDiagnóstico: VE MUCHAS SERIES DE SANGRE Y ASESINATOS\nObservaciones: VER MAS SERIES DE ZOMBIES\nRegistrado por: Jeffry Venegas',5,NULL,'activo',NULL,NULL),(11,116,'salud','2026-02-10 14:04:22','Historial Medico\nFecha: 2026-02-10\nDiagnóstico: ZARNA\nObservaciones: VACUNARSE\nRegistrado por: Jeffry Venegas',5,NULL,'activo',NULL,NULL),(12,116,'alimentacion','2026-02-10 14:05:20','especial de sopa de pollo',5,NULL,'activo',NULL,NULL),(13,45,'actividad','2026-02-10 16:16:52','NUEVA CAMA REGISTRADA:\nNúmero: CAMA 001\nHabitación: habitacion 102\nPiso: primer piso\nZona: A\nTipo: Individual\nEstado: Disponible\nRegistrado por: Jeffry Venegas',5,NULL,'activo',NULL,NULL),(14,93,'actividad','2026-02-10 16:19:34','ASIGNACIÓN DE CAMA:\nResidente: Abril Terrón\nCama asignada: CAMA 001 (Habitación: habitacion 102)\nMotivo: Ingreso\nObservaciones: \nAsignado por: Jeffry Venegas',5,NULL,'activo',NULL,NULL);
/*!40000 ALTER TABLE `bitacora_pacientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `camas`
--

DROP TABLE IF EXISTS `camas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `camas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `numero` varchar(20) NOT NULL,
  `habitacion` varchar(50) DEFAULT NULL,
  `piso` varchar(20) DEFAULT NULL,
  `zona` enum('A','B','C','D','UCI','Aislamiento') DEFAULT 'A',
  `tipo` enum('Individual','Doble','UCI','Aislamiento','Rehabilitacion') DEFAULT 'Individual',
  `estado` enum('Disponible','Ocupada','Mantenimiento','Reservada','Inactiva') DEFAULT 'Disponible',
  `caracteristicas` text,
  `observaciones` text,
  `activo` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero` (`numero`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `camas`
--

LOCK TABLES `camas` WRITE;
/*!40000 ALTER TABLE `camas` DISABLE KEYS */;
INSERT INTO `camas` VALUES (1,'CAMA 001','habitacion 102','primer piso','A','Individual','Ocupada','barandas laterales, mesa de noche.','',1,'2026-02-10 22:16:52','2026-02-10 22:19:34');
/*!40000 ALTER TABLE `camas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial_cambios_cama`
--

DROP TABLE IF EXISTS `historial_cambios_cama`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_cambios_cama` (
  `id` int NOT NULL AUTO_INCREMENT,
  `residente_id` int NOT NULL,
  `cama_anterior_id` int DEFAULT NULL,
  `cama_nueva_id` int NOT NULL,
  `fecha_cambio` datetime DEFAULT CURRENT_TIMESTAMP,
  `motivo` varchar(255) DEFAULT NULL,
  `observaciones` text,
  `cambiado_por` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cama_anterior_id` (`cama_anterior_id`),
  KEY `cama_nueva_id` (`cama_nueva_id`),
  KEY `cambiado_por` (`cambiado_por`),
  KEY `idx_residente_cambio` (`residente_id`),
  KEY `idx_fecha_cambio` (`fecha_cambio`),
  CONSTRAINT `historial_cambios_cama_ibfk_1` FOREIGN KEY (`residente_id`) REFERENCES `residentes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `historial_cambios_cama_ibfk_2` FOREIGN KEY (`cama_anterior_id`) REFERENCES `camas` (`id`) ON DELETE SET NULL,
  CONSTRAINT `historial_cambios_cama_ibfk_3` FOREIGN KEY (`cama_nueva_id`) REFERENCES `camas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `historial_cambios_cama_ibfk_4` FOREIGN KEY (`cambiado_por`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_cambios_cama`
--

LOCK TABLES `historial_cambios_cama` WRITE;
/*!40000 ALTER TABLE `historial_cambios_cama` DISABLE KEYS */;
/*!40000 ALTER TABLE `historial_cambios_cama` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial_medico`
--

DROP TABLE IF EXISTS `historial_medico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_medico` (
  `id` int NOT NULL AUTO_INCREMENT,
  `residente_id` int DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `diagnostico` text,
  `observaciones` text,
  PRIMARY KEY (`id`),
  KEY `residente_id` (`residente_id`),
  CONSTRAINT `historial_medico_ibfk_1` FOREIGN KEY (`residente_id`) REFERENCES `residentes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_medico`
--

LOCK TABLES `historial_medico` WRITE;
/*!40000 ALTER TABLE `historial_medico` DISABLE KEYS */;
INSERT INTO `historial_medico` VALUES (20,65,'2024-02-15','Hipertensión arterial','Paciente con presión elevada. Se recomienda control diario.'),(21,65,'2024-03-01','Diabetes tipo 2','Se indicó dieta baja en azúcares y control de glucosa.'),(22,65,'2024-03-20','Infección urinaria','Tratamiento con antibióticos por 7 días.'),(23,65,'2024-04-05','Caída leve','Moretón en el brazo derecho. Se hizo control y no hay fracturas.'),(24,65,'2024-04-22','Revisión general','Estable. Se continuará con tratamiento actual.'),(40,105,'2025-06-03','DIBETES','OBSERVACION POR 15 DIAS'),(42,126,'2026-02-10','ANGUSITA SEVERA','NO PRESENTA MAS SINTOMAS'),(43,126,'2026-02-10','DIFOISIS','SIN COMPLICACIONES'),(44,126,'2026-02-10','AMOXIL','SIN TOMA'),(45,125,'2026-02-10','VE MUCHAS SERIES DE SANGRE Y ASESINATOS','VER MAS SERIES DE ZOMBIES'),(46,116,'2026-02-10','ZARNA','VACUNARSE');
/*!40000 ALTER TABLE `historial_medico` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medicacion`
--

DROP TABLE IF EXISTS `medicacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medicacion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `residente_id` int NOT NULL,
  `medicamento` varchar(100) NOT NULL,
  `dosis` varchar(50) NOT NULL,
  `via_administracion` enum('oral','intravenosa','subcutanea','topica','inhalada') NOT NULL DEFAULT 'oral',
  `frecuencia` varchar(50) NOT NULL,
  `horarios` varchar(100) NOT NULL DEFAULT '08:00',
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date DEFAULT NULL,
  `estado` enum('activa','suspendida','completada') NOT NULL DEFAULT 'activa',
  `notas` text,
  `creado_por` int NOT NULL,
  `creado_en` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `actualizado_en` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `residente_id` (`residente_id`),
  KEY `fk_medicacion_usuario` (`creado_por`),
  CONSTRAINT `fk_medicacion_usuario` FOREIGN KEY (`creado_por`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `medicacion_ibfk_1` FOREIGN KEY (`residente_id`) REFERENCES `residentes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medicacion`
--

LOCK TABLES `medicacion` WRITE;
/*!40000 ALTER TABLE `medicacion` DISABLE KEYS */;
INSERT INTO `medicacion` VALUES (27,126,'ibuprofeno','500','intravenosa','1 vez al día','10:23','2026-02-05','2026-02-27','activa','',5,'2026-02-10 15:23:48','2026-02-10 15:23:48'),(28,126,'anapril','20','oral','1 vez al día','10:43','2026-02-10','2026-02-10','activa','',5,'2026-02-10 15:43:18','2026-02-10 15:43:18');
/*!40000 ALTER TABLE `medicacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `residentes`
--

DROP TABLE IF EXISTS `residentes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `residentes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `apellido1` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `apellido2` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `cedula` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `genero` enum('Masculino','Femenino','Otro') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `estado_civil` enum('Soltero','Casado','Viudo','Divorciado') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `nacionalidad` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `direccion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `telefono_contacto` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `contacto_emergencia_nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `contacto_emergencia_parentesco` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `contacto_emergencia_telefono` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `condiciones_medicas` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `medicamentos_actuales` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `movilidad` enum('Independiente','Con ayuda','Dependiente') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `estado_mental` enum('Lúcido','Desorientado','Demencia','Otro') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`,`cedula`),
  UNIQUE KEY `cedula` (`cedula`)
) ENGINE=InnoDB AUTO_INCREMENT=127 DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `residentes`
--

LOCK TABLES `residentes` WRITE;
/*!40000 ALTER TABLE `residentes` DISABLE KEYS */;
INSERT INTO `residentes` VALUES (15,'Haydée','Rubio','Cárdenas','729784079','1958-03-17','Femenino','Divorciado','Indonesia','Ronda Rosalía Aguado 37, Ceuta, 47349','+34866256323','Florina Roberta Sanmartín Echeverría','Esposo','+34918 67 43 06','Sano','Ninguno','Independiente','Desorientado',1),(16,'Augusto','Barrera','Mariscal','974962561','1931-02-06','Femenino','Casado','Tayikistán','Acceso Cosme Huguet 6, Córdoba, 37981','+34921 385 726','Berta Lastra','Hijo','+34887 47 60 86','Alzheimer','Paracetamol','Con ayuda','Lúcido',1),(17,'Yaiza','Miró','Morillo','621320121','1948-01-09','Femenino','Soltero','Armenia','Cuesta de Vera Corominas 82 Puerta 4 , Girona, 36417','+34 803 02 44 20','Emiliano Omar Calderón Mulet','Nieto','+34973 272 684','Diabetes','Ibuprofeno','Independiente','Lúcido',1),(20,'José','Álamo','Pagès','941898744','1941-10-26','Masculino','Divorciado','Irán','Callejón Virginia Verdugo 858 Piso 6 , Ourense, 46391','+34 882 37 94 88','Paz Andres Pineda','Nieto','+34 947 62 96 21','Diabetes','Paracetamol','Dependiente','Demencia',1),(21,'Sara','Barberá','Molins','266582851','1961-09-08','Femenino','Casado','Malawi','Cañada Ramiro Goñi 9 Piso 8 , Huelva, 33309','+34827 19 94 22','Anselmo Expósito Torre','Hija','+34 887 715 000','Artritis','Ibuprofeno','Con ayuda','Lúcido',1),(22,'Soledad','Alvarado','Marqués','539775362','1942-01-23','Masculino','Soltero','Camerún','Camino Paca Perales 99, Palencia, 03196','+34 918 41 66 70','Encarnacion de Oliva','Hija','+34886 391 324','Hipertensión','Metformina','Con ayuda','Demencia',1),(23,'Ligia','Aller','Menéndez','367403824','1953-08-17','Masculino','Casado','República Centroafricana','Cañada de Ramón Ángel 651 Puerta 4 , Ceuta, 34938','+34927 390 852','Moreno Hierro-Arteaga','Sobrino','+34 821235897','Diabetes','Metformina','Dependiente','Desorientado',1),(24,'Pepe','Morcillo','Villalba','856459100','1945-03-19','Femenino','Viudo','Micronesia','Vial Soraya Colomer 27, Murcia, 31985','+34 810751950','Ciro Ferrández Ordóñez','Hijo','+34957 112 395','Diabetes','Metformina','Dependiente','Desorientado',1),(25,'Ruth','Arroyo','Villalonga','887843779','1938-09-19','Masculino','Casado','Bhután','Calle de Jacobo Calderón 60 Apt. 66 , Badajoz, 10402','+34 703341028','Reynaldo Guillen Serra','Hijo','+34956 845 006','Sano','Ibuprofeno','Dependiente','Lúcido',1),(26,'Jenaro','Bou','Ricart','782282741','1961-12-08','Femenino','Divorciado','Swazilandia','Urbanización Jacinta Urrutia 85 Piso 4 , Tarragona, 03062','+34724457471','Alma Hilda Palomares Guijarro','Nieto','+34955 82 59 89','Diabetes','Ninguno','Independiente','Desorientado',1),(27,'Lola','Herrero','Ribes','695797463','1937-04-25','Femenino','Divorciado','Congo','Vial Rómulo Luz 4, Las Palmas, 36693','+34 928742888','Régulo de Garriga','Hijo','+34 944806877','Diabetes','Paracetamol','Dependiente','Lúcido',1),(28,'Gloria','Mascaró','Manso','968645639','1959-08-25','Masculino','Soltero','Etiopía','Cañada de Flavia Álvaro 551 Puerta 2 , Tarragona, 38104','+34 982366086','Manuelita Vicens Baquero','Hijo','+34862471329','Alzheimer','Metformina','Dependiente','Desorientado',1),(29,'Chema','Ródenas','Correa','263028617','1952-11-27','Masculino','Viudo','Mauricio','Pasadizo de Itziar Cañas 819, Burgos, 31790','+34 849885483','Alonso Ribas Taboada','Hijo','+34975 00 65 28','Artritis','Ibuprofeno','Con ayuda','Lúcido',1),(30,'Anastasio','Sotelo','Lasa','214009060','1946-11-09','Femenino','Soltero','Palau','C. de Segismundo Batalla 66, Madrid, 16006','+34876769750','Desiderio Benavent Espinosa','Hermano','+34884 175 342','Hipertensión','Ninguno','Dependiente','Desorientado',1),(31,'Dan','Amo','Jaume','387201607','1938-09-25','Masculino','Soltero','Swazilandia','Camino Azahar Morán 20, Ceuta, 49145','+34 986 771 462','Dionisia Pereira Gibert','Hija','+34 872 79 83 23','Artritis','Paracetamol','Independiente','Demencia',1),(32,'Juan Francisco','Izquierdo','Olmo','913799798','1954-08-09','Femenino','Casado','Omán','C. de Severo Miranda 495 Puerta 0 , Madrid, 33429','+34822 673 041','Alex Arana-Baeza','Hijo','+34 845 77 21 24','Artritis','Losartán','Con ayuda','Desorientado',1),(33,'Cándida','Vives','Cardona','999633298','1961-10-04','Femenino','Soltero','Iraq','Pasaje de Telmo Torrecilla 7, Navarra, 01689','+34825323842','Olivia Carvajal Pinilla','Hermano','+34 820102940','Artritis','Metformina','Independiente','Demencia',1),(34,'Jordán','Noriega','Arribas','659829604','1933-05-12','Masculino','Soltero','Sudán del Sur','Rambla Chus Peralta 7 Piso 2 , Zamora, 42991','+34806 65 67 47','Vicente Luz Amaya','Hija','+34715 745 869','Artritis','Paracetamol','Con ayuda','Desorientado',1),(35,'Valerio','Royo','Sotelo','256987686','1961-05-01','Femenino','Casado','Sudáfrica','Pasaje Roxana Albero 851 Apt. 55 , Cuenca, 01953','+34 924 10 47 26','Felix Aguilera-Crespo','Hija','+34849 437 797','Alzheimer','Metformina','Con ayuda','Demencia',1),(36,'Odalys','Rey','Exposito','121955770','1952-05-05','Masculino','Viudo','Malta','Camino de Selena Narváez 3 Apt. 25 , Huelva, 32365','+34 925 134 056','Luis Cárdenas Goñi','Hermano','+34900015712','Artritis','Paracetamol','Con ayuda','Lúcido',1),(37,'Sigfrido','Báez','Guzman','746509801','1948-11-08','Masculino','Viudo','República Árabe Siria','Camino Heriberto Campoy 340 Puerta 7 , Alicante, 04490','+34 949825518','Remigio Cerezo','Hija','+34 920 054 203','Alzheimer','Ninguno','Independiente','Lúcido',1),(38,'Eugenio','Seco','Gual','581906687','1931-09-26','Femenino','Casado','Nueva Zelandia','Alameda de León Gálvez 92 Piso 0 , Girona, 15046','+34 879905468','Ciríaco Mateu Baena','Sobrino','+34 988 76 20 77','Alzheimer','Ibuprofeno','Con ayuda','Desorientado',1),(39,'Kike','Teruel','Guardiola','312569798','1940-12-24','Femenino','Divorciado','Noruega','Ronda de Ema Marcos 35, Ávila, 37764','+34826 37 40 82','Melchor Armengol Figuerola','Esposo','+34862 115 184','Hipertensión','Ninguno','Independiente','Demencia',1),(40,'Marcio','Rodríguez','Salazar','631086228','1964-05-30','Femenino','Divorciado','República de Macedonia del Norte','Camino Federico Segovia 42, Zamora, 26328','+34 879 51 52 24','Vicenta Valdés Saura','Esposo','+34 747 22 81 50','Sano','Metformina','Independiente','Demencia',1),(41,'Amalia','Romero','Díaz','609402367','1963-12-15','Masculino','Viudo','Perú','Callejón Lara Ojeda 30 Apt. 58 , Madrid, 16684','+34972 76 17 23','Alma Goñi-Cárdenas','Hijo','+34888211320','Sano','Ninguno','Independiente','Lúcido',1),(42,'Úrsula','Fuertes','Albero','553907606','1959-06-03','Masculino','Soltero','Dominicana','Calle de Goyo Coll 70, La Coruña, 31476','+34 960053341','Fernanda Otero Barrena','Hermano','+34846536624','Hipertensión','Paracetamol','Independiente','Desorientado',1),(43,'Marino','Blanes','Pera','915261542','1952-04-23','Femenino','Casado','Austria','Plaza de Perlita Noriega 3 Piso 7 , Ceuta, 22979','+34 826 203 840','Ascensión Estrada Díaz','Hijo','+34 924 791 829','Hipertensión','Paracetamol','Dependiente','Desorientado',1),(44,'Primitiva','Leal','Carnero','392994640','1957-04-09','Masculino','Soltero','Suriname','Glorieta de Humberto Agustí 57, León, 17432','+34 975 73 88 41','Eutropio de Calvet','Hija','+34983 306 905','Diabetes','Losartán','Dependiente','Lúcido',1),(45,'Primitivo','Gomila','Rovira','105817305','1952-03-17','Femenino','Soltero','Senegal','Camino de Dolores Rocamora 52, Teruel, 18403','+34 871 373 219','Ismael Villegas Cañellas','Hija','+34872 06 95 56','Sano','Ninguno','Independiente','Lúcido',1),(46,'Angelita','Ferrán','Berenguer','682196054','1935-02-25','Masculino','Viudo','Comoras','Via de Vinicio Larrea 4 Piso 1 , Tarragona, 43811','+34845555768','Rodolfo del Isern','Esposo','+34 979662057','Hipertensión','Ninguno','Dependiente','Lúcido',1),(47,'Carmen','Badía','Granados','607599520','1948-03-28','Masculino','Casado','Letonia','Via Cirino Ramis 853, Álava, 06880','+34 942 24 10 80','Dan Solís Bonet','Esposo','+34 974 372 126','Sano','Losartán','Independiente','Desorientado',1),(48,'Ale','Alcaraz','Haro','944412022','1933-12-27','Masculino','Soltero','Bangladesh','Pasadizo Eli Aparicio 6 Piso 7 , Vizcaya, 03397','+34 967240662','Florina Montenegro','Sobrino','+34 877 325 305','Alzheimer','Losartán','Independiente','Lúcido',1),(49,'Sosimo','Narváez','Quintero','168164876','1953-05-09','Masculino','Viudo','Timor-Leste','Pasadizo Maristela Fabra 996 Piso 8 , Murcia, 03768','+34927990004','Raimundo Riera Vicente','Hijo','+34948 30 18 72','Hipertensión','Ninguno','Con ayuda','Demencia',1),(50,'Hortensia','Chamorro','Pareja','127287493','1946-01-25','Femenino','Divorciado','Indonesia','Pasaje de Ernesto Lopez 81, La Rioja, 30617','+34 841528328','Emiliana Uribe Francisco','Hermano','+34807 372 225','Artritis','Ninguno','Independiente','Desorientado',1),(51,'Josep','Torralba','Bauzà','777581262','1942-09-14','Femenino','Soltero','Belice','Camino de Dafne Anguita 77 Apt. 93 , Badajoz, 15355','+34841 146 769','Leonardo Báez Ayuso','Hija','+34974 151 139','Diabetes','Ninguno','Con ayuda','Demencia',1),(52,'Marcelo','Terrón','Palomar','410485684','1948-10-04','Femenino','Viudo','Papua Nueva Guinea','Urbanización Socorro Berrocal 35 Apt. 13 , Vizcaya, 23774','+34 885509478','Gabino Enríquez Cuevas','Nieto','+34 983 440 872','Artritis','Ninguno','Independiente','Desorientado',1),(53,'Matías','Almansa','Lopez','638144969','1936-12-06','Femenino','Soltero','Paraguay','C. Mar Perera 37 Puerta 8 , Badajoz, 01047','+34 983 63 51 72','Natalia Casas Guardia','Nieto','+34 887261360','Sano','Ibuprofeno','Independiente','Demencia',1),(54,'Leopoldo','Espinosa','Somoza','558142879','1942-04-09','Femenino','Casado','Indonesia','Via Borja Guerrero 96 Piso 7 , Zamora, 21655','+34 981 679 626','Emilio Piñol Aragonés','Hermano','+34974910941','Diabetes','Ninguno','Dependiente','Desorientado',1),(55,'Aitor','Pozuelo','Ureña','605394589','1941-08-27','Femenino','Soltero','El Salvador','Vial Miguel Escobar 11 Piso 8 , Cantabria, 38489','+34878 40 69 03','Griselda Redondo Gargallo','Hijo','+34 942 003 180','Artritis','Ninguno','Independiente','Lúcido',1),(57,'Fidel','Alfaro','Cánovas','320261612','1929-11-26','Femenino','Viudo','Bulgaria','Plaza Pascuala Iriarte 85 Apt. 70 , Jaén, 34504','+34 985 414 840','Édgar Domínguez Gracia','Hijo','+34877 97 21 17','Hipertensión','Metformina','Independiente','Desorientado',1),(58,'Cándido','Araujo','Torralba','503539312','1937-10-28','Masculino','Casado','Mauricio','Alameda Reynaldo Alberdi 6, Ceuta, 27474','+34 986 831 797','Abraham Cuenca Tejera','Sobrino','+34 849 80 64 24','Diabetes','Ibuprofeno','Dependiente','Lúcido',1),(59,'Ainara','Lara','Paz','149157425','1959-04-11','Masculino','Soltero','Cuba','Vial de Javiera Tormo 72 Apt. 30 , Salamanca, 39556','+34 885436026','Íñigo Badía-Valencia','Esposo','+34 845634523','Hipertensión','Ninguno','Dependiente','Desorientado',1),(60,'Lucas','Casas','Fernández','990156833','1950-03-14','Femenino','Viudo','Islas Salomón','Cuesta Juan José Gisbert 45 Puerta 9 , Guadalajara, 32359','+34 876 140 030','Clarisa Arce Martínez','Esposo','+34900885325','Diabetes','Paracetamol','Con ayuda','Lúcido',1),(65,'REBECA','LUNA','BOLAÑOS','412025665','2005-11-24','Femenino','Soltero','COSTA RICA','ALAJUELA','89754526','ANGELICA LUNA BOLAÑOS','HERMANA','88995566','LOQUERA','LORAZEPAN','Independiente','Demencia',1),(66,'FUGIAT','ALIAS','EXERCITATI','Animi voluptas moll','1995-01-27','Otro','Soltero','ET HIC NULLA MAXIME','NIHIL ET QUASI AB VO','+1 (121) 806-5223','SOLUTA ID LAUDANTIU','NULLA FUGIAT VOLUPT','Et consequat Corpor','EXPEDITA EST EXERCI','ASPERIORES DELENITI','Dependiente','Demencia',1),(67,'Manola','Haro','Uribe','919545643','1934-08-09','Masculino','Divorciado','Bahrein','Acceso de Benigna Manso 403, Badajoz, 20532','+34 922 06 82 33','Encarnacion Rovira Elorza','Sobrino','+34944 67 04 82','Alzheimer','Losartán','Con ayuda','Demencia',1),(68,'Eloy','Machado','Almazán','910517301','1935-03-23','Masculino','Divorciado','Bosnia y Herzegovina','Glorieta Narcisa Pou 7, Guipúzcoa, 09412','+34872 43 89 73','Alcides Mateu Carbó','Sobrino','+34987738333','Alzheimer','Ninguno','Con ayuda','Desorientado',1),(69,'Manu','Ortuño','Orozco','442983430','1950-09-25','Masculino','Casado','República Checa','Ronda de Cristina Pacheco 739, Cuenca, 38475','+34744 25 78 76','Blanca Rosales Riquelme','Hija','+34807877218','Hipertensión','Metformina','Dependiente','Desorientado',1),(70,'Isaías','Cárdenas','Pablo','825736898','1939-05-24','Masculino','Divorciado','Azerbaiyán','Callejón Pedro Carbonell 12, Valladolid, 29852','+34 823417693','Sarita Badía Figuerola','Hermano','+34814 280 228','Diabetes','Ibuprofeno','Con ayuda','Demencia',1),(71,'Nicodemo','Andres','Mora','665685090','1938-05-28','Femenino','Casado','Uruguay','Acceso Gema Paredes 9 Piso 6 , Zamora, 21844','+34971 889 114','Eusebio Canals','Esposo','+34 885 961 434','Hipertensión','Ninguno','Independiente','Lúcido',1),(72,'Ruben','Contreras','Riquelme','755388706','1949-05-10','Femenino','Soltero','España','Cañada de Almudena Tejada 49, Barcelona, 03478','+34 949 08 37 58','Lilia Celestina Cózar Albero','Esposo','+34 926 56 56 30','Alzheimer','Ibuprofeno','Con ayuda','Demencia',1),(73,'Bernabé','Cabello','Cabeza','484628442','1955-09-18','Masculino','Casado','Belice','Plaza de Osvaldo Marin 37 Puerta 2 , Huelva, 34922','+34 988 90 16 70','David de Sastre','Hijo','+34874819892','Sano','Losartán','Con ayuda','Desorientado',1),(74,'Ale','Sola','Clemente','466841151','1944-12-25','Femenino','Soltero','Vietman','Acceso Raimundo Ramírez 45 Piso 0 , Granada, 32934','+34976 792 407','Clotilde Madrid Perera','Hija','+34 828 97 85 41','Alzheimer','Ninguno','Independiente','Lúcido',1),(75,'Agapito','Perez','Ballester','598670309','1946-01-03','Masculino','Soltero','Chipre','Pasaje Jeremías Vigil 91 Puerta 2 , Córdoba, 24533','+34820 42 01 40','Quique Ariel Caballero Ojeda','Hijo','+34 981429751','Hipertensión','Ninguno','Con ayuda','Lúcido',1),(76,'Albino','Clavero','Benítez','223372159','1954-05-30','Masculino','Viudo','República de Macedonia del Norte','Vial Francisco Jose Lara 6 Apt. 22 , Ávila, 36233','+34 914670821','Calisto Clavero','Nieto','+34 900 500 618','Sano','Ninguno','Con ayuda','Lúcido',1),(77,'Jordán','Sastre','Cobo','969315517','1950-11-16','Femenino','Soltero','Granada','Calle de Beatriz Camacho 8, Valencia, 44894','+34 882587341','Nazaret Eugenia Montero Camacho','Sobrino','+34 900468868','Alzheimer','Paracetamol','Con ayuda','Desorientado',1),(78,'Andrés','Puente','Álamo','932229771','1954-08-31','Femenino','Casado','Guinea','Calle Pía Pujadas 4 Piso 4 , Pontevedra, 50812','+34 901 190 271','Inmaculada Vila','Hija','+34986976892','Hipertensión','Metformina','Con ayuda','Lúcido',1),(79,'Rosa','Cerro','Capdevila','149503013','1947-10-06','Femenino','Divorciado','Malawi','Avenida Cebrián Aragonés 61, Vizcaya, 34002','+34 881616757','Valentín Goicoechea Sanz','Hermano','+34926 249 686','Diabetes','Ibuprofeno','Dependiente','Lúcido',1),(80,'Guadalupe','Benavente','Barrera','260778981','1963-02-09','Masculino','Viudo','Granada','Cuesta Geraldo Boada 39, Segovia, 26132','+34 877 664 849','Alba Gárate Ríos','Hermano','+34988 23 36 94','Artritis','Paracetamol','Con ayuda','Desorientado',1),(81,'Dora','Escudero','Feliu','747667447','1955-10-25','Masculino','Soltero','Maldivas','Glorieta de Palmira Batalla 62 Piso 4 , Almería, 20613','+34945 156 379','Eva Camps Marquez','Hijo','+34 942 765 448','Alzheimer','Metformina','Independiente','Demencia',1),(82,'Eutimio','Jurado','Barco','251676619','1940-02-21','Masculino','Casado','Timor-Leste','Avenida de Herminio Torrent 48, Cádiz, 38065','+34 823911206','Édgar Bonet Pujol','Sobrino','+34825 883 570','Diabetes','Ibuprofeno','Independiente','Lúcido',1),(83,'Lilia','Téllez','Ponce','340749474','1935-08-09','Masculino','Divorciado','Islandia','Plaza Angelita Valverde 6, León, 38358','+34 971 566 416','Eufemia Gimenez Soriano','Hijo','+34984 215 184','Alzheimer','Metformina','Independiente','Desorientado',1),(84,'Elpidio','Sedano','Amigó','759301044','1937-11-06','Masculino','Divorciado','Canadá','C. Pepita Cabrera 943, Tarragona, 49886','+34 930 862 524','Andrea Nuñez-Calderon','Hija','+34 883482912','Diabetes','Paracetamol','Con ayuda','Lúcido',1),(85,'Bibiana','Ayllón','Barrera','724338108','1952-05-11','Masculino','Casado','Somalia','Plaza Saturnino Peñas 45, Álava, 48439','+34 823 958 242','Francisca Coronado Arce','Esposo','+34 901 38 82 58','Hipertensión','Ibuprofeno','Con ayuda','Demencia',1),(86,'JUAN CARLOS','VIÑAS','LILLO','853444270','1962-01-11','Masculino','Casado','REPÚBLICA POPULAR DEMOCRÁTICA DE COREA','CAMINO NIDIA PELÁEZ 27 PUERTA 7 , BALEARES, 08470','+34846 239 802','JULIO CÉSAR MÁRMOL','SOBRINO','+34901 280 057','ALZHEIMER','LOSARTÁN','Dependiente','Lúcido',1),(87,'Juan Francisco','Jiménez','Narváez','121858786','1945-12-02','Masculino','Divorciado','Sudáfrica','Avenida de Galo Vara 849 Apt. 94 , Castellón, 29828','+34824 69 21 62','José Luis Puerta Campoy','Hijo','+34 844 612 545','Alzheimer','Paracetamol','Independiente','Desorientado',1),(88,'Amelia','Hierro','Amor','732677422','1958-05-01','Femenino','Casado','Jordania','Camino Paz Sola 3 Piso 2 , Navarra, 51511','+34 880039677','Jesusa Carreras Coloma','Hermano','+34 849876042','Hipertensión','Ninguno','Dependiente','Lúcido',1),(89,'Toni','Carbonell','Buendía','545011691','1950-10-25','Masculino','Soltero','Maldivas','Urbanización de Febe Fabra 60 Apt. 29 , Baleares, 05298','+34 837803522','Ana Blasco Donoso','Sobrino','+34960130053','Hipertensión','Losartán','Dependiente','Desorientado',1),(90,'Teófilo','Bernat','Sanz','406102292','1932-04-20','Masculino','Soltero','Finlandia','Urbanización de Modesta Márquez 28 Puerta 6 , Murcia, 03990','+34 902 974 552','Malena Mulet Tormo','Hija','+34875572956','Diabetes','Ibuprofeno','Independiente','Lúcido',1),(91,'Olga','Amores','Solís','622822932','1948-12-29','Femenino','Divorciado','Luxemburgo','Pasaje Bárbara Jiménez 580 Puerta 8 , Huesca, 28794','+34922 94 28 70','Cipriano Barragán Cifuentes','Nieto','+34806 773 935','Artritis','Losartán','Con ayuda','Lúcido',1),(92,'Renato','Bauzà','Rocha','923299087','1949-09-23','Masculino','Viudo','Letonia','Cuesta de Rosalva Pareja 40, Guipúzcoa, 22389','+34 944026200','Azucena del Cáceres','Esposo','+34 943671802','Sano','Ibuprofeno','Con ayuda','Demencia',1),(93,'Abril','Terrón','Salas','416851838','1931-01-27','Femenino','Casado','República Dominicana','Acceso Nereida Tejedor 2 Piso 7 , Zamora, 09084','+34 924753134','Azahar Acedo Malo','Nieto','+34 880297112','Sano','Metformina','Dependiente','Desorientado',1),(94,'Felipe','Estevez','Bas','408549125','1955-10-20','Masculino','Casado','Saint Kitts y Nevis','Pasadizo de Eliana Calvet 262, Asturias, 30349','+34 980947901','Reynaldo Mate Solsona','Hija','+34 872430631','Diabetes','Ninguno','Con ayuda','Desorientado',1),(95,'Agapito','Pujol','Carnero','990004639','1951-02-06','Femenino','Soltero','Croacia','Callejón de Fidela Lasa 1 Apt. 82 , Baleares, 17528','+34825 36 49 47','Rodrigo Ramirez-Llorente','Nieto','+34 707 42 09 57','Sano','Losartán','Dependiente','Lúcido',1),(96,'Mario','Manjón','Nogués','834055760','1965-02-03','Femenino','Divorciado','China','Plaza Julián Puga 88 Piso 3 , Córdoba, 21220','+34901 53 54 49','Olegario Lasa Benavides','Nieto','+34848 150 788','Hipertensión','Paracetamol','Dependiente','Demencia',1),(97,'Joel','Peralta','Arregui','234442625','1962-12-30','Masculino','Casado','Colombia','Calle Valerio Sureda 2 Piso 9 , Vizcaya, 44793','+34946 28 03 42','Isabel Llamas Velasco','Hija','+34874242221','Alzheimer','Ninguno','Independiente','Desorientado',1),(98,'Toribio','Querol','Cueto','527503190','1931-10-19','Masculino','Casado','Guatemala','Ronda de Lorenzo Prieto 35 Puerta 6 , Zaragoza, 11588','+34977 867 521','Omar Llamas Isern','Nieto','+34924 766 398','Alzheimer','Ibuprofeno','Dependiente','Desorientado',1),(99,'Isidoro','Esteve','Gutiérrez','250173341','1935-01-16','Masculino','Divorciado','Costa Rica','Via Calisto Bueno 79, Huesca, 44024','+34 884795020','Eleuterio Barberá Carrasco','Hijo','+34 947 79 01 77','Artritis','Ibuprofeno','Con ayuda','Desorientado',1),(100,'Rosario','Lerma','Mateos','177072532','1948-01-29','Femenino','Viudo','República Popular Democrática de Corea','Acceso María Cristina Chacón 681, Alicante, 46128','+34927469056','Esperanza Nuñez Solano','Hijo','+34946 243 282','Sano','Ibuprofeno','Independiente','Lúcido',1),(101,'Chucho','Vigil','Cáceres','557826927','1962-04-09','Femenino','Soltero','República Árabe Siria','Urbanización de Joan Izaguirre 52, Pontevedra, 14047','+34 975 948 290','Patricio Cerdán Estrada','Nieto','+34 927 20 20 36','Sano','Ninguno','Con ayuda','Lúcido',1),(102,'Francisco Javier','Calvet','Teruel','455222295','1949-07-25','Masculino','Viudo','Francia','Vial de Anastasio Company 55, León, 22206','+34942 829 700','Yaiza Fernandez','Hija','+34836 87 07 83','Alzheimer','Metformina','Dependiente','Desorientado',1),(103,'Marcelo','Vall','Álamo','801584506','1959-12-07','Masculino','Divorciado','Rwanda','Pasaje de Eufemia Villegas 614 Apt. 54 , Soria, 11218','+34949233248','Narciso Soler Cabañas','Esposo','+34946 26 67 16','Diabetes','Losartán','Con ayuda','Lúcido',1),(104,'Montserrat','Vallejo','Rocamora','547871891','1934-12-20','Masculino','Divorciado','Malta','Camino Inés Sabater 15 Apt. 18 , León, 38778','+34884 91 23 89','Urbano del Doménech','Nieto','+34719 161 932','Artritis','Metformina','Independiente','Demencia',1),(105,'María','Quintana','Céspedes','571001728','1945-04-14','Femenino','Soltero','Gabón','C. Dolores Ríos 7 Piso 8 , Salamanca, 51924','+34843841976','Conrado Teruel Nicolau','Hija','+34 986 806 843','Diabetes','Metformina','Con ayuda','Lúcido',1),(106,'Ámbar','Jimenez','Torrent','710051123','1949-02-04','Femenino','Viudo','Etiopía','Camino de Anabel Carbonell 946, La Rioja, 51906','+34979 288 448','Renato Estévez','Hija','+34 708357708','Diabetes','Metformina','Dependiente','Lúcido',1),(107,'Jenaro','Reyes','Mariscal','576461571','1944-08-17','Femenino','Divorciado','Italia','Paseo Jimena Múñiz 21 Piso 8 , Sevilla, 12010','+34 921587421','Marco Torrents Codina','Hijo','+34 943 42 60 41','Alzheimer','Ninguno','Dependiente','Lúcido',1),(108,'Poncio','Cabañas','Garzón','519784251','1948-02-12','Femenino','Soltero','Armenia','Callejón de Cosme Cañizares 764, Lleida, 43960','+34 985 28 93 13','Custodia Valderrama Niño','Hijo','+34971 23 37 87','Alzheimer','Paracetamol','Dependiente','Demencia',1),(110,'Araceli','Huguet','Castells','684860968','1942-05-27','Masculino','Soltero','Australia','Glorieta Tecla Rueda 84, Tarragona, 32037','+34 916883699','Federico Tristán España Tamarit','Nieto','+34826133846','Sano','Ninguno','Con ayuda','Lúcido',1),(111,'Celso','Cabrera','Tormo','589515155','1942-09-15','Femenino','Divorciado','Namibia','Cañada de Saturnina Tormo 83, Málaga, 22854','+34 881552488','Reyes Patiño Anguita','Nieto','+34 711 134 526','Sano','Ibuprofeno','Con ayuda','Desorientado',1),(112,'Buenaventura','Pellicer','Cañas','704175912','1938-07-19','Masculino','Viudo','Jordania','Glorieta Pepe Porcel 558 Puerta 6 , Guadalajara, 36615','+34 946 813 342','Nélida Vázquez Navarro','Hija','+34 987 84 37 21','Diabetes','Losartán','Independiente','Demencia',1),(113,'Domingo','Gallego','Torrijos','578887544','1963-01-13','Femenino','Soltero','Ecuador','Cañada Chuy Barros 922 Apt. 33 , Cantabria, 12575','+34973 983 741','Clara Polo Alcalde','Nieto','+34 887 694 766','Hipertensión','Ibuprofeno','Dependiente','Demencia',1),(114,'Víctor','León','Matas','455892246','1930-04-08','Femenino','Viudo','Belice','Glorieta Ámbar Carreño 19 Puerta 8 , Álava, 17420','+34 841 41 96 83','Juan Francisco Calleja Murillo','Esposo','+34717 45 07 67','Sano','Ninguno','Dependiente','Desorientado',1),(115,'Teodora','Noguera','Rocamora','609379346','1964-02-28','Femenino','Soltero','Rwanda','Ronda Hortensia Acosta 23, La Rioja, 51977','+34923958468','Lope Cadenas Gonzalo','Esposo','+34949 371 287','Sano','Ninguno','Independiente','Lúcido',1),(116,'Victorino','Toro','Amigó','641067641','1955-01-02','Masculino','Casado','República Democrática Popular Lao','Glorieta de Aurelia Tejedor 44 Piso 7 , Toledo, 13266','+34 887962810','patric','Nieto','+34928 202 862','Diabetes','Ibuprofeno','Con ayuda','Lúcido',1),(125,'SUSANA','ESQUIVEL','SANCHEZ','111111','2005-10-18','Femenino','Soltero','COSTA RICA','HEREDIA','88555555','TATAN','PADRE','888888',NULL,NULL,'Independiente','Demencia',1),(126,'CARLOS','FONSECA','ARROYO','2222','2026-01-30','Masculino','Divorciado','COSTA RICA','HEREDIA','88555555','DIEGO','PADRE','888888',NULL,NULL,'Independiente','Lúcido',0);
/*!40000 ALTER TABLE `residentes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `correo` varchar(100) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `rol` enum('administrador','medico','enfermeria','cuidador','bodega','farmacia','personal_salud') NOT NULL,
  `nombre` varchar(100) DEFAULT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  UNIQUE KEY `correo` (`correo`),
  KEY `idx_rol` (`rol`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (5,'admin','jeffrivg@gmail.com','scrypt:32768:8:1$LeuENiNYjx34I5r1$73b09e440361c3358fbe81ead389ec3c7daf752631f94387ef98ca2b4619533c7690aa76e1894fc59b936642c6aad86fd281b19da35c8dd82fbc9b02ec9a48f9','administrador','Jeffry Venegas',1),(6,'carlos','carlos@ga.com','scrypt:32768:8:1$SbTeVqJQ58DhGzCh$275098fb542809da11aa789de8e173480dd460589b30dd9858455c5b5c6c196054cae4fbffbe6fc612a8c7c0b59651838475c04046f60e1a72329629f10271db','medico','carlos fonseca arrollo',1),(7,'mcampos','mcampos@uh.com','pbkdf2:sha256:1000000$0yacfvl5IVkgexn8$bba6374bed6987e7fdeeeac3ff845b8d7db6a148ccf0ecde3023f68b647aeeaf','enfermeria','Manuel Campos',1);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-11  7:16:58
