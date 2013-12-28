"""first migrations

Revision ID: 24e51bc5e9d0
Revises: None
Create Date: 2013-12-23 14:31:59.524773

"""

# revision identifiers, used by Alembic.
revision = '24e51bc5e9d0'
down_revision = None

from datetime import datetime
from alembic import op
import sqlalchemy as db



def now():
    return datetime.now()


def upgrade():
    pass


def downgrade():
    pass
