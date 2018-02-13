import tkinter as tk
import pygame as pg
import tkinter.messagebox
import re
import time
import random
import threading
import os.path
import sys

from tkinter import filedialog

# --- REGEXES ---
regexQuote = r'"(.+)"'

# --- PYGAME MIXER ---
pg.mixer.init()
pg.init()
pg.mixer.set_num_channels(50)

# --- TKINTER ---
main = tk.Tk()

# --- GLOBAL VARS ---
soundScapes = []
playingSoundScape = False

# --- WIDGETS ---

# Listbox
lbList = tk.Listbox(main, width=100, height=20)

# Sound path label
lSoundPath = tk.Label(main, text="Root sound folder:")

# Now Playing label
labelText = tk.StringVar()
labelText.set("No soundscape playing.")
lPlaying = tk.Label(main, textvariable=labelText)

# Sound path textbox
tbSoundPath = tk.Text(main, height=1, width=50)
tbSoundPath.insert(tk.INSERT, "H:/GCFScape extract/HL2/sound")

# Load label
lLoad = tk.Label(main, text="Load soundscape file:")

# --- BUTTONS ---

# Load button
def LoadButton_Pressed():
	global soundScapes
	filePath = filedialog.askopenfilename()
	if not filePath == '':
		print("Selected file: {}".format(filePath))
		soundScapes = LoadSoundscape(filePath, lbList)
		main.title("Soundscape Player - {}".format(filePath.split("/")[-1]))

# Sound path help button
def SoundPathHelp_Pressed():
	tk.messagebox.showinfo("Help", "This is the path to the directory where all the game's sound files are located. You must extract these from the game's VPK files using GCFScape. (for example, for Half-Life 2, you can find the VPK file at C:/Program Files/Steam/steamapps/common/Half-Life 2/hl2/ called 'hl2_sound_misc_dir.vpk', extract this and you'll get a 'sound' folder. That's the folder that you have to select.)")

def PlayButton_Pressed():
	global playingSoundScape
	selected = lbList.get(lbList.curselection()[0]).strip()
	print("Playing: '{}'".format(selected))
	labelText.set("Playing: {}".format(selected))

	if not playingSoundScape == False:
		for obj in playingSoundScape.objects:
			obj.Stop()
	
	playingSoundScape = GetSoundScape(selected)

def StopButton_Pressed():
	global playingSoundScape
	if not playingSoundScape == False:
		for obj in playingSoundScape.objects:
			obj.Stop()

	playingSoundScape = False
	labelText.set("No soundscape playing.")

# Load button
bLoad = tk.Button(main, text="Browse...", command=LoadButton_Pressed)

# Sound path help button
bSoundPathHelp = tk.Button(main, text="?", command=SoundPathHelp_Pressed, width=2)

# Play button
bPlay = tk.Button(main, text="Play Soundscape", command=PlayButton_Pressed)

# Stop button
bStop = tk.Button(main, text="Stop Soundscape", command=StopButton_Pressed)



# --- FUNCTIONS ---
def MainTimer(stopEvent):
	if not playingSoundScape == False:
		for obj in playingSoundScape.objects:
			obj.Play()

	if not stopEvent.is_set():
		threading.Timer(1, MainTimer, [stopEvent]).start()

def GetSoundScape(name):
	for ss in soundScapes:
		if ss.name == name:
			return ss
	return False

def GetPath(add=""):
	path = GetTBText(tbSoundPath)
	if not path.endswith("/") and not path.endswith("\\"):
		path += "/"

	if not add == "":
		if add.startswith("*") or add.startswith("#") or add.startswith(")"):
			add = add [ 1 : ]
		while add.startswith("/") or add.startswith("\\"):
			path = path[1 : ]

	return path+add

def GetTBText(textbox):
	return textbox.get("1.0", tk.END).strip()

