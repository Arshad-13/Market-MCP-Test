"""
Market Intelligence MCP Server - Core Package

This package contains the core analytics and data processing modules
adapted from Genesis2025 HFT platform for use with MCP.
"""

from .analytics import MicrostructureAnalyzer
from .anomaly_detection import AnomalyDetector
from .data_validator import DataValidator

__all__ = [
    "MicrostructureAnalyzer",
    "AnomalyDetector", 
    "DataValidator",
]
