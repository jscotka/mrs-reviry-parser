#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys,re
from optparse import OptionParser

parser = OptionParser()
parser = OptionParser()
parser.add_option("-i", "--input", dest="fileinput",
                  help="read input file")
parser.add_option("-o", "--output", dest="fileoutput",
                  help="write results to file")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print debug messages")
options, args = parser.parse_args()

infile = open(options.fileinput, 'r')
outfile = open(options.fileoutput, 'w')

def convert(coor):
    output=0
    found = re.search("(\d+)\D+(\d+)\D+([0-9.]+)",coor)
    if found:
        output = float(found.group(1))+(float(found.group(2))/60.0)+(float(found.group(3)))/3600.0
    else:
        print >> sys.stderr, "ERROR convert coordinates:", coor
    return output


count=1
preamble=True
reviry={}
revir = "X"
multi=""
for xxx in infile:
    foo = xxx.replace("–","-").replace(" "," ").replace("\t"," ").replace("<","").replace(">","")
    if preamble:
        if re.search('REV.*RY.*PSTRUHOV.*', foo):
            preamble=False
        continue
    # 461 001 BALINKA 1 
    found_revir = re.search('(^[(\[\s]*\d{3}\D+\d{3})',foo)
    if found_revir:
        revir = found_revir.group(1)
        print "Actual Revir:", revir
    if reviry.has_key(revir):
        if re.search('^\s*GPS.*Z.*K',foo):
            print "   reka: ",foo
            co=re.search('Z\S+\D+([^N]+)\S+\D+([^E]+)\S+\D+([^N]+)\S+\D+([^E]+)',foo)
            if co:
                reviry[revir]['GPS'].append([convert(co.group(1)), convert(co.group(2)), convert(co.group(3)), convert(co.group(4)), multi, foo])
                print "adding reka:", revir, convert(co.group(1)), convert(co.group(2)), convert(co.group(3)), convert(co.group(4))
            else:
                print >> sys.stderr, "ERROR unable to find all GPS revir:{0} (reka): {1}".format(revir, foo)
                
        elif re.search('^\s*GPS',foo):
            print "   rybnik: ", foo
            co=re.search('\S+\s+([^N]+)\S+\s+([^E]+)',foo)
            if co:
                reviry[revir]['GPS'].append([convert(co.group(1)), convert(co.group(2)), multi, foo])
                print "adding rybnik:", revir, convert(co.group(1)), convert(co.group(2))
            else:
                print >> sys.stderr,  "ERROR unable to find all GPS revir:{0} (rybnik): {1}".format(revir, foo)
        elif re.search('\s*\S+\s+.*GPS',foo):
            print >> sys.stderr,  "WARN: GPS used inside revir:{0} text:{1}".format(revir, foo)
        reviry[revir]['text'] += foo
    elif re.search('\d{3}\s+\d{3}\s+([^-]*)(.*)',foo):
        print  "NEW REVIR:", foo
        detail = re.search('\d{3}\s+\d{3}\s+([^-]*)(.*)',foo)
        reviry[revir] = {'id': revir, 'name':detail.group(1), 'org':detail.group(2), 'text':"", 'GPS':[]}
    multi = foo.strip()

intro="""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
"""
modnum=10
for foo in range(0,modnum):
    color=""
    for bar in range(1,5):
        if foo%bar == 0:
            color+=str(foo)
        else:
            color+="0"
    intro +="""
    <Style id="reka{0}">
    <LineStyle>
    <color>ffff{1}</color>
    <width>4</width>
    </LineStyle>
    </Style>
    <Style id="rybnik{0}">
    <IconStyle>
    <color>ffff{1}</color>
    <Icon><href>http://www.gstatic.com/mapspro/images/stock/1363-rec-fish.png</href></Icon>
    </IconStyle>
    </Style>
""".format(foo, color)

outfile.write(intro)

count=0
for foo in reviry:
    if len(reviry[foo]['GPS'])==0:
        print >> sys.stderr,  "ERROR: no GPS for {0}: {1}: {2}\ndetails:\n{3}".format(foo,reviry[foo]['name'],reviry[foo]['org'], reviry[foo]['text'])
    else:
        count += 1
    for bar in reviry[foo]['GPS']:
        outfile.write('<Placemark>\n')
        outfile.write('<name>{0}: {1}: {2}</name>'.format(reviry[foo]['name'], reviry[foo]['id'], bar[-1]))
        # CDATA not supported on google maps
        #outfile.write('<description>\n<![CDATA[\n<h1>{0}</h1>\n<p>{1}</p>\n<pre>{2}</pre>\n]]>\n</description>\n'.format(bar[-2],reviry[foo]['org'], reviry[foo]['text']))
        outfile.write('<description>\nJmeno: {0}\n\nOrganizace: {1}\nPodrobny popis:\n{2}</description>\n'.format(bar[-2], reviry[foo]['org'], reviry[foo]['text']))
        if len(bar)==4:
            outfile.write('<styleUrl>#rybnik{0}</styleUrl>\n'.format(count%modnum))
            outfile.write('<Point> <coordinates>{0},{1}\n</coordinates> </Point>\n'.format(bar[1],bar[0]))
        elif len(bar)==6:
            outfile.write('<styleUrl>#reka{0}</styleUrl>\n'.format(count%modnum))
            outfile.write('<LineString><tessellate>1</tessellate><coordinates>{0},{1}\n{2},{3}\n</coordinates> </LineString>\n'.format(bar[1],bar[0],bar[3],bar[2]))
        outfile.write('</Placemark>')

outfile.write('</Document>\n')
outfile.write('</kml>')
outfile.close()
infile.close()

