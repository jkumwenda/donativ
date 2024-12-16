from sqlalchemy import true
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from models.models import ActivityLog

load_dotenv()


class Dependency:
    def __init__(self, db: Session):
        self.db = db

    def log_activity(self, user_id, action, target, ip_address, additional_data):
        create_log = ActivityLog(
            user_id=user_id,
            action=action,
            target=target,
            ip_address=ip_address,
            additional_data=additional_data,
        )
        self.db.add(create_log)
        self.db.commit()
        self.db.refresh(create_log)

    def request_ip(self, request):
        client_ip = request.client.host
        if x_forwarded_for := request.headers.get('X-Forwarded-For'):
            client_ip = x_forwarded_for.split(',')[0]
        return client_ip

    def cascade_soft_delete_recursive(self, model, record_id, visited=None):
        if visited is None:
            visited = set()

        if record_id in visited:
            return

        visited.add(record_id)

        record = self.db.query(model).get(record_id)
        if not record:
            return

        record.deleted_at = func.now()

        for relationship in record.__mapper__.relationships:
            relationship_attr_name = relationship.key

            related_records = getattr(record, relationship_attr_name)

            if isinstance(related_records, list):
                for related in related_records:
                    if hasattr(related, 'deleted_at'):
                        related.deleted_at = func.now()
                        self.cascade_soft_delete_recursive(
                            related.__class__, related.id, visited)

            elif related_records and hasattr(related_records, 'deleted_at'):
                related_records.deleted_at = func.now()
                self.cascade_soft_delete_recursive(
                    related_records.__class__, related_records.id, visited)

        self.db.commit()

    def restore(self, model, record_id):
        if record := self.db.query(model).get(record_id):
            record.deleted_at = None
            self.db.commit()
