#!/usr/bin/env python3

# Name: Batch Text-to-speech
# Author: Jonathan Rogivue
# Last updated: 2020-04-14
# -----------------------------


# USER STORY: 
# -----------------------------
# "As a language learner, 
# I should be able to quickly convert a text file of sentences into audio files, 
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

# POLLY EXAMPLE
# aws polly synthesize-speech \
#    --output-format mp3 \
#    --voice-id Joanna \
#    --text 'Hello, my name is Joanna. I learned about the W3C on 10/3 of last year.' \
#    hello.mp3

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
# 3. Edit `sentences.txt`, put sentences you want to make speech for
# 4. Run the program with `./tts.py`
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
                    help="Directory where output files will be saved. \
                    WARNING: This directory is deleted each time the program is run.")

parser.add_argument("-v1", "--voice1",
                    required=True,
                    help="Voice ID of AWS Polly voice to use for the VOICE #1. \
                    See list of available voices: https://docs.aws.amazon.com/polly/latest/dg/voicelist.html")
# Examples: "Lupe" (ES), "Zhiyu" (CN)

parser.add_argument("-v2", "--voice2",
                    default="Salli",
                    help="Voice ID of AWS Polly voice to use for the VOICE #2. \
                    See list of available voices: https://docs.aws.amazon.com/polly/latest/dg/voicelist.html")
# Examples: "Lupe" (ES), "Zhiyu" (CN)

parser.add_argument("-p", "--padding",
                    type=int,
                    default=0.5,
                    help="Number of SECONDS of padding to add to end of sound file (better for playlists)")

parser.add_argument("-s", "--speed",
                    type=int,
                    default=100,
                    help="Voice speed rate (in PERCENTAGE)")

parser.add_argument("-v1e", "--voice1_engine",
                    choices=["standard", "neural"],
                    default="standard",
                    help="Allows you to set the voice engine (for VOICE 1), if supported")

parser.add_argument("-v2e", "--voice2_engine",
                    choices=["standard", "neural"],
                    default="standard",
                    help="Allows you to set the voice engine (for VOICE 2), if supported")

# TODO: Add dry run

# Assign arguments to SETTINGS variables
args = parser.parse_args()

# SETTINGS VARIABLES
mode = args.mode
input_file = args.filename
output_dir = args.output_dir
foreign_voice_id = args.voice1
english_voice_id = args.voice2
padding = args.padding
voice_speed = args.speed
foreign_voice_engine = args.voice1_engine
english_voice_engine = args.voice2_engine

# TODO: Dicts? some other structure?
template_0_dir = "FW-EW/"
template_1_dir = "EW-FW/"
template_2_dir = "FW-EW-FP-EP/"
template_3_dir = "EW-FW-EP-FP/"
template_4_dir = "EP/"
template_5_dir = "FP/"
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

    os.mkdir(output_dir + template_0_dir)
    os.mkdir(output_dir + template_1_dir)
    os.mkdir(output_dir + template_2_dir)
    os.mkdir(output_dir + template_3_dir)
    os.mkdir(output_dir + template_4_dir)
    os.mkdir(output_dir + template_5_dir)
    os.mkdir(output_dir + workspace_dir)
    print("Output files will be stored at: %s" % output_dir)


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


# Mode: CSV
# - Read from a 2-column CSV file
def convert_pcm_to_wav(input_filename):
    logging.debug("\n\n--------[ Converting PCM to WAV ]--------")
    logging.debug("Input filename: " + input_filename)

    output_filename = input_filename.replace(".pcm", ".wav")
    logging.debug("Output filename: " + output_filename)

    # Build out `ffmpeg` command to convert PCM to WAV
    cmd = [
        "ffmpeg",
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


def concat_wav_files(audio_files, output_filename):
    logging.debug("\n\n--------[ Concat WAV files  ]--------")
    logging.debug("Output filename: " + output_filename)
    ffmpeg_concat_list_filename = output_filename.replace(output_dir + workspace_dir, "").replace(".wav", ".txt")
    logging.debug("FFMPEG Concat list filename:" + ffmpeg_concat_list_filename)

    # Create a text file, and populate it (using `ffmpeg`s concat file format) with list of filenames
    with open(ffmpeg_concat_list_filename, "w") as concat_list_file:
        for filename in audio_files:
            escaped_filename = filename.replace("'", r"'\''")
            concat_list_file.write("file '{file}'\n".format(file=escaped_filename))

    concat_list_file.close()

    # Build out `ffmpeg` command to use the concat text file (containing list of of WAV files) into a single WAV
    cmd = [
        "ffmpeg",
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

    # TODO: Delete list file by default, keep if verbose

    return output_filename


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


def text_to_wav(voice_id, voice_engine, text):
    logging.debug("\n\n-------[ Text to WAV: {text} ]--------".format(text=text))
    logging.debug("Voice ID: " + voice_id)
    logging.debug("Voice Engine: " + voice_engine)
    logging.debug("Text: " + text)

    ssml_text = "<speak><prosody rate='{voice_speed}%'>{text}</prosody></speak>".format(
        voice_speed=voice_speed, text=text)
    pcm_filename = output_dir + workspace_dir + voice_id + " - " + text + ".pcm"
    create_pcm_from_ssml(voice_id, voice_engine, ssml_text, pcm_filename)
    wav_filename = convert_pcm_to_wav(pcm_filename)

    logging.debug("Text to WAV - Output filename: " + wav_filename)
    logging.debug("---[ END: Text to WAV: {text} ]---".format(text=text))
    return wav_filename


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


def tts_from_csv(input_file):
    short_silence = create_silent_wav_file(0.5)
    medium_silence = create_silent_wav_file(1.5)
    long_silence = create_silent_wav_file(4)

    # Used to add a sequence number to file names
    row_count = 1

    # Open CSV file which has columns: FW | EW | FP | EP
    with open(input_file) as cvs_file:
        csv_reader = csv.reader(cvs_file, delimiter=',')
        for row in csv_reader:

            # Assign words & phrases from CSV format
            foreign_word_text = row[0]
            english_word_text = row[1]
            foreign_phrase_text = row[2]
            english_phrase_text = row[3]

            # Create WAV for FW (Foreign Word)
            foreign_word = text_to_wav(foreign_voice_id, foreign_voice_engine, foreign_word_text)

            # Create WAV for EW (English Word)
            english_word = text_to_wav(english_voice_id, english_voice_engine, english_word_text)

            # Create WAV for FP (Foreign Phrase)
            foreign_phrase = text_to_wav(foreign_voice_id, foreign_voice_engine, foreign_phrase_text)

            # Create WAV for EP (English Phrase)
            english_phrase = text_to_wav(english_voice_id, english_voice_engine, english_phrase_text)


            # Combine the individual speech files into lessons based on templates

            # Template #0: "FW - EW"
            audio_files = [
                short_silence,
                foreign_word,
                medium_silence,
                english_word,
                short_silence
            ]
            filename_format = "{row} - {FW} - {EW}".format(
                row=row_count, FW=foreign_word_text, EW=english_word_text)
            combine_audio_files_to_mp3(audio_files, filename_format, template_0_dir)


            # Template #1: "EW - FW"
            audio_files = [
                short_silence,
                english_word,
                medium_silence,
                foreign_word,
                short_silence
            ]
            filename_format = "{row} - {EW} - {FW}".format(
                row=row_count, EW=english_word_text, FW=foreign_word_text)
            combine_audio_files_to_mp3(audio_files, filename_format, template_1_dir)


            # Template 3: "EW-FW-EP-FP/"
            audio_files = [
                short_silence,
                english_word,
                medium_silence,
                foreign_word,
                medium_silence,
                english_phrase,
                long_silence,
                foreign_phrase,
                short_silence
            ]
            filename_format = "{row} - {EW} - {FW} - {EP} - {FP}".format(
                row=row_count, EW=english_word_text, FW=foreign_word_text, EP=english_phrase_text, FP=foreign_word_text)
            combine_audio_files_to_mp3(audio_files, filename_format, template_3_dir)




            # ffmpeg_cmd_3 = "ffmpeg \
            #  -f lavfi -i anullsrc=channel_layout=mono:sample_rate=16000 \
            #  -i \"{f0}\" \
            #  -i \"{f1}\" \
            #  -i \"{f2}\" \
            #  -i \"{f3}\" \
            #  -filter_complex \"\
            #  [0]atrim=duration=0.5[pause1];\
            #  [0]atrim=duration=1[pause2];\
            #  [0]atrim=duration=1[pause3];\
            #  [0]atrim=duration=4[pause4];\
            #  [0]atrim=duration=0.5[pause5];\
            #  [pause1][2][pause2][1][pause3][4][pause4][3][pause5]concat=n=9:v=0:a=1\" \
            #  \"{output_dir}{template_dir}{row_count} - {p2} - {p1} - {p3}.mp3\"".format(f0=foreign_word_pcm_filename, f1=english_word_pcm_filename, f2=foreign_phrase_pcm_filename, f3=english_phrase_pcm_filename, p1=row[0], p2=row[1], p3=row[2], output_dir=output_dir, template_dir=template_3_dir,
            #                                                                             row_count=row_count)
            #
            # # Template 4: "EP/"
            # ffmpeg_cmd_4 = "ffmpeg \
            #  -f lavfi -i anullsrc=channel_layout=mono:sample_rate=16000 \
            #  -i \"{f3}\" \
            #  -filter_complex \"\
            #  [0]atrim=duration=0.5[pause1];\
            #  [0]atrim=duration=1[pause2];\
            #  [pause1][1][pause2]concat=n=3:v=0:a=1\" \
            #  \"{output_dir}{template_dir}{row_count} - {p2}.mp3\"".format(f0=foreign_word_pcm_filename, f1=english_word_pcm_filename, f2=foreign_phrase_pcm_filename, f3=english_phrase_pcm_filename, p1=row[1], p2=row[3], output_dir=output_dir, template_dir=template_4_dir,
            #                                                               row_count=row_count)
            #
            #
            #
            # # Template 5: "FP/"
            # ffmpeg_cmd_5 = "ffmpeg \
            #  -f lavfi -i anullsrc=channel_layout=mono:sample_rate=16000 \
            #  -i \"{f2}\" \
            #  -filter_complex \"\
            #  [0]atrim=duration=1[pause1];\
            #  [0]atrim=duration=1[pause2];\
            #  [pause1][1][pause2]concat=n=3:v=0:a=1\" \
            #  \"{output_dir}{template_dir}{row_count} - {p1}.mp3\"".format(f0=foreign_word_pcm_filename, f1=english_word_pcm_filename, f2=foreign_phrase_pcm_filename, f3=english_phrase_pcm_filename, p1=row[2], output_dir=output_dir, template_dir=template_5_dir,
            #                                                               row_count=row_count)
            #
            #


            # # Run the FFMPEG commands
            # logging.debug(ffmpeg_cmd_0)
            # os.system(ffmpeg_cmd_0)
            #
            # logging.debug(ffmpeg_cmd_1)
            # os.system(ffmpeg_cmd_1)
            #
            # logging.debug(ffmpeg_cmd_2)
            # os.system(ffmpeg_cmd_2)
            #
            # logging.debug(ffmpeg_cmd_3)
            # os.system(ffmpeg_cmd_3)
            #
            # logging.debug(ffmpeg_cmd_4)
            # os.system(ffmpeg_cmd_4)
            #
            # logging.debug(ffmpeg_cmd_5)
            # #os.system(ffmpeg_cmd_5)

            row_count += 1


def create_silent_wav_file(seconds):
    logging.debug("\n\n--------[ Creating silent audio file: {seconds} seconds ]--------".format(seconds=seconds))

    filename = output_dir + workspace_dir + "silence_{seconds}s.wav".format(seconds=seconds)
    logging.debug(filename)

    cmd = [
        "ffmpeg",
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


def main():
    print("-----------------")
    print("Text-to-speech using AWS Polly")
    start_time = datetime.now()  # Timer

    # Setup
    create_output_directories()

    # Create text-to-speech phrase files from CSV file
    tts_from_csv(input_file)

    # Timer
    completion_time = datetime.now() - start_time
    print("-----------------")
    print("Completed time: ", str(completion_time))  # TODO: Format time better


if __name__ == "__main__":
    main()
