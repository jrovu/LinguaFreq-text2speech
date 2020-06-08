#!/usr/bin/env python3

# Name: Batch Text-to-speech
# Author: Jonathan Rogivue
# Last updated: 2020-04-19
# -----------------------------


# USER STORY: 
# -----------------------------
# "As a language learner, 
# I should be able to quickly convert a list of words & phrases of sentences into audio files,
# so that I can practice listening to them"


# TECHNICAL OVERVIEW:
# -----------------------------
# This script uses AWS Polly (text-to-speech engine), to create individual MP3 files from lines of text in a file


# INFORMATION
# -------------------------------

# Polly Console: https://console.aws.amazon.com/polly/home/SynthesizeSpeech
# Polly Voice ID list: https://docs.aws.amazon.com/polly/latest/dg/voicelist.html
# - Chinese: "Zhiyu"
# - Spanish: "Lupe"

# CHANGE VOICE SPEED EXAMPLE
# --text-type ssml
# --text "<speak><prosody rate='50%'>这个人好是好，就是不适合</prosody></speak>"

# TERMINOLOGY & ABBREVIATIONS
# -------------------------------
# "EW" = English Word
# "EP" = English Phrase
# "FW" = Foreign Word
# "FP" = Foreign Phrase


# PREREQUISITES:
# -----------------------------
# - AWS account (https://aws.amazon.com/)
#     - Account with AWS Polly permission
# - Mac homebrew (https://brew.sh/)
#     - git (`brew install git`)
#     - aws CLI (`brew install awscli`)
#     - python3 (`brew install python3`)
#     - ffmpeg (`brew install ffmpeg`)
# - `awscli` configured (`aws configure`) with correct user


# HOW TO INSTALL 
# -----------------------------
# 1. Git clone: `git clone https://github.com/Helicer/batch-text2speech.git`
# 2. Change to the directory `batch-text2speech.git`
# 3. Edit `example_chinese.csv`, put sentences you want to make speech for
# 4. Run the program with `./tts.py`
# EXAMPLE: ./tts.py -f example_spanish.csv --foreign_voice Lupe --foreign_voice_engine neural --english_voice Joanna --english_voice_engine neural -s 90
#
# GET HELP by running `tts.py -h`


import argparse
import csv
import logging
import os
import shutil
from datetime import datetime
import subprocess

# COMMAND LINE ARGUMENTS
# Setup Arguments
parser = argparse.ArgumentParser(description="Text to speech. Takes a file as input, and converts the lines into MP3s.")

# Arguments: 
parser.add_argument("-v", "--verbose",
                    action="store_true",
                    help="Increase verbosity of the program & turns on debug mode. When debug is enabled, workspace directories & files are not deleted.")

parser.add_argument("-f", "--filename",
                    required=True,
                    help="Name of the input file")

parser.add_argument("-o", "--output_dir",
                    default="_TTS-Output/",
                    help="Directory where output files will be saved. \
                    WARNING: This directory is deleted each time the program is run.")

parser.add_argument("--foreign_voice",
                    required=True,
                    help="Voice ID of AWS Polly voice to use for the FOREIGN VOICE. \
                    See list of available voices: https://docs.aws.amazon.com/polly/latest/dg/voicelist.html")
# Examples: "Lupe" (ES), "Zhiyu" (CN)

parser.add_argument("--english_voice",
                    default="Joanna",
                    help="Voice ID of AWS Polly voice to use for the ENGLISH VOICE. \
                    See list of available voices: https://docs.aws.amazon.com/polly/latest/dg/voicelist.html")
# Examples: "Salli" (EN), "Joanna" (EN)

parser.add_argument("-s", "--speed",
                    type=int,
                    default=100,
                    help="Voice speed rate (in PERCENTAGE)")

parser.add_argument("--foreign_voice_engine",
                    choices=["standard", "neural"],
                    default="standard",
                    help="Allows you to set the voice engine (for FOREIGN VOICE), if supported")

