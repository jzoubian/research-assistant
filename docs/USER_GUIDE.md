# Research Assistant User Guide

This guide walks through a complete end-to-end example using the Research Assistant, demonstrating all features through a practical data analysis project.

## Table of Contents

1. [Example Project: Iris Species Classification](#example-project-iris-species-classification)
2. [Prerequisites](#prerequisites)
3. [Dataset Setup](#dataset-setup)
4. [End-to-End Walkthrough](#end-to-end-walkthrough)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)

---

## Example Project: Iris Species Classification

We'll analyze the classic **Iris flower dataset** to explore species classification based on morphological measurements. This dataset is:

- **Small**: Only 150 samples, 5 columns
- **Built-in**: Available in scikit-learn, no download needed
- **Simple**: Clear features and well-defined classification problem
- **Laptop-friendly**: Runs in seconds on any machine

**Research Question**: Can we develop a robust classification model to distinguish Iris species based on petal and sepal measurements, and identify which morphological features are most discriminative?

---

## Prerequisites

### 1. Install Research Assistant

```bash
cd research-assistant
pip install -e .
```

### 2. Install Required Dependencies

The assistant will manage most dependencies through environment managers, but you need one of:

```bash
# Option A: pixi (recommended for scientific computing)
curl -fsSL https://pixi.sh/install.sh | bash

# Option B: conda (alternative)
# Already installed with Anaconda/Miniconda

# Option C: standard Python venv
# No additional installation needed
```

### 3. Configure GitHub Copilot SDK

The assistant is built on the [GitHub Copilot SDK](https://github.com/copilot-extensions/copilot-sdk) and uses multi-agent orchestration for research tasks.

**Authenticate with GitHub Copilot:**

```bash
# Authenticate with GitHub
gh auth login

# The Copilot SDK will automatically use your GitHub Copilot subscription
```

The Copilot SDK enables:
- Multi-agent orchestration with specialized roles
- Tool use and function calling
- Streaming responses for long-running tasks
- Automatic error handling and retries

**Requirements:**
- Active GitHub Copilot subscription (Individual, Business, or Enterprise)
- GitHub CLI (`gh`) installed and authenticated

---

## Dataset Setup

### Quick Start: Built-in Iris Dataset

The Iris dataset is included with scikit-learn, so no manual download is needed. We'll configure the assistant to load it automatically.

### Verify Dataset Availability

First, install scikit-learn (it's not included by default):

```bash
pip install scikit-learn
```

Then verify the dataset is accessible:

```bash
python -c "from sklearn.datasets import load_iris; print('Iris dataset ready to use')"
```

The assistant will also install scikit-learn automatically when it generates analysis code that requires it.

---

## End-to-End Walkthrough

### Step 1: Initialize Project

Create a new research project:

```bash
research-assistant init iris_classification --env-manager pixi
```

**What this does**:
- Creates project directory structure
- Initializes state management
- Sets up environment configuration
- Creates default configuration file

**Output structure**:
```
iris_classification/
├── input/
│   └── data_description.md          # Your dataset description
├── output/
│   ├── idea.md                      # Generated research ideas
│   ├── literature.md                # Literature review
│   ├── methodology.md               # Analysis methodology
│   ├── code/                        # Generated analysis code
│   ├── plots/                       # Visualizations
│   └── paper.md                     # Final paper draft
├── .research_state.json             # State tracking (auto-managed)
├── .iterations/                     # Iteration history
└── research_config.toml             # Configuration file
```

---

### Step 2: Describe Your Dataset

Edit `iris_classification/input/data_description.md`:

```markdown
# Iris Flower Dataset Analysis

## Dataset Overview

The Iris dataset contains 150 samples of iris flowers from three species:
- Iris setosa
- Iris versicolor
- Iris virginica

## Available Data

**Source**: scikit-learn built-in dataset (`sklearn.datasets.load_iris`)

**Features**:
- Sepal length (cm)
- Sepal width (cm)
- Petal length (cm)
- Petal width (cm)
- Species (target variable)

**Size**: 150 samples (50 per species)

## Research Context

This is a classic dataset in machine learning and statistics, originally collected by 
botanist Edgar Anderson and made famous by statistician Ronald Fisher. We want to 
explore modern classification approaches and feature importance analysis.

## Computational Resources

**Environment**: Local laptop
**Constraints**: 
- 8GB RAM available
- No GPU required
- Processing time: < 5 minutes per analysis

## Tools Available

- Python 3.10+
- scikit-learn for ML algorithms
- pandas for data manipulation
- matplotlib/seaborn for visualization
- numpy for numerical operations

## Research Questions

1. Which morphological features best distinguish the three Iris species?
2. Can we achieve >95% classification accuracy using standard ML algorithms?
3. Are there any unexpected patterns or correlations in the feature space?
4. How do different classification algorithms compare in performance?
```

**Why this matters**: The data description guides the AI agents in understanding your context, available resources, and research objectives.

---

### Step 3: Configure Project Settings

Edit `iris_classification/research_config.toml`:

```toml
# Project Metadata
project_name = "iris_classification"
description = "Iris species classification analysis"
version = "1.0.0"

# Environment Configuration
env_manager = "pixi"  # or "conda", "venv", "apptainer", "nix", "guix"
python_version = "3.10"

# Execution Settings
[execution]
mode = "interactive"           # Pause for review between steps
max_iterations = 3             # Number of analysis iterations per run
max_debug_attempts = 10        # Maximum debugging attempts per iteration
timeout_seconds = 300          # 5-minute timeout per code execution

# Agent Configurations
[agents.idea_maker]
name = "idea_maker"
model = "gpt-4"
temperature = 0.9              # Higher creativity for ideas

[agents.literature_reviewer]
name = "literature_reviewer"
model = "gpt-4"
temperature = 0.5

[agents.methodologist]
name = "methodologist"
model = "gpt-4"
temperature = 0.7

[agents.analyst]
name = "analyst"
model = "o3-mini"              # Use reasoning model for analysis
temperature = 0.3
reasoning_effort = "medium"    # Balance quality and speed

[agents.paper_writer]
name = "paper_writer"
model = "gpt-4"
temperature = 0.6

[agents.reviewer]
name = "reviewer"
model = "gpt-4"
temperature = 0.4

# Module Settings
[modules.idea]
enabled = true
focus_areas = ["classification", "feature_importance", "visualization"]

[modules.literature]
enabled = true
max_papers = 10                # Limit literature search
databases = ["arxiv", "semantic_scholar"]

[modules.methodology]
enabled = true
require_validation = true

[modules.analysis]
enabled = true
save_intermediate = true       # Save intermediate results
generate_plots = true

[modules.paper]
enabled = true
journal_format = "generic"     # or "nature", "science", "plos"
max_length = 3000              # words

[modules.review]
enabled = true

# Resource Constraints
[resources]
max_memory_gb = 8
max_runtime_minutes = 10
gpu_required = false
cluster_submission = false

# Custom Parameters for this Analysis
[custom]
dataset_name = "iris"
dataset_source = "sklearn.datasets.load_iris"
classification_algorithms = ["RandomForest", "SVM", "LogisticRegression", "KNN"]
cross_validation_folds = 5
test_split_ratio = 0.2
random_seed = 42
```

**Feature Highlight**: Configuration files make your entire research pipeline reproducible and version-controllable.

---

### Step 4: Generate Research Ideas (Interactive Mode)

```bash
research-assistant idea --project iris_classification --interactive
```

**What happens**:

1. **Agent reads context**: The Idea Maker agent reads your data description
2. **Generates proposals**: Creates multiple research angle suggestions
3. **Outputs to file**: Writes to `output/idea.md`
4. **Waits for review**: Assistant pauses, prompting you to review

**Sample output** (`output/idea.md`):

```markdown
# Research Ideas: Iris Species Classification

## Idea 1: Multi-Algorithm Comparison Study
Systematically compare performance of classical ML algorithms (Random Forest, SVM, 
k-NN, Logistic Regression) on iris classification. Focus on accuracy, training 
time, and interpretability trade-offs.

**Novelty**: While iris is a classic dataset, few studies rigorously compare 
modern scikit-learn implementations with standardized cross-validation.

## Idea 2: Feature Importance Hierarchy
Use multiple feature importance methods (permutation importance, SHAP values, 
coefficient analysis) to establish consensus ranking of morphological features.

**Impact**: Helps botanists understand which measurements are most diagnostic 
for species identification in the field.

## Idea 3: Misclassification Pattern Analysis
Investigate which species pairs are most commonly confused, and identify the 
feature ranges where classification uncertainty is highest.

**Application**: Informs data collection priorities for ambiguous specimens.

## Recommended Focus
Combine Idea 1 and 2: Perform rigorous algorithm comparison while extracting 
interpretable feature importance insights. This balances methodological rigor 
with practical applicability.
```

**Your action**: 
- Review the ideas in `output/idea.md`
- Edit the file directly if you want to refine the direction
- Add notes about which ideas to prioritize

**To regenerate ideas with iteration tracking**: Use the `--iterate` flag with optional notes:

```bash
research-assistant idea --project iris_classification --iterate --notes "Focus more on visualization techniques"
```

This creates a new iteration entry in the project history and **preserves the previous output files** in `.iterations/idea/iteration_X/` before generating updated ideas.

**Understanding iteration tracking**:
- **Analysis iterations** (`max_iterations` in config): Number of refinement cycles the analyst performs (each generates new code, executes, interprets results)
- **Debug attempts** (`max_debug_attempts` in config): How many times the engineer can try to fix errors within a single iteration
- **Manual iteration** (`--iterate` flag): Explicitly start a new batch of iterations, tracked separately in project history
- **Continuation**: After configured iterations complete, you can choose to run more iterations

---

### Step 5: View Iteration History

```bash
research-assistant iterations iris_classification --module idea
```

**Output**:
```
Iteration History for Module: idea

Iteration 1 (2026-02-25 10:30:15)
  Status: completed
  Input: data_description.md
  Output: output/idea.md
  Notes: Initial idea generation
  Agent: idea_maker (gpt-4, temp=0.9)

Iteration 2 (2026-02-25 10:45:22)
  Status: completed
  Input: output/idea.md (edited)
  Output: output/idea_v2.md
  Notes: Focus more on visualization techniques
  Agent: idea_maker (gpt-4, temp=0.9)
  Parent: Iteration 1
```

**Feature Highlight**: Complete audit trail of all research iterations, including:
- Timestamps
- Input/output files
- User notes
- Agent configurations
- Iteration relationships

---

### Step 6: Literature Review

```bash
research-assistant literature --project iris_classification
```

**What happens**:

1. **Query formulation**: Agent creates search queries based on your idea
2. **Database search**: Searches arXiv, Semantic Scholar for relevant papers
3. **Synthesis**: Summarizes key findings and methodologies
4. **Citation tracking**: Maintains proper citations

**Sample output** (`output/literature.md`):

```markdown
# Literature Review: Iris Classification

## Classic Foundational Work

**Fisher, R.A. (1936)**. "The use of multiple measurements in taxonomic problems"
*Annals of Eugenics*, 7(2), 179-188.

The original paper introducing the iris dataset and linear discriminant analysis. 
Fisher demonstrated that linear combinations of features could effectively separate 
species, achieving near-perfect classification with a discriminant function.

**Key methodology**: Linear Discriminant Analysis (LDA)
**Results**: Near-perfect separation of setosa from other species, with some 
overlap between versicolor and virginica.

## Modern Machine Learning Approaches

**Brownlee, J. (2020)**. "Machine Learning Mastery with Python"
Chapter on iris classification comparing multiple algorithms.

Systematic comparison showing Random Forest (97.3%), SVM (98.0%), and Logistic 
Regression (96.7%) achieving comparable high accuracy. Notes that modern 
implementations handle feature scaling and regularization better than classical 
methods.

## Feature Importance Studies

**Molnar, C. (2019)**. "Interpretable Machine Learning"
Section on feature importance using SHAP values.

Demonstrates that petal length and petal width are most discriminative features, 
with SHAP values confirming this across multiple model types. Sepal width shows 
lowest importance for species discrimination.

## Visualization Best Practices

**Waskom, M. et al. (2021)**. "seaborn: statistical data visualization"
Journal of Open Source Software.

Modern approaches to multivariate visualization using pair plots, violin plots, 
and dimensionally-reduced projections (PCA, t-SNE) for exploring high-dimensional 
classification problems.

## Research Gap

While iris is well-studied, most analyses don't:
1. Rigorously compare model interpretability across algorithms
2. Systematically analyze misclassification patterns
3. Provide reproducible pipelines with modern tools

**Our contribution**: Fill this gap with reproducible, well-documented analysis 
using current best practices.
```

**Your action**: Review and edit if needed to focus literature scope.

---

### Step 7: Methodology Design

```bash
research-assistant methodology --project iris_classification
```

**What happens**:

1. **Method selection**: Agent proposes analysis approach based on literature
2. **Validation plan**: Designs cross-validation strategy
3. **Metric selection**: Chooses appropriate evaluation metrics
4. **Workflow diagram**: Creates analysis flowchart

**Sample output** (`output/methodology.md`):

```markdown
# Methodology: Iris Species Classification

## Data Preparation

1. **Load dataset**: `sklearn.datasets.load_iris()`
2. **Split strategy**: 80/20 train/test split, stratified by species
3. **Random seed**: 42 for reproducibility
4. **Feature scaling**: StandardScaler (important for SVM and k-NN)

## Algorithms to Compare

1. **Random Forest Classifier** (n_estimators=100)
   - Handles non-linear relationships
   - Provides feature importance

2. **Support Vector Machine** (RBF kernel)
   - Effective in high-dimensional spaces
   - Requires feature scaling

3. **Logistic Regression** (L2 regularization)
   - Baseline linear model
   - Interpretable coefficients

4. **k-Nearest Neighbors** (k=5)
   - Non-parametric approach
   - Sensitive to feature scaling

## Validation Strategy

**5-Fold Cross-Validation** on training set:
- Stratified folds to maintain class balance
- Report mean ± std dev for each metric
- Statistical significance testing between algorithms

**Final Evaluation** on held-out test set:
- Confusion matrices
- Classification reports (precision, recall, F1)
- ROC curves (one-vs-rest for multiclass)

## Feature Importance Analysis

1. **Permutation Importance**: Model-agnostic approach
2. **Random Forest Feature Importance**: Gini-based rankings
3. **Logistic Regression Coefficients**: Linear model weights
4. **Correlation Analysis**: Pairwise feature relationships

## Visualization Plan

1. **Pair plot**: All feature combinations colored by species
2. **Feature importance plot**: Comparative importance across models
3. **Confusion matrices**: For each algorithm
4. **ROC curves**: Multiclass performance visualization
5. **Decision boundary plot**: 2D projection (PCA) showing classification regions

## Success Criteria

- **Primary**: Overall accuracy > 95% on test set
- **Secondary**: Balanced performance across all three species
- **Tertiary**: Consistent feature importance rankings across methods

## Code Organization

```
code/
├── 1_data_loading.py          # Load and explore data
├── 2_preprocessing.py         # Scaling and splitting
├── 3_model_training.py        # Train all classifiers
├── 4_evaluation.py            # Compute metrics
├── 5_feature_importance.py    # Importance analysis
└── 6_visualization.py         # Generate all plots
```

## Reproducibility Checklist

- ✓ Fixed random seeds
- ✓ Version-pinned dependencies
- ✓ Documented hyperparameters
- ✓ Saved trained models
- ✓ Logged all metrics
```

**Your action**: Review methodology, adjust algorithms or validation strategy if needed.

---

### Step 8: Configure Computational Resources

Before executing code, specify resource constraints:

```bash
research-assistant resources iris_classification --configure
```

**Interactive prompts**:
```
Configure Computational Resources

Max Memory (GB) [default: 8]: 4
Max Runtime (minutes) [default: 10]: 5
Require GPU? [y/N]: n
Submit to cluster? [y/N]: n
Cluster scheduler (if yes) [slurm/pbs/sge]: 

Resources configured:
  Memory: 4 GB
  Runtime: 5 minutes
  GPU: Not required
  Cluster: Local execution
```

**Alternative**: Edit configuration file directly:

```toml
[resources]
max_memory_gb = 4
max_runtime_minutes = 5
gpu_required = false
cluster_submission = false
```

**View current resources**:

```bash
research-assistant resources iris_classification --show
```

**Feature Highlight**: Resource management ensures:
- Code doesn't exceed memory limits
- Long-running jobs are detected and can be killed
- Cluster submission scripts are auto-generated when needed
- Reproducibility across different compute environments

---

### Step 9: Analysis Execution (Automatic with Post-Review)

```bash
research-assistant analysis --project iris_classification
```

**What happens**:

1. **Process cleanup**: Checks for and terminates any existing analysis processes from previous runs
2. **Code generation**: Analyst agent writes Python code based on methodology
3. **Environment setup**: Creates isolated environment (pixi/conda/venv)
4. **Automatic execution**: Runs code immediately without approval prompt
5. **Debug loop**: If execution fails, automatically debugs and retries (up to configured max attempts)
6. **Iteration**: Repeats generation→execution→debug cycle until all configured iterations complete
7. **Post-completion review**: Prompts user to review results and optionally run more iterations

**Note**: The `--approve-code` flag is deprecated. Code now executes automatically to enable efficient debugging workflows.

**Execution output**:

```
Checking for existing analysis processes...
✓ No existing processes found

Analysis Iteration 1/3
=====================

Engineer writing code (iteration 1)...
✓ Code generated: output/code/analysis_01.py

Executing code in isolated environment...
Environment: pixi (iris_classification/.pixi/envs/default)

Installing dependencies:
  - numpy==1.24.3
  - pandas==2.0.2
  - scikit-learn==1.3.0
  - matplotlib==3.7.1
  - seaborn==0.12.2

Running analysis_01.py...
Dataset shape: (150, 5)

Feature statistics:
       sepal length (cm)  sepal width (cm)  ...
count         150.000000        150.000000  ...
mean            5.843333          3.057333  ...
std             0.828066          0.435866  ...
...

Class distribution:
setosa        50
versicolor    50
virginica     50

Data saved to output/intermediate/iris_data.csv

✓ Execution completed successfully (2.3s)
Memory used: 145 MB / 4000 MB

Analyst interpreting results...
✓ Analysis interpretation complete

Analysis Iteration 2/3
=====================
[... continues through all iterations ...]

Analysis Complete - Review Results
===================================

Review output files:
  - Analysis: output/analysis_final.md
  - Code: output/code/
  - Plots: output/plots/
  - Intermediate: output/intermediate/

Do you want to run additional analysis iterations? [y/N]: 
```

**Post-completion options**:
- **N** (default): Complete the analysis workflow
- **y**: Run additional iterations with the same configuration

**Feature Highlights**: 
- **Automatic execution** eliminates interruptions during iterative refinement
- **Automatic debugging** handles failures transparently (up to max_debug_attempts)
- **Process cleanup** prevents orphaned processes from previous runs
- **Post-completion review** gives user control after seeing results
- **Optional continuation** allows extending analysis based on outcomes

---

### Step 10: Handling Code Errors (Automatic Debug Loop)

If code fails during execution, the assistant automatically enters a debug loop:

```
Running analysis_01.py...
Error: ModuleNotFoundError: No module named 'sklearn'

Debug attempt 1/10
==================

Engineer debugging code...
✓ Fixed code generated: output/code/analysis_01.py

Executing updated code...
✓ Execution completed successfully (2.1s)

Analyst interpreting results...
✓ Analysis interpretation complete
```

**What happens**:
1. Error is captured with full traceback
2. Engineer agent receives error message and analyzes the issue
3. New code version generated with fixes
4. Code is automatically re-executed (no approval needed)
5. Loop continues until success or max_debug_attempts reached
6. All iterations are tracked in project history

**If max debug attempts exceeded**:

```
Debug attempt 10/10 failed
===========================

Maximum debug attempts reached. Analysis cannot proceed.

Saved error details to: output/intermediate/error_log.txt

Options:
1. Review error log and manually fix code
2. Adjust max_debug_attempts in config
3. Skip this analysis iteration

Choice [1]: 
```

**View debugging history**:

```bash
research-assistant iterations iris_classification --module analysis
```

```
Analysis Iteration 1
  Debug Attempt 1 (failed): ModuleNotFoundError
  Debug Attempt 2 (success): Fixed dependency specification
  Status: completed
  
Analysis Iteration 2
  Initial Execution (success): No debugging needed
  Status: completed
```

**Feature Highlight**: Automatic debugging eliminates manual intervention for common errors like missing imports, syntax issues, or data path problems, making the workflow much more efficient.

---

### Step 11: Complete Analysis Pipeline

After all configured iterations complete (default: 3-5 iterations), the analysis provides a summary:

```
Analysis Iteration 3/3 Complete
================================

✓ All iterations completed successfully
✓ Code executed without errors
✓ Results interpreted by analyst

Analysis Results Summary
========================

Test Set Accuracy:
  Random Forest:       97.0% (±1.2%)
  SVM (RBF):          98.0% (±0.8%)
  Logistic Regression: 96.5% (±1.5%)
  k-NN (k=5):         95.8% (±1.8%)

Feature Importance (consensus ranking):
  1. Petal length (cm)   - importance: 0.89
  2. Petal width (cm)    - importance: 0.78
  3. Sepal length (cm)   - importance: 0.34
  4. Sepal width (cm)    - importance: 0.21

Plots generated:
  - output/plots/pairplot.png
  - output/plots/feature_importance.png
  - output/plots/confusion_matrix_rf.png
  - output/plots/roc_curves.png
  - output/plots/decision_boundaries.png

All results saved to: output/analysis_results.json

Analysis Complete - Review Results
===================================

Review output files:
  - Analysis: output/analysis_final.md
  - Code: output/code/
  - Plots: output/plots/
  - Intermediate: output/intermediate/

Do you want to run additional analysis iterations? [y/N]: N

✓ Analysis workflow complete
```

**Generated outputs**:

```
iris_classification/output/
├── analysis_results.json          # Machine-readable metrics
├── analysis_final.md              # Human-readable summary from final iteration
├── code/                          # All generated scripts
│   ├── analysis_01.py             # Iteration 1
│   ├── analysis_02.py             # Iteration 2
│   └── analysis_03.py             # Iteration 3 (final)
├── plots/                         # All visualizations
│   ├── pairplot.png
│   ├── feature_importance.png
│   ├── confusion_matrix_rf.png
│   ├── confusion_matrix_svm.png
│   ├── confusion_matrix_lr.png
│   ├── confusion_matrix_knn.png
│   ├── roc_curves.png
│   └── decision_boundaries.png
└── intermediate/                  # Intermediate data
    ├── iris_data.csv
    ├── X_train.npy
    ├── X_test.npy
    ├── models/
    │   ├── rf_model.pkl
    │   ├── svm_model.pkl
    │   ├── lr_model.pkl
    │   └── knn_model.pkl
    └── metrics.json
```

**Note**: Each iteration generates a new `analysis_XX.py` file. The final iteration's analysis is saved as `analysis_final.md`.

---

### Step 12: Paper Writing

```bash
research-assistant paper --project iris_classification --format generic
```

**What happens**:

1. **Content synthesis**: Agent compiles ideas, literature, methodology, results
2. **Structure creation**: Follows scientific paper format
3. **Citation formatting**: Maintains proper references
4. **Figure integration**: References generated plots

**Sample output** (`output/paper.md`):

```markdown
# Comparative Analysis of Machine Learning Algorithms for Iris Species Classification

## Abstract

We present a systematic comparison of four classical machine learning algorithms 
(Random Forest, Support Vector Machine, Logistic Regression, and k-Nearest 
Neighbors) for classifying iris flower species based on morphological measurements. 
Using the Fisher iris dataset, we achieved >95% accuracy across all methods, with 
SVM demonstrating the highest performance (98.0%). Feature importance analysis 
revealed petal measurements as significantly more discriminative than sepal 
measurements, with petal length exhibiting the strongest classification signal. 
Our reproducible analysis pipeline, implemented with modern Python tools, provides 
a template for rigorous comparative evaluation of classification algorithms on 
biological datasets.

## Introduction

The classification of iris species based on morphological features represents a 
foundational problem in statistical pattern recognition. First introduced by 
Fisher (1936), the iris dataset has become a standard benchmark for evaluating 
classification algorithms. However, with advances in machine learning methodology 
and computational tools, there is value in revisiting this classic problem with 
modern techniques and reproducible pipelines.

### Research Objectives

1. Systematically compare four widely-used classification algorithms
2. Quantify feature importance across methods to identify discriminative morphology
3. Analyze misclassification patterns to understand algorithm limitations
4. Provide a fully reproducible analysis pipeline using current best practices

## Methods

### Dataset

We used the Fisher iris dataset (N=150 samples, 4 features, 3 species) accessed 
via scikit-learn (version 1.3.0). The dataset contains measurements of sepal 
length, sepal width, petal length, and petal width (all in centimeters) for 50 
samples each of *Iris setosa*, *I. versicolor*, and *I. virginica*.

### Preprocessing

Features were standardized using `StandardScaler` (zero mean, unit variance) to 
ensure comparability across algorithms sensitive to feature scales. Data were 
split into training (80%, N=120) and test (20%, N=30) sets using stratified 
sampling (random seed=42).

### Classification Algorithms

We evaluated four algorithms implemented in scikit-learn:

1. **Random Forest (RF)**: Ensemble of 100 decision trees
2. **Support Vector Machine (SVM)**: RBF kernel, regularization C=1.0
3. **Logistic Regression (LR)**: L2 regularization, penalty=0.01
4. **k-Nearest Neighbors (k-NN)**: k=5, Euclidean distance

Hyperparameters were selected based on preliminary 5-fold cross-validation.

### Evaluation Metrics

- Classification accuracy (overall and per-class)
- Precision, recall, F1-score
- Confusion matrices
- ROC-AUC (one-vs-rest multiclass)

### Feature Importance

We computed feature importance using:
- Permutation importance (model-agnostic)
- RF Gini importance
- LR coefficient magnitudes

Results were normalized and averaged across methods.

## Results

### Classification Performance

All algorithms achieved >95% test accuracy (Figure 1). SVM demonstrated the 
highest performance (98.0% ± 0.8%), followed closely by RF (97.0% ± 1.2%). 
Logistic Regression (96.5% ± 1.5%) and k-NN (95.8% ± 1.8%) showed slightly 
lower but still excellent performance.

![Confusion matrices for all classifiers](plots/confusion_matrices_combined.png)

**Figure 1**: Confusion matrices reveal that misclassifications occur primarily 
between *I. versicolor* and *I. virginica*, with *I. setosa* perfectly 
classified by all methods.

### Feature Importance

Petal measurements dominated feature importance across all methods (Figure 2):

1. Petal length: 0.89 (normalized importance)
2. Petal width: 0.78
3. Sepal length: 0.34
4. Sepal width: 0.21

![Feature importance comparison](plots/feature_importance.png)

**Figure 2**: Consensus feature importance averaged across permutation importance, 
RF Gini scores, and LR coefficient magnitudes. Error bars show standard deviation 
across methods.

### Misclassification Patterns

Analysis of the 2-3 misclassified samples revealed they were exclusively 
*I. versicolor* or *I. virginica* with overlapping feature values in the petal 
length range of 4.5-5.0 cm and petal width of 1.3-1.7 cm.

## Discussion

### Interpretation

Our results confirm that petal morphology is the primary discriminant for iris 
species classification, with petal length being most diagnostic. This aligns with 
botanical knowledge that petal size varies more dramatically between species than 
sepal characteristics.

The high accuracy across diverse algorithms (95-98%) suggests the iris 
classification problem is linearly separable in feature space, with minimal 
advantage from complex non-linear methods. The consistent misclassification 
between *I. versicolor* and *I. virginica* indicates genuine morphological 
overlap rather than methodological limitations.

### Comparison to Literature

Our SVM accuracy (98%) matches or exceeds historical results, while our systematic 
feature importance analysis provides stronger quantitative support for petal-based 
classification than previous studies.

### Limitations

- Small sample size (N=150) limits statistical power
- Dataset lacks temporal, geographic, or environmental covariates
- Binary classification subproblems (e.g., setosa vs. others) may be more relevant 
  for practical applications

### Reproducibility

Our complete analysis pipeline with fixed random seeds, version-pinned 
dependencies, and documented hyperparameters ensures full reproducibility. All 
code and data are available at [repository link].

## Conclusion

We demonstrated that modern machine learning algorithms achieve excellent (>95%) 
accuracy on iris species classification, with SVM performing best. Feature 
importance analysis quantitatively confirmed petal measurements as the most 
discriminative morphological features. Our reproducible pipeline provides a 
template for rigorous comparative algorithm evaluation on biological datasets.

## References

Fisher, R.A. (1936). The use of multiple measurements in taxonomic problems. 
*Annals of Eugenics*, 7(2), 179-188.

Pedregosa et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of 
Machine Learning Research*, 12, 2825-2830.

[Additional references from literature review...]

## Supplementary Materials

- Complete Python code: `output/code/`
- All plots: `output/plots/`
- Trained models: `output/intermediate/models/`
- Raw metrics: `output/analysis_results.json`
```

**Your action**: Review paper, edit for style/clarity, add domain-specific insights.

---

### Step 13: Final Review and Critique

```bash
research-assistant review --project iris_classification
```

**What happens**:

1. **Critical evaluation**: Reviewer agent critiques the entire workflow
2. **Identifies gaps**: Highlights missing analyses or limitations
3. **Suggests improvements**: Proposes refinements for each section
4. **Quality check**: Validates reproducibility claims

**Sample output** (`output/review.md`):

```markdown
# Review: Iris Species Classification Analysis

## Overall Assessment

**Strengths**:
✓ Clear research objectives with focused scope
✓ Rigorous methodology with appropriate validation
✓ Reproducible pipeline with documented dependencies
✓ Strong feature importance analysis across multiple methods
✓ Well-structured paper with proper scientific format

**Weaknesses**:
✗ Limited novelty (well-studied dataset and standard methods)
✗ No statistical significance testing between algorithm performances
✗ Missing hyperparameter tuning justification
✗ Could benefit from dimensionality reduction visualization (PCA/t-SNE)

**Overall Rating**: 7.5/10 (Solid reproducible analysis, limited novelty)

## Detailed Critique by Section

### Introduction
- **Strength**: Clearly motivates the analysis and sets expectations
- **Improvement**: Could better articulate why revisiting this classic problem 
  matters (e.g., pedagogical value, reproducibility best practices)

### Methods
- **Strength**: Comprehensive description enabling reproduction
- **Weakness**: Hyperparameter selection described as "preliminary" without details
- **Suggestion**: Add grid search or cross-validation plots showing hyperparameter 
  selection process

### Results
- **Strength**: Clear presentation with effective visualizations
- **Weakness**: No confidence intervals or significance tests for accuracy differences
- **Suggestion**: Add McNemar's test or paired t-test to determine if 98% vs 97% 
  is statistically significant

### Discussion
- **Strength**: Honest acknowledgment of limitations
- **Weakness**: Could expand on practical applications or extensions
- **Suggestion**: Discuss how this pipeline could be adapted to other botanical 
  classification problems

## Reproducibility Checklist

✓ Fixed random seeds documented
✓ Software versions specified
✓ Complete code provided
✓ Hyperparameters listed
✗ Hardware specifications not mentioned (consider adding for transparency)
✗ Execution time not reported (useful for scalability assessment)

## Suggested Improvements

### High Priority
1. **Add statistical testing**: Compare algorithm performances with McNemar's test
2. **Hyperparameter tuning**: Document grid search process and results
3. **Execution metrics**: Report runtime and memory usage

### Medium Priority
4. **PCA visualization**: Add 2D projection showing decision boundaries
5. **Learning curves**: Show training/validation accuracy vs sample size
6. **Ablation study**: Test performance with subsets of features

### Low Priority (Extensions)
7. **Ensemble methods**: Try voting or stacking classifiers
8. **Deep learning baseline**: Add simple neural network for comparison
9. **Uncertainty quantification**: Report prediction confidence intervals

## Recommendations for Iteration

If you have time for one more iteration:
→ Focus on **statistical testing** (high impact, low effort)

If you have time for a full revision:
→ Add **hyperparameter tuning documentation** and **PCA visualization**

## Publication Readiness

**Current status**: Suitable for course project, technical blog post, or 
reproducibility tutorial.

**Not yet suitable for**: Academic journal (limited novelty, well-studied problem)

**Best target venues**:
- Technical blog (Medium, Towards Data Science)
- GitHub repository showcase
- Educational tutorial
- Internal technical report
```

**Your action**: Review critique, decide whether to iterate or finalize.

---

### Step 14: Iteration Based on Review

If you want to address reviewer comments, you can re-run the analysis module to run additional iterations:

```bash
# Simply re-run analysis - will prompt for continuation after completing configured iterations
research-assistant analysis --project iris_classification

# Or use --iterate flag to explicitly start a new iteration batch
research-assistant analysis --project iris_classification --iterate --notes "Add statistical significance testing"
```

**What happens**:

1. **Continuation prompt**: After the configured number of iterations complete, you're asked if you want more iterations
2. **Context preservation**: New iterations build on previous work (models, intermediate results)
3. **Iteration tracking**: All iterations are tracked in the project state
4. **Incremental refinement**: Each iteration can add new analyses or improve existing ones

**After responding 'y' to continuation prompt**:


```
Starting additional analysis iterations...

Analysis Iteration 4/∞
=====================

Engineer writing code (iteration 4)...
Incorporating previous findings: statistical significance testing
✓ Code generated: output/code/analysis_04.py

Executing code...
✓ Execution completed successfully (1.8s)

Analyst interpreting results...
✓ Updated analysis with statistical tests

Analysis Complete - Review Results
===================================

New findings added:
  - McNemar's test: SVM vs RF (p=0.342, no significant difference)
  - Statistical significance testing section in analysis

Do you want to run additional analysis iterations? [y/N]: N

✓ Analysis workflow complete
```

**Updated code** (`code/analysis_04.py`):

```python
"""
Statistical significance testing between classifiers
Added in iteration 4 based on reviewer feedback
"""
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from mlxtend.evaluate import mcnemar_table, mcnemar
import pickle

# Load models and test data
with open('output/intermediate/models/rf_model.pkl', 'rb') as f:
    rf_model = pickle.load(f)
with open('output/intermediate/models/svm_model.pkl', 'rb') as f:
    svm_model = pickle.load(f)

X_test = np.load('output/intermediate/X_test.npy')
y_test = np.load('output/intermediate/y_test.npy')

# Get predictions
rf_pred = rf_model.predict(X_test)
svm_pred = svm_model.predict(X_test)

# McNemar's test
tb = mcnemar_table(y_target=y_test, 
                   y_model1=rf_pred, 
                   y_model2=svm_pred)

chi2, p_value = mcnemar(ary=tb, corrected=True)

print(f"McNemar's Test: RF vs SVM")
print(f"Chi-square statistic: {chi2:.4f}")
print(f"P-value: {p_value:.4f}")

if p_value < 0.05:
    print("→ Significant difference in performance")
else:
    print("→ No significant difference (p > 0.05)")

# Save results
results = {
    'chi2': chi2,
    'p_value': p_value,
    'contingency_table': tb.tolist()
}

import json
with open('output/intermediate/statistical_tests.json', 'w') as f:
    json.dump(results, f, indent=2)
```

**Result**: Additional iterations complete automatically, paper can be updated with new findings, and all work is tracked in iteration history.

---

### Step 15: Export Configuration for Reproducibility

```bash
research-assistant config iris_classification --export-template --output iris_analysis_v1.toml
```

**Generated template** (`iris_analysis_v1.toml`):

```toml
# Reproducible configuration for Iris Classification Analysis v1.0
# Generated: 2026-02-25
# Author: [Your Name]
# 
# To reproduce this analysis:
#   1. Install research-assistant: pip install -e .
#   2. Run: research-assistant init new_project --config iris_analysis_v1.toml
#   3. Run: research-assistant run new_project

project_name = "iris_classification"
description = "Iris species classification with statistical testing"
version = "1.0.0"

env_manager = "pixi"
python_version = "3.10"

[execution]
mode = "interactive"
require_code_approval = true
max_iterations = 3
timeout_seconds = 300

[agents.idea_maker]
name = "idea_maker"
model = "gpt-4"
temperature = 0.9

[agents.analyst]
name = "analyst"
model = "o3-mini"
temperature = 0.3
reasoning_effort = "medium"

# ... (complete configuration)

[custom]
dataset_name = "iris"
dataset_source = "sklearn.datasets.load_iris"
statistical_tests = ["mcnemar", "friedman"]
visualization_extras = ["pca_2d", "learning_curves"]
```

**Share this file** with collaborators to reproduce your exact analysis pipeline.

---

### Step 16: Resume from Checkpoint

If you need to stop and resume later:

```bash
# Work is automatically saved to .research_state.json

# Resume from where you left off
research-assistant resume iris_classification

# Or resume from a specific module
research-assistant resume iris_classification --from methodology
```

**What happens**:
- State is loaded from `.research_state.json`
- Previous outputs are preserved
- You continue from the last completed module
- All iteration history is maintained

---

### Step 17: Run Complete Pipeline (Non-Interactive)

For subsequent runs or after you've validated the approach:

```bash
research-assistant run --project iris_classification --no-interactive
```

**What happens**:
- Runs all modules sequentially without pauses
- Code is executed automatically (default behavior)
- Complete in ~5-10 minutes for iris dataset
- Useful for reproducibility testing or batch processing

**Note**: The `--no-approve-code` flag is deprecated as automatic execution is now the default.

---

## Advanced Features

### Feature 1: Environment Manager Comparison

Test your analysis across different environment managers:

```bash
# Run with pixi
research-assistant init iris_pixi --env-manager pixi
research-assistant run iris_pixi --from analysis

# Run with conda
research-assistant init iris_conda --env-manager conda
research-assistant run iris_conda --from analysis

# Run with apptainer (containerized, for HPC)
research-assistant init iris_container --env-manager apptainer
research-assistant run iris_container --from analysis
```

**Use cases**:
- **pixi**: Modern, fast, reproducible (recommended for scientific computing)
- **conda**: Widely used, good compatibility
- **venv**: Lightweight, standard Python
- **apptainer**: Containerized, for HPC clusters and maximum reproducibility
- **nix**: Declarative, bit-for-bit reproducible
- **guix**: Free software ecosystem, research reproducibility

### Feature 2: Resource-Constrained Execution

Simulate resource limits for testing:

```bash
# Test analysis under memory constraints
research-assistant resources iris_classification --configure \
  --max-memory 2 \
  --max-runtime 3 \
  --gpu false

research-assistant analysis --project iris_classification
```

**If code exceeds limits**:
```
Memory limit exceeded: 2.3 GB / 2.0 GB
Analysis terminated.

Options:
1. Increase memory limit
2. Optimize code to reduce memory usage
3. Skip this analysis

Choice [1]: 2
Additional notes: Use data chunking, process in batches
```

**Feature Highlight**: Prevents runaway processes and prepares code for cluster execution.

### Feature 3: Cluster Job Submission

For larger analyses, generate cluster submission scripts:

```bash
research-assistant resources iris_large --configure \
  --cluster true \
  --scheduler slurm \
  --nodes 1 \
  --cpus 16 \
  --memory 64 \
  --time 24:00:00

research-assistant analysis --project iris_large --generate-submit-script
```

**Generated script** (`output/submit_analysis.sh`):

```bash
#!/bin/bash
#SBATCH --job-name=iris_analysis
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=logs/analysis_%j.out
#SBATCH --error=logs/analysis_%j.err

# Load environment
module load python/3.10
source .pixi/envs/default/bin/activate

# Run analysis
cd $SLURM_SUBMIT_DIR
python code/3_model_training.py
python code/4_evaluation.py

echo "Analysis completed on $(date)"
```

Submit with: `sbatch output/submit_analysis.sh`

### Feature 4: Multi-Project Comparison

Compare different approaches to the same problem:

```bash
# Approach 1: Classical ML (our example)
research-assistant init iris_classical --config classical_config.toml

# Approach 2: Deep Learning
research-assistant init iris_dl --config deep_learning_config.toml

# Approach 3: Ensemble Methods
research-assistant init iris_ensemble --config ensemble_config.toml

# Compare results
research-assistant compare iris_classical iris_dl iris_ensemble \
  --metrics accuracy f1_score runtime memory_usage
```

**Comparison output**:

```
Project Comparison
==================

Metric: Accuracy
  iris_classical: 98.0% (±0.8%)
  iris_dl:        97.2% (±1.1%)
  iris_ensemble:  98.5% (±0.6%)  ← Best

Metric: F1-Score
  iris_classical: 0.979
  iris_dl:        0.971
  iris_ensemble:  0.984  ← Best

Metric: Runtime
  iris_classical: 2.3s    ← Best
  iris_dl:        45.7s
  iris_ensemble:  8.1s

Metric: Memory Usage
  iris_classical: 145 MB  ← Best
  iris_dl:        1.2 GB
  iris_ensemble:  380 MB

Recommendation: iris_ensemble for accuracy, iris_classical for efficiency
```

### Feature 5: Agent Model Switching

Test different LLM models for specific tasks:

```toml
# Use different models for different agents
[agents.idea_maker]
model = "gpt-4"           # Creative thinking

[agents.analyst]
model = "o3-mini"         # Code generation + reasoning
reasoning_effort = "high"

[agents.paper_writer]
model = "claude-opus-4"   # Long-form writing

[agents.reviewer]
model = "gpt-4"           # Critical analysis
```

**Compare model performance**:

```bash
research-assistant compare-models iris_classification \
  --agent analyst \
  --models "gpt-4,o3-mini,claude-sonnet-4" \
  --metric code_quality
```

### Feature 6: Partial Workflow Execution

Run only specific modules:

```bash
# Only generate ideas and methodology, skip execution
research-assistant run iris_classification \
  --modules idea,methodology \
  --skip analysis,paper,review

# Only re-run paper writing with different format
research-assistant paper iris_classification \
  --format nature

# Re-run paper with iteration tracking
research-assistant paper iris_classification \
  --format nature --iterate --notes "Adjusted for Nature journal style"
```

### Feature 7: Debugging and Logging

Enable verbose logging for troubleshooting:

```bash
research-assistant run iris_classification --verbose --log-file debug.log
```

**Log output** (`debug.log`):

```
[2026-02-25 10:30:15] INFO: Initializing project: iris_classification
[2026-02-25 10:30:16] INFO: Environment manager: pixi
[2026-02-25 10:30:16] DEBUG: Loading state from .research_state.json
[2026-02-25 10:30:16] DEBUG: State loaded: 0 modules completed
[2026-02-25 10:30:17] INFO: Starting module: idea
[2026-02-25 10:30:17] DEBUG: Agent: idea_maker (model=gpt-4, temp=0.9)
[2026-02-25 10:30:17] DEBUG: Input file: input/data_description.md (1024 bytes)
[2026-02-25 10:30:18] DEBUG: API call: OpenAI GPT-4 (tokens: 856 in, 1234 out)
[2026-02-25 10:30:45] INFO: Generated output: output/idea.md (3456 bytes)
[2026-02-25 10:30:45] DEBUG: Saving state to .research_state.json
[2026-02-25 10:30:45] INFO: Module 'idea' completed successfully
[2026-02-25 10:30:45] INFO: Waiting for user review (interactive mode)...
```

---

## Troubleshooting

### Issue 1: API Rate Limits

**Problem**: Too many API calls in short time

**Solution**:
```bash
# Add rate limiting to config
[execution]
api_rate_limit_rpm = 20  # Requests per minute
retry_on_rate_limit = true
retry_max_attempts = 3
retry_backoff_seconds = 60
```

### Issue 2: Environment Setup Fails

**Problem**: Pixi/conda can't resolve dependencies

**Solution**:
```bash
# Try different environment manager
research-assistant config iris_classification --set env_manager=venv

# Or manually create environment
pixi init iris_classification
pixi add python=3.10 numpy pandas scikit-learn matplotlib
research-assistant run iris_classification --use-existing-env
```

### Issue 3: Code Execution Timeout

**Problem**: Analysis exceeds time limit

**Solution**:
```bash
# Increase timeout
research-assistant resources iris_classification --configure --max-runtime 30

# Or run in background
research-assistant analysis iris_classification --background --notify email@example.com
```

### Issue 4: Out of Memory

**Problem**: Code uses too much RAM

**Solution**:
```bash
# Enable automatic code optimization
research-assistant config iris_classification --set optimize_for_memory=true

# Or use data chunking
[custom]
use_data_chunking = true
chunk_size = 1000
```

### Issue 5: Lost Work After Crash

**Problem**: Terminal closed during execution

**Solution**:
```bash
# State is auto-saved every step
research-assistant resume iris_classification

# Check last saved state
research-assistant status iris_classification
```

**Status output**:
```
Project: iris_classification
Status: In Progress (60% complete)

Completed Modules:
  ✓ idea (2026-02-25 10:45:30)
  ✓ literature (2026-02-25 11:02:15)
  ✓ methodology (2026-02-25 11:18:42)

Next Module: analysis

Last state save: 2026-02-25 11:18:43
Iterations: 2 (1 in idea, 1 in methodology)
```

---

## Summary: Complete Command Reference

```bash
# Project lifecycle
research-assistant init <project> --env-manager <pixi|conda|venv|apptainer|nix|guix>
research-assistant run <project> [--interactive]
research-assistant resume <project> [--from <module>]
research-assistant status <project>

# Individual modules (with iteration support)
research-assistant idea <project> [--interactive] [--iterate] [--notes "..."]
research-assistant literature <project> [--interactive] [--iterate] [--notes "..."]
research-assistant methodology <project> [--interactive] [--iterate] [--notes "..."]
research-assistant analysis <project> [--iterate] [--notes "..."]
research-assistant paper <project> [--format nature|science|plos|generic] [--iterate] [--notes "..."]
research-assistant review <project> [--interactive] [--iterate] [--notes "..."]

# Configuration
research-assistant config <project> --show
research-assistant config <project> --edit
research-assistant config <project> --validate
research-assistant config <project> --export-template --output <file>

# Resources
research-assistant resources <project> --configure
research-assistant resources <project> --show

# Iteration tracking
research-assistant iterations <project> [--module <name>]

# Utilities
research-assistant compare <project1> <project2> [--metrics ...]
research-assistant compare-models <project> --agent <name> --models "..."
research-assistant export <project> --format <zip|tar|git>
research-assistant validate <project>  # Check reproducibility
```

**Note**: The `--approve-code` flag has been deprecated. Code execution is now automatic by default to enable efficient debugging workflows.

---

## Next Steps

After completing the iris example, you can:

1. **Adapt to your data**: Replace iris with your dataset in `data_description.md`
2. **Customize agents**: Adjust model/temperature in `research_config.toml`
3. **Scale up**: Use cluster resources for larger analyses
4. **Share workflows**: Export configuration templates for collaborators
5. **Build library**: Create reusable configuration templates for common analyses

**Example extensions**:
- Classification: Other UCI datasets (wine, breast cancer, digits)
- Regression: Boston housing, diabetes, California housing
- Time series: Stock prices, weather data, sensor readings
- Text: Sentiment analysis, topic modeling, NER
- Images: MNIST, CIFAR-10 (with deep learning config)

---

## Conclusion

The Research Assistant provides a complete human-in-the-loop scientific workflow with:

- ✓ **Interactive control** at key decision points
- ✓ **Automatic execution** with intelligent debugging
- ✓ **Full iteration tracking** for reproducibility
- ✓ **Post-completion review** for user control
- ✓ **Resource management** for efficient execution
- ✓ **Configuration management** for sharing
- ✓ **Multiple environment managers** for flexibility
- ✓ **State persistence** for reliability

The iris classification example demonstrated all features in a simple, reproducible context that runs on any laptop in minutes. Adapt this workflow to your research domain and scale up as needed.

**Questions or issues?** See [QUICKREF.md](QUICKREF.md) for command syntax or [HUMAN_IN_THE_LOOP.md](HUMAN_IN_THE_LOOP.md) for iteration details.
