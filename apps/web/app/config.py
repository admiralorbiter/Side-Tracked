import os


class Config:
    """Base application configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-sidetrack-secret-key-change-in-prod")
    PROJECT_NAME = "Sidetrack"
    TAGLINE = "A Field Guide to Getting Sidetracked"
    INITIAL_REGION = "Greater Kansas City"
    INITIAL_TAXON = "Birds"
    DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///sidetrack.db")
    TESTING = False


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING = True
    _worker = os.environ.get("PYTEST_XDIST_WORKER", "gw0")
    DATABASE_URI = f"sqlite:///data/test_sidetrack_{_worker}.db"
    PLANNER_DB_PATH = f"data/test_route_plans_{_worker}.db"
    FEEDBACK_DB_PATH = f"data/test_walk_feedback_{_worker}.db"


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False
