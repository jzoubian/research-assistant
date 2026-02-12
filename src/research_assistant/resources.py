"""Resource management for computational constraints."""

from typing import Optional, List, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field
import json


class ComputeResource(BaseModel):
    """Specification of available computational resources."""
    
    # CPU resources
    cpu_cores: Optional[int] = Field(None, description="Number of CPU cores available")
    cpu_memory_gb: Optional[float] = Field(None, description="RAM available in GB")
    
    # GPU resources
    gpu_available: bool = Field(False, description="Whether GPU is available")
    gpu_count: Optional[int] = Field(None, description="Number of GPUs")
    gpu_type: Optional[str] = Field(None, description="GPU model (e.g., 'A100', 'V100', 'RTX4090')")
    gpu_memory_gb: Optional[float] = Field(None, description="GPU memory per device in GB")
    cuda_version: Optional[str] = Field(None, description="CUDA version if applicable")
    
    # Cluster resources
    cluster_available: bool = Field(False, description="Whether cluster/HPC access is available")
    cluster_type: Optional[str] = Field(None, description="Cluster type (e.g., 'SLURM', 'PBS', 'SGE')")
    cluster_partition: Optional[str] = Field(None, description="Default partition/queue to use")
    max_nodes: Optional[int] = Field(None, description="Maximum nodes available")
    max_walltime_hours: Optional[float] = Field(None, description="Maximum walltime in hours")
    
    # Storage resources
    storage_gb: Optional[float] = Field(None, description="Available storage in GB")
    scratch_dir: Optional[Path] = Field(None, description="Path to scratch/temporary storage")
    
    # Network/bandwidth
    network_bandwidth: Optional[str] = Field(None, description="Network bandwidth (e.g., '10Gbps', '100Mbps')")
    internet_access: bool = Field(True, description="Whether internet access is available")
    
    # Software constraints
    mpi_available: bool = Field(False, description="Whether MPI is available")
    openmp_available: bool = Field(True, description="Whether OpenMP is available")
    
    # Custom constraints
    custom_constraints: Dict[str, Any] = Field(default_factory=dict, description="Additional custom constraints")


class ResourceConstraints(BaseModel):
    """Constraints that must be respected during computation."""
    
    # Hard limits
    max_memory_per_job_gb: Optional[float] = Field(None, description="Maximum memory per job")
    max_cpu_per_job: Optional[int] = Field(None, description="Maximum CPUs per job")
    max_gpu_per_job: Optional[int] = Field(None, description="Maximum GPUs per job")
    max_runtime_hours: Optional[float] = Field(None, description="Maximum runtime per job")
    
    # Soft preferences
    prefer_cpu: bool = Field(False, description="Prefer CPU over GPU when both available")
    prefer_parallel: bool = Field(True, description="Prefer parallel execution when possible")
    
    # Budget/quota
    has_quota: bool = Field(False, description="Whether resource quota exists")
    quota_details: Optional[str] = Field(None, description="Description of quota limits")
    
    # Environment preferences
    preferred_env: Optional[str] = Field(None, description="Preferred environment manager")
    required_packages: List[str] = Field(default_factory=list, description="Required packages")
    forbidden_packages: List[str] = Field(default_factory=list, description="Packages that cannot be used")


