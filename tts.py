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



# COMMAND LINE ARGUMENTS
# Setup Aruments
parser = argparse.ArgumentParser(description = "Text to speech. Takes a file as input, and converts the lines into MP3s.")

# Arguments: 
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

parser.add_argument("-v1", "--voice1", 
    required=True, 
    help="Voice ID of AWS Polly voice to use for the VOICE #1. See list of available voices: https://docs.aws.amazon.com/polly/latest/dg/voicelist.html")
    # Examples: "Lupe" (ES), "Zhiyu" (CN)

parser.add_argument("-v2", "--voice2", 
    default="Salli",
    help="Voice ID of AWS Polly voice to use for the VOICE #2. See list of available voices: https://docs.aws.amazon.com/polly/latest/dg/voicelist.html")
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


# SETTINGS VARIABLES
mode = args.mode
input_file = args.filename
output_dir = args.output_dir
voice1_id = args.voice1
voice2_id = args.voice2
padding = args.padding
voice_speed = args.speed


# LOGGING
# - Configure & enable logging when --verbose 
if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

logging.debug('Verbose / Debug mode enabled')


# Deletes & creates output directory for MP3s
def create_output_directories():
    # Remove output from previous runs
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # Create directories for output
    os.mkdir(output_dir)
    os.mkdir(output_dir + "Combined")
    print("Created directory: %s" % output_dir)



# AWS POLLY call: 
# - Take line of text, and creates a text-to-speed audio file
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

    # TODO: Update this to use Popen?
    os.system(polly_cmd)
    # TODO: Trap aws CLI call output: https://stackoverflow.com/questions/3503879/assign-output-of-os-system-to-a-variable-and-prevent-it-from-being-displayed-on




# Mode: SIMPLETEXT
# - For "Textfile mode" (input from a simple TXT)
def tts_from_textfile(input_file):

    # Loop through the lines of text in a file
    with open(input_file, "r") as file:

        print("Opened file: " + input_file)

        for line in file:

            # Strip newlines from the lines, else they appear in filenames
            stripped_line = line.strip()
            filename = stripped_line + ".mp3"

            print("-----------------")
            print("Processing: " + stripped_line)
            print("-----------------")

            ssml_text =  "<speak><prosody rate='{voice_speed}%'>{stripped_line}</prosody><break time='{padding}s'/></speak>".format(voice_speed=voice_speed, stripped_line=stripped_line, padding=padding)
            generate_text_to_speech_file(voice_id, ssml_text, output_dir, filename)
            # TODO: Use format/replace better



def create_audio_from_ssml(voice_id, ssml_text, filename):
    logging.debug("Voice ID: " + voice_id)
    logging.debug("SSML: " + ssml_text)
    logging.debug("Filename: " + filename)


    # Build out command to call AWS Polly to generate speech files
    polly_cmd = '''
        aws polly synthesize-speech \
       --output-format mp3 \
       --text-type ssml \
       --voice-id {voice_id} \
       --text "{ssml_text}" \
       "{filename}"
    '''.format(voice_id=voice_id, \
        ssml_text=ssml_text, \
        output_dir=output_dir, \
        filename=filename)

    logging.debug("Polly CMD: " + polly_cmd) # Debug
    os.system(polly_cmd)


# Mode: CSV
# - Read from a 2-column CSV file
def tts_from_csv(input_file):

    phrase_clip_file = []

    row_count = 1
    with open(input_file) as cvs_file:
        csv_reader = csv.reader(cvs_file, delimiter=',')
        for row in csv_reader:

            ssml_text = "<speak><prosody rate='{voice_speed}%'>{text}</prosody><break time='1s'/></speak>".format(voice_speed=voice_speed, text=row[0])
            filename_0 = output_dir + voice1_id + " - " + row[0] + ".mp3"
            create_audio_from_ssml(voice1_id, ssml_text, filename_0)

            ssml_text = "<speak><prosody rate='100%'>{text}</prosody><break time='0.3s'/></speak>".format(voice_speed=voice_speed, text=row[1])
            filename_1 = output_dir + voice2_id + " - " + row[1] + ".mp3"
            create_audio_from_ssml(voice2_id, ssml_text, filename_1)

            ssml_text = "<speak><prosody rate='{voice_speed}%'>{text}</prosody><break time='4s'/></speak>".format(voice_speed=voice_speed, text=row[2])
            filename_2 = output_dir + voice1_id + " - " + row[2] + ".mp3"
            create_audio_from_ssml(voice1_id, ssml_text, filename_2)

            ssml_text = "<speak><prosody rate='100%'>{text}</prosody><break time='0.5s'/></speak>".format(voice_speed=voice_speed, text=row[3])
            filename_3 = output_dir + voice2_id + " - " + row[3] + ".mp3"
            create_audio_from_ssml(voice2_id, ssml_text, filename_3)

            # https://superuser.com/questions/314239/how-to-join-merge-many-mp3-files
            # output_file = concat_phrase_clips(phrase_clip_filenames)

            ffmpeg_cmd = "ffmpeg -i \"concat:{f0}|{f1}|{f2}|{f3}\" -acodec copy \"{output_dir}Combined/{row_count} {p1} - {p2}.mp3\"".format(
                f0=filename_0, f1=filename_1, f2=filename_2, f3=filename_3, p1=row[0], p2=row[1], output_dir=output_dir, row_count=row_count)

            row_count += 1
            logging.debug(ffmpeg_cmd)
            os.system(ffmpeg_cmd)

            # ffmpeg -i "concat:{f1}|{f2}|{f3}|{f4}"  -acodec copy {filename}.txt
            print("-")





# SSML Template: 2 phrase
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
        # TODO: Use format/replace better

    return ssml_text



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
# [X] 2nd language should be "good" english
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
