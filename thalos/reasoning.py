"""
Hybrid reasoning engine combining symbolic and vector-based approaches.

Provides reasoning capabilities over the knowledge space.
"""

from typing import Dict, List, Optional, Any, Tuple
import numpy as np

from .knowledge_space import KnowledgeSpace, KnowledgeNode, KnowledgeEdge


class ReasoningRule:
    """A symbolic reasoning rule."""
    
    def __init__(
        self,
        rule_id: str,
        pattern: Dict[str, Any],
        conclusion: Dict[str, Any]
    ):
        self.rule_id = rule_id
        self.pattern = pattern
        self.conclusion = conclusion
    
    def matches(self, node: KnowledgeNode) -> bool:
        """Check if a node matches this rule's pattern."""
        for key, value in self.pattern.items():
            if key == "node_type":
                if node.node_type != value:
                    return False
            elif key in node.properties:
                if node.properties[key] != value:
                    return False
            else:
                return False
        return True


class HybridReasoning:
    """
    Hybrid reasoning engine combining symbolic rules and vector similarity.
    """
    
    def __init__(self, knowledge_space: KnowledgeSpace):
        self.knowledge_space = knowledge_space
        self.rules: Dict[str, ReasoningRule] = {}
    
    def add_rule(self, rule: ReasoningRule) -> None:
        """Add a reasoning rule."""
        self.rules[rule.rule_id] = rule
    
    def apply_rules(self, node_id: str) -> List[Dict[str, Any]]:
        """
        Apply reasoning rules to a node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            List of inferred facts
        """
        node = self.knowledge_space.get_node(node_id)
        if not node:
            return []
        
        inferences = []
        for rule in self.rules.values():
            if rule.matches(node):
                inferences.append({
                    "rule_id": rule.rule_id,
                    "node_id": node_id,
                    "conclusion": rule.conclusion
                })
        
        return inferences
    
    def infer_relationships(
        self,
        node_id: str,
        relationship_type: str,
        threshold: float = 0.7
    ) -> List[Tuple[str, float]]:
        """
        Infer potential relationships using vector similarity.
        
        Args:
            node_id: ID of the source node
            relationship_type: Type of relationship to infer
            threshold: Similarity threshold
            
        Returns:
            List of (target_node_id, confidence) tuples
        """
        node = self.knowledge_space.get_node(node_id)
        if not node or node.embedding is None:
            return []
        
        # Find similar nodes
        similar = self.knowledge_space.find_similar(node.embedding, top_k=20)
        
        # Filter by threshold and exclude self
        candidates = [
            (nid, score)
            for nid, score in similar
            if nid != node_id and score >= threshold
        ]
        
        return candidates
    
    def explain_similarity(
        self,
        node_id1: str,
        node_id2: str
    ) -> Dict[str, Any]:
        """
        Explain why two nodes are similar.
        
        Args:
            node_id1: ID of first node
            node_id2: ID of second node
            
        Returns:
            Dictionary with explanation
        """
        node1 = self.knowledge_space.get_node(node_id1)
        node2 = self.knowledge_space.get_node(node_id2)
        
        if not node1 or not node2:
            return {"error": "Node not found"}
        
        explanation = {
            "nodes": [node_id1, node_id2],
            "type_match": node1.node_type == node2.node_type,
            "common_properties": [],
            "vector_similarity": None,
        }
        
        # Check common properties
        common_keys = set(node1.properties.keys()) & set(node2.properties.keys())
        for key in common_keys:
            if node1.properties[key] == node2.properties[key]:
                explanation["common_properties"].append(key)
        
        # Calculate vector similarity
        if node1.embedding is not None and node2.embedding is not None:
            norm1 = np.linalg.norm(node1.embedding)
            norm2 = np.linalg.norm(node2.embedding)
            if norm1 > 0 and norm2 > 0:
                similarity = np.dot(node1.embedding, node2.embedding) / (norm1 * norm2)
                explanation["vector_similarity"] = float(similarity)
        
        return explanation
    
    def chain_reasoning(
        self,
        start_node_id: str,
        goal_property: Dict[str, Any],
        max_depth: int = 3
    ) -> List[List[str]]:
        """
        Perform chain reasoning to find paths to nodes with goal properties.
        
        Args:
            start_node_id: ID of starting node
            goal_property: Target properties to find
            max_depth: Maximum reasoning depth
            
        Returns:
            List of paths (each path is a list of node IDs)
        """
        paths = []
        visited = set()
        
        def dfs(node_id: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            
            if node_id in visited:
                return
            
            visited.add(node_id)
            node = self.knowledge_space.get_node(node_id)
            
            if not node:
                return
            
            # Check if goal reached
            goal_reached = True
            for key, value in goal_property.items():
                if key not in node.properties or node.properties[key] != value:
                    goal_reached = False
                    break
            
            if goal_reached:
                paths.append(path + [node_id])
                return
            
            # Apply rules and get inferences
            inferences = self.apply_rules(node_id)
            
            # Continue search through neighbors
            neighbors = self.knowledge_space.get_neighbors(node_id)
            for neighbor in neighbors:
                dfs(neighbor.node_id, path + [node_id], depth + 1)
        
        dfs(start_node_id, [], 0)
        return paths
    
    def answer_query(self, query: str, context_nodes: List[str]) -> Dict[str, Any]:
        """
        Answer a query using hybrid reasoning over context nodes.
        
        Args:
            query: Natural language query
            context_nodes: List of relevant node IDs
            
        Returns:
            Dictionary with answer and supporting evidence
        """
        # Gather context
        context = []
        for node_id in context_nodes:
            node = self.knowledge_space.get_node(node_id)
            if node:
                context.append({
                    "node_id": node_id,
                    "type": node.node_type,
                    "properties": node.properties
                })
        
        # Apply reasoning rules
        inferences = []
        for node_id in context_nodes:
            node_inferences = self.apply_rules(node_id)
            inferences.extend(node_inferences)
        
        return {
            "query": query,
            "context": context,
            "inferences": inferences,
            "reasoning_type": "hybrid"
        }
