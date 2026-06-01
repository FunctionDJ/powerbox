# powerbox

Rekordbox exporter to take your library on-the-go.

#### What it does

- scans `master.db` for playlists and the tracks inside them
- supports folder remapping to run powerbox on a server or other machine where paths are different from where Rekordbox is installed
- compresses tracks to ~192kbit/s VBR AAC (configurable), preserving album art and embedded metadata
- writes playlist files (.m3u8) in the same folder hierarchy as Rekordbox
- designed to make a portable Rekordbox playlists+music copy to sync to a mobile phone (I use [syncthing-android](https://github.com/researchxxl/syncthing-android))

#### Why?

Because the official Rekordbox app is very bad and slow, syncing takes forever, and there's no support for external players or compressing files to save storage. I keep a lot of music in lossless formats, but I don't need that on my phone.

#### Clients

I use Android, so I can't evaluate apps on other platforms. I have not found a player yet that will scan for playlists and show them in a hierarchy. The workaround is opening playlists from a file explorer app or using a flat view, depending on the app.

See [docs/clients.md](docs/clients.md) for the clients I've tested and what they support.
TL;DR Poweramp Pro comes close, but has no hierarchical view for external playlists. It was the intended target client for this project, hence the name, but now I'm looking for a better one.

#### Configuration (required)

Copy `powerbox/user_settings_example.py` to `powerbox/user_settings.py` (this file has the role of a `.env`).
Configure accordingly.
I can't tell you the SQL cipher encryption key.

#### Install + Usage

Install `uv` (Python tooling) and run `uv run main.py`.

#### How do I automate this?

Use any scheduler, task runner, or init system you like.
I use systemd and there are some example service and timer unit files in `systemd`.
Or you can use https://netoz.au/tools/systemd-generator if you like.

#### Does this support smart playlists?

I've only tested a single one and it doesn't work (might be because of pyrekordbox). I don't plan to support this but PRs are welcome.

#### Does this support waveforms and cue points?

Some mobile music players support waveforms (see [clients](docs/clients.md)). You can use those, but powerbox itself doesn't write any waveform data.
Same for cue points, but if you know of a music player app (Android) that supports cue points from external files, let me know and I'll try to implement it. PRs are welcome.

#### Why not .opus?

I wanted to use Opus, but ffmpeg can't write album art to it, see https://trac.ffmpeg.org/ticket/4448 . Also I didn't want to add other dependencies and make the code more complicated to work around this limitation.
