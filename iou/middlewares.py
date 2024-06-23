from contextvars import ContextVar

from django.contrib.auth.models import User


class CurrentUserMiddleware:
    _current_user: ContextVar[User | None] = ContextVar(
        "current_user",
        default=None,
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._current_user.set(request.user)
        return self.get_response(request)

    @classmethod
    def get_current_user(cls) -> User | None:
        return cls._current_user.get()
