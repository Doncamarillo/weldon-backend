"""Add description and image_url to Project model

Revision ID: c9b039b9a2c6
Revises: bb8ff2fbe40a
Create Date: 2024-12-11 19:57:32.344142

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9b039b9a2c6'
down_revision = 'bb8ff2fbe40a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('image_url', sa.String(length=500), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.drop_column('image_url')
        batch_op.drop_column('description')

    # ### end Alembic commands ###