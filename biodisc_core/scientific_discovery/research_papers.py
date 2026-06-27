"""
Research Paper Processing Module

Handles PDF processing, citation networks, and literature mining for scientific papers.
This module can be used for both biology and astronomy papers.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

# PDF library availability checks
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False


@dataclass
class Paper:
    """Scientific paper metadata and content"""
    title: str
    authors: List[str]
    abstract: str
    year: int
    journal: str
    doi: str
    pdf_path: Optional[Path] = None
    full_text: Optional[str] = None
    citations: List[str] = None

    def __post_init__(self):
        if self.citations is None:
            self.citations = []


@dataclass
class CitationGraph:
    """Citation network structure"""
    papers: Dict[str, Paper]
    citation_links: Dict[str, List[str]]  # paper_id -> list of cited paper_ids

    def __post_init__(self):
        if not self.papers:
            self.papers = {}
        if not self.citation_links:
            self.citation_links = {}


class PDFProcessor:
    """
    PDF text extraction with multiple library fallbacks.

    Supports multiple PDF libraries with automatic fallback.
    """

    def __init__(self):
        self.has_pdf_support = HAS_PDFPLUMBER or HAS_PYPDF2

        if not self.has_pdf_support:
            logger.warning("No PDF library available. Install pdfplumber or PyPDF2.")

        logger.info(f"PDFProcessor initialized (pdfplumber={HAS_PDFPLUMBER}, PyPDF2={HAS_PYPDF2})")

    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract full text from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text content
        """
        if not self.has_pdf_support:
            raise ImportError("No PDF library available. Install pdfplumber or PyPDF2.")

        if HAS_PDFPLUMBER:
            return self._extract_with_pdfplumber(pdf_path)
        elif HAS_PYPDF2:
            return self._extract_with_pypdf2(pdf_path)
        else:
            raise ImportError("No PDF library available")

    def _extract_with_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber"""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting text with pdfplumber: {e}")
        return text

    def _extract_with_pypdf2(self, pdf_path: Path) -> str:
        """Extract text using PyPDF2"""
        text = ""
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {e}")
        return text


class CitationNetwork:
    """
    Citation network analysis and management.

    Builds and analyzes citation relationships between papers.
    """

    def __init__(self):
        self.graph = CitationGraph(papers={}, citation_links={})

    def add_paper(self, paper: Paper) -> str:
        """Add paper to citation network"""
        paper_id = self._generate_paper_id(paper)
        self.graph.papers[paper_id] = paper
        self.graph.citation_links[paper_id] = paper.citations
        return paper_id

    def _generate_paper_id(self, paper: Paper) -> str:
        """Generate unique ID for paper"""
        if paper.doi:
            return paper.doi
        else:
            content = f"{paper.title}{paper.year}{paper.journal}"
            return hashlib.md5(content.encode()).hexdigest()[:16]

    def get_citation_count(self, paper_id: str) -> int:
        """Get number of citations for a paper"""
        count = 0
        for citing_papers in self.graph.citation_links.values():
            if paper_id in citing_papers:
                count += 1
        return count

    def get_co_citation_network(self, paper_ids: List[str]) -> Dict[str, int]:
        """Get co-citation counts between papers"""
        co_citations = {}
        for citing_papers in self.graph.citation_links.values():
            cited_in_source = [p for p in citing_papers if p in paper_ids]
            for i, p1 in enumerate(cited_in_source):
                for p2 in cited_in_source[i+1:]:
                    key = tuple(sorted([p1, p2]))
                    co_citations[key] = co_citations.get(key, 0) + 1
        return co_citations


class LiteratureMiner:
    """
    Literature mining and knowledge extraction.

    Extracts key information from research papers.
    """

    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.citation_network = CitationNetwork()

    def process_paper(self, pdf_path: Path) -> Paper:
        """Process research paper and extract metadata"""
        text = self.pdf_processor.extract_text(pdf_path)
        metadata = self._extract_metadata(text)

        paper = Paper(
            title=metadata.get('title', 'Unknown'),
            authors=metadata.get('authors', []),
            abstract=metadata.get('abstract', ''),
            year=metadata.get('year', 0),
            journal=metadata.get('journal', 'Unknown'),
            doi=metadata.get('doi', ''),
            pdf_path=pdf_path,
            full_text=text
        )

        return paper

    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from paper text"""
        metadata = {}

        # Simple extraction heuristics (can be improved)
        lines = text.split('\n')

        # Try to find title (first non-empty line)
        for line in lines:
            if line.strip() and len(line.strip()) > 10:
                metadata['title'] = line.strip()
                break

        # Try to find abstract
        abstract_match = re.search(r'Abstract\s*:?\s*(.*?)(?:\n\s*(?:Keywords?|Introduction|1\.|$))', text, re.DOTALL | re.IGNORECASE)
        if abstract_match:
            metadata['abstract'] = abstract_match.group(1).strip()

        return metadata


class PaperAnalyzer:
    """
    Advanced paper analysis and comparison.

    Analyzes research papers for patterns, themes, and relationships.
    """

    def __init__(self):
        self.literature_miner = LiteratureMiner()

    def analyze_papers(self, papers: List[Paper]) -> Dict[str, Any]:
        """Analyze collection of papers"""
        analysis = {
            'total_papers': len(papers),
            'year_distribution': {},
            'journal_distribution': {},
            'common_keywords': self._extract_common_keywords(papers)
        }

        for paper in papers:
            # Year distribution
            year = paper.year
            analysis['year_distribution'][year] = analysis['year_distribution'].get(year, 0) + 1

            # Journal distribution
            journal = paper.journal
            analysis['journal_distribution'][journal] = analysis['journal_distribution'].get(journal, 0) + 1

        return analysis

    def _extract_common_keywords(self, papers: List[Paper]) -> Dict[str, int]:
        """Extract common keywords from paper titles and abstracts"""
        keywords = {}

        for paper in papers:
            text = f"{paper.title} {paper.abstract}"
            words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())

            for word in words:
                if word not in ['abstract', 'introduction', 'conclusion', 'results', 'methods']:
                    keywords[word] = keywords.get(word, 0) + 1

        # Return top 20 keywords
        return dict(sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:20])


def extract_paper_metadata(pdf_path: Path) -> Dict[str, Any]:
    """Extract metadata from PDF paper"""
    miner = LiteratureMiner()
    paper = miner.process_paper(pdf_path)
    return {
        'title': paper.title,
        'authors': paper.authors,
        'abstract': paper.abstract,
        'year': paper.year,
        'journal': paper.journal,
        'doi': paper.doi
    }


def build_citation_network(papers: List[Paper]) -> CitationNetwork:
    """Build citation network from papers"""
    network = CitationNetwork()
    for paper in papers:
        network.add_paper(paper)
    return network.graph
