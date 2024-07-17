CHANGELOG
=========

0.7.1 - 2024-07-17
------------------

This is a maintenance release. The distributed config.yml file has been changed. The event "ag" (attention getter) has been added and the colors of the events in the "gaze" timeline have been changed.

0.7.0 - 2024-07-16
------------------

New features:

- The format of the project file is upgraded to 2. This introduces a backward-incompatibility which may affect users. Indeed, previous versions of ViCodePy will refuse to load a project file with version 1 and the user will be invited to upgrade the application.

- The identity of the person doing the code (name and email address), as well as the date and time of last modification are now stored into the configuration file (in the `coders` field). The identity information is asked when the project file is saved for the first time and is persistent for the duration of the session.

- A new context menu is now added when right-clicking on a timeline. It allows to:
  * Add a new timeline.
  * Delete the timeline. This is not yet fully operational, since the timeline is not actually removed. For now, the timeline is only emptied from its annotations.
  * Edit the timeline label.
  * Edit the events defined for the timeline. it is possible to change the label and the background color of each event already defined for the current timeline.

Bug fix:

The base name of the CSV file saved in the project file is now exactly the same as the base name of the video file. In the previous version, it was wrongly set to the name of the ZIP file.

0.6.4 - 2024-07-13
------------------

This is a maintenance release, which fixes the reading of the CSV file.

0.6.3 - 2024-07-12
------------------

This is a maintenance release, with some code improvements. The only user visible change is the fixing of a bug causing the label of the annotation not changed when the event was changed.

0.6.2 - 2024-07-11
------------------

This is a bug-fixing, maintenance release. User visible changes:

- The format version of the project file is set to 1. In the previous release, it was wrongly set to 2.
- The Help/About window shows now the format version of the project file.

0.6.1 - 2024-07-11
------------------

This is a bug-fixing, maintenance release. User visible changes:

- When moving the borders of the selected annotation, they cannot go past the borders of adjacent annotations.
- Better logic for finding the current version of ViCodePy.

0.6.0 - 2024-07-08
------------------

New features:

- All the work done during a session can now be saved in a “project file”. This file is in ZIP format and contains the video file, the configuration file (which defines the timelines and the style of the events), and the CSV file (which contains the annotations). This file can also be loaded into ViCodePy, in order to resume of visualize previous sessions. The format of the project file is described in the `FORMAT.md` file. Provisions will be made for assuring backward and forward compatibility regarding the format of the project file.

- It is now possible to do further manipulations on a annotation, once it is created, by right-clicking on it:
  - Change the label (and the associated color) of the annotation.
  - Add comments to the annotation.
  - Merge with an adjacent annotation, if there is no gap between both of them and if they both indicate the same event.

- The configuration system is improved:
  - The loading of the configuration file `config.yml` is now incremental. Files named `config.yml` are read from the package, the system, the user, and the local directories, in this order. Latter settings override the former.
  - It is now possible to specify the separator for the CSV files (typically `,` or `;`), in the `config.yml` file.

- In the CSV file, time is now coded in milliseconds, instead of seconds. This avoids errors related to floating point precision.

- There is now an “About” entry in the “Help” for showing the version of ViCodePy.

- It is possible to horizontally scroll the timelines with Shift + mouse wheel.

- The annotation under the cursor is now highlighted. This is useful for creating contiguous annotations.

- Clicking on a timeline selects it. Double-clicking selects the timeline and move the cursor to the mouse pointer position.

Bugs fixed:

- Fixed several visualization problems, related to the zooming of the timeline and the location of annotation borders and the cursor, which are now precisely placed at the instant of time corresponding the each image in the video.

- The responses to the key presses are improved. In particular, if the Right key is kept pressed, the movie is played continuously.

- Several minor bugs in the interface have been fixed.

0.5.2 - 2024-06-21
------------------

Maintenance release: Integrate the changes for indicating the active timeline via the title bar (forgotten in last version).

0.5.1 - 2024-06-21
------------------

Enhancements:

- The handle for the video player / timeline editor splitter changes now its color when hovered by the mouse
- The title bars of the timelines change color to indicate which one is selected

User-invisible change:

- Code files reorganization

0.5.0 - 2024-06-20
------------------

New features:

- It is now possible to add annotations in multiple timelines
- When clicking on the timeline, the cursor is moved to the mouse position
- It is possible to go forward and backward in time in steps of 5 and 10 frames, either with keystrokes or with buttons in the video player
- Durations of the annotations are now saved in the CSV file
- New system for loading the configuration files (local-, user- and system-wide)
- The program does not exit before proposing to save the created annotations

User-visible fixed bugs:

- During the creation of a new annotation, the other existing annotation can not be made active
- The choice of color for a new label is persistent
- The menu entry for the creation of an annotation is more informative
- The existence of the video file is checked before loading it

0.4.5 - 2024-06-11
------------------

This is a maintenance release. The user visible changes are:

* Require version 6.6.2 of PySide6
* The zooming of the timeline is now centered on the mouse position
* The CSV file is now exported to the same directory where the video file is located
* The annotations appear in chronological order in the exported CSV file
* Improvements in the display of the tick labels in the timescale
* Fix bug when selecting annotations created by pressing the Left key
* At startup, if no video is loaded, a message is shown inviting the user to load a file

0.4.4 - 2024-06-02
------------------

* Annotations do not overlap anymore

0.4.3 - 2024-06-02
------------------

* Use better names for columns in the exported CSV file
* Improved documentation

0.4.2 - 2024-06-01
------------------

* The program accepts now command line arguments
* Annotation labels can be chosen directly using the keyboard, once the annotation dialog is displayed

0.4.1 - 2024-05-31
------------------

* All supported video file formats can now be loaded
* Annotation handles can now be clicked/dragged with the mouse
* Improved color contrast of annotation labels

0.4.0 - 2024-05-30
------------------

* First release to PyPI
* The code has been ported from PQt6 to PySide6
* Bugs fixed / Added features
  - The timeline can be zoomed/dezoomed
  - Annotation creation can be aborted
  - Annotation data can be saved in a CSV file
  - The configuration is now in YAML format and can store several annotation label definitions

0.3.7 - 2024-05-28
------------------

Depend on PySide6

0.3.6 - 2024-05-28
------------------

Add dependency on PyQt6-Qt6

0.3.5 - 2024-05-28
------------------

Force dependency on PyQt6 == 6.4

0.3.4 - 2024-05-23
------------------

Use GitLab CI and AutoPub for automatic publication of the package

0.3.3 - 2024-05-23
------------------

* First release to test.pypi.org
* The timeline is now implemented with QGraphics* objects
* Annotations are now clickable

0.2 - 2024-04-30
----------------

* Fix video playing issues
* The timeline is now functional and it is possible to add annotations

0.1 - 2024-03-25
----------------

Initial release, containing a very simple interface that allows loading a video file and playing it. A timeline is show but is not yet functional.
