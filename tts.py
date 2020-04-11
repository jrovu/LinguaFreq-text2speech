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
#     - ffmpeg (`brew install ffmpeg`)

# HOW TO INSTALL 
#-----------------------------
# 1. Git clone: `git clone https://github.com/Helicer/batch-text2speech.git`
# 2. Change to the directory `batch-text2speech.git`
# 3. Edit `sentences.txt`, put sentences you want to make speech for
# 4. Run the program with `./tts.py`

# HOW TO INSTALL 
#-----------------------------

import os
from datetime import datetime
import shutil



input_file = "sentences.txt"
output_dir = "_Output/"
voice_id = "Lupe" # Lupe (ES), Zhiyu (CN)
padding = 1 # How many seconds of silence at end of padded mp3s
voice_speed = 80 # percent



# Take line of text, and creates a text-to-speed audio file
def text_to_speech(text, filename):
    
    # SSML & Prosody allows us to control the rate of speed
    ssml_formatted_text = "<speak><prosody rate='{voice_speed}%'>{text}</prosody></speak>".format(voice_speed=voice_speed, text=text)
    
    # Build out command to call AWS Polly to generate speech files
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

    #print(polly_cmd) # Debug
    os.system(polly_cmd)



def create_output_directories():
    # Remove output from previous runs
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # Create directories for output
    os.mkdir(output_dir)
    print("Created directory: %s" % output_dir)



def tts_from_textfile(input_file):

    # Loop through the lines of text in a file
    with open(input_file, "r") as file:

        print("Opened file: " + input_file)

        for line in file:

            # Strip newlines from the lines
            stripped_line = line.strip()
            filename = stripped_line + ".mp3"


            print("-----------------")
            print("Processing: " + stripped_line)
            print("-----------------")

            # Call text_to_speech(stripped line, filename)
            text_to_speech(stripped_line, filename)



def main():
    print("-----------------")
    print("Text-to-speech using AWS Polly")
    startTime = datetime.now() # Timer

    create_output_directories()

    mode = "textfile"

    if mode is "textfile":
        print("Mode: Simple text file")
        tts_from_textfile(input_file)
    elif mode is "csv":
        print("Mode: CSV file")
        #tts_from_csv()
        pass



    # Timer
    completionTime = datetime.now() - startTime 
    print("-----------------")
    print("Completed time: ", str(completionTime))




if __name__ == "__main__":
    main()

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
# [_] <language 1> pause <language 2 / translation>
# [_] Control naming ( lang1, lang2)
# [_] Add padding equal to length of clip
# [X] "This should make the directories from scratch"
# [X] Adjustable Speed 
# [X] Wipe output folder each run
# [X] Add timer
# [_] Adjustable speed in CLI
# [_] "I should be able to specify a text file from the command line"
# [_] Background sounds eg coffee shop
