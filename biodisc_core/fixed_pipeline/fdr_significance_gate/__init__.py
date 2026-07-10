"""FDR significance gate system."""
from .significance_validator import SignificanceValidator, SignificanceValidationResult

def create_significance_validator() -> SignificanceValidator:
    """Factory function to create significance validator."""
    return SignificanceValidator()