class ResourceManager:
    """Manage computational resources and constraints."""
    
    def __init__(self, project_dir: Path):
        """Initialize resource manager.
        
        Args:
            project_dir: Path to project directory
        """
        self.project_dir = project_dir
        self.resources_file = project_dir / "resources.json"
        self.resources: Optional[ComputeResource] = None
        self.constraints: Optional[ResourceConstraints] = None
        
    def load_resources(self) -> bool:
        """Load resource specification from file.
        
        Returns:
            True if loaded successfully
        """
        if not self.resources_file.exists():
            return False
            
        try:
            with open(self.resources_file, 'r') as f:
                data = json.load(f)
            
            self.resources = ComputeResource(**data.get('resources', {}))
            self.constraints = ResourceConstraints(**data.get('constraints', {}))
            return True
        except Exception as e:
            print(f"Failed to load resources: {e}")
            return False
    
    def save_resources(self) -> bool:
        """Save resource specification to file.
        
        Returns:
            True if saved successfully
        """
        if not self.resources or not self.constraints:
            return False
            
        try:
            data = {
                'resources': self.resources.model_dump(exclude_none=True),
                'constraints': self.constraints.model_dump(exclude_none=True)
            }
            
            with open(self.resources_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Failed to save resources: {e}")
            return False
    
    def create_default_resources(self) -> None:
        """Create default resource specification."""
        import os
        import psutil
        
        # Try to detect system resources
        cpu_count = os.cpu_count() or 4
        memory_gb = psutil.virtual_memory().total / (1024**3) if psutil else 8.0
        
        self.resources = ComputeResource(
            cpu_cores=cpu_count,
            cpu_memory_gb=round(memory_gb, 1),
            gpu_available=False,
            cluster_available=False,
            internet_access=True,
            openmp_available=True,
            mpi_available=False,
        )
        
        self.constraints = ResourceConstraints(
            max_memory_per_job_gb=memory_gb * 0.8,  # Use up to 80% of RAM
            max_cpu_per_job=cpu_count,
            prefer_parallel=True,
        )
    
    def get_execution_config(self, env_type: str) -> Dict[str, Any]:
        """Get execution configuration based on resources and environment.
        
        Args:
            env_type: Environment manager type
            
        Returns:
            Dictionary with execution parameters
        """
        if not self.resources or not self.constraints:
            return {}
        
        config = {
            'env_type': env_type,
        }
        
        # Add CPU configuration
        if self.resources.cpu_cores:
            max_cpu = min(
                self.resources.cpu_cores,
                self.constraints.max_cpu_per_job or self.resources.cpu_cores
            )
            config['num_threads'] = max_cpu
            config['OMP_NUM_THREADS'] = str(max_cpu)
        
        # Add GPU configuration
        if self.resources.gpu_available and not self.constraints.prefer_cpu:
            config['use_gpu'] = True
            if self.resources.gpu_count:
                max_gpu = min(
                    self.resources.gpu_count,
                    self.constraints.max_gpu_per_job or self.resources.gpu_count
                )
                config['num_gpus'] = max_gpu
                config['CUDA_VISIBLE_DEVICES'] = ','.join(str(i) for i in range(max_gpu))
        else:
            config['use_gpu'] = False
            config['CUDA_VISIBLE_DEVICES'] = ''
        
        # Add memory limits
        if self.constraints.max_memory_per_job_gb:
            config['max_memory_gb'] = self.constraints.max_memory_per_job_gb
        
        # Add runtime limits
        if self.constraints.max_runtime_hours:
            config['max_runtime_seconds'] = int(self.constraints.max_runtime_hours * 3600)
        
        # Add cluster configuration
        if self.resources.cluster_available:
            config['cluster_type'] = self.resources.cluster_type
            config['cluster_partition'] = self.resources.cluster_partition
            if self.resources.max_walltime_hours:
                config['max_walltime_hours'] = self.resources.max_walltime_hours
        
        # Add scratch directory
        if self.resources.scratch_dir:
            config['scratch_dir'] = str(self.resources.scratch_dir)
        
        return config
    
    def validate_requirements(self, requirements: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate if requirements can be met with available resources.
        
        Args:
            requirements: Dictionary of required resources
            
        Returns:
            Tuple of (can_meet_requirements, list_of_issues)
        """
        if not self.resources:
            return False, ["No resource specification loaded"]
        
        issues = []
        
        # Check CPU requirements
        if 'min_cpu_cores' in requirements:
            if not self.resources.cpu_cores or self.resources.cpu_cores < requirements['min_cpu_cores']:
                issues.append(f"Requires {requirements['min_cpu_cores']} CPU cores, only {self.resources.cpu_cores} available")
        
        # Check memory requirements
        if 'min_memory_gb' in requirements:
            if not self.resources.cpu_memory_gb or self.resources.cpu_memory_gb < requirements['min_memory_gb']:
                issues.append(f"Requires {requirements['min_memory_gb']} GB RAM, only {self.resources.cpu_memory_gb} GB available")
        
        # Check GPU requirements
        if requirements.get('requires_gpu', False):
            if not self.resources.gpu_available:
                issues.append("GPU required but not available")
            elif 'min_gpu_memory_gb' in requirements:
                if not self.resources.gpu_memory_gb or self.resources.gpu_memory_gb < requirements['min_gpu_memory_gb']:
                    issues.append(f"Requires {requirements['min_gpu_memory_gb']} GB GPU memory, only {self.resources.gpu_memory_gb} GB available")
        
        # Check cluster requirements
        if requirements.get('requires_cluster', False) and not self.resources.cluster_available:
            issues.append("Cluster access required but not available")
        
        # Check MPI requirements
        if requirements.get('requires_mpi', False) and not self.resources.mpi_available:
            issues.append("MPI required but not available")
        
        # Check internet requirements
        if requirements.get('requires_internet', False) and not self.resources.internet_access:
            issues.append("Internet access required but not available")
        
        # Check package conflicts
        if self.constraints:
            required_pkgs = requirements.get('required_packages', [])
            forbidden = [pkg for pkg in required_pkgs if pkg in self.constraints.forbidden_packages]
            if forbidden:
                issues.append(f"Required packages are forbidden: {', '.join(forbidden)}")
        
        return len(issues) == 0, issues
    
    def get_resource_summary(self) -> str:
        """Get human-readable summary of resources.
        
        Returns:
            Formatted string with resource summary
        """
        if not self.resources:
            return "No resources configured"
        
        lines = ["Available Computational Resources:", ""]
        
        # CPU
        lines.append(f"CPU: {self.resources.cpu_cores} cores, {self.resources.cpu_memory_gb} GB RAM")
        
        # GPU
        if self.resources.gpu_available:
            gpu_info = f"GPU: {self.resources.gpu_count}x {self.resources.gpu_type or 'Unknown'}"
            if self.resources.gpu_memory_gb:
                gpu_info += f" ({self.resources.gpu_memory_gb} GB each)"
            lines.append(gpu_info)
        else:
            lines.append("GPU: Not available")
        
        # Cluster
        if self.resources.cluster_available:
            cluster_info = f"Cluster: {self.resources.cluster_type or 'Available'}"
            if self.resources.max_nodes:
                cluster_info += f" (up to {self.resources.max_nodes} nodes)"
            lines.append(cluster_info)
        
        # Storage
        if self.resources.storage_gb:
            lines.append(f"Storage: {self.resources.storage_gb} GB")
        
        # Constraints
        if self.constraints:
            lines.append("")
            lines.append("Constraints:")
            if self.constraints.max_memory_per_job_gb:
                lines.append(f"  Max memory per job: {self.constraints.max_memory_per_job_gb} GB")
            if self.constraints.max_cpu_per_job:
                lines.append(f"  Max CPUs per job: {self.constraints.max_cpu_per_job}")
            if self.constraints.max_runtime_hours:
                lines.append(f"  Max runtime: {self.constraints.max_runtime_hours} hours")
            if self.constraints.has_quota:
                lines.append(f"  Quota: {self.constraints.quota_details or 'Limited'}")
        
        return "\n".join(lines)
    
    def generate_cluster_script(self, job_name: str, command: str) -> str:
        """Generate cluster submission script based on resources.
        
        Args:
            job_name: Name of the job
            command: Command to execute
            
        Returns:
            Cluster script content
        """
        if not self.resources or not self.resources.cluster_available:
            return ""
        
        cluster_type = self.resources.cluster_type or "SLURM"
        
        if cluster_type.upper() == "SLURM":
            script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output={job_name}_%j.out
#SBATCH --error={job_name}_%j.err
"""
            if self.resources.cluster_partition:
                script += f"#SBATCH --partition={self.resources.cluster_partition}\n"
            if self.constraints and self.constraints.max_cpu_per_job:
                script += f"#SBATCH --ntasks={self.constraints.max_cpu_per_job}\n"
            if self.constraints and self.constraints.max_memory_per_job_gb:
                script += f"#SBATCH --mem={int(self.constraints.max_memory_per_job_gb)}G\n"
            if self.constraints and self.constraints.max_runtime_hours:
                hours = int(self.constraints.max_runtime_hours)
                minutes = int((self.constraints.max_runtime_hours - hours) * 60)
                script += f"#SBATCH --time={hours:02d}:{minutes:02d}:00\n"
            if self.resources.gpu_available and self.constraints and self.constraints.max_gpu_per_job:
                script += f"#SBATCH --gres=gpu:{self.constraints.max_gpu_per_job}\n"
            
            script += f"\n{command}\n"
            return script
        
        elif cluster_type.upper() == "PBS":
            script = f"""#!/bin/bash
#PBS -N {job_name}
#PBS -o {job_name}.out
#PBS -e {job_name}.err
"""
            if self.resources.cluster_partition:
                script += f"#PBS -q {self.resources.cluster_partition}\n"
            if self.constraints and self.constraints.max_cpu_per_job:
                script += f"#PBS -l nodes=1:ppn={self.constraints.max_cpu_per_job}\n"
            if self.constraints and self.constraints.max_memory_per_job_gb:
                script += f"#PBS -l mem={int(self.constraints.max_memory_per_job_gb)}gb\n"
            if self.constraints and self.constraints.max_runtime_hours:
                hours = int(self.constraints.max_runtime_hours)
                minutes = int((self.constraints.max_runtime_hours - hours) * 60)
                script += f"#PBS -l walltime={hours:02d}:{minutes:02d}:00\n"
            
            script += f"\ncd $PBS_O_WORKDIR\n{command}\n"
            return script
        
        return ""
