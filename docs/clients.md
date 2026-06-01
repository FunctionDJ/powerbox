<sub>"why no emojis?" because emojis (and unicode checkmark symbols etc) in big markdown tables are a [pain](https://github.com/microsoft/vscode/issues/100730)</sub>

|                                                                                  | Poweramp Pro[^1]     | Musicolet     | Retro Music   | Spotify Premium[^2] | [Fossify Music Player](https://github.com/FossifyOrg/Music-Player)[^3] | [Oto Music](https://play.google.com/store/apps/details?id=com.piyush.music)[^4] | [AIMP](https://aimp.ru/?do=download&os=android) | [Pulsar Music Player](https://rhmsoft.com/pulsar/index.html) |
| -------------------------------------------------------------------------------- | -------------------- | ------------- | ------------- | ------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------ |
| Type                                                                             | Payware, Google Play | F-Droid       | F-Droid       | Google Play         | F-Droid                                                                | Google Play                                                                     | Google-Play                                     | Google-Play                                                  |
| Scans / adopts external playlists                                                | y                    | n             | n             | n                   | n                                                                      | n                                                                               | n                                               | n                                                            |
| Hierarchical (external) playlist view                                            | n                    | n             | n             | n                   | n                                                                      | n                                                                               | n                                               | n                                                            |
| Supports powerbox playlists (.m3u8 with relative paths) (e.g. by importing them) | y                    | y             | y[^5]         | n                   | n                                                                      | n                                                                               | y                                               | y                                                            |
| Supports opening powerbox playlists from a file explorer app                     | y                    | y             | n             | n                   | n                                                                      | n                                                                               | y                                               | n                                                            |
| Has _some_ sort of waveform                                                      | y                    | n             | n             | n                   | n                                                                      | n                                                                               | y                                               | n                                                            |
| Design & UX impression (subjective of course)                                    | 4/5                  | 5/5           | 4/5           | 3/5                 | 3/5                                                                    | 4/5                                                                             | 4/5                                             | 3/5                                                          |
| Version checked                                                                  | 1024004              | 5300          | 6.6.0 Pro     | 9.1.52.1394         | 1.8.1                                                                  | 4.0.7                                                                           | 4.30.1728                                       | 1.13.11 (v291)                                               |
| Date checked                                                                     | 30th May 2026        | 30th May 2026 | 30th May 2026 | 30th May 2026       | 30th May 2026                                                          | 30th May 2026                                                                   | 30th May 2026                                   | 1st Jun 2026                                                 |

[^1]: Poweramp Pro is almost perfect and was the intended client for powerbox, but it shows external playlists in a flat list

[^2]: including Spotify is a bit of a joke, but it's widely used for streaming

[^3]: Fossify feels like it's a fork of Musicolet or Retro or vice-versa

[^4]: Oto has an import feature but playlists show as "0" tracks (will have to re-test with music permissions instead of storage scopes)

[^5]:
    Works if permission is given for Music in general.
    When only using Storage Scopes for just the powerbox export (which includes both playlist and music files), imported playlists show up as having "0" tracks. This might apply to all apps - I have not tested this thoroughly yet.
    Weird.

General notes:

- all tests done on Pixel 7 Pro, Android 16, GrapheneOS
- notes for individual apps or features are marked using footnotes and I recommend reading them

TODO:

- Music Player Go
- Phonograph
- Vinyl Music Player (Phonograph fork)
- Simple Music Player
- Metro (Retro fork)
- Timber (deprecated)
- TimberX (unmaintained)
- Canaree
- Shuttle (Shuttle 2?)
- Symphony
- CuteMusic
- Auxio
- VLC
- Metrolist
- EffinMusic
- Castafiore
- Chora
- PlayNavi (alpha)
- Musly
- Tempus
- Lotus
- Flamingo
- Namida
- PixelPlayer
- Rhythm
- Finamp (idk if it makes sense because streaming)
- BoomingMusicPlayer
- Phocid
- Gonemad
- Black Player
- Pulsar (Pulsar+?)
- Symfonium
- Neutron Music Player
