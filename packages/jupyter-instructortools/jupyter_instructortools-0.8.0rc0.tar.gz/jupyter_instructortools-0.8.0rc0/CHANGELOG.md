# Changelog

## 0.8.0 (July 15, 2024)
* **DEPRECATION**: Switched hide code to default Jupyter Lab collapse code 
  behavior.
* Added commands and menu items to undo the highlighted indication of 
  protected cells and those flagged for code-collapse or hiding on print.
* Added commands to allow temporary complete hiding (not collapse) of code 
  but not the output.
* Console debug messages off by default.
## 0.7.0 (June 5, 2024)
* Converted to a Jupyter Lab 4+ and notebook 7+ compatible plugin.
* Updated dependencies to be Jupyter Lab 4+ and notebook 7+ compatible.
* Switched to Jupyter compatible BSD license.
* **DEPRECATION:** Support for classic Jupyter (nbclassic) is dropped. 
  Versions 0.6.1 should still work with classic Jupyter.
* Added capability to enable and disable the Instructor Tools menu as well 
  as show and hide it using the Jupyter Lab command palette. This allows the 
  plugin to exist in a Jupyter Hub 
  installation used by both the instructor and students. By default, the menu 
  is deactivated and will not activate if a student has a notebook set to 
  disallow use of instructor tools.
* Added boilerplate instructions for creating a pdf of notebook with 
  collapsed headings.

 ## 0.6.1
* Updates to requirements to utilize upstream bug fixes.
 ## 0.6.0
* Converted to hierarchical menu that appears in the menu bar rather 
  than the toolbar.
## 0.5.6.2
* Simplified styling of highlight bars to reduce chances of markdown 
  cell sanitization making them not show up.
* Converted highlights to look more like brackets.
* Added option for a red left bracket highlight.
* require notebook version >= 6.4.10 for security fix.
## 0.5.6.1 
* require notebook version >=6.4.7 for html styling and security 
    fixes.
## 0.5.6
* Expanded highlight bar options to insert in markdown cells to: 
  horizontal green start; horizontal brown stop; left vertical 
  chrome-blue highlight (only works well in Chrome browser).
* Pin the notebook version to 6.4.0 because 6.4.1+ has started 
  stripping all html styling from markdown cells.
## 0.5.5
* Added option to flag cells as hide_code_on_print.
* Added option to flag cells as hide_code (auto-hidden in
JPSL).
* Added ability to highlight these cells.
## 0.5.4 
* Minor bug fixes and interface tweaks.
## 0.5.3 
* Added options to flag cells as allowed to be hidden.
* Added ability to test hide/show of cells.
* Added ability to place light blue highlight bar at left of markdown 
  cells.
* README updates.
## 0.5.2
* Better messages and Readme updates.
## 0.5.1
* Added permanently deactivate menu option.
* Added get names and timestamp option.
* Added insert boilerplate about initializing notebook option.
* Began using
  [JPSLUtils](https://github.com/JupyterPhysSciLab/JPSLUtils)
  for tools used across JupyterPhysSciLab.
* Updated README, included suggested workflow, license and more details.
## 0.5.0 Initial release.