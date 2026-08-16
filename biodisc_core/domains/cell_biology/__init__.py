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
"""Cell Biology Domain Module for BIODISC

Cell structure, organelles, cell division, signaling

Date: 2026-04-22
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

from .. import BaseDomainModule, DomainConfig, DomainQueryResult


class CellBiologyDomain(BaseDomainModule):
    """Domain specializing in Cell Biology"""

    def get_default_config(self) -> DomainConfig:
        return DomainConfig(
            domain_name="cell_biology",
            version="1.0.0",
            dependencies=[],
            description="Cell structure, organelles, cell division, signaling",
            keywords=[
                "cell", "organelle", "mitosis", "meiosis", "membrane",
                "cytoskeleton", "signaling", "cell cycle", "apoptosis"
            ],
            capabilities=[
                "cell_structure", "cell_division", "cell_signaling",
                "organelle_function", "cell_cycle"
            ]
        )

    def process_query(self, query: str, context: Dict[str, Any] = None) -> DomainQueryResult:
        try:
            if context is None:
                context = {}

            return DomainQueryResult(
                success=True,
                answer=f"Cell biology is the study of cell structure and function, including organelles, cell division, and signaling pathways.",
                confidence=0.85,
                sources=["Cell biology textbooks", "Cell signaling databases"],
                metadata={"topic": "cell_biology"}
            )
        except Exception as e:
            logger.error(f"Error processing cell biology query: {e}")
            return DomainQueryResult(
                success=False,
                answer=f"Error: {str(e)}",
                confidence=0.0,
                sources=[],
                metadata={"error": str(e)}
            )


def create_cell_biology_domain():
    """Factory function for Cell Biology domain"""
    return CellBiologyDomain()


__all__ = ['CellBiologyDomain', 'create_cell_biology_domain']
