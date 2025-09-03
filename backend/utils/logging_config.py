"""
Centralized logging configuration for the AIDE backend
"""

import logging
import sys
import os
from pathlib import Path

class ErrorFilter(logging.Filter):
    """Filter to only allow ERROR and CRITICAL level messages"""
    def filter(self, record):
        return record.levelno >= logging.ERROR

def setup_logging(log_level=logging.INFO, log_file='server.log'):
    """
    Setup logging configuration for the entire application
    
    Args:
        log_level: Logging level (default: INFO)
        log_file: Log file path (default: server.log)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler
            logging.FileHandler(log_dir / log_file),
        ]
    )
    
    # Add error file handler with filter
    error_handler = logging.FileHandler(log_dir / 'errors.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.addFilter(ErrorFilter())
    logging.getLogger().addHandler(error_handler)
    
    # Set specific loggers to avoid duplicate messages
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    logger.info(f"Log level: {logging.getLevelName(log_level)}")
    logger.info(f"Log files: {log_dir}")

def get_logger(name):
    """
    Get a logger instance with the specified name
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def log_request_info(request, logger):
    """
    Log request information for debugging
    
    Args:
        request: Flask request object
        logger: Logger instance
    """
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    # Only try to access JSON for POST/PUT requests
    if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
        try:
            logger.info(f"Body: {request.json}")
        except Exception as e:
            logger.warning(f"Could not parse JSON body: {e}")
    
    logger.info(f"Remote IP: {request.remote_addr}")

def log_response_info(response, logger):
    """
    Log response information for debugging
    
    Args:
        response: Flask response object
        logger: Logger instance
    """
    logger.info(f"Response Status: {response.status_code}")
    logger.info(f"Response Headers: {dict(response.headers)}")

def log_error(error, logger, context=""):
    """
    Log error information with context
    
    Args:
        error: Exception object
        logger: Logger instance
        context: Additional context information
    """
    if context:
        logger.error(f"Error in {context}: {str(error)}", exc_info=True)
    else:
        logger.error(f"Error: {str(error)}", exc_info=True)
