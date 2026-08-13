"""Business logic for user signup/identity."""

import uuid

from sqlalchemy import case
from sqlalchemy.orm import Session

from app.core.exceptions import InvalidCredentialsError, UsernameAlreadyExistsError
from app.core.security import hash_password, verify_password
from app.models.user import User

# Characters that mean something special inside a SQL LIKE pattern. Anything a
# user types has to be neutered before it goes into one — otherwise a search for
# "%" is the pattern "%%%", which matches every row in the table.
_LIKE_ESCAPE_CHAR = "\\"


class UserService:
    def __init__(self, db: Session):
        self._db = db

    def sign_up(self, username: str, password: str) -> User:
        """Create and persist a new user with a hashed password.

        Same shape as AccountService.open_account: build the object, add,
        commit, refresh, return. The one new step: hash the password with
        app.core.security.hash_password() before putting it on the User —
        never store what the caller typed.
        """
        if self.get_user_by_username(username):
            raise UsernameAlreadyExistsError

        user = User(username=username, hashed_password=hash_password(password))
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def get_user_by_username(self, username: str) -> User:
        return self._db.query(User).filter(User.username == username).first()

    def get_user(self, user_id: uuid.UUID) -> User:
        return self._db.query(User).filter(User.id == user_id).first()

    def search_users(
        self, query: str, exclude_user_id: uuid.UUID | None = None, limit: int = 10
    ) -> list[User]:
        """Find users whose username contains `query`, for the typeahead dropdown.

        A blank query returns nothing rather than the whole table — the caller
        should show its own default list (e.g. your friends) in that case.

        Results put prefix matches first ("al" surfaces "alice" above
        "calvin_al"), which is what makes the dropdown feel like it's
        completing what you typed rather than just listing matches.
        """
        query = query.strip()
        if not query:
            return []

        escaped = (
            query.replace(_LIKE_ESCAPE_CHAR, _LIKE_ESCAPE_CHAR * 2)
            .replace("%", f"{_LIKE_ESCAPE_CHAR}%")
            .replace("_", f"{_LIKE_ESCAPE_CHAR}_")
        )

        # The leading % means this can't use ix_users_username — it's a table
        # scan. Fine at this size; if the user table ever gets large, dropping
        # to a prefix-only "escaped%" match lets the index serve it again.
        contains = User.username.like(f"%{escaped}%", escape=_LIKE_ESCAPE_CHAR)
        starts_with = User.username.like(f"{escaped}%", escape=_LIKE_ESCAPE_CHAR)

        statement = self._db.query(User).filter(contains)
        if exclude_user_id is not None:
            statement = statement.filter(User.id != exclude_user_id)

        return (
            statement.order_by(case((starts_with, 0), else_=1), User.username)
            .limit(limit)
            .all()
        )

    def authenticate(self, username: str, password: str) -> User:
        """Verify a login attempt, returning the User if valid.

        Deliberately raises the same InvalidCredentialsError whether the
        username doesn't exist OR the password is wrong — telling an
        attacker which one failed would let them enumerate valid usernames.
        """
        user = self.get_user_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError
        return user