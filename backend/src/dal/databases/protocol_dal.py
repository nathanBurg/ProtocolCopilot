from typing import List, Optional
from psycopg2.extras import RealDictCursor
from .psql_client import PostgreSQLClient
from ...core.entities.protocol_entities import ProtocolDocument, Protocol, ProtocolStep


class ProtocolDAL:
    def __init__(self):
        self.db_client = PostgreSQLClient()

    def create_protocol_document(self, document: ProtocolDocument) -> ProtocolDocument:
        """Create a new protocol document in the database."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = """
                INSERT INTO protocol_documents 
                (document_id, document_name, description, object_url, mime_type, 
                 ingestion_status, ingested_at, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (document_id) DO UPDATE SET
                    document_name = EXCLUDED.document_name,
                    description = EXCLUDED.description,
                    object_url = EXCLUDED.object_url,
                    mime_type = EXCLUDED.mime_type,
                    ingestion_status = EXCLUDED.ingestion_status,
                    ingested_at = EXCLUDED.ingested_at,
                    updated_at = EXCLUDED.updated_at
                RETURNING *
            """
            cursor.execute(sql, (
                str(document.document_id),
                document.document_name,
                document.description,
                document.object_url,
                document.mime_type,
                document.ingestion_status.value,
                document.ingested_at,
                document.created_at,
                document.updated_at
            ))
            result = cursor.fetchone()
            conn.commit()
            
            return ProtocolDocument(**dict(result))
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error creating protocol document: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_protocol_document(self, document_id: str) -> Optional[ProtocolDocument]:
        """Get a protocol document by ID."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "SELECT * FROM protocol_documents WHERE document_id = %s"
            cursor.execute(sql, (document_id,))
            result = cursor.fetchone()
            
            if result:
                return ProtocolDocument(**dict(result))
            return None
        except Exception as e:
            raise Exception(f"Error getting protocol document: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_all_protocol_documents(self) -> List[ProtocolDocument]:
        """Get all protocol documents."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "SELECT * FROM protocol_documents ORDER BY created_at DESC"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            return [ProtocolDocument(**dict(row)) for row in results]
        except Exception as e:
            raise Exception(f"Error getting all protocol documents: {e}")
        finally:
            cursor.close()
            conn.close()

    def create_protocol(self, protocol: Protocol) -> Protocol:
        """Create a new protocol in the database."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = """
                INSERT INTO protocols 
                (protocol_id, document_id, protocol_name, description, 
                 created_by_user_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (protocol_id) DO UPDATE SET
                    document_id = EXCLUDED.document_id,
                    protocol_name = EXCLUDED.protocol_name,
                    description = EXCLUDED.description,
                    created_by_user_id = EXCLUDED.created_by_user_id,
                    updated_at = EXCLUDED.updated_at
                RETURNING *
            """
            cursor.execute(sql, (
                str(protocol.protocol_id),
                str(protocol.document_id),
                protocol.protocol_name,
                protocol.description,
                str(protocol.created_by_user_id) if protocol.created_by_user_id else None,
                protocol.created_at,
                protocol.updated_at
            ))
            result = cursor.fetchone()
            conn.commit()
            
            return Protocol(**dict(result))
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error creating protocol: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_protocol(self, protocol_id: str) -> Optional[Protocol]:
        """Get a protocol by ID."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "SELECT * FROM protocols WHERE protocol_id = %s"
            cursor.execute(sql, (protocol_id,))
            result = cursor.fetchone()
            
            if result:
                return Protocol(**dict(result))
            return None
        except Exception as e:
            raise Exception(f"Error getting protocol: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_all_protocols(self) -> List[Protocol]:
        """Get all protocols."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "SELECT * FROM protocols ORDER BY created_at DESC"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            return [Protocol(**dict(row)) for row in results]
        except Exception as e:
            raise Exception(f"Error getting all protocols: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_protocols_by_document_id(self, document_id: str) -> List[Protocol]:
        """Get all protocols for a specific document."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "SELECT * FROM protocols WHERE document_id = %s ORDER BY created_at DESC"
            cursor.execute(sql, (document_id,))
            results = cursor.fetchall()
            
            return [Protocol(**dict(row)) for row in results]
        except Exception as e:
            raise Exception(f"Error getting protocols by document ID: {e}")
        finally:
            cursor.close()
            conn.close()

    def create_protocol_step(self, protocol_step: ProtocolStep) -> ProtocolStep:
        """Create a new protocol step in the database."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = """
                INSERT INTO protocol_steps 
                (protocol_step_id, protocol_id, step_number, step_name, 
                 instruction, expected_duration_minutes, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (protocol_step_id) DO UPDATE SET
                    protocol_id = EXCLUDED.protocol_id,
                    step_number = EXCLUDED.step_number,
                    step_name = EXCLUDED.step_name,
                    instruction = EXCLUDED.instruction,
                    expected_duration_minutes = EXCLUDED.expected_duration_minutes,
                    updated_at = EXCLUDED.updated_at
                RETURNING *
            """
            cursor.execute(sql, (
                str(protocol_step.protocol_step_id),
                str(protocol_step.protocol_id),
                protocol_step.step_number,
                protocol_step.step_name,
                protocol_step.instruction,
                protocol_step.expected_duration_minutes,
                protocol_step.created_at,
                protocol_step.updated_at
            ))
            result = cursor.fetchone()
            conn.commit()
            
            return ProtocolStep(**dict(result))
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error creating protocol step: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_protocol_step(self, protocol_step_id: str) -> Optional[ProtocolStep]:
        """Get a protocol step by ID."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "SELECT * FROM protocol_steps WHERE protocol_step_id = %s"
            cursor.execute(sql, (protocol_step_id,))
            result = cursor.fetchone()
            
            if result:
                return ProtocolStep(**dict(result))
            return None
        except Exception as e:
            raise Exception(f"Error getting protocol step: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_protocol_steps_by_protocol_id(self, protocol_id: str) -> List[ProtocolStep]:
        """Get all protocol steps for a specific protocol, ordered by step number."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = """
                SELECT * FROM protocol_steps 
                WHERE protocol_id = %s 
                ORDER BY step_number ASC
            """
            cursor.execute(sql, (protocol_id,))
            results = cursor.fetchall()
            
            return [ProtocolStep(**dict(row)) for row in results]
        except Exception as e:
            raise Exception(f"Error getting protocol steps by protocol ID: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_all_protocol_steps(self) -> List[ProtocolStep]:
        """Get all protocol steps."""
        conn = self.db_client.connect()
        if not conn:
            raise Exception("No active database connection")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            sql = "SELECT * FROM protocol_steps ORDER BY protocol_id, step_number ASC"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            return [ProtocolStep(**dict(row)) for row in results]
        except Exception as e:
            raise Exception(f"Error getting all protocol steps: {e}")
        finally:
            cursor.close()
            conn.close()
