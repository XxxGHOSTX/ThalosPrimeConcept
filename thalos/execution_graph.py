"""
Execution Graph (EG) - DAG of tasks with data dependencies.

Provides task orchestration with dependency resolution.
"""

from typing import Dict, List, Set, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import networkx as nx


class TaskStatus(Enum):
    """Status of a task in the execution graph."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """
    A task in the execution graph with dependencies.
    """
    task_id: str
    name: str
    function: Callable
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def execute(self, input_data: Dict[str, Any]) -> Any:
        """
        Execute the task with input data from dependencies.
        
        Args:
            input_data: Dictionary mapping dependency task IDs to their results
            
        Returns:
            Result of the task execution
        """
        self.status = TaskStatus.RUNNING
        self.start_time = datetime.utcnow()
        
        try:
            # Merge dependency results with task parameters
            merged_params = {**self.parameters, **input_data}
            result = self.function(**merged_params)
            self.result = result
            self.status = TaskStatus.COMPLETED
            self.end_time = datetime.utcnow()
            return result
        except Exception as e:
            self.error = str(e)
            self.status = TaskStatus.FAILED
            self.end_time = datetime.utcnow()
            raise


class ExecutionGraph:
    """
    A DAG of tasks with data dependencies, executed by an orchestrator.
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.tasks: Dict[str, Task] = {}
        self.execution_order: Optional[List[str]] = None
        
    def add_task(self, task: Task) -> None:
        """
        Add a task to the execution graph.
        
        Args:
            task: Task to add
        """
        self.tasks[task.task_id] = task
        self.graph.add_node(task.task_id, task=task)
        
        # Add edges for dependencies
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                raise ValueError(f"Dependency {dep_id} not found for task {task.task_id}")
            self.graph.add_edge(dep_id, task.task_id)
        
        # Invalidate cached execution order
        self.execution_order = None
    
    def validate(self) -> bool:
        """
        Validate that the graph is a valid DAG (no cycles).
        
        Returns:
            True if valid, False otherwise
        """
        return nx.is_directed_acyclic_graph(self.graph)
    
    def get_execution_order(self) -> List[str]:
        """
        Get the topological order for task execution.
        
        Returns:
            List of task IDs in execution order
        """
        if self.execution_order is None:
            if not self.validate():
                raise ValueError("Execution graph contains cycles")
            self.execution_order = list(nx.topological_sort(self.graph))
        return self.execution_order
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute all tasks in the graph in dependency order.
        
        Returns:
            Dictionary mapping task IDs to their results
        """
        execution_order = self.get_execution_order()
        results = {}
        
        for task_id in execution_order:
            task = self.tasks[task_id]
            
            # Gather results from dependencies
            dep_results = {
                dep_id: results[dep_id]
                for dep_id in task.dependencies
                if dep_id in results
            }
            
            # Execute the task
            try:
                result = task.execute(dep_results)
                results[task_id] = result
            except Exception as e:
                # Task failed, mark dependent tasks as skipped
                for dependent_id in nx.descendants(self.graph, task_id):
                    self.tasks[dependent_id].status = TaskStatus.SKIPPED
                raise
        
        return results
    
    def get_task_status(self, task_id: str) -> TaskStatus:
        """Get the status of a task."""
        return self.tasks[task_id].status
    
    def visualize(self) -> str:
        """
        Generate a text-based visualization of the graph.
        
        Returns:
            String representation of the graph
        """
        lines = ["Execution Graph:"]
        execution_order = self.get_execution_order()
        
        for task_id in execution_order:
            task = self.tasks[task_id]
            deps = ", ".join(task.dependencies) if task.dependencies else "none"
            status = task.status.value
            lines.append(f"  {task_id} [{status}] - deps: {deps}")
        
        return "\n".join(lines)

    def generate_branch_applications(
        self,
        max_paths: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate deployment-ready application specs for each root-to-leaf branch.
        
        Branch IDs are 1-based to keep identifiers human-friendly and aligned with
        textual run reports.
        
        Args:
            max_paths: Optional cap on the number of branch applications to generate.
                When set, a ValueError is raised if the graph contains more paths.
        
        Returns:
            List of dictionaries describing each branch application with task order
        """
        if not self.tasks:
            return []
        
        if not self.validate():
            raise ValueError(
                "Cannot generate branch applications: execution graph contains cycles or is invalid"
            )
        
        sources = [
            node for node in self.graph.nodes
            if self.graph.in_degree(node) == 0
        ]
        sinks = [
            node for node in self.graph.nodes
            if self.graph.out_degree(node) == 0
        ]
        
        applications: List[Dict[str, Any]] = []
        next_branch_id = 1  # human-friendly branch numbering for readability
        path_count = 0
        
        for source in sources:
            for sink in sinks:
                paths_iter = nx.all_simple_paths(self.graph, source, sink)
                limit_error = (
                    f"Graph contains more than {max_paths} paths; limit exceeded."
                    if max_paths is not None else None
                )
                
                for path in paths_iter:
                    if max_paths is not None and path_count >= max_paths:
                        raise ValueError(limit_error)
                    path_count += 1
                    applications.append({
                        "branch_id": f"branch_{next_branch_id}",
                        "tasks": path,
                        "deployment_sequence": [
                            {
                                "task_id": task_id,
                                "name": self.tasks[task_id].name,
                                "status": self.tasks[task_id].status.value,
                                "dependencies": self.tasks[task_id].dependencies,
                            }
                            for task_id in path
                        ]
                    })
                    next_branch_id += 1
        
        return applications
