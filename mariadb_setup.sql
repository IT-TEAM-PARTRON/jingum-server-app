-- Jingum MariaDB initialization
-- IMPORTANT: replace CHANGE_ME_WITH_A_STRONG_PASSWORD before running this file.

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS `qc_jingum`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `qc_jingum`;

CREATE TABLE IF NOT EXISTS `records` (
  `collection` VARCHAR(64) NOT NULL,
  `doc_id` VARCHAR(255) NOT NULL,
  `data` JSON NOT NULL,
  `updated_at` VARCHAR(40) NOT NULL,
  PRIMARY KEY (`collection`, `doc_id`)
) ENGINE=InnoDB
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Accounts for an application running on the same server as MariaDB.
-- DB_HOST=127.0.0.1 uses the 127.0.0.1 account; a Unix socket may use localhost.
CREATE USER IF NOT EXISTS 'jingum'@'127.0.0.1'
  IDENTIFIED BY 'CHANGE_ME_WITH_A_STRONG_PASSWORD';
ALTER USER 'jingum'@'127.0.0.1'
  IDENTIFIED BY 'CHANGE_ME_WITH_A_STRONG_PASSWORD';

CREATE USER IF NOT EXISTS 'jingum'@'localhost'
  IDENTIFIED BY 'CHANGE_ME_WITH_A_STRONG_PASSWORD';
ALTER USER 'jingum'@'localhost'
  IDENTIFIED BY 'CHANGE_ME_WITH_A_STRONG_PASSWORD';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE
  ON `jingum`.* TO 'jingum'@'127.0.0.1';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE
  ON `jingum`.* TO 'jingum'@'localhost';

FLUSH PRIVILEGES;

-- If the application runs on another machine, create a restricted account for
-- that machine instead of using '%'. Replace 10.0.0.25 with the application IP:
--
-- CREATE USER IF NOT EXISTS 'jingum'@'10.0.0.25'
--   IDENTIFIED BY 'CHANGE_ME_WITH_A_STRONG_PASSWORD';
-- ALTER USER 'jingum'@'10.0.0.25'
--   IDENTIFIED BY 'CHANGE_ME_WITH_A_STRONG_PASSWORD';
-- GRANT SELECT, INSERT, UPDATE, DELETE, CREATE
--   ON `jingum`.* TO 'jingum'@'10.0.0.25';
-- FLUSH PRIVILEGES;

SELECT `collection`, COUNT(*) AS `total`
FROM `records`
GROUP BY `collection`;
