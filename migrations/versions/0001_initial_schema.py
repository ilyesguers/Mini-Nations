"""Create the initial game round history table."""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "game_rounds",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("game", sa.String(length=24), nullable=False),
        sa.Column("outcome", sa.String(length=16), nullable=False),
        sa.Column("multiplier", sa.Float(), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("source", sa.String(length=24), nullable=False, server_default="manual"),
        sa.Column("details", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_game_rounds_game_recorded_at", "game_rounds", ["game", "recorded_at"])


def downgrade() -> None:
    op.drop_index("ix_game_rounds_game_recorded_at", table_name="game_rounds")
    op.drop_table("game_rounds")
