# mrs-reviry-parser
This tool creates KML map from "soupis reviru" form MRS text file 
It allow also to use CRS sources, it had to be converted to txt via:


### As input there have to be reviry2.txt file

 It stores output to "output.kml" file , debug output goes to stderr
 
 `pdftotext -layout soupisy_mp_reviru_2016_2017.pdf output.txt`
 
 OR
 
 `oowriter --convert-to txt:Text input.docx`
 
Select your interest part and call code:

`./parser-exact.py  -i output.txt -o output.kml 2>output.error`

Usage:

 `$ ./parser-exact.py  -i output.txt -o output.kml`
