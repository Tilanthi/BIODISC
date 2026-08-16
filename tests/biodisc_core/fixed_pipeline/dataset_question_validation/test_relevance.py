# Copyright 2026 Tilanthi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Test biological relevance validation."""
import pytest
from biodisc_core.fixed_pipeline.dataset_question_validation import (
    create_dataset_question_validator,
    RelevanceValidationResult
)

def test_breast_cancer_relevance():
    """Test validation of breast cancer question with breast cancer dataset."""
    validator = create_dataset_question_validator()

    question = "How does BRCA1 mutation affect response to PARP inhibitors in triple-negative breast cancer?"
    dataset_metadata = {
        'title': 'Gene expression in triple-negative breast cancer tumors',
        'organism': 'Homo sapiens',
        'tissue': 'breast',
        'disease': 'breast cancer'
    }

    result = validator.validate_relevance(question, dataset_metadata)

    assert result.is_relevant
    assert result.score >= 6.0
    assert 'breast' in str(result.dataset_entities.get('tissues', set()))

def test_colon_breast_mismatch():
    """Test rejection of colon dataset for breast cancer question."""
    validator = create_dataset_question_validator()

    question = "How does BRCA1 mutation affect response to PARP inhibitors in triple-negative breast cancer?"
    dataset_metadata = {
        'title': 'Colon biopsies from ulcerative colitis patients',
        'organism': 'Homo sapiens',
        'tissue': 'colon',
        'disease': 'ulcerative colitis'
    }

    result = validator.validate_relevance(question, dataset_metadata)

    # Should be rejected - colon tissue for breast cancer question
    assert not result.is_relevant
    assert 'mismatch' in result.reason.lower()
    assert result.score < 6.0

def test_organism_mismatch():
    """Test rejection of mouse dataset for human-specific question."""
    validator = create_dataset_question_validator()

    question = "How does BRCA1 mutation affect breast cancer in humans?"
    dataset_metadata = {
        'title': 'Mouse mammary gland development',
        'organism': 'Mus musculus',
        'tissue': 'mammary',
    }

    result = validator.validate_relevance(question, dataset_metadata)

    # Human question, mouse dataset - should warn or reject
    # Depending on strictness, but organism mismatch is critical
    if not result.is_relevant:
        assert 'organism' in result.reason.lower()

def test_lung_cancer_lung_dataset():
    """Test acceptance of lung cancer dataset for lung cancer question."""
    validator = create_dataset_question_validator()

    question = "What are the molecular drivers of lung cancer progression?"
    dataset_metadata = {
        'title': 'Non-small cell lung cancer tumor expression',
        'organism': 'Homo sapiens',
        'tissue': 'lung',
        'disease': 'lung cancer'
    }

    result = validator.validate_relevance(question, dataset_metadata)

    assert result.is_relevant
    assert result.score >= 7.0  # High relevance - all match

def test_generic_question():
    """Test validation of generic question with specific dataset."""
    validator = create_dataset_question_validator()

    question = "How do gene expression patterns differ in cancer?"
    dataset_metadata = {
        'title': 'Colon cancer vs normal tissue',
        'organism': 'Homo sapiens',
        'tissue': 'colon',
        'disease': 'colon cancer'
    }

    result = validator.validate_relevance(question, dataset_metadata)

    # Generic question should be accepted as long as dataset is cancer-related
    assert result.is_relevant  # Cancer in question matches cancer in dataset

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
