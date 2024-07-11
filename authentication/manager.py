from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("Username must be provided")

        user = self.model(
            username=username,
            email=None if not email else self.normalize_email(email).lower(),
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, email, **extra_fields):
        if not username:
            raise ValueError("Username must be provided")

        if not email:
            raise ValueError("Email must be provided")

        if not password:
            raise ValueError('Password is not provided')

        user = self.model(
            username=username,
            email=self.normalize_email(email).lower(),
            is_active=True,
            is_superuser=True,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user