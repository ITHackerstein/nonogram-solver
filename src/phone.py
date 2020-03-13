import subprocess
import psutil
import time
import re
import os
import platform
from PIL import Image

if platform.system() == "Windows":
	ADB_RUNTIME = f"{os.environ['SYSTEMDRIVE']}\\adb\\adb.exe"
elif platform.system() == "Linux":
	ADB_RUNTIME = "adb"

def parse_evt(evt):
	return re.sub(r' {2,}', ' ', evt.replace('[', '').replace(']', '').strip()).split(" ")

# Sample touch input
# [  696772.147087] EV_ABS       ABS_PRESSURE         0000007f
# [  696772.147087] EV_ABS       ABS_MT_POSITION_X    00000203
# [  696772.147087] EV_ABS       ABS_MT_POSITION_Y    0000040b
# [  696772.147087] EV_ABS       ABS_MT_TRACKING_ID   00000000
# [  696772.147087] EV_ABS       ABS_MT_TOUCH_MAJOR   00000090
# [  696772.147087] EV_SYN       SYN_MT_REPORT        00000000
# [  696772.147087] EV_SYN       SYN_REPORT           00000000
# [  696772.157883] EV_ABS       ABS_MT_POSITION_X    00000203
# [  696772.157883] EV_ABS       ABS_MT_POSITION_Y    0000040b
# [  696772.157883] EV_ABS       ABS_MT_TRACKING_ID   00000000
# [  696772.157883] EV_ABS       ABS_MT_TOUCH_MAJOR   00000090
# [  696772.157883] EV_SYN       SYN_MT_REPORT        00000000
# [  696772.157883] EV_SYN       SYN_REPORT           00000000
# [  696772.168659] EV_ABS       ABS_MT_POSITION_X    00000203
# [  696772.168659] EV_ABS       ABS_MT_POSITION_Y    0000040b
# [  696772.168659] EV_ABS       ABS_MT_TRACKING_ID   00000000
# [  696772.168659] EV_ABS       ABS_MT_TOUCH_MAJOR   00000090
# [  696772.168659] EV_SYN       SYN_MT_REPORT        00000000
# [  696772.168659] EV_SYN       SYN_REPORT           00000000
# [  696772.179181] EV_ABS       ABS_MT_POSITION_X    00000203
# [  696772.179181] EV_ABS       ABS_MT_POSITION_Y    0000040b
# [  696772.179181] EV_ABS       ABS_MT_TRACKING_ID   00000000
# [  696772.179181] EV_ABS       ABS_MT_TOUCH_MAJOR   00000090
# [  696772.179181] EV_SYN       SYN_MT_REPORT        00000000
# [  696772.179181] EV_SYN       SYN_REPORT           00000000
# [  696772.189785] EV_SYN       SYN_MT_REPORT        00000000
# [  696772.189785] EV_SYN       SYN_REPORT           00000000

class ADB:
	def __init__(self):
		for proc in psutil.process_iter():
			if proc.name() == 'adb' or proc.name() == 'adb.exe':
				break
		else:
			subprocess.run([ADB_RUNTIME, "start-server"])
		self.set_touch_device()

	def kill_server(self):
		subprocess.run([ADB_RUNTIME, "kill-server"])

	def device_connected(self):
		p = subprocess.Popen([ADB_RUNTIME, "devices"], stdout=subprocess.PIPE)
		devices = p.communicate()[0].decode("ascii").strip().split("\n")[1:]

		if len(devices) != 1:
			return False

		return devices[0].split("\t")[1] == "device"

	def set_touch_device(self):
		assert self.device_connected(), "Make sure there is ONLY ONE device connected!"
		p = subprocess.Popen([ADB_RUNTIME, "shell", "getevent", "-lp"], stdout=subprocess.PIPE)
		lines = p.communicate()[0].decode("ascii").strip().split("\n")
		device_name = ""
		found = False
		for line in lines:
			line = line.strip()
			if "add device" in line:
				start = len(line) - 1
				while line[start] != ' ':
					start -= 1
				device_name = line[start + 1:]
				continue
			if "MT" in line:
				found = True
				break
		assert found, "Touch device not found!"
		self.touch_device = device_name

	def get_touch_inputs(self, time_range=5):
		assert self.device_connected(), "Make sure there is ONLY ONE device connected!"
		p = subprocess.Popen([ADB_RUNTIME, "shell", "getevent", "-lt", self.touch_device], stdout=subprocess.PIPE)
		time.sleep(time_range)
		p.terminate()

		out = p.communicate()[0].decode("ascii")

		if out == "":
			return []

		inputs = [l.strip() for l in out.strip().split("\n")]

		res = []

		i = 0
		while i < len(inputs):
			cur_evt = parse_evt(inputs[i])
			type_ = cur_evt[2]
			if type_ == "ABS_MT_POSITION_X":
				i += 1
				next_evt = parse_evt(inputs[i])
				x_value = int(cur_evt[3], 16)
				y_value = int(next_evt[3], 16)
				res.append([x_value, y_value])
			i += 1

		return res

	def get_screen(self):
		assert self.device_connected(), "Make sure there is ONLY ONE device connected!"
		DEV_NULL = open(os.devnull, "w")
		subprocess.run([ADB_RUNTIME, "shell", "screencap", "/sdcard/screen.png"], stdout=DEV_NULL, stderr=subprocess.STDOUT)
		subprocess.run([ADB_RUNTIME, "pull", "/sdcard/screen.png"], stdout=DEV_NULL, stderr=subprocess.STDOUT)
		subprocess.run([ADB_RUNTIME, "shell", "rm", "/sdcard/screen.png"], stdout=DEV_NULL, stderr=subprocess.STDOUT)
		ret = Image.open("screen.png")
		DEV_NULL.close()
		return ret

	def send_file(self, src, dest):
		assert self.device_connected(), "Make sure there is ONLY ONE device connected!"
		subprocess.run([ADB_RUNTIME, "push", src, dest])

	def run_command(self, cmd):
		assert self.device_connected(), "Make sure there is ONLY ONE device connected!"
		subprocess.run([ADB_RUNTIME, "shell", cmd])