parser.add_argument("--english_voice_engine",
                    choices=["standard", "neural"],
                    default="standard",
                    help="Allows you to set the voice engine (for ENGLISH VOICE), if supported")

parser.add_argument("--mode",
                    choices=["lessons", "pyramid"],
                    default="lessons",
                    help="Determines which CSV structure and output to use.")

# TODO: Add dry run

# Assign arguments to SETTINGS variables
args = parser.parse_args()

# SETTINGS VARIABLES
input_file = args.filename
output_dir = args.output_dir
foreign_voice_id = args.foreign_voice
english_voice_id = args.english_voice
voice_speed = args.speed
foreign_voice_engine = args.foreign_voice_engine
english_voice_engine = args.english_voice_engine
mode = args.mode

# TODO: Dicts? some other structure?
template_0_dir = "FW-EW/"
template_1_dir = "EW-FW/"
template_2_dir = "FW-EW-FP-EP/"
template_3_dir = "EW-FW-EP-FP/"
template_4_dir = "EP/"
template_5_dir = "FP/"
template_6_dir = "FP+Pause/"
template_7_dir = "FP+Pause (Slow)/"
template_8_dir = "Pyramid/"
workspace_dir = "_Workspace/"

# LOGGING
# - Configure & enable logging when --verbose 
if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

logging.debug('Verbose mode enabled')


# Deletes & creates output directory for MP3s
def create_output_directories():
    # Remove output from previous runs
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # Create directories for output
    os.mkdir(output_dir)

    # Create directories for each template
    os.mkdir(output_dir + template_0_dir)
    os.mkdir(output_dir + template_1_dir)
    os.mkdir(output_dir + template_2_dir)
    os.mkdir(output_dir + template_3_dir)
    os.mkdir(output_dir + template_4_dir)
    os.mkdir(output_dir + template_5_dir)
    os.mkdir(output_dir + template_6_dir)
    os.mkdir(output_dir + template_7_dir)
    os.mkdir(output_dir + template_8_dir)
    os.mkdir(output_dir + workspace_dir)
    print("Output files will be stored at: %s" % output_dir)


# Calls AWS Polly API and creates PCM audio files
def create_pcm_from_ssml(voice_id, engine, ssml_text, filename):
    logging.debug("\n\n-------[ AWS Polly to PCM ]--------")
    logging.debug("Voice ID: " + voice_id)
    logging.debug("SSML: " + ssml_text)
    logging.debug("Filename: \"" + filename + "\"")

    # Build out command to call AWS Polly to generate speech files
    cmd = [
        "aws", "polly", "synthesize-speech",
        "--output-format", "pcm",
        "--sample-rate", "16000",
        "--text-type", "ssml",
        "--voice-id", voice_id,
        "--engine", engine,
        "--text", ssml_text,
        filename
    ]

    logging.debug("Polly CMD: \n" + subprocess.list2cmdline(cmd))
    process = subprocess.run(cmd, capture_output=True, text=True)
    logging.debug("Polly CMD standard output: \n" + process.stdout)
    logging.debug("Polly CMD error output: \n" + process.stderr)


# Converts a PCM audio file to WAV audio file
def convert_pcm_to_wav(input_filename):
    logging.debug("\n\n--------[ Converting PCM to WAV ]--------")
    logging.debug("Input filename: " + input_filename)

    output_filename = input_filename.replace(".pcm", ".wav")
    logging.debug("Output filename: " + output_filename)

    # Build out `ffmpeg` command to convert PCM to WAV
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "s16le",
        "-ar", "16000",
        "-ac", "1",
        "-i", input_filename,
        output_filename
    ]

    logging.debug("FFMPEG PCM to WAV CMD: \n" + subprocess.list2cmdline(cmd))
    process = subprocess.run(cmd, capture_output=True, text=True)
    logging.debug("FFMPEG PCM to WAV standard output: \n" + process.stdout)
    logging.debug("FFMPEG PCM to WAV error output: \n" + process.stderr)

    return output_filename


