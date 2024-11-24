from collections.abc import Iterable
from typing import Any, ClassVar, TypeVar
from typing_extensions import Literal, Never, Self

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser as AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager as BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.base import Model
from django.db.models.manager import EmptyManager, ManyToManyRelatedManager

_AnyUser = AbstractUser | AnonymousUser

_T = TypeVar("_T", bound=Model)

def update_last_login(
    sender: type[AbstractBaseUser], user: AbstractBaseUser, **kwargs: Any
) -> None: ...

_PermissionT = TypeVar("_PermissionT", bound=Permission)

class PermissionManager(models.Manager[_PermissionT]):
    def get_by_natural_key(
        self, codename: str, app_label: str, model: str
    ) -> _PermissionT: ...

class Permission(models.Model):
    content_type_id: int
    objects: ClassVar[PermissionManager[Self]]  # type: ignore[assignment]

    name = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    codename = models.CharField(max_length=100)
    def natural_key(self) -> tuple[str, str, str]: ...
    group_set = ManyToManyRelatedManager["Group", "Permission"]()

_GroupT = TypeVar("_GroupT", bound=Group)

class GroupManager(models.Manager[_GroupT]):
    def get_by_natural_key(self, name: str) -> _GroupT: ...

class Group(models.Model):
    objects: ClassVar[GroupManager[Self]]  # type: ignore[assignment]

    name = models.CharField(max_length=150)
    permissions = models.ManyToManyField[Permission, Any](Permission)
    def natural_key(self) -> tuple[str]: ...
    user_set = ManyToManyRelatedManager["PermissionsMixin", "Group"]()

class UserManager(BaseUserManager[_T]):
    use_in_migrations: bool = ...
    def create_user(
        self,
        username: str,
        email: str | None = ...,
        password: str | None = ...,
        **extra_fields: Any,
    ) -> _T: ...
    def create_superuser(
        self,
        username: str,
        email: str | None,
        password: str | None,
        **extra_fields: Any,
    ) -> _T: ...
    def with_perm(
        self,
        perm: str | Permission,
        is_active: bool = ...,
        include_superusers: bool = ...,
        backend: type[ModelBackend] | str | None = ...,
        obj: Model | None = ...,
    ) -> Self | UserManager[_T]: ...

class PermissionsMixin(models.Model):
    is_superuser = models.BooleanField()
    groups = models.ManyToManyField[Group, Any](Group)
    user_permissions = models.ManyToManyField[Permission, Any](Permission)
    def get_user_permissions(self, obj: Model | None = ...) -> set[str]: ...
    def get_group_permissions(self, obj: Model | None = ...) -> set[str]: ...
    def get_all_permissions(self, obj: Model | None = ...) -> set[str]: ...
    def has_perm(self, perm: str, obj: Model | None = ...) -> bool: ...
    def has_perms(self, perm_list: Iterable[str], obj: Model | None = ...) -> bool: ...
    def has_module_perms(self, app_label: str) -> bool: ...

class AbstractUser(AbstractBaseUser, PermissionsMixin):
    username_validator: UnicodeUsernameValidator = ...

    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    EMAIL_FIELD: str = ...
    USERNAME_FIELD: str = ...
    def get_full_name(self) -> str: ...
    def get_short_name(self) -> str: ...
    def email_user(
        self, subject: str, message: str, from_email: str | None = ..., **kwargs: Any
    ) -> None: ...

    objects: ClassVar[UserManager[Self]]  # type: ignore[assignment]

class User(AbstractUser): ...

class AnonymousUser:
    id: None = ...
    pk: None = ...
    username: str = ...
    is_staff: bool = ...
    is_active: bool = ...
    is_superuser: bool = ...
    def save(self) -> Never: ...
    def delete(self) -> Never: ...
    def set_password(self, raw_password: str) -> Never: ...
    def check_password(self, raw_password: str) -> Never: ...
    @property
    def groups(self) -> EmptyManager[Group]: ...
    @property
    def user_permissions(self) -> EmptyManager[Permission]: ...
    def get_user_permissions(self, obj: _AnyUser | None = ...) -> set[str]: ...
    def get_group_permissions(self, obj: _AnyUser | None = ...) -> set[str]: ...
    def get_all_permissions(self, obj: _AnyUser | None = ...) -> set[str]: ...
    def has_perm(self, perm: str, obj: _AnyUser | None = ...) -> bool: ...
    def has_perms(
        self, perm_list: Iterable[str], obj: _AnyUser | None = ...
    ) -> bool: ...
    def has_module_perms(self, module: str) -> bool: ...
    @property
    def is_anonymous(self) -> Literal[True]: ...
    @property
    def is_authenticated(self) -> Literal[False]: ...
    def get_username(self) -> str: ...
