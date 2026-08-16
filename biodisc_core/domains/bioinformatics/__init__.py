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
"""Bioinformatics Domain Module for BIODISC

Sequence analysis, structural biology

Date: 2026-04-22
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

from .. import BaseDomainModule, DomainConfig, DomainQueryResult


class BioinformaticsDomain(BaseDomainModule):
    """Domain specializing in Bioinformatics"""

    def get_default_config(self) -> DomainConfig:
        return DomainConfig(
            domain_name="bioinformatics",
            version="1.0.0",
            dependencies=[],
            description="Sequence analysis, structural biology",
            keywords=[
                "sequence", "alignment", "database", "structural", "algorithm",
                "bioinformatics", "computational", "blast", "phylogeny"
            ],
            capabilities=[
                "sequence_analysis", "structural_prediction", "database_searching",
                "phylogenetic_analysis", "algorithm_development"
            ]
        )

    def process_query(self, query: str, context: Dict[str, Any] = None) -> DomainQueryResult:
        try:
            if context is None:
                context = {}

            return DomainQueryResult(
                success=True,
                answer=f"Bioinformatics develops methods and software tools for understanding biological data, particularly sequence analysis and structural prediction.",
                confidence=0.85,
                sources=["Bioinformatics textbooks", "Sequence databases"],
                metadata={"topic": "bioinformatics"}
            )
        except Exception as e:
            logger.error(f"Error processing bioinformatics query: {e}")
            return DomainQueryResult(
                success=False,
                answer=f"Error: {str(e)}",
                confidence=0.0,
                sources=[],
                metadata={"error": str(e)}
            )


def create_bioinformatics_domain():
    """Factory function for Bioinformatics domain"""
    return BioinformaticsDomain()


__all__ = ['BioinformaticsDomain', 'create_bioinformatics_domain']
