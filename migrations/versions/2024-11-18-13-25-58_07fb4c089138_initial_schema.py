"""initial schema

Revision ID: 07fb4c089138
Revises: f83b8c2d9a66
Create Date: 2024-11-18 13:25:58.952455

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "07fb4c089138"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "instances",
        sa.Column("id", sa.String(length=24), nullable=False, comment="Instance ID"),
        sa.Column("name", sa.String(length=50), nullable=True, comment="Instance Name"),
        sa.Column("added_at", sa.DateTime(), nullable=True, comment="Added At"),
        sa.Column("updated_at", sa.DateTime(), nullable=True, comment="Updated At"),
        sa.Column("checked_at", sa.DateTime(), nullable=True, comment="Checked At"),
        sa.Column("uptime", sa.Integer(), nullable=True, comment="Uptime"),
        sa.Column("up", sa.Boolean(), nullable=True, comment="Is Instance Up?"),
        sa.Column("dead", sa.Boolean(), nullable=True, comment="Is Instance Dead?"),
        sa.Column("version", sa.String(), nullable=True, comment="Instance Version"),
        sa.Column("ipv6", sa.Boolean(), nullable=True, comment="Is IPv6 Enabled?"),
        sa.Column("https_score", sa.Integer(), nullable=True, comment="Https Score"),
        sa.Column("https_rank", sa.String(), nullable=True, comment="Https Rank"),
        sa.Column("obs_score", sa.Integer(), nullable=True, comment="OBS Score"),
        sa.Column("obs_rank", sa.String(), nullable=True, comment="OBS Rank"),
        sa.Column("users", sa.String(), nullable=True, comment="Number of Users"),
        sa.Column("statuses", sa.String(), nullable=True, comment="Number of Statuses"),
        sa.Column("connections", sa.String(), nullable=True, comment="Number of Statuses"),
        sa.Column("open_registrations", sa.Boolean(), nullable=True, comment="Is Open to Register?"),
        sa.Column(
            "info",
            sa.JSON(),
            nullable=True,
            comment="Instance Info",
        ),
        sa.Column("thumbnail", sa.String(), nullable=True, comment="Thumbnail"),
        sa.Column("thumbnail_proxy", sa.String(), nullable=True, comment="Thumbnail Proxy"),
        sa.Column("active_users", sa.Integer(), nullable=True, comment="Number of Active Users"),
        sa.Column("email", sa.String(), nullable=True, comment="Owner E-mail"),
        sa.Column("admin", sa.String(), nullable=True, comment="Admin"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "accounts",
        sa.Column("id", sa.BigInteger(), nullable=False, comment="Account ID"),
        sa.Column("username", sa.String(), nullable=True, comment="Username"),
        sa.Column("acct", sa.String(), nullable=True, comment="Acct"),
        sa.Column("display_name", sa.String(), nullable=True, comment="Display Name"),
        sa.Column("locked", sa.Boolean(), nullable=True, comment="Is Locked?"),
        sa.Column("bot", sa.Boolean(), nullable=True, comment="Is Bot?"),
        sa.Column("discoverable", sa.Boolean(), nullable=True, comment="Is Discoverable?"),
        sa.Column("group", sa.Boolean(), nullable=True, comment="Is Group?"),
        sa.Column("created_at", sa.DateTime(), nullable=True, comment="Created At"),
        sa.Column("note", sa.String(), nullable=True, comment="Note"),
        sa.Column("url", sa.String(), nullable=True, comment="URL"),
        sa.Column("avatar", sa.String(), nullable=True, comment="Avatar"),
        sa.Column("avatar_static", sa.String(), nullable=True, comment="Avatar Static"),
        sa.Column("header", sa.String(), nullable=True, comment="Header"),
        sa.Column("header_static", sa.String(), nullable=True, comment="Header Static"),
        sa.Column("followers_count", sa.Integer(), nullable=True, comment="Followers Count"),
        sa.Column("following_count", sa.Integer(), nullable=True, comment="Following Count"),
        sa.Column("statuses_count", sa.Integer(), nullable=True, comment="Statuses Count"),
        sa.Column("last_status_at", sa.DateTime(), nullable=True, comment="Last Status At"),
        sa.Column("instance_url", sa.String(), nullable=True, comment="Instance URL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("accounts_acct_index", "accounts", ["acct"], unique=True)
    op.create_index("accounts_instance_url_index", "accounts", ["instance_url"], unique=False)

    op.create_table(
        "statuses",
        sa.Column("id", sa.BigInteger(), nullable=False, comment="Status ID"),
        sa.Column("created_at", sa.DateTime(), nullable=True, comment="Created At"),
        sa.Column("in_reply_to_id", sa.BigInteger(), nullable=True, comment="In Reply To ID"),
        sa.Column("in_reply_to_account_id", sa.BigInteger(), nullable=True, comment="In Reply To Account ID"),
        sa.Column("sensitive", sa.Boolean(), nullable=True, comment="Sensitive"),
        sa.Column("spoiler_text", sa.String(), nullable=True, comment="Spoiler Text"),
        sa.Column("visibility", sa.String(), nullable=True, comment="Visibility"),
        sa.Column("language", sa.String(), nullable=True, comment="Language"),
        sa.Column("uri", sa.String(), nullable=True, comment="URI"),
        sa.Column("url", sa.String(), nullable=True, comment="URL"),
        sa.Column("replies_count", sa.Integer(), nullable=True, comment="Replies Count"),
        sa.Column("reblogs_count", sa.Integer(), nullable=True, comment="ReBlogs Count"),
        sa.Column("favourites_count", sa.Integer(), nullable=True, comment="Favourites Count"),
        sa.Column("edited_at", sa.DateTime(), nullable=True, comment="Edited At"),
        sa.Column("content", sa.String(), nullable=True, comment="Content"),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("statuses_tags_index", "statuses", ["tags"], postgresql_using="gin")

    op.create_table(
        "trends",
        sa.Column("id", sa.Integer(), nullable=False, comment="Trend ID"),
        sa.Column("name", sa.String(), nullable=True, comment="Trend Name"),
        sa.Column("url", sa.String(), nullable=True, comment="Trend URL"),
        sa.Column("uses_in_last_seven_days", sa.Integer(), nullable=True, comment="Uses in Last Seven Days"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "suspicious_trends",
        sa.Column("id", sa.BigInteger(), nullable=False, comment="Suspicious Trend ID"),
        sa.Column("name", sa.String(), nullable=True, comment="Suspicious Trend Name"),
        sa.Column("url", sa.String(), nullable=False, comment="Suspicious Trend URL"),
        sa.Column("uses_in_last_seven_days", sa.Integer(), nullable=True, comment="Uses in Last Seven Days"),
        sa.Column("number_of_accounts", sa.Integer(), nullable=True, comment="The Number of Accounts Uses This Tag"),
        sa.Column("instance_url", sa.String(), nullable=True, comment="Instance URL"),
        sa.Column(
            "number_of_similar_statuses",
            sa.Integer(),
            server_default=text("0"),
            nullable=True,
            comment="The number of similar posts",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("suspicious_trends_url_index", "suspicious_trends", ["url"], unique=True)
    op.create_index("suspicious_trends_instance_url_index", "suspicious_trends", ["instance_url"], unique=False)

    op.create_table(
        "raw_statuses",
        sa.Column("id", sa.BigInteger(), nullable=False, comment="Status ID"),
        sa.Column("created_at", sa.DateTime(), nullable=True, comment="Created At"),
        sa.Column("in_reply_to_id", sa.BigInteger(), nullable=True, comment="In Reply To ID"),
        sa.Column("in_reply_to_account_id", sa.BigInteger(), nullable=True, comment="In Reply To Account ID"),
        sa.Column("sensitive", sa.Boolean(), nullable=True, comment="Sensitive"),
        sa.Column("spoiler_text", sa.String(), nullable=True, comment="Spoiler Text"),
        sa.Column("visibility", sa.String(), nullable=True, comment="Visibility"),
        sa.Column("language", sa.String(), nullable=True, comment="Language"),
        sa.Column("uri", sa.String(), nullable=True, comment="URI"),
        sa.Column("url", sa.String(), nullable=True, comment="URL"),
        sa.Column("replies_count", sa.Integer(), nullable=True, comment="Replies Count"),
        sa.Column("reblogs_count", sa.Integer(), nullable=True, comment="ReBlogs Count"),
        sa.Column("favourites_count", sa.Integer(), nullable=True, comment="Favourites Count"),
        sa.Column("edited_at", sa.DateTime(), nullable=True, comment="Edited At"),
        sa.Column("content", sa.String(), nullable=True, comment="Content"),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("raw_statuses")
    op.drop_table("suspicious_trends")
    op.drop_table("trends")
    op.drop_table("statuses")
    op.drop_table("accounts")
    op.drop_table("instances")
