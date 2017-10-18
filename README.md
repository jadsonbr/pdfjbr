# Introduction


# Requirements
Before running this tool you need to install:
- PyInstaller in version 3.2.1
- PyPDF2 in version 1.26.0


# Usage
Split the pdf `file.pdf` in several pdf files containing 5 pages each
```shell
pdfjbr split 5 file.pdf
```

Devide the pdf `file.pdf` in several pdf files of 3 MB
```shell
pdfjbr chunk 3 file.pdf outputDir
```

Split the pdf `file.pdf` in several pdf containing 1 page each (equivalent to `pdfjbr split 1 file.pdf`)
```shell
pdfjbr burst file.pdf
```

Merge 2 pdf files `f1.pdf` and `f2.pdf` into a single pdf file
```shell
pdfjbr merge f1.pdf f2.pdf                
```                

Merge all pdfs in the directory `dir` into a single output pdf file `output.pdf`
```shell
pdfjbr merge output.pdf dir
```

Display document information (size, page number, title, ...) of the pdf file `file.pdf`
```shell
pdfjbr info file.pdf
```

Display the number of pages of the pdf file `file.pdf`
```shell
pdfjbr pagecount file.pdf
```

