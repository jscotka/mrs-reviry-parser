#!/usr/bin/python
# sed -i 's/GPS 2/GPS Z/g' reviry.txt
#

import os,sys,re

def convert(coor):
    #49'21'07.60
    translated = coor.replace("t", "1").replace("B", "8").replace("O", "0")
    output=0
    correct=""
    count=0

    found = re.search("(\d+)\D+(\d+)\D+(\d+)\D+(\d+)",translated)
    if found:
        output = float(found.group(1))+(float(found.group(2))/60.0)+((float(found.group(3))+float("0."+found.group(4)))/3600.0)
    else:
        print >> sys.stderr, "ERROR1:", coor
    return output

f = open('reviry2.txt', 'r')
count=1
reviry={}
revir = "X"
for foo in f:
    # 461 001 BALINKA 1 
    found_revir = re.search('([0-9]{3} +[0-9]{3})',foo)
    if found_revir:
        revir = found_revir.group(1)
        print >> sys.stderr,  revir
    if reviry.has_key(revir):
        # GPS Z: 49'21'07.60"N, 16'00'58.25"E, K: 49'23'36.27"N, 15'52'27.94"E
        textsplitted = [x for x in reviry[revir]['text'].split("\n") if len(x)>3]
        if textsplitted:
            multi = textsplitted[-1]
        else:
            multi = "---"
        if re.search('^\s*GPS.*Z.*K',foo):
            print >> sys.stderr,  "   reka: ",foo
            co=re.search('Z\S+\s+([^N]+)\S+\s+([^E]+)\S+\s+([^N]+)\S+\s+([^E]+)',foo)
            if co:
                reviry[revir]['GPS'].append([convert(co.group(1)), convert(co.group(2)), convert(co.group(3)), convert(co.group(4)), multi, foo])
                print >> sys.stderr,  convert(co.group(1)), convert(co.group(2)), convert(co.group(3)), convert(co.group(4))
            else:
                print >> sys.stderr,  "ERROR2", foo
                
        elif re.search('^\s*GPS',foo):
            print >> sys.stderr,  "   rybnik: ",foo
            co=re.search('\S+\s+([^N]+)\S+\s+([^E]+)',foo)
            if co:
                reviry[revir]['GPS'].append([convert(co.group(1)), convert(co.group(2)), multi, foo])
                #print convert(co.group(1)), convert(co.group(2))
            else:
                print >> sys.stderr,  "ERROR:", foo
        if len(foo)>3:
            reviry[revir]['text'] += foo.replace("<","").replace(">","")
    else:
        detail=re.search('[0-9]{3} +[0-9]{3} (\S+ \S+)(.*)',foo)
        reviry[revir] = {'id': revir, 'name':detail.group(1), 'org':detail.group(2), 'text':"", 'GPS':[]}

print  >> sys.stderr, '----------------------------------------------'
print  >> sys.stderr, " "
print '<?xml version="1.0" encoding="UTF-8"?>'
print '<kml xmlns="http://www.opengis.net/kml/2.2">'
print '<Document>'
print '<Style id="reka">'
print '<LineStyle>'
print '<color>ff0000</color>'
print '<width>4</width>'
print '</LineStyle>'
print '</Style>'
print '<Style id="rybnik">'
print '<IconStyle>'
print '<Icon>'
print '<href>http://www.iconsdb.com/icons/preview/soylent-red/star-5-xxl.png</href>'
print '</Icon>'
print '</IconStyle>'
print '</Style>'
for foo in reviry:
    for bar in reviry[foo]['GPS']:
        print '<Placemark>'
        print '<name>{0}: {1} :{2} </name>'.format(reviry[foo]['name'], reviry[foo]['id'],bar[-1])
        print '<description>{0}\n{1}\n{2}</description>'.format(bar[-2],reviry[foo]['org'], reviry[foo]['text'])
        if len(bar)==4:
            print '<styleUrl>#rybnik</styleUrl>'
            print '<Point> <coordinates>{0},{1}\n</coordinates> </Point>'.format(bar[1],bar[0])
        elif len(bar)==6:
            print '<styleUrl>#reka</styleUrl>'
            print '<LineString><tessellate>1</tessellate><coordinates>{0},{1},0.0\n{2},{3},0.0\n</coordinates> </LineString>'.format(bar[1],bar[0],bar[3],bar[2])
        print '</Placemark>'

print '</Document>'
print '</kml>'
