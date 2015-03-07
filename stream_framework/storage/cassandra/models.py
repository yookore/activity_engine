from cqlengine import columns
from cqlengine.models import Model
from cqlengine.exceptions import ValidationError


class VarInt(columns.Column):
    db_type = 'varint'

    def validate(self, value):
        val = super(VarInt, self).validate(value)
        if val is None:
            return
        try:
            return long(val)
        except (TypeError, ValueError):
            raise ValidationError(
                "{} can't be converted to integer value".format(value))

    def to_python(self, value):
        return self.validate(value)

    def to_database(self, value):
        return self.validate(value)


class BaseActivity(Model):
    feed_id = columns.Ascii(primary_key=True, partition_key=True)
    activity_id = columns.TimeUUID(primary_key=True, clustering_order='desc')


class Activity(BaseActivity):
    actor = columns.Text(required=True)
    extra_context = columns.Bytes(required=False)
    object = columns.TimeUUID(required=True)
    object_type = columns.Text(required=True)
    target = columns.Text(required=False)
    target_type = columns.Text(required=False)
    time = columns.DateTime(required=False)
    verb = columns.Integer(required=True)


class AggregatedActivity(BaseActivity):
    activities = columns.Bytes(required=False)
    created_at = columns.DateTime(required=False)
    group = columns.Ascii(required=False)
    updated_at = columns.DateTime(required=False)
