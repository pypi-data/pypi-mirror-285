# icreports

This project is a collection of tools and templates for generating reports at IHCEC.

# Contents #

## Latex Templates ##

### Technical Report ###

There is a sample Technical Report template in `meida/templates/latex/technical_report.tex`, which can be converted to a PDF with `pdflatex`.

### Gantt Chart ###

There is a sample Gantt Chart template in `media/templates/latex/gantt.tex`. It needs a few LaTeX packages for use:

``` shell
tlmgr install pgfgantt standalone helvetic
```

Then it can be used to generate a PDF with `pdflatex`.

# Copyright #

Copyright 2024 Irish Centre for High End Computing

The software in this repository can be used under the conditions of the GPLv3+ license, which is available for reading in the accompanying 
