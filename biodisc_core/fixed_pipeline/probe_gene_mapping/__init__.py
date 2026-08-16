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
"""Probe ID to gene symbol mapping system."""
from typing import Dict, List, Optional
from .platform_parser import PlatformParser, PlatformAnnotation
from .gene_resolver import GeneResolver, GeneResolutionResult

class ProbeGeneMapper:
    """Complete probe ID to gene symbol mapping system."""

    def __init__(self):
        self.platform_parser = PlatformParser()
        self.gene_resolver = GeneResolver()
        self.rejections = 0

    def validate_and_resolve(
        self,
        identifiers: List[str],
        platform_id: Optional[str] = None
    ) -> GeneResolutionResult:
        """
        Validate identifiers and resolve probe IDs to gene symbols.

        Args:
            identifiers: List of gene symbols or probe IDs
            platform_id: Optional platform ID

        Returns:
            GeneResolutionResult - if success.failed is True, discovery should be REJECTED
        """

        result = self.gene_resolver.resolve_probes_to_genes(identifiers, platform_id)

        if not result.success:
            self.rejections += 1

        return result

    def get_statistics(self) -> Dict:
        """Get mapping statistics."""
        stats = self.gene_resolver.get_statistics()
        stats['rejections'] = self.rejections
        return stats

def create_probe_gene_mapper() -> ProbeGeneMapper:
    """Factory function to create probe-gene mapper."""
    return ProbeGeneMapper()
