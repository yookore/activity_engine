import datetime
import uuid
from feed_engine import Relationship

Relationship.create(user='lisanoritha', target_user='jomski2009', creationdate=datetime.datetime.now(), relationship_id=uuid.uuid4(), status='active', type='friend')





