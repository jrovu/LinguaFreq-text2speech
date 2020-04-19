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
voice1_id = args.voice1
voice2_id = args.voice2
padding = args.padding
voice_speed = args.speed
voice1_engine = args.voice1_engine
voice2_engine = args.voice2_engine

# TODO: Dicts? some other structure?
template_1_dir = "FW-EW/"
template_2_dir = "EW-FW/"
template_3_dir = "FW-EW-FP-EP/"
template_4_dir = "EW-FW-EP-FP/"
template_5_dir = "EP/"
template_6_dir = "FP/"
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

    os.mkdir(output_dir + template_1_dir)
    os.mkdir(output_dir + template_2_dir)
    os.mkdir(output_dir + template_3_dir)
    os.mkdir(output_dir + template_4_dir)
    os.mkdir(output_dir + template_5_dir)
    os.mkdir(output_dir + template_6_dir)
    os.mkdir(output_dir + workspace_dir)
    print("Created output directory: %s" % output_dir)



def create_audio_from_ssml(voice_id, engine, ssml_text, filename):
    logging.debug("\n\n-------[ AWS Polly call ]--------")
    logging.debug("Voice ID: " + voice_id)
    logging.debug("SSML: " + ssml_text)
    logging.debug("Filename: \"" + filename + "\"")

    # Build out command to call AWS Polly to generate speech files
    polly_cmd = '''
        aws polly synthesize-speech \
       --output-format pcm \
       --sample-rate 16000 \
       --text-type ssml \
       --voice-id {voice_id} \
       --engine {engine} \
       --text "{ssml_text}" \
       "{filename}"
    '''.format(voice_id=voice_id,
               engine=engine,
               ssml_text=ssml_text,
               output_dir=output_dir,
               filename=filename)


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

    # Convert PCM to WAV
    # https://stackoverflow.com/questions/11986279/can-ffmpeg-convert-audio-from-raw-pcm-to-wav
    cmd = '''
    ffmpeg \
    -f s16le \
    -ar 16000 \
    -ac 1 \
    -i \"{input_filename}\" \
    -y \
    \"{output_filename}\"
    '''.format(input_filename=input_filename, output_filename=output_filename)

    logging.debug("ffmpeg cmd:")
    logging.debug(cmd)
    os.system(cmd)

    return output_filename


def concat_audio_files(audio_files, output_filename):
    logging.debug("\n\n--------[ FFMPEG Concat ]--------")
    logging.debug("Output filename: " + output_filename)
    ffmpeg_concat_list_filename = output_filename.replace(".wav", ".txt")
    logging.debug("FFMPEG Concat list filename:" + ffmpeg_concat_list_filename)

    with open(ffmpeg_concat_list_filename, "w") as concat_list_file:
        for file in audio_files:
            concat_list_file.write("file '{file}'\n".format(file=file))

    concat_list_file.close()

    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", ffmpeg_concat_list_filename,
        "-c", "copy",
        output_dir + workspace_dir + output_filename
    ]

    logging.debug("FFMPEG Concat CMD: \n" + subprocess.list2cmdline(cmd))
    process = subprocess.run(cmd, capture_output=True, text=True)
    logging.debug("FFMPEG Concat standard output: \n" + process.stdout)
    logging.debug("FFMPEG Concat error output: \n" + process.stderr)




    # TODO: Delete list file by default, keep if verbose

    return output_filename


def convert_wav_to_mp3(combined_filename_0, param):
    pass


