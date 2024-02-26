# mrs-reviry-parser
This tool creates KML map from "soupis reviru" form MRS text file 
It allow also to use CRS sources, it had to be converted to txt via:

## New parser from web of MRS
 It is connected with page https://z.mrsbrno.cz/index.php/rybarske-reviry/ct-menu-item-12
It parse it and creates `KML` file as output eg.: `./parser-mrs-url.py` and stores KML file into predefined or user custom file

Full help:
```commandline
$ ./parser-mrs-url.py --help
Usage: parser-mrs-url.py [OPTIONS]

Options:
  -u, --url TEXT
  -o, --outputfile TEXT
  -q, --quiet
  --help                 Show this message and exit.

```


## New parser from web of CRS
It is connected with page for Severni Morava reviry https://www.rybsvaz.cz/pages_cz/reviry/reviry.php?page=reviry%2Freviry&lang=cz&fromIDS=&typ=mpr&id_svaz=7&id_r1=471

It parse it and creates `KML` file as output eg.: `./parser-crs-url.py` and stores KML file into predefined or user custom file.
(As side efect it also stores `YAML` file with raw data, because pages are highly dynamic, so unable to get data as in MRS, but used `selenium` so do not forget to install selenium dependencies for python)

```commandline
$ ./parser-crs-url.py --help
Usage: parser-crs-url.py [OPTIONS]

Options:
  -u, --url TEXT
  -o, --outputfile TEXT
  -q, --quiet
  --help                 Show this message and exit.

```
