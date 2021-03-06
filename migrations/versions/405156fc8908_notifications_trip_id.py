"""notifications trip_id

Revision ID: 405156fc8908
Revises: 94467f2845c5
Create Date: 2018-12-17 21:58:42.207101

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '405156fc8908'
down_revision = '94467f2845c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notification', sa.Column('trip_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'notification', 'trip', ['trip_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'notification', type_='foreignkey')
    op.drop_column('notification', 'trip_id')
    # ### end Alembic commands ###
