#!/bin/bash

echo "Text to Speech using AWS Polly"

input="_Input/sentences.txt"
output="_Output/"

echo "Using $input as input."

# Open a text file

# Loop over each line

while IFS= read -r line
do
#	echo "$line"

	filename="$output$line"
	touch "${filename}"

done < "$input"




# Read in each line

# Pass the line as a text to speech, and also the output file name

# Save as a file

# Add gap







#aws polly synthesize-speech \ 
#    --output-format mp3 \
#    --voice-id Joanna \
#    --text 'Hello, my name is Joanna. I learned about the W3C on 10/3 of last year.' \
#    hello.mp3
