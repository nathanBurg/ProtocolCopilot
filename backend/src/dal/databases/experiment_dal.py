from typing import List, Optional
from psycopg2.extras import RealDictCursor
from .psql_client import PostgreSQLClient
from ...core.entities.experiment_entities import Experiment, ExperimentStep, ExperimentConversation, SenderRole, MessageType


class ExperimentDAL:
    def __init__(self):
        self.db_client = PostgreSQLClient()

    # =============================================================================
    # EXPERIMENT CRUD OPERATIONS
    # =============================================================================

    def create_experiment(self, experiment: Experiment) -> Experiment:
        """Create a new experiment in the database."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = """
                INSERT INTO experiments 
                (experiment_id, protocol_id, user_id, start_time, end_time, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (experiment_id) DO UPDATE SET
                    protocol_id = EXCLUDED.protocol_id,
                    user_id = EXCLUDED.user_id,
                    start_time = EXCLUDED.start_time,
                    end_time = EXCLUDED.end_time,
                    status = EXCLUDED.status,
                    updated_at = EXCLUDED.updated_at
                RETURNING *
            """
            cursor.execute(sql, (
                str(experiment.experiment_id),
                str(experiment.protocol_id),
                str(experiment.user_id) if experiment.user_id else None,
                experiment.start_time,
                experiment.end_time,
                experiment.status,
                experiment.created_at,
                experiment.updated_at
            ))
            result = cursor.fetchone()
            conn.commit()
            
            return Experiment(**dict(result))
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error creating experiment: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """Get an experiment by ID."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "SELECT * FROM experiments WHERE experiment_id = %s"
            cursor.execute(sql, (experiment_id,))
            result = cursor.fetchone()
            
            if result:
                return Experiment(**dict(result))
            return None
        except Exception as e:
            raise Exception(f"Error getting experiment: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_all_experiments(self) -> List[Experiment]:
        """Get all experiments."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "SELECT * FROM experiments ORDER BY created_at DESC"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            return [Experiment(**dict(row)) for row in results]
        except Exception as e:
            raise Exception(f"Error getting all experiments: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_experiments_by_protocol_id(self, protocol_id: str) -> List[Experiment]:
        """Get all experiments for a specific protocol."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "SELECT * FROM experiments WHERE protocol_id = %s ORDER BY created_at DESC"
            cursor.execute(sql, (protocol_id,))
            results = cursor.fetchall()
            
            return [Experiment(**dict(row)) for row in results]
        except Exception as e:
            raise Exception(f"Error getting experiments by protocol ID: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_experiments_by_user_id(self, user_id: str) -> List[Experiment]:
        """Get all experiments for a specific user."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "SELECT * FROM experiments WHERE user_id = %s ORDER BY created_at DESC"
            cursor.execute(sql, (user_id,))
            results = cursor.fetchall()
            
            return [Experiment(**dict(row)) for row in results]
        except Exception as e:
            raise Exception(f"Error getting experiments by user ID: {e}")
        finally:
            cursor.close()
            conn.close()

    def update_experiment(self, experiment: Experiment) -> Experiment:
        """Update an existing experiment."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = """
                UPDATE experiments 
                SET protocol_id = %s, user_id = %s, start_time = %s, end_time = %s, 
                    status = %s, updated_at = %s
                WHERE experiment_id = %s
                RETURNING *
            """
            cursor.execute(sql, (
                str(experiment.protocol_id),
                str(experiment.user_id) if experiment.user_id else None,
                experiment.start_time,
                experiment.end_time,
                experiment.status,
                experiment.updated_at,
                str(experiment.experiment_id)
            ))
            result = cursor.fetchone()
            conn.commit()
            
            if not result:
                raise Exception(f"Experiment with ID {experiment.experiment_id} not found")
            
            return Experiment(**dict(result))
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error updating experiment: {e}")
        finally:
            cursor.close()
            conn.close()

    def delete_experiment(self, experiment_id: str) -> bool:
        """Delete an experiment by ID."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "DELETE FROM experiments WHERE experiment_id = %s"
            cursor.execute(sql, (experiment_id,))
            deleted_count = cursor.rowcount
            conn.commit()
            
            return deleted_count > 0
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error deleting experiment: {e}")
        finally:
            cursor.close()
            conn.close()

    # =============================================================================
    # EXPERIMENT STEP CRUD OPERATIONS
    # =============================================================================

    def create_experiment_step(self, experiment_step: ExperimentStep) -> ExperimentStep:
        """Create a new experiment step in the database."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = """
                INSERT INTO experiment_steps 
                (experiment_step_id, experiment_id, protocol_step_id, actual_start_time, 
                 actual_end_time, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (experiment_step_id) DO UPDATE SET
                    experiment_id = EXCLUDED.experiment_id,
                    protocol_step_id = EXCLUDED.protocol_step_id,
                    actual_start_time = EXCLUDED.actual_start_time,
                    actual_end_time = EXCLUDED.actual_end_time,
                    status = EXCLUDED.status,
                    updated_at = EXCLUDED.updated_at
                RETURNING *
            """
            cursor.execute(sql, (
                str(experiment_step.experiment_step_id),
                str(experiment_step.experiment_id),
                str(experiment_step.protocol_step_id),
                experiment_step.actual_start_time,
                experiment_step.actual_end_time,
                experiment_step.status,
                experiment_step.created_at,
                experiment_step.updated_at
            ))
            result = cursor.fetchone()
            conn.commit()
            
            return ExperimentStep(**dict(result))
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error creating experiment step: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_experiment_step(self, experiment_step_id: str) -> Optional[ExperimentStep]:
        """Get an experiment step by ID."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "SELECT * FROM experiment_steps WHERE experiment_step_id = %s"
            cursor.execute(sql, (experiment_step_id,))
            result = cursor.fetchone()
            
            if result:
                return ExperimentStep(**dict(result))
            return None
        except Exception as e:
            raise Exception(f"Error getting experiment step: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_experiment_steps_by_experiment_id(self, experiment_id: str) -> List[ExperimentStep]:
        """Get all experiment steps for a specific experiment."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = """
                SELECT * FROM experiment_steps 
                WHERE experiment_id = %s 
                ORDER BY created_at ASC
            """
            cursor.execute(sql, (experiment_id,))
            results = cursor.fetchall()
            
            return [ExperimentStep(**dict(row)) for row in results]
        except Exception as e:
            raise Exception(f"Error getting experiment steps by experiment ID: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_all_experiment_steps(self) -> List[ExperimentStep]:
        """Get all experiment steps."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "SELECT * FROM experiment_steps ORDER BY experiment_id, created_at ASC"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            return [ExperimentStep(**dict(row)) for row in results]
        except Exception as e:
            raise Exception(f"Error getting all experiment steps: {e}")
        finally:
            cursor.close()
            conn.close()

    def update_experiment_step(self, experiment_step: ExperimentStep) -> ExperimentStep:
        """Update an existing experiment step."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = """
                UPDATE experiment_steps 
                SET experiment_id = %s, protocol_step_id = %s, actual_start_time = %s, 
                    actual_end_time = %s, status = %s, updated_at = %s
                WHERE experiment_step_id = %s
                RETURNING *
            """
            cursor.execute(sql, (
                str(experiment_step.experiment_id),
                str(experiment_step.protocol_step_id),
                experiment_step.actual_start_time,
                experiment_step.actual_end_time,
                experiment_step.status,
                experiment_step.updated_at,
                str(experiment_step.experiment_step_id)
            ))
            result = cursor.fetchone()
            conn.commit()
            
            if not result:
                raise Exception(f"Experiment step with ID {experiment_step.experiment_step_id} not found")
            
            return ExperimentStep(**dict(result))
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error updating experiment step: {e}")
        finally:
            cursor.close()
            conn.close()

    def delete_experiment_step(self, experiment_step_id: str) -> bool:
        """Delete an experiment step by ID."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "DELETE FROM experiment_steps WHERE experiment_step_id = %s"
            cursor.execute(sql, (experiment_step_id,))
            deleted_count = cursor.rowcount
            conn.commit()
            
            return deleted_count > 0
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error deleting experiment step: {e}")
        finally:
            cursor.close()
            conn.close()

    # =============================================================================
    # EXPERIMENT CONVERSATION CRUD OPERATIONS
    # =============================================================================

    def create_experiment_conversation(self, conversation: ExperimentConversation) -> ExperimentConversation:
        """Create a new experiment conversation message in the database."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = """
                INSERT INTO experiment_conversations 
                (message_id, experiment_id, experiment_step_id, sender_role, message_type, content, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (message_id) DO UPDATE SET
                    experiment_id = EXCLUDED.experiment_id,
                    experiment_step_id = EXCLUDED.experiment_step_id,
                    sender_role = EXCLUDED.sender_role,
                    message_type = EXCLUDED.message_type,
                    content = EXCLUDED.content,
                    created_at = EXCLUDED.created_at
                RETURNING *
            """
            cursor.execute(sql, (
                str(conversation.message_id),
                str(conversation.experiment_id),
                str(conversation.experiment_step_id) if conversation.experiment_step_id else None,
                conversation.sender_role.value,
                conversation.message_type.value,
                conversation.content,
                conversation.created_at
            ))
            result = cursor.fetchone()
            conn.commit()
            
            return ExperimentConversation(**dict(result))
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error creating experiment conversation: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_experiment_conversation(self, message_id: str) -> Optional[ExperimentConversation]:
        """Get an experiment conversation message by ID."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "SELECT * FROM experiment_conversations WHERE message_id = %s"
            cursor.execute(sql, (message_id,))
            result = cursor.fetchone()
            
            if result:
                return ExperimentConversation(**dict(result))
            return None
        except Exception as e:
            raise Exception(f"Error getting experiment conversation: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_experiment_conversations_by_experiment_id(self, experiment_id: str) -> List[ExperimentConversation]:
        """Get all conversation messages for a specific experiment."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = """
                SELECT * FROM experiment_conversations 
                WHERE experiment_id = %s 
                ORDER BY created_at ASC
            """
            cursor.execute(sql, (experiment_id,))
            results = cursor.fetchall()
            
            return [ExperimentConversation(**dict(row)) for row in results]
        except Exception as e:
            raise Exception(f"Error getting experiment conversations by experiment ID: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_experiment_conversations_by_experiment_step_id(self, experiment_step_id: str) -> List[ExperimentConversation]:
        """Get all conversation messages for a specific experiment step."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = """
                SELECT * FROM experiment_conversations 
                WHERE experiment_step_id = %s 
                ORDER BY created_at ASC
            """
            cursor.execute(sql, (experiment_step_id,))
            results = cursor.fetchall()
            
            return [ExperimentConversation(**dict(row)) for row in results]
        except Exception as e:
            raise Exception(f"Error getting experiment conversations by experiment step ID: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_experiment_conversations_by_sender_role(self, experiment_id: str, sender_role: SenderRole) -> List[ExperimentConversation]:
        """Get all conversation messages for a specific experiment by sender role."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = """
                SELECT * FROM experiment_conversations 
                WHERE experiment_id = %s AND sender_role = %s
                ORDER BY created_at ASC
            """
            cursor.execute(sql, (experiment_id, sender_role.value))
            results = cursor.fetchall()
            
            return [ExperimentConversation(**dict(row)) for row in results]
        except Exception as e:
            raise Exception(f"Error getting experiment conversations by sender role: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_all_experiment_conversations(self) -> List[ExperimentConversation]:
        """Get all experiment conversation messages."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "SELECT * FROM experiment_conversations ORDER BY experiment_id, created_at ASC"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            return [ExperimentConversation(**dict(row)) for row in results]
        except Exception as e:
            raise Exception(f"Error getting all experiment conversations: {e}")
        finally:
            cursor.close()
            conn.close()

    def delete_experiment_conversation(self, message_id: str) -> bool:
        """Delete an experiment conversation message by ID."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "DELETE FROM experiment_conversations WHERE message_id = %s"
            cursor.execute(sql, (message_id,))
            deleted_count = cursor.rowcount
            conn.commit()
            
            return deleted_count > 0
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error deleting experiment conversation: {e}")
        finally:
            cursor.close()
            conn.close()
