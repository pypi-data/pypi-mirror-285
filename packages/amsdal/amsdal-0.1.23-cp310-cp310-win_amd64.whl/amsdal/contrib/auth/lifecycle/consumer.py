import logging
from typing import Any

import jwt
from amsdal_data.transactions.decorators import transaction
from amsdal_models.classes.helpers.reference_loader import ReferenceLoader
from amsdal_models.classes.model import Model
from amsdal_utils.lifecycle.consumer import LifecycleConsumer
from amsdal_utils.models.data_models.reference import Reference
from amsdal_utils.models.enums import Versions

from amsdal.contrib.auth.errors import AuthenticationError

logger = logging.getLogger(__name__)


class CheckAndCreateSuperUserConsumer(LifecycleConsumer):
    @transaction
    def on_event(self) -> None:
        from amsdal.contrib.auth.settings import auth_settings
        from models.contrib.permission import Permission  # type: ignore[import-not-found]
        from models.contrib.user import User  # type: ignore[import-not-found]

        logger.info('Ensure super user exists')

        if not (auth_settings.ADMIN_USER_EMAIL and auth_settings.ADMIN_USER_PASSWORD):
            logger.info('Email / password missing for super user - skipping')
            return

        user = (
            User.objects.filter(email=auth_settings.ADMIN_USER_EMAIL, _address__object_version=Versions.LATEST)
            .get_or_none()
            .execute()
        )
        if user is not None:
            logger.info('Super user already exists - skipping')
            return

        logger.info("Super user doesn't exist - creating now")

        access_all_permission = (
            Permission.objects.filter(
                model='*',
                action='*',
                _address__object_version=Versions.LATEST,
            )
            .get()
            .execute()
        )

        instance = User(
            email=auth_settings.ADMIN_USER_EMAIL,
            password=auth_settings.ADMIN_USER_PASSWORD,
            permissions=[access_all_permission],
        )
        instance.save(force_insert=True)
        logger.info('Super user created successfully')


class AuthenticateUserConsumer(LifecycleConsumer):
    def on_event(self, auth_header: str, authentication_info: Any) -> None:
        from amsdal.contrib.auth.settings import auth_settings
        from models.contrib.user import User  # type: ignore[import-not-found]

        authentication_info.user = None
        email: str | None

        try:
            jwt_payload = jwt.decode(
                auth_header,
                auth_settings.AUTH_JWT_KEY,  # type: ignore[arg-type]
                algorithms=['HS256'],
            )
            email = jwt_payload['email']
        except jwt.ExpiredSignatureError as exc:
            logger.error('Auth token expired. Defaulting to anonymous user.')

            msg = 'Auth token has expired.'
            raise AuthenticationError(msg) from exc
        except Exception as exc:
            logger.error('Auth token decode failure. Defaulting to anonymous user.')

            msg = 'Failed to decode auth token.'
            raise AuthenticationError(msg) from exc

        user = User.objects.filter(email=email, _address__object_version=Versions.LATEST).get_or_none().execute()

        authentication_info.user = user


class CheckPermissionConsumer(LifecycleConsumer):
    def _prepopulate_default_permissions(self, object_class: type[Model], permissions_info: Any) -> None:
        from amsdal.contrib.auth.settings import auth_settings
        from models.contrib.permission import Permission  # type: ignore[import-not-found]

        permissions_info.has_read_permission = not auth_settings.REQUIRE_DEFAULT_AUTHORIZATION
        permissions_info.has_create_permission = not auth_settings.REQUIRE_DEFAULT_AUTHORIZATION
        permissions_info.has_update_permission = not auth_settings.REQUIRE_DEFAULT_AUTHORIZATION
        permissions_info.has_delete_permission = not auth_settings.REQUIRE_DEFAULT_AUTHORIZATION

        required_permissions = Permission.objects.filter(
            model=object_class.__name__,
            _address__object_version=Versions.LATEST,
        ).execute()

        for required_permission in required_permissions:
            if required_permission.action == 'read':
                permissions_info.has_read_permission = False
            elif required_permission.action == 'create':
                permissions_info.has_create_permission = False
            elif required_permission.action == 'update':
                permissions_info.has_update_permission = False
            elif required_permission.action == 'delete':
                permissions_info.has_delete_permission = False

    def _check_class_permissions(self, object_class: type[Model], user: Any, permissions_info: Any) -> None:
        if hasattr(object_class, 'has_permission'):
            for action in ['read', 'create', 'update', 'delete']:
                setattr(permissions_info, f'has_{action}_permission', object_class.has_permission(user, action))

        if not user or not getattr(user, 'permissions', None):
            return

        user_permissions = [
            ReferenceLoader(p).load_reference() if isinstance(p, Reference) else p for p in user.permissions
        ]

        for user_permission in user_permissions:
            if user_permission.model not in [object_class.__name__, '*']:
                continue

            if user_permission.action == 'read':
                permissions_info.has_read_permission = True
            elif user_permission.action == 'create':
                permissions_info.has_create_permission = True
            elif user_permission.action == 'update':
                permissions_info.has_update_permission = True
            elif user_permission.action == 'delete':
                permissions_info.has_delete_permission = True
            elif user_permission.action == '*':
                permissions_info.has_read_permission = True
                permissions_info.has_create_permission = True
                permissions_info.has_update_permission = True
                permissions_info.has_delete_permission = True

    def _check_object_permissions(self, obj: Model, user: Any, permissions_info: Any) -> None:
        if hasattr(obj, 'has_object_permission'):
            for action in ['read', 'update', 'delete']:
                setattr(
                    permissions_info,
                    f'has_{action}_permission',
                    getattr(permissions_info, f'has_{action}_permission') and obj.has_object_permission(user, action),
                )

    def on_event(
        self,
        object_class: type[Model],
        user: Any,
        access_types: list[Any],  # noqa: ARG002
        permissions_info: Any,
        obj: Model | None = None,
    ) -> None:
        self._prepopulate_default_permissions(object_class, permissions_info)
        self._check_class_permissions(object_class, user, permissions_info)

        if obj:
            self._check_object_permissions(obj, user, permissions_info)
