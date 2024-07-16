# ViCodePy – Video coder in Python for Experimental Psychology

[![PyPI Version](https://img.shields.io/pypi/v/vicodepy)](https://pypi.org/project/vicodepy/)
![License](https://img.shields.io/pypi/l/vicodepy?color=blue)

ViCodePy is an application for doing video coding, written entirely in Python, meant essentially for use in Experimental Psychology. ViCodePy looks like a video editor, but it is not possible to alter the video file loaded into it. Instead, it is possible to add temporal annotations and save them as CSV (comma-separated value) files.

## Installation

The application can be installed via:

    python -m pip install vicodepy

## Usage

### Loading the video file

After launching the application (`vicodepy.exe` on Windows, `vicodepy` on Linux), a video file can be loaded via the menu entry `File⇒Open…`. Almost all popular video formats are supported.

### Playing/stopping the video and moving around it

Once the video is loaded, it can be played and stopped using the space key. The left and right arrow keys can be used for going backward and forward, respectively, by one frame in the video. Positioning the cursor (a black triangle) with the mouse is also possible by clicking and dragging the cursor on the timeline.

### Annotations

Annotations can be defined by pressing the enter key. This will mark one of the borders of the annotation. The other border can be defined by using the arrow keys or by clicking and dragging the cursor. Once the cursor is at the desired position, type enter again. This will open a dialog window for choosing the label and the color of the annotation. New labels can be defined in the dialog window by simply typing them. The new created labels will appear in the list of proposed labels when new annotations will be subsequently created.

Once an annotation is created, it is possible to change its borders by double-clicking on the annotation. Two handles will appear, one at the left border of the annotation and the other at the right border. Click on a border handle and move it with the left and right arrow keys.

The creation of an annotation can be aborted, once it is start by either typing the Escape key or by clicking on the Abort button in the pop-up window.

The timeline can be zoomed in and out by using the scroll wheel of the mouse.

The annotations can be saved as a CSV file via the menu item `File⇒Export CSV…`.

## Configuration

(more to come later)

## Contributing

The source code will be available in a public repository at the Gitlab instance of the University of Grenoble Alpes.

## Authors

Copyright (C) 2024  Esteban Milleret (<esteban.milleret@etu.univ-grenoble-alpes.fr>)

Copyright (C) 2024  Rafael Laboissière (<rafael.laboissiere@cnrs.fr>)


## License

This project is licensed under the terms of the GPL 3.0 or later.
