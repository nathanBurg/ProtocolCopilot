-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE
    protocol_documents (
        document_id UUID NOT NULL DEFAULT uuid_generate_v4(),
        document_name VARCHAR(255) NOT NULL,
        description TEXT,
        object_url VARCHAR(1024) NOT NULL, 
        mime_type VARCHAR(128), 
        ingestion_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (ingestion_status IN ('pending', 'ingested', 'failed')),
        ingested_at TIMESTAMP,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (document_id),
        UNIQUE (object_url)
    );

CREATE TABLE
    protocols (
        protocol_id UUID NOT NULL DEFAULT uuid_generate_v4(),
        document_id UUID NOT NULL,
        protocol_name VARCHAR(255) NOT NULL,
        description TEXT,
        created_by_user_id UUID,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (protocol_id),
        CONSTRAINT fk_protocols_document FOREIGN KEY (document_id) REFERENCES protocol_documents (document_id) ON DELETE RESTRICT ON UPDATE CASCADE
    );

CREATE TABLE
    protocol_steps (
        protocol_step_id UUID NOT NULL DEFAULT uuid_generate_v4(),
        protocol_id UUID NOT NULL,
        step_number INT NOT NULL,
        step_name VARCHAR(255) NOT NULL,
        instruction TEXT NOT NULL,
        expected_duration_minutes INT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (protocol_step_id),
        CONSTRAINT fk_protocol_steps_protocol FOREIGN KEY (protocol_id) REFERENCES protocols (protocol_id) ON DELETE CASCADE ON UPDATE CASCADE,
        UNIQUE (protocol_id, step_number)
    );

CREATE TABLE
    experiments (
        experiment_id UUID NOT NULL DEFAULT uuid_generate_v4(),
        protocol_id UUID NOT NULL,
        user_id UUID,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        status VARCHAR(255) NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (experiment_id),
        CONSTRAINT fk_experiments_protocol FOREIGN KEY (protocol_id) REFERENCES protocols (protocol_id) ON DELETE RESTRICT ON UPDATE CASCADE
    );

CREATE INDEX idx_protocol_id ON experiments (protocol_id);

CREATE TABLE
    experiment_steps (
        experiment_step_id UUID NOT NULL DEFAULT uuid_generate_v4(),
        experiment_id UUID NOT NULL,
        protocol_step_id UUID NOT NULL,
        actual_start_time TIMESTAMP,
        actual_end_time TIMESTAMP,
        status VARCHAR(255) NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (experiment_step_id),
        CONSTRAINT fk_experiment_steps_experiment FOREIGN KEY (experiment_id) REFERENCES experiments (experiment_id) ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT fk_experiment_steps_protocol_step FOREIGN KEY (protocol_step_id) REFERENCES protocol_steps (protocol_step_id) ON DELETE RESTRICT ON UPDATE CASCADE
    );

CREATE INDEX idx_experiment_steps_experiment_id ON experiment_steps (experiment_id);
CREATE INDEX idx_experiment_steps_protocol_step_id ON experiment_steps (protocol_step_id);

CREATE TABLE
    experiment_conversations (
        message_id UUID NOT NULL DEFAULT uuid_generate_v4(),
        experiment_id UUID NOT NULL,
        experiment_step_id UUID,
        sender_role VARCHAR(255) NOT NULL, --  user, agent, system
        message_type VARCHAR(255) NOT NULL, -- instruction, observation, question, response, summary
        content TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (message_id),
        CONSTRAINT fk_conversation_experiment FOREIGN KEY (experiment_id) REFERENCES experiments (experiment_id) ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT fk_conversation_experiment_step FOREIGN KEY (experiment_step_id) REFERENCES experiment_steps (experiment_step_id) ON DELETE SET NULL ON UPDATE CASCADE
    );

CREATE INDEX idx_experiment_conversations_experiment_id ON experiment_conversations (experiment_id);
CREATE INDEX idx_experiment_step_id ON experiment_conversations (experiment_step_id);
CREATE INDEX idx_sender_role ON experiment_conversations (sender_role);
