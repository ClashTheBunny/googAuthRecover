#!/usr/bin/python3

import json
import base64
import xmltodict as xd
import qrcode
from termcolor import colored, cprint
import binascii
import sys
import tarfile
import io
import pprint as pp
import subprocess
import urllib
import os

filenameSwitcher = {".gz": "data/data/org.fedorahosted.freeotp/./shared_prefs/tokens.xml",
                    ".ab": "apps/org.fedorahosted.freeotp/sp/tokens.xml"} # I'm actually not sure what it is in the android backup, probably needs a prefix.

def getTarObjectFromABBackup(filename):
    abHeaderReplacement = b"\x1f\x8b\x08\x00\x00\x00\x00\x00"
    ab = open(filename, 'rb')
    ab.seek(24)
    abf = abHeaderReplacement + ab.read()
    tar = open(filename[:-3] + ".tar.gz", 'wb')
    tar.write(abf)
    tar.close()
    return tarfile.open(filename[:-3] + ".tar.gz")

def getTarObjectFromTarBackup(filename):
    print(filename)
    return tarfile.open(filename)

def extractXMLFileFromTarObject(tarObj,backupExtension):
    return tarObj.extractfile(filenameSwitcher[backupExtension])

backupFile = sys.argv[1]
backupExtension = sys.argv[1][-3:]

extensionSwitcher = {".ab": getTarObjectFromABBackup,
                     ".gz": getTarObjectFromTarBackup}

xmlFH = extractXMLFileFromTarObject(extensionSwitcher[backupExtension](backupFile), backupExtension)

xmldata = xd.parse(xmlFH)

data = [json.loads(x['#text']) for x in xmldata['map']['string']]

for datum in data[:-1]:
    pp.pprint(datum)
    if type(datum) == list:
        continue
    # issuerExt = ''
    # issuerExtTemplate = ''
    # if 'issuerExt' in datum and len(datum['issuerExt']) > 0:
    #     issuerExt=datum['issuerExt']
    #     issuerExtTemplate = '?issuer={issuerExt}'
    issuerInt = ''
    issuerIntTemplate = ''
    if 'issuerInt' in datum and len(datum['issuerInt']) > 0:
        issuerInt=datum['issuerInt']
        issuerIntTemplate = '{issuerInt}:'
    secret=str(base64.b32encode( b''.join([x.to_bytes(1,'big',signed=True) for x in datum['secret']])))[2:-1]
    codeTextTempl = "otpauth://{type}/" + issuerIntTemplate + "{label}?secret={secret}" # + issuerExtTemplate
    codeText = codeTextTempl.format(type=datum['type'].lower(),label=datum['label'],secret=secret,issuerInt=issuerInt) #,issuerExt=issuerExt)
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
    print(codeText.replace(" ", "%20"))
    if os.environ.get('PASSWORD_STORE_DIR'):
        env={"PASSWORD_STORE_DIR": os.environ.get('PASSWORD_STORE_DIR')}
    else:
        env={}
    subprocess.run("pass otp insert " + issuerIntTemplate.format(issuerInt=issuerInt).replace(":","/") + datum['label'], env=env, shell=True, input=codeText.replace(" ", "%20"), encoding='ascii')
