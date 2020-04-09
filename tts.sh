#!/bin/bash

echo "Text to Speech using AWS Polly"

# TODO: Make these configurable
input_dir="_Input/"
input_file="sentences.txt"
output_dir="_Output/"

echo "Using ${input_dir}${input_file} as input."


# Loop over each line of input file
while read -r line
do

	echo ""
	echo "-------------------------"
	echo "Processing: $line"
	echo "-------------------------"
	
	# Name the file based off the text
	filename="${line}.mp3"
	echo $filename

	# Create MP3s using AWS Polly
	echo aws polly synthesize-speech \
	   --output-format mp3 \
	   --voice-id Zhiyu \
	   --text "${line}" \
	   "${output_dir}${filename}"

	
	#ffmpeg -i "${output_dir}${filename}" -af "apad=pad_dur=1" "${output_dir}padded/${filename}"
	



done < "${input_dir}${input_file}"


# Add gap

# Voiecs
# Chinese Zhiyu
# Lupe


# Voice list: https://docs.aws.amazon.com/polly/latest/dg/voicelist.html
# Polly Console: https://console.aws.amazon.com/polly/home/SynthesizeSpeech
# Voice speed: https://docs.aws.amazon.com/polly/latest/dg/voice-speed-vip.html


#aws polly synthesize-speech \ 
#    --output-format mp3 \
#    --voice-id Joanna \
#    --text 'Hello, my name is Joanna. I learned about the W3C on 10/3 of last year.' \
#    hello.mp3


# WISHLIST
# [_] Add padding equal to length of clip
# [_] Speed 
# [_] Background sounds eg coffee shop