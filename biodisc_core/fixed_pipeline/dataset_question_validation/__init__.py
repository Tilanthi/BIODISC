"""Dataset-question validation system."""
from .biological_relevance import BiologicalRelevanceValidator, RelevanceValidationResult
from .ontology_mapper import OntologyMapper

def create_dataset_question_validator() -> BiologicalRelevanceValidator:
    """Factory function to create dataset-question validator."""
    return BiologicalRelevanceValidator()
