# ENUNU for Linux

This software allows you to use [NNSVS-singing-models](https://github.com/nnsvs/nnsvs) like [UTAU-VBs](https://github.com/adventHymnals/openUtau). It runs as a service. Install once and forget about it, unless you need to mess around with it abit.

For the windows version you can check [Enunu for Windows](https://github.com/stakira/ENUNU/releases)

## Requirements
- python 3.8
- [OpenUtau for Linux]((https://github.com/adventHymnals/openUtau).)

## Notes

1. This version is a standalone python application. It does not run as a plugin. No need to put it in the Plugins folder.
2. I couldn't get pysinsy to build in my system, so I built it in colab and included it as a dependency with this repo. You may need to rebuild it for your system. 
3. Since the files written by enunu server running as a service are owned by `root:root`, the work-around has been adopted of changing their ownership to `nobody:nogroup`

## Installing

Manually download from [releases](https://github.com/adventHymnals/ENUNU/releases) or run:
```bash
curl --silent "https://api.github.com/repos/adventHymnals/ENUNU/releases/latest"|   grep "browser_download_url.*amd64.deb" | head -n 1 | cut -d : -f 2,3 | tr -d \"  | xargs wget -O tmp.deb && sudo dpkg -i tmp.deb
```

### Uninstalling
```bash
sudo apt remove enunu
```

## Usage
### In dev mode

```bash
## just in case 
sudo apt install python3-pip
sudo apt install python3.8-venv

python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt --no-cache-dir
```

Or just run
```bash
./enunu_server.sh
```

## Tips

- It is recommended to include the consonant in the previous note.
  - \[さ]\[っ]\[ぽ]\[ろ] → \[さっ]\[ぽ]\[ろ]
- It does not support multi-syllable-hiragana-lyric in one note, except for "っ".
 Lets you enter phonemes directly, separated by spaces. Can be used with hiragana, but cannot be mixed in one note.
  - \[い]\[ら]\[ん]\[か]\[ら]\[ぷ]\[て] → \[i]\[r a]\[N]\[k a]\[ら]\[p]\[て]
- You can have more than one syllable in a note by entering phonemes directly.
  - \[さっ]\[ぽ]\[ろ] → \[さっ]\[p o r o]

## Terms of Use

Please follow the rules of each VB or singing-model when using. The terms of this software are provided separately as LICENSE files.




---

Following contents are for developers.

---



## Development Environment

- Ubuntu 22.04
- Python 3.8
  - utaupy 1.14.1
  - numpy 1.21.2（do not use 1.19.4）
  - torch 1.7.0+cu101
  - nnsvs (develepment version)
  - nnmnkwii (develepment version)
- CUDA 11.0


## Notes about LAB file format

The full context label specification is different from Sinsy's. Important differences include:.

- Does not handle information about phrases (e18 - e25, g, h, i, j3)
- Do not use musical symbols such as note strength (e 26 - e 56)
- does not deal with information about measures (e10 - e17, j2, j3)
- Does not handle beat information (c4, d4, e4)
- Relative note pitch (d2, e2, f2) specifications are different
  Since the key of the note cannot be obtained, the octave information is ignored and the relative pitch is assumed to be C = 0.
- Lock note key (d3, e3, f3) to 120
  - 120 if not manually specified
  Any value that is a multiple of -12 and does not appear on the Sinsy label can be substituted. (24, etc.)
- **Note and syllable information (a, c, d, f) are different with rest in between**
  - According to the Sinsy specification, the "Next Note" information in the note immediately before the rest points to the note after the rest, but this tool is designed to point to the rest.
  - Notes immediately following a rest are similarly designed to point to the rest itself, not to the start of the rest.
  - Same with syllables.

## Todo
See [issues]()
- [ ] Making this work in a remote server
- [ ] Building a web frontend for this to replace OpenUtau.
