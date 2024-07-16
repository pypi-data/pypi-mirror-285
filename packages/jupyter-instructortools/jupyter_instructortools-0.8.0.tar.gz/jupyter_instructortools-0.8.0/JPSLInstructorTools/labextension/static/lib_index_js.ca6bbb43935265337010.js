"use strict";
(self["webpackChunkJPSLInstructorTools"] = self["webpackChunkJPSLInstructorTools"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__);





const plugin = {
    id: 'JPSLInstructorTools:plugin',
    description: 'Tool to assist instructors in creating notebook templates for student Jupyter worksheets.',
    autoStart: true,
    requires: [_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_0__.IMainMenu, _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ICommandPalette, _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__.INotebookTracker, _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__.INotebookTools],
    activate: async (app, 
    //shell: ILabShell,
    MainMenu, palette, notebookTracker, notebookTools) => {
        const { commands } = app;
        // Is the menu activated flag?
        let menuactive = false;
        // Is this tool allowed in current notebook flag. Updated each time a notebook is focused.
        // When true the menu will be hidden and the show menu command in the pallet will create an alert to notify
        // the user.
        let thistoolforbidden = false;
        /**
        * Build the commands to add to the menu
         */
        // New Data Table is defined in jupyter-datainputtable package.
        const NewDataTable = {
            id: 'NewDataTable:jupyter-inputtable',
            label: 'Insert Data Entry Table...',
            caption: 'Insert a new Data Entry Table'
        };
        /*
            commands.addCommand(NewDataTable.id, {
              label: NewDataTable.label,
              caption: NewDataTable.caption,
              execute: (args: any) => {
                console.log(
                  `New Data Table has been called ${args['origin']}.`
                );
                window.alert(
                  `New Data Table has been called ${args['origin']}.`
                );
              },
            });
        */
        // Insert Green Start Bar
        const grnstart = {
            id: 'grnstart:JPSLInstructorTools:main-menu',
            label: 'Insert green start bar',
            caption: 'Insert green start bar in a markdown cell.'
        };
        commands.addCommand(grnstart.id, {
            label: grnstart.label,
            caption: grnstart.caption,
            execute: () => {
                const htmlstr = "<div style = \"width: 100%; height:10px;" +
                    "border-width:5px; border-color:green;" +
                    "border-style:solid;border-bottom-style:none;" +
                    "margin-bottom: 4px; min-width: 15px;" +
                    "background-color:beige;\"></div>\n\n";
                if (notebookTools.selectedCells) {
                    // We will only act on the first selected cell
                    const cellEditor = notebookTools.selectedCells[0].editor;
                    if (cellEditor) {
                        const tempPos = { column: 0, line: 0 };
                        //cellEditor.setCursorPosition(tempPos);
                        cellEditor.setSelection({ start: tempPos, end: tempPos });
                        if (cellEditor.replaceSelection) {
                            cellEditor.replaceSelection(htmlstr);
                        }
                    }
                }
                else {
                    window.alert('Please select a cell in a notebook.');
                }
                console.log('Insert green start bar has been called.');
            },
        });
        // Insert Brown Stop Bar
        const brnstop = {
            id: 'brnstop:JPSLInstructorTools:main-menu',
            label: 'Insert brown stop bar',
            caption: 'Insert brown stop bar in a markdown cell.'
        };
        commands.addCommand(brnstop.id, {
            label: brnstop.label,
            caption: brnstop.caption,
            execute: () => {
                const htmlstr = "\n\n<div style = \"width: 100%; height:10px;" +
                    "border-width:5px;border-color:sienna;" +
                    "border-style:solid;border-top-style:none;" +
                    "margin-top: 4px; min-width: 15px;" +
                    "background-color:beige;\"></div>";
                if (notebookTools.selectedCells) {
                    // We will only act on the first selected cell
                    const cellEditor = notebookTools.selectedCells[0].editor;
                    if (cellEditor) {
                        const endline = cellEditor.lineCount - 1;
                        let tempPos = { column: 0, line: endline };
                        const endlinecont = cellEditor.getLine(endline);
                        if (endlinecont) {
                            tempPos.column = endlinecont.length;
                        }
                        cellEditor.setSelection({ start: tempPos, end: tempPos });
                        if (cellEditor.replaceSelection) {
                            cellEditor.replaceSelection(htmlstr);
                        }
                    }
                }
                else {
                    window.alert('Please select a cell in a notebook.');
                }
                console.log('Insert brown stop bar has been called.');
            },
        });
        // Insert left cyan highlight
        const cyanhighlight = {
            id: 'cyanhighlight:JPSLInstructorTools:main-menu',
            label: 'Insert left cyan highlight',
            caption: 'Insert left cyan highlight in a markdown cell.'
        };
        commands.addCommand(cyanhighlight.id, {
            label: cyanhighlight.label,
            caption: cyanhighlight.caption,
            execute: () => {
                const htmlstr = "<div style = \"height: 100%; width:10px;" +
                    "float:left; border-width:5px; border-color:cyan;" +
                    "border-style:solid; border-right-style:none;" +
                    "margin-right: 4px; min-height: 15px;\"></div>\n\n";
                if (notebookTools.selectedCells) {
                    // We will only act on the first selected cell
                    const cellEditor = notebookTools.selectedCells[0].editor;
                    if (cellEditor) {
                        const tempPos = { column: 0, line: 0 };
                        //cellEditor.setCursorPosition(tempPos);
                        cellEditor.setSelection({ start: tempPos, end: tempPos });
                        if (cellEditor.replaceSelection) {
                            cellEditor.replaceSelection(htmlstr);
                        }
                    }
                }
                else {
                    window.alert('Please select a cell in a notebook.');
                }
                console.log('Insert left cyan highlight has been called.');
            },
        });
        // Insert left red highlight
        const redhighlight = {
            id: 'redhighlight:JPSLInstructorTools:main-menu',
            label: 'Insert left red highlight',
            caption: 'Insert left red highlight in a markdown cell.'
        };
        commands.addCommand(redhighlight.id, {
            label: redhighlight.label,
            caption: redhighlight.caption,
            execute: () => {
                const htmlstr = "<div style = \"height: 100%; width:10px;" +
                    "float:left; border-width:5px; border-color:red;" +
                    "border-style:solid; border-right-style:none;" +
                    "margin-right: 4px; min-height: 15px;\"></div>\n\n";
                if (notebookTools.selectedCells) {
                    // We will only act on the first selected cell
                    const cellEditor = notebookTools.selectedCells[0].editor;
                    if (cellEditor) {
                        const tempPos = { column: 0, line: 0 };
                        //cellEditor.setCursorPosition(tempPos);
                        cellEditor.setSelection({ start: tempPos, end: tempPos });
                        if (cellEditor.replaceSelection) {
                            cellEditor.replaceSelection(htmlstr);
                        }
                    }
                }
                else {
                    window.alert('Please select a cell in a notebook.');
                }
                console.log('Insert left red highlight has been called.');
            },
        });
        // Protect Selected Cells
        const protectcells = {
            id: 'protectcells:JPSLInstructorTools:main-menu',
            label: 'Protect selected cells',
            caption: 'Protect selected cells'
        };
        commands.addCommand(protectcells.id, {
            label: protectcells.label,
            caption: protectcells.caption,
            execute: () => {
                if (notebookTracker.currentWidget) {
                    if (notebookTools.selectedCells) {
                        for (const cell of notebookTools.selectedCells) {
                            cell.model.setMetadata("editable", false);
                            cell.model.setMetadata("deletable", false);
                            cell.node.setAttribute("style", "background-color:pink;");
                        }
                    }
                    else {
                        window.alert("Cell protection failed. Did you select cells?");
                    }
                }
                else {
                    let alertstr = "Cell protection failed. Try the Property Inspector advanced mode and set the";
                    alertstr += "'editable'parameter to false. Then add the 'deletable' parameter set to false.";
                    window.alert(alertstr);
                }
                console.log(`Protect selected cells has been called.`);
            },
        });
        // Deprotect Selected Cells
        const deprotectcells = {
            id: 'deprotectcells:JPSLInstructorTools:main-menu',
            label: 'Deprotect selected cells',
            caption: 'Deprotect selected cells'
        };
        commands.addCommand(deprotectcells.id, {
            label: deprotectcells.label,
            caption: deprotectcells.caption,
            execute: () => {
                if (notebookTracker.currentWidget) {
                    if (notebookTools.selectedCells) {
                        for (const cell of notebookTools.selectedCells) {
                            cell.model.setMetadata("editable", true);
                            cell.model.setMetadata("deletable", true);
                            cell.node.removeAttribute("style");
                        }
                    }
                    else {
                        window.alert("Cell deprotection failed. Did you select cells?");
                    }
                }
                else {
                    let alertstr = "Cell deprotection failed. Try the Property Inspector advanced mode and set the";
                    alertstr += "'editable' parameter to true. Then set the 'deletable' parameter to true.";
                    window.alert(alertstr);
                }
                console.log(`Deprotect selected cells has been called.`);
            },
        });
        // Indicate Protected Cells
        const indicateprotectcells = {
            id: 'indicateprotectcells:JPSLInstructorTools:main-menu',
            label: 'Indicate protected cells',
            caption: 'Indicate protected cells'
        };
        commands.addCommand(indicateprotectcells.id, {
            label: indicateprotectcells.label,
            caption: indicateprotectcells.caption,
            execute: () => {
                if (notebookTracker.currentWidget) {
                    if (notebookTracker.currentWidget.content.widgets) {
                        let found = 0;
                        for (const cell of notebookTracker.currentWidget.content.widgets) {
                            if (!cell.model.getMetadata('editable') && !cell.model.getMetadata('deletable')
                                && cell.model.getMetadata('editable') != null) {
                                cell.node.setAttribute("style", "background-color:pink;");
                                found += 1;
                            }
                        }
                        if (found == 0) {
                            window.alert("No protected cells found.");
                        }
                    }
                    else {
                        window.alert("No notebook cells found.");
                    }
                }
                else {
                    window.alert("You do not appear to have a notebook in front or selected. Try again.");
                }
                console.log(`Indicate protected cells has been called.`);
            },
        });
        // Mark Cells To Hide Before Printing
        const sethidecellbeforeprint = {
            id: 'sethidecellbeforeprint:JPSLInstructorTools:main-menu',
            label: 'Allow hiding of selected cells',
            caption: 'Sets the hide before printing flag of the selected cells.'
        };
        commands.addCommand(sethidecellbeforeprint.id, {
            label: sethidecellbeforeprint.label,
            caption: sethidecellbeforeprint.caption,
            execute: () => {
                if (notebookTracker.currentWidget) {
                    if (notebookTools.selectedCells) {
                        for (const cell of notebookTools.selectedCells) {
                            let metadata = cell.model.getMetadata('JPSL');
                            if (!metadata) {
                                cell.model.setMetadata('JPSL', { "hide_on_print": true });
                            }
                            else {
                                metadata.hide_on_print = true;
                                cell.model.setMetadata('JPSL', metadata);
                            }
                            cell.node.setAttribute("style", "background-color:beige;");
                        }
                    }
                    else {
                        window.alert("Set of hide before printing flag failed. Did you select cells?");
                    }
                }
                else {
                    let alertstr = 'Set of hide before printing flag failed. Try the Property Inspector advanced mode and';
                    alertstr += 'enter "JPSL":{"hide_on_print": true}.';
                    window.alert(alertstr);
                }
                console.log('Set of hide before printing flag has been called.');
            },
        });
        // Unset Cells To Hide Before Printing
        const unsethidecellbeforeprint = {
            id: 'unsethidecellbeforeprint:JPSLInstructorTools:main-menu',
            label: 'Disallow hiding of selected cells',
            caption: 'Unsets the hide before printing flag of the selected cells.'
        };
        commands.addCommand(unsethidecellbeforeprint.id, {
            label: unsethidecellbeforeprint.label,
            caption: unsethidecellbeforeprint.caption,
            execute: () => {
                if (notebookTracker.currentWidget) {
                    if (notebookTools.selectedCells) {
                        for (const cell of notebookTools.selectedCells) {
                            let metadata = cell.model.getMetadata('JPSL');
                            if (!metadata) {
                                cell.model.setMetadata('JPSL', { "hide_on_print": false });
                            }
                            else {
                                metadata.hide_on_print = false;
                                cell.model.setMetadata('JPSL', metadata);
                            }
                            cell.node.removeAttribute("style");
                        }
                    }
                    else {
                        window.alert("Unset of hide before printing flag failed. Did you select cells?");
                    }
                }
                else {
                    let alertstr = 'Unset of hide before printing flag failed. Try the Property Inspector advanced mode and';
                    alertstr += 'enter "JPSL":{"hide_on_print": false}.';
                    window.alert(alertstr);
                }
                console.log('Unset of hide before printing flag has been called.');
            },
        });
        // Indicate hide before print cells
        const indicatehidecellbeforeprint = {
            id: 'indicatehidecellbeforeprint:JPSLInstructorTools:main-menu',
            label: 'Indicate hide before print cells',
            caption: 'Indicates hide before print cells.'
        };
        commands.addCommand(indicatehidecellbeforeprint.id, {
            label: indicatehidecellbeforeprint.label,
            caption: indicatehidecellbeforeprint.caption,
            execute: () => {
                if (notebookTracker.currentWidget) {
                    if (notebookTracker.currentWidget.content.widgets) {
                        let found = 0;
                        for (const cell of notebookTracker.currentWidget.content.widgets) {
                            let metadata = cell.model.getMetadata('JPSL');
                            if (metadata) {
                                if (metadata.hide_on_print) {
                                    cell.node.setAttribute("style", "background-color:beige;");
                                    found += 1;
                                }
                            }
                        }
                        if (found == 0) {
                            window.alert("No hide before print cells found.");
                        }
                    }
                    else {
                        window.alert("No notebook cells found.");
                    }
                }
                else {
                    window.alert("You do not appear to have a notebook in front or selected. Try again.");
                }
                console.log(`Indicate hide before print cells has been called.`);
            },
        });
        // Mark cells to hide code before printing
        const sethidecodebeforeprint = {
            id: 'sethidecodebeforeprint:JPSLInstructorTools:main-menu',
            label: 'Allow hiding of code',
            caption: 'Set hide code before print flag for selected cells.'
        };
        commands.addCommand(sethidecodebeforeprint.id, {
            label: sethidecodebeforeprint.label,
            caption: sethidecodebeforeprint.caption,
            execute: () => {
                if (notebookTracker.currentWidget) {
                    if (notebookTools.selectedCells) {
                        for (const cell of notebookTools.selectedCells) {
                            let metadata = cell.model.getMetadata('JPSL');
                            if (!metadata) {
                                cell.model.setMetadata('JPSL', { "hide_code_on_print": true });
                            }
                            else {
                                metadata.hide_code_on_print = true;
                                cell.model.setMetadata('JPSL', metadata);
                            }
                            cell.node.setAttribute("style", "background-color:orange;");
                        }
                    }
                    else {
                        window.alert("Set of hide code before printing flag failed. Did you select cells?");
                    }
                }
                else {
                    let alertstr = 'Set of hide code before printing flag failed. Try the Property Inspector advanced';
                    alertstr += ' mode and enter "JPSL":{"hide_code_on_print": true}.';
                    window.alert(alertstr);
                }
                console.log('Set of hide code before printing flag has been called.');
            },
        });
        // Unset cells to hide code before printing
        const unsethidecodebeforeprint = {
            id: 'unsethidecodebeforeprint:JPSLInstructorTools:main-menu',
            label: 'Disallow hiding of code',
            caption: 'Unset hide code before print flag for selected cells.'
        };
        commands.addCommand(unsethidecodebeforeprint.id, {
            label: unsethidecodebeforeprint.label,
            caption: unsethidecodebeforeprint.caption,
            execute: () => {
                if (notebookTracker.currentWidget) {
                    if (notebookTools.selectedCells) {
                        for (const cell of notebookTools.selectedCells) {
                            let metadata = cell.model.getMetadata('JPSL');
                            if (!metadata) {
                                cell.model.setMetadata('JPSL', { "hide_code_on_print": false });
                            }
                            else {
                                metadata.hide_code_on_print = false;
                                cell.model.setMetadata('JPSL', metadata);
                            }
                            cell.node.removeAttribute("style");
                        }
                    }
                    else {
                        window.alert("Unset of hide code before printing flag failed. Did you select cells?");
                    }
                }
                else {
                    let alertstr = 'Unset of hide code before printing flag failed. Try the Property Inspector advanced';
                    alertstr += ' mode andenter "JPSL":{"hide_code_on_print": false}.';
                    window.alert(alertstr);
                }
                console.log('Unset of hide code before printing flag has been called.');
            },
        });
        // Indicate hide code before printing cells
        const indicatehidecodebeforeprint = {
            id: 'indicatehidecodebeforeprint:JPSLInstructorTools:main-menu',
            label: 'Indicate hide code before print cells',
            caption: 'Indicate hide code before print cells.'
        };
        commands.addCommand(indicatehidecodebeforeprint.id, {
            label: indicatehidecodebeforeprint.label,
            caption: indicatehidecodebeforeprint.caption,
            execute: () => {
                if (notebookTracker.currentWidget) {
                    if (notebookTracker.currentWidget.content.widgets) {
                        let found = 0;
                        for (const cell of notebookTracker.currentWidget.content.widgets) {
                            let metadata = cell.model.getMetadata('JPSL');
                            if (metadata) {
                                if (metadata.hide_code_on_print) {
                                    cell.node.setAttribute("style", "background-color:orange;");
                                    found += 1;
                                }
                            }
                        }
                        if (found == 0) {
                            window.alert("No hide code before print cells found.");
                        }
                    }
                    else {
                        window.alert("No notebook cells found.");
                    }
                }
                else {
                    window.alert("You do not appear to have a notebook in front or selected. Try again.");
                }
                console.log(`Indicate hide code before print cells has been called.`);
            },
        });
        // Test hide before print
        const tsthidebeforeprint = {
            id: 'tsthidebeforeprint:JPSLInstructorTools:main-menu',
            label: 'Test hide before print',
            caption: 'Test hide before print.'
        };
        commands.addCommand(tsthidebeforeprint.id, {
            label: tsthidebeforeprint.label,
            caption: tsthidebeforeprint.caption,
            execute: () => {
                if (notebookTracker.currentWidget) {
                    if (notebookTracker.currentWidget.content.widgets) {
                        let found = 0;
                        for (const cell of notebookTracker.currentWidget.content.widgets) {
                            let metadata = cell.model.getMetadata('JPSL');
                            if (metadata) {
                                if (metadata.hide_on_print) {
                                    cell.node.setAttribute("style", "display:none;");
                                    cell.hide();
                                    found += 1;
                                }
                                if (metadata.hide_code_on_print) {
                                    cell.inputHidden = true;
                                    found += 1;
                                }
                            }
                        }
                        if (found == 0) {
                            window.alert("No hide before print cells found.");
                        }
                    }
                    else {
                        window.alert("No notebook cells found.");
                    }
                }
                else {
                    window.alert("You do not appear to have a notebook in front or selected. Try again.");
                }
                console.log(`Test hide before print cells has been called.`);
            },
        });
        // Undo hide before print
        const undohidebeforeprint = {
            id: 'undohidebeforeprint:JPSLInstructorTools:main-menu',
            label: 'Undo hide before print',
            caption: 'Undo hide before print.'
        };
        commands.addCommand(undohidebeforeprint.id, {
            label: undohidebeforeprint.label,
            caption: undohidebeforeprint.caption,
            execute: () => {
                if (notebookTracker.currentWidget) {
                    if (notebookTracker.currentWidget.content.widgets) {
                        let found = 0;
                        for (const cell of notebookTracker.currentWidget.content.widgets) {
                            let metadata = cell.model.getMetadata('JPSL');
                            if (metadata) {
                                if (metadata.hide_on_print) {
                                    cell.node.removeAttribute("style");
                                    cell.show();
                                    found += 1;
                                }
                                if (metadata.hide_code_on_print) {
                                    cell.inputHidden = false;
                                    found += 1;
                                }
                            }
                        }
                        if (found == 0) {
                            window.alert("No hide before print cells found.");
                        }
                    }
                    else {
                        window.alert("No notebook cells found.");
                    }
                }
                else {
                    window.alert("You do not appear to have a notebook in front or selected. Try again.");
                }
                console.log(`Undo test hide before print cells has been called.`);
            },
        });
        // Set hide code in JPSL
        const sethidecodeJPSL = {
            id: 'sethidecodeJPSL:JPSLInstructorTools:main-menu',
            label: 'Set hide code in JPSL',
            caption: 'Set hide code in JPSL flag for selected cells.'
        };
        commands.addCommand(sethidecodeJPSL.id, {
            label: sethidecodeJPSL.label,
            caption: sethidecodeJPSL.caption,
            execute: () => {
                if (notebookTracker.currentWidget) {
                    if (notebookTools.selectedCells) {
                        for (const cell of notebookTools.selectedCells) {
                            let metadata = cell.model.getMetadata('JPSL');
                            if (!metadata) {
                                cell.model.setMetadata('JPSL', { "hide_code": true });
                            }
                            else {
                                metadata.hide_code = true;
                                cell.model.setMetadata('JPSL', metadata);
                            }
                            cell.node.setAttribute("style", "background-color:beige;");
                        }
                    }
                    else {
                        window.alert("Set of hide code in JPSL flag failed. Did you select cells?");
                    }
                }
                else {
                    let alertstr = 'Set of hide code in JPSL flag failed. Try the Property Inspector advanced';
                    alertstr += ' mode and enter "JPSL":{"hide_code": true}.';
                    window.alert(alertstr);
                }
                console.log('Set of hide code in JPSL flag has been called.');
            },
        });
        // Unset hide code in JPSL
        const unsethidecodeJPSL = {
            id: 'unsethidecodeJPSL:JPSLInstructorTools:main-menu',
            label: 'Unset hide code in JPSL',
            caption: 'Unset hide code in JPSL flag for selected cells.'
        };
        commands.addCommand(unsethidecodeJPSL.id, {
            label: unsethidecodeJPSL.label,
            caption: unsethidecodeJPSL.caption,
            execute: () => {
                if (notebookTracker.currentWidget) {
                    if (notebookTools.selectedCells) {
                        for (const cell of notebookTools.selectedCells) {
                            let metadata = cell.model.getMetadata('JPSL');
                            if (!metadata) {
                                cell.model.setMetadata('JPSL', { "hide_code": false });
                            }
                            else {
                                metadata.hide_code = false;
                                cell.model.setMetadata('JPSL', metadata);
                            }
                            cell.node.removeAttribute("style");
                        }
                    }
                    else {
                        window.alert("Unset of hide code in JPSL flag failed. Did you select cells?");
                    }
                }
                else {
                    let alertstr = 'Unset of hide code in JPSL flag failed. Try the Property Inspector advanced';
                    alertstr += ' mode and enter "JPSL":{"hide_code": false}.';
                    window.alert(alertstr);
                }
                console.log('Unset of hide code in JPSL flag has been called.');
            },
        });
        // Indicate hide code in JPSL
        const indicatehidecodeJPSL = {
            id: 'indicatehidecodeJPSL:JPSLInstructorTools:main-menu',
            label: 'Indicate hide code in JPSL cells',
            caption: 'Indicate hide code in JPSL cells.'
        };
        commands.addCommand(indicatehidecodeJPSL.id, {
            label: indicatehidecodeJPSL.label,
            caption: indicatehidecodeJPSL.caption,
            execute: () => {
                if (notebookTracker.currentWidget) {
                    if (notebookTracker.currentWidget.content.widgets) {
                        let found = 0;
                        for (const cell of notebookTracker.currentWidget.content.widgets) {
                            let metadata = cell.model.getMetadata('JPSL');
                            if (metadata) {
                                if (metadata.hide_code) {
                                    cell.node.setAttribute("style", "background-color:beige;");
                                    found += 1;
                                }
                            }
                        }
                        if (found == 0) {
                            window.alert("No hide code in JPSL cells found.");
                        }
                    }
                    else {
                        window.alert("No notebook cells found.");
                    }
                }
                else {
                    window.alert("You do not appear to have a notebook in front or selected. Try again.");
                }
                console.log(`Indicate hide code in JPSL cells has been called.`);
            },
        });
        // Insert Instructions BoilerPlate
        const insertInstructionBoilerPlate = {
            id: 'insertInstructionBoilerPlate:JPSLInstructorTools:main-menu',
            label: 'Insert instructions Boilerplate',
            caption: 'Insert Instruction Boilerplate into selected cell.'
        };
        commands.addCommand(insertInstructionBoilerPlate.id, {
            label: insertInstructionBoilerPlate.label,
            caption: insertInstructionBoilerPlate.caption,
            execute: () => {
                const mkdstr = "### You must initialize the software each time you use this notebook.\n" +
                    " 1. First, check that the notebook is \"Trusted\" by looking near" +
                    " the right of the Jupyter toolbars. If the notebook is not trusted" +
                    " you need to click on the \"not trusted\" button and trust the" +
                    " notebook. **You should only trust notebooks that come from a" +
                    " *trusted source*, such as the class website.**\n" +
                    " 2. The cell immediately below contains code that loads the" +
                    " software modules necessary for this notebook to run. **You" +
                    " must run this cell each time you open the notebook or later cells" +
                    " may not work.**\n 3. If you are doing calculations that depend upon" +
                    " using variables passed from calculations done the previous" +
                    " time the notebook was opened, you will need to run those" +
                    " previous cells to redefine the variables. You can run each cell" +
                    " individually in order, or use the 'Restart the kernel and run all" +
                    " cells' button (usually represented by double fast-forward arrows).\n";
                if (notebookTools.selectedCells) {
                    // We will only act on the first selected cell
                    const cellEditor = notebookTools.selectedCells[0].editor;
                    if (cellEditor) {
                        const tempPos = { column: 0, line: 0 };
                        //cellEditor.setCursorPosition(tempPos);
                        cellEditor.setSelection({ start: tempPos, end: tempPos });
                        if (cellEditor.replaceSelection) {
                            cellEditor.replaceSelection(mkdstr);
                        }
                    }
                }
                else {
                    window.alert('Please select a cell in a notebook.');
                }
                console.log('Insert Instructions Boilerplate has been called.');
            },
        });
        // Insert make PDF Instructions
        const insertmakePDFInstructions = {
            id: 'insertmakePDFInstructions:JPSLInstructorTools:main-menu',
            label: 'Insert make PDF instructions',
            caption: 'Insert make PDF instructions into selected cell.'
        };
        commands.addCommand(insertmakePDFInstructions.id, {
            label: insertmakePDFInstructions.label,
            caption: insertmakePDFInstructions.caption,
            execute: () => {
                const mkdstr = "### Steps to create a PDF file to turn in.\n" +
                    "To convert this notebook to a lab report to turn in you need to" +
                    " hide the majority of the instruction and informational cells" +
                    " before making a .pdf document.\n" +
                    "1. Your instructor has already chosen the cells they want hidden." +
                    " To hide them select \"Hide Cells\" from the JPSL Tools menu.\n" +
                    "2. To make a pdf you must use the Browser's print capabilities. In" +
                    " most user interfaces this option is hidden in the little collapsed" +
                    " menu at the upper right of the browser window. On a macintosh it" +
                    " can be found in the file menu. Select \"Print\".\n" +
                    "\t* Set the destination to \"Save to PDF\".\n" +
                    "\t* Set the format to \"Landscape\" to accommodate the cell width.\n" +
                    "\t* Adjust the scale so that the whole width appears in the preview" +
                    "   (usually 60% - 80%).\n" +
                    "\t* Make sure to save the file in a" +
                    "   location you can find (your \"Desktop\" or maybe \"Documents\" directory).\n" +
                    "\t* Do Not use the options in the Jupyter \"File\" menu.\n" +
                    "3. It is a good idea to open the created document to make sure it is OK.\n" +
                    "4. When everything is OK, save this notebook one more time using" +
                    " \"Save Notebook\" in the Jupyter \"File\" menu and then close" +
                    " it using the \"Close and Shutdown Notebook\" option in the Jupyter \"File\"" +
                    " menu.\n" +
                    "5. Turn in: the **pdf** and **ipynb** version of this notebook plus any **datafiles**.";
                if (notebookTools.selectedCells) {
                    // We will only act on the first selected cell
                    const cellEditor = notebookTools.selectedCells[0].editor;
                    if (cellEditor) {
                        const tempPos = { column: 0, line: 0 };
                        //cellEditor.setCursorPosition(tempPos);
                        cellEditor.setSelection({ start: tempPos, end: tempPos });
                        if (cellEditor.replaceSelection) {
                            cellEditor.replaceSelection(mkdstr);
                        }
                    }
                }
                else {
                    window.alert('Please select a cell in a notebook.');
                }
                console.log('Insert make PDF instructions has been called.');
            },
        });
        // Activate Instructor Tools Menu
        const activateinstructormenu = {
            id: 'activateinstructormenu:JPSLInstructorTools:main-menu',
            label: 'Activate menu',
            caption: 'Activate the Instructor Tools menu.'
        };
        commands.addCommand(activateinstructormenu.id, {
            label: activateinstructormenu.label,
            caption: activateinstructormenu.caption,
            execute: async () => {
                menuactive = true;
                // Check the forbidden state of the front most notebook.
                await _updateforbiddenstate(null, null);
                if (thistoolforbidden) {
                    window.alert('Instructor Tools menu has been activated, but it ' +
                        'cannot be used with the front window. It will appear ' +
                        'when a notebook it can be used with is in front.');
                }
                commands.execute('Show:JPSLInstructorTools:main-menu');
                console.log('Activate menu has been called.');
            },
        });
        // Deactivate Instructor Tools Menu
        const deactivateinstructormenu = {
            id: 'deactivateinstructormenu:JPSLInstructorTools:main-menu',
            label: 'Deactivate menu',
            caption: 'Deactivate the Instructor Tools menu.'
        };
        commands.addCommand(deactivateinstructormenu.id, {
            label: deactivateinstructormenu.label,
            caption: deactivateinstructormenu.caption,
            execute: () => {
                menuactive = false;
                commands.execute('Hide:JPSLInstructorTools:main-menu');
                console.log('deactivate menu has been called.');
            },
        });
        // disable the menu and hide title.
        const hidemenu = {
            id: 'Hide:JPSLInstructorTools:main-menu',
            label: 'Hide Menu',
            caption: 'Hide Menu'
        };
        commands.addCommand(hidemenu.id, {
            label: hidemenu.label,
            caption: hidemenu.caption,
            execute: () => {
                menu.hide();
                const mainmenuDOM = document.getElementById('jp-MainMenu');
                if (mainmenuDOM) {
                    //window.alert(mainmenuDOM.toString());
                    const mainmenulabels = mainmenuDOM.querySelectorAll('.lm-MenuBar-item');
                    for (const item of mainmenulabels) {
                        const itemlabel = item.querySelector('.lm-MenuBar-itemLabel');
                        if (itemlabel) {
                            if (itemlabel.innerHTML == 'JPSL Instructor Tools') {
                                item.setAttribute('hidden', 'true');
                            }
                        }
                    }
                }
                else {
                    window.alert('Did not find the Main menu DOM element!');
                }
            },
        });
        palette.addItem({
            command: hidemenu.id,
            category: 'JPSL Instructor Tools',
            args: { origin: 'from the palette' }
        });
        // Enable the menu and show the title.
        const showmenu = {
            id: 'Show:JPSLInstructorTools:main-menu',
            label: 'Show Menu',
            caption: 'Show Menu'
        };
        commands.addCommand(showmenu.id, {
            label: showmenu.label,
            caption: showmenu.caption,
            execute: () => {
                if (!menuactive) {
                    window.alert('You need to activate the menu before it will appear.');
                    return;
                }
                if (thistoolforbidden) {
                    window.alert('You are not allowed to use JPSL Instructor Tools with this notebook.');
                    return;
                }
                else {
                    menu.show();
                    const mainmenuDOM = document.getElementById('jp-MainMenu');
                    if (mainmenuDOM) {
                        const mainmenulabels = mainmenuDOM.querySelectorAll('.lm-MenuBar-item');
                        for (const item of mainmenulabels) {
                            const itemlabel = item.querySelector('.lm-MenuBar-itemLabel');
                            if (itemlabel) {
                                if (itemlabel.innerHTML == 'JPSL Instructor Tools') {
                                    item.removeAttribute('hidden');
                                }
                            }
                        }
                    }
                }
            },
        });
        palette.addItem({
            command: showmenu.id,
            category: 'JPSL Instructor Tools',
            args: { origin: 'from the palette' }
        });
        // Disallow Instructor Tools Menu with this Notebook
        const disallowinstructormenu = {
            id: 'disallowinstructormenu:JPSLInstructorTools:main-menu',
            label: 'Disallow menu in Notebook',
            caption: 'Prevent use of the Instructor Tools menu with this Notebook.'
        };
        commands.addCommand(disallowinstructormenu.id, {
            label: disallowinstructormenu.label,
            caption: disallowinstructormenu.caption,
            execute: async () => {
                // Reminder that this a permanent change and provide chance to cancel.
                const dialogmsg = 'Are you sure? This action in irreversible. Instructor Tools ' +
                    'will no longer work with this notebook.';
                const buttons = [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.cancelButton(), _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton()];
                const result = await (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showDialog)({ body: dialogmsg,
                    buttons: buttons,
                    hasClose: false });
                if (result.button.accept) {
                    if (notebookTracker.currentWidget) {
                        let notebook = notebookTracker.currentWidget.model;
                        if (notebook) {
                            let metadata = notebook.getMetadata('JPSL');
                            if (!metadata) {
                                notebook.setMetadata('JPSL', { "noinstructortools": true });
                            }
                            else {
                                metadata.noinstructortools = true;
                                notebook.setMetadata('JPSL', metadata);
                            }
                            if (notebookTracker.currentWidget.content.widgets) {
                                for (const cell of notebookTracker.currentWidget.content.widgets) {
                                    let metadata = cell.model.getMetadata('JPSL');
                                    if (metadata) {
                                        metadata.noinstructortools = true;
                                        cell.model.setMetadata("JPSL", metadata);
                                    }
                                    else {
                                        cell.model.setMetadata("JPSL", { "noinstructortools": true });
                                    }
                                }
                            }
                        }
                        else {
                            window.alert("Set of disallow instructor tools flag failed. Is a notebook selected?");
                        }
                    }
                }
                console.log('Set disallow instructor tools flag has been called.');
            },
        });
        // Add selected commands to the command palette
        palette.addItem({
            command: activateinstructormenu.id,
            category: 'JPSL Instructor Tools',
            args: { origin: 'from the palette' },
        });
        palette.addItem({
            command: deactivateinstructormenu.id,
            category: 'JPSL Instructor Tools',
            args: { origin: 'from the palette' },
        });
        palette.addItem({
            command: disallowinstructormenu.id,
            category: 'JPSL Instructor Tools',
            args: { origin: 'from the palette' },
        });
        /*
            // Add a menu using the settings settingRegistry
            settingRegistry.load(extension.id);
        */
        /**
        * Create the menu that exposes the commands
         */
        /** submenus */
        // Protect cell submenu
        const protectsubmenu = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.MenuSvg({ commands });
        protectsubmenu.title.label = 'Cell Locking';
        protectsubmenu.addItem({
            command: protectcells.id,
            args: { label: protectcells.label, caption: protectcells.caption }
        });
        protectsubmenu.addItem({
            command: deprotectcells.id,
            args: { label: deprotectcells.label, caption: deprotectcells.caption }
        });
        protectsubmenu.addItem({
            command: indicateprotectcells.id,
            args: { label: indicateprotectcells.label, caption: indicateprotectcells.caption }
        });
        // Markdown cell highlighting menu
        const mkdownsubmenu = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.MenuSvg({ commands });
        mkdownsubmenu.title.label = 'Markdown Cell Highlighting';
        mkdownsubmenu.addItem({
            command: grnstart.id,
            args: { label: grnstart.label, caption: grnstart.caption }
        });
        mkdownsubmenu.addItem({
            command: brnstop.id,
            args: { label: brnstop.label, caption: brnstop.caption }
        });
        mkdownsubmenu.addItem({
            command: cyanhighlight.id,
            args: { label: cyanhighlight.label, caption: cyanhighlight.caption }
        });
        mkdownsubmenu.addItem({
            command: redhighlight.id,
            args: { label: redhighlight.label, caption: redhighlight.caption }
        });
        // Hide before printing submenu
        const hidebeforeprintsubmenu = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.MenuSvg({ commands });
        hidebeforeprintsubmenu.title.label = 'Hide before printing';
        hidebeforeprintsubmenu.addItem({
            command: sethidecellbeforeprint.id,
            args: { label: sethidecellbeforeprint.label, caption: sethidecellbeforeprint.caption }
        });
        hidebeforeprintsubmenu.addItem({
            command: unsethidecellbeforeprint.id,
            args: { label: unsethidecellbeforeprint.label, caption: unsethidecellbeforeprint.caption }
        });
        hidebeforeprintsubmenu.addItem({
            command: indicatehidecellbeforeprint.id,
            args: { label: indicatehidecellbeforeprint.label, caption: indicatehidecellbeforeprint.caption }
        });
        hidebeforeprintsubmenu.addItem({
            type: "separator"
        });
        hidebeforeprintsubmenu.addItem({
            command: sethidecodebeforeprint.id,
            args: { label: sethidecodebeforeprint.label, caption: sethidecodebeforeprint.caption }
        });
        hidebeforeprintsubmenu.addItem({
            command: unsethidecodebeforeprint.id,
            args: { label: unsethidecodebeforeprint.label, caption: unsethidecodebeforeprint.caption }
        });
        hidebeforeprintsubmenu.addItem({
            command: indicatehidecodebeforeprint.id,
            args: { label: indicatehidecodebeforeprint.label, caption: indicatehidecodebeforeprint.caption }
        });
        hidebeforeprintsubmenu.addItem({
            type: "separator"
        });
        hidebeforeprintsubmenu.addItem({
            command: tsthidebeforeprint.id,
            args: { label: tsthidebeforeprint.label, caption: tsthidebeforeprint.caption }
        });
        hidebeforeprintsubmenu.addItem({
            command: undohidebeforeprint.id,
            args: { label: undohidebeforeprint.label, caption: undohidebeforeprint.caption }
        });
        // Hide code in JPSL submenu
        const JPSLhidecodesubmenu = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.MenuSvg({ commands });
        JPSLhidecodesubmenu.title.label = 'Hide code in JPSL';
        JPSLhidecodesubmenu.addItem({
            command: sethidecodeJPSL.id,
            args: { label: sethidecodeJPSL.label, caption: sethidecodeJPSL.caption }
        });
        JPSLhidecodesubmenu.addItem({
            command: unsethidecodeJPSL.id,
            args: { label: unsethidecodeJPSL.label, caption: unsethidecodeJPSL.caption }
        });
        JPSLhidecodesubmenu.addItem({
            command: indicatehidecodeJPSL.id,
            args: { label: indicatehidecodeJPSL.label, caption: indicatehidecodeJPSL.caption }
        });
        // Add the menu using API
        const menu = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.MenuSvg({ commands });
        menu.title.label = 'JPSL Instructor Tools';
        menu.addClass('jp-JPSLInstructor-tools-menu'); // This only gets added to the popup when it is active.
        menu.addItem({
            command: insertInstructionBoilerPlate.id,
            args: { label: insertInstructionBoilerPlate.label, caption: insertInstructionBoilerPlate.caption }
        });
        menu.addItem({
            command: NewDataTable.id,
            args: { label: NewDataTable.label, caption: NewDataTable.caption }
        });
        menu.addItem({
            type: "submenu",
            args: { label: protectsubmenu.title.label },
            submenu: protectsubmenu
        });
        menu.addItem({
            type: "submenu",
            submenu: mkdownsubmenu,
            args: { label: mkdownsubmenu.title.label }
        });
        menu.addItem({
            type: "submenu",
            submenu: hidebeforeprintsubmenu,
            args: { label: hidebeforeprintsubmenu.title.label }
        });
        menu.addItem({
            type: "submenu",
            submenu: JPSLhidecodesubmenu,
            args: { label: JPSLhidecodesubmenu.title.label }
        });
        menu.addItem({
            command: insertmakePDFInstructions.id,
            args: { label: insertmakePDFInstructions.label, caption: insertmakePDFInstructions.caption }
        });
        // open documentation url
        menu.addItem({
            command: 'help:open',
            args: { text: "Instructor Tools Docs",
                url: "https://github.com/JupyterPhysSciLab/jupyter-instructortools",
                newBrowserTab: "true" }
        });
        MainMenu.addMenu(menu);
        // Hide the popup so that the title is just a placeholder until activated
        menu.hide();
        async function _updateforbiddenstate(sender, Args) {
            console.log(`Update forbidden states has been called.`);
            if (!menuactive) {
                // Make sure it is hidden
                commands.execute('Hide:JPSLInstructorTools:main-menu');
                return;
            }
            if (notebookTracker.currentWidget) {
                await notebookTracker.currentWidget.revealed;
                if (notebookTracker.currentWidget.model) {
                    const notebookmeta = notebookTracker.currentWidget.model.getMetadata("JPSL");
                    if (notebookmeta) {
                        if (notebookmeta.noinstructortools != null) {
                            commands.execute('Hide:JPSLInstructorTools:main-menu');
                            thistoolforbidden = true;
                            return;
                        }
                    }
                }
                if (notebookTracker.currentWidget.content.widgets) {
                    for (const cell of notebookTracker.currentWidget.content.widgets) {
                        let metadata = cell.model.getMetadata('JPSL');
                        if (metadata) {
                            if (metadata.noinstructortools != null) {
                                commands.execute('Hide:JPSLInstructorTools:main-menu');
                                thistoolforbidden = true;
                                return;
                            }
                        }
                    }
                }
                thistoolforbidden = false;
                commands.execute('Show:JPSLInstructorTools:main-menu');
            }
            else {
                // No notebook so should not show menu
                commands.execute('Hide:JPSLInstructorTools:main-menu');
            }
        }
        // subscribe to the notebookTracker changed signals
        notebookTracker.widgetAdded.connect(_updateforbiddenstate);
        notebookTracker.currentChanged.connect(_updateforbiddenstate);
        console.log('JupyterLab extension JPSLInstructorTools is activated!');
        console.log('The app is:', app);
        console.log('The shell is:', app.shell);
        console.log('notebookTracker', notebookTracker);
        console.log('notebookTools', notebookTools);
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.ca6bbb43935265337010.js.map