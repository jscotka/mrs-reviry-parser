#!/usr/bin/python3
import os.path
import sys
import re
import click
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import yaml

from selenium.webdriver.firefox.options import Options



def get_reviry_params(url):
    options = Options()
    options.set_preference('intl.accept_languages', 'cz-CZ, cz')

    driver = webdriver.Firefox(options=options)

    driver.get(url)
    output = dict()
    elements = driver.find_elements(By.XPATH, "//tr[contains(@id,'revir_')]")
    clicks = [x.get_attribute("onClick") for x in elements]
    for item in clicks:
        driver.execute_script(item)
        sleep(6)
        try:
            name = driver.find_element(By.TAG_NAME, "H3").text
        except NoSuchElementException:
            print("ERROR name:", item)
            continue
        allitems = driver.find_elements(By.TAG_NAME, "FIELDSET")
        desc = ""
        for field in allitems:
            if field.text.startswith("Popis"):
                desc = field.text
        mapy_link = ""
        try:
            mapy = driver.find_element(By.XPATH, "//a[contains(@href,'/inc/mapy.php')]")
            mapy_link = f"https://www.rybsvaz.cz/{mapy.get_attribute('href')}"
        except NoSuchElementException:
            print("ERROR MAPA:", item)
        output[name] = f"{desc}\n{mapy_link}"
        driver.back()
    return output

def strip_list(inp):
    output = []
    for item in inp:
        if item is not None:
            output.append(item.strip())

def revir_data(text, revir_name):
    jmeno = revir_name
    jmeno_add = ""
    GPS = {}
    for line in text.split("\n"):
        #print(">>:", line, file=sys.stderr)
        stripped_line = line.strip()
        print("REVIR:", jmeno, file=sys.stderr)

        # podrevir
        search = re.search('^\d+\..*ha', stripped_line)
        if search:
            jmeno_add = stripped_line
            print("NAME:", jmeno_add, file=sys.stderr)
            continue

        # reka
        search1 = re.search('^\(?GPS.*Z:(.+)K:(.+)', stripped_line)
        # rybnik
        search2 = re.search('^\(GPS(.*)', stripped_line)
        # ostani
        search3 = re.findall(r'GPS\S*\s+([^N]+N\S*\s+[^E]+E)', line)

        if search1:
            zacatek = search1.groups()[0].split("N")
            konec = search1.groups()[1].split("N")
            GPS[jmeno_add] = (convert(zacatek[0]), convert(zacatek[1]), convert(konec[0]), convert(konec[1]))
            print("adding reka", zacatek, konec, file=sys.stderr)
        elif search2:
            zacatek = search2.group(0).split("N")
            if len(zacatek) < 2:
                raise Exception(f"BAD GPS {zacatek}")
            GPS[jmeno_add] = (convert(zacatek[0]), convert(zacatek[1]))
            print("adding rybnik", zacatek)
        else:
            for item in search3:
                #print(">>>>>>>>>>>", search)
                zacatek = item.split("N")

                GPS[f"ZAKAZ ci RYBNIK: {item}"] = (convert(zacatek[0]), convert(zacatek[1]))
                print("ZAKAZ ci RYBNIK", zacatek, file=sys.stderr)
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
        for revir_name, data in reviry.items():
            count += 1
            for k, v in data['GPS'].items():
                outfile.write('<Placemark>\n')
                outfile.write(f'<name>{revir_name}</name>')
                description = data["data"]
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
@click.option("--url", "-u", default="https://www.rybsvaz.cz/pages_cz/reviry/reviry.php?page=reviry%2Freviry&lang=cz&fromIDS=&typ=mpr&id_svaz=7&id_r1=471")
@click.option("--outputfile", "-o", default="crs-reviry-mimopstruhove.kml")
@click.option("--quiet", "-q", is_flag=True, default=False)
def parser(url, outputfile, quiet):
    reviry = {}
    tempfile = f"{outputfile}.yaml"
    if os.path.exists(tempfile):
        with open(tempfile) as fd:
            data = yaml.safe_load(fd)
    else:
        data = get_reviry_params(url)
        with open(tempfile, "w") as fd:
            fd.write(yaml.safe_dump(data))
    for int_name, text in data.items():
        jmeno, GPS = revir_data(text, int_name)
        reviry[jmeno] = {'GPS': GPS, 'data': text}
    output_to_file(outputfile, reviry)



if __name__ == '__main__':
    parser()

