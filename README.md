### Example 1: Parse and deduplicate BLAST outputs
This step filters raw BLAST results to remove duplicates and extract unique protein identifiers for downstream analysis.

```bash
cd scripts
python 01_deduplication.py -i ../example_data/blast_results_test.txt -od ../results/filtered_blast_data.txt -oi ../results/unique_protein_ids.txt
```

### Example 2: Filter bacterial proteins (Two-step workflow)
This workflow identifies bacterial proteins by mapping accessions to taxonomy databases. It features a two-step process designed to robustly rescue sequences with merged or updated TaxIDs.

#### Explanation of Toy Dataset for Taxonomy Mapping
To demonstrate the robustness of the taxonomy mapping scripts without requiring the 40GB+ NCBI database, a minimal toy dataset is provided in `example_data/`. 

**1. Taxonomy Definitions (`categories_test.dmp`):**
- `1001` represents **Bacteria** (mapped to category `B`).
- `1002` represents **Eukaryota** (mapped to category `E`).

**2. Input Proteins (`input_id_test.txt`) and Designed Logic:**
- **`prot_A`**: A standard bacterial protein (TaxID 1001 in `a2t_test.tsv`). 
  * *Expected behavior:* Successfully identified in Step 2.1.
- **`prot_X`**: A bacterial protein from the obsolete/dead database (TaxID 1001 in `a2t_dead_test.tsv`). 
  * *Expected behavior:* Successfully identified in Step 2.1.
- **`prot_C`**: A eukaryotic protein (TaxID 1002). 
  * *Expected behavior:* Filtered out as non-bacterial.
- **`prot_Y`**: An unmapped sequence with no database records. 
  * *Expected behavior:* Marked as missing.
- **`prot_M`**: A protein with an outdated TaxID (9999) that has been merged into the bacterial TaxID 1001 (`merged_test.dmp`). 
  * *Expected behavior:* Rescued in Step 2.2.
- **`prot_L`**: A protein with a TaxID (8888) missing from the category list but possessing a bacterial lineage (Domain ID `2` in `taxidlineage_test.dmp`). 
  * *Expected behavior:* Rescued in Step 2.2.

#### Execution
```bash
# Ensure you are in the 'scripts' directory
python 02_1_find_bacteria.py -i ../example_data/input_id_test.txt -t ../example_data/categories_test.dmp -a ../example_data/a2t_test.tsv -d ../example_data/a2t_dead_test.tsv -of ../results/02_1_found_bacteria.txt -on ../results/02_1_non_bacterial.txt -om ../results/02_1_missing.txt -ot ../results/02_1_tax_not_found.txt

# Step 2.2: Re-evaluate missing taxonomy (Merged & Lineage databases)
python 02_2_taxid_redefination.py -tl ../example_data/taxidlineage_test.dmp -m ../example_data/merged_test.dmp -tc ../example_data/categories_test.dmp -a ../example_data/a2t_test.tsv -d ../example_data/a2t_dead_test.tsv -i ../results/02_1_tax_not_found.txt -ob ../results/02_2_rescued_bacteria.txt -onb ../results/02_2_rescued_non_bacteria.txt -onf ../results/02_2_final_not_found.txt
```

### Example 3: K-mer extraction, t-SNE dimensionality reduction, and DBSCAN clustering
To guarantee absolute code reproducibility without altering any parameters (e.g., `perplexity=30`, `n_components=50`) in the original manuscript script, we have provided a pre-generated synthetic FASTA file (`input.fasta`) and its corresponding ID lists in the `example_data/` directory. This mock dataset contains sufficient K-mer diversity and sequence count to satisfy the strict requirements of SVD and t-SNE algorithms.

```bash
# Navigate to the example data directory where the hardcoded input files are located
cd ../example_data

# Execute the unmodified clustering script
python ../scripts/03_kmer_tsne_dbscan.py
```

### Example 4: Phenotypic Fold-Change Heatmap Generation
This step generates a publication-ready (500 DPI, LZW-compressed TIFF) hierarchical clustering heatmap from susceptibility or expression data. The script applies custom continuous gradients, automated text contrast adjustments (white text for heavily elevated expression), and statistical significance annotations. We have provided pre-generated mock matrices (`fc_mean.xlsx` and `p_values.xlsx`) in the `example_data/` directory.

```bash
# Execute the unmodified plotting script (ensure you are still in the example_data directory)
python ../scripts/04_plot_mic_heatmap.py
```

### Example 5: Global Distribution Mapping of Identified MBLs
This script visualizes the geographical distribution of the identified sequences. A representative subset of sampling coordinates (`samples.xlsx`) and the global base map shapefiles are provided in `example_data/`.

```bash
python ../scripts/05_geographic_distribution.py
```

### Example 6: Global and Regional Habitat Distribution
This script generates publication-quality, split-panel stacked bar charts to visualize the distribution of sequences across different countries and specific US states, categorized by environmental habitats. A representative subset of the original metadata (`input_data.xlsx`) is provided in `example_data/`.

```bash
python ../scripts/06_env_distribution.py
```

### Example 7: Spatiotemporal Dynamics of Isolates
This script visualizes the temporal isolation density and year of isolation distribution across different environmental habitats using a jittered scatter timeline. It seamlessly shares the same input metadata (`input_data.xlsx`) used in Example 6.

```bash
# Execute the unmodified timeline plotting script
python ../scripts/07_time_distribution.py
```
