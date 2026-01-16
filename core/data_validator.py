"""
Data Validation Module

This module provides validation utilities for market data,
ensuring data quality and integrity before analysis.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Optional
import math


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    
    def __bool__(self) -> bool:
        return self.is_valid


class DataValidator:
    """
    Validates market data snapshots for sanity and completeness.
    
    Provides:
    - Required field validation
    - Type checking
    - Range validation  
    - Cross-field validation (e.g., bid < ask)
    - Data sanitization
    """
    
    REQUIRED_FIELDS = ["bids", "asks"]
    
    @classmethod
    def validate_snapshot(cls, snapshot: Dict) -> ValidationResult:
        """
        Validate a market snapshot.
        
        Args:
            snapshot: Dictionary containing order book data
            
        Returns:
            ValidationResult with is_valid flag and any errors/warnings
        """
        errors: List[str] = []
        warnings: List[str] = []
        
        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if field not in snapshot:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        bids = snapshot["bids"]
        asks = snapshot["asks"]
        
        # Validate bids structure
        if not isinstance(bids, list):
            errors.append("Bids must be a list")
        elif len(bids) == 0:
            errors.append("Bids list cannot be empty")
        else:
            bid_errors = cls._validate_levels(bids, "bid")
            errors.extend(bid_errors)
        
        # Validate asks structure
        if not isinstance(asks, list):
            errors.append("Asks must be a list")
        elif len(asks) == 0:
            errors.append("Asks list cannot be empty")
        else:
            ask_errors = cls._validate_levels(asks, "ask")
            errors.extend(ask_errors)
        
        # Cross-validation: bid < ask
        if not errors and len(bids) > 0 and len(asks) > 0:
            best_bid = bids[0][0] if isinstance(bids[0], list) else bids[0]
            best_ask = asks[0][0] if isinstance(asks[0], list) else asks[0]
            
            if cls._is_valid_number(best_bid) and cls._is_valid_number(best_ask):
                if best_bid >= best_ask:
                    errors.append(f"Invalid book: best_bid ({best_bid}) >= best_ask ({best_ask})")
                
                spread = best_ask - best_bid
                mid_price = (best_bid + best_ask) / 2
                
                if spread < 0:
                    errors.append(f"Negative spread: {spread}")
                elif mid_price > 0 and spread > mid_price * 0.1:
                    warnings.append(f"Wide spread: {spread:.4f} ({spread/mid_price*100:.1f}%)")
        
        # Validate mid_price if present
        if "mid_price" in snapshot:
            mid_price = snapshot["mid_price"]
            if not cls._is_valid_number(mid_price) or mid_price <= 0:
                errors.append(f"Invalid mid_price: {mid_price}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    @classmethod
    def _validate_levels(cls, levels: List, side: str, max_check: int = 10) -> List[str]:
        """Validate order book levels."""
        errors = []
        
        for i, level in enumerate(levels[:max_check]):
            if not isinstance(level, (list, tuple)) or len(level) < 2:
                errors.append(f"{side.title()} level {i}: must be [price, volume]")
                continue
            
            price, volume = level[0], level[1]
            
            if not cls._is_valid_number(price) or price <= 0:
                errors.append(f"{side.title()} level {i}: invalid price {price}")
            
            if not cls._is_valid_number(volume) or volume < 0:
                errors.append(f"{side.title()} level {i}: invalid volume {volume}")
        
        return errors
    
    @staticmethod
    def _is_valid_number(value: Any) -> bool:
        """Check if value is a valid, finite number."""
        if value is None:
            return False
        
        try:
            if isinstance(value, (int, float)):
                return not (math.isnan(value) or math.isinf(value))
            # Try converting
            float_val = float(value)
            return not (math.isnan(float_val) or math.isinf(float_val))
        except (TypeError, ValueError):
            return False
    
    @classmethod
    def sanitize_snapshot(cls, snapshot: Dict) -> Dict:
        """
        Attempt to fix common issues in snapshot data.
        
        Args:
            snapshot: Potentially malformed snapshot
            
        Returns:
            Sanitized copy of the snapshot
        """
        result = snapshot.copy()
        
        # Sanitize mid_price
        if "mid_price" in result:
            result["mid_price"] = cls._sanitize_number(result["mid_price"], default=100.0)
        
        # Sanitize bids
        if "bids" in result and isinstance(result["bids"], list):
            result["bids"] = [
                [cls._sanitize_number(p, 100.0), cls._sanitize_number(v, 0.0)]
                for p, v in result["bids"]
                if isinstance((p, v), tuple) or (isinstance(p, (int, float)) and isinstance(v, (int, float)))
            ]
        
        # Sanitize asks
        if "asks" in result and isinstance(result["asks"], list):
            result["asks"] = [
                [cls._sanitize_number(p, 100.0), cls._sanitize_number(v, 0.0)]
                for p, v in result["asks"]
                if isinstance((p, v), tuple) or (isinstance(p, (int, float)) and isinstance(v, (int, float)))
            ]
        
        return result
    
    @classmethod
    def _sanitize_number(cls, value: Any, default: float = 0.0) -> float:
        """Replace invalid numbers with default."""
        if cls._is_valid_number(value):
            return float(value)
        return default


def validate_order_book(bids: List[List[float]], asks: List[List[float]]) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate raw order book data.
    
    Args:
        bids: List of [price, volume] pairs
        asks: List of [price, volume] pairs
        
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    result = DataValidator.validate_snapshot({"bids": bids, "asks": asks})
    return result.is_valid, result.errors
