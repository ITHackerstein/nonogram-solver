from phone import ADB
import sys

size, rules_off = 600, 100
FPS = 60

if len(sys.argv) > 1 and sys.argv[1] == "PHONE":
	adb = ADB()
