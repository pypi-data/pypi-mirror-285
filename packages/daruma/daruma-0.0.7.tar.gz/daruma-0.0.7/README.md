# Disorder order clAssifier by Rapid and User-friendly Machine, DARUMA

## Installation
### Install package
    pip install daruma


## USAGE
### Command Line Execution
    daruma [SEQUENCE FILE] -o [OUTPUT FILE]

SEQUENCE FILE : Path to fasta formatted file(supports both multi-fasta and single-fasta).

### Script Execution
```python=
import daruma

pred = daruma.predict( seq )
```
