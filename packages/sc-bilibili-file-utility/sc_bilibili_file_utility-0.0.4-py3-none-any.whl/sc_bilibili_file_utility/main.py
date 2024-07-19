# The MIT License (MIT)
#
# Copyright (c) 2024 Scott Lau
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging

from sc_utilities import Singleton
from sc_utilities import log_init

log_init()

from sc_config import ConfigUtils
from sc_bilibili_file_utility import PROJECT_NAME, __version__
import argparse

import subprocess
import os
import json


class Runner(metaclass=Singleton):

    def __init__(self):
        project_name = PROJECT_NAME
        ConfigUtils.clear(project_name)
        self._config = ConfigUtils.get_config(project_name)
        self._target_directory = self._config.get("output.directory")
        self._process_result_file = self._config.get("output.process_result_file")
        self._processed_list = list()

        self._codec = self._config.get("output.codec")
        self._audio_filename = self._config.get("output.filename.audio")
        self._video_filename = self._config.get("output.filename.video")
        self._ext_av = self._config.get("output.filename.extension.av")
        self._ext_audio = self._config.get("output.filename.extension.audio")

        self._input_file_ext = self._config.get("scan.file.input_file_ext")
        self._output_audio_filename = "{}{}".format(self._audio_filename, self._input_file_ext)
        self._output_video_filename = "{}{}".format(self._video_filename, self._input_file_ext)

        self._video_list = list()
        video_list = self._config.get("scan.file.video_list")
        if video_list is not None and isinstance(video_list, list):
            self._video_list.extend(video_list)

        self._mac_entry_filename = self._config.get("scan.file.mac.entry_file")
        self._mac_group_name_field = self._config.get("scan.file.mac.group_name_field")
        self._mac_file_name_field = self._config.get("scan.file.mac.file_name_field")
        self._mac_progress_field = self._config.get("scan.file.mac.progress_field")
        mac_file_header = self._config.get("scan.file.mac.file_header")
        if mac_file_header is not None and isinstance(mac_file_header, str):
            self._mac_file_header = mac_file_header.encode('utf-8')
        audio_file_mark = self._config.get("scan.file.mac.audio_file_mark")
        if audio_file_mark is not None and isinstance(audio_file_mark, str):
            self._audio_file_mark = audio_file_mark.encode('utf-8')
        video_file_mark = self._config.get("scan.file.mac.video_file_mark")
        if video_file_mark is not None and isinstance(video_file_mark, str):
            self._video_file_mark = video_file_mark.encode('utf-8')

        self._phone_entry_filename = self._config.get("scan.file.phone.entry_file")
        self._phone_group_name_field = self._config.get("scan.file.phone.group_name_field")
        self._phone_page_data_field = self._config.get("scan.file.phone.page_data_field")
        self._phone_page_data_part_field = self._config.get("scan.file.phone.page_data_part_field")

    def scandir_recursive(self, directory):
        for entry in os.scandir(directory):
            if entry.is_dir(follow_symlinks=False):
                self.scandir_recursive(entry.path)
            else:
                if entry.name == self._mac_entry_filename:
                    self.handle_mac_entry(entry.path)
                if entry.name == self._phone_entry_filename:
                    self.handle_phone_entry(entry.path)

    def merge(self, audio_file, video_file, output_filename, include_video=False):
        codec = self._codec
        extension = self._ext_av if include_video else self._ext_audio
        fullname = "{}{}".format(output_filename, extension)
        if include_video:
            result = subprocess.run(["ffmpeg", "-y", "-i", video_file, "-i", audio_file, "-c", codec, fullname])
        else:
            result = subprocess.run(["ffmpeg", "-y", "-i", audio_file, "-c", codec, fullname])
        return result.returncode

    def run(self, *, args):
        logging.getLogger(__name__).info("arguments {}".format(args))
        logging.getLogger(__name__).info("program {} version {}".format(PROJECT_NAME, __version__))
        logging.getLogger(__name__).info("configurations {}".format(self._config.as_dict()))

        self.read_processed_file()
        self.scandir_recursive(os.path.abspath("."))
        logging.getLogger(__name__).info("process finished")
        return 0

    @staticmethod
    def replace_illegal_chars(input_string):
        # Define illegal characters and their replacements
        illegal_chars = '\\/:*?"<>| '
        replacement_char = '_'

        # Create a translation table
        translation_table = str.maketrans(illegal_chars, replacement_char * len(illegal_chars))

        # Replace illegal characters
        result_string = input_string.translate(translation_table)

        return result_string

    def handle_mac_entry(self, path):
        logging.getLogger(__name__).info("found mac entry {}".format(path))
        with open(path, 'r') as f:
            data = json.load(f)
            if self._mac_progress_field not in data:
                logging.getLogger(__name__).error("field {} not found".format(self._mac_progress_field))
                return
            progress = data[self._mac_progress_field]
            if progress is None or progress != 100:
                logging.getLogger(__name__).error("file download progress {} not completed".format(progress))
                return
            if self._mac_group_name_field not in data:
                logging.getLogger(__name__).error("field {} not found".format(self._mac_group_name_field))
                return
            group_name = data[self._mac_group_name_field]
            group_name = Runner.replace_illegal_chars(group_name)
            logging.getLogger(__name__).info("group {}".format(group_name))
            if self._mac_file_name_field not in data:
                logging.getLogger(__name__).error("field {} not found".format(self._mac_file_name_field))
                return
            filename = data[self._mac_file_name_field]
            filename = Runner.replace_illegal_chars(filename)
            logging.getLogger(__name__).info("filename {}".format(filename))

            video_filename = None
            audio_filename = None
            # videoInfo.json 所在文件夹
            parent_directory = os.path.dirname(path)
            parent_directory_basename = os.path.basename(parent_directory)
            if parent_directory_basename in self._processed_list:
                logging.getLogger(__name__).info("{} already processed".format(parent_directory_basename))
                return
            include_video = parent_directory_basename in self._video_list
            # 先找特定的文件（audio.m4s, video.m4s）
            audio_filename_temp = os.path.join(parent_directory, self._output_audio_filename)
            if os.path.isfile(audio_filename_temp):
                audio_filename = audio_filename_temp
            if include_video:
                video_filename_temp = os.path.join(parent_directory, self._output_video_filename)
                if os.path.isfile(video_filename_temp):
                    video_filename = video_filename_temp
            if (not audio_filename) or (include_video and not video_filename):
                # 如果找不到，则需要遍历此目录
                for entry in os.scandir(parent_directory):
                    if entry.is_dir(follow_symlinks=False):
                        continue
                    base_filename = os.path.basename(entry.path)
                    if not base_filename.endswith(self._input_file_ext):
                        continue
                    logging.getLogger(__name__).info("found file {}".format(entry.path))
                    with open(entry.path, 'rb') as file:
                        rewrite = False
                        first_line = file.readline()
                        if first_line and self._mac_file_header in first_line:
                            rewrite = True
                            first_line = first_line.replace(self._mac_file_header, b"")
                        contains_sound = self._audio_file_mark in first_line
                        contains_video = include_video and self._video_file_mark in first_line
                        # Read the rest of the file
                        rest_of_file = file.read()
                        contains_sound = contains_sound or self._audio_file_mark in rest_of_file
                        if contains_sound:
                            audio_filename = entry.path
                            if rewrite:
                                new_filename = self._output_audio_filename
                        contains_video = include_video and (contains_video or self._video_file_mark in rest_of_file)
                        if contains_video:
                            video_filename = entry.path
                            if rewrite:
                                new_filename = self._output_video_filename
                        if rewrite and (contains_sound or contains_video):
                            output_filename = os.path.join(parent_directory, new_filename)
                            logging.getLogger(__name__).info("rewriting file {}".format(output_filename))
                            with open(output_filename, 'wb') as output_file:
                                # Write the modified first line and the rest of the file to the new file
                                output_file.write(first_line)
                                output_file.write(rest_of_file)
                            if contains_sound:
                                audio_filename = output_filename
                            if contains_video:
                                video_filename = output_filename

            if not audio_filename:
                logging.getLogger(__name__).error("audio file not found")
                return
            if include_video and not video_filename:
                logging.getLogger(__name__).error("video file not found")
                return
            group_directory = os.path.join(self._target_directory, group_name)
            if not os.path.exists(group_directory):
                os.makedirs(group_directory)
            target_filename = os.path.join(self._target_directory, group_name, filename)
            return_code = self.merge(audio_filename, video_filename, target_filename, include_video)
            logging.getLogger(__name__).info("ffmpeg merge result {}".format(return_code))
            if return_code != 0:
                logging.getLogger(__name__).error(
                    "failed to merge file audio {}, include video {} video {}"
                    .format(audio_filename, include_video, video_filename))
                return
            process_result_file_path = os.path.join(self._target_directory, self._process_result_file)
            with open(process_result_file_path, 'a') as output_file:
                output_file.write("{}\n".format(parent_directory_basename))

    def handle_phone_entry(self, path):
        logging.getLogger(__name__).info("found phone entry {}".format(path))
        with open(path, 'r') as f:
            data = json.load(f)
            if self._phone_group_name_field not in data:
                logging.getLogger(__name__).error("field {} not found".format(self._phone_group_name_field))
                return
            group_name = data[self._phone_group_name_field]
            group_name = Runner.replace_illegal_chars(group_name)
            logging.getLogger(__name__).info("group {}".format(group_name))
            if self._phone_page_data_field not in data:
                logging.getLogger(__name__).error("field {} not found".format(self._phone_page_data_field))
                return
            page_data = data[self._phone_page_data_field]
            if self._phone_page_data_part_field not in page_data:
                logging.getLogger(__name__).error("field {} not found".format(self._phone_page_data_part_field))
                return
            filename = page_data[self._phone_page_data_part_field]
            logging.getLogger(__name__).info("filename {}".format(filename))
            if len(filename) == 0:
                logging.getLogger(__name__).info("filename is empty, using group name".format(group_name))
                filename = group_name
            filename = Runner.replace_illegal_chars(filename)

            video_filename = None
            audio_filename = None
            # entry.json 所在文件夹
            parent_directory = os.path.dirname(path)
            parent_directory_basename = os.path.basename(parent_directory)
            if parent_directory_basename in self._processed_list:
                logging.getLogger(__name__).info("{} already processed".format(parent_directory_basename))
                return
            include_video = parent_directory_basename in self._video_list
            for entry in os.scandir(parent_directory):
                if entry.is_file(follow_symlinks=False):
                    continue
                # entry.json 所在文件夹下的子目录
                for sub_entry in os.scandir(entry.path):
                    if sub_entry.is_dir(follow_symlinks=False):
                        continue
                    sub_entry_filename = os.path.basename(sub_entry.path)
                    if not sub_entry_filename.endswith(self._input_file_ext):
                        continue
                    logging.getLogger(__name__).info("found file {}".format(sub_entry.path))
                    if sub_entry_filename == self._output_audio_filename:
                        audio_filename = sub_entry.path
                    if sub_entry_filename == self._output_video_filename:
                        video_filename = sub_entry.path

            if not audio_filename:
                logging.getLogger(__name__).error("audio file not found")
                return
            if include_video and not video_filename:
                logging.getLogger(__name__).error("video file not found")
                return
            group_directory = os.path.join(self._target_directory, group_name)
            if not os.path.exists(group_directory):
                os.makedirs(group_directory)
            target_filename = os.path.join(self._target_directory, group_name, filename)
            return_code = self.merge(audio_filename, video_filename, target_filename, include_video)
            logging.getLogger(__name__).info("ffmpeg merge result {}".format(return_code))
            if return_code != 0:
                logging.getLogger(__name__).error(
                    "failed to merge file audio {}, include video {} video {}"
                    .format(audio_filename, include_video, video_filename))
                return
            process_result_file_path = os.path.join(self._target_directory, self._process_result_file)
            with open(process_result_file_path, 'a') as output_file:
                output_file.write("{}\n".format(parent_directory_basename))

    def read_processed_file(self):
        process_result_file_path = os.path.join(self._target_directory, self._process_result_file)
        if not os.path.exists(process_result_file_path):
            logging.getLogger(__name__).info("processed file {} not found".format(process_result_file_path))
            return

        logging.getLogger(__name__).info("read processed file {}".format(process_result_file_path))
        with open(process_result_file_path, 'r') as file:
            # Read the file contents into a list and strip the newline characters
            lines = [line.strip() for line in file.readlines()]
            self._processed_list.extend(lines)


def main():
    try:
        parser = argparse.ArgumentParser(description='Python project')
        args = parser.parse_args()
        state = Runner().run(args=args)
    except Exception as e:
        logging.getLogger(__name__).exception('An error occurred.', exc_info=e)
        return 1
    else:
        return state
