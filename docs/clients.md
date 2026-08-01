<sub>"why no emojis?" because emojis (and unicode checkmark symbols etc) in big markdown tables are a [pain](https://github.com/microsoft/vscode/issues/100730)</sub>

|                                                                                  | Poweramp Pro[^1]     | Musicolet     | Retro Music   | Spotify Premium[^2] | [Fossify Music Player](https://github.com/FossifyOrg/Music-Player)[^3] | [Oto Music](https://play.google.com/store/apps/details?id=com.piyush.music) | [AIMP](https://aimp.ru/?do=download&os=android) | [Pulsar Music Player](https://rhmsoft.com/pulsar/index.html) |
| -------------------------------------------------------------------------------- | -------------------- | ------------- | ------------- | ------------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------ |
| Type                                                                             | Payware, Google Play | F-Droid       | F-Droid       | Google Play         | F-Droid                                                                | Google Play                                                                 | Google-Play                                     | Google-Play                                                  |
| Scans / adopts external playlists                                                | Yes                  | No            | No            | No                  | No                                                                     | No                                                                          | No                                              | No                                                           |
| Hierarchical (external) playlist view                                            | No                   | No            | No            | No                  | No                                                                     | No                                                                          | No                                              | No                                                           |
| Supports powerbox playlists (.m3u8 with relative paths) (e.g. by importing them) | Yes                  | Yes           | Yes[^5]       | No                  | No                                                                     | Yes[^4]                                                                     | Yes                                             | Yes                                                          |
| Supports opening powerbox playlists from a file explorer app                     | Yes                  | Yes           | No            | No                  | No                                                                     | No                                                                          | Yes                                             | No                                                           |
| Has _some_ sort of waveform                                                      | Yes                  | No            | No            | No                  | No                                                                     | No                                                                          | Yes                                             | No                                                           |
| Design & UX impression (subjective of course)                                    | 4/5                  | 5/5           | 4/5           | 3/5                 | 3/5                                                                    | 4/5                                                                         | 4/5                                             | 3/5                                                          |
| Version checked                                                                  | 1024004              | 5300          | 6.6.0 Pro     | 9.1.52.1394         | 1.8.1                                                                  | 4.0.7                                                                       | 4.30.1728                                       | 1.13.11 (v291)                                               |
| Date checked                                                                     | 30th May 2026        | 30th May 2026 | 30th May 2026 | 30th May 2026       | 30th May 2026                                                          | 30th May 2026                                                               | 30th May 2026                                   | 1st Jun 2026                                                 |

[^1]: Poweramp Pro is almost perfect and was the intended client for powerbox, but it shows external playlists in a flat list

[^2]: including Spotify is a bit of a joke, but it's widely used for streaming

[^3]: Fossify feels like it's a fork of Musicolet or Retro or vice-versa

[^4]: Wait until Oto's scan has finished - otherwise imported playlists may contain "0" tracks

[^5]:
    Works if permission is given for Music in general.
    When only using Storage Scopes for just the powerbox export (which includes both playlist and music files), imported playlists show up as having "0" tracks. This might apply to all apps - I have not tested this thoroughly yet.
    Weird.

General notes:

- all tests done on Pixel 7 Pro, Android 16, GrapheneOS
- I've experienced some difference in features depending on if I give general "Music" permissions vs. narrower Storage Scopes for just the powerbox export (includes playlist and music files)
- notes for individual apps or features are marked using footnotes and I recommend reading them

Clients I won't test because they're unmaintained (you're welcome to test and add them to the table with a PR):

- [Music Player Go](https://github.com/enricocid/Music-Player-GO)
- [Phonograph](https://github.com/karimknaebel/Phonograph)
- [Vinyl Music Player](https://github.com/VinylMusicPlayer/VinylMusicPlayer) (Phonograph fork)

TODO:

- [Simple Music Player](https://github.com/SimpleMobileTools/Simple-Music-Player)
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
