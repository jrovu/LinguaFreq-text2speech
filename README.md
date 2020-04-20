# batch-text2speech
Creates voice audio files from a list of sentences, using AWS Polly (text-to-speech)

Example for Chinese, at 90% speed
`./tts.py -f example_chinese.csv --foreign_voice Zhiyu  --english_voice Joanna --english_voice_engine neural -s 90`

Example for Spanish at 90% speed
`./tts.py -f example_spanish.csv --foreign_voice Lupe --foreign_voice_engine neural --english_voice Joanna --english_voice_engine neural -s 90`
