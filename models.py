from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    connect
)
from mongoengine.fields import (
    UUIDField,
    StringField,
    ReferenceField,
    ListField,
    FloatField,
    IntField,
    DateTimeField,
)
from mongoengine import (
    CASCADE,
    NULLIFY
)
import os
from dotenv import load_dotenv


def connect_to_db():
    load_dotenv()
    DB_URI = os.getenv("MONGO_URI")
    connect(host=DB_URI, alias="hashtopDB")


class User(Document):
    __table_name__ = "users"

    id = UUIDField(primary_key=True)
    wallet_addr = StringField()
    miners = ListField(ReferenceField('Miner'))
    stats = ReferenceField('DailyStats')


# each user has their mining stats, keep stats even if user is deleted for
# total statistics analysis
# aggregates over 24 hours
# real time data should be queried by dashboard directly
class DailyStats(Document):
    __table_name__ = "dailyStats"

    begin_timestamp = IntField()

    balance = EmbeddedDocumentField(document_type='FloatAggrDaily')
    est_revenue = EmbeddedDocumentField(document_type='FloatAggrDaily')

    valid_shares = EmbeddedDocumentField(document_type='IntAggrDaily')
    stale_shares = EmbeddedDocumentField(document_type='IntAggrDaily')
    invalid_shares = EmbeddedDocumentField(document_type='IntAggrDaily')
    round_share_percent = EmbeddedDocumentField(document_type='FloatAggrDaily')

    hashrate = EmbeddedDocumentField(document_type='FloatAggrDaily')


class TimestampFloat(EmbeddedDocument):
    timestamp = IntField()
    value = FloatField()


class TimestampInt(EmbeddedDocument):
    timestamp = IntField()
    value = IntField()


class FloatAggrDaily(EmbeddedDocument):
    begin_timestamp = IntField()
    aggregate = ListField(
        EmbeddedDocumentField(document_type='TimestampFloat'),
        max_length=24 * 6
    )


class IntAggrDaily(EmbeddedDocument):
    begin_timestamp = IntField()
    aggregate = ListField(
        EmbeddedDocumentField(document_type='TimestampInt'),
        max_length=24 * 6
    )


# a user can have one or more miners
class Miner(Document):
    __table_name__ = "miners"

    id = UUIDField(primary_key=True)
    user_id = ReferenceField(User, reverse_delete_rule=CASCADE)
    wallet_addr = StringField(required=True)
    gpus = ListField(ReferenceField('Gpu'))


# each miner can have one or more gpus
class Gpu(Document):
    __table_name__ = "gpus"

    miner = ReferenceField(Miner, reverse_delete_rule=NULLIFY)
    temps = EmbeddedDocumentField(document_type='IntAggrDaily')
