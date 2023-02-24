#!/usr/bin/python
# -*- coding: utf-8 -*-

from math import ceil
import ffmpeg
import os
from colorama import Fore
import argparse

FG_GREEN = Fore.GREEN
FG_RED = Fore.RED
FG_YELLOW = Fore.YELLOW
FG_BLUE = Fore.BLUE
FG_CYAN = Fore.CYAN
FG_WHITE = Fore.WHITE
FG_RESET = Fore.RESET

parser = argparse.ArgumentParser(
	prog='Video extension Converter',
	description='Converts video extensions files to any other extension'
)

parser.add_argument('-i', '--input', help='Extension of the input files', required=False, default='ts')
parser.add_argument('-o', '--output', help='Extension of the output files', required=False, default='mp4')

skip_dirs = [
	'.git',
	'.vscode',
	'.idea',
	'node_modules',
	'__pycache__',
	'__MACOSX',
	'vendor',
	'bin',
	'venv'
]

def get_videos(folder_path, extension_input = 'ts', extension_output = 'mp4'):
	for root, dirs, files in os.walk(folder_path):
		remove_invalid_dirs(dirs)

		short_root = root.replace(folder_path, '')
		print(f'{FG_WHITE}Root:{FG_RESET} {FG_BLUE}{short_root}{FG_RESET} | {FG_WHITE}Directorios:{FG_RESET} {FG_BLUE}{len(dirs)}{FG_RESET} | {FG_WHITE}Archivos:{FG_RESET} {FG_BLUE}{len(files)}{FG_RESET}')
		success, failed = 0, 0

		for file in files:
			if file.endswith(f'.{extension_input}'):
				if (proccess_file(root, file, extension_input, extension_output)):
					success += 1
				else:
					failed += 1
		
		print(f'{FG_GREEN}Procesados:{FG_RESET} {success} | {FG_RED}Fallidos:{FG_RESET} {failed}\n')


def remove_invalid_dirs(dirs):
	for skip_dir in skip_dirs:
		if skip_dir in dirs:
			print(f'{FG_RED}Skipping directory:{FG_RESET} {FG_BLUE}{skip_dir}{FG_RESET}')
			dirs.remove(skip_dir)


def proccess_file(root:str, file:str, extension_input = 'ts', extension_output = 'mp4'):
	input_path = os.path.join(root, file)
	output_path = os.path.join(root, file.replace(f'.{extension_input}', f'.{extension_output}'))

	try:
		file_info = get_file_info(input_path)
	except ValueError as e:
		print(f'{FG_RED}{e}')
		return False

	print(f' - {FG_YELLOW}File:{FG_RESET} {FG_CYAN}{file}{FG_RESET} | {FG_WHITE}Size:{FG_RESET} {file_info["human_size"]} | {FG_WHITE}Width:{FG_RESET} {file_info["width"]} | {FG_WHITE}Height:{FG_RESET} {file_info["height"]}')
	crf = calc_crf(file_info)

	return convert_to_mp4(input_path, output_path, crf)


def get_file_info(file_path):
	probe = ffmpeg.probe(file_path)
	video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
	audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)

	file_name = os.path.basename(file_path)
	if video_stream is None:
		raise ValueError(f'No video stream found in {file_name}')
	if audio_stream is None:
		raise ValueError(f'No audio stream found in {file_name}')

	return {
		'file_path': file_path,
		'duration': probe['format']['duration'],
		'size': probe['format']['size'],
		'human_size': readable_size(int(probe['format']['size'])),
		'vcodec': video_stream['codec_name'],
		'acodec': audio_stream['codec_name'],
		'width': video_stream['width'],
		'height': video_stream['height'],
		'bitrate': probe['format']['bit_rate']
	}


def readable_size(byte:int):
	for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
		if byte < 1024:
			return f'{byte:.2f} {unit}'
		byte /= 1024


def calc_crf(fileinfo):
	size = ceil(float(fileinfo['size']))
	duration = ceil(float(fileinfo['duration']))
	bitrate = ceil(float(fileinfo['bitrate']))
	crf = 0

	# file < 50 mb crf = 0
	if size < 52428800:
		return crf

	crf = str(0.5 * (bitrate / 1000) * (duration / 100) * (size / 1000))
	crf = int(crf[:2]) - 10

	return 30 if crf > 31 else crf


def convert_to_mp4(video_path, output_path, crf):
	try:
		(
			ffmpeg
			.input(video_path)
			.output(output_path, **{
				'c:v': 'h264_nvenc',
				'rc': 'constqp',
				'crf': crf,
				'c:a': 'aac',
			})
			.run()
		)
		return True
	except ffmpeg.Error as e:
		print(e.stderr)
		return False


def read_bool_input(message, options = ['y', 'n'], default = None):
	while True:

		message += f' ({FG_YELLOW}{"/".join(options)}{FG_RESET}) ' if options is not None else ' '
		user_input = input(message).lower()

		if user_input == '' and default is not None:
			return True if default == 'y' else False
		elif user_input in options:
			return True if user_input == 'y' else False
		else:
			print(f'"{user_input}" no es una opción válida')


def ask_path():
	path = os.getcwd()
	print(f'{FG_WHITE}Directorio actual:{FG_RESET} {FG_BLUE}{path}{FG_RESET}')

	if read_bool_input(f'{FG_WHITE}¿Desea cambiar el directorio?{FG_RESET}', default='n'):
		path = input(f'{FG_WHITE}Ingrese el directorio:{FG_RESET} ')

		if not os.path.exists(path):
			print(f'{FG_RED}El directorio ingresado no existe{FG_RESET}')
			return None

	print()
	return path


def main():
	args = parser.parse_args()

	path = ask_path()
	if path is None:
		return

	get_videos(os.getcwd(), args.input, args.output)


if __name__ == '__main__':
	main()