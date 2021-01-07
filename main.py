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
    parser.add_argument('--save-to', default='downloads')
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


def refine_name(text):
    ignore_case = ['|', '[', ']', '\n', '/', ':', '-', '.']
    xx = re.compile('[0-9]+:[0-9]+')
    xxx = re.compile('[0-9]+:[0-9]+:[0-9]+')
    xxx = re.compile('[0-9]')
    for m in  xx.findall(text):
        text = text.replace(m, '')

    for m in  xxx.findall(text):
        text = text.replace(m, '')
    for case in ignore_case:
        text = text.replace(case, '')
    return text

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
        meta['refine_name'] = refine_name(meta['name'])
    df = pd.DataFrame.from_dict(meta_sounds)
    df['duration'] = df['et']-df['st']
    print(df)
    return meta_sounds


def main():
    args = parse_args()
    with open(args.meta) as f:
        lines = f.readlines()
    os.makedirs('cache', exist_ok=True)

    link = lines[0].replace('\n', '')

    out = 'cache/'+lines[1].replace('\n', '')+'.mp3'
    out_split_dir = osp.join(args.save_to, os.path.basename(out).split('.')[0])

    lines = lines[2:]

    if not osp.exists(out):
        download_youtube_mp3(link, out)

    meta_sounds = [parse_meta(text) for text in lines]
    meta_sounds = compete_et(meta_sounds)
    print(f'Reading {out}')
    sound = None
    os.makedirs(out_split_dir, exist_ok=True)
    for i, meta in enumerate(meta_sounds):
        song_name = f"{meta['refine_name']}.mp3"
        out_path = osp.join(out_split_dir, song_name)
        if not osp.exists(out_path):
            sound = AudioSegment.from_file(out) if sound is None else sound
            song_sound = sound[meta['st']*1000:meta['et']*1000]
            song_sound.export(out_path, format="mp3")
            print("Exporting:",meta,' -> ', out_path)

if __name__ == '__main__':
    main()
