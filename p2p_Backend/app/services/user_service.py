"""Business logic for user signup/identity."""

from sqlalchemy.orm import Session

from app.core.exceptions import InvalidCredentialsError, UsernameAlreadyExistsError
from app.core.security import hash_password, verify_password
from app.models.user import User


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