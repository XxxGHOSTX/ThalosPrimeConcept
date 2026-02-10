"""
Knowledge Space - Vector embeddings, knowledge graph, and raw documents.

Provides automated discovery with hybrid reasoning capabilities.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np
from dataclasses import dataclass


@dataclass
class Document:
    """A document in the knowledge space."""
    doc_id: str
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class KnowledgeNode:
    """A node in the knowledge graph."""
    node_id: str
    node_type: str
    properties: Dict[str, Any]
    embedding: Optional[np.ndarray] = None


@dataclass
class KnowledgeEdge:
    """An edge in the knowledge graph."""
    edge_id: str
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any]


class KnowledgeSpace:
    """
    A knowledge space with vector embeddings, knowledge graph, and raw documents.
    
    Supports automated discovery and hybrid reasoning.
    """
    
    def __init__(self, embedding_dim: int = 384):
        """
        Initialize the knowledge space.
        
        Args:
            embedding_dim: Dimension of embedding vectors
        """
        self.embedding_dim = embedding_dim
        self.documents: Dict[str, Document] = {}
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: Dict[str, KnowledgeEdge] = {}
        self.embeddings: Dict[str, np.ndarray] = {}
    
    def add_document(self, document: Document) -> None:
        """
        Add a document to the knowledge space.
        
        Args:
            document: Document to add
        """
        self.documents[document.doc_id] = document
    
    def add_node(self, node: KnowledgeNode) -> None:
        """
        Add a node to the knowledge graph.
        
        Args:
            node: Node to add
        """
        self.nodes[node.node_id] = node
        if node.embedding is not None:
            self.embeddings[node.node_id] = node.embedding
    
    def add_edge(self, edge: KnowledgeEdge) -> None:
        """
        Add an edge to the knowledge graph.
        
        Args:
            edge: Edge to add
        """
        if edge.source_id not in self.nodes:
            raise ValueError(f"Source node {edge.source_id} not found")
        if edge.target_id not in self.nodes:
            raise ValueError(f"Target node {edge.target_id} not found")
        self.edges[edge.edge_id] = edge
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID."""
        return self.documents.get(doc_id)
    
    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def find_similar(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Find similar nodes using cosine similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (node_id, similarity_score) tuples
        """
        if len(self.embeddings) == 0:
            return []
        
        similarities = []
        query_norm = np.linalg.norm(query_embedding)
        
        for node_id, embedding in self.embeddings.items():
            embedding_norm = np.linalg.norm(embedding)
            if query_norm > 0 and embedding_norm > 0:
                similarity = np.dot(query_embedding, embedding) / (query_norm * embedding_norm)
                similarities.append((node_id, float(similarity)))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def get_neighbors(self, node_id: str, relationship_type: Optional[str] = None) -> List[KnowledgeNode]:
        """
        Get neighboring nodes in the knowledge graph.
        
        Args:
            node_id: ID of the node
            relationship_type: Optional filter by relationship type
            
        Returns:
            List of neighboring nodes
        """
        neighbors = []
        for edge in self.edges.values():
            if edge.source_id == node_id:
                if relationship_type is None or edge.relationship_type == relationship_type:
                    neighbor = self.nodes.get(edge.target_id)
                    if neighbor:
                        neighbors.append(neighbor)
        return neighbors
    
    def traverse_graph(self, start_node_id: str, max_depth: int = 3) -> List[str]:
        """
        Traverse the knowledge graph from a starting node.
        
        Args:
            start_node_id: ID of the starting node
            max_depth: Maximum traversal depth
            
        Returns:
            List of visited node IDs
        """
        visited = set()
        queue = [(start_node_id, 0)]
        result = []
        
        while queue:
            node_id, depth = queue.pop(0)
            if node_id in visited or depth > max_depth:
                continue
            
            visited.add(node_id)
            result.append(node_id)
            
            # Add neighbors to queue
            for neighbor in self.get_neighbors(node_id):
                if neighbor.node_id not in visited:
                    queue.append((neighbor.node_id, depth + 1))
        
        return result
    
    def hybrid_search(
        self,
        query_embedding: Optional[np.ndarray] = None,
        node_type: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        top_k: int = 10
    ) -> List[KnowledgeNode]:
        """
        Perform hybrid search combining vector similarity and graph properties.
        
        Args:
            query_embedding: Optional query embedding for similarity search
            node_type: Optional filter by node type
            properties: Optional filter by node properties
            top_k: Number of results to return
            
        Returns:
            List of matching nodes
        """
        candidates = list(self.nodes.values())
        
        # Filter by node type
        if node_type:
            candidates = [n for n in candidates if n.node_type == node_type]
        
        # Filter by properties
        if properties:
            filtered = []
            for node in candidates:
                match = True
                for key, value in properties.items():
                    if key not in node.properties or node.properties[key] != value:
                        match = False
                        break
                if match:
                    filtered.append(node)
            candidates = filtered
        
        # Sort by similarity if query embedding provided
        if query_embedding is not None:
            similar_ids = self.find_similar(query_embedding, top_k=len(candidates))
            similar_id_set = {node_id for node_id, _ in similar_ids}
            candidates = [n for n in candidates if n.node_id in similar_id_set]
            
            # Sort by similarity score
            id_to_score = {node_id: score for node_id, score in similar_ids}
            candidates.sort(key=lambda n: id_to_score.get(n.node_id, 0), reverse=True)
        
        return candidates[:top_k]
    
    def export_graph(self) -> Dict[str, Any]:
        """
        Export the knowledge graph structure.
        
        Returns:
            Dictionary with nodes and edges
        """
        return {
            "nodes": [
                {
                    "node_id": node.node_id,
                    "node_type": node.node_type,
                    "properties": node.properties,
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "edge_id": edge.edge_id,
                    "source_id": edge.source_id,
                    "target_id": edge.target_id,
                    "relationship_type": edge.relationship_type,
                    "properties": edge.properties,
                }
                for edge in self.edges.values()
            ],
        }
