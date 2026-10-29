"""Конфигурация подключения к MS SQL Server."""

DB_CONFIG = {
    "driver": "{ODBC Driver 18 for SQL Server}",
    "server": "localhost",
    "database": "ReviewsRatingsDB",
    "trusted_connection": "yes",
    "trust_server_certificate": "yes",
}

ROLE_ADMIN = "admin"
ROLE_USER = "user"

STATUS_ON_MODERATION = 1
STATUS_PUBLISHED = 2
STATUS_REJECTED = 3