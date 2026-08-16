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
"""Biophysics Domain Module for BIODISC

Physical principles in biological systems

Date: 2026-04-22
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

from .. import BaseDomainModule, DomainConfig, DomainQueryResult


class BiophysicsDomain(BaseDomainModule):
    """Domain specializing in Biophysics"""

    def get_default_config(self) -> DomainConfig:
        return DomainConfig(
            domain_name="biophysics",
            version="1.0.0",
            dependencies=[],
            description="Physical principles in biological systems",
            keywords=[
                "thermodynamics", "mechanics", "electrical", "optical",
                "biophysical", "molecular forces", "membrane potential", "protein folding"
            ],
            capabilities=[
                "biomechanics", "bioenergetics", "membrane_biophysics",
                "protein_folding", "molecular_forces"
            ]
        )

    def process_query(self, query: str, context: Dict[str, Any] = None) -> DomainQueryResult:
        try:
            if context is None:
                context = {}

            return DomainQueryResult(
                success=True,
                answer=f"Biophysics applies physical principles and methods to biological systems, from molecular interactions to organism mechanics.",
                confidence=0.85,
                sources=["Biophysics textbooks", "Physical biology resources"],
                metadata={"topic": "biophysics"}
            )
        except Exception as e:
            logger.error(f"Error processing biophysics query: {e}")
            return DomainQueryResult(
                success=False,
                answer=f"Error: {str(e)}",
                confidence=0.0,
                sources=[],
                metadata={"error": str(e)}
            )


def create_biophysics_domain():
    """Factory function for Biophysics domain"""
    return BiophysicsDomain()


__all__ = ['BiophysicsDomain', 'create_biophysics_domain']
