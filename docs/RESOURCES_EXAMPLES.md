# Computational Resources Examples

This directory contains example `resources.json` configurations for different computing environments.

## Laptop / Personal Computer

```json
{
  "resources": {
    "cpu_cores": 8,
    "cpu_memory_gb": 16,
    "gpu_available": false,
    "storage_gb": 500,
    "internet_access": true,
    "openmp_available": true,
    "mpi_available": false
  },
  "constraints": {
    "max_memory_per_job_gb": 12,
    "max_cpu_per_job": 6,
    "max_runtime_hours": 4,
    "prefer_parallel": false
  }
}
```

## Workstation with GPU

```json
{
  "resources": {
    "cpu_cores": 32,
    "cpu_memory_gb": 128,
    "gpu_available": true,
    "gpu_count": 2,
    "gpu_type": "RTX4090",
    "gpu_memory_gb": 24,
    "cuda_version": "12.1",
    "storage_gb": 2000,
    "internet_access": true,
    "openmp_available": true,
    "mpi_available": false
  },
  "constraints": {
    "max_memory_per_job_gb": 100,
    "max_cpu_per_job": 24,
    "max_gpu_per_job": 2,
    "max_runtime_hours": 24,
    "prefer_parallel": true
  }
}
```

## University HPC Cluster (SLURM)

```json
{
  "resources": {
    "cpu_cores": 128,
    "cpu_memory_gb": 512,
    "gpu_available": true,
    "gpu_count": 8,
    "gpu_type": "A100",
    "gpu_memory_gb": 80,
    "cuda_version": "12.2",
    "cluster_available": true,
    "cluster_type": "SLURM",
    "cluster_partition": "gpu",
    "max_nodes": 4,
    "max_walltime_hours": 168,
    "storage_gb": 50000,
    "scratch_dir": "/scratch/username",
    "network_bandwidth": "100Gbps",
    "internet_access": true,
    "mpi_available": true,
    "openmp_available": true
  },
  "constraints": {
    "max_memory_per_job_gb": 400,
    "max_cpu_per_job": 64,
    "max_gpu_per_job": 4,
    "max_runtime_hours": 72,
    "prefer_parallel": true,
    "has_quota": true,
    "quota_details": "10000 GPU-hours per month, 50TB storage quota"
  }
}
```

## National Supercomputer (PBS)

```json
{
  "resources": {
    "cpu_cores": 256,
    "cpu_memory_gb": 2048,
    "gpu_available": true,
    "gpu_count": 16,
    "gpu_type": "A100",
    "gpu_memory_gb": 80,
    "cuda_version": "12.2",
    "cluster_available": true,
    "cluster_type": "PBS",
    "cluster_partition": "gpu-large",
    "max_nodes": 16,
    "max_walltime_hours": 336,
    "storage_gb": 100000,
    "scratch_dir": "/scratch/project/username",
    "network_bandwidth": "200Gbps",
    "internet_access": false,
    "mpi_available": true,
    "openmp_available": true
  },
  "constraints": {
    "max_memory_per_job_gb": 1800,
    "max_cpu_per_job": 128,
    "max_gpu_per_job": 8,
    "max_runtime_hours": 168,
    "prefer_parallel": true,
    "has_quota": true,
    "quota_details": "100000 node-hours per allocation period"
  }
}
```

## Cloud Instance (AWS/GCP)

```json
{
  "resources": {
    "cpu_cores": 96,
    "cpu_memory_gb": 384,
    "gpu_available": true,
    "gpu_count": 8,
    "gpu_type": "V100",
    "gpu_memory_gb": 32,
    "cuda_version": "11.8",
    "storage_gb": 10000,
    "internet_access": true,
    "mpi_available": true,
    "openmp_available": true
  },
  "constraints": {
    "max_memory_per_job_gb": 300,
    "max_cpu_per_job": 64,
    "max_gpu_per_job": 8,
    "max_runtime_hours": 48,
    "prefer_parallel": true,
    "has_quota": false
  }
}
```

## Restricted Environment (Air-gapped)

```json
{
  "resources": {
    "cpu_cores": 64,
    "cpu_memory_gb": 256,
    "gpu_available": false,
    "cluster_available": true,
    "cluster_type": "SLURM",
    "cluster_partition": "secure",
    "max_nodes": 8,
    "storage_gb": 10000,
    "internet_access": false,
    "mpi_available": true,
    "openmp_available": true
  },
  "constraints": {
    "max_memory_per_job_gb": 200,
    "max_cpu_per_job": 32,
    "max_runtime_hours": 24,
    "prefer_parallel": true,
    "required_packages": ["numpy", "scipy", "pandas"],
    "forbidden_packages": ["tensorflow", "pytorch", "requests", "urllib3"]
  }
}
```

## Usage

To use an example configuration:

```bash
# Copy example to your project
cp resources_examples/hpc_cluster.json my_project/resources.json

# Or configure interactively
research-assistant resources my_project --configure

# View current configuration
research-assistant resources my_project --show
```

## Custom Configuration Fields

You can add custom constraints:

```json
{
  "resources": {
    "custom_constraints": {
      "requires_infiniband": true,
      "min_bandwidth_gbps": 100,
      "specialized_hardware": "TPU v4"
    }
  }
}
```

These will be available to agents for specialized requirements.
