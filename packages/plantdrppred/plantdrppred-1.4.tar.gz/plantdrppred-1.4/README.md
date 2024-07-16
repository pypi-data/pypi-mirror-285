# PlantDRPpred
A method for prediction of Plant Disease Resistance Protein

# Introduction
PlantDRPpred is developed for predicting, mapping and scanning plant resistance proteins. More information on PlantDRPpred is available from its web server http://webs.iiitd.edu.in/raghava/plantdrppred. This page provides information about the standalone version of PlantDRPpred.

## PIP Installation
PIP version is also available for easy installation and usage of this tool. The following command is required to install the package 
```
pip install plantdrppred
```
To know about the available option for the pip package, type the following command:
```
plantdrppred -h
```

# Standalone

Standalone version of PlantDRPpred is written in python3 and the following libraries are necessary for a successful run:

- scikit-learn > 1.3.0
- Pandas
- Numpy
- blastp


**Minimum USAGE** 

To know about the available option for the standalone, type the following command:
```
PlantDRPpred.py -h
```
To run the example, type the following command:
```
PlantDRPpred.py -i seq.fasta

```
where seq.fasta is a input FASTA file. This will predict plant resistance protein in FASTA format. It will use other parameters by default. It will save output in "output_result.csv" in CSV (comma separated variables).

**Full Usage**: 
```
Following is complete list of all options, you may get these options
usage: plantdrppred [-h] -i INPUT [-o OUTPUT] [-t THRESHOLD] [-m {1,2}] [-d {1,2}] [-wd WORKING]
```
```
Please provide the following arguments.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input: protein or peptide sequence in FASTA format
  -o OUTPUT, --output OUTPUT
                        Output: File for saving results by default outfile.csv
  -t THRESHOLD, --threshold THRESHOLD
                        Threshold: Value between 0 to 1 by default 0.48
  -m {1,2}, --model {1,2}
                        Model: 1: AAC feature based ExtraTrees Classifier , 2: AAC + PSSM feature based ExtraTrees Classifier, by default 1
  -d {1,2}, --display {1,2}
                        Display: 1:AFP, 2: All peptides, by default 2
  -wd WORKING, --working WORKING
                        Working Directory: Temporary directory to write files

```

**Input File**: It allow users to provide input in two format; i) FASTA format (standard) (e.g. seq.fasta)  

**Output File**: Program will save result in CSV format, in case user do not provide output file name, it will be stored in output_result.csv.


**Models**: In this program, two models have been incorporated;  
  i) Model1 for predicting given input protein sequence as R protein and non-R proteins  using SVC based on amino-acid composition of the proteins; 

  ii) Model2 for predicting given input peptide/protein sequence as R proteins and non-R protein using Hybrid approach, which is the ensemble of ET + BLAST. It combines the scores generated from machine learning (ET), and BLAST as Hybrid Score, and the prediction is based on Hybrid Score.


PlantDRPpred Package Files
=======================
It contain following files, brief description of these files given below

It contains the following files, brief description of these files given below

LICENSE : License information

README.md : This file provide information about this package

model : This folder contains two pickled models

plantdrppred.py : Main python program

possum : This folder contains the program POSSUM, that is used to calculate PSSM features

blastdb : Folder that contains the blast database of training dataset



