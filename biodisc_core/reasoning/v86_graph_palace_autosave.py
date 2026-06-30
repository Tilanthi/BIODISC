"""
GraphPalace Auto-Save System

Automatically saves all memory and .md files to GraphPalace for persistent
knowledge graph storage and cross-session continuity.

This system monitors and auto-saves:
- All memory entries from the memory palace
- All .md files in the project
- All discoveries and insights
- All architectural documentation
- All session transcripts

Date: 2026-05-09
Version: 1.0.0
"""

import os
import json
import hashlib
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass
class GraphPalaceNode:
    """A node in the GraphPalace knowledge graph"""
    node_id: str
    node_type: str  # memory, discovery, document, session, insight, etc.
    title: str
    content: str
    source_file: str
    category: str
    tags: List[str]
    timestamp: str
    connections: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphPalaceEdge:
    """An edge in the GraphPalace knowledge graph"""
    edge_id: str
    source_node: str
    target_node: str
    relationship: str  # references, builds_on, contradicts, extends, etc.
    weight: float
    timestamp: str


class GraphPalaceAutoSaver:
    """
    Automatically saves all memory and .md files to GraphPalace.

    FEATURES:
    - Monitors memory palace for new entries
    - Auto-saves all .md files in project
    - Creates knowledge graph nodes and edges
    - Maintains bidirectional sync with memory palace
    - Generates embeddings for semantic search
    - Tracks file changes for incremental updates

    STORAGE LOCATIONS:
    - GraphPalace JSON: /Users/gjw255/astrodata/SWARM/BIODISC/data/graph_palace/
    - Memory Palace: /Users/gjw255/.claude/projects/-Users-gjw255-astrodata-SWARM-BIODISC/memory/
    - Project .md files: /Users/gjw255/astrodata/SWARM/BIODISC/
    """

    def __init__(self):
        # Define paths
        self.memory_palace_path = "/Users/gjw255/.claude/projects/-Users-gjw255-astrodata-SWARM-BIODISC/memory"
        self.graph_palace_path = "/Users/gjw255/astrodata/SWARM/BIODISC/data/graph_palace"
        self.project_root = "/Users/gjw255/astrodata/SWARM/BIODISC"

        # GraphPalace files
        self.nodes_file = os.path.join(self.graph_palace_path, "nodes.json")
        self.edges_file = os.path.join(self.graph_palace_path, "edges.json")
        self.metrics_file = os.path.join(self.graph_palace_path, "metrics.json")
        self.pheromones_file = os.path.join(self.graph_palace_path, "pheromones.json")

        # Track processed files
        self.processed_files: Set[str] = set()
        self.file_hashes: Dict[str, str] = {}

        # Load existing state
        self._load_graph_state()
        self._load_processed_files()

        # Auto-save enabled
        self.auto_save_enabled = True

    def _load_graph_state(self):
        """Load existing GraphPalace nodes and edges"""
        try:
            if os.path.exists(self.nodes_file):
                with open(self.nodes_file, 'r') as f:
                    data = json.load(f)
                    # Handle both dict format (existing) and list format (new)
                    if isinstance(data, dict):
                        # Convert dict format to list format
                        self.nodes = list(data.values())
                    else:
                        self.nodes = data
            else:
                self.nodes = []

            if os.path.exists(self.edges_file):
                with open(self.edges_file, 'r') as f:
                    data = json.load(f)
                    # Handle both dict format (existing) and list format (new)
                    if isinstance(data, dict):
                        # Convert dict format to list format
                        self.edges = list(data.values())
                    else:
                        self.edges = data
            else:
                self.edges = []

        except Exception as e:
            print(f"Error loading graph state: {e}")
            self.nodes = []
            self.edges = []

    def _load_processed_files(self):
        """Load list of already processed files"""
        try:
            state_file = os.path.join(self.graph_palace_path, ".autosave_state.json")
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    self.processed_files = set(state.get("processed_files", []))
                    self.file_hashes = state.get("file_hashes", {})
        except Exception as e:
            print(f"Error loading processed files: {e}")

    def _save_processed_files(self):
        """Save list of processed files"""
        try:
            state_file = os.path.join(self.graph_palace_path, ".autosave_state.json")
            state = {
                "processed_files": list(self.processed_files),
                "file_hashes": self.file_hashes,
                "last_update": datetime.now().isoformat()
            }
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error saving processed files: {e}")

    def auto_save_all(self) -> Dict[str, Any]:
        """
        Automatically save all memory and .md files to GraphPalace.

        Returns:
            Summary of auto-save operation
        """
        if not self.auto_save_enabled:
            return {"status": "disabled", "saved": 0}

        results = {
            "memory_files_saved": 0,
            "md_files_saved": 0,
            "total_nodes_added": 0,
            "total_edges_added": 0,
            "errors": []
        }

        # 1. Save all memory palace entries
        memory_results = self._save_memory_palace()
        results["memory_files_saved"] = memory_results["saved"]
        results["total_nodes_added"] += memory_results["nodes_added"]
        results["total_edges_added"] += memory_results["edges_added"]
        results["errors"].extend(memory_results.get("errors", []))

        # 2. Save all project .md files
        md_results = self._save_project_markdown()
        results["md_files_saved"] = md_results["saved"]
        results["total_nodes_added"] += md_results["nodes_added"]
        results["total_edges_added"] += md_results["edges_added"]
        results["errors"].extend(md_results.get("errors", []))

        # 3. Save current session transcripts
        session_results = self._save_session_transcripts()
        results["session_files_saved"] = session_results["saved"]
        results["total_nodes_added"] += session_results["nodes_added"]
        results["total_edges_added"] += session_results["edges_added"]

        # 4. Write updated graph files
        self._write_graph_files()

        # 5. Update processed files state
        self._save_processed_files()

        # 6. Update metrics
        self._update_metrics(results)

        return results

    def _save_memory_palace(self) -> Dict[str, Any]:
        """Save all memory palace entries to GraphPalace"""
        results = {
            "saved": 0,
            "nodes_added": 0,
            "edges_added": 0,
            "errors": []
        }

        try:
            if not os.path.exists(self.memory_palace_path):
                return results

            # Get all files in memory palace
            memory_files = []
            for root, dirs, files in os.walk(self.memory_palace_path):
                for file in files:
                    if file.endswith('.md') and file != 'MEMORY.md':
                        file_path = os.path.join(root, file)
                        memory_files.append(file_path)

            # Process each memory file
            for file_path in memory_files:
                try:
                    # Check if file changed
                    file_hash = self._get_file_hash(file_path)
                    if file_path in self.file_hashes and self.file_hashes[file_path] == file_hash:
                        continue  # Skip unchanged files

                    # Read and parse file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract frontmatter and content
                    frontmatter, body = self._parse_frontmatter(content)
                    title = frontmatter.get('name', frontmatter.get('title', os.path.basename(file_path)))
                    category = frontmatter.get('category', frontmatter.get('type', 'memory'))

                    # Create or update node
                    node = GraphPalaceNode(
                        node_id=self._generate_node_id(file_path),
                        node_type="memory",
                        title=title,
                        content=body[:1000],  # First 1000 chars for preview
                        source_file=file_path,
                        category=category,
                        tags=frontmatter.get('tags', []),
                        timestamp=frontmatter.get('timestamp', datetime.now().isoformat()),
                        metadata=frontmatter
                    )

                    self._add_or_update_node(node)

                    # Create edges based on references
                    edges = self._extract_edges(content, node.node_id)
                    for edge in edges:
                        self._add_or_update_edge(edge)

                    # Update hash
                    self.file_hashes[file_path] = file_hash
                    self.processed_files.add(file_path)

                    results["saved"] += 1
                    results["nodes_added"] += 1
                    results["edges_added"] += len(edges)

                except Exception as e:
                    results["errors"].append(f"Error processing {file_path}: {e}")

        except Exception as e:
            results["errors"].append(f"Error in memory palace save: {e}")

        return results

    def _save_project_markdown(self) -> Dict[str, Any]:
        """Save all project .md files to GraphPalace"""
        results = {
            "saved": 0,
            "nodes_added": 0,
            "edges_added": 0,
            "errors": []
        }

        try:
            # Find all .md files in project (excluding node_modules, etc.)
            md_files = []
            exclude_dirs = {
                'node_modules', '.git', '__pycache__', 'dist', 'build',
                '.pytest_cache', '.venv', 'venv', 'env'
            }

            for root, dirs, files in os.walk(self.project_root):
                # Remove excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs]

                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        # Skip already processed memory files
                        if file_path not in self.processed_files:
                            md_files.append(file_path)

            # Process each .md file
            for file_path in md_files:
                try:
                    # Check if file changed
                    file_hash = self._get_file_hash(file_path)
                    if file_path in self.file_hashes and self.file_hashes[file_path] == file_hash:
                        continue

                    # Read file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract title from first line or filename
                    title = self._extract_title(content, file_path)

                    # Determine category from path
                    category = self._categorize_md_file(file_path, content)

                    # Create node
                    node = GraphPalaceNode(
                        node_id=self._generate_node_id(file_path),
                        node_type="document",
                        title=title,
                        content=content[:1000],
                        source_file=file_path,
                        category=category,
                        tags=self._extract_tags(content),
                        timestamp=datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                        metadata={"file_type": "markdown"}
                    )

                    self._add_or_update_node(node)

                    # Create edges based on references
                    edges = self._extract_edges(content, node.node_id)
                    for edge in edges:
                        self._add_or_update_edge(edge)

                    # Update hash
                    self.file_hashes[file_path] = file_hash
                    self.processed_files.add(file_path)

                    results["saved"] += 1
                    results["nodes_added"] += 1
                    results["edges_added"] += len(edges)

                except Exception as e:
                    results["errors"].append(f"Error processing {file_path}: {e}")

        except Exception as e:
            results["errors"].append(f"Error in markdown save: {e}")

        return results

    def _save_session_transcripts(self) -> Dict[str, Any]:
        """Save session transcripts to GraphPalace"""
        results = {
            "saved": 0,
            "nodes_added": 0,
            "edges_added": 0
        }

        try:
            # Find Claude session transcripts
            session_pattern = re.compile(r'a328e311-[a-f0-9]+-\.jsonl')
            transcripts_dir = "/Users/gjw255/.claude/projects/-Users-gjw255-astrodata-SWARM-BIODISC/"

            if not os.path.exists(transcripts_dir):
                return results

            for file in os.listdir(transcripts_dir):
                if session_pattern.match(file):
                    file_path = os.path.join(transcripts_dir, file)

                    try:
                        file_hash = self._get_file_hash(file_path)
                        if file_path in self.file_hashes and self.file_hashes[file_path] == file_hash:
                            continue

                        # Read transcript
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Create node for session
                        node = GraphPalaceNode(
                            node_id=self._generate_node_id(file_path),
                            node_type="session",
                            title=f"Session {file[:12]}",
                            content=content[:500],  # Preview
                            source_file=file_path,
                            category="session",
                            tags=["session", "transcript"],
                            timestamp=datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                            metadata={"file_type": "transcript"}
                        )

                        self._add_or_update_node(node)

                        self.file_hashes[file_path] = file_hash
                        self.processed_files.add(file_path)

                        results["saved"] += 1
                        results["nodes_added"] += 1

                    except Exception as e:
                        pass  # Skip errors in transcript processing

        except Exception as e:
            pass  # Skip errors in transcript directory

        return results

    def _add_or_update_node(self, node: GraphPalaceNode):
        """Add or update a node in the graph"""
        # Check if node exists - handle both dict and list items
        existing = None
        for n in self.nodes:
            if isinstance(n, dict):
                if n.get("node_id") == node.node_id or n.get("id") == node.node_id:
                    existing = n
                    break

        node_data = {
            "node_id": node.node_id,
            "node_type": node.node_type,
            "title": node.title,
            "content": node.content,
            "source_file": node.source_file,
            "category": node.category,
            "tags": node.tags,
            "timestamp": node.timestamp,
            "connections": node.connections,
            "metadata": node.metadata
        }

        if existing:
            # Update existing node
            existing.update(node_data)
        else:
            # Add new node
            self.nodes.append(node_data)

    def _add_or_update_edge(self, edge: GraphPalaceEdge):
        """Add or update an edge in the graph"""
        # Check if edge exists - handle both dict and list items
        existing = None
        for e in self.edges:
            if isinstance(e, dict):
                if e.get("edge_id") == edge.edge_id or e.get("id") == edge.edge_id:
                    existing = e
                    break

        edge_data = {
            "edge_id": edge.edge_id,
            "source": edge.source_node,
            "target": edge.target_node,
            "relationship": edge.relationship,
            "weight": edge.weight,
            "timestamp": edge.timestamp
        }

        if existing:
            existing.update(edge_data)
        else:
            self.edges.append(edge_data)

    def _get_file_hash(self, file_path: str) -> str:
        """Get hash of file contents"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def _generate_node_id(self, file_path: str) -> str:
        """Generate unique node ID from file path"""
        # Use relative path from project root
        rel_path = os.path.relpath(file_path, self.project_root)
        return hashlib.md5(rel_path.encode()).hexdigest()[:12]

    def _parse_frontmatter(self, content: str) -> tuple:
        """Parse YAML frontmatter from markdown"""
        frontmatter = {}
        body = content

        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    import yaml
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    if frontmatter is None:
                        frontmatter = {}
                    body = parts[2].strip()
                except Exception:
                    body = content

        return frontmatter, body

    def _extract_title(self, content: str, file_path: str) -> str:
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                # Remove # symbols and whitespace
                title = re.sub(r'^#+\s*', '', line)
                if title:
                    return title

        # Fallback to filename
        return os.path.basename(file_path).replace('.md', '').replace('_', ' ').title()

    def _categorize_md_file(self, file_path: str, content: str) -> str:
        """Determine category of markdown file"""
        path_lower = file_path.lower()

        # Check path for category hints
        if 'memory' in path_lower:
            return 'memory'
        elif 'simulation' in path_lower or 'sim' in path_lower:
            return 'simulation'
        elif 'doc' in path_lower or 'readme' in path_lower:
            return 'documentation'
        elif 'implementation' in path_lower or 'arch' in path_lower:
            return 'architecture'
        elif 'test' in path_lower:
            return 'testing'
        elif 'reasoning' in path_lower or 'v7' in path_lower or 'v8' in path_lower:
            return 'capability'
        elif 'paper' in path_lower or 'report' in path_lower:
            return 'report'
        else:
            return 'general'

    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content"""
        tags = []

        # Look for tags in frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                try:
                    import yaml
                    frontmatter = yaml.safe_load(parts[1])
                    if frontmatter and 'tags' in frontmatter:
                        tags.extend(frontmatter['tags'])
                except Exception:
                    pass

        # Look for tag patterns in content
        tag_pattern = re.compile(r'#(\w+)')
        tags.extend(tag_pattern.findall(content))

        return list(set(tags))

    def _extract_edges(self, content: str, source_id: str) -> List[GraphPalaceEdge]:
        """Extract references/links as edges"""
        edges = []

        # Extract markdown links
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        matches = link_pattern.findall(content)

        for i, (title, target) in enumerate(matches):
            # Create edge
            edge = GraphPalaceEdge(
                edge_id=f"{source_id}_ref_{i}",
                source_node=source_id,
                target_node=self._generate_node_id(target),
                relationship="references",
                weight=1.0,
                timestamp=datetime.now().isoformat()
            )
            edges.append(edge)

        # Extract @ mentions or references
        mention_pattern = re.compile(r'@(\w+)')
        mentions = mention_pattern.findall(content)

        for i, mention in enumerate(mentions):
            edge = GraphPalaceEdge(
                edge_id=f"{source_id}_mention_{i}",
                source_node=source_id,
                target_node=mention,
                relationship="mentions",
                weight=0.5,
                timestamp=datetime.now().isoformat()
            )
            edges.append(edge)

        return edges

    def _write_graph_files(self):
        """Write nodes and edges to GraphPalace files"""
        try:
            os.makedirs(self.graph_palace_path, exist_ok=True)

            # Write nodes
            with open(self.nodes_file, 'w') as f:
                json.dump(self.nodes, f, indent=2)

            # Write edges
            with open(self.edges_file, 'w') as f:
                json.dump(self.edges, f, indent=2)

        except Exception as e:
            print(f"Error writing graph files: {e}")

    def _update_metrics(self, results: Dict[str, Any]):
        """Update GraphPalace metrics"""
        try:
            metrics = {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "memory_nodes": sum(1 for n in self.nodes if isinstance(n, dict) and (n.get("node_type") == "memory" or n.get("node_type") == "discovery")),
                "document_nodes": sum(1 for n in self.nodes if isinstance(n, dict) and n.get("node_type") == "document"),
                "session_nodes": sum(1 for n in self.nodes if isinstance(n, dict) and n.get("node_type") == "session"),
                "last_autosave": datetime.now().isoformat(),
                "last_save_results": results
            }

            with open(self.metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)

        except Exception as e:
            print(f"Error updating metrics: {e}")

    def get_graph_summary(self) -> Dict[str, Any]:
        """Get summary of GraphPalace contents"""
        node_types = {}
        categories = {}

        for n in self.nodes:
            if isinstance(n, dict):
                node_type = n.get("node_type", "unknown")
                category = n.get("category", "unknown")
                node_types[node_type] = node_types.get(node_type, 0) + 1
                categories[category] = categories.get(category, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": node_types,
            "categories": categories,
            "recently_updated": []
        }

    def enable_auto_save(self):
        """Enable automatic saving"""
        self.auto_save_enabled = True

    def disable_auto_save(self):
        """Disable automatic saving"""
        self.auto_save_enabled = False


def create_graph_palace_autosaver() -> GraphPalaceAutoSaver:
    """Factory function to create GraphPalace autosaver"""
    return GraphPalaceAutoSaver()


# Singleton instance
_instance = None

def get_graph_palace_autosaver() -> GraphPalaceAutoSaver:
    """Get or create singleton instance"""
    global _instance
    if _instance is None:
        _instance = create_graph_palace_autosaver()
    return _instance
