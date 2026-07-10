"""Ontology mapper for biological entities."""
import logging
from typing import Dict, Set, Optional, Tuple
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class OntologyMapping:
    """Mapping of biological terms to ontology IDs."""

    # Tissue mappings (Uberon)
    TISSUE_MAPPING = {
        'breast': 'UBERON:0001959',
        'mammary': 'UBERON:0001959',
        'colon': 'UBERON:0001155',
        'colorectal': 'UBERON:0001155',
        'intestine': 'UBERON:0001155',
        'lung': 'UBERON:0002167',
        'liver': 'UBERON:0002107',
        'brain': 'UBERON:0000955',
        'heart': 'UBERON:0000948',
        'kidney': 'UBERON:0002113',
        'prostate': 'UBERON:0000131',
        'skin': 'UBERON:0002097',
        'blood': 'UBERON:0000170',
        'plasma': 'UBERON:0000170',
        'serum': 'UBERON:0000170',
    }

    # Disease mappings (DOID - Human Disease Ontology)
    DISEASE_MAPPING = {
        'cancer': 'DOID:162',
        'carcinoma': 'DOID:162',
        'tumor': 'DOID:162',
        'neoplasm': 'DOID:162',
        'breast cancer': 'DOID:1612',
        'breast carcinoma': 'DOID:1612',
        'colon cancer': 'DOID:9256',
        'colorectal cancer': 'DOID:9256',
        'lung cancer': 'DOID:1324',
        'prostate cancer': 'DOID:9251',
        'leukemia': 'DOID:9391',
        'lymphoma': 'DOID:5562',
        'diabetes': 'DOID:9351',
        'alzheimer': 'DOID:10652',
        'parkinson': 'DOID:14330',
        'inflammatory bowel disease': 'DOID:0060510',
        'ulcerative colitis': 'DOID:0060511',
        'crohn': 'DOID:0060512',
    }

    # Organism mappings
    ORGANISM_MAPPING = {
        'human': 'NCBITaxon:9606',
        'homo sapiens': 'NCBITaxon:9606',
        'mouse': 'NCBITaxon:10090',
        'mus musculus': 'NCBITaxon:10090',
        'rat': 'NCBITaxon:10116',
        'rattus norvegicus': 'NCBITaxon:10116',
        'zebrafish': 'NCBITaxon:7955',
        'danio rerio': 'NCBITaxon:7955',
        'fruit fly': 'NCBITaxon:7227',
        'drosophila': 'NCBITaxon:7227',
        'yeast': 'NCBITaxon:559292',
        'saccharomyces': 'NCBITaxon:559292',
    }

class OntologyMapper:
    """Map biological terms to ontology IDs for validation."""

    def __init__(self):
        self.tissue_map = OntologyMapping.TISSUE_MAPPING
        self.disease_map = OntologyMapping.DISEASE_MAPPING
        self.organism_map = OntologyMapping.ORGANISM_MAPPING

        logger.info("🗺️  OntologyMapper initialized with tissue/disease/organism mappings")

    def extract_entities(self, text: str) -> Dict[str, Set[str]]:
        """
        Extract biological entities from text.

        Returns:
            {
                'tissues': set(['breast', 'colon']),
                'diseases': set(['cancer', 'breast cancer']),
                'organisms': set(['human'])
            }
        """
        text_lower = text.lower()

        tissues = set()
        diseases = set()
        organisms = set()

        # Extract tissues
        for tissue, uber_id in self.tissue_map.items():
            if tissue in text_lower:
                tissues.add(tissue)

        # Extract diseases (multi-word first, then single-word)
        for disease in sorted(self.disease_map.keys(), key=len, reverse=True):
            if disease in text_lower:
                diseases.add(disease)

        # Extract organisms
        for organism in sorted(self.organism_map.keys(), key=len, reverse=True):
            if organism in text_lower:
                organisms.add(organism)

        result = {
            'tissues': tissues,
            'diseases': diseases,
            'organisms': organisms
        }

        logger.debug(f"Extracted entities: {result}")
        return result

    def check_relevance(self, question_entities: Dict, dataset_entities: Dict) -> Tuple[bool, str]:
        """
        Check if question and dataset are biologically relevant.

        Returns:
            (is_relevant, reason)
        """

        # Check organism match (critical)
        q_orgs = question_entities.get('organisms', set())
        d_orgs = dataset_entities.get('organisms', set())

        if q_orgs and d_orgs:
            if not q_orgs.intersection(d_orgs):
                return False, f"Organism mismatch: question mentions {q_orgs} but dataset is {d_orgs}"

        # Check tissue match (important)
        q_tissues = question_entities.get('tissues', set())
        d_tissues = dataset_entities.get('tissues', set())

        if q_tissues and d_tissues:
            if not q_tissues.intersection(d_tissues):
                return False, f"Tissue mismatch: question mentions {q_tissues} but dataset is {d_tissues}"

        # Check disease match (important)
        q_diseases = question_entities.get('diseases', set())
        d_diseases = dataset_entities.get('diseases', set())

        if q_diseases and d_diseases:
            if not q_diseases.intersection(d_diseases):
                # If question specifies disease but dataset doesn't, check if dataset is healthy controls
                if 'control' not in str(d_diseases).lower() and 'normal' not in str(d_diseases).lower():
                    return False, f"Disease mismatch: question mentions {q_diseases} but dataset is {d_diseases}"

        # If all checks pass
        return True, "Biological relevance confirmed"
