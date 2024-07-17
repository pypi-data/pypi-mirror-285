from _typeshed import Incomplete
from amsdal.cloud.services.actions.manager import CloudActionsManager as CloudActionsManager
from amsdal.cloud.services.auth.manager import AuthManager as AuthManager
from amsdal.cloud.services.auth.signup_service import SignupService as SignupService
from amsdal.configs.main import settings as settings
from amsdal.errors import AmsdalAuthenticationError as AmsdalAuthenticationError, AmsdalMissingCredentialsError as AmsdalMissingCredentialsError, AmsdalRuntimeError as AmsdalRuntimeError, AmsdalSignupError as AmsdalSignupError
from amsdal.fixtures.manager import FixturesManager as FixturesManager
from amsdal.mixins.build_mixin import BuildMixin as BuildMixin
from amsdal.mixins.class_versions_mixin import ClassVersionsMixin as ClassVersionsMixin
from amsdal.operations.manager import OperationsManager as OperationsManager
from amsdal.schemas.manager import SchemaManager as SchemaManager
from amsdal_models.classes.manager import ClassManager
from amsdal_utils.config.data_models.amsdal_config import AmsdalConfig as AmsdalConfig
from amsdal_utils.utils.singleton import Singleton
from pathlib import Path

class AmsdalManager(BuildMixin, ClassVersionsMixin, metaclass=Singleton):
    _class_manager: ClassManager
    _config_manager: Incomplete
    _connections_manager: Incomplete
    _data_manager: Incomplete
    _table_schemas_manager: Incomplete
    _is_setup: bool
    __is_authenticated: bool
    _schema_manager: Incomplete
    _metadata_manager: Incomplete
    _auth_manager: Incomplete
    def __init__(self, *, raise_on_new_signup: bool = False) -> None:
        """
        Initializes all sub managers. Reads the configuration.
        """
    @property
    def is_setup(self) -> bool: ...
    @property
    def is_authenticated(self) -> bool:
        """
        Indicates if you have passed the AMSDAL license authentication process.
        """
    def pre_setup(self) -> None:
        """
        Initiates models root path and adds it into sys.path
        """
    def setup(self) -> None:
        """
        Initiates models root path and the connections
        """
    def build(self, source_models_path: Path, source_transactions_path: Path, source_static_files_path: Path, source_fixtures_path: Path, source_migrations_path: Path) -> None:
        """
        Build method

        :param source_models_path: Path to the directory where the source models are located.
        :param source_transactions_path: Path to the directory where the source transactions are located.
        :param source_static_files_path: Path to the directory where the source static files are located.
        :param source_fixtures_path: Path to the directory where the source fixtures are located.
        :param source_migrations_path: Path to the directory where the source migrations are located.
        :return: None

        This method is used to build the necessary components for the Amsdal framework.
        It takes four parameters which are all of type `Path`.
        These parameters represent the paths to the directories where the corresponding components are located.

        The method performs the following build steps in order:
        - Builds the models from the `source_models_path` by calling the `build_models` method.
        - Builds the transactions from the `source_transactions_path` by calling the `build_transactions` method.
        - Builds the static files from the `source_static_files_path` by calling the `build_static_files` method.
        - Builds the fixtures from the `source_fixtures_path` by calling the `build_fixtures` method.

        Note: This method is part of the `AmsdalManager` class which includes mixins for `BuildMixin`
        and `ClassVersionsMixin`. It is intended to be used in the Amsdal framework for managing
        and building components.
        """
    def post_setup(self) -> None:
        """
        Registers internal classes and prepares connections (creates internal tables).
        """
    def migrate(self) -> None:
        """
        DEPRECATED: Check changes in the models and apply them to the database.
        """
    def _check_auth(self) -> None: ...
    @property
    def cloud_actions_manager(self) -> CloudActionsManager: ...
    def authenticate(self) -> None:
        """
        Run AMSDAL license authentication process.
        """
    def apply_fixtures(self) -> None:
        """
        Loads and applies fixtures defined in your application.
        """
    def init_classes(self) -> None: ...
    def teardown(self) -> None:
        """
        Clean up everything on the application exit.
        """
