#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys, re
import click
from html import parser
from urllib import request, response



def get_reviry_list(url, separator="<br />", match="""a href="/index.php/14-mimopstruhove-reviry/"""):
    output = []
    urlparser = request.urlparse(url)
    with request.urlopen(url) as basepage:
        htmlpage = basepage.read().decode()
        for item in htmlpage.split(separator):
            if match in item:
                rematch = re.search('href="([^"]+)"', item)
                if rematch:
                    output.append(f"{urlparser.scheme}://{urlparser.netloc}{rematch.groups()[0]}")
    return output

def parser_revir_page(url):
    with request.urlopen(url) as page:
        readed = page.read().decode()
        sep = """<article class="art-post">"""
        sep2 = """</article>"""
        tmp = readed.split(sep)[1].split(sep2)[0]
        tmp = re.sub(r"</div>", "\n", tmp)
        tmp = re.sub(r"</span>", " ", tmp)
        tmp = re.sub(r"<.?br[^>]+>", "\n", tmp)
        tmp = re.sub(r"<[^>]+>", " ", tmp)
        tmp = re.sub(r"&[^;]+;", "", tmp)
        return tmp

def strip_list(inp):
    output = []
    for item in inp:
        if item is not None:
            output.append(item.strip())

def revir_data(text):
    jmeno = ""
    jmeno_add = ""
    GPS = {}
    for line in text.split("\n"):
        #print(">>:", line, file=sys.stderr)
        stripped_line = line.strip()
        if not jmeno:
            jmeno = stripped_line
            jmeno_add = jmeno
            print("REVIR:", jmeno, file=sys.stderr)
            continue

        # podrevir
        search = re.search('^\d+\..*ha', stripped_line)
        if search:
            jmeno_add = stripped_line
            print("NAME:", jmeno_add, file=sys.stderr)
            continue

        # reka
        search = re.search('^GPS.*Z:(.+)K:(.+)', stripped_line)
        if search:
            zacatek = search.groups()[0].split("N")
            konec = search.groups()[1].split("N")
            GPS[jmeno_add] = (convert(zacatek[0]), convert(zacatek[1]), convert(konec[0]), convert(konec[1]))
            print("adding reka", zacatek, konec, file=sys.stderr)
            continue

        # rybnik
        search = re.search('^GPS(.*)', stripped_line)
        if search:
            zacatek = search.group(0).split("N")
            if len(zacatek) < 2:
                raise Exception(f"BAD GPS {zacatek}")
            GPS[jmeno_add] = (convert(zacatek[0]), convert(zacatek[1]))
            print("adding rybnik", zacatek)
            continue

        # misto ci zakaz
        search_all = re.findall(r'GPS\S*\s+([^N]+N\S*\s+[^E]+E)', line)
        for search in search_all:
            #print(">>>>>>>>>>>", search)
            zacatek = search.split("N")

            GPS[f"ZAKAZ ci RYBNIK: {search}"] = (convert(zacatek[0]), convert(zacatek[1]))
            print("ZAKAZ ci RYBNIK", zacatek, file=sys.stderr)
            continue
    return jmeno, GPS




def convert(coor):
    output = 0
    found = re.search(r"(\d+)\D+(\d+)\D+([0-9.]+)", coor)
    if found:
        output = float(found.group(1)) + (float(found.group(2)) / 60.0) + (float(found.group(3))) / 3600.0
    else:
        found = re.search(r"(\d+\.\d+)", coor)
        if found:
            output = float(found.group(1))
        else:
            print(sys.stderr, "ERROR convert coordinates:", coor, file=sys.stderr)
    return output


def output_to_file(filename, reviry):
    with open(filename, mode="w") as outfile:
        intro="""<?xml version="1.0" encoding="UTF-8"?>
                 <kml xmlns="http://www.opengis.net/kml/2.2">
                <Document>
    """
        modnum=1
        colors=["ff0000", "ffff00", "ff00ff", "990000", "99ff00", "9900ff", "ff9900", "ff0099", "550000", "55ff00", "5500ff"]
        for foo in range(0, modnum):
            intro +="""
                <Style id="reka{0}">
                    <LineStyle>
                    <color>ff{1}</color>
                    <width>4</width>
                    </LineStyle>
                </Style>
                <Style id="rybnik{0}">
                    <IconStyle>
                    <color>ff{1}</color>
                    <Icon><href>http://www.gstatic.com/mapspro/images/stock/1363-rec-fish.png</href></Icon>
                    </IconStyle>
                </Style>
                <Style id="nevim{0}">
                    <IconStyle>
                    <color>ff{1}</color>
                    <Icon><href>https://www.freeiconspng.com/img/41652</href></Icon>
                    </IconStyle>
                </Style>
                    """.format(foo, colors[foo])

        outfile.write(intro)

        count=0
        for revir_name, revir_data in reviry.items():
            count += 1
            for k, v in revir_data['GPS'].items():
                outfile.write('<Placemark>\n')
                outfile.write(f'<name>{revir_name}</name>')
                description = revir_data["data"]
                outfile.write(f'<description>\nJmeno: {k}\n\n{description}</description>')
                if "ZAKAZ" in k:
                    outfile.write('<styleUrl>#nevim{0}</styleUrl>\n'.format(count % modnum))
                    outfile.write('<Point> <coordinates>{0},{1}\n</coordinates> </Point>\n'.format(v[1], v[0]))
                elif len(v) == 2:
                    outfile.write('<styleUrl>#rybnik{0}</styleUrl>\n'.format(count%modnum))
                    outfile.write('<Point> <coordinates>{0},{1}\n</coordinates> </Point>\n'.format(v[1], v[0]))
                elif len(v) == 4:
                    outfile.write('<styleUrl>#reka{0}</styleUrl>\n'.format(count%modnum))
                    outfile.write('<LineString><tessellate>1</tessellate><coordinates>{0},{1}\n{2},{3}\n</coordinates> </LineString>\n'.format(v[1], v[0], v[3], v[2]))
                outfile.write('</Placemark>')
        outfile.write('</Document>\n')
        outfile.write('</kml>')


@click.command()
@click.option("--url", "-u", default="http://mrsbrno.cz/index.php/33-seznam-reviru/142-seznam-rybarskych-reviru-mimopstruhovych")
@click.option("--outputfile", "-o", default="outfile.kml")
@click.option("--quiet", "-q", is_flag=True, default=False)
def parser(url, outputfile, quiet):
    reviry = {}
    for item in get_reviry_list(url):
        text = parser_revir_page(item)
        jmeno, GPS = revir_data(text)
        reviry[jmeno] = {'GPS': GPS, 'data': text}
    output_to_file(outputfile, reviry)



if __name__ == '__main__':
    parser()
