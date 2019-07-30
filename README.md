# mrs-reviry-parser
This tool creates KML map from "soupis reviru" form MRS text file 
It allow also to use CRS sources, it had to be converted to txt via:

## New parser from web of MRS
 It it connected with page http://mrsbrno.cz/index.php/kontakty/33-seznam-reviru/142-seznam-rybarskych-reviru-mimopstruhovych
It parse it and creates `KML` file as output eg.: `./parser-mrs-url.py -o output.kml
`

Full help:
```
$ ./parser-mrs-url.py --help
Usage: parser-mrs-url.py [OPTIONS]

Options:
  -u, --url TEXT
  -o, --outputfile TEXT
  -q, --quiet
  --help                 Show this message and exit.

```


### As input there have to be reviry2.txt file

 It stores output to "output.kml" file , debug output goes to stderr
 
 `pdftotext -layout soupisy_mp_reviru_2016_2017.pdf output.txt`
 
 OR
 
 `oowriter --convert-to txt:Text input.docx`
 
Select your interest part and call code:

 `./parser-exact.py  -i output.txt -o output.kml 2>output.error`

Usage:
```
 $ ./parser-exact.py --help
Usage: parser-exact.py [options]

Options:
  -h, --help            show this help message and exit
  -i FILEINPUT, --input=FILEINPUT
                        read input file
  -o FILEOUTPUT, --output=FILEOUTPUT
                        write results to file
  -q, --quiet           don't print debug messages

```

