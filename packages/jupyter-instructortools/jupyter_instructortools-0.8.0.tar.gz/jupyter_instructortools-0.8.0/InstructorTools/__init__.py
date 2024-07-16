# Tools for using a Jupyter notebook as a lab notebook.
# These tools are specifically to aid instructors in setting
# up notebook templates with embedded instructions and tools
# for students.
# J. Gutow <gutow@uwosh.edu>
# license GPL V3 or greater.

from IPython.display import display, HTML
from IPython.display import Javascript as JS

import os
from input_table import * #import the input table builder
import JPSLUtils # import the Utilities
import JPSLMenus # import tools for hierarchical menus

try:
    from ._version import __version__
except ImportError:
    # Fallback when using the package in dev mode without installing
    # in editable mode with pip. It is highly recommended to install
    # the package from a stable release or in editable mode: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
    import warnings
    warnings.warn("Importing 'jupyter-instructortool' outside a proper "
                  "installation.")
    __version__ = "dev"


def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "intructortools"
    }]

# Locate jupyter_instructortools package directory
mydir = os.path.dirname(__file__)  # absolute path to directory containing this file.

def instmenu_act():
    """
    Adds the instructor menu to the Jupyter menu bar
    :return:
    """
    tempJSfile = open(os.path.join(mydir, 'javascript', 'InstructorToolsmnu.js'))
    tempscript = '<script type="text/javascript">'
    tempscript += tempJSfile.read() + '</script>'
    tempJSfile.close()
    display(HTML(tempscript))
    display(JS('JPSLUtils.createJPSLToolsMenu('
               ');InstructorTools.createInstructorToolsMenu();'))
    warnstr = "This cell should only contain `import InstructorTools`"
    warnstr += " as it will be deleted when the tools"
    warnstr+= " are deactivated.\n\nWARNING: if you select the '!deactivate "
    warnstr+= " permanently!' option to make a student worksheet, the menu "
    warnstr+= "cannot be reactivated. Only use that option on a copy you "
    warnstr+= "intend to pass out to students."
    print(warnstr)
    pass

def instmenu_deact():
    """
    Removes the instructor menu from the Jupyter menu bar
    :return:
    """
    display(JS('deleteInstructorToolsMenu()'))
    print("Delete this cell after the menu has been removed.")
    pass

instmenu_act()