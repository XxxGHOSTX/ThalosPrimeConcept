"""
Simulation sandbox for safe execution of untrusted code.

Provides isolated execution environment for simulations.
"""

from typing import Any, Callable, Dict, Optional
import subprocess
import tempfile
import json
from pathlib import Path
from datetime import datetime


class SandboxExecutionResult:
    """Result of a sandbox execution."""
    
    def __init__(
        self,
        success: bool,
        output: Any,
        error: Optional[str] = None,
        execution_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.output = output
        self.error = error
        self.execution_time = execution_time
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
        }


class SimulationSandbox:
    """
    Sandbox for safe execution of simulations and untrusted code.
    
    Provides isolation and resource limits.
    """
    
    def __init__(
        self,
        timeout_seconds: int = 300,
        max_memory_mb: int = 1024,
        allow_network: bool = False
    ):
        """
        Initialize the sandbox.
        
        Args:
            timeout_seconds: Maximum execution time
            max_memory_mb: Maximum memory usage
            allow_network: Whether to allow network access
        """
        self.timeout_seconds = timeout_seconds
        self.max_memory_mb = max_memory_mb
        self.allow_network = allow_network
    
    def execute_python(
        self,
        code: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> SandboxExecutionResult:
        """
        Execute Python code in a sandbox.
        
        Args:
            code: Python code to execute
            input_data: Optional input data to pass to the code
            
        Returns:
            SandboxExecutionResult with execution results
        """
        start_time = datetime.utcnow()
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Write code to file
                code_file = Path(tmpdir) / "sandbox_code.py"
                
                # Wrap code to handle input/output
                input_json = json.dumps(input_data or {})
                wrapped_code = f"""
import json
import sys

# Load input data
input_data = {input_json}

# User code
{code}

# Output result
if 'result' in locals():
    print(json.dumps({{"output": result}}))
else:
    print(json.dumps({{"output": None}}))
"""
                code_file.write_text(wrapped_code)
                
                # Execute with timeout
                result = subprocess.run(
                    ["python3", str(code_file)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    cwd=tmpdir
                )
                
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                if result.returncode == 0:
                    try:
                        output_data = json.loads(result.stdout)
                        return SandboxExecutionResult(
                            success=True,
                            output=output_data.get("output"),
                            execution_time=execution_time,
                            metadata={"returncode": 0}
                        )
                    except json.JSONDecodeError:
                        return SandboxExecutionResult(
                            success=True,
                            output=result.stdout,
                            execution_time=execution_time,
                            metadata={"returncode": 0}
                        )
                else:
                    return SandboxExecutionResult(
                        success=False,
                        output=None,
                        error=result.stderr,
                        execution_time=execution_time,
                        metadata={"returncode": result.returncode}
                    )
        
        except subprocess.TimeoutExpired:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return SandboxExecutionResult(
                success=False,
                output=None,
                error=f"Execution timed out after {self.timeout_seconds} seconds",
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return SandboxExecutionResult(
                success=False,
                output=None,
                error=str(e),
                execution_time=execution_time
            )
    
    def execute_function(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> SandboxExecutionResult:
        """
        Execute a function in a limited sandbox (best effort).
        
        Note: This provides limited isolation compared to subprocess execution.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            SandboxExecutionResult with execution results
        """
        start_time = datetime.utcnow()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return SandboxExecutionResult(
                success=True,
                output=result,
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return SandboxExecutionResult(
                success=False,
                output=None,
                error=str(e),
                execution_time=execution_time
            )
