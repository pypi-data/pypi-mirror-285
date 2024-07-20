# srtseg

Extend srt lib and allow video to be segmented according to subtitle. Also provide m3u8, webttv etc

The simplest file format is .srt, and it can be handled pretty well with srt lib.
srtseg provides the additional feature on top of srt:

- Get duration of each video (cut in the middle of the space between two subtitle)
- Segment selection
- M3U8 export
- WebVTT export
