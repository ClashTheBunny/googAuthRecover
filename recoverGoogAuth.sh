#!/bin/bash

for line in $(sqlite3 "$1" "select email,secret from accounts;")
do
  qrencode "$(echo $line | sed -e 's#\(.*\)|\(.*\)#otpauth://totp/\1?secret=\2#g')" -o qrcode.png
  display qrcode.png &
  sleep 3
  rm qrcode.png
done
