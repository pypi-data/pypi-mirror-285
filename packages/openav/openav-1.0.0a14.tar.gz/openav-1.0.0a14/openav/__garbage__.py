# sphinx-intl update -p docs/build/gettext -l en -l ru
# sphinx-build -b gettext docs/source/ docs/build/gettext
# sphinx-build -a -b html -D language=ru ./docs/source ./docs/build/ru


# for front_cnt, _ in enumerate(self.__front):
#     torchaudio.save(
#         self.__part_audio_path[front_cnt],
#         self.__aframes[channel][
#             speech_timestamps[0]['start']:speech_timestamps[0]['end']
#         ].unsqueeze(0),
#         self.__file_metadata['audio_fps']
#     )


# torchaudio.save(
#     '/Users/dl/Desktop/test/' + str(cnt) + '.wav',
#     self.__aframes[channel].unsqueeze(0),
#     self.__file_metadata['audio_fps']
# )


# print(self.__part_video_path, self.__part_audio_path)

# continue
#
# print(speech_timestamps, start_time, end_time)
# print(str(Path(self.__local_path(self.__curr_path)).parent))
# print(self.__aframes[channel][0:10].shape, self.__aframes[channel].unsqueeze(0).shape)
# print(self.__aframes[channel].shape, speech_timestamps[0]['start'], speech_timestamps[0]['end'])
#
# torchaudio.save(
#     '/Users/dl/Desktop/test/' + str(cnt) + '_2.wav',
#     self.__aframes[channel][speech_timestamps[0]['start']:speech_timestamps[0]['end']].unsqueeze(0),
#     self.__file_metadata['audio_fps']
# )


# # Тип файла
# kind = filetype.guess(self.__curr_path)
#
# # Видео
# if kind.mime.startswith('video/') is True: pass
#
#
#
# continue

# import subprocess  # Работа с процессами
# # https://trac.ffmpeg.org/wiki/audio%20types
# # Выполнение в новом процессе
# with subprocess.Popen(
#         ['ffmpeg', '-loglevel', 'quiet', '-i', str(self.__curr_path)] + [] +
#         ['-ar', str(16000), '-ac', str(1), '-f', 's16le', '-'],
#         stdout = subprocess.PIPE) as process:
#     t = None
#
#     while True:
#         data = process.stdout.read(4000)
#         if len(data) == 0: break
#
#         if t is None:
#             t = torch.frombuffer(data, dtype = torch.float32)
#         else:
#             t = torch.cat((t, torch.frombuffer(data, dtype = torch.float32)), 0)
#         # print(t.shape, t[0:10])

# t = t.unsqueeze(0)
# t = t.view(t.shape[0], 1)
# print(type(t), t.shape)
# print(torch.flatten(t).shape)

# torchaudio.save('/Users/dl/Desktop/test/' + str(self.__i) + '.wav', t, 16000)

# Чтение аудиофайла
# self.__wav = read_audio(
#     '/Users/dl/@DmitryRyumin/Databases/LRW/LRW_AUDIO/ABSOLUTELY_00001.wav',
#     sampling_rate = 16000
# )
# # print(type(self.__wav), self.__wav[0:100])
# self.__wav = self.__wav.unsqueeze(0)
# torchaudio.save('/Users/dl/Desktop/test/' + str(self.__i) + '.wav', self.__wav, 16000)

# v, a, h = torchvision.io.read_video(
#     self.__curr_path
# )
#
# print(v.shape)
# print(a.shape)
# print(h)
# kind = filetype.guess(self.__curr_path)
# print(kind)
#
# torchaudio.save('/Users/dl/Desktop/test/' + str(self.__i) + '.wav', a, 16000)
