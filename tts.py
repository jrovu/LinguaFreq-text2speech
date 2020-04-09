import os



input_dir = "_Input/"
input_file = "sentences.txt"
output_dir = "_Output/"
#voice_id = "Zhiyu" 
voice_id = "Lupe" 
padding = 1 # How many seconds of silence at end of padded mp3s
voice_speed = 50 # percent

print("Text to Speech using AWS Polly")

with open(input_dir + input_file, "r") as file:

	print("Opened file: " + input_dir + input_file)

	for line in file:

		# Strip newlines from the lines
		stripped_line = line.strip()
		filename = stripped_line + ".mp3"

		print("-----------------")
		print("Processing: " + stripped_line)
		print("-----------------")

		ssml_formatted_text = "<speak><prosody rate='{voice_speed}%'>{stripped_line}</prosody></speak>".format(voice_speed=voice_speed, stripped_line=stripped_line)
		#print(ssml_formatted_text)
		
		# Build command for AWS Polly
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
		os.system(polly_cmd)
		print(polly_cmd)


		ffmpeg_cmd = '''
		ffmpeg -i "{output_dir}{filename}" -af "apad=pad_dur=1" "{output_dir}padded/{filename}"
		'''.format(output_dir=output_dir, filename=filename)
		os.system(ffmpeg_cmd)
		print(ffmpeg_cmd)

