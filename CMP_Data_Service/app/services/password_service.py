from bcrypt import hashpw, checkpw, gensalt
from fastapi.concurrency import run_in_threadpool


class passwordService:

    # -------------------------
    # HASH PASSWORD
    # -------------------------
    @staticmethod
    async def create_password(plain_password: str) -> str:
        def _hash():
            salt = gensalt()
            return hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")

        return await run_in_threadpool(_hash)

    # -------------------------
    # VERIFY PASSWORD
    # -------------------------
    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        def _check():
            return checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )

        return await run_in_threadpool(_check)

PasswordService = passwordService()