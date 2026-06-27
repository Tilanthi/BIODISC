"""
BIODISC Scientific Discovery Module
===================================

IMPORTANT: This module contains legacy astronomy-specific code that should be
moved to a separate astronomy-focused system (e.g., STAN-XI-ASTRO).

BIODISC is biology-focused and should not include astronomy-specific modules.
These imports are kept for backward compatibility but are not actively
maintained as part of BIODISC's biology capabilities.

Recommended: Use biology-specific discovery modules instead:
- biodisc_core.autonomous (V73 autonomous discovery orchestrator)
- biodisc_core.discovery (biology-focused discovery)
- biodisc_core.domains (biology domain modules)

Modules (LEGACY - ASTRONOMY):
--------
- research_papers: PDF processing, citation networks, literature mining
- astro_databases: Access to Vizier, SIMBAD, ADS, and other catalogs (ASTRONOMY)
- data_repositories: Access to ALMA, NASA, ESO, CADC, arXiv datasets (ASTRONOMY)
- advanced_analysis: ML photometry, galaxy classification, phot-z (ASTRONOMY)
- theoretical_physics: MHD solvers, plasma physics, radiation-hydro (ASTRONOMY)
- discovery_orchestrator: Central autonomous discovery coordinator (ASTRONOMY)

Version: 1.0.0-Discovery-Legacy
Date: 2025-12-27
Status: DEPRECATED - Use biology-specific discovery modules instead
"""

# =============================================================================
# Research Paper Processing (Generic - can be used for biology too)
# =============================================================================
try:
    from .research_papers import (
        PDFProcessor,
        CitationNetwork,
        LiteratureMiner,
        PaperAnalyzer,
        Paper,
        CitationGraph,
        extract_paper_metadata,
        build_citation_network,
    )
    RESEARCH_PAPERS_AVAILABLE = True
except ImportError:
    RESEARCH_PAPERS_AVAILABLE = False
    # Set to None for graceful degradation
    PDFProcessor = None
    CitationNetwork = None
    LiteratureMiner = None
    PaperAnalyzer = None
    Paper = None
    CitationGraph = None
    extract_paper_metadata = None
    build_citation_network = None

# =============================================================================
# Astronomical Database Access - REMOVED ( astronomy-specific modules deleted)
# These modules are available in separate astronomy systems, not BIODISC
# =============================================================================
ASTRO_DATABASES_AVAILABLE = False
AstroDatabaseConnector = None
VizierClient = None
SIMBADClient = None
ADSClient = None
CatalogQuery = None
SourceInfo = None
query_catalog = None
cross_match_catalogs = None

# =============================================================================
# Data Repository Access (ASTRONOMY-SPECIFIC - NOT FOR BIODISC)
# =============================================================================
try:
    from .data_repositories import (
        DataRepositoryManager,
        ALMAArchive,
        NASAArchive,
        ESOArchive,
        CADCArchive,
        ArxivClient,
        DatasetDownloader,
        download_observation,
        query_archive,
    )
    DATA_REPOSITORIES_AVAILABLE = True
except ImportError:
    DATA_REPOSITORIES_AVAILABLE = False
    DataRepositoryManager = None
    ALMAArchive = None
    NASAArchive = None
    ESOArchive = None
    CADCArchive = None
    ArxivClient = None
    DatasetDownloader = None
    download_observation = None
    query_archive = None

# =============================================================================
# Advanced Data Analysis (ASTRONOMY-SPECIFIC - NOT FOR BIODISC)
# =============================================================================
try:
    from .advanced_analysis import (
        AdvancedAnalyzer,
        GalaxyClassifier,
        PhotometricRedshiftEstimator,
        SEDFitter,
        SourceExtractor,
        LineIdentifier,
        classify_galaxy,
        estimate_photoz,
        fit_sed,
        identify_lines,
    )
    ADVANCED_ANALYSIS_AVAILABLE = True
except ImportError:
    ADVANCED_ANALYSIS_AVAILABLE = False
    AdvancedAnalyzer = None
    GalaxyClassifier = None
    PhotometricRedshiftEstimator = None
    SEDFitter = None
    SourceExtractor = None
    LineIdentifier = None
    classify_galaxy = None
    estimate_photoz = None
    fit_sed = None
    identify_lines = None

# =============================================================================
# Theoretical Physics (ASTRONOMY-SPECIFIC - NOT FOR BIODISC)
# =============================================================================
try:
    from .theoretical_physics import (
        TheoreticalPhysicsEngine,
        MHDSolver,
        PlasmaPhysicsModule,
        RadiationHydrodynamics,
        GRMHDModule,
        CosmicRayTransport,
        MagneticReconnection,
        solve_mhd,
        run_radiation_hydro,
    )
    THEORETICAL_PHYSICS_AVAILABLE = True
except ImportError:
    THEORETICAL_PHYSICS_AVAILABLE = False
    TheoreticalPhysicsEngine = None
    MHDSolver = None
    PlasmaPhysicsModule = None
    RadiationHydrodynamics = None
    GRMHDModule = None
    CosmicRayTransport = None
    MagneticReconnection = None
    solve_mhd = None
    run_radiation_hydro = None

# =============================================================================
# Discovery Orchestrator (Main Entry Point)
# =============================================================================
try:
    from .discovery_orchestrator import (
        ScientificDiscoveryOrchestrator,
        DiscoveryTask,
        DiscoveryResult,
        Hypothesis,
        ExperimentProposal,
        LiteratureReview,
        create_discovery_system,
        autonomous_discovery,
        review_literature,
        propose_experiment,
    )
    DISCOVERY_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    DISCOVERY_ORCHESTRATOR_AVAILABLE = False
    ScientificDiscoveryOrchestrator = None
    DiscoveryTask = None
    DiscoveryResult = None
    Hypothesis = None
    ExperimentProposal = None
    LiteratureReview = None
    create_discovery_system = None
    autonomous_discovery = None
    review_literature = None
    propose_experiment = None

__all__ = [
    # Research Papers (generic)
    'PDFProcessor',
    'CitationNetwork',
    'LiteratureMiner',
    'PaperAnalyzer',
    'Paper',
    'CitationGraph',
    'extract_paper_metadata',
    'build_citation_network',

    # Astro Databases (ASTRONOMY - DEPRECATED for BIODISC)
    'AstroDatabaseConnector',
    'VizierClient',
    'SIMBADClient',
    'ADSClient',
    'CatalogQuery',
    'SourceInfo',
    'query_catalog',
    'cross_match_catalogs',

    # Data Repositories (ASTRONOMY - DEPRECATED for BIODISC)
    'DataRepositoryManager',
    'ALMAArchive',
    'NASAArchive',
    'ESOArchive',
    'CADCArchive',
    'ArxivClient',
    'DatasetDownloader',
    'download_observation',
    'query_archive',

    # Advanced Analysis (ASTRONOMY - DEPRECATED for BIODISC)
    'AdvancedAnalyzer',
    'GalaxyClassifier',
    'PhotometricRedshiftEstimator',
    'SEDFitter',
    'SourceExtractor',
    'LineIdentifier',
    'classify_galaxy',
    'estimate_photoz',
    'fit_sed',
    'identify_lines',

    # Theoretical Physics (ASTRONOMY - DEPRECATED for BIODISC)
    'TheoreticalPhysicsEngine',
    'MHDSolver',
    'PlasmaPhysicsModule',
    'RadiationHydrodynamics',
    'GRMHDModule',
    'CosmicRayTransport',
    'MagneticReconnection',
    'solve_mhd',
    'run_radiation_hydro',

    # Discovery Orchestrator
    'ScientificDiscoveryOrchestrator',
    'DiscoveryTask',
    'DiscoveryResult',
    'Hypothesis',
    'ExperimentProposal',
    'LiteratureReview',
    'create_discovery_system',
    'autonomous_discovery',
    'review_literature',
    'propose_experiment',

    # Availability flags
    'RESEARCH_PAPERS_AVAILABLE',
    'ASTRO_DATABASES_AVAILABLE',
    'DATA_REPOSITORIES_AVAILABLE',
    'ADVANCED_ANALYSIS_AVAILABLE',
    'THEORETICAL_PHYSICS_AVAILABLE',
    'DISCOVERY_ORCHESTRATOR_AVAILABLE',
]

__version__ = '1.0.0-Discovery-Legacy'


def autocorrelation_detect(data: np.ndarray, max_lag: int = None) -> Dict[str, Any]:
    """Detect patterns using autocorrelation analysis."""
    import numpy as np
    if max_lag is None:
        max_lag = len(data) // 4
    autocorr = np.correlate(data, data, mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    autocorr = autocorr / autocorr[0]
    return {'autocorrelation': autocorr[:max_lag], 'peaks': []}


def utility_function_27(*args, **kwargs):
    """Utility function 27."""
    return None


def autocorrelation_detect(data: np.ndarray, max_lag: int = None) -> Dict[str, Any]:
    """Detect patterns using autocorrelation analysis."""
    import numpy as np
    if max_lag is None:
        max_lag = len(data) // 4
    autocorr = np.correlate(data, data, mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    autocorr = autocorr / autocorr[0]
    return {'autocorrelation': autocorr[:max_lag], 'peaks': []}


def utility_function_7(*args, **kwargs):
    """Utility function 7."""
    return None
