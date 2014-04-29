# encoding: utf8

"""
Download Thru.de PRTR database and create
relationship triple file 'thrude.csv'.
More information: http://www.thru.de/thrude/downloads/
"""

import csv
import sqlite3
import urllib2
import zipfile
import os

# URL of latest file
URL = "http://www.thru.de/fileadmin/SITE_MASTER/content/Dokumente/Downloads/PRTR-Gesamtdatenbestand_stand_maerz2014.zip"


def download_url(url, filename):
    print("Downloading %s..." % URL)
    r = urllib2.urlopen(URL)
    data = r.read()
    f = open(filename, "wb")
    f.write(data)
    f.close()
    print("Downloaded %d MB, saved to %s" % (len(data) / 1024 / 1024, filename))


def extract_file(zippath, filepath, localpath):
    print("Extracting %s from %s to %s" % (filepath, zippath, localpath))
    with zipfile.ZipFile(zippath, "r") as myzip:
        myzip.extract(filepath)
        os.rename(filepath, localpath)
    os.rmdir(os.path.split(filepath)[0])


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

if __name__ == "__main__":
    zippath = "thrude_db.zip"
    dbpath = "thrude.sqlite3"
    output = "thrude.csv"
    download_url(URL, zippath)
    extract_file(zippath, "prtr-db/prtr.db", dbpath)
    os.remove(zippath)
    conn = sqlite3.connect(dbpath)
    conn.row_factory = dict_factory
    c = conn.cursor()
    with open(output, "wb") as csvfile:
        print("Writing to %s" % output)
        csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(["firma1", "beziehung", "firma2"])
        for row in c.execute("SELECT * FROM betriebe ORDER BY id"):
            #print row
            if row["muttergesellschaft"] is not None:
                csvwriter.writerow([
                    row["name"].encode("utf8"),
                    "hat die Muttergesellschaft",
                    row["muttergesellschaft"].encode("utf8")
                ])
            if row["betreiber"] is not None:
                if row["betreiber"] != row["muttergesellschaft"]:
                    csvwriter.writerow([
                        row["name"].encode("utf8"),
                        "hat den Betreiber",
                        row["betreiber"].encode("utf8")
                    ])
    c.close()
    conn.close()
    os.remove(dbpath)