CREATE TABLE
    protocol_documents (
        document_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        document_name VARCHAR(255) NOT NULL,
        description TEXT NULL,
        object_url VARCHAR(1024) NOT NULL, 
        mime_type VARCHAR(128) NULL, 
        ingestion_status ENUM ('pending', 'ingested', 'failed') NOT NULL DEFAULT 'pending',
        ingested_at DATETIME NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (document_id),
        UNIQUE KEY uix_object_url (object_url(191))  
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    protocols (
        protocol_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        document_id BIGINT UNSIGNED NOT NULL,
        protocol_name VARCHAR(255) NOT NULL,
        description TEXT NULL,
        created_by_user_id BIGINT UNSIGNED NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (protocol_id),
        CONSTRAINT fk_protocols_document FOREIGN KEY (document_id) REFERENCES protocol_documents (document_id) ON DELETE RESTRICT ON UPDATE CASCADE
    ) ENGINE = InnoDB;

CREATE TABLE
    protocol_steps (
        protocol_step_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        protocol_id BIGINT UNSIGNED NOT NULL,
        step_number INT NOT NULL,
        step_name VARCHAR(255) NOT NULL,
        instruction TEXT NULL,
        expected_duration_minutes INT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (protocol_step_id),
        CONSTRAINT fk_protocol_steps_protocol FOREIGN KEY (protocol_id) REFERENCES protocols (protocol_id) ON DELETE CASCADE ON UPDATE CASCADE,
        UNIQUE KEY uix_protocol_step_number (protocol_id, step_number)
    ) ENGINE = InnoDB;

CREATE TABLE
    experiments (
        experiment_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        protocol_id BIGINT UNSIGNED NOT NULL,
        user_id BIGINT UNSIGNED NULL,
        start_time DATETIME NULL,
        end_time DATETIME NULL,
        status VARCHAR(255) NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (experiment_id),
        CONSTRAINT fk_experiments_protocol FOREIGN KEY (protocol_id) REFERENCES protocols (protocol_id) ON DELETE RESTRICT ON UPDATE CASCADE,
        INDEX idx_protocol_id (protocol_id)
    ) ENGINE = InnoDB;

CREATE TABLE
    experiment_steps (
        experiment_step_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        experiment_id BIGINT UNSIGNED NOT NULL,
        protocol_step_id BIGINT UNSIGNED NOT NULL,
        actual_start_time DATETIME NULL,
        actual_end_time DATETIME NULL,
        status VARCHAR(255) NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (experiment_step_id),
        CONSTRAINT fk_experiment_steps_experiment FOREIGN KEY (experiment_id) REFERENCES experiments (experiment_id) ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT fk_experiment_steps_protocol_step FOREIGN KEY (protocol_step_id) REFERENCES protocol_steps (protocol_step_id) ON DELETE RESTRICT ON UPDATE CASCADE,
        INDEX idx_experiment_id (experiment_id),
        INDEX idx_protocol_step_id (protocol_step_id)
    ) ENGINE = InnoDB;

CREATE TABLE
    experiment_conversations (
        message_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        experiment_id BIGINT UNSIGNED NOT NULL,
        experiment_step_id BIGINT UNSIGNED NULL,
        sender_role VARCHAR(255) NOT NULL, --  user, agent, system
        message_type VARCHAR(255) NOT NULL, -- instruction, observation, question, response, summary
        content TEXT NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (message_id),
        CONSTRAINT fk_conversation_experiment FOREIGN KEY (experiment_id) REFERENCES experiments (experiment_id) ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT fk_conversation_experiment_step FOREIGN KEY (experiment_step_id) REFERENCES experiment_steps (experiment_step_id) ON DELETE SET NULL ON UPDATE CASCADE,
        INDEX idx_experiment_id (experiment_id),
        INDEX idx_experiment_step_id (experiment_step_id),
        INDEX idx_sender_role (sender_role)
    ) ENGINE = InnoDB;
