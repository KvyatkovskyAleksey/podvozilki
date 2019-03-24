"""notifications_trips2

Revision ID: 1ba417fa604e
Revises: 405156fc8908
Create Date: 2018-12-19 22:36:40.566349

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1ba417fa604e'
down_revision = '405156fc8908'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notifications_trips',
    sa.Column('trip_id', sa.Integer(), nullable=True),
    sa.Column('notification_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['notification_id'], ['notification.id'], ),
    sa.ForeignKeyConstraint(['trip_id'], ['trip.id'], )
    )
    op.drop_constraint('notification_ibfk_2', 'notification', type_='foreignkey')
    op.drop_column('notification', 'trip_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notification', sa.Column('trip_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('notification_ibfk_2', 'notification', 'trip', ['trip_id'], ['id'])
    op.drop_table('notifications_trips')
    # ### end Alembic commands ###
