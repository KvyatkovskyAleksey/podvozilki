"""notifications

Revision ID: 900d8b0c88a4
Revises: 0267e4948f09
Create Date: 2018-12-16 11:08:29.159238

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '900d8b0c88a4'
down_revision = '0267e4948f09'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_timestamp'), 'notification', ['timestamp'], unique=False)
    op.add_column('user', sa.Column('last_notification_read_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_notification_read_time')
    op.drop_index(op.f('ix_notification_timestamp'), table_name='notification')
    op.drop_table('notification')
    # ### end Alembic commands ###