# Concatenates several audio files into a single WAV file
def concat_wav_files(audio_files, output_filename):
    logging.debug("\n\n--------[ Concat WAV files  ]--------")
    logging.debug("Output filename: " + output_filename)
    ffmpeg_concat_list_filename = output_filename.replace(output_dir + workspace_dir, "").replace(".wav", ".txt")
    logging.debug("FFMPEG Concat list filename:" + ffmpeg_concat_list_filename)

    # Create a text file, and populate it (using `ffmpeg`s concat file format) with list of filenames
    with open(ffmpeg_concat_list_filename, "w") as concat_list_file:
        for filename in audio_files:

            # Escape filenames according to FFMPEG's formatting.
            # See: https://superuser.com/questions/787064/filename-quoting-in-ffmpeg-concat/787651
            escaped_filename = filename.replace("'", r"'\''")
            concat_list_file.write("file '{file}'\n".format(file=escaped_filename))

    concat_list_file.close()

    # Build out `ffmpeg` command to use the concat text file (containing list of of WAV files) into a single WAV
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", ffmpeg_concat_list_filename,
        "-c", "copy",
        output_filename
    ]

    logging.debug("FFMPEG Concat CMD: \n" + subprocess.list2cmdline(cmd))
    process = subprocess.run(cmd, capture_output=True, text=True)
    logging.debug("FFMPEG Concat standard output: \n" + process.stdout)
    logging.debug("FFMPEG Concat error output: \n" + process.stderr)

    # Delete the concat text unless Verbose/debug mode is enabled
    if args.verbose is not True:
        os.remove(ffmpeg_concat_list_filename)

    return output_filename


# Converts a WAV audio file to an MP3 audio file
def convert_wav_to_mp3(input_filename, output_filename):
    logging.debug("\n\n--------[ Convert WAV to MP3  ]--------")
    logging.debug("Input filename: " + input_filename)
    logging.debug("Output filename: " + output_filename)

    # Build out `ffmpeg` command to convert a WAV file to and MP3
    cmd = [
        "ffmpeg",
        "-i", input_filename,
        output_filename
    ]

    logging.debug("FFMPEG Convert WAV to MP3 CMD: \n" + subprocess.list2cmdline(cmd))
    process = subprocess.run(cmd, capture_output=True, text=True)
    logging.debug("FFMPEG Convert WAV to MP3 standard output: \n" + process.stdout)
    logging.debug("FFMPEG Convert WAV to MP3 error output: \n" + process.stderr)

    return output_filename


# Creates a WAV audio file from text
# - Calls AWS Polly, gets a PCM file, convert that file to WAV
def text_to_wav(voice_id, voice_engine, text, voice_speed=voice_speed):
    logging.debug("\n\n-------[ Text to WAV: {text} ]--------".format(text=text))
    logging.debug("Voice ID: " + voice_id)
    logging.debug("Voice Engine: " + voice_engine)
    logging.debug("Text: " + text)
    logging.debug("Speed: " + str(voice_speed))

    ssml_text = "<speak><prosody rate='{voice_speed}%'>{text}</prosody></speak>".format(
        voice_speed=voice_speed, text=text)
    pcm_filename = output_dir + workspace_dir + voice_id + " - " + text + " - " + str(voice_speed) + ".pcm"
    create_pcm_from_ssml(voice_id, voice_engine, ssml_text, pcm_filename)
    wav_filename = convert_pcm_to_wav(pcm_filename)

    logging.debug("Text to WAV - Output filename: " + wav_filename)
    logging.debug("---[ END: Text to WAV: {text} ]---".format(text=text))
    return wav_filename


# Combine audio files, create MP3s
# - Takes a list of WAV audio files as input
# - Concats WAV audio files
# - Converts concat'd WAV file to MP3
def combine_audio_files_to_mp3(audio_files, filename_format, template_dir):
    logging.debug("\n\n-------[ Combine Audio files to MP3 ]--------")
    logging.debug("Audio files: " + str(audio_files))
    logging.debug("Filename format: " + filename_format)
    logging.debug("Template directory: " + template_dir)

    combined_wav_filename = \
        concat_wav_files(audio_files, output_dir + workspace_dir + filename_format + ".wav")
    combined_mp3_filename = \
        convert_wav_to_mp3(combined_wav_filename, output_dir + template_dir + filename_format + ".mp3")

    logging.debug("Created MP3 from audio files: " + combined_mp3_filename)
    print("► Created: " + combined_mp3_filename)
    logging.debug("---[ END: Combine mp3 from audio files ]---")


