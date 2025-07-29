"""
Logging configuration for Jasmin SMS Dashboard
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any

def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Logging configuration
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "default",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "app": {
                "level": log_level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "error_file"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console", "file"]
        }
    }
    
    # Apply logging configuration
    logging.config.dictConfig(config)
    
    # Set specific logger levels
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger("app.core.logging")
    logger.info("Logging configuration initialized")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(f"app.{name}")