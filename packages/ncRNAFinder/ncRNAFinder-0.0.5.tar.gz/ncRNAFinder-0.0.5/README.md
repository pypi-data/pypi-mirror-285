# ncRNAFinder
ncRNAFinder is an automatic and scalable system for large-scale data annotation analysis of ncRNAs which use both sequence and structural search strategy for ncRNA annotation.

## Install
To use the ncRNAFinder, it is necessary to install some dependencies and databases. First, the necessary tools are [BLAST](https://blast.ncbi.nlm.nih.gov/Blast.cgi) (version 2.15.0) and [INFERNAL](http://eddylab.org/infernal/) (1.1.5). Second, the databases needed are [RNAcentral](https://rnacentral.org) (version 24) and [Rfam](https://rfam.org) (version 14.10). Lastly, the Python libraries required are biopython, joblib, matplotlib, matplotlib_venn, numpy and pandas. 

> [!IMPORTANT]
> The download of the RNAcentral database takes some time, almost 7 hours.

## Requirements
- [Python](https://www.python.org)
  - [Biopython](https://biopython.org)
  - [Joblib](https://joblib.readthedocs.io/en/stable/)
  - [Matplotlib](https://matplotlib.org)
  - [Matplotlib_venn](https://pypi.org/project/matplotlib-venn/)
  - [Numpy](https://numpy.org)
  - [Pandas](https://pandas.pydata.org)
- [BLAST](https://blast.ncbi.nlm.nih.gov/Blast.cgi)
- [INFERNAL](http://eddylab.org/infernal/)

> [!NOTE]
> All Python libraries are automatically installed. The BLAST and INFERNAL tools should be download by the user and add to the PATH.

## Usage
To execute the tool, simply use the following command:
~~~
import ncRNAFinder as nf
nf.ncRNAFinder(input_file, output_name, pident, coverage, threads, BestHit)

or

annotation = nf.ncRNAFinder(input_file, output_name, pident, coverage, threads, BestHit)
~~~

### Mandatory parameters:
~~~
input_file <file_name>                                       Input file in FASTA format

output_name <output_name>                                    Output name to save the results
~~~

### Optional parameters:
~~~
pident <integer>                                       Minimun percentage of identity of BLASTn. (Default: 95)

coverage <integer>                                     Minimun percentage of coverage of BLASTn. (Default: 95)

threads <integer>                                      Number of threads. (Default: 1)

BestHit <1|0>                                          Option to filter only the best result between two strands, based on E-value), 1-yes or 0-no. (Default: 1)
~~~

## Output
The ncRNAFinder function outputs the annotation in format of dataframe. Besides that, it automatically outputs the annotation in GFF and CSV formats, along with a text file containing the IDs with the original annotation from each tool (BLAST and INFERNAL), a table with the number of ncRNAs annotated, and three graphs: (i) a bar plot showing the number of ncRNAs annotated, (ii) a Venn diagram with the number of ncRNAs identified by each tool (BLAST and INFERNAL), and (iii) a stacked bar plot with the number of ncRNAs identified in each chromosome. Additionally, the ncRNAFinder generates exclusive outputs for miRNA and tRNA, including their annotations in CSV and GFF formats, their sequences, and a table with each type. 

```
<output_name>/
├──  <output_name>_annotation.gff
├──  <output_name>_annotation.csv
├──  <output_name>_ID_annotation.txt
├──  <output_name>_sequences_ncRNA.fa
├──  <output_name>_Table_quantity_ncRNAs.csv
├──  Figures/
│   ├──  <output_name>_BarPlot.png
│   ├──  <output_name>_DiagramaVeen.png
│   └──  <output_name>_StackedPlot.png
├──  miRNA/
│   ├──  <output_name>_miRNA_annotation.gff
│   ├──  <output_name>_miRNAs.csv
│   ├──  <output_name>_miRNA_sequences_ncRNA.fa
│   └──  <output_name>_miRNA_Table_quantity_ncRNAs.csv
└──  tRNA/
    ├──  <output_name>_tRNA_annotation.gff
    ├──  <output_name>_tRNAs.csv
    ├──  <output_name>_tRNA_sequences_ncRNA.fa
    └──  <output_name>_tRNA_Table_quantity_ncRNAs.csv
```

## Reference

## Contact
To report bugs, to ask for help and to give any feedback, please contact Alexandre R. Paschoal (paschoal@utfpr.edu.br) or Vitor Gregorio (vitor-gregorio@hotmail.com).