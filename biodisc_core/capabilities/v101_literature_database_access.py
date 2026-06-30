"""
Literature Database Access Capability

Autonomous access to scientific literature databases and repositories for
independent literature search, retrieval, and integration capabilities.

CAPABILITIES:
- Independent access to scientific databases (PubMed, NCBI, arXiv, etc.)
- Literature search and retrieval
- Citation management and formatting
- Literature synthesis and analysis
- Integration with biological knowledge systems

ETHICAL USE:
- Respect database access policies and rate limits
- Proper citation of all sources
- No unauthorized access to subscription databases
- Compliance with database terms of service

Date: 2026-06-29
Version: 1.0.0
Priority: 0.80 (Highest)
Agency Enhancement: 9.6%
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging
import json
import re
from datetime import datetime, timedelta
import time
import hashlib
import requests
from urllib.parse import urlencode, quote

logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    """Types of scientific databases"""
    PUBMED = "pubmed"
    NCBI_GENE = "ncbi_gene"
    NCBI_PUBCHEM = "ncbi_pubchem"
    ARXIV = "arxiv"
    BIORXIV = "biorxiv"
    PMC = "pmc"  # PubMed Central (full-text)
    GENBANK = "genbank"
    UNIPROT = "uniprot"
    PDB = "pdb"  # Protein Data Bank

class SearchResult:
    """Literature search result"""
    def __init__(self, title: str, authors: List[str], abstract: str,
                 journal: str, year: int, doi: str, url: str,
                 database: DatabaseType, pmid: str = None):
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.journal = journal
        self.year = year
        self.doi = doi
        self.url = url
        self.database = database
        self.pmid = pmid
        self.relevance_score = 0.0
        self.extraction_date = datetime.now()

class Citation:
    """Academic citation"""
    def __init__(self, authors: List[str], title: str, journal: str,
                 year: int, volume: str = None, issue: str = None,
                 pages: str = None, doi: str = None, pmid: str = None):
        self.authors = authors
        self.title = title
        self.journal = journal
        self.year = year
        self.volume = volume
        self.issue = issue
        self.pages = pages
        self.doi = doi
        self.pmid = pmid

    def format_apa(self) -> str:
        """Format citation in APA style"""
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += ", et al."

        citation = f"{authors_str} ({self.year}). {self.title}."

        if self.journal:
            citation += f" {self.journal}"
        if self.volume:
            citation += f", {self.volume}"
        if self.issue:
            citation += f"({self.issue})"
        if self.pages:
            citation += f", {self.pages}"

        if self.doi:
            citation += f". https://doi.org/{self.doi}"

        return citation

    def format_mla(self) -> str:
        """Format citation in MLA style"""
        if self.authors:
            first_author = self.authors[0].split()[-1] if self.authors[0] else ""
        else:
            first_author = ""

        citation = f'"{self.title}."'
        if self.authors:
            citation += f" {', '.join(self.authors)}"
        citation += f" {self.journal}"
        if self.volume:
            citation += f", vol. {self.volume}"
        if self.issue:
            citation += f", no. {self.issue}"
        if self.pages:
            citation += f", pp. {self.pages}"
        citation += f", {self.year}"

        return citation

@dataclass
class LiteratureQuery:
    """Literature search query"""
    query_id: str
    search_terms: List[str]
    databases: List[DatabaseType]
    date_range: Tuple[datetime, datetime] = None
    max_results: int = 50
    relevance_threshold: float = 0.3
    require_full_text: bool = False
    search_fields: List[str] = field(default_factory=lambda: ["title", "abstract", "keywords"])

class LiteratureDatabaseAccess:
    """
    Autonomous literature database access system.

    Provides independent access to scientific databases for literature search,
    retrieval, and integration capabilities.
    """

    def __init__(self):
        self.search_results: Dict[str, List[SearchResult]] = {}
        self.citation_cache: Dict[str, Citation] = {}
        self.access_count = 0
        self.last_access_time = None
        self.rate_limits: Dict[DatabaseType, Dict[str, Any]] = {}

        # Initialize rate limits
        self._initialize_rate_limits()

        logger.info("Literature Database Access initialized")
        logger.info(f"Supported databases: {[db.value for db in DatabaseType]}")

    def _initialize_rate_limits(self):
        """Initialize rate limits for different databases"""
        # PubMed API: 3 requests per second without API key
        self.rate_limits[DatabaseType.PUBMED] = {
            "requests_per_second": 3,
            "requests_per_minute": 100,
            "daily_limit": 10000
        }

        # NCBI databases: 3 requests per second
        self.rate_limits[DatabaseType.NCBI_GENE] = {
            "requests_per_second": 3,
            "requests_per_minute": 100
        }
        self.rate_limits[DatabaseType.NCBI_PUBCHEM] = {
            "requests_per_second": 3,
            "requests_per_minute": 100
        }

        # arXiv: 1 request per second
        self.rate_limits[DatabaseType.ARXIV] = {
            "requests_per_second": 1,
            "requests_per_minute": 50
        }

        # BioRxiv: 1 request per second
        self.rate_limits[DatabaseType.BIORXIV] = {
            "requests_per_second": 1,
            "requests_per_minute": 50
        }

    def search_literature(self, query: LiteratureQuery) -> List[SearchResult]:
        """
        Search literature databases with specified query.
        """
        logger.info(f"Searching literature for query: {query.query_id}")
        logger.info(f"Search terms: {', '.join(query.search_terms)}")
        logger.info(f"Databases: {[db.value for db in query.databases]}")

        all_results = []

        for database in query.databases:
            try:
                results = self._search_database(query, database)
                all_results.extend(results)
                logger.info(f"Found {len(results)} results from {database.value}")

                # Rate limiting
                time.sleep(1.0 / self.rate_limits[database]["requests_per_second"])

            except Exception as e:
                logger.warning(f"Error searching {database.value}: {e}")
                continue

        # Sort by relevance and limit results
        all_results.sort(key=lambda r: r.relevance_score, reverse=True)
        all_results = all_results[:query.max_results]

        # Cache results
        self.search_results[query.query_id] = all_results

        logger.info(f"Total results found: {len(all_results)}")

        return all_results

    def _search_database(self, query: LiteratureQuery, database: DatabaseType) -> List[SearchResult]:
        """Search specific database"""
        if database == DatabaseType.PUBMED:
            return self._search_pubmed(query)
        elif database == DatabaseType.ARXIV:
            return self._search_arxiv(query)
        elif database == DatabaseType.BIORXIV:
            return self._search_biorxiv(query)
        elif database == DatabaseType.NCBI_GENE:
            return self._search_ncbi_gene(query)
        else:
            logger.warning(f"Database {database.value} not yet implemented")
            return []

    def _search_pubmed(self, query: LiteratureQuery) -> List[SearchResult]:
        """Search PubMed database using E-utilities API"""
        logger.info("Searching PubMed...")

        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_terms = " AND ".join(query.search_terms)

        params = {
            "db": "pubmed",
            "term": search_terms,
            "retmax": min(query.max_results, 20),  # PubMed limit
            "retmode": "json",
            "sort": "relevance"
        }

        # Add date range if specified
        if query.date_range:
            start_date, end_date = query.date_range
            params["datetype"] = "edat"
            params["mindate"] = start_date.strftime("%Y/%m/%d")
            params["maxdate"] = end_date.strftime("%Y/%m/%d")

        try:
            # Search for PMIDs
            search_response = requests.get(base_url, params=params)
            search_response.raise_for_status()
            search_data = search_response.json()

            pmids = search_data.get("esearchresult", {}).get("idlist", [])

            if not pmids:
                logger.info("No PMIDs found for search")
                return []

            logger.info(f"Found {len(pmids)} PMIDs")

            # Fetch summaries for each PMID
            summaries_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            summary_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "json"
            }

            # Rate limiting
            time.sleep(0.4)

            summary_response = requests.get(summaries_url, params=summary_params)
            summary_response.raise_for_status()
            summary_data = summary_response.json()

            results = []
            for pmid in pmids:
                result = self._parse_pubmed_summary(pmid, summary_data.get("result", {}).get(pmid, {}))
                if result:
                    results.append(result)

            logger.info(f"Parsed {len(results)} PubMed results")
            return results

        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []

    def _parse_pubmed_summary(self, pmid: str, summary_data: Dict) -> Optional[SearchResult]:
        """Parse PubMed summary data into SearchResult"""
        try:
            title = summary_data.get("title", "")
            authors = [author.get("name", "") for author in summary_data.get("authors", [])]

            # Get abstract
            abstract = summary_data.get("abstract", "")
            if not abstract and "abstracttext" in summary_data:
                abstract = summary_data["abstracttext"]

            # Get journal info
            journal_data = summary_data.get("source", "")
            year = int(summary_data.get("pubdate", "2024").split()[0]) if summary_data.get("pubdate") else 2024

            # Get DOI
            doi = ""
            if "articleids" in summary_data:
                for article_id in summary_data["articleids"]:
                    if article_id.get("idtype") == "doi":
                        doi = article_id.get("value", "")
                        break

            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

            result = SearchResult(
                title=title,
                authors=authors,
                abstract=abstract,
                journal=journal_data,
                year=year,
                doi=doi,
                url=url,
                database=DatabaseType.PUBMED,
                pmid=pmid
            )

            # Calculate relevance score based on query matching
            result.relevance_score = self._calculate_relevance(result, [" ".join(query.search_terms)])

            return result

        except Exception as e:
            logger.warning(f"Error parsing PMID {pmid}: {e}")
            return None

    def _search_arxiv(self, query: LiteratureQuery) -> List[SearchResult]:
        """Search arXiv database"""
        logger.info("Searching arXiv...")

        base_url = "http://export.arxiv.org/api/query"
        search_terms = " AND ".join([f"all:{term}" for term in query.search_terms])

        params = {
            "search_query": search_terms,
            "start": 0,
            "max_results": min(query.max_results, 10),
            "sortBy": "relevance",
            "sortOrder": "descending"
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()

            # Parse arXiv response (simple XML parsing)
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            results = []
            for entry in root.findall(".//entry"):
                title = entry.findtext("title")
                summary = entry.findtext("summary")

                # Authors
                authors = []
                for author in entry.findall(".//author"):
                    name = author.findtext("name")
                    if name:
                        authors.append(name)

                # Published date
                published = entry.findtext("published")
                year = int(published[:4]) if published else 2024

                # URLs
                arxiv_id = entry.findtext("id")
                url = entry.findtext("link") or f"https://arxiv.org/abs/{arxiv_id}"

                # Journal reference (if published)
                journal_ref = entry.findtext("journal_ref")
                journal = journal_ref if journal_ref else "arXiv preprint"

                result = SearchResult(
                    title=title,
                    authors=authors,
                    abstract=summary,
                    journal=journal,
                    year=year,
                    doi="",  # arXiv papers may not have DOI
                    url=url,
                    database=DatabaseType.ARXIV,
                    pmid=None
                )

                result.relevance_score = self._calculate_relevance(result, query.search_terms)
                results.append(result)

            logger.info(f"Found {len(results)} arXiv results")
            return results

        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
            return []

    def _search_biorxiv(self, query: LiteratureQuery) -> List[SearchResult]:
        """Search bioRxiv database"""
        logger.info("Searching bioRxiv...")

        # bioRxiv uses Content Server API
        base_url = "https://www.biorxiv.org/search"

        search_terms = " ".join(query.search_terms)

        params = {
            "q": search_terms,
            "page": 1,
            "numresults": min(query.max_results, 10)
        }

        try:
            # Note: bioRxiv doesn't have a public API, so we'll use a simplified approach
            # In production, you'd need to use their official API or web scraping
            logger.warning("bioRxiv API not fully implemented - using placeholder")

            # Placeholder implementation
            placeholder_result = SearchResult(
                title=f"Placeholder result for: {search_terms}",
                authors=["Various Authors"],
                abstract="bioRxiv search not fully implemented - API access required",
                journal="bioRxiv",
                year=2024,
                doi="",
                url="https://www.biorxiv.org",
                database=DatabaseType.BIORXIV,
                pmid=None
            )

            return [placeholder_result]

        except Exception as e:
            logger.error(f"Error searching bioRxiv: {e}")
            return []

    def _search_ncbi_gene(self, query: LiteratureQuery) -> List[SearchResult]:
        """Search NCBI Gene database"""
        logger.info("Searching NCBI Gene...")

        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

        params = {
            "db": "gene",
            "term": " ".join(query.search_terms),
            "retmax": min(query.max_results, 10),
            "retmode": "json"
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            gene_ids = data.get("esearchresult", {}).get("idlist", [])

            # Fetch gene summaries
            if gene_ids:
                summaries_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                summary_params = {
                    "db": "gene",
                    "id": ",".join(gene_ids),
                    "retmode": "json"
                }

                time.sleep(0.4)

                summary_response = requests.get(summaries_url, params=summary_params)
                summary_response.raise_for_status()
                summary_data = summary_response.json()

                results = []
                for gene_id in gene_ids:
                    gene_data = summary_data.get("result", {}).get(gene_id, {})

                    # Create search result from gene data
                    result = SearchResult(
                        title=f"Gene: {gene_data.get('name', gene_id)}",
                        authors=["NCBI Gene Database"],
                        abstract=gene_data.get("description", ""),
                        journal="NCBI Gene Database",
                        year=2024,
                        doi="",
                        url=f"https://www.ncbi.nlm.nih.gov/gene/{gene_id}",
                        database=DatabaseType.NCBI_GENE,
                        pmid=None
                    )

                    result.relevance_score = 0.7  # Gene database results are highly relevant
                    results.append(result)

                logger.info(f"Found {len(results)} NCBI Gene results")
                return results

            return []

        except Exception as e:
            logger.error(f"Error searching NCBI Gene: {e}")
            return []

    def get_citation(self, pmid: str) -> Optional[Citation]:
        """Get formatted citation for PMID"""
        if pmid in self.citation_cache:
            return self.citation_cache[pmid]

        # Fetch citation data
        try:
            summaries_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            params = {
                "db": "pubmed",
                "id": pmid,
                "retmode": "json"
            }

            time.sleep(0.4)

            response = requests.get(summaries_url, params=params)
            response.raise_for_status()
            data = response.json()

            summary_data = data.get("result", {}).get(pmid, {})

            # Create citation
            citation = Citation(
                authors=[author.get("name", "") for author in summary_data.get("authors", [])],
                title=summary_data.get("title", ""),
                journal=summary_data.get("source", ""),
                year=int(summary_data.get("pubdate", "2024").split()[0]) if summary_data.get("pubdate") else 2024,
                volume=summary_data.get("volume"),
                issue=summary_data.get("issue"),
                pages=summary_data.get("pages"),
                doi=summary_data.get("elocationid", ""),  # May need formatting
                pmid=pmid
            )

            self.citation_cache[pmid] = citation
            return citation

        except Exception as e:
            logger.error(f"Error getting citation for PMID {pmid}: {e}")
            return None

    def synthesize_literature(self, query_id: str, focus_areas: List[str] = None) -> Dict[str, Any]:
        """
        Synthesize literature from search results into coherent analysis.
        """
        if query_id not in self.search_results:
            logger.warning(f"No search results found for query {query_id}")
            return {}

        results = self.search_results[query_id]

        logger.info(f"Synthesizing literature from {len(results)} results")

        synthesis = {
            "total_papers": len(results),
            "date_range": self._get_date_range(results),
            "journals": self._get_journal_distribution(results),
            "key_themes": self._extract_key_themes(results, focus_areas),
            "citation_overview": [f"{r.authors[0] if r.authors else 'Unknown'} et al. ({r.year})" for r in results[:10]],
            "highly_cited_works": self._identify_highly_cited(results),
            "research_gaps": self._identify_research_gaps(results, focus_areas),
            "methodologies": self._extract_methodologies(results),
            "summary": self._generate_literature_summary(results)
        }

        logger.info("Literature synthesis complete")

        return synthesis

    def _calculate_relevance(self, result: SearchResult, search_terms: List[str]) -> float:
        """Calculate relevance score based on search term matching"""
        if not search_terms:
            return 0.5

        score = 0.0
        search_text = " ".join([result.title, result.abstract]).lower()

        for term in search_terms:
            term_lower = term.lower()
            # Exact phrase match in title
            if term_lower in result.title.lower():
                score += 0.3
            # Word match in title
            elif any(word in result.title.lower() for word in term_lower.split()):
                score += 0.2
            # Match in abstract
            elif term_lower in result.abstract.lower():
                score += 0.1
            # Word match in abstract
            elif any(word in result.abstract.lower() for word in term_lower.split()):
                score += 0.05

        return min(score, 1.0)

    def _get_date_range(self, results: List[SearchResult]) -> Dict[str, int]:
        """Get date range of results"""
        if not results:
            return {}

        years = [r.year for r in results if r.year]
        if not years:
            return {}

        return {
            "earliest": min(years),
            "latest": max(years),
            "span": max(years) - min(years)
        }

    def _get_journal_distribution(self, results: List[SearchResult]) -> Dict[str, int]:
        """Get distribution of journals"""
        journals = {}
        for result in results:
            if result.journal:
                journals[result.journal] = journals.get(result.journal, 0) + 1
        return journals

    def _extract_key_themes(self, results: List[SearchResult], focus_areas: List[str]) -> List[str]:
        """Extract key themes from literature"""
        themes = []

        # Simple keyword extraction from titles and abstracts
        word_counts = {}
        for result in results[:20]:  # Analyze top 20
            text = f"{result.title} {result.abstract}".lower()
            words = re.findall(r'\b[a-z]{4,}\b', text)

            for word in words:
                if word not in ["that", "this", "with", "from", "have", "been", "were", "are"]:
                    word_counts[word] = word_counts.get(word, 0) + 1

        # Get top themes
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        themes = [word for word, count in sorted_words[:10] if count >= 3]

        return themes

    def _identify_highly_cited(self, results: List[SearchResult]) -> List[str]:
        """Identify potentially highly cited works (placeholder)"""
        # In production, this would use citation databases
        # For now, return recent papers from high-impact journals
        high_impact_journals = ["nature", "science", "cell", "pnas", "embo j"]

        highly_cited = []
        for result in results[:10]:
            if any(journal in result.journal.lower() for journal in high_impact_journals):
                highly_cited.append(f"{result.title[:60]}... ({result.journal})")

        return highly_cited

    def _identify_research_gaps(self, results: List[SearchResult], focus_areas: List[str]) -> List[str]:
        """Identify potential research gaps"""
        gaps = []

        if not focus_areas:
            return gaps

        # Simple gap analysis: check if focus areas are well-covered
        for area in focus_areas:
            area_lower = area.lower()
            coverage = sum(1 for r in results if area_lower in r.title.lower() or area_lower in r.abstract.lower())

            if coverage < 3:  # Less than 3 papers covering the area
                gaps.append(f"Limited research on: {area}")

        return gaps

    def _extract_methodologies(self, results: List[SearchResult]) -> List[str]:
        """Extract methodologies mentioned in literature"""
        methodologies = []

        method_keywords = ["crystallography", "sequencing", "microscopy", "assay", "analysis",
                          "simulation", "modeling", "experiment", "computational", "statistical"]

        for result in results[:15]:
            text = result.abstract.lower()
            found_methods = []
            for method in method_keywords:
                if method in text:
                    found_methods.append(method)

            if found_methods:
                methodologies.append(f"{', '.join(found_methods)} ({result.year})")

        return methodologies

    def _generate_literature_summary(self, results: List[SearchResult]) -> str:
        """Generate overall summary of literature"""
        if not results:
            return "No results found for summary generation."

        summary_parts = []

        summary_parts.append(f"Analyzed {len(results)} research papers")

        # Topic overview
        if results:
            first_paper = results[0]
            summary_parts.append(f"Research spans {min(r.year for r in results)} to {max(r.year for r in results)}")

        # Key focus areas
        themes = self._extract_key_themes(results, None)
        if themes:
            summary_parts.append(f"Primary research themes: {', '.join(themes[:5])}")

        # Methodologies
        methods = self._extract_methodologies(results)
        if methods:
            method_names = list(set(m.split()[0] for m in methods[:5]))
            summary_parts.append(f"Common methodologies include: {', '.join(method_names)}")

        return ". ".join(summary_parts) + "."

# Factory function for creating literature database access
def create_literature_database_access() -> LiteratureDatabaseAccess:
    """Create and initialize literature database access system."""
    system = LiteratureDatabaseAccess()
    return system

# Singleton instance
_literature_database_access_instance = None

def get_literature_database_access() -> LiteratureDatabaseAccess:
    """Get or create singleton literature database access instance."""
    global _literature_database_access_instance
    if _literature_database_access_instance is None:
        _literature_database_access_instance = create_literature_database_access()
    return _literature_database_access_instance