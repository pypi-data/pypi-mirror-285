# This is a bioinformatic python package.

## Install
```shell
pip install pybioinformatic --upgrade
```

## Usage example
### RNA secondary structure prediction.
```python
from pybioinformatic import Nucleotide

# Generate random nucleic acid sequence.
random_nucl = Nucleotide.random_nucl(name='demo', length=[100, 150], bias=1.0)

# Secondary structure prediction
ss, mfe = random_nucl.predict_secondary_structure('test/structure.ps')
print(ss, mfe, sep='\n')
```
```
>demo length=135
CAAAAAAAAACCATAAGCCGCCATGTCTCACATCGCAACCGGCTCAAGTAGAGTGCCCCTAATAATATGATCTTCGCTACAGAAGTTCCCCCCCCGCTGCCGGCTAGATGCGAACTCCACGCCTGGATGGCTCAG
...............((((((((.((......(((((.(.((((...((((.................((.((((......)))).))........)))).)))).).))))).......)).))).)))))...
-27.299999237060547
```
![image](test/structure.png)
