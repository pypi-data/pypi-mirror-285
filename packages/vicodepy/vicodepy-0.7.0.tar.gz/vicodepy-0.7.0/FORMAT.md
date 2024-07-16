# Format specification of the project file

## Version 2 (published on 2024-07-16)

The project file is a [ZIP][] file and must have the file extension `.zip`.

[ZIP]: https://en.wikipedia.org/wiki/ZIP

It must contain no sub-directories. At the top-level directory of the ZIP file, a file `metadata.yml`, in [YAML][] format, must be present. This file must contain a single associative array, with two fields:

[YAML]: https://en.wikipedia.org/wiki/YAML

- `format`, whose value must be an integer, greater or equal to 1. This value specify the format version of the project file.

- `video`, whose value must be a string with the name of the video file. The associated file must exist at the top-level directory of the ZIP file.

The video file must be in any of the formats currently accepted by ViCodePy, whose MIME names are:

- video/mp4
- video/ogg
- video/quicktime
- video/vnd.avi
- video/webm
- video/x-matroska
- video/x-ms-wmv

Two other files may be present at the top-level directory of the project ZIP file:

1. A [CSV][] file containing information about the timelines and annotations. The name of this file must be the same as the video file, but with the `.csv` extension. This file is a text file, containing a data frame with comma-separated values. Each line corresponds to an annotation. The headers of this file must be the following:

```
timeline,label,begin,end,duration,comment
```

The types of the columns are the following:

- `timeline`: a string containing the name of the timeline, indicating where is the annotation associated with the line
- `label`: a string containing the label of the annotation
- `begin`: a float number, indicating the begin time of the annotation (in milliseconds)
- `end`: a float number, indicating the end time of the annotation (in milliseconds)
- `duration`: a float number indicating the duration of the annotation (in milliseconds)
- `comment`: a string containing comments associated with the annotation; the value can be multi-lined, in which case it must be delimited by double quote characters (`"`)

[CSV]: https://en.wikipedia.org/wiki/Comma-separated_values

2. A file named `config.yml`, in YAML format, containing the possible events that the annotations will represent. This file must contain a associative array, with, at least, a key `timelines`. The value of the `timeline` field must be a list. Each element of the list is an associative array with two fields: `name` and `events`. The value of the `name` field is a string containing the name of the timeline. The `events` field must contain a list of annotation events definitions. Each element of this list is an associative array with two fields: `name` and `color`. The value of the `name` field is a string corresponding to the label associated with the event. The value of the `color` field can be either a [SVG 1.0 color name][] or a [CSS 2 RGB specification][] and will be the color of the annotations representing the associated event.

[CSS 2 RGB specification]: https://www.w3.org/TR/SVG11/types.html#ColorKeywords
[SVG 1.0 color name]: https://www.w3.org/TR/2008/REC-CSS2-20080411/syndata.html#color-units

The timeline names and annotation labels appearing in the CSV must appear in the `config.yml` file.

Here is an example of the contents of a `config.yml` file (this is the current default content of the configuration file of ViCodePy):

```
timelines:
  - name: phase
    events:
      - name: fam
        color: yellow
      - name: test
        color: green
  - name: gaze
    events:
      - name: 0
        color: gainsboro
      - name: 1
        color: cyan
      - name: 2
        color: pink
```

The following are other optional fields recognized in `config.yml`:

- `csv-delimiter`: A string representing the delimiter in the CSV file (default: `,`)

- `coders`: A list of coder information. Each element of this list contains the identity of the person who did the video coding (name and email address) and the date and time of the last modifications. Each element must be an associated array with fields `name` (a string, *mandatory*), `email` (a string, *optional*), and `last-time` (a string representing the date and the time, in `datetime.strftime` format `%Y-%m-%d %H:%M:%S`, *optional*).

## History of changes in the format specification

### From version 1 (published on 2024-07-08)

Added the `coders` field to the `config.yml` file.
