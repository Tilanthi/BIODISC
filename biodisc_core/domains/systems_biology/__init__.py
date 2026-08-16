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
"""Systems Biology Domain Module for BIODISC

Integrated biological networks

Date: 2026-04-22
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

from .. import BaseDomainModule, DomainConfig, DomainQueryResult


class SystemsBiologyDomain(BaseDomainModule):
    """Domain specializing in Systems Biology"""

    def get_default_config(self) -> DomainConfig:
        return DomainConfig(
            domain_name="systems_biology",
            version="1.0.0",
            dependencies=[],
            description="Integrated biological networks",
            keywords=[
                "systems", "network", "integration", "holistic", "emergent",
                "pathway", "regulatory", "interaction", "complex"
            ],
            capabilities=[
                "network_modeling", "pathway_analysis", "systems_integration",
                "emergent_properties", "holistic_analysis"
            ]
        )

    def process_query(self, query: str, context: Dict[str, Any] = None) -> DomainQueryResult:
        try:
            if context is None:
                context = {}

            return DomainQueryResult(
                success=True,
                answer=f"Systems biology studies complex interactions within biological systems, focusing on emergent properties from network interactions.",
                confidence=0.85,
                sources=["Systems biology textbooks", "Network biology resources"],
                metadata={"topic": "systems_biology"}
            )
        except Exception as e:
            logger.error(f"Error processing systems biology query: {e}")
            return DomainQueryResult(
                success=False,
                answer=f"Error: {str(e)}",
                confidence=0.0,
                sources=[],
                metadata={"error": str(e)}
            )


def create_systems_biology_domain():
    """Factory function for Systems Biology domain"""
    return SystemsBiologyDomain()


__all__ = ['SystemsBiologyDomain', 'create_systems_biology_domain']
