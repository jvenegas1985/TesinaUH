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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `asignacion_camas`
--

LOCK TABLES `asignacion_camas` WRITE;
/*!40000 ALTER TABLE `asignacion_camas` DISABLE KEYS */;
INSERT INTO `asignacion_camas` VALUES (4,1,3,'2026-02-11','2026-02-12','Ingreso','',5,'Finalizada','2026-02-11 16:55:22'),(5,2,4,'2026-02-11','2026-02-12','Ingreso','',5,'Finalizada','2026-02-11 16:55:48'),(6,3,9,'2026-02-11',NULL,'Ingreso','',5,'Activa','2026-02-11 16:56:09'),(7,4,7,'2026-02-11',NULL,'Ingreso','',5,'Activa','2026-02-11 16:56:15'),(8,5,2,'2026-02-11',NULL,'Ingreso','',5,'Activa','2026-02-11 16:56:23'),(9,6,8,'2026-02-11',NULL,'Ingreso','',5,'Activa','2026-02-12 00:06:43'),(10,7,1,'2026-02-11',NULL,'Ingreso','',5,'Activa','2026-02-12 00:06:57'),(11,8,5,'2026-02-11',NULL,'Ingreso','',5,'Activa','2026-02-12 00:07:07'),(12,9,6,'2026-02-11',NULL,'Ingreso','',5,'Activa','2026-02-12 00:07:25');
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
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bitacora_pacientes`
--

LOCK TABLES `bitacora_pacientes` WRITE;
/*!40000 ALTER TABLE `bitacora_pacientes` DISABLE KEYS */;
INSERT INTO `bitacora_pacientes` VALUES (17,3,'actividad','2026-02-11 10:55:22','ASIGNACIÓN DE CAMA:\nResidente: ANA MORA\nCama asignada: A-101 (Habitación: Habitación 101)\nMotivo: Ingreso\nObservaciones: \nAsignado por: Jeffry Venegas',5,NULL,'activo',NULL,NULL),(18,4,'actividad','2026-02-11 10:55:48','ASIGNACIÓN DE CAMA:\nResidente: CARLOS JIMÉNEZ\nCama asignada: A-102 (Habitación: Habitación 102)\nMotivo: Ingreso\nObservaciones: \nAsignado por: Jeffry Venegas',5,NULL,'activo',NULL,NULL),(19,9,'actividad','2026-02-11 10:56:09','ASIGNACIÓN DE CAMA:\nResidente: ELENA QUIRÓS\nCama asignada: A-103 (Habitación: Habitación 103)\nMotivo: Ingreso\nObservaciones: \nAsignado por: Jeffry Venegas',5,NULL,'activo',NULL,NULL),(20,7,'actividad','2026-02-11 10:56:15','ASIGNACIÓN DE CAMA:\nResidente: FLOR CASTILLO\nCama asignada: A-104 (Habitación: Habitación 104)\nMotivo: Ingreso\nObservaciones: \nAsignado por: Jeffry Venegas',5,NULL,'activo',NULL,NULL),(21,2,'actividad','2026-02-11 10:56:23','ASIGNACIÓN DE CAMA:\nResidente: JOSÉ VARGAS\nCama asignada: A-105 (Habitación: Habitación 105)\nMotivo: Ingreso\nObservaciones: \nAsignado por: Jeffry Venegas',5,NULL,'activo',NULL,NULL),(22,8,'actividad','2026-02-11 18:06:43','ASIGNACIÓN DE CAMA:\nResidente: JUAN CHAVES\nCama asignada: B-201 (Habitación: Habitación 201)\nMotivo: Ingreso\nObservaciones: \nAsignado por: Jeffry Venegas',5,NULL,'activo',NULL,NULL),(23,1,'actividad','2026-02-11 18:06:57','ASIGNACIÓN DE CAMA:\nResidente: MARÍA RODRÍGUEZ\nCama asignada: B-202 (Habitación: Habitación 202)\nMotivo: Ingreso\nObservaciones: \nAsignado por: Jeffry Venegas',5,NULL,'activo',NULL,NULL),(24,5,'actividad','2026-02-11 18:07:07','ASIGNACIÓN DE CAMA:\nResidente: PATRICIA SÁNCHEZ\nCama asignada: B-203 (Habitación: Habitación 203)\nMotivo: Ingreso\nObservaciones: \nAsignado por: Jeffry Venegas',5,NULL,'activo',NULL,NULL),(25,6,'actividad','2026-02-11 18:07:25','ASIGNACIÓN DE CAMA:\nResidente: RAFAEL RAMÍREZ\nCama asignada: B-204 (Habitación: Habitación 204)\nMotivo: Ingreso\nObservaciones: \nAsignado por: Jeffry Venegas',5,NULL,'activo',NULL,NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `camas`
--

LOCK TABLES `camas` WRITE;
/*!40000 ALTER TABLE `camas` DISABLE KEYS */;
INSERT INTO `camas` VALUES (1,'A-101','Habitación 101','Piso 1','A','Individual','Mantenimiento','Cama eléctrica, barandas laterales abatibles, colchón antiescaras, mesa de noche, llamador de enfermería','Cama en excelente estado, mantenimiento preventivo realizado el 01/02/2026',1,'2026-02-11 16:46:55','2026-02-12 14:22:30'),(2,'A-102','Habitación 102','Piso 1','A','Individual','Disponible','Cama manual, barandas fijas, colchón estándar, mesa de noche, luz de lectura','Requiere revisión de ruedas, hacen ruido al mover',1,'2026-02-11 16:46:55','2026-02-12 14:57:47'),(3,'A-103','Habitación 103','Piso 1','A','Individual','Ocupada','Cama eléctrica, colchón de presión alterna, barandas automáticas, mesa sobrecama','Paciente con alto riesgo de úlceras por presión',1,'2026-02-11 16:46:55','2026-02-11 16:56:09'),(4,'A-104','Habitación 104','Piso 1','A','Individual','Ocupada','Cama estándar, colchón viscoelástico, barandas laterales','Recién desinfectada, lista para nuevo ingreso',1,'2026-02-11 16:46:55','2026-02-11 16:56:15'),(5,'A-105','Habitación 105','Piso 1','A','Doble','Ocupada','Dos camas individuales, separador de ambiente, mesas de noche individuales','Habitación matrimonial, ideal para parejas',1,'2026-02-11 16:46:55','2026-02-11 16:56:23'),(6,'B-201','Habitación 201','Piso 1','B','Individual','Ocupada','Cama eléctrica, colchón de espuma viscoelástica, barandas automáticas','Equipada con televisor y sillón reclinable para visitas',1,'2026-02-11 16:46:55','2026-02-12 00:06:43'),(7,'B-202','Habitación 202','Piso 1','B','Individual','Ocupada','Cama eléctrica, sistema de elevación de paciente','En reparación por falla en motor de elevación, repuestos en camino',1,'2026-02-11 16:46:55','2026-02-12 00:06:57'),(8,'B-203','Habitación 203','Piso 1','B','Individual','Ocupada','Cama bariátrica, capacidad 250kg, colchón de alta densidad','Paciente con obesidad mórbida, cama especial',1,'2026-02-11 16:46:55','2026-02-12 00:07:07'),(9,'B-204','Habitación 204','Piso 1','B','Individual','Ocupada','Cama eléctrica, colchón antiescaras, sistema de oxígeno central','Reservada para ingreso programado 15/02/2026',1,'2026-02-11 16:46:55','2026-02-12 00:07:25'),(10,'B-205','Habitación 205','Piso 1','B','Doble','Disponible','Dos camas, una eléctrica y una manual, separador de privacidad','Habitación compartida, ideal para hermanos',1,'2026-02-11 16:46:55','2026-02-11 16:46:55');
/*!40000 ALTER TABLE `camas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categorias_insumos`
--

DROP TABLE IF EXISTS `categorias_insumos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias_insumos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `activo` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias_insumos`
--

LOCK TABLES `categorias_insumos` WRITE;
/*!40000 ALTER TABLE `categorias_insumos` DISABLE KEYS */;
INSERT INTO `categorias_insumos` VALUES (1,'Medicamentos','Fármacos y medicinas para tratamiento de pacientes',1,'2026-02-12 17:29:50'),(2,'Material de curación','Gasas, vendas, algodón, apósitos, etc.',1,'2026-02-12 17:29:50'),(3,'Insumos de enfermería','Jeringas, agujas, guantes, sondas, etc.',1,'2026-02-12 17:29:50'),(4,'Insumos de limpieza','Productos para limpieza y desinfección',1,'2026-02-12 17:29:50'),(5,'Alimentos y suplementos','Nutrición enteral, suplementos alimenticios',1,'2026-02-12 17:29:50'),(6,'Equipo médico','Equipos y dispositivos médicos reutilizables',1,'2026-02-12 17:29:50'),(7,'Papelería','Material administrativo y oficina',1,'2026-02-12 17:29:50'),(8,'Ropa y textil','Ropa de cama, uniformes, toallas',1,'2026-02-12 17:29:50'),(9,'Insumos de rehabilitación','Material para fisioterapia y rehabilitación',1,'2026-02-12 17:29:50'),(10,'Otros','Insumos varios no categorizados',1,'2026-02-12 17:29:50');
/*!40000 ALTER TABLE `categorias_insumos` ENABLE KEYS */;
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
/*!40000 ALTER TABLE `historial_medico` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insumos`
--

