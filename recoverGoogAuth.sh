#!/bin/bash

for line in $(sqlite3 "$1" "select email,secret from accounts;")
do
  echo $line
  qrencode "$(echo $line | sed -e 's#\(.*\)|\(.*\)#otpauth://totp/\1?secret=\2#g')" -t ANSI
done
