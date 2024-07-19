# ratesb_web: Rate Law Analysis for SBML and Antimony Models

`ratesb_web` is the python backend support for ratesb. Basically it removes all the packages using c++ so that `ratesb_web` can be embedded in ratesb website. To use ratesb in python, please install [ratesb_python](https://github.com/sys-bio/ratesb_python).

## Installation

`ratesb_web` is not designed for python useage, but if you would like a pure python package, to install `ratesb_web`, execute the following command in your terminal:

```bash
pip install ratesb_web
```

## Versions

0.1.0: initial release, prepared for integration with RateSB
0.1.1: fixed classifier file path problem

## Development

Once a new version of `ratesb_python` is released, copy and paste all codes except for reaction_data.py (preprocessing the model data is different). Adjust testing accordingly. 

Ideally we would like the same testing files for the two packages, but to achieve that we need python-libsbml and antimony, which are c++ based packages that cannot be used here. Working on a solution...

## License

`ratesb_web` is licensed under the MIT license. Please see the LICENSE file for more information.

## Contact

For additional queries, please contact Longxuan Fan at longxuan@usc.edu.