# googAuthRecover
This is a simple script that will recover and print out your QR codes for your backed up Google Authenticator or FreeOTP settings.

You should just run it with the bash script on your Google Authenticator backup database, or with the python script on the FreeOTP backup.

Get a backup with:
`adb backup org.fedorahosted.freeotp`
then run it with
`python3 recoverGoogAuth.py backup.ab`

`sudo apt install qrencode` for the bash script.  Check the head on the python script for required libraries.
