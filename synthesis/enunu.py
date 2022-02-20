#! /usr/bin/env python3
# coding: utf-8
# Copyright (c) 2020 oatsu
"""
1. UTAUプラグインのテキストファイルを読み取る。
  - 音源のフォルダを特定する。
  - プロジェクトもしくはUSTファイルのパスを特定する。
2. LABファイルを(一時的に)生成する
  - キャッシュフォルダでいいと思う。
3. LABファイル→WAVファイル
"""
from datetime import datetime
from os import chdir, makedirs, startfile
from os.path import basename, dirname, exists, join, splitext
from shutil import copy
from sys import argv
from tempfile import mkdtemp

import colored_traceback.always  # pylint: disable=unused-import
import utaupy
from omegaconf import DictConfig, OmegaConf

from enulib.duration import timelag2duration
from enulib.extensions import run_extension
from enulib.timelag import score2timelag
from enulib.utauplugin2hts import utauplugin2hts

# try:
#     from hts2wav import hts2wav
# except ModuleNotFoundError:
#     print('----------------------------------------------------------')
#     print('初回起動ですね。')
#     print('PC環境に合わせてPyTorchを自動インストールします。')
#     print('インストール完了までしばらくお待ちください。')
#     print('----------------------------------------------------------')
#     from install_torch import pip_install_torch
#     pip_install_torch(join('.', 'python-3.8.10-embed-amd64', 'python.exe'))
#     print('----------------------------------------------------------')
#     print('インストール成功しました。歌声合成を始めます。')
#     print('----------------------------------------------------------\n')
#     from hts2wav import hts2wav  # pylint: disable=ungrouped-imports


def get_project_path(path_utauplugin):
    """
    キャッシュパスとプロジェクトパスを取得する。
    """
    plugin = utaupy.utauplugin.load(path_utauplugin)
    setting = plugin.setting
    # ustのパス
    path_ust = setting.get('Project')
    # 音源フォルダ
    voice_dir = setting['VoiceDir']
    # 音声キャッシュのフォルダ(LABとJSONを設置する)
    cache_dir = setting['CacheDir']

    return path_ust, voice_dir, cache_dir


def full2mono(path_full, path_mono):
    """
    フルラベルをモノラベルに変換して保存する。
    """
    full_label = utaupy.hts.load(path_full)
    mono_label = full_label.as_mono()
    mono_label.write(path_mono)


