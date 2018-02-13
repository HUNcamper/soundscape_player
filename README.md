# Written in Python 3.6.4

![Screenshot of the software](https://media.discordapp.net/attachments/238764565981036544/412983158296805387/unknown.png?width=470&height=325)

## About
This little tool/program can recognize and play Source Engine Soundscape scripts. Unpack them with GCFScape by opening the main VPK files, and checking the **scripts** folder, where the **soundscapes_*.txt** files are located. Load these files, and play them freely.
_Half-Life 2 soundscape scripts are included in the releases._

You also have to unpack the game's sound files by opening the main sound VPKs _(for Half-Life 2, it's called **hl2_sound_misc_dir.vpk**)_ and unpacking the **sound** folder. After unpacking it, copy and paste in the path of the folder into the program.

#### Python build dependencies:
* [PyGame](https://www.pygame.org)
* [tkinter](https://docs.python.org/2/library/tkinter.html) - preinstalled with Python most of the time

#### Recommended software:
* [GCFScape for unpacking soundscapes and sound files](http://nemesis.thewavelength.net/?p=26)

## Known issues:
* Soundscapes with positioned sound sources can act weird, since no 3D sound functionality is implemented yet. For example, the Dust 2 soundscape plays all the music from the map at the same time at the same position.
* No pitch change functionality is implemented yet, however, it's not really noticeable.
* References to other soundscape files aren't possible yet.
* Other left out functionalities

## Final notes:
The program is far from perfect, and probably has a ton of bugs. I'll probably fix these over the time, but if you can read the messy code, you can send in pull requests too.