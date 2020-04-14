#!/usr/bin/env python3

# Name: Batch Text-to-speech
# Author: Jonathan Rogivue
# Last updated: 2020-04-14
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
# - `awscli` configured (`aws comfigure`) with correct user


# HOW TO INSTALL 
#-----------------------------
# 1. Git clone: `git clone https://github.com/Helicer/batch-text2speech.git`
# 2. Change to the directory `batch-text2speech.git`
# 3. Edit `sentences.txt`, put sentences you want to make speech for
# 4. Run the program with `./tts.py`
#
# GET HELP by running `tts.py -h`


import os
from datetime import datetime
import shutil
import csv
import argparse 
import logging





# Setup Aruments
parser = argparse.ArgumentParser(description = "Text to speech. Takes a file as input, and converts the lines into MP3s.")

# Describe Args
parser.add_argument("-v", "--verbose", 
    action="store_true", 
    help="Increase verbosity of the program")

parser.add_argument("-m", "--mode", 
    choices=["simpletext", "csv"], 
    required=True, 
    help="Determines which mode to use. A simple text file ('simpletext'), or a CSV ('csv')")
    # TODO: Determine mode from file format

parser.add_argument("-f", "--filename", 
    required=True, 
    help="Name of the input file")

parser.add_argument("-o", "--output_dir", 
    default="_TTS-Output/", 
    help="Directory where output files will be saved. WARNING: This directory is deleted each time the program is run.")

parser.add_argument("--voice", 
    required=True, 
    help="Voice ID of AWS Polly voice to use for the voice of the non-English audio. See list of available voices: https://docs.aws.amazon.com/polly/latest/dg/voicelist.html")
    # Examples: "Lupe" (ES), "Zhiyu" (CN)

parser.add_argument("-p", "--padding", 
    type=int, 
    default=0.5, 
    help="Number of SECONDS of padding to add to end of sound file (better for playlists)")

parser.add_argument("-s", "--speed", 
    type=int, 
    default=100, 
    help="Voice speed rate (in PERCENTAGE)")

# TODO: Add dry run

# Assign arguments to SETTINGS variables
args = parser.parse_args()

# SETTINGS
mode = args.mode
input_file = args.filename
output_dir = args.output_dir
voice_id = args.voice
padding = args.padding
voice_speed = args.speed


# Configure & enable logging when --verbose 
if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

logging.debug('Verbose / Debug mode enabled')





# Take line of text, and creates a text-to-speed audio file
def generate_text_to_speech_file(voice_id, ssml_text, output_dir, filename):
    
    # Build out command to call AWS Polly to generate speech files
    polly_cmd = '''
        aws polly synthesize-speech \
       --output-format mp3 \
       --text-type ssml \
       --voice-id {voice_id} \
       --text "{ssml_text}" \
       "{output_dir}{filename}"
    '''.format(voice_id=voice_id, \
        ssml_text=ssml_text, \
        output_dir=output_dir, \
        filename=filename)

    logging.debug(polly_cmd) # Debug
    os.system(polly_cmd)



def create_output_directories():
    # Remove output from previous runs
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # Create directories for output
    os.mkdir(output_dir)
    print("Created directory: %s" % output_dir)



# For "Textfile mode" (input from a simple TXT)
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

            ssml_text =  "<speak><prosody rate='{voice_speed}%'>{stripped_line}</prosody><break time='{padding}s'/></speak>".format(voice_speed=voice_speed, stripped_line=stripped_line, padding=padding)
            generate_text_to_speech_file(voice_id, ssml_text, output_dir, filename)



# "2 phrase" SSML template:
# Creates SSML-formatted text based on a phrase, a pause, then its translation
def create_2phrase_ssml(language_1, phrase_1, language_2, phrase_2):

    ssml_text = '''
        <speak>
            <prosody rate='{voice_speed}%'> 
                <lang xml:lang='{language_1}'>{phrase_1}</lang>
            </prosody>
            <break time='1.5s'/>
            <lang xml:lang='{language_2}'>{phrase_2}</lang>
            <break time='{padding}s'/>
        </speak>
        '''.format(
        voice_speed=voice_speed,
        language_1=language_1,
        phrase_1=phrase_1,
        language_2=language_2,
        phrase_2=phrase_2,
        padding=padding)

    return ssml_text


# "CSV mode" — Read from a 2-column CSV file
def tts_from_csv(input_file):
    language_1 = ""
    language_2 = ""

    row_counter = 0
    with open(input_file) as cvs_file:
        csv_reader = csv.reader(cvs_file, delimiter=',')
        for row in csv_reader:

            # Use column headers as ISO language codes (e.g. "en-US", "cmn-CN")
            if row_counter is 0:
                language_1 = row[0]
                language_2 = row[1]
                row_counter += 1
            else:
                phrase_1 = row[0]
                phrase_2 = row[1]
                ssml_text = create_2phrase_ssml(language_1, phrase_1, language_2, phrase_2)
                filename = phrase_1 + " - " + phrase_2 + ".mp3"

                generate_text_to_speech_file(voice_id, ssml_text, output_dir, filename)




def main():
    print("-----------------")
    print("Text-to-speech using AWS Polly")
    startTime = datetime.now() # Timer

    create_output_directories()

    print(mode)

    if mode == "csv":
        print("Mode: CSV file")
        tts_from_csv(input_file)
    elif mode == "simpletext":
        print("Mode: Simple text file")
        tts_from_textfile(input_file)

    # Timer
    completionTime = datetime.now() - startTime 
    print("-----------------")
    print("Completed time: ", str(completionTime)) # TODO: Format time better




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
# [_] 2nd language should be "good" english
# [_] Say at fast speed, then repeat at slow speed
# [_] Add padding equal to length of clip
# [_] Background sounds eg coffee shop
# [_] Performance: Async calls?



# DONE
# [X] Control naming ( lang1, lang2)
# [X] "This should make the directories from scratch"
# [X] Adjustable voice speed 
# [X] Add timer
# [X] <language 1> pause <language 2 / translation>
# [X] Wipe output folder each run
# [X] "I should be able to specify a text file from the command line"
# [X] Adjustable speed in CLI
