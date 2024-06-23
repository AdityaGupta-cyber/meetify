"""Added Timezone to the Meetings model

Revision ID: 9599212c7084
Revises: 
Create Date: 2024-06-22 18:06:47.314043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9599212c7084'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('meetings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('timezone', sa.String(length=20), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('meetings', schema=None) as batch_op:
        batch_op.drop_column('timezone')

    # ### end Alembic commands ###
