import os

test_env_vars = {
    "logger_name": "languru_test",
    "is_test": True,
    "is_dev": False,
    "is_prod": False,
    "is_staging": False,
    "is_ci": True,
    "pytest": True,
    "pytest_session": True,
}


def set_test_env_vars():
    for k, v in test_env_vars.items():
        os.environ[k] = str(v)
        os.environ[k.upper()] = str(v)


set_test_env_vars()
