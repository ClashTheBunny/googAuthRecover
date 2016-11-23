#!/usr/bin/python3

import json
import base64
import xmltodict as xd
import qrcode
from termcolor import colored, cprint
import binascii
import sys
import tarfile

tarFilename = "data/data/org.fedorahosted.freeotp/./shared_prefs/tokens.xml"
abFilename = "data/data/org.fedorahosted.freeotp/./shared_prefs/tokens.xml"

def getTarObjectFromABBackup(filename):
    abHeaderReplacement = b"\x1f\x8b\x08\x00\x00\x00\x00\x00"
    ab = open(filename, 'rb')
    ab.seek(24)
    abf = io.BytesIO(abHeaderReplacement + ab.read())
    return tarfile.open(abf)

def getTarObjectFromTarBackup(filename):
    print(filename)
    return tarfile.open(filename)

def extractXMLFileFromTarObject(tarObj):
    return tarObj.extractfile(abFilename)

extensionSwitcher = {".ab": getTarObjectFromABBackup,
                     ".gz": getTarObjectFromTarBackup}

xmlFH = extractXMLFileFromTarObject(extensionSwitcher[sys.argv[1][-3:]](sys.argv[1]))

xmldata = xd.parse(xmlFH)

data = [json.loads(x['#text']) for x in xmldata['map']['string']]

for datum in data[:-1]:
    codeText = "otpauth://" + datum['type'].lower() + '/' + datum['label'] + '?secret=' + str(base64.b32encode( b''.join([x.to_bytes(1,'big',signed=True) for x in datum['secret']])))[2:-1]
    qrfactory = qrcode.QRCode(box_size=1)
    qrfactory.add_data(codeText)
    qrfactory.make(fit=True)
    img = qrfactory.make_image()
    pixels = list(img.getdata())
    pixMap = {0: "", 255: "reverse"}
    for pixel, value in enumerate(pixels):
        if pixel % img.height == 0:
            print()
        if value == 0:
            text = colored("  ", "white", attrs=[])
        else:
            text = colored("  ", "white", attrs=["reverse"])
        print(text,end="")
    print()
    print(codeText)