def main_as_plugin(path_plugin: str) -> str:
    """
    UtauPluginオブジェクトから音声ファイルを作る
    """
    # UTAUの一時ファイルに書いてある設定を読み取る
    print(f'{datetime.now()} : reading setting in TMP')
    path_ust, voice_dir, _ = get_project_path(path_plugin)
    path_enuconfig = join(voice_dir, 'enuconfig.yaml')

    # configファイルがあるか調べて、なければ例外処理
    if not exists(path_enuconfig):
        raise Exception(
            '音源フォルダに enuconfig.yaml が見つかりません。'
            'UTAU音源選択でENUNU用モデルを指定してください。'
        )
    # カレントディレクトリを音源フォルダに変更する
    chdir(voice_dir)

    # configファイルを読み取る
    print(f'{datetime.now()} : reading enuconfig')
    config = DictConfig(OmegaConf.load(path_enuconfig))

    # 日付時刻を取得
    str_now = datetime.now().strftime('%Y%m%d_%H%M%S')
    # 入出力パスを設定する
    if path_ust is not None:
        songname = splitext(basename(path_ust))[0]
        out_dir = dirname(path_ust)
        temp_dir = join(out_dir, f'{songname}_enutemp')
    # USTが未保存の場合
    else:
        print('USTが保存されていないので一時フォルダにWAV出力します。')
        songname = f"temp__{str_now}"
        temp_dir = mkdtemp(prefix='enunu-')
        out_dir = temp_dir

    # 一時出力フォルダがなければつくる
    makedirs(temp_dir, exist_ok=True)
    # 各種出力ファイルのパスを設定
    path_temp_ust = join(temp_dir, 'temp.ust')
    path_full_score = join(temp_dir, 'score.full')
    path_mono_score = join(temp_dir, 'score.lab')
    path_full_timelag = join(temp_dir, 'timelag.full')
    path_mono_timelag = join(temp_dir, 'timelag.lab')
    path_full_duration = join(temp_dir, 'duration.full')
    path_mono_duration = join(temp_dir, 'duration.lab')
    path_full_timing = join(temp_dir, 'timing.full')
    path_mono_timing = join(temp_dir, 'timing.lab')
    path_f0 = join(temp_dir, 'acoustic.f0')
    path_bap = join(temp_dir, 'acoustic.bap')
    path_mgc = join(temp_dir, 'acoustic.mgc')
    path_wav = join(out_dir, f'{songname}__{str_now}.wav')

    # USTを一時フォルダに複製
    print(f'{datetime.now()} : copying UST(for UTAU-plugins)')
    copy(path_plugin, path_temp_ust)

    # USTを事前加工
    ust_editor = config.get('ust_editor')
    if ust_editor is not None:
        print(f'{datetime.now()} : editing UST(for UTAU-plugins) with {ust_editor}')
        run_extension(
            ust_editor,
            ust=path_temp_ust
        )

    # フルラベル(score)生成
    print(f'{datetime.now()} : converting UST(for UTAU-plugins) to LAB(score)')
    utauplugin2hts(
        path_temp_ust,
        config.table_path,
        path_full_score,
        path_mono_out=path_mono_score,
        strict_sinsy_style=(not config.trained_for_enunu)
    )

    # フルラベル(score)を加工
    editor = config.get('score_editor')
    if editor is not None:
        print(f'{datetime.now()} : editing score with {editor}')
        full2mono(path_full_score, path_mono_score)
        run_extension(
            editor,
            ust=path_temp_ust,
            full_score=path_full_score,
            mono_score=path_mono_score
        )

    # フルラベル(timelag)を生成: score.full -> timelag.full
    print(f'{datetime.now()} : converting TMP to LAB(timelag)')
    score2timelag(config, path_full_score, path_full_timelag)

    # フルラベル(timelag)を加工: timelag.full -> timelag.full
    editor = config.get('timelag_editor')
    if editor is not None:
        print(f'{datetime.now()} : editing timelag with {editor}')
        run_extension(
            editor,
            ust=path_temp_ust,
            full_score=path_full_score,
            mono_score=path_mono_score,
            full_timelag=path_full_timelag,
            mono_timelag=path_mono_timelag
        )

    # フルラベル(duration) を生成 score.full & timelag.full -> duration.full
    print(f'{datetime.now()} : predicting Timelag features')
    timelag2duration(config, path_full_score, path_full_timelag)

    # フルラベル(duration)を加工: duration.full -> duration.full
    editor = config.get('duration_editor')
    if editor is not None:
        print(f'{datetime.now()} : editing duration with {editor}')
        run_extension(
            editor,
            ust=path_temp_ust,
            full_score=path_full_score,
            mono_score=path_mono_score,
            full_timelag=path_full_timelag,
            mono_timelag=path_mono_timelag,
            full_duration=path_full_duration,
            mono_duration=path_mono_duration
        )

    # フルラベル(timing) を生成 timelag.full & duration.full -> timing.full
    print(f'{datetime.now()} : generationg LAB(timing)')
    duration2timing(config, path_full_score,
                    path_full_timelag, path_full_duration)

    # フルラベル(timing) を加工: timing.full -> timing.full
    editor = config.get('timing_editor')
    if editor is not None:
        print(f'{datetime.now()} : editing timing with {editor}')
        run_extension(
            editor,
            ust=path_temp_ust,
            full_score=path_full_score,
            mono_score=path_mono_score,
            full_timelag=path_full_timelag,
            mono_timelag=path_mono_timelag,
            full_duration=path_full_duration,
            mono_duration=path_mono_duration,
            full_timing=path_full_timing,
            mono_timing=path_mono_timing
        )

    # 音響パラメータを推定 timing.full -> f0, bap, mgc
    print(f'{datetime.now()} : predicting acoustic features')
    timing2acoustic(config, path_full_timing, path_f0, path_bap, path_mgc)

    # 音響パラメータを加工: timing.full -> timing.full
    editor = config.get('acoustic_editor')
    if editor is not None:
        print(f'{datetime.now()} : editing acoustic with {editor}')
        run_extension(
            editor,
            ust=path_temp_ust,
            full_score=path_full_score,
            mono_score=path_mono_score,
            full_timelag=path_full_timelag,
            mono_timelag=path_mono_timelag,
            full_duration=path_full_duration,
            mono_duration=path_mono_duration,
            full_timing=path_full_timing,
            mono_timing=path_mono_timing,
            f0=path_f0,
            bap=path_bap,
            mgc=path_mgc
        )

    # WORLDを使って音声ファイルを生成: f0, bap, mgc -> <songname>.wav
    print(f'{datetime.now()} : synthesizing WAV')
    acoustic2wav(
        config,
        path_wav,
        path_f0=path_f0,
        path_bap=path_bap,
        path_mgc=path_bap
    )

    # 音声ファイルを加工: <songname>.wav -> <songname>.wav
    editor = config.get('wav_editor')
    if editor is not None:
        print(f'{datetime.now()} : editing WAV with {editor}')
        run_extension(
            editor,
            ust=path_temp_ust,
            full_score=path_full_score,
            mono_score=path_mono_score,
            full_timelag=path_full_timelag,
            mono_timelag=path_mono_timelag,
            full_duration=path_full_duration,
            mono_duration=path_mono_duration,
            full_timing=path_full_timing,
            mono_timing=path_mono_timing,
            f0=path_f0,
            bap=path_bap,
            mgc=path_mgc,
            wav=path_wav
        )

    # print(f'{datetime.now()} : converting LAB to JSON')
    # hts2json(path_full_score, path_json)

    # Windowsの時は音声を再生する。
    startfile(path_wav)

    return path_wav


def main(path: str):
    """
    入力ファイルによって処理を分岐する。
    """
    # logging.basicConfig(level=logging.INFO)
    if path.endswith('.tmp'):
        main_as_plugin(path)
    else:
        raise ValueError('Input file must be TMP(plugin).')


if __name__ == '__main__':
    print('_____ξ ・ヮ・)ξ < ENUNU v0.2.5 ________')
    print(f'argv: {argv}')
    if len(argv) == 2:
        main(argv[1])
    elif len(argv) == 1:
        main(input('Input file path of TMP(plugin)\n>>> ').strip('"'))
    else:
        raise Exception('引数が多すぎます。')
