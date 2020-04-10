#!/usr/bin/env python3

# Name: Batch Text-to-speech
# Author: Jonathan Rogivue
# Last updated: 2020-04-10
#----------------------------- 


# USER STORY: 
#-----------------------------
# "As a language learner, 
# I should be able to quickly convert a text file of sentences into audio files, 
# so that I can practice listening to them"


# TECHNICAL OVERVIEW:
#-----------------------------
# This script uses AWS Polly (text-to-speech engine), to create individual MP3 files from lines of text in a file


# PREREQUISITES:
#-----------------------------
# - AWS account (https://aws.amazon.com/)
#     - Account with AWS Polly permission
# - Mac homebrew (https://brew.sh/)
#     - git (`brew install git`)
#     - aws CLI (`brew install awscli`)
#     - python3 (`brew install python3`)

# HOW TO INSTALL & USE:
#-----------------------------
# 1. Git clone: `git clone https://github.com/Helicer/batch-text2speech.git`
# 2. Change to the directory `batch-text2speech.git`
# 3. Edit `sentences.txt`, put sentences you want to make speech for
# 4. Run the program with `./tts.py`

import os

input_file = "sentences.txt"
output_dir = "_Output/"
padded_dir = output_dir + "padded/"
voice_id = "Lupe" # Lupe (ES), Zhiyu (CN)
padding = 1 # How many seconds of silence at end of padded mp3s
voice_speed = 50 # percent

print("Text to Speech using AWS Polly")


# Create directories for output
if not os.path.exists(output_dir):
	os.mkdir(output_dir)
	print("Created directory: %s" % output_dir)

	os.mkdir(padded_dir)
	print("Created directory: %s" % padded_dir)



with open(input_file, "r") as file:

	print("Opened file: " + input_file)

	for line in file:

		# Strip newlines from the lines
		stripped_line = line.strip()
		filename = stripped_line + ".mp3"

		print("-----------------")
		print("Processing: " + stripped_line)
		print("-----------------")

		# SSML & Prosody allows us to control the rate of speed
		ssml_formatted_text = "<speak><prosody rate='{voice_speed}%'>{stripped_line}</prosody></speak>".format(voice_speed=voice_speed, stripped_line=stripped_line)
		#print(ssml_formatted_text) # Debug
		
		# Build command for AWS Polly
		polly_cmd = '''
			aws polly synthesize-speech \
		   --output-format mp3 \
		   --text-type ssml \
		   --voice-id {voice_id} \
		   --text "{ssml_formatted_text}" \
		   "{output_dir}{filename}"
		'''.format(voice_id=voice_id, \
			ssml_formatted_text=ssml_formatted_text, \
			output_dir=output_dir, \
			filename=filename)
		
		# print(polly_cmd) # Debug
		os.system(polly_cmd)
		


		ffmpeg_cmd = '''
		ffmpeg -i "{output_dir}{filename}" -y -af -hide_banner -loglevel panic "apad=pad_dur=1" "{padded_dir}{filename}"
		'''.format(output_dir=output_dir, filename=filename, padded_dir=padded_dir)
		
		# print(ffmpeg_cmd) # Debug
		os.system(ffmpeg_cmd)
		


#-------------------------------
#       Information
#-------------------------------


# Polly Console: https://console.aws.amazon.com/polly/home/SynthesizeSpeech
# Polly Voice ID list: https://docs.aws.amazon.com/polly/latest/dg/voicelist.html
# - Chinese: "Zhiyu"
# - Spanish: "Lupe"

# POLLY EXAMPLE
#aws polly synthesize-speech \ 
#    --output-format mp3 \
#    --voice-id Joanna \
#    --text 'Hello, my name is Joanna. I learned about the W3C on 10/3 of last year.' \
#    hello.mp3

# CHANGE VOICE SPEED EXAMPLE
#--text-type ssml
#--text "<speak><prosody rate='50%'>这个人好是好，就是不适合</prosody></speak>"



#-------------------------------
#       Wishlist / TODO
#-------------------------------
# [_] "I should be able to specify a text file from the command line"
# [X] "This should make the directories from scratch"
# [_] Add padding equal to length of clip
# [X] Adjustable Speed 
# [_] Adjustable speed in CLI
# [_] Background sounds eg coffee shop
