# not an official test package

from novus_pytils import files, wav
for file in files.get_files_by_extension("/media/john/The Archive/bioamla_data", [".wav"]):
    print(wav.read_wav_file_metadata(file))