def LoadSoundscape(fname, listbox):
	listbox.delete(0, tk.END)
	soundscapes = [] # soundscape list
	soundScape = False
	obj = False

	depth = 0 # depth in script

	with open(fname) as f:

		for line in f:
			line = line.strip() # stripping endlines

			if depth == 0 and line.startswith('"'):
				ssName = re.match(regexQuote, line).group(1)
				print("Found soundscape: {}".format(ssName))
				listbox.insert(listbox.size()+1, ssName)

				if not soundScape == False:
					if not obj == False:
						soundScape.objects.append(obj)
					soundscapes.append(soundScape)

				obj = False
				soundScape = SoundScape(ssName)

			elif depth == 1 and line.startswith('"playrandom"') or line.startswith('"playlooping"') or line.startswith('"playsoundscape"'):
				if not soundScape == False and not obj == False:
					soundScape.objects.append(obj)

				ssName = RegExMatchGroup(regexQuote, line)
				obj = SoundScapeObj(ssName)

			if depth == 2 and line.startswith('"volume"'):
				print("VOLUME")
				volume = RegExMatchGroup(regexQuote, line.replace('"volume"', "").strip()).split(",")
				obj.volume = []

				for a in volume:
					if a.startswith("."):
						a = "0" + a
					obj.volume.append(float(a))

			elif depth == 1 and line.startswith('"pitch"'):
				print("PITCH")
				pitch = RegExMatchGroup(regexQuote, line.replace('"pitch"', "").strip()).split(",")
				obj.pitch = []
				
				for a in pitch:
					obj.pitch.append(float(a))

			elif depth == 2 and line.startswith('"time"'):
				print("TIME")
				time = RegExMatchGroup(regexQuote, line.replace('"time"', "").strip()).split(",")
				obj.time = []
				
				for a in time:
					a = a.replace("`", "")
					obj.time.append(int(float(a.strip())))

				obj.GenPlayTime()

			elif depth == 2 and line.startswith('"wave"'):
				print("WAVE")
				sound = RegExMatchGroup(regexQuote, line.replace('"wave"', "").strip())
				obj.wave = sound
				print("Adding looped sound {}".format(sound))

			elif depth == 2 and line.startswith('"name"'):
				print("SOUNDSCAPE")
				ss = RegExMatchGroup(regexQuote, line.replace('"name"', "").strip())
				obj.soundscape = ss
				print("Adding soundscape reference {}".format(ss))

			elif depth == 3 and line.startswith('"wave"'):
				sound = RegExMatchGroup(regexQuote, line.replace('"wave"', "").strip())
				obj.contents.append(sound)
				print("Adding random sound {}".format(sound))

			if line.startswith("{"):
				depth += 1
			elif line.startswith("}"):
				depth -= 1
	
	if not soundScape == False:
		if not obj == False:
			soundScape.objects.append(obj)
		soundscapes.append(soundScape)

	return soundscapes

def RegExMatchGroup(regex, string):
	return re.match(regex, string.strip()).group(1)


# --- Classes ---
class SoundScape:
	def __init__(self, name):
		self.name = name
		self.objects = []
		self.volume = 1

class SoundScapeObj:
	def __init__(self, sstype=""):
		self.type = sstype
		self.volume = [1,1]
		self.pitch = [100,100]
		self.time = [1,1]
		self.playtime = 1
		self.contents = []
		self.wave = ""
		self.soundscape = "" # soundscape to play
		self.playing = False
		self.seconds = 0
		self.globalvolume = 1
		self.sound = False
		self.isMusic = False

	def GenPlayTime(self):
		try:
			self.playtime = random.randint(self.time[0], self.time[1])
			if self.playtime < 1:
				self.playtime = 1
		except Exception:
			self.playtime = self.time[0]

	def Stop(self):
		if self.playing:
			if not self.sound == False:
				self.sound.stop()
			elif self.isMusic:
				pg.mixer.music.stop()
			self.playing = False

	def Play(self):
		if self.type == "playrandom":
			self.seconds += 1
			if self.seconds % self.playtime == 0:
				fname = random.choice(self.contents)
				if os.path.isfile(GetPath(fname)):
					try:
						self.sound = pg.mixer.Sound(GetPath(fname))
					except Exception as e:
						print("Failed to play {}: {}".format(fname, e))
					
					try:
						volume = random.uniform(self.volume[0], self.volume[1]) * self.globalvolume
					except Exception:
						volume = float(self.volume[0]) * self.globalvolume
					self.sound.set_volume(volume)
					self.sound.play()
					print("Playing {}".format(fname))
					self.GenPlayTime()
					self.seconds = 0
				else:
					print("Failed to play sound {}, it doesn't exist".format(fname))
		elif self.type == "playlooping" and not self.playing:
			if os.path.isfile(GetPath(self.wave)):
				volume = float(self.volume[0]) * self.globalvolume
				if not self.wave.endswith(".mp3"):
					print("Looping {}".format(self.wave))
					self.sound = pg.mixer.Sound(GetPath(self.wave))
					self.sound.play(-1)
				else:
					print("Playing music {}".format(self.wave))
					pg.mixer.music.load(GetPath(self.wave))
					pg.mixer.music.play()
					self.isMusic = True
				self.playing = True
			else:
				print("Failed to play sound {}, it doesn't exist".format(self.wave))
		elif self.type == "playsoundscape" and not self.playing:
			global playingSoundScape
			soundscape = GetSoundScape(self.soundscape)
			if not soundscape == False:
				print("Playing soundscape '{}'".format(soundscape.name))
				for o in soundscape.objects:
					obj = o
					obj.globalvolume = self.volume[0]
					playingSoundScape.objects.append(obj)
				self.playing = True
			else:
				print("Failed to play soundscape '{}': Not found".format(self.soundscape))

# --- PROTOCOLS ---
def onClose():
	stopEvent.set()
	main.destroy()
	sys.exit()
main.protocol("WM_DELETE_WINDOW", onClose)

# --- WIDGET PLACEMENT ---

lLoad.grid(row=0, column=0)
bLoad.grid(row=0, column=1)
lSoundPath.grid(row=1, column=0)
tbSoundPath.grid(row=1, column=1)
bSoundPathHelp.grid(row=1, column=2)
lbList.grid(row=3, columnspan=3)
bPlay.grid(row=4, column=0)
lPlaying.grid(row=4, column=1)
bStop.grid(row=4, column=2)

stopEvent = threading.Event()
MainTimer(stopEvent)

main.resizable(False, False)
main.title("Soundscape Player")

main.mainloop()