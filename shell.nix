{ pkgs ? import <nixpkgs> {} }:

let
  fhs = pkgs.buildFHSEnv {
    name = "research-assistant-env";
    
    targetPkgs = pkgs: with pkgs; [
    # Python environment
    python311
    python311Packages.pip
    python311Packages.virtualenv
    
    # Node.js (required for Copilot CLI agent)
    nodejs_22
    
    # Build tools
    gcc
    gnumake
    cmake
    pkg-config
    
    # System libraries
    stdenv.cc.cc.lib
    zlib
    libffi
    openssl
    readline
    sqlite
    bzip2
    xz
    ncurses
    
    # Git for version control
    git
    
    # GitHub CLI (for Copilot SDK authentication)
    gh
    
    # Pixi package manager
    pixi
    
    # Additional utilities
    which
    curl
    wget
    
    # Text processing (for PDF handling)
    poppler-utils  # pdftotext
  ];
  
  multiPkgs = pkgs: with pkgs; [
    # Additional 32-bit libraries if needed
  ];
  
  profile = ''
    # Set up Python environment
    export PIP_PREFIX="$HOME/.local"
    export PYTHONPATH="$HOME/.local/lib/python3.11/site-packages:$PYTHONPATH"
    export PATH="$HOME/.local/bin:$PATH"
    
    # Set up Node.js/npm environment (for Copilot CLI)
    export NPM_CONFIG_PREFIX="$HOME/.npm-global"
    export PATH="$HOME/.npm-global/bin:$PATH"
    
    # Set up locale
    export LOCALE_ARCHIVE="${pkgs.glibcLocales}/lib/locale/locale-archive"
    export LC_ALL=en_US.UTF-8
    
    # Set up SSL certificates
    export SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
    export REQUESTS_CA_BUNDLE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
    
    # Set up compiler flags
    export NIX_CFLAGS_COMPILE="-I${pkgs.zlib.dev}/include -I${pkgs.openssl.dev}/include"
    export NIX_LDFLAGS="-L${pkgs.zlib}/lib -L${pkgs.openssl.out}/lib"
    
    # Install research-assistant if not already installed
    if ! command -v research-assistant &> /dev/null; then
      # Try to find pyproject.toml in current directory or parent
      if [ -f "$PWD/pyproject.toml" ]; then
        echo "Installing research-assistant from $PWD..."
        # Install GitHub Copilot SDK first
        echo "Installing github-copilot-sdk..."
        pip install github-copilot-sdk
        pip install -I -e "$PWD"
      elif [ -f "$(dirname "$PWD")/pyproject.toml" ]; then
        RESEARCH_ASSISTANT_DIR="$(dirname "$PWD")"
        echo "Installing research-assistant from $RESEARCH_ASSISTANT_DIR..."
        # Install GitHub Copilot SDK first
        echo "Installing github-copilot-sdk..."
        pip install github-copilot-sdk
        pip install -I -e "$RESEARCH_ASSISTANT_DIR"
      else
        echo "Warning: pyproject.toml not found. Install manually with:"
        echo "  pip install github-copilot-sdk"
        echo "  cd /path/to/research-assistant && pip install -I -e ."
      fi
    fi
    
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║         Research Assistant Development Environment            ║"
    echo "║              Built on GitHub Copilot SDK                       ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Available tools:"
    echo "  • Python $(python --version | cut -d' ' -f2)"
    echo "  • Pixi $(pixi --version | cut -d' ' -f2)"
    echo "  • Research Assistant CLI: research-assistant --help"
    echo ""
    echo "Quick start:"
    echo "  research-assistant init my_project --env-manager pixi"
    echo "  research-assistant run my_project --interactive"
    echo ""
    echo "GitHub Copilot SDK Configuration:"
    echo "  - Authenticate with: gh auth login"
    echo "  - Requires active GitHub Copilot subscription"
    echo ""
  '';
  
  runScript = "bash";
  };
in fhs.env
