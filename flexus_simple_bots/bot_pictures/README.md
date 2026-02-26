# Bot Pictures


This directory contains scripts for generating and processing bot avatar images.
optimizing them for web use with compression and format conversion.

Generate initial images from text prompts:

`python flexus_simple_bots/bot_pictures/_pictures_generate.py -f _frogs.txt -o _new_bot_pics`


Make a webp version:

`python flexus_simple_bots/bot_pictures/_convert_to_webp.py _new_bot_pics`


Convert them to avatar format with bigger face:

`python flexus_simple_bots/bot_pictures/_pictures_to_avatars.py _new_bot_pics`
