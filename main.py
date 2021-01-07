from __future__ import unicode_literals
import pandas as pd
import os
import os.path as osp
import re

import youtube_dl
from pydub import AudioSegment
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description='args')
    parser.add_argument('meta', help='path to meta data')
    return parser.parse_args()


def to_second(x):
    if x is not None:
        h, m, s = x
        h = int(h) if h.isdigit() else 0
        print(h, m, s)
        return int(m)*60+int(s)+h*3600
    else:
        return x


def parse_meta(text):
    po = re.compile('(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)')
    times = po.findall(text)
    times = [_ for _ in times if _[1] != '']
    if len(times) == 2:
        st, et = times
    elif len:
        st, et = times[0], None
    else:
        import ipdb
        ipdb.set_trace()
    # index = text
    # name = text[:index].replace('\n', '')
    out = dict(name=text, st=to_second(st), et=to_second(et))
    print(st)
    return out


def download_youtube_mp3(link, out=None):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],

    }
    if out is not None:
        ydl_opts['outtmpl'] = out

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])


def compete_et(meta_sounds, max_sound_length=-1):
    for i, meta in enumerate(meta_sounds):
        if meta['et'] is not None:
            et = meta['et']
        else:
            if i != len(meta_sounds) - 1:
                et = meta_sounds[i+1]['st']
            else:
                et = max_sound_length
        meta['et'] = et
    df = pd.DataFrame.from_dict(meta_sounds)
    df['duration'] = df['et']-df['st']
    print(df)

    return meta_sounds


def main():
    args = parse_args()
    with open(args.meta) as f:
        lines = f.readlines()

    link = lines[0].replace('\n', '')
    out = lines[1].replace('\n', '')+'.mp3'
    out_split_dir = out.split('.')[0]

    lines = lines[2:]

    if not osp.exists(out):
        download_youtube_mp3(link, out)

    meta_sounds = [parse_meta(text) for text in lines]
    meta_sounds = compete_et(meta_sounds)
    print(f'Reading {out}')
    sound = AudioSegment.from_file(out)

    print('Parsing')
    os.makedirs(out_split_dir, exist_ok=True)
    for i, meta in enumerate(meta_sounds):
        print("Exporting:", meta)
        song_sound = sound[meta['st']*1000:meta['et']*1000]
        song_name = f"{meta['name']}.mp3"
        out_path = osp.join(out_split_dir, song_name)
        song_sound.export(out_path, format="mp3")


if __name__ == '__main__':
    main()
