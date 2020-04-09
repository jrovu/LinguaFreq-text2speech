#!/bin/bash

echo "Text to Speech using AWS Polly"

# TODO: Make these configurable
input_dir="_Input/"
input_file="sentences.txt"
output_dir="_Output/"
silence_file="_Resources/1SecSilence.mp3"

echo "Using ${input_dir}${input_file} as input."


# Loop over each line of input file
while IFS= read -r line
do

	echo "Processing: $line"
	
	# Name the file based off the text
	filename="${line}.mp3"

	# Create MP3s using AWS Polly
	aws polly synthesize-speech \
	   --output-format mp3 \
	   --voice-id Lupe \
	   --text "${line}" \
	   "${output_dir}${filename}"

	
	#ffmpeg -i "concat:${output}${filename}|${silence_file}" -c copy 



done < "${input_dir}${input_file}"


# Add gap




# Voice list: https://docs.aws.amazon.com/polly/latest/dg/voicelist.html
# Polly Console: https://console.aws.amazon.com/polly/home/SynthesizeSpeech


#aws polly synthesize-speech \ 
#    --output-format mp3 \
#    --voice-id Joanna \
#    --text 'Hello, my name is Joanna. I learned about the W3C on 10/3 of last year.' \
#    hello.mp3
