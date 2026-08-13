"""Business logic for a user's saved-contacts ("friends") list."""

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import (
    FriendshipAlreadyExistsError,
    FriendshipNotFoundError,
    SelfFriendshipError,
    UserNotFoundError,
)
from app.models.friendship import Friendship
from app.models.user import User
from app.services.user_service import UserService


class FriendService:
    def __init__(self, db: Session):
        self._db = db
        self._users = UserService(db)

    def list_friends(self, user_id: uuid.UUID) -> list[User]:
        """The users on `user_id`'s list, alphabetically."""
        return (
            self._db.query(User)
            .join(Friendship, Friendship.friend_id == User.id)
            .filter(Friendship.user_id == user_id)
            .order_by(User.username)
            .all()
        )

    def get_friend_ids(self, user_id: uuid.UUID) -> set[uuid.UUID]:
        """Just the ids — used to flag `is_friend` on search results without a
        second round trip per row."""
        rows = self._db.query(Friendship.friend_id).filter(Friendship.user_id == user_id).all()
        return {row[0] for row in rows}

    def add_friend(self, user_id: uuid.UUID, friend_username: str) -> User:
        """Save a user to `user_id`'s list, returning the user that was added.

        One-way: this creates no reverse row, so the person being added doesn't
        get `user_id` on their list.
        """
        friend = self._users.get_user_by_username(friend_username)
        if not friend:
            raise UserNotFoundError

        if friend.id == user_id:
            raise SelfFriendshipError

        if self._get_friendship(user_id, friend.id):
            raise FriendshipAlreadyExistsError

        self._db.add(Friendship(user_id=user_id, friend_id=friend.id))
        self._db.commit()
        return friend

    def remove_friend(self, user_id: uuid.UUID, friend_id: uuid.UUID) -> None:
        friendship = self._get_friendship(user_id, friend_id)
        if not friendship:
            raise FriendshipNotFoundError

        self._db.delete(friendship)
        self._db.commit()

    def _get_friendship(self, user_id: uuid.UUID, friend_id: uuid.UUID) -> Friendship | None:
        return (
            self._db.query(Friendship)
            .filter(Friendship.user_id == user_id, Friendship.friend_id == friend_id)
            .first()
        )
