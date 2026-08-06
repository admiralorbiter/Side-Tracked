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
    DATABASE_URI = "sqlite:///:memory:"

class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
