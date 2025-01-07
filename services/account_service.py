# stdlib

from sqlalchemy.dialects.postgresql import insert

from db.db_setup import ScopedSession
from db.models.account_model import AccountModel


def create_or_update_account(session: ScopedSession, account: dict, instance_url: str):
    insert_stmt = insert(AccountModel).values(**account)

    insert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["acct"],
        set_=dict(
            locked=account["locked"],
            bot=account["bot"],
            discoverable=account["discoverable"],
            group=account["group"],
            note=account["note"],
            url=account["url"],
            avatar=account["avatar"],
            avatar_static=account["avatar_static"],
            header=account["header"],
            header_static=account["header_static"],
            followers_count=account["followers_count"],
            following_count=account["following_count"],
            statuses_count=account["statuses_count"],
            last_status_at=account["last_status_at"],
            instance_url=instance_url,
        ),
    )

    return session.execute(insert_stmt)