# CSV to Text-to-speech (TTS)
# - Creates silent audio clips to use for pauses between clips
# - Reads a CSV file which contains the words & phrases
# - For each set of words & phrases, create WAV lessons based on templates
def lessons_from_csv(input_file):
    short_silence_file = create_silent_wav_file(1.0)
    medium_silence_file = create_silent_wav_file(1.5)
    long_silence_file = create_silent_wav_file(4)

    # Open CSV file which has columns: FW | EW | FP | EP
    with open(input_file) as cvs_file:
        csv_reader = csv.reader(cvs_file, delimiter=',')
        for row in csv_reader:

            # Assign words & phrases from CSV format
            phrase_number = row[0]
            foreign_word_text = row[1]
            english_word_text = row[2]
            foreign_phrase_text = row[3]
            english_phrase_text = row[4]

            # Create WAV files for each word & phrases
            # -----------------------------------------

            # Create WAV for FW (Foreign Word)
            foreign_word_file = text_to_wav(foreign_voice_id, foreign_voice_engine, foreign_word_text)

            # Create WAV for EW (English Word)
            english_word_file = text_to_wav(english_voice_id, english_voice_engine, english_word_text)

            # Create WAV for FP (Foreign Phrase)
            foreign_phrase_file = text_to_wav(foreign_voice_id, foreign_voice_engine, foreign_phrase_text)

            # Create WAV for FP (Foreign Phrase)
            foreign_phrase_slow_file = text_to_wav(foreign_voice_id, foreign_voice_engine, foreign_phrase_text, voice_speed=80)

            # Create WAV for EP (English Phrase)
            english_phrase_file = text_to_wav(english_voice_id, english_voice_engine, english_phrase_text)

            # Combine the individual speech files into lessons based on templates
            # -----------------------------------------

            # Template #0: "FW - EW"
            audio_files = [
                short_silence_file,
                foreign_word_file,
                medium_silence_file,
                english_word_file,
                short_silence_file
            ]
            filename_format = "{phrase_number} - {FW} - {EW}".format(
                phrase_number=phrase_number, FW=foreign_word_text, EW=english_word_text)
            combine_audio_files_to_mp3(audio_files, filename_format, template_0_dir)

            # Template #1: "EW - FW"
            audio_files = [
                short_silence_file,
                english_word_file,
                medium_silence_file,
                foreign_word_file,
                short_silence_file
            ]
            filename_format = "{phrase_number} - {EW} - {FW}".format(
                phrase_number=phrase_number, EW=english_word_text, FW=foreign_word_text)
            combine_audio_files_to_mp3(audio_files, filename_format, template_1_dir)

            # Template 2: "FW-EW-FP-EP/"
            audio_files = [
                short_silence_file,
                foreign_word_file,
                medium_silence_file,
                english_word_file,
                medium_silence_file,
                foreign_phrase_file,
                long_silence_file,
                english_phrase_file,
                short_silence_file
            ]
            filename_format = "{phrase_number} - {FW} - {EW} - {FP} - {EP}".format(
                phrase_number=phrase_number, EW=english_word_text, FW=foreign_word_text, EP=english_phrase_text, FP=foreign_phrase_text)
            combine_audio_files_to_mp3(audio_files, filename_format, template_2_dir)

            # Template 3: "EW-FW-EP-FP/"
            audio_files = [
                short_silence_file,
                english_word_file,
                medium_silence_file,
                foreign_word_file,
                medium_silence_file,
                english_phrase_file,
                long_silence_file,
                foreign_phrase_file,
                short_silence_file
            ]
            filename_format = "{phrase_number} - {EW} - {FW} - {EP} - {FP}".format(
                phrase_number=phrase_number, EW=english_word_text, FW=foreign_word_text, EP=english_phrase_text, FP=foreign_phrase_text)
            combine_audio_files_to_mp3(audio_files, filename_format, template_3_dir)

            # Template 4: "EP/"
            audio_files = [
                short_silence_file,
                english_phrase_file,
                short_silence_file
            ]
            filename_format = "{phrase_number} - {EP}".format(
                phrase_number=phrase_number, EP=english_phrase_text)
            combine_audio_files_to_mp3(audio_files, filename_format, template_4_dir)

            # Template 5: "FP/"
            audio_files = [
                short_silence_file,
                foreign_phrase_file,
                short_silence_file
            ]
            filename_format = "{phrase_number} - {FP}".format(
                phrase_number=phrase_number, FP=foreign_phrase_text)
            combine_audio_files_to_mp3(audio_files, filename_format, template_5_dir)

            # Template 6: "FP+Pause/"
            audio_files = [
                short_silence_file,
                foreign_phrase_file,
                long_silence_file
            ]
            filename_format = "{phrase_number} - {FP}".format(
                phrase_number=phrase_number, FP=foreign_phrase_text)
            combine_audio_files_to_mp3(audio_files, filename_format, template_6_dir)

            # Template 7: "FP+Pause (Slow)/"
            audio_files = [
                short_silence_file,
                foreign_phrase_slow_file,
                long_silence_file
            ]
            filename_format = "{phrase_number} - {FP}".format(
                phrase_number=phrase_number, FP=foreign_phrase_text)
            combine_audio_files_to_mp3(audio_files, filename_format, template_7_dir)


# Creates silent WAV files of a given length in seconds
def create_silent_wav_file(seconds):
    logging.debug("\n\n--------[ Creating silent audio file: {seconds} seconds ]--------".format(seconds=seconds))

    filename = output_dir + workspace_dir + "silence_{seconds}s.wav".format(seconds=seconds)
    logging.debug(filename)

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", "anullsrc=channel_layout=mono:sample_rate=16000",
        "-t", "{seconds}".format(seconds=seconds),
        filename
    ]

    logging.debug("FFMPEG Create Silent Audio CMD: \n" + subprocess.list2cmdline(cmd))
    process = subprocess.run(cmd, capture_output=True, text=True)
    logging.debug("FFMPEG Create Silent Audio standard output: \n" + process.stdout)
    logging.debug("FFMPEG Create Silent Audio error output: \n" + process.stderr)

    return filename


# Takes a list of phrase pieces (e.g. "I", "am", "going") and creates factorial-like
# phrases. Like "I", "I am", "I am going"
def phrase_pieces_to_pyramid_phrases(phrase_pieces):
    logging.debug("\n\n--------[ Phrase Pieces to Pyramid Phrases ]--------")
    logging.debug("Pieces: " + str(phrase_pieces))
    pyramid_phrases = []
    pyramid_phrase = ""

    for piece in phrase_pieces:
        pyramid_phrase = pyramid_phrase + piece
        logging.debug("Phrase: " + pyramid_phrase)
        pyramid_phrases.append(pyramid_phrase)

    return pyramid_phrases


def pyramid_from_csv(input_file):
    logging.debug("\n\n--------[ Pyramid from CSV ]--------")


    short_silence_file = create_silent_wav_file(1.0)

    # Open CSV file which has columns: Row #, <unbounded list of phrases to combine>
    with open(input_file) as cvs_file:
        phrases = csv.reader(cvs_file, delimiter=',')

        # For each phrase line
        for phrase in phrases:

            column_count = 0

            # Phrase: This is one row in the XLS. E.g. "I", "am", "going", "to", "work
            # phrase_pieces: list of pieces in a Phrase
            # Pyramid phrase: For each Phrase, we create a Pyramid_phrase from its Phrase_pieces
            #   "I"
            #   "I am"
            #   "I am going"
            #   "I am going to"...

            # List of all pieces for THIS phrase
            phrase_pieces = []
            phrase_number = 0  # TODO: Default to none?
            phrase_text = ""

            # For each word in a phrase, add it to the phrase_pieces list
            #
            # Skips the first column, as it's reserved for the phrase number:
            for phrase_piece in phrase:

                # First column (phrase #)
                if column_count is 0:
                    logging.debug("Pyramid: #" + str(phrase_piece))
                    phrase_number = phrase_piece

                # For all the other phrase pieces:
                else:
                    # CSV creates empty columns to pad out a row, to the row with the most columns.
                    # We do not want to include these empty pieces.
                    #
                    # Skips adding a piece, if this piece is EMPTY:
                    if phrase_piece not in (None, ""):

                        # Adds this piece to the list of phrases:
                        phrase_pieces.append(phrase_piece)

                # This will be used to provide an number for each pyramid associated with a phrase
                column_count = column_count + 1

            # For a phrase, create pyramid strings from phrase's pieces
            pyramid_phrases = phrase_pieces_to_pyramid_phrases(phrase_pieces)
            logging.debug("Pyramid phrases: " + str(pyramid_phrases))

            # Create audio files for each pyramid phrase
            pyramid_phrase_files = []
            for pyramid_phrase in pyramid_phrases:
                logging.debug("Text to speech: " + pyramid_phrase)
                pyramid_phrase_file = text_to_wav(foreign_voice_id, foreign_voice_engine, pyramid_phrase)
                pyramid_phrase_files.append(pyramid_phrase_file)

                # TODO: Update to use silent gaps which match the length of the word
                pyramid_phrase_files.append(short_silence_file)

            logging.debug("Pyramid phrase files: " + str(pyramid_phrase_files))

            # Combine the LIST of a phrase's pieces into a STRING
            phrase_text = ' '.join(map(str, phrase_pieces))

            filename_format = "{phrase_number} - {phrase_text} - Pyramid".format(
                phrase_number=phrase_number, phrase_text=phrase_text)
            combine_audio_files_to_mp3(pyramid_phrase_files, filename_format, template_8_dir)

            # TODO: NEXT STEP
            # Create a lesson var as a list. This contains the playlist of all the soundfiles to combine
            # Set a counter
            # Loop thru the list of files
            # For each file
            # - Add to the lesson list
            # - Add appropriate gap
            # Burn these as one big MP3





            # piece_count = column count, minus the row number
            # pieces = each, word, in, an, array
            # pyramid_phrases = pieces_to_pyramid(pieces):
            #   pyramid_phrases = (empty list)
            #   combined_phrase = ""
            #   for piece in pieces:
            #       combined_phrase = combined_phrase + piece
            #       pyramid_phrases.add(combined_phrase)
            #   return pyramid_phrase
            #

            # for phrase in pyramid_phrases:
            #   phrase_file = text_to_wav(phrase)
            #   audio_files = (silence, phrase file, etc)
            #   format the file name, phrase number and pyramid iteration
            #   combine audio files to mp3
            #







            # Assign words & phrases from CSV format
            phrase_number = phrase[0]




            foreign_word_text = phrase[1]
            english_word_text = phrase[2]
            foreign_phrase_text = phrase[3]
            english_phrase_text = phrase[4]




def main():
    print("-----------------")
    print("Text-to-speech using AWS Polly")
    start_time = datetime.now()  # Timer

    # Create directories to store the audio clips
    create_output_directories()



    # Create text-to-speech phrase files from CSV file
    if "lessons" in mode:
        logging.debug("Using Mode: lesson")
        lessons_from_csv(input_file)

    if "pyramid" in mode:
        logging.debug("Using Mode: Pyramid")
        pyramid_from_csv(input_file)


    # Delete workspace directories unless verbose/debug mode is enabled
    if args.verbose is not True:
        print("Cleaning up workspace directories...")
        shutil.rmtree(output_dir + workspace_dir)

    # Display how long it took for the program to run
    completion_time = datetime.now() - start_time
    print("-----------------")
    print("Completed time: ", str(completion_time))  # TODO: Format time better


if __name__ == "__main__":
    main()