DROP TABLE IF EXISTS `insumos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insumos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `descripcion` text,
  `categoria_id` int DEFAULT NULL,
  `proveedor_id` int DEFAULT NULL,
  `unidad_medida` varchar(50) DEFAULT NULL,
  `stock_actual` int DEFAULT '0',
  `stock_minimo` int DEFAULT '5',
  `precio_compra` decimal(10,2) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `categoria_id` (`categoria_id`),
  KEY `proveedor_id` (`proveedor_id`),
  CONSTRAINT `insumos_ibfk_1` FOREIGN KEY (`categoria_id`) REFERENCES `categorias_insumos` (`id`),
  CONSTRAINT `insumos_ibfk_2` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insumos`
--

LOCK TABLES `insumos` WRITE;
/*!40000 ALTER TABLE `insumos` DISABLE KEYS */;
INSERT INTO `insumos` VALUES (1,'MED-001','ACETAMINOFÉN 500MG','Analgésico y antipirético, caja con 100 tabletas',1,1,'Caja',45,20,1250.00,1,'2026-02-12 17:29:50'),(2,'MED-002','IBUPROFENO 400MG','Antiinflamatorio no esteroideo, caja con 50 tabletas',1,1,'Caja',38,15,1450.00,1,'2026-02-12 17:29:50'),(3,'MED-003','LOSARTÁN 50MG','Antihipertensivo, caja con 30 tabletas',1,7,'Caja',52,20,2200.00,1,'2026-02-12 17:29:50'),(4,'MED-004','METFORMINA 850MG','Antidiabético oral, caja con 60 tabletas',1,7,'Caja',65,25,1850.00,1,'2026-02-12 17:29:50'),(5,'MED-005','AMOXICILINA 500MG','Antibiótico, caja con 14 cápsulas',1,1,'Caja',28,15,2500.00,1,'2026-02-12 17:29:50'),(6,'MED-006','OMEPRAZOL 20MG','Inhibidor de bomba de protones, caja con 28 cápsulas',1,1,'Caja',42,20,3200.00,1,'2026-02-12 17:29:50'),(7,'MED-007','SERTRALINA 50MG','Antidepresivo, caja con 30 tabletas',1,7,'Caja',18,10,3800.00,1,'2026-02-12 17:29:50'),(8,'MED-008','FUROSEMIDA 40MG','Diurético, caja con 20 tabletas',1,7,'Caja',15,8,1950.00,1,'2026-02-12 17:29:50'),(9,'MED-009','ENALAPRIL 10MG','Antihipertensivo, caja con 30 tabletas',1,1,'Caja',22,10,1750.00,1,'2026-02-12 17:29:50'),(10,'MED-010','INSULINA NPH','Insulina humana, frasco de 10ml',1,7,'Frasco',12,5,5200.00,1,'2026-02-12 17:29:50'),(11,'CUR-001','GASAS ESTÉRILES 10X10CM','Paquete con 10 unidades estériles',2,2,'Paquete',85,30,850.00,1,'2026-02-12 17:29:50'),(12,'CUR-002','VENDAS ELÁSTICAS 10CM','Venda de sujeción, unidad',2,2,'Unidad',120,40,550.00,1,'2026-02-12 17:29:50'),(13,'CUR-003','APÓSITOS ADHESIVOS','Caja con 50 unidades, 10x10cm',2,5,'Caja',45,15,1800.00,1,'2026-02-12 17:29:50'),(14,'CUR-004','ALGODÓN HIDRÓFILO','Paquete de 500 gramos',2,2,'Paquete',18,10,1450.00,1,'2026-02-12 17:29:50'),(15,'CUR-005','ESPARADRAPO QUIRÚRGICO','Rollo de 5cm x 10m',2,5,'Rollo',32,15,950.00,1,'2026-02-12 17:29:50'),(16,'CUR-006','GASA VASELINADA','Paquete con 5 unidades',2,2,'Paquete',25,10,2100.00,1,'2026-02-12 17:29:50'),(17,'CUR-007','SUERO FISIOLÓGICO','Botella de 500ml',2,2,'Botella',40,20,750.00,1,'2026-02-12 17:29:50'),(18,'CUR-008','YODO POVIDONA','Frasco de 120ml',2,5,'Frasco',22,12,1250.00,1,'2026-02-12 17:29:50'),(19,'ENF-001','JERINGAS 5ML','Caja con 100 unidades, con aguja',3,3,'Caja',52,20,3800.00,1,'2026-02-12 17:29:50'),(20,'ENF-002','JERINGAS 10ML','Caja con 100 unidades, con aguja',3,3,'Caja',15,20,4200.00,1,'2026-02-12 17:29:50'),(21,'ENF-003','AGUJAS HIPODÉRMICAS','Caja con 100 unidades, calibre 21G',3,3,'Caja',8,25,2800.00,1,'2026-02-12 17:29:50'),(22,'ENF-004','GUANTES DE LÁTEX TALLA M','Caja con 100 pares',3,3,'Caja',15,20,5200.00,0,'2026-02-12 17:29:50'),(23,'ENF-005','GUANTES DE NITRILO TALLA L','Caja con 100 pares, sin látex',3,3,'Caja',8,15,6100.00,1,'2026-02-12 17:29:50'),(24,'ENF-006','SONDAS NASOGÁSTRICAS','Unidad, calibre 16Fr',3,6,'Unidad',22,10,1350.00,1,'2026-02-12 17:29:50'),(25,'ENF-007','CATÉTERES IV','Caja con 50 unidades, calibre 20G',3,6,'Caja',18,10,4500.00,1,'2026-02-12 17:29:50'),(26,'ENF-008','MASCARILLAS QUIRÚRGICAS','Caja con 50 unidades',3,3,'Caja',35,25,1800.00,1,'2026-02-12 17:29:50'),(27,'ENF-009','GORROS QUIRÚRGICOS','Paquete con 20 unidades',3,3,'Paquete',25,15,950.00,1,'2026-02-12 17:29:50'),(28,'LIMP-001','ALCOHOL ETÍLICO 70°','Botella de 1 litro',4,8,'Botella',42,20,950.00,1,'2026-02-12 17:29:50'),(29,'LIMP-002','CLORO COMERCIAL','Botella de 3.78 litros',4,8,'Botella',18,10,1250.00,1,'2026-02-12 17:29:50'),(30,'LIMP-003','JABÓN LÍQUIDO ANTIBACTERIAL','Botella de 1 litro',4,8,'Botella',35,15,1150.00,1,'2026-02-12 17:29:50'),(31,'LIMP-004','DESINFECTANTE DE SUPERFICIES','Botella de 1 litro',4,8,'Botella',22,12,1250.00,1,'2026-02-12 17:29:50'),(32,'LIMP-005','BOLSAS PARA DESECHOS BIOPELIGROSOS','Paquete con 50 unidades, rojo',4,8,'Paquete',12,10,2800.00,1,'2026-02-12 17:29:50'),(33,'LIMP-006','TOALLAS DE PAPEL','Paquete con 100 hojas',4,8,'Paquete',28,15,950.00,1,'2026-02-12 17:29:50'),(34,'ALI-001','SUPLEMENTO NUTRICIONAL ENSURE','Caja con 24 botellas de 237ml, sabor vainilla',5,9,'Caja',15,8,25000.00,1,'2026-02-12 17:29:50'),(35,'ALI-002','GELATINA SIN AZÚCAR','Paquete con 10 sobres, sabor frutas',5,9,'Paquete',42,20,1450.00,1,'2026-02-12 17:29:50'),(36,'ALI-003','PURÉ DE FRUTAS','Bolsa de 1 kg, manzana',5,9,'Bolsa',8,10,1850.00,1,'2026-02-12 17:29:50'),(37,'ALI-004','CREMA DE ARROZ','Paquete de 500 gramos',5,9,'Paquete',8,8,1250.00,1,'2026-02-12 17:29:50'),(38,'ALI-005','AGUA EMBOTELLADA','Caja con 12 botellas de 500ml',5,9,'Caja',25,15,2200.00,1,'2026-02-12 17:29:50'),(39,'EQ-001','GLUCÓMETRO','Medidor de glucosa en sangre, incluye tiras',6,4,'Unidad',5,3,18500.00,1,'2026-02-12 17:29:50'),(40,'EQ-002','TENSIMÓMETRO DIGITAL','Monitor de presión arterial de brazo',6,4,'Unidad',4,3,22500.00,1,'2026-02-12 17:29:50'),(41,'EQ-003','TERMÓMETRO DIGITAL','Termómetro infrarrojo',6,4,'Unidad',8,5,9500.00,1,'2026-02-12 17:29:50'),(42,'EQ-004','OXÍMETRO DE PULSO','Medidor de saturación de oxígeno',6,4,'Unidad',6,4,15800.00,1,'2026-02-12 17:29:50'),(43,'PAP-001','RESMA DE PAPEL CARTA','Resma de 500 hojas, papel bond',7,NULL,'Resma',15,10,3500.00,1,'2026-02-12 17:29:50'),(44,'PAP-002','BOLÍGRAFOS','Caja con 50 unidades, color azul',7,NULL,'Caja',8,5,2500.00,1,'2026-02-12 17:29:50'),(45,'PAP-003','CARPETAS ARCHIVADORAS','Unidad, color negro',7,NULL,'Unidad',22,15,850.00,1,'2026-02-12 17:29:50'),(46,'PAP-004','ETIQUETAS ADHESIVAS','Paquete con 100 etiquetas',7,NULL,'Paquete',12,8,1200.00,1,'2026-02-12 17:29:50'),(47,'TEX-001','SÁBANA HOSPITALARIA','Juego de sábana bajera y encimera',8,10,'Juego',18,10,8500.00,1,'2026-02-12 17:29:50'),(48,'TEX-002','ALMOHADA HOSPITALARIA','Almohada antialérgica',8,10,'Unidad',12,8,6200.00,1,'2026-02-12 17:29:50'),(49,'TEX-003','TOALLA DE BAÑO','Toalla de algodón 70x140cm',8,10,'Unidad',25,15,3800.00,1,'2026-02-12 17:29:50'),(50,'TEX-004','UNIFORME DE ENFERMERÍA','Juego de pants y camisa',8,10,'Juego',8,6,12500.00,1,'2026-02-12 17:29:50'),(51,'REH-001','BANDAS ELÁSTICAS DE RESISTENCIA','Juego de 5 niveles de resistencia',9,6,'Juego',10,5,4500.00,1,'2026-02-12 17:29:50'),(52,'REH-002','PELOTAS DE REHABILITACIÓN','Pelota de 55cm para ejercicios',9,6,'Unidad',6,4,5800.00,1,'2026-02-12 17:29:50'),(53,'REH-003','MASAJEADOR MANUAL','Rodillo de espuma para terapia',9,6,'Unidad',8,5,3200.00,1,'2026-02-12 17:29:50');
/*!40000 ALTER TABLE `insumos` ENABLE KEYS */;
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
/*!40000 ALTER TABLE `medicacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimientos_inventario`
--

DROP TABLE IF EXISTS `movimientos_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientos_inventario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `insumo_id` int NOT NULL,
  `tipo` enum('Entrada','Salida','Ajuste') NOT NULL,
  `cantidad` int NOT NULL,
  `stock_anterior` int NOT NULL,
  `stock_nuevo` int NOT NULL,
  `usuario_id` int DEFAULT NULL,
  `fecha` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `observacion` text,
  PRIMARY KEY (`id`),
  KEY `insumo_id` (`insumo_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `movimientos_inventario_ibfk_1` FOREIGN KEY (`insumo_id`) REFERENCES `insumos` (`id`),
  CONSTRAINT `movimientos_inventario_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos_inventario`
--

LOCK TABLES `movimientos_inventario` WRITE;
/*!40000 ALTER TABLE `movimientos_inventario` DISABLE KEYS */;
INSERT INTO `movimientos_inventario` VALUES (1,1,'Entrada',5,40,45,5,'2026-02-12 17:29:50','Compra OC-2026-001'),(2,2,'Entrada',5,33,38,5,'2026-02-12 17:29:50','Compra OC-2026-001'),(3,5,'Entrada',3,25,28,5,'2026-02-12 17:29:50','Compra OC-2026-001'),(4,9,'Entrada',4,18,22,5,'2026-02-12 17:29:50','Compra OC-2026-001'),(5,11,'Entrada',10,75,85,5,'2026-02-12 17:29:50','Compra OC-2026-002'),(6,12,'Entrada',15,105,120,5,'2026-02-12 17:29:50','Compra OC-2026-002'),(7,14,'Entrada',5,13,18,5,'2026-02-12 17:29:50','Compra OC-2026-002'),(8,17,'Entrada',3,12,15,5,'2026-02-12 17:29:50','Compra OC-2026-003'),(9,18,'Entrada',3,15,18,5,'2026-02-12 17:29:50','Compra OC-2026-003'),(10,19,'Entrada',5,60,65,5,'2026-02-12 17:29:50','Compra OC-2026-003'),(11,21,'Entrada',2,6,8,5,'2026-02-12 17:29:50','Compra OC-2026-003'),(12,3,'Entrada',4,48,52,5,'2026-02-12 17:29:50','Compra OC-2026-004'),(13,4,'Entrada',6,59,65,5,'2026-02-12 17:29:50','Compra OC-2026-004'),(14,6,'Entrada',5,37,42,5,'2026-02-12 17:29:50','Compra OC-2026-004'),(15,13,'Entrada',3,42,45,5,'2026-02-12 17:29:50','Compra OC-2026-005'),(16,15,'Entrada',5,27,32,5,'2026-02-12 17:29:50','Compra OC-2026-005'),(17,16,'Entrada',2,23,25,5,'2026-02-12 17:29:50','Compra OC-2026-005'),(18,27,'Entrada',4,18,22,5,'2026-02-12 17:29:50','Compra OC-2026-005'),(19,29,'Entrada',8,34,42,5,'2026-02-12 17:29:50','Compra OC-2026-006'),(20,30,'Entrada',4,14,18,5,'2026-02-12 17:29:50','Compra OC-2026-006'),(21,31,'Entrada',6,29,35,5,'2026-02-12 17:29:50','Compra OC-2026-006'),(22,1,'Salida',-2,45,43,5,'2026-02-12 17:29:50','Consumo - Residente MARÍA RODRÍGUEZ'),(23,1,'Salida',-1,43,42,5,'2026-02-12 17:29:50','Consumo - Residente JOSÉ VARGAS'),(24,2,'Salida',-1,38,37,5,'2026-02-12 17:29:50','Consumo - Residente ANA MORA'),(25,3,'Salida',-1,52,51,5,'2026-02-12 17:29:50','Consumo - Residente CARLOS JIMÉNEZ'),(26,4,'Salida',-2,65,63,5,'2026-02-12 17:29:50','Consumo - Residente PATRICIA SÁNCHEZ'),(27,5,'Salida',-1,28,27,5,'2026-02-12 17:29:50','Consumo - Residente RAFAEL RAMÍREZ'),(28,11,'Salida',-5,85,80,5,'2026-02-12 17:29:50','Consumo - Curación de herida'),(29,12,'Salida',-3,120,117,5,'2026-02-12 17:29:50','Consumo - Vendajes varios'),(30,17,'Salida',-2,15,13,5,'2026-02-12 17:29:50','Consumo - Administración de medicamentos'),(31,18,'Salida',-1,18,17,5,'2026-02-12 17:29:50','Consumo - Administración de medicamentos'),(32,29,'Salida',-2,42,40,5,'2026-02-12 17:29:50','Consumo - Limpieza habitación 101'),(33,31,'Salida',-1,35,34,5,'2026-02-12 17:29:50','Consumo - Limpieza general'),(34,20,'Ajuste',-5,20,15,5,'2026-02-12 17:29:50','Ajuste por inventario - producto dañado'),(35,24,'Ajuste',-2,12,10,5,'2026-02-12 17:29:50','Ajuste por vencimiento'),(36,37,'Ajuste',-2,10,8,5,'2026-02-12 17:29:50','Ajuste por inventario');
/*!40000 ALTER TABLE `movimientos_inventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orden_compra_detalles`
--

DROP TABLE IF EXISTS `orden_compra_detalles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orden_compra_detalles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `orden_id` int NOT NULL,
  `insumo_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `orden_id` (`orden_id`),
  KEY `insumo_id` (`insumo_id`),
  CONSTRAINT `orden_compra_detalles_ibfk_1` FOREIGN KEY (`orden_id`) REFERENCES `ordenes_compra` (`id`) ON DELETE CASCADE,
  CONSTRAINT `orden_compra_detalles_ibfk_2` FOREIGN KEY (`insumo_id`) REFERENCES `insumos` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orden_compra_detalles`
--

LOCK TABLES `orden_compra_detalles` WRITE;
/*!40000 ALTER TABLE `orden_compra_detalles` DISABLE KEYS */;
INSERT INTO `orden_compra_detalles` VALUES (1,1,1,5,1250.00),(2,1,2,5,1450.00),(3,1,5,3,2500.00),(4,1,9,4,1750.00),(5,2,11,10,850.00),(6,2,12,15,550.00),(7,2,14,5,1450.00),(8,3,17,3,3800.00),(9,3,18,3,4200.00),(10,3,19,5,2800.00),(11,3,21,2,6100.00),(12,4,3,4,2200.00),(13,4,4,6,1850.00),(14,4,6,5,3200.00),(15,5,13,3,1800.00),(16,5,15,5,950.00),(17,5,16,2,2100.00),(18,5,27,4,1250.00),(19,6,29,8,950.00),(20,6,30,4,1250.00),(21,6,31,6,1150.00),(22,7,1,6,1250.00),(23,7,2,6,1450.00),(24,7,5,4,2500.00),(25,8,35,2,25000.00),(26,8,37,5,1850.00),(27,9,17,2,3800.00),(28,9,18,2,4200.00),(29,9,24,4,1350.00),(30,10,38,2,18500.00),(31,10,39,2,22500.00),(32,10,40,3,9500.00),(33,11,5,15,2300.00),(34,11,28,5,2000.00);
/*!40000 ALTER TABLE `orden_compra_detalles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ordenes_compra`
--

DROP TABLE IF EXISTS `ordenes_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ordenes_compra` (
  `id` int NOT NULL AUTO_INCREMENT,
  `numero_orden` varchar(50) NOT NULL,
  `proveedor_id` int NOT NULL,
  `fecha` date NOT NULL,
  `estado` enum('Pendiente','Recibida','Cancelada') DEFAULT 'Pendiente',
  `total` decimal(10,2) DEFAULT '0.00',
  `creado_por` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero_orden` (`numero_orden`),
  KEY `proveedor_id` (`proveedor_id`),
  KEY `creado_por` (`creado_por`),
  CONSTRAINT `ordenes_compra_ibfk_1` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id`),
  CONSTRAINT `ordenes_compra_ibfk_2` FOREIGN KEY (`creado_por`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordenes_compra`
--

LOCK TABLES `ordenes_compra` WRITE;
/*!40000 ALTER TABLE `ordenes_compra` DISABLE KEYS */;
INSERT INTO `ordenes_compra` VALUES (1,'OC-2026-001',1,'2026-02-01','Recibida',28000.00,5,'2026-02-12 17:29:50'),(2,'OC-2026-002',2,'2026-02-03','Recibida',24000.00,5,'2026-02-12 17:29:50'),(3,'OC-2026-003',3,'2026-02-05','Recibida',50200.00,5,'2026-02-12 17:29:50'),(4,'OC-2026-004',7,'2026-02-08','Recibida',35900.00,5,'2026-02-12 17:29:50'),(5,'OC-2026-005',5,'2026-02-10','Recibida',19350.00,5,'2026-02-12 17:29:50'),(6,'OC-2026-006',8,'2026-02-12','Recibida',19500.00,5,'2026-02-12 17:29:50'),(7,'OC-2026-007',1,'2026-02-15','Pendiente',26200.00,5,'2026-02-12 17:29:50'),(8,'OC-2026-008',9,'2026-02-16','Pendiente',59250.00,5,'2026-02-12 17:29:50'),(9,'OC-2026-009',3,'2026-02-17','Pendiente',21400.00,5,'2026-02-12 17:29:50'),(10,'OC-2026-010',4,'2026-02-18','Cancelada',110500.00,5,'2026-02-12 17:29:50'),(11,'OC-2026-0212114256',7,'2026-02-12','Pendiente',44500.00,5,'2026-02-12 17:42:56');
/*!40000 ALTER TABLE `ordenes_compra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `telefono` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `direccion` text,
  `activo` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
INSERT INTO `proveedores` VALUES (1,'FARMACIA COSTARRICENSE S.A.','2256-7890','ventas@farmacostar.com','San José, Calle 20, Edificio Farma, 100 m este de la Catedral',1,'2026-02-12 17:29:50'),(2,'DISTRIBUIDORA MÉDICA NACIONAL','2245-6789','pedidos@dismedica.com','Heredia, Santo Domingo, 200 m norte del Mall Oxígeno',1,'2026-02-12 17:29:50'),(3,'PROVEEDORA GERIÁTRICA S.A.','2234-5678','ventas@provegeriatica.com','Alajuela, Residencial Las Flores, del BAC 300 m oeste',1,'2026-02-12 17:29:50'),(4,'TÉCNICOS EN SALUD CR','2290-1234','cotizaciones@tecnicossalud.com','Cartago, Barrio El Molino, contiguo a la Basílica',1,'2026-02-12 17:29:50'),(5,'INSUMOS HOSPITALARIOS CR','2278-4567','ventas@insumoscr.com','San José, Zapote, 100 m sur del ICE',1,'2026-02-12 17:29:50'),(6,'SUMINISTROS MÉDICOS DEL ESTE','2289-7654','info@suministrosmedicos.com','Curridabat, Condominio Industrial del Este',1,'2026-02-12 17:29:50'),(7,'FARMACÉUTICA NACIONAL','2258-9876','ventas@farmaceuticacr.com','San José, La Uruca, contiguo al Hospital México',1,'2026-02-12 17:29:50'),(8,'PROVEEDORA DE LIMPIEZA INTEGRAL','2250-4321','pedidos@limpiezacr.com','San José, Barrio Tournón, 75 m este de la Iglesia',1,'2026-02-12 17:29:50'),(9,'DISTRIBUIDORA DE ALIMENTOS SALUD','2232-5678','ventas@alimentossalud.com','Heredia, San Francisco, 150 m oeste del Palacio',1,'2026-02-12 17:29:50'),(10,'TEXTILES HOSPITALARIOS CR','2255-7890','ventas@textilescr.com','Alajuela, Barrio San José, del Parque 200 m sur',1,'2026-02-12 17:29:50');
/*!40000 ALTER TABLE `proveedores` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `residentes`
--

LOCK TABLES `residentes` WRITE;
/*!40000 ALTER TABLE `residentes` DISABLE KEYS */;
INSERT INTO `residentes` VALUES (1,'MARÍA','RODRÍGUEZ','QUESADA','101237456','1945-03-12','Femenino','Viudo','COSTA RICA','Barrio Amón, San José, 100 m este de la Plaza de la Democracia','8875-1234','CARLOS RODRÍGUEZ','HIJO','8875-5678','Diabetes tipo 2, Hipertensión arterial','Metformina 850mg, Losartán 50mg','Con ayuda','Lúcido',1),(2,'JOSÉ','VARGAS','MADRIGAL','1056791','1938-07-25','Masculino','Casado','COSTA RICA','Urbanización Lomas del Río, Pavas, San José','8876-9012','ANA VARGAS','ESPOSA','8876-3456','Alzheimer etapa temprana, Artritis reumatoide','Donepezilo 10mg, Ibuprofeno 400mg','Independiente','Desorientado',1),(3,'ANA','MORA','CASTRO','10892035','1950-11-30','Femenino','Soltero','COSTA RICA','Condominio Bosques de Lindora, Santa Ana','7089-4567','LAURA MORA','HIJA','7089-8901','Ninguna','Ninguno','Independiente','Lúcido',1),(4,'CARLOS','JIMÉNEZ','FALLAS','112340566','1935-09-18','Masculino','Divorciado','COSTA RICA','Barrio Fátima, Desamparados, San José','8345-6789','ROBERTO JIMÉNEZ','HIJO','8345-1234','Hipertensión, Osteoporosis, Parkinson','Losartán 50mg, Levodopa/Carbidopa','Dependiente','Lúcido',1),(5,'PATRICIA','SÁNCHEZ','ARAYA','206780124','1942-02-28','Femenino','Casado','COSTA RICA','Barrio San Vicente, Santo Domingo de Heredia','2234-5678','FERNANDO SÁNCHEZ','ESPOSO','2234-9012','Artritis, Colesterol alto','Atorvastatina 20mg','Con ayuda','Lúcido',1),(6,'RAFAEL','RAMÍREZ','CAMPOS','304560780','1948-06-14','Masculino','Viudo','COSTA RICA','Urbanización Los Ángeles, San Rafael de Alajuela','2445-6789','MÓNICA RAMÍREZ','HIJA','2445-1234','Enfermedad Pulmonar Obstructiva Crónica (EPOC)','Salbutamol inhalador','Con ayuda','Lúcido',1),(7,'FLOR','CASTILLO','AGUILAR','407890734','1939-12-05','Femenino','Viudo','COSTA RICA','Barrio El Molino, Cartago centro','2550-7890','JORGE CASTILLO','HIJO','2550-4321','Diabetes tipo 1, Neuropatía diabética','Insulina NPH, Pregabalina 75mg','Dependiente','Desorientado',1),(8,'JUAN','CHAVES','ROJAS','509870124','1944-08-20','Masculino','Casado','COSTA RICA','Barrio El Carmen, Liberia, Guanacaste','2666-7890','MARÍA CHAVES','ESPOSA','2666-5432','Hipertensión, Insuficiencia cardíaca leve','Enalapril 10mg, Furosemida 40mg','Con ayuda','Lúcido',1),(9,'ELENA','QUIRÓS','NAVARRO','608928345','1941-01-15','Femenino','Soltero','COSTA RICA','Barrio El Pacífico, Puntarenas centro','2661-7890','MANUEL QUIRÓS','HERMANO','2661-4321','Hipotiroidismo, Depresión mayor','Levotiroxina 100mcg, Sertralina 50mg','Independiente','Demencia',1);
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (5,'admin','jeffrivg@gmail.com','scrypt:32768:8:1$LeuENiNYjx34I5r1$73b09e440361c3358fbe81ead389ec3c7daf752631f94387ef98ca2b4619533c7690aa76e1894fc59b936642c6aad86fd281b19da35c8dd82fbc9b02ec9a48f9','administrador','Jeffry Venegas',1),(6,'carlos','carlos@ga.com','scrypt:32768:8:1$SbTeVqJQ58DhGzCh$275098fb542809da11aa789de8e173480dd460589b30dd9858455c5b5c6c196054cae4fbffbe6fc612a8c7c0b59651838475c04046f60e1a72329629f10271db','medico','carlos fonseca arrollo',1),(7,'mcampos','mcampos@uh.com','pbkdf2:sha256:1000000$0yacfvl5IVkgexn8$bba6374bed6987e7fdeeeac3ff845b8d7db6a148ccf0ecde3023f68b647aeeaf','enfermeria','Manuel Campos',1),(8,'sesquivel','sesquivel@gmail.com','pbkdf2:sha256:1000000$S7mZ3MkOCTZe6S6H$8c20b8d4c448324f9c02c4413fce5fb8cd307c49eba1e7671069b0a66f6ec358','administrador','Susana Esquivel Sanchez',1);
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

-- Dump completed on 2026-02-12 15:38:45
