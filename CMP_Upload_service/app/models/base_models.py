from sqlalchemy import Column, DateTime, Boolean, func


class BaseMixin:
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    is_deleted = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)