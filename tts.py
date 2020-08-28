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




import argparse
import csv
import logging
import os
import shutil
from datetime import datetime
import subprocess
import json
import uuid



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
                    default="audioResources/",
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
native_voice_id = args.english_voice # TODO: "native"
voice_speed = args.speed
foreign_voice_engine = args.foreign_voice_engine
native_voice_engine = args.english_voice_engine # TODO: "native"
mode = args.mode


# audio/es/"phrase".mp3

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

    os.remove(input_filename)

    return output_filename


# Converts a WAV audio file to an MP3 audio file
def convert_wav_to_mp3(input_filename):
    logging.debug("\n\n--------[ Convert WAV to MP3  ]--------")
    logging.debug("Input filename: " + input_filename)
    output_filename = input_filename.replace(".wav", ".mp3")
    logging.debug("Output filename: " + output_filename)

    # Build out `ffmpeg` command to convert a WAV file to and MP3
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_filename,
        output_filename
    ]

    logging.debug("FFMPEG Convert WAV to MP3 CMD: \n" + subprocess.list2cmdline(cmd))
    process = subprocess.run(cmd, capture_output=True, text=True)
    logging.debug("FFMPEG Convert WAV to MP3 standard output: \n" + process.stdout)
    logging.debug("FFMPEG Convert WAV to MP3 error output: \n" + process.stderr)

    os.remove(input_filename)

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
    pcm_filename = output_dir + voice_id + " - " + text + " - " + str(voice_speed) + ".pcm"

    pcm_filename = output_dir + voice_id + "_" + str(uuid.uuid4()) + "_" + str(voice_speed) + ".pcm"

    create_pcm_from_ssml(voice_id, voice_engine, ssml_text, pcm_filename)
    wav_filename = convert_pcm_to_wav(pcm_filename)

    logging.debug("Text to WAV - Output filename: " + wav_filename)
    logging.debug("---[ END: Text to WAV: {text} ]---".format(text=text))
    return wav_filename





# CSV to Text-to-speech (TTS)
# - Creates silent audio clips to use for pauses between clips
# - Reads a CSV file which contains the words & phrases
# - For each set of words & phrases, create WAV lessons based on templates
def lessons_from_csv(input_file):
    short_silence_file = convert_wav_to_mp3(create_silent_wav_file(1.0))
    medium_silence_file = convert_wav_to_mp3(create_silent_wav_file(1.5))
    long_silence_file = convert_wav_to_mp3(create_silent_wav_file(4))

    # JSON
    #    lessons []


    lessons = []



    # Open CSV file which has columns: FW | EW | FP | EP
    with open(input_file) as cvs_file:
        csv_reader = csv.reader(cvs_file, delimiter=',')
        for row in csv_reader:

            # Assign words & phrases from CSV format
            frequency_rank = row[0]
            foreign_phrase_text = row[1]
            native_phrase_text = row[2]
            foreign_sentence_text = row[3]
            native_sentence_text = row[4]

            print("#######")
            print("Frequency rank: " + frequency_rank)
            print("#######")



            # Create WAV files for each word & phrases
            # -----------------------------------------

            # Create WAV for FW (Foreign Word)
            foreign_phrase_file = convert_wav_to_mp3(text_to_wav(foreign_voice_id, foreign_voice_engine, foreign_phrase_text))

            # Create WAV for EW (English Word)
            native_phrase_file = convert_wav_to_mp3(text_to_wav(native_voice_id, native_voice_engine, native_phrase_text))

            # Create WAV for FP (Foreign Phrase)
            foreign_sentence_file = convert_wav_to_mp3(text_to_wav(foreign_voice_id, foreign_voice_engine, foreign_sentence_text))

            # Create WAV for FP (Foreign Phrase)
            foreign_sentence_slow_file = convert_wav_to_mp3(text_to_wav(foreign_voice_id, foreign_voice_engine, foreign_sentence_text, voice_speed=80))

            # Create WAV for EP (English Phrase)
            native_sentence_file = convert_wav_to_mp3(text_to_wav(native_voice_id, native_voice_engine, native_sentence_text))



            # # TODO: Update to cleaner jSON format
            # foreign_phrase = {"text": foreign_phrase_text, "audioResource": ""}
            # native_phrase = {"text": native_phrase_text, "audioResource": ""}
            # phrase = {"foreign": foreign_phrase, "native": native_phrase}
            # foreign_sentence = {"text": foreign_sentence_text, "audioResource": ""}
            # native_sentence = {"text": native_sentence_text, "audioResource": ""}
            # sentence = {"foreign": foreign_sentence, "native": native_sentence}
            # lesson = {"phrase": phrase, "sentence": sentence, "frequencyRank": int(frequency_rank)}
            #

            lesson = {
                "frequencyRank": int(frequency_rank),
                "phrase": {
                    "foreign": {
                        "text": foreign_phrase_text,
                        "audioResource": foreign_phrase_file
                    },
                    "native": {
                        "text": native_phrase_text,
                        "audioResource": native_phrase_file
                    }
                },
                "sentence": {
                    "foreign": {
                        "text": foreign_sentence_text,
                        "audioResource": foreign_sentence_file
                    },
                    "native": {
                        "text": native_sentence_text,
                        "audioResource": native_sentence_file
                    }
                },
            }

            lessons.append(lesson)




    json_export = open("es-lessons.json", "w")
    json_export.write(json.dumps(lessons, indent=2, ensure_ascii=False))
    json_export.close()

# Creates silent WAV files of a given length in seconds
def create_silent_wav_file(seconds):
    logging.debug("\n\n--------[ Creating silent audio file: {seconds} seconds ]--------".format(seconds=seconds))

    filename = output_dir + "silence_{seconds}s.wav".format(seconds=seconds)
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


    # Delete workspace directories unless verbose/debug mode is enabled
    if args.verbose is not True:
        print("Cleaning up workspace directories...")
        shutil.rmtree(output_dir)

    # Display how long it took for the program to run
    completion_time = datetime.now() - start_time
    print("-----------------")
    print("Completed time: ", str(completion_time))  # TODO: Format time better


if __name__ == "__main__":
    main()
