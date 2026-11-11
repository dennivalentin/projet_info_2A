import os

from utils.env_variables import load_environment_variables

load_environment_variables()

os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_only_for_pytest_0123456789")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
