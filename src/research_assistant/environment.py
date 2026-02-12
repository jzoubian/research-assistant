"""Environment management for reproducible code execution."""

import os
import subprocess
from pathlib import Path
from typing import Optional
import json


class EnvironmentManager:
    """Manage isolated execution environments for reproducible analysis."""

    def __init__(self, project_dir: Path, env_type: str = "pixi"):
        """Initialize environment manager.

        Args:
            project_dir: Path to project directory
            env_type: Type of environment manager (pixi, apptainer, nix, guix)
        """
        self.project_dir = project_dir
        self.env_type = env_type
        self.env_dir = project_dir / ".env"

    def initialize_environment(self, python_version: str = "3.10") -> bool:
        """Initialize the execution environment.

        Args:
            python_version: Python version to use

        Returns:
            True if successful
        """
        if self.env_type == "pixi":
            return self._initialize_pixi(python_version)
        elif self.env_type == "apptainer":
            return self._initialize_apptainer(python_version)
        elif self.env_type == "nix":
            return self._initialize_nix(python_version)
        elif self.env_type == "guix":
            return self._initialize_guix(python_version)
        else:
            raise ValueError(f"Unsupported environment type: {self.env_type}")

    def _initialize_pixi(self, python_version: str) -> bool:
        """Initialize pixi environment."""
        # Create pixi.toml if it doesn't exist
        pixi_file = self.project_dir / "pixi.toml"
        if not pixi_file.exists():
            pixi_config = f"""[project]
name = "research-analysis"
version = "0.1.0"
description = "Research analysis environment"
channels = ["conda-forge"]
platforms = ["linux-64", "osx-64", "osx-arm64"]

[dependencies]
python = "{python_version}.*"
numpy = "*"
scipy = "*"
pandas = "*"
matplotlib = "*"
seaborn = "*"
jupyterlab = "*"

[tasks]
run = "python"
"""
            pixi_file.write_text(pixi_config)

        # Initialize pixi
        try:
            subprocess.run(
                ["pixi", "install"],
                cwd=self.project_dir,
                check=True,
                capture_output=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Failed to initialize pixi: {e}")
            return False

    def _initialize_conda(self, python_version: str) -> bool:
        """Initialize conda environment - DEPRECATED: Use pixi instead."""
        env_name = f"research-{self.project_dir.name}"

        # Create environment.yml if it doesn't exist
        env_file = self.project_dir / "environment.yml"
        if not env_file.exists():
            env_config = f"""name: {env_name}
channels:
  - conda-forge
  - defaults
dependencies:
  - python={python_version}
  - numpy
  - scipy
  - pandas
  - matplotlib
  - seaborn
  - jupyterlab
"""
            env_file.write_text(env_config)

        # Create conda environment
        try:
            subprocess.run(
                ["conda", "env", "create", "-f", str(env_file), "--force"],
                check=True,
                capture_output=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Failed to initialize conda: {e}")
            return False

    def _initialize_apptainer(self, python_version: str) -> bool:
        """Initialize Apptainer (Singularity) container for HPC environments."""
        # Create apptainer.def if it doesn't exist
        def_file = self.project_dir / "apptainer.def"
        if not def_file.exists():
            def_content = f"""Bootstrap: docker
From: python:{python_version}-slim

%post
    # Install system dependencies
    apt-get update && apt-get install -y \\
        build-essential \\
        gfortran \\
        libopenblas-dev \\
        liblapack-dev \\
        && rm -rf /var/lib/apt/lists/*
    
    # Install Python scientific stack
    pip install --no-cache-dir \\
        numpy>=1.24.0 \\
        scipy>=1.10.0 \\
        pandas>=2.0.0 \\
        matplotlib>=3.7.0 \\
        seaborn>=0.12.0 \\
        scikit-learn>=1.3.0 \\
        astropy>=5.3.0 \\
        h5py>=3.9.0 \\
        jupyterlab>=4.0.0

%environment
    export LC_ALL=C
    export PATH=/usr/local/bin:$PATH

%runscript
    exec python "$@"
"""
            def_file.write_text(def_content)

        # Build container
        try:
            sif_file = self.project_dir / "research_env.sif"
            subprocess.run(
                ["apptainer", "build", "--fakeroot", str(sif_file), str(def_file)],
                check=True,
                capture_output=True,
                cwd=str(self.project_dir)
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Failed to initialize apptainer: {e}")
            return False

    def _initialize_nix(self, python_version: str) -> bool:
        """Initialize Nix environment for declarative reproducible builds."""
        # Create default.nix if it doesn't exist
        nix_file = self.project_dir / "default.nix"
        if not nix_file.exists():
            py_ver = python_version.replace('.', '')
            nix_content = f"""{{ pkgs ? import <nixpkgs> {{}} }}:

pkgs.mkShell {{
  buildInputs = with pkgs; [
    python{py_ver}
    python{py_ver}Packages.numpy
    python{py_ver}Packages.scipy
    python{py_ver}Packages.pandas
    python{py_ver}Packages.matplotlib
    python{py_ver}Packages.seaborn
    python{py_ver}Packages.scikit-learn
    python{py_ver}Packages.jupyterlab
    python{py_ver}Packages.h5py
    
    # Scientific libraries
    openblas
    lapack
    gfortran
  ];
  
  shellHook = ''
    echo "Nix scientific computing environment ready"
    export PYTHONPATH=$PYTHONPATH:$(pwd)
  '';
}}
"""
            nix_file.write_text(nix_content)

        # Verify nix is available
        try:
            subprocess.run(
                ["nix-shell", "--version"],
                check=True,
                capture_output=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Failed to initialize nix (is nix installed?): {e}")
            return False

    def _initialize_guix(self, python_version: str) -> bool:
        """Initialize GNU Guix environment for functional package management."""
        # Create guix.scm if it doesn't exist
        guix_file = self.project_dir / "guix.scm"
        if not guix_file.exists():
            guix_content = """(use-modules (guix packages)
             (guix build-system python)
             (gnu packages python)
             (gnu packages python-xyz)
             (gnu packages python-science)
             (gnu packages maths)
             (gnu packages gcc))

(specifications->manifest
 '("python"
   "python-numpy"
   "python-scipy"
   "python-pandas"
   "python-matplotlib"
   "python-seaborn"
   "python-scikit-learn"
   "python-jupyterlab"
   "python-h5py"
   "openblas"
   "lapack"
   "gfortran-toolchain"))
"""
            guix_file.write_text(guix_content)

        # Verify guix is available
        try:
            subprocess.run(
                ["guix", "--version"],
                check=True,
                capture_output=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Failed to initialize guix (is guix installed?): {e}")
            return False

    def execute_code(self, code: str, timeout: int = 300) -> tuple[bool, str, str]:
        """Execute code in the isolated environment.

        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds

        Returns:
            Tuple of (success, stdout, stderr)
        """
        if self.env_type == "pixi":
            return self._execute_pixi(code, timeout)
        elif self.env_type == "apptainer":
            return self._execute_apptainer(code, timeout)
        elif self.env_type == "nix":
            return self._execute_nix(code, timeout)
        elif self.env_type == "guix":
            return self._execute_guix(code, timeout)
        elif self.env_type == "conda":
            return self._execute_conda(code, timeout)
        else:
            raise ValueError(f"Unsupported environment type: {self.env_type}")

    def _execute_pixi(self, code: str, timeout: int) -> tuple[bool, str, str]:
        """Execute code using pixi."""
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir=self.project_dir
        ) as f:
            f.write(code)
            temp_file = f.name

        try:
            result = subprocess.run(
                ["pixi", "run", "python", temp_file],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            os.unlink(temp_file)
            return (result.returncode == 0, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            os.unlink(temp_file)
            return (False, "", f"Execution timed out after {timeout} seconds")
        except Exception as e:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            return (False, "", str(e))

    def _execute_conda(self, code: str, timeout: int) -> tuple[bool, str, str]:
        """Execute code using conda."""
        import tempfile

        env_name = f"research-{self.project_dir.name}"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir=self.project_dir
        ) as f:
            f.write(code)
            temp_file = f.name

        try:
            result = subprocess.run(
                ["conda", "run", "-n", env_name, "python", temp_file],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            os.unlink(temp_file)
            return (result.returncode == 0, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            os.unlink(temp_file)
            return (False, "", f"Execution timed out after {timeout} seconds")
        except Exception as e:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            return (False, "", str(e))

    def _execute_apptainer(self, code: str, timeout: int) -> tuple[bool, str, str]:
        """Execute code using Apptainer container."""
        import tempfile

        sif_file = self.project_dir / "research_env.sif"
        if not sif_file.exists():
            return (False, "", "Apptainer container not built. Run initialize_environment first.")

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir=self.project_dir
        ) as f:
            f.write(code)
            temp_file = f.name

        try:
            result = subprocess.run(
                ["apptainer", "exec", "--bind", f"{self.project_dir}:/workspace", 
                 str(sif_file), "python", temp_file],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            os.unlink(temp_file)
            return (result.returncode == 0, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            os.unlink(temp_file)
            return (False, "", f"Execution timed out after {timeout} seconds")
        except Exception as e:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            return (False, "", str(e))

    def _execute_nix(self, code: str, timeout: int) -> tuple[bool, str, str]:
        """Execute code using Nix shell."""
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir=self.project_dir
        ) as f:
            f.write(code)
            temp_file = f.name

        try:
            result = subprocess.run(
                ["nix-shell", "--run", f"python {temp_file}"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=True,
            )
            os.unlink(temp_file)
            return (result.returncode == 0, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            os.unlink(temp_file)
            return (False, "", f"Execution timed out after {timeout} seconds")
        except Exception as e:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            return (False, "", str(e))

    def _execute_guix(self, code: str, timeout: int) -> tuple[bool, str, str]:
        """Execute code using GNU Guix environment."""
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir=self.project_dir
        ) as f:
            f.write(code)
            temp_file = f.name

        try:
            result = subprocess.run(
                ["guix", "shell", "-m", "guix.scm", "--", "python", temp_file],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            os.unlink(temp_file)
            return (result.returncode == 0, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            os.unlink(temp_file)
            return (False, "", f"Execution timed out after {timeout} seconds")
        except Exception as e:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            return (False, "", str(e))

    def _execute_venv(self, code: str, timeout: int) -> tuple[bool, str, str]:
        """Execute code using venv - DEPRECATED."""
        import tempfile

        python_path = self.env_dir / "bin" / "python"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir=self.project_dir
        ) as f:
            f.write(code)
            temp_file = f.name

        try:
            result = subprocess.run(
                [str(python_path), temp_file],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            os.unlink(temp_file)
            return (result.returncode == 0, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            os.unlink(temp_file)
            return (False, "", f"Execution timed out after {timeout} seconds")
        except Exception as e:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            return (False, "", str(e))

    def _execute_docker(self, code: str, timeout: int) -> tuple[bool, str, str]:
        """Execute code using docker - DEPRECATED."""
        import tempfile

        image_name = f"research-{self.project_dir.name}"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir=self.project_dir
        ) as f:
            f.write(code)
            temp_file = Path(f.name).name  # Get just the filename

        try:
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{self.project_dir}:/workspace",
                    image_name,
                    "python",
                    f"/workspace/{temp_file}",
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            os.unlink(self.project_dir / temp_file)
            return (result.returncode == 0, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            os.unlink(self.project_dir / temp_file)
            return (False, "", f"Execution timed out after {timeout} seconds")
        except Exception as e:
            temp_path = self.project_dir / temp_file
            if temp_path.exists():
                os.unlink(temp_path)
            return (False, "", str(e))

    def install_package(self, package: str) -> bool:
        """Install a package in the environment.

        Args:
            package: Package name (can include version spec, e.g., "numpy>=1.24")

        Returns:
            True if successful
        """
        if self.env_type == "pixi":
            try:
                subprocess.run(
                    ["pixi", "add", package],
                    cwd=self.project_dir,
                    check=True,
                    capture_output=True,
                )
                return True
            except subprocess.CalledProcessError:
                return False
        elif self.env_type == "apptainer":
            # For apptainer, need to rebuild container with new package
            print(f"Note: Adding {package} to apptainer.def. Rebuild container with initialize_environment().")
            def_file = self.project_dir / "apptainer.def"
            if def_file.exists():
                content = def_file.read_text()
                # Add package to pip install line
                content = content.replace("jupyterlab>=4.0.0", f"jupyterlab>=4.0.0 \\\n        {package}")
                def_file.write_text(content)
            return True
        elif self.env_type == "nix":
            print(f"Note: For nix, manually add {package} to default.nix buildInputs")
            return True
        elif self.env_type == "guix":
            print(f"Note: For guix, manually add {package} to guix.scm specifications")
            return True
        elif self.env_type == "conda":
            env_name = f"research-{self.project_dir.name}"
            try:
                subprocess.run(
                    ["conda", "install", "-n", env_name, "-y", package],
                    check=True,
                    capture_output=True,
                )
                return True
            except subprocess.CalledProcessError:
                return False
        return False

    def get_environment_info(self) -> dict:
        """Get information about the current environment.

        Returns:
            Dictionary with environment details
        """
        info = {
            "type": self.env_type,
            "project_dir": str(self.project_dir),
        }
        
        # Add type-specific info
        if self.env_type == "pixi":
            pixi_file = self.project_dir / "pixi.toml"
            if pixi_file.exists():
                info["config_file"] = str(pixi_file)
        elif self.env_type == "apptainer":
            def_file = self.project_dir / "apptainer.def"
            sif_file = self.project_dir / "research_env.sif"
            if def_file.exists():
                info["definition_file"] = str(def_file)
            if sif_file.exists():
                info["container_file"] = str(sif_file)
        elif self.env_type == "nix":
            nix_file = self.project_dir / "default.nix"
            if nix_file.exists():
                info["config_file"] = str(nix_file)
        elif self.env_type == "guix":
            guix_file = self.project_dir / "guix.scm"
            if guix_file.exists():
                info["config_file"] = str(guix_file)
        
        return info
