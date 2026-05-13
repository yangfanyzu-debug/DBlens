-- DBLens MySQL full initialization script.
-- Use this when the target environment cannot run Alembic migrations.
-- If Alembic is available, prefer:
--   1. CREATE DATABASE ...
--   2. python -m alembic upgrade head

CREATE DATABASE IF NOT EXISTS dblens
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE dblens;

CREATE TABLE IF NOT EXISTS connections (
  id VARCHAR(36) NOT NULL,
  name VARCHAR(128) NOT NULL,
  db_type ENUM('mysql', 'postgresql', 'sqlite', 'doris') NOT NULL,
  host VARCHAR(256) NULL,
  port INT NULL,
  username VARCHAR(128) NULL,
  password_enc TEXT NULL,
  `database` VARCHAR(128) NULL,
  group_name VARCHAR(64) NULL,
  ssh_enabled BOOL NULL DEFAULT 0,
  ssh_host VARCHAR(256) NULL,
  ssh_port INT NULL DEFAULT 22,
  ssh_username VARCHAR(128) NULL,
  ssh_password_enc TEXT NULL,
  ssh_private_key TEXT NULL,
  ssl_enabled BOOL NULL DEFAULT 0,
  ssl_ca TEXT NULL,
  ssl_cert TEXT NULL,
  ssl_key TEXT NULL,
  created_at DATETIME NULL,
  updated_at DATETIME NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS query_sessions (
  query_id VARCHAR(36) NOT NULL,
  conn_id VARCHAR(36) NULL,
  `database` VARCHAR(128) NULL,
  sql TEXT NULL,
  status ENUM('running', 'success', 'error', 'killed') NULL DEFAULT 'running',
  db_thread_id INT NULL,
  started_at DATETIME NULL,
  finished_at DATETIME NULL,
  error_msg TEXT NULL,
  PRIMARY KEY (query_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS operation_logs (
  id VARCHAR(36) NOT NULL,
  user_id INT NULL,
  username VARCHAR(128) NULL,
  roles VARCHAR(512) NULL,
  is_admin BOOL NULL DEFAULT 0,
  action VARCHAR(64) NOT NULL,
  resource_type VARCHAR(64) NOT NULL,
  resource_id VARCHAR(128) NULL,
  conn_id VARCHAR(36) NULL,
  db_name VARCHAR(128) NULL,
  table_name VARCHAR(128) NULL,
  sql_text TEXT NULL,
  detail TEXT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'success',
  error_msg TEXT NULL,
  duration_ms INT NULL,
  created_at DATETIME NULL,
  PRIMARY KEY (id),
  INDEX ix_operation_logs_created_at (created_at),
  INDEX ix_operation_logs_user_id (user_id),
  INDEX ix_operation_logs_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS alembic_version (
  version_num VARCHAR(32) NOT NULL,
  PRIMARY KEY (version_num)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DELETE FROM alembic_version;
INSERT INTO alembic_version (version_num) VALUES ('0003');