def tts_from_csv(input_file):

    silent_short = create_silent_audio_file(0.5)
    silent_medium = create_silent_audio_file(1)
    silent_long = create_silent_audio_file(4)



    row_count = 1
    with open(input_file) as cvs_file:
        csv_reader = csv.reader(cvs_file, delimiter=',')
        for row in csv_reader:

            # FW - Foreign Word
            ssml_text = "<speak><prosody rate='{voice_speed}%'>{text}</prosody><break time='0s'/></speak>".format(
                voice_speed=voice_speed, text=row[0])
            pcm_filename_0 = output_dir + workspace_dir + voice1_id + " - " + row[0] + ".pcm"
            create_audio_from_ssml(voice1_id, voice1_engine, ssml_text, pcm_filename_0)
            wav_filename_0 = convert_pcm_to_wav(pcm_filename_0)



            # EW - English Word
            ssml_text = "<speak><prosody rate='100%'>{text}</prosody><break time='0s'/></speak>".format(
                voice_speed=voice_speed, text=row[1])
            pcm_filename_1 = output_dir + workspace_dir + voice2_id + " - " + row[1] + ".pcm"
            create_audio_from_ssml(voice2_id, voice2_engine, ssml_text, pcm_filename_1)
            wav_filename_1 = convert_pcm_to_wav(pcm_filename_1)

            # FP - Foreign Phrase
            ssml_text = "<speak><prosody rate='{voice_speed}%'>{text}</prosody><break time='0s'/></speak>".format(
                voice_speed=voice_speed, text=row[2])
            pcm_filename_2 = output_dir + workspace_dir + voice1_id + " - " + row[2] + ".pcm"
            create_audio_from_ssml(voice1_id, voice1_engine, ssml_text, pcm_filename_2)
            wav_filename_2 = convert_pcm_to_wav(pcm_filename_2)

            # EP - English Phrase
            ssml_text = "<speak><prosody rate='100%'>{text}</prosody><break time='0s'/></speak>".format(
                voice_speed=voice_speed, text=row[3])
            pcm_filename_3 = output_dir + workspace_dir + voice2_id + " - " + row[3] + ".pcm"
            create_audio_from_ssml(voice2_id, voice2_engine, ssml_text, pcm_filename_3)
            wav_filename_3 = convert_pcm_to_wav(pcm_filename_3)


            # Combine the individual speech files into lessons based on templates


            audio_files_0 = [
                silent_short,
                wav_filename_0,
                silent_medium,
                wav_filename_1,
                silent_short
            ]
            filename_format = "Combined {row} - {w0} - {w1}".format(row=row_count, w0=row[0], w1=row[1])
            
            combined_filename_0 = concat_audio_files(audio_files_0, filename_format + ".wav")
            convert_wav_to_mp3(combined_filename_0, filename_format + ".mp3")





            # Reference:
            # https://ffmpeg.org/ffmpeg-filters.html#Filtergraph-syntax-1

            # Template 0: "FW - pause - EW - pause"
            ffmpeg_cmd_0 = "ffmpeg \
             -f lavfi -i anullsrc=channel_layout=mono:sample_rate=16000 \
             -i \"{f0}\" \
             -i \"{f1}\" \
             -filter_complex \"\
             [0]atrim=duration=0.5[pause1];\
             [0]atrim=duration=1[pause2];\
             [0]atrim=duration=0.5[pause3];\
             [pause1][1][pause2][2][pause3]concat=n=5:v=0:a=1\" \
             \"{output_dir}{template_dir}{row_count} - {p1} - {p2}.mp3\"".format(f0=pcm_filename_0, f1=pcm_filename_1, p1=row[0], p2=row[1], output_dir=output_dir, template_dir=template_1_dir,
                row_count=row_count)


            # WIP
            ffmpeg_cmd = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", "anullsrc=channel_layout=mono:sample_rate=16000",
                "-i", pcm_filename_0,
                "-i", pcm_filename_1,
                "-filter_complex",
            ]

            # Template 1: EW - pause - FW - pause
            ffmpeg_cmd_1 = "ffmpeg \
             -f lavfi -i anullsrc=channel_layout=mono:sample_rate=16000 \
             -i \"{f0}\" \
             -i \"{f1}\" \
             -filter_complex \"\
             [0]atrim=duration=0.5[pause1];\
             [0]atrim=duration=1[pause2];\
             [0]atrim=duration=0.5[pause3];\
             [pause1][2][pause2][1][pause3]concat=n=5:v=0:a=1\" \
             \"{output_dir}{template_dir}{row_count} - {p2} - {p1}.mp3\"".format(f0=pcm_filename_0, f1=pcm_filename_1, p1=row[0], p2=row[1], output_dir=output_dir, template_dir=template_2_dir,
                row_count=row_count)


            # Template 2: FW - pause - EW - pause - FP - pause - EP
            ffmpeg_cmd_2 = "ffmpeg \
             -f lavfi -i anullsrc=channel_layout=mono:sample_rate=16000 \
             -i \"{f0}\" \
             -i \"{f1}\" \
             -i \"{f2}\" \
             -i \"{f3}\" \
             -filter_complex \"\
             [0]atrim=duration=0.5[pause1];\
             [0]atrim=duration=1[pause2];\
             [0]atrim=duration=1[pause3];\
             [0]atrim=duration=4[pause4];\
             [0]atrim=duration=0.5[pause5];\
             [pause1][1][pause2][2][pause3][3][pause4][4][pause5]concat=n=9:v=0:a=1\" \
             \"{output_dir}{template_dir}{row_count} - {p1} - {p2} - {p3}.mp3\"".format(f0=pcm_filename_0, f1=pcm_filename_1, f2=pcm_filename_2, f3=pcm_filename_3, p1=row[0], p2=row[1], p3=row[2], output_dir=output_dir, template_dir=template_3_dir,
                row_count=row_count)

            # Template 3: "EW-FW-EP-FP/"
            ffmpeg_cmd_3 = "ffmpeg \
             -f lavfi -i anullsrc=channel_layout=mono:sample_rate=16000 \
             -i \"{f0}\" \
             -i \"{f1}\" \
             -i \"{f2}\" \
             -i \"{f3}\" \
             -filter_complex \"\
             [0]atrim=duration=0.5[pause1];\
             [0]atrim=duration=1[pause2];\
             [0]atrim=duration=1[pause3];\
             [0]atrim=duration=4[pause4];\
             [0]atrim=duration=0.5[pause5];\
             [pause1][2][pause2][1][pause3][4][pause4][3][pause5]concat=n=9:v=0:a=1\" \
             \"{output_dir}{template_dir}{row_count} - {p2} - {p1} - {p3}.mp3\"".format(f0=pcm_filename_0, f1=pcm_filename_1, f2=pcm_filename_2, f3=pcm_filename_3, p1=row[0], p2=row[1], p3=row[2], output_dir=output_dir, template_dir=template_4_dir,
                row_count=row_count)

            # Template 4: "EP/"
            ffmpeg_cmd_4 = "ffmpeg \
             -f lavfi -i anullsrc=channel_layout=mono:sample_rate=16000 \
             -i \"{f3}\" \
             -filter_complex \"\
             [0]atrim=duration=0.5[pause1];\
             [0]atrim=duration=1[pause2];\
             [pause1][1][pause2]concat=n=3:v=0:a=1\" \
             \"{output_dir}{template_dir}{row_count} - {p2}.mp3\"".format(f0=pcm_filename_0, f1=pcm_filename_1, f2=pcm_filename_2, f3=pcm_filename_3, p1=row[1], p2=row[3], output_dir=output_dir, template_dir=template_5_dir,
                row_count=row_count)



            # Template 5: "FP/"
            ffmpeg_cmd_5 = "ffmpeg \
             -f lavfi -i anullsrc=channel_layout=mono:sample_rate=16000 \
             -i \"{f2}\" \
             -filter_complex \"\
             [0]atrim=duration=1[pause1];\
             [0]atrim=duration=1[pause2];\
             [pause1][1][pause2]concat=n=3:v=0:a=1\" \
             \"{output_dir}{template_dir}{row_count} - {p1}.mp3\"".format(f0=pcm_filename_0, f1=pcm_filename_1, f2=pcm_filename_2, f3=pcm_filename_3, p1=row[2], output_dir=output_dir, template_dir=template_6_dir,
                row_count=row_count)




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


def create_silent_audio_file(seconds):
    logging.debug(" ")
    logging.debug(" ")
    logging.debug("--------[ Creating silent audio file: {seconds} seconds ]--------".format(seconds=seconds))

    filename = output_dir + workspace_dir + "silence_{seconds}s.wav".format(seconds=seconds)
    logging.debug(filename)

    cmd = '''
    ffmpeg \
    -f lavfi \
    -i anullsrc=channel_layout=mono:sample_rate=16000 \
    -t {seconds} \
    \"{filename}\"
    '''.format(seconds=seconds, filename=filename)

    logging.debug("ffmpeg command:")
    logging.debug(cmd)
    os.system(cmd)
    return filename




def main():
    print("-----------------")
    print("Text-to-speech using AWS Polly")
    start_time = datetime.now()  # Timer

    # Setup
    create_output_directories()

    print(mode)



    tts_from_csv(input_file)


    # Timer
    completion_time = datetime.now() - start_time
    print("-----------------")
    print("Completed time: ", str(completion_time))  # TODO: Format time better


if __name__ == "__main__":
    main()
