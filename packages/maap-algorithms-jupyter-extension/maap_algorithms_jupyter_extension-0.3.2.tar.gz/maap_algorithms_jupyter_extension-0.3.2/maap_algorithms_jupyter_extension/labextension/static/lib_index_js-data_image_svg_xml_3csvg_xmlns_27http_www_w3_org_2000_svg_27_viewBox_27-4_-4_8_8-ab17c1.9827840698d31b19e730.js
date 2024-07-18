"use strict";
(self["webpackChunkmaap_algorithms_jupyter_extension"] = self["webpackChunkmaap_algorithms_jupyter_extension"] || []).push([["lib_index_js-data_image_svg_xml_3csvg_xmlns_27http_www_w3_org_2000_svg_27_viewBox_27-4_-4_8_8-ab17c1"],{

/***/ "./node_modules/css-loader/dist/cjs.js!./style/actionBar.css":
/*!*******************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/actionBar.css ***!
  \*******************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, `.action-bar {
    display: flex;
    flex-direction: row-reverse;
    margin: 1rem;
}`, "",{"version":3,"sources":["webpack://./style/actionBar.css"],"names":[],"mappings":"AAAA;IACI,aAAa;IACb,2BAA2B;IAC3B,YAAY;AAChB","sourcesContent":[".action-bar {\n    display: flex;\n    flex-direction: row-reverse;\n    margin: 1rem;\n}"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./lib/classes/App.js":
/*!****************************!*\
  !*** ./lib/classes/App.js ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   AlgorithmCatalogWidget: () => (/* binding */ AlgorithmCatalogWidget),
/* harmony export */   RegisterAlgorithmsWidget: () => (/* binding */ RegisterAlgorithmsWidget)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react-redux */ "webpack/sharing/consume/default/react-redux/react-redux");
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react_redux__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../constants */ "./lib/constants.js");
/* harmony import */ var _redux_store__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../redux/store */ "./lib/redux/store.js");
/* harmony import */ var regenerator_runtime_runtime__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! regenerator-runtime/runtime */ "./node_modules/regenerator-runtime/runtime.js");
/* harmony import */ var regenerator_runtime_runtime__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(regenerator_runtime_runtime__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _components_AlgorithmsApp__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../components/AlgorithmsApp */ "./lib/components/AlgorithmsApp.js");
/* harmony import */ var _components_RegistrationForm__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../components/RegistrationForm */ "./lib/components/RegistrationForm.js");








class AlgorithmCatalogWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ReactWidget {
    jupyterApp;
    constructor(jupyterApp) {
        super();
        this.addClass(_constants__WEBPACK_IMPORTED_MODULE_4__.JUPYTER_EXT.EXTENSION_CSS_CLASSNAME);
        this.jupyterApp = jupyterApp;
    }
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_redux__WEBPACK_IMPORTED_MODULE_2__.Provider, { store: _redux_store__WEBPACK_IMPORTED_MODULE_5__.store },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_AlgorithmsApp__WEBPACK_IMPORTED_MODULE_6__.AlgorithmsApp, { jupyterApp: this.jupyterApp })));
    }
}
class RegisterAlgorithmsWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ReactWidget {
    data;
    constructor(data) {
        super();
        this.addClass(_constants__WEBPACK_IMPORTED_MODULE_4__.JUPYTER_EXT.EXTENSION_CSS_CLASSNAME);
        this.data = data;
    }
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_redux__WEBPACK_IMPORTED_MODULE_2__.Provider, { store: _redux_store__WEBPACK_IMPORTED_MODULE_5__.store },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_RegistrationForm__WEBPACK_IMPORTED_MODULE_7__.RegistrationForm, { data: this.data })));
    }
}


/***/ }),

/***/ "./lib/components/ActionBar.js":
/*!*************************************!*\
  !*** ./lib/components/ActionBar.js ***!
  \*************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ActionBar: () => (/* binding */ ActionBar)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react_bootstrap__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react-bootstrap */ "webpack/sharing/consume/default/react-bootstrap/react-bootstrap");
/* harmony import */ var react_bootstrap__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _style_actionBar_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../style/actionBar.css */ "./style/actionBar.css");
/* harmony import */ var _utils_jupyter__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../utils/jupyter */ "./lib/utils/jupyter.js");




const ActionBar = ({ jupyterApp }) => {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "action-bar" },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Button, { variant: "primary", onClick: () => (0,_utils_jupyter__WEBPACK_IMPORTED_MODULE_3__.openRegistration)(jupyterApp, null) }, "+ New Algorithm")));
};


/***/ }),

/***/ "./lib/components/AlgorithmDetails.js":
/*!********************************************!*\
  !*** ./lib/components/AlgorithmDetails.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   AlgorithmDetails: () => (/* binding */ AlgorithmDetails)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react_bootstrap__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react-bootstrap */ "webpack/sharing/consume/default/react-bootstrap/react-bootstrap");
/* harmony import */ var react_bootstrap__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react-redux */ "webpack/sharing/consume/default/react-redux/react-redux");
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react_redux__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _redux_slices_registeredAlgorithms__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../redux/slices/registeredAlgorithms */ "./lib/redux/slices/registeredAlgorithms.js");




const AlgorithmDetails = () => {
    // Redux
    const { selectedAlgorithm } = (0,react_redux__WEBPACK_IMPORTED_MODULE_2__.useSelector)(_redux_slices_registeredAlgorithms__WEBPACK_IMPORTED_MODULE_3__.selectRegisteredAlgorithms);
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "job-details-container" },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("h2", null, "Algorithm Details"),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Tab.Container, { id: "left-tabs-example", defaultActiveKey: "general" },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Nav, { variant: "pills", className: "nav-menu" },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Nav.Item, null,
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Nav.Link, { eventKey: "general" }, "General")),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Nav.Item, null,
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Nav.Link, { eventKey: "inputs" }, "Inputs"))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Tab.Content, { className: "content-padding" },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Tab.Pane, { eventKey: "general" }),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Tab.Pane, { eventKey: "inputs" },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("table", null,
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("thead", null,
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", null,
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("th", null, "ID"),
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("th", null, "Data Type"),
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("th", null, "Default Value"),
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("th", null, "Required?"))),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tbody", null, selectedAlgorithm ?
                            selectedAlgorithm.inputs.map((input) => {
                                console.log("iterating over inputs");
                                console.log(input);
                                return react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", null,
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, input.id),
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, input.dataType),
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, input.defaultValue),
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, input.required));
                            }) : react__WEBPACK_IMPORTED_MODULE_0___default().createElement("i", null, "\"No algorithm selected\""))))))));
};


/***/ }),

/***/ "./lib/components/Algorithms.js":
/*!**************************************!*\
  !*** ./lib/components/Algorithms.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   Algorithms: () => (/* binding */ Algorithms)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react_table__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react-table */ "webpack/sharing/consume/default/react-table/react-table");
/* harmony import */ var react_table__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react_table__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react_bootstrap__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react-bootstrap */ "webpack/sharing/consume/default/react-bootstrap/react-bootstrap");
/* harmony import */ var react_bootstrap__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react_bootstrap__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _ActionBar__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./ActionBar */ "./lib/components/ActionBar.js");
/* harmony import */ var react_icons_bs__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! react-icons/bs */ "./node_modules/react-icons/bs/index.esm.js");
/* harmony import */ var _redux_slices_splitPaneSlice__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../redux/slices/splitPaneSlice */ "./lib/redux/slices/splitPaneSlice.js");
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react-redux */ "webpack/sharing/consume/default/react-redux/react-redux");
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(react_redux__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _utils_jupyter__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../utils/jupyter */ "./lib/utils/jupyter.js");
/* harmony import */ var _redux_slices_registeredAlgorithms__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../redux/slices/registeredAlgorithms */ "./lib/redux/slices/registeredAlgorithms.js");
/* harmony import */ var _utils_api__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../utils/api */ "./lib/utils/api.js");










function DefaultColumnFilter({ column: { filterValue, preFilteredRows, setFilter, columns }, }) {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("input", { value: filterValue || '', onChange: e => {
            setFilter(e.target.value || undefined);
        }, placeholder: `Search...` }));
}
function ReactTable({ columns, data, jupyterApp }) {
    // Redux
    const dispatch = (0,react_redux__WEBPACK_IMPORTED_MODULE_3__.useDispatch)();
    const { setSelectedAlgorithm } = _redux_slices_registeredAlgorithms__WEBPACK_IMPORTED_MODULE_4__.registeredAlgorithmsActions;
    const { rowCount } = (0,react_redux__WEBPACK_IMPORTED_MODULE_3__.useSelector)(_redux_slices_splitPaneSlice__WEBPACK_IMPORTED_MODULE_5__.selectSplitPane);
    const { algorithmsList } = (0,react_redux__WEBPACK_IMPORTED_MODULE_3__.useSelector)(_redux_slices_registeredAlgorithms__WEBPACK_IMPORTED_MODULE_4__.selectRegisteredAlgorithms);
    // Local
    const [hoveredRowIndex, setHoveredRowIndex] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(null);
    const [show, setShow] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(false);
    const [unregisterAlgoID, setUnregisterAlgoID] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)("");
    const [showSpinner, setShowSpinner] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(false);
    const handleRowHover = rowIndex => {
        setHoveredRowIndex(rowIndex);
    };
    const handleRowClick = row => {
        const algorithm = row.original;
        console.log("Data: ", algorithm);
        dispatch(setSelectedAlgorithm(algorithm));
    };
    const handleUnregisterModal = row => {
        setUnregisterAlgoID(row.values.id);
        setShow(true);
    };
    const handleUnregistration = algoID => {
        (0,_utils_api__WEBPACK_IMPORTED_MODULE_6__.unregisterAlgorithm)(algoID).finally(() => {
            console.log("unregistered return");
        });
    };
    const handleClose = () => setShow(false);
    const defaultColumn = react__WEBPACK_IMPORTED_MODULE_0___default().useMemo(() => ({
        Filter: DefaultColumnFilter,
    }), []);
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        setPageSize(rowCount);
    }, [rowCount]);
    // useEffect(() => {
    //     console.log("Algorithms")
    //     console.log(algorithmsData)
    // }, [algorithmsData]);
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        setShowSpinner(true);
        (0,_utils_api__WEBPACK_IMPORTED_MODULE_6__.describeAllAlgorithms)().finally(() => setShowSpinner(false));
    }, [algorithmsList]);
    const { getTableProps, getTableBodyProps, headerGroups, rows, canPreviousPage, canNextPage, prepareRow, pageOptions, pageCount, gotoPage, nextPage, previousPage, setPageSize, state: { pageIndex, pageSize } } = (0,react_table__WEBPACK_IMPORTED_MODULE_1__.useTable)({
        defaultColumn,
        columns,
        data,
        initialState: { pageIndex: 0, pageSize: rowCount }
    }, react_table__WEBPACK_IMPORTED_MODULE_1__.useFilters, react_table__WEBPACK_IMPORTED_MODULE_1__.usePagination);
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_2__.Table, { ...getTableProps(), className: 'hover' },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("thead", null, headerGroups.map(headerGroup => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", { ...headerGroup.getHeaderGroupProps() }, headerGroup.headers.map(column => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("th", { ...column.getHeaderProps() },
                column.render('Header'),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", null, column.canFilter ? column.render('Filter') : null)))))))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tbody", { ...getTableBodyProps() }, showSpinner ? react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", { colSpan: columns.length, style: { textAlign: "center" } },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_2__.Spinner, { animation: "border", variant: "primary" }))) :
                rows.map((row, i) => {
                    prepareRow(row);
                    const isRowHovered = i === hoveredRowIndex;
                    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", { ...row.getRowProps(), onClick: () => handleRowClick(row), onMouseEnter: () => handleRowHover(i), onMouseLeave: () => handleRowHover(null), className: isRowHovered ? 'hovered' : '' },
                        row.cells.map(cell => {
                            return react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", { ...cell.getCellProps() }, cell.render('Cell'));
                        }),
                        isRowHovered ? (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", { className: "row-actions" },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_bs__WEBPACK_IMPORTED_MODULE_7__.BsFillPlayFill, { color: 'green', size: 18, title: "Run", onClick: () => (0,_utils_jupyter__WEBPACK_IMPORTED_MODULE_8__.openJobs)(jupyterApp, row) }),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_bs__WEBPACK_IMPORTED_MODULE_7__.BsFillTrash3Fill, { color: 'red', size: 16, title: "Unregister", onClick: () => handleUnregisterModal(row) }))) : react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null)));
                }))),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: 'pagination-footer' },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", null,
                "Showing ",
                pageOptions.length === 0 ? 0 : pageIndex + 1,
                " of ",
                pageOptions.length),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_2__.Pagination, null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_2__.Pagination.First, { onClick: () => gotoPage(0), disabled: !canPreviousPage }),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_2__.Pagination.Prev, { onClick: () => previousPage(), disabled: !canPreviousPage }),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_2__.Pagination.Next, { onClick: () => nextPage(), disabled: !canNextPage }),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_2__.Pagination.Last, { onClick: () => gotoPage(pageCount - 1), disabled: !canNextPage }))),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_2__.Modal, { show: show, onHide: handleClose, centered: true },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_2__.Modal.Header, { closeButton: true },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_bs__WEBPACK_IMPORTED_MODULE_7__.BsExclamationTriangleFill, { color: 'red', size: 30, className: "margin-right-1" })),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_2__.Modal.Body, null,
                "Are you sure you want to unregister ",
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("i", null, unregisterAlgoID),
                " ?"),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_2__.Modal.Footer, null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_2__.Button, { variant: "secondary", onClick: handleClose }, "Cancel"),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_2__.Button, { variant: "danger", onClick: () => handleUnregistration(unregisterAlgoID) }, "Unregister")))));
}
const Algorithms = ({ jupyterApp }) => {
    const { algorithmsData } = (0,react_redux__WEBPACK_IMPORTED_MODULE_3__.useSelector)(_redux_slices_registeredAlgorithms__WEBPACK_IMPORTED_MODULE_4__.selectRegisteredAlgorithms);
    const data = (0,react__WEBPACK_IMPORTED_MODULE_0__.useMemo)(() => algorithmsData, [algorithmsData]);
    const columns = (0,react__WEBPACK_IMPORTED_MODULE_0__.useMemo)(() => [
        {
            Header: 'Algorithm ID',
            accessor: 'id',
        }
        // {
        //     Header: 'Creator',
        //     accessor: 'creator' as const,
        //     width: 50
        // },
        // {
        //     Header: 'Description',
        //     accessor: 'description' as const,
        // },
        // {
        //     Header: 'Last Updated',
        //     accessor: 'time_last_update' as const,
        //     width: 100
        // }
    ], []);
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_ActionBar__WEBPACK_IMPORTED_MODULE_9__.ActionBar, { jupyterApp: jupyterApp }),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(ReactTable, { columns: columns, data: data, jupyterApp: jupyterApp })));
};


/***/ }),

/***/ "./lib/components/AlgorithmsApp.js":
/*!*****************************************!*\
  !*** ./lib/components/AlgorithmsApp.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   AlgorithmsApp: () => (/* binding */ AlgorithmsApp)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _Algorithms__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./Algorithms */ "./lib/components/Algorithms.js");
/* harmony import */ var bootstrap_dist_css_bootstrap_min_css__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! bootstrap/dist/css/bootstrap.min.css */ "./node_modules/bootstrap/dist/css/bootstrap.min.css");
/* harmony import */ var react_split_pane__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react-split-pane */ "webpack/sharing/consume/default/react-split-pane/react-split-pane");
/* harmony import */ var react_split_pane__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react_split_pane__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _AlgorithmDetails__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./AlgorithmDetails */ "./lib/components/AlgorithmDetails.js");
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react-redux */ "webpack/sharing/consume/default/react-redux/react-redux");
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(react_redux__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _redux_slices_splitPaneSlice__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../redux/slices/splitPaneSlice */ "./lib/redux/slices/splitPaneSlice.js");
/* harmony import */ var _utils_api__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../utils/api */ "./lib/utils/api.js");









// import { useDispatch } from 'react-redux';
const AlgorithmsApp = ({ jupyterApp }) => {
    // Redux
    const dispatch = (0,react_redux__WEBPACK_IMPORTED_MODULE_3__.useDispatch)();
    const { updateSize } = _redux_slices_splitPaneSlice__WEBPACK_IMPORTED_MODULE_4__.splitPaneActions;
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        (0,_utils_api__WEBPACK_IMPORTED_MODULE_5__.getAlgorithms)();
    }, []);
    const handleDragFinish = (size) => {
        console.log("Sizes: ");
        console.log(size);
        let newSize = Math.floor(size[0] / 4000) - 1;
        if (newSize < 1) {
            newSize = 1;
        }
        console.log(newSize);
        dispatch(updateSize(newSize));
    };
    let splitPaneProps = {
        split: "horizontal",
        defaultSize: 200,
        primary: "first",
        onChange: (size) => handleDragFinish(size),
        pane1Style: { "position": "relative" }
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react_split_pane__WEBPACK_IMPORTED_MODULE_2___default()), { ...splitPaneProps },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react_split_pane__WEBPACK_IMPORTED_MODULE_2___default()), null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_Algorithms__WEBPACK_IMPORTED_MODULE_6__.Algorithms, { jupyterApp: jupyterApp })),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react_split_pane__WEBPACK_IMPORTED_MODULE_2___default()), null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_AlgorithmDetails__WEBPACK_IMPORTED_MODULE_7__.AlgorithmDetails, null))));
};


/***/ }),

/***/ "./lib/components/EmptyRow.js":
/*!************************************!*\
  !*** ./lib/components/EmptyRow.js ***!
  \************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   EmptyRow: () => (/* binding */ EmptyRow)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../constants */ "./lib/constants.js");


const EmptyRow = ({ text }) => {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", { colSpan: _constants__WEBPACK_IMPORTED_MODULE_1__.COLUMN_SPAN, className: "empty-row" }, text)));
};


/***/ }),

/***/ "./lib/components/InputRow.js":
/*!************************************!*\
  !*** ./lib/components/InputRow.js ***!
  \************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   InputRow: () => (/* binding */ InputRow)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react_bootstrap__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react-bootstrap */ "webpack/sharing/consume/default/react-bootstrap/react-bootstrap");
/* harmony import */ var react_bootstrap__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../constants */ "./lib/constants.js");
/* harmony import */ var react_icons_bs__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react-icons/bs */ "./node_modules/react-icons/bs/index.esm.js");




const InputRow = ({ row, handleRemoveRow, handleDataChange }) => {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", { className: "input-row", id: row.inputId.toString() },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Form.Control, { id: _constants__WEBPACK_IMPORTED_MODULE_2__.ALGO_INPUT_FIELDS.INPUT_NAME, type: "text", placeholder: "What is the input name?", onChange: handleDataChange, value: row.inputName })),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Form.Control, { id: _constants__WEBPACK_IMPORTED_MODULE_2__.ALGO_INPUT_FIELDS.INPUT_DESC, type: "text", placeholder: "Describe the input parameter", onChange: handleDataChange, value: row.inputDesc })),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Form.Switch, { id: _constants__WEBPACK_IMPORTED_MODULE_2__.ALGO_INPUT_FIELDS.IS_REQUIRED, className: "center-align", "aria-label": "required_input", onChange: handleDataChange, checked: row.isRequired })),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Form.Control, { id: _constants__WEBPACK_IMPORTED_MODULE_2__.ALGO_INPUT_FIELDS.INPUT_DEFAULT, type: "text", placeholder: "Default value", onChange: handleDataChange, value: row.inputDefault })),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", { style: { verticalAlign: "middle" } },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_bs__WEBPACK_IMPORTED_MODULE_3__.BsFillXCircleFill, { className: "danger-icon", id: row.inputId.toString(), onClick: () => handleRemoveRow(row.inputId.toString()) })))));
};


/***/ }),

/***/ "./lib/components/RegistrationForm.js":
/*!********************************************!*\
  !*** ./lib/components/RegistrationForm.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   RegistrationForm: () => (/* binding */ RegistrationForm)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react_bootstrap__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react-bootstrap */ "webpack/sharing/consume/default/react-bootstrap/react-bootstrap");
/* harmony import */ var react_bootstrap__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react_icons_bs__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! react-icons/bs */ "./node_modules/react-icons/bs/index.esm.js");
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react-redux */ "webpack/sharing/consume/default/react-redux/react-redux");
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react_redux__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _redux_slices_algorithmSlice__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../redux/slices/algorithmSlice */ "./lib/redux/slices/algorithmSlice.js");
/* harmony import */ var _TableFileInputs__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./TableFileInputs */ "./lib/components/TableFileInputs.js");
/* harmony import */ var _TablePositionalInputs__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./TablePositionalInputs */ "./lib/components/TablePositionalInputs.js");
/* harmony import */ var _utils_algoConfig__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../utils/algoConfig */ "./lib/utils/algoConfig.js");
/* harmony import */ var react_select_async__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react-select/async */ "./node_modules/react-select/async/dist/react-select-async.esm.js");
/* harmony import */ var _utils_api__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../utils/api */ "./lib/utils/api.js");
/* harmony import */ var _utils_utils__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../utils/utils */ "./lib/utils/utils.js");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4__);












const RegistrationForm = ({ data }) => {
    // Local state variables
    const [firstStep, setFirstStep] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(true);
    // const [validRepo, setValidRepo] = useState(false)
    const [validRepo, setValidRepo] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(true);
    const [repoBranches, setRepoBranches] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)([]);
    const [firstRepoCheck, setFirstRepoCheck] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(true);
    const [show, setShow] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(false);
    const [showSpinner, setShowSpinner] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(false);
    const [showNotification, setShowNotification] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(false);
    // Redux
    const dispatch = (0,react_redux__WEBPACK_IMPORTED_MODULE_2__.useDispatch)();
    const { registrationUrl, repoRunCommand, algoResource, algoContainer } = (0,react_redux__WEBPACK_IMPORTED_MODULE_2__.useSelector)(_redux_slices_algorithmSlice__WEBPACK_IMPORTED_MODULE_5__.selectAlgorithm);
    const { setAlgoDesc, setAlgoDiskSpace, setAlgoName, setAlgoResource, setAlgoContainerURL, setRepoBranch, setRepoRunCommand, setRepoBuildCommand, setRepoUrl } = _redux_slices_algorithmSlice__WEBPACK_IMPORTED_MODULE_5__.algorithmActions;
    const validateRepo = (e) => {
        (0,_utils_utils__WEBPACK_IMPORTED_MODULE_6__.checkUrlExists)(e.target.value) ? setValidRepo(true) : setValidRepo(false);
        setFirstRepoCheck(false);
    };
    const handleKeyPress = (e) => {
        if (e.keyCode === 13) {
            e.target.blur();
        }
    };
    const handleAlgoNameChange = e => {
        dispatch(setAlgoName(e.target.value));
    };
    const handleRepoUrlChange = e => {
        dispatch(setRepoUrl(e.target.value));
    };
    const handleBranchChange = e => {
        dispatch(setRepoBranch(e.target.value));
    };
    const handleRunCmdChange = e => {
        dispatch(setRepoRunCommand(e.target.value));
    };
    const handleBuildCmdChange = e => {
        dispatch(setRepoBuildCommand(e.target.value));
    };
    const handleAlgoDescChange = e => {
        dispatch(setAlgoDesc(e.target.value));
    };
    const handleDiskSpaceChange = e => {
        dispatch(setAlgoDiskSpace(e.target.value));
    };
    const handleResourceChange = value => {
        dispatch(setAlgoResource(value));
    };
    const handleContainerURLChange = e => {
        dispatch(setAlgoContainerURL(e.target.value));
    };
    const handleModalClose = () => setShow(false);
    const handleModalShow = () => setShow(true);
    async function submitHandler(e) {
        e.preventDefault();
        // setShowSpinner(true)
        let res = await (0,_utils_algoConfig__WEBPACK_IMPORTED_MODULE_7__.registerAlgorithm)();
        if (res) {
            // setShowSpinner(false)
            handleModalShow();
            setShowNotification(true);
        }
    }
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        // The container from which the workspace is running will be the default container for algorithm registration.
        (0,_utils_api__WEBPACK_IMPORTED_MODULE_8__.getWorkspaceContainer)().then((param) => {
            let container = param["DOCKERIMAGE_PATH"];
            if (container != null) {
                dispatch(setAlgoContainerURL(container));
            }
        });
    }, []);
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        if (showNotification) {
            _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4__.Notification.success("The algorithm was successfully submitted.", {
                autoClose: 5000,
                actions: [
                    {
                        label: 'View algorithm registration progress here',
                        callback: event => {
                            event.preventDefault();
                            window.open(registrationUrl, '_blank', 'noreferrer');
                        },
                        displayType: 'link'
                    }
                ]
            });
            setShowNotification(false);
        }
    }, [showNotification]);
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Form, { onSubmit: submitHandler },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: 'section-padding' },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("h2", null, "Register Algorithm"),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Alert, { variant: "primary", className: "alert-box" },
                    "To register an algorithm to the MAAP, your code must be committed to a public code repository.",
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("br", null),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("br", null),
                    "Need more tips and tricks? Documentation may be found ",
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("a", { href: "" }, "here"),
                    "."),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("h3", null, "Repository Information"),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Table, { className: "form-table" },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tbody", null,
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", null,
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, "Repository URL"),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", { className: 'flex' },
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", null,
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: 'flex' },
                                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Form.Control, { onChange: handleRepoUrlChange, onKeyDown: handleKeyPress, onBlur: validateRepo, type: "text", placeholder: "Enter repository URL" }),
                                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: firstRepoCheck ? 'hide' : 'show' }, validRepo ? react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_bs__WEBPACK_IMPORTED_MODULE_9__.BsFillCheckCircleFill, { className: 'success-icon' }) : react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_bs__WEBPACK_IMPORTED_MODULE_9__.BsFillXCircleFill, { className: 'danger-icon' }))),
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: firstStep ? firstRepoCheck ? 'hide' : 'show' : 'hide' })))),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", null,
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, "Repository Branch"),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null,
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Form.Control, { type: "text", placeholder: "Enter repository branch", onChange: handleBranchChange }))),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", null,
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, "Run Command"),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null,
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Form.Control, { type: "text", placeholder: "Enter run command", onChange: handleRunCmdChange }))),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", null,
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, "Build Command"),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null,
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Form.Control, { type: "text", placeholder: "Enter build command", onChange: handleBuildCmdChange })))))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: 'section-padding' },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("h3", null, "General Information"),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Table, { className: "form-table" },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tbody", null,
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", null,
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, "Algorithm Name"),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null,
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Form.Control, { type: "text", placeholder: "Enter algorithm name", onChange: handleAlgoNameChange }))),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", null,
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, "Algorithm Description"),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null,
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Form.Control, { type: "textarea", placeholder: "Enter algorithm description", onChange: handleAlgoDescChange }))),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", null,
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, "Disk Space (GB)"),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null,
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Form.Control, { type: "text", placeholder: "Enter disk space", onChange: handleDiskSpaceChange }))),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", null,
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, "Resource Allocation"),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null,
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Form.Group, { className: "mb-3 algorithm-input" },
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_select_async__WEBPACK_IMPORTED_MODULE_3__["default"], { cacheOptions: true, defaultOptions: true, value: algoResource, loadOptions: _utils_api__WEBPACK_IMPORTED_MODULE_8__.getResources, onChange: handleResourceChange, placeholder: "Select resource" })))),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", null,
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, "Container URL"),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null,
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Form.Control, { type: "text", defaultValue: algoContainer, placeholder: "Enter container URL", onChange: handleContainerURLChange }))))),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: 'section-padding' },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("h3", null, "Inputs"),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_TableFileInputs__WEBPACK_IMPORTED_MODULE_10__.TableFileInputs, null),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_TablePositionalInputs__WEBPACK_IMPORTED_MODULE_11__.TablePositionalInputs, null)),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Button, { variant: "primary", type: "submit" }, "Register Algorithm"))),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Modal, { show: show, "aria-labelledby": "contained-modal-title-vcenter", onHide: handleModalClose },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Modal.Header, { closeButton: true },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Modal.Title, null, "Algorithm submitted for registration")),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Modal.Body, null,
                    "Your algorithm was submitted for registration. You can view the progress here: ",
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("a", { href: registrationUrl, target: "_blank" }, registrationUrl)),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Modal.Footer, null,
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Button, { variant: "primary", onClick: handleModalClose }, "Close"))))));
};


/***/ }),

/***/ "./lib/components/TableFileInputs.js":
/*!*******************************************!*\
  !*** ./lib/components/TableFileInputs.js ***!
  \*******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   TableFileInputs: () => (/* binding */ TableFileInputs)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react_bootstrap__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react-bootstrap */ "webpack/sharing/consume/default/react-bootstrap/react-bootstrap");
/* harmony import */ var react_bootstrap__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react_icons_bs__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! react-icons/bs */ "./node_modules/react-icons/bs/index.esm.js");
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react-redux */ "webpack/sharing/consume/default/react-redux/react-redux");
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react_redux__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _redux_slices_algorithmSlice__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../redux/slices/algorithmSlice */ "./lib/redux/slices/algorithmSlice.js");
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../constants */ "./lib/constants.js");
/* harmony import */ var _InputRow__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./InputRow */ "./lib/components/InputRow.js");
/* harmony import */ var _EmptyRow__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./EmptyRow */ "./lib/components/EmptyRow.js");
/* harmony import */ var react_tooltip__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react-tooltip */ "webpack/sharing/consume/default/react-tooltip/react-tooltip");
/* harmony import */ var react_tooltip__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(react_tooltip__WEBPACK_IMPORTED_MODULE_3__);









const TableFileInputs = () => {
    // Redux
    const dispatch = (0,react_redux__WEBPACK_IMPORTED_MODULE_2__.useDispatch)();
    const { fileData, inputId } = (0,react_redux__WEBPACK_IMPORTED_MODULE_2__.useSelector)(_redux_slices_algorithmSlice__WEBPACK_IMPORTED_MODULE_4__.selectAlgorithm);
    const { addFileData, updateFileData, removeFileData, incrementInputId } = _redux_slices_algorithmSlice__WEBPACK_IMPORTED_MODULE_4__.algorithmActions;
    const addRow = () => {
        dispatch(addFileData({ [_constants__WEBPACK_IMPORTED_MODULE_5__.ALGO_INPUT_FIELDS.INPUT_NAME]: "",
            [_constants__WEBPACK_IMPORTED_MODULE_5__.ALGO_INPUT_FIELDS.INPUT_DEFAULT]: "",
            [_constants__WEBPACK_IMPORTED_MODULE_5__.ALGO_INPUT_FIELDS.INPUT_DESC]: "",
            [_constants__WEBPACK_IMPORTED_MODULE_5__.ALGO_INPUT_FIELDS.IS_REQUIRED]: false,
            [_constants__WEBPACK_IMPORTED_MODULE_5__.ALGO_INPUT_FIELDS.INPUT_ID]: inputId }));
        dispatch(incrementInputId());
    };
    const handleDataChange = e => {
        switch (e.target.type) {
            case "checkbox": {
                dispatch(updateFileData({ inputId: e.target.parentNode.parentNode.parentNode.id, inputField: [e.target.id], inputValue: e.target.checked }));
                break;
            }
            default:
                dispatch(updateFileData({ inputId: e.target.parentNode.parentNode.id, inputField: [e.target.id], inputValue: e.target.value }));
                break;
        }
    };
    const handleRemoveRow = (inputId) => {
        dispatch(removeFileData({ key: inputId }));
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "input-types" },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("h4", null, "File Inputs"),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_tooltip__WEBPACK_IMPORTED_MODULE_3__.Tooltip, { anchorId: "file_input_info", place: "right", variant: "dark", content: _constants__WEBPACK_IMPORTED_MODULE_5__.ALGO_INPUTS_DESC.FILE_INPUTS }),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { id: "file_input_info" },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_bs__WEBPACK_IMPORTED_MODULE_6__.BsInfoCircle, null))),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Table, { className: "inputs-table" },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("thead", null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", null,
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null,
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_bs__WEBPACK_IMPORTED_MODULE_6__.BsPlusCircleFill, { className: "success-icon", onClick: addRow })),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, "Name"),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, "Description"),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", { className: "center-align" }, "Required?"),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, "Default Value"),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tbody", null, fileData.length == 0 ? react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_EmptyRow__WEBPACK_IMPORTED_MODULE_7__.EmptyRow, { text: "No inputs specified" }) : Object.entries(fileData).map(([key, data]) => {
                return react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_InputRow__WEBPACK_IMPORTED_MODULE_8__.InputRow, { row: data, handleRemoveRow: handleRemoveRow, handleDataChange: handleDataChange });
            })))));
};


/***/ }),

/***/ "./lib/components/TablePositionalInputs.js":
/*!*************************************************!*\
  !*** ./lib/components/TablePositionalInputs.js ***!
  \*************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   TablePositionalInputs: () => (/* binding */ TablePositionalInputs)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react_bootstrap__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react-bootstrap */ "webpack/sharing/consume/default/react-bootstrap/react-bootstrap");
/* harmony import */ var react_bootstrap__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react_icons_bs__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! react-icons/bs */ "./node_modules/react-icons/bs/index.esm.js");
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react-redux */ "webpack/sharing/consume/default/react-redux/react-redux");
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react_redux__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _redux_slices_algorithmSlice__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../redux/slices/algorithmSlice */ "./lib/redux/slices/algorithmSlice.js");
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../constants */ "./lib/constants.js");
/* harmony import */ var _InputRow__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./InputRow */ "./lib/components/InputRow.js");
/* harmony import */ var _EmptyRow__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./EmptyRow */ "./lib/components/EmptyRow.js");
/* harmony import */ var react_tooltip__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react-tooltip */ "webpack/sharing/consume/default/react-tooltip/react-tooltip");
/* harmony import */ var react_tooltip__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(react_tooltip__WEBPACK_IMPORTED_MODULE_3__);









const TablePositionalInputs = () => {
    // Redux
    const dispatch = (0,react_redux__WEBPACK_IMPORTED_MODULE_2__.useDispatch)();
    const { positionalData, inputId } = (0,react_redux__WEBPACK_IMPORTED_MODULE_2__.useSelector)(_redux_slices_algorithmSlice__WEBPACK_IMPORTED_MODULE_4__.selectAlgorithm);
    const { addPositionalData, updatePositionalData, removePositionalData, incrementInputId } = _redux_slices_algorithmSlice__WEBPACK_IMPORTED_MODULE_4__.algorithmActions;
    const addRow = () => {
        dispatch(addPositionalData({ [_constants__WEBPACK_IMPORTED_MODULE_5__.ALGO_INPUT_FIELDS.INPUT_NAME]: "",
            [_constants__WEBPACK_IMPORTED_MODULE_5__.ALGO_INPUT_FIELDS.INPUT_DEFAULT]: "",
            [_constants__WEBPACK_IMPORTED_MODULE_5__.ALGO_INPUT_FIELDS.INPUT_DESC]: "",
            [_constants__WEBPACK_IMPORTED_MODULE_5__.ALGO_INPUT_FIELDS.IS_REQUIRED]: false,
            [_constants__WEBPACK_IMPORTED_MODULE_5__.ALGO_INPUT_FIELDS.INPUT_ID]: inputId }));
        dispatch(incrementInputId());
    };
    const handleDataChange = e => {
        switch (e.target.type) {
            case "checkbox": {
                dispatch(updatePositionalData({ inputId: e.target.parentNode.parentNode.parentNode.id, inputField: [e.target.id], inputValue: e.target.checked }));
                break;
            }
            default:
                dispatch(updatePositionalData({ inputId: e.target.parentNode.parentNode.id, inputField: [e.target.id], inputValue: e.target.value }));
                break;
        }
    };
    const handleRemoveRow = (inputId) => {
        dispatch(removePositionalData({ key: inputId }));
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "input-types" },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("h4", null, "Positional Inputs"),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_tooltip__WEBPACK_IMPORTED_MODULE_3__.Tooltip, { anchorId: "positional_input_info", place: "right", variant: "dark", content: _constants__WEBPACK_IMPORTED_MODULE_5__.ALGO_INPUTS_DESC.POSITIONAL_INPUTS }),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { id: "positional_input_info" },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_bs__WEBPACK_IMPORTED_MODULE_6__.BsInfoCircle, null))),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_bootstrap__WEBPACK_IMPORTED_MODULE_1__.Table, { className: "inputs-table" },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("thead", null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tr", null,
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null,
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_bs__WEBPACK_IMPORTED_MODULE_6__.BsPlusCircleFill, { className: "success-icon", onClick: addRow })),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, "Name"),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, "Description"),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", { className: "center-align" }, "Required?"),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null, "Default Value"),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("td", null))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("tbody", null, positionalData.length == 0 ? react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_EmptyRow__WEBPACK_IMPORTED_MODULE_7__.EmptyRow, { text: "No inputs specified" }) : Object.entries(positionalData).map(([key, data]) => {
                return react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_InputRow__WEBPACK_IMPORTED_MODULE_8__.InputRow, { row: data, handleRemoveRow: handleRemoveRow, handleDataChange: handleDataChange });
            })))));
};


/***/ }),

/***/ "./lib/constants.js":
/*!**************************!*\
  !*** ./lib/constants.js ***!
  \**************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ALGO_INPUTS: () => (/* binding */ ALGO_INPUTS),
/* harmony export */   ALGO_INPUTS_DESC: () => (/* binding */ ALGO_INPUTS_DESC),
/* harmony export */   ALGO_INPUT_FIELDS: () => (/* binding */ ALGO_INPUT_FIELDS),
/* harmony export */   COLUMN_SPAN: () => (/* binding */ COLUMN_SPAN),
/* harmony export */   JUPYTER_EXT: () => (/* binding */ JUPYTER_EXT)
/* harmony export */ });
/*******************************
 * Jupyter Extension
 *******************************/
const JUPYTER_EXT = {
    EXTENSION_CSS_CLASSNAME: 'jl-ReactAppWidget',
    VIEW_ALGORITHMS_PLUGIN_ID: 'view_algorithms:plugin',
    VIEW_ALGORITHMS_NAME: 'View Algorithms',
    VIEW_ALGORITHMS_OPEN_COMMAND: 'view_algorithms:open',
    REGISTER_ALGORITHM_PLUGIN_ID: 'register_algorithm:plugin',
    REGISTER_ALGORITHM_NAME: 'Register Algorithm',
    REGISTER_ALGORITHM_OPEN_COMMAND: 'register_algorithm:open',
    SUBMIT_JOBS_OPEN_COMMAND: 'jobs_submit:open',
};
/*******************************
 * Algorithms
 *******************************/
const ALGO_INPUTS = {
    CONFIGURATION_INPUTS: 'configuration_inputs',
    FILE_INPUTS: 'file_inputs',
    POSITIONAL_INPUTS: 'positional_inputs'
};
const ALGO_INPUTS_DESC = {
    CONFIGURATION_INPUTS: "Inputs defined here will be written to a json file named 'inputs.json' in \
                            the working directory. It is recommended that config inputs be used to \
                            change the behavior of the algorithm the user runs.",
    FILE_INPUTS: "Inputs defined here will be downloaded and placed in a directory named 'inputs'.",
    POSITIONAL_INPUTS: "Inputs defined here will be used as inputs to the run command defined as \
                           run_command. The order in which the inputs are defined will be preserved \
                           when building the run_command. It is recommended that positional inputs  \
                           be used when users wish to change the behavior of the run command \
                           and not the behavior of the algorithm e.g. adding a verbose flag."
};
const ALGO_INPUT_FIELDS = {
    INPUT_NAME: "inputName",
    INPUT_DEFAULT: "inputDefault",
    INPUT_DESC: "inputDesc",
    IS_REQUIRED: "isRequired",
    INPUT_ID: "inputId"
};
/* The colSpan attribute for td elements in React accepts a
   number -- unlike raw td elements where you could specify colspan=100%  */
const COLUMN_SPAN = 6;


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/launcher */ "webpack/sharing/consume/default/@jupyterlab/launcher");
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./constants */ "./lib/constants.js");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _classes_App__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./classes/App */ "./lib/classes/App.js");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_5__);








// Add 'View Algorithms' and 'Register Algorithms' plugins to the jupyter lab 'Algorithms' menu
const algorithms_menu_plugin = {
    id: 'algorithms-menu',
    autoStart: true,
    requires: [_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2__.IMainMenu],
    activate: (app, mainMenu) => {
        const { commands } = app;
        let algorithmsMenu = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_3__.Menu({ commands });
        algorithmsMenu.id = 'algorithms-menu';
        algorithmsMenu.title.label = 'Algorithms';
        [
            // JUPYTER_EXT.VIEW_ALGORITHMS_OPEN_COMMAND,
            _constants__WEBPACK_IMPORTED_MODULE_6__.JUPYTER_EXT.REGISTER_ALGORITHM_OPEN_COMMAND
        ].forEach(command => {
            algorithmsMenu.addItem({ command });
        });
        mainMenu.addMenu(algorithmsMenu);
    }
};
const algorithm_catalog_plugin = {
    id: _constants__WEBPACK_IMPORTED_MODULE_6__.JUPYTER_EXT.VIEW_ALGORITHMS_PLUGIN_ID,
    autoStart: true,
    optional: [_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_0__.ILauncher, _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4__.ICommandPalette, _jupyterlab_application__WEBPACK_IMPORTED_MODULE_5__.ILayoutRestorer],
    activate: (app, launcher, palette, restorer) => {
        const { commands } = app;
        const command = _constants__WEBPACK_IMPORTED_MODULE_6__.JUPYTER_EXT.VIEW_ALGORITHMS_OPEN_COMMAND;
        let algorithmCatalogWidget = null;
        const algorithmCatalogTracker = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4__.WidgetTracker({
            namespace: 'view-algorithms-tracker'
        });
        if (restorer) {
            restorer.restore(algorithmCatalogTracker, {
                command: _constants__WEBPACK_IMPORTED_MODULE_6__.JUPYTER_EXT.VIEW_ALGORITHMS_OPEN_COMMAND,
                name: () => 'view-algorithms-tracker'
            });
        }
        commands.addCommand(command, {
            caption: _constants__WEBPACK_IMPORTED_MODULE_6__.JUPYTER_EXT.VIEW_ALGORITHMS_NAME,
            label: _constants__WEBPACK_IMPORTED_MODULE_6__.JUPYTER_EXT.VIEW_ALGORITHMS_NAME,
            icon: (args) => (args['isPalette'] ? null : _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.treeViewIcon),
            execute: () => {
                const content = new _classes_App__WEBPACK_IMPORTED_MODULE_7__.AlgorithmCatalogWidget(app);
                algorithmCatalogWidget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4__.MainAreaWidget({ content });
                algorithmCatalogWidget.title.label = _constants__WEBPACK_IMPORTED_MODULE_6__.JUPYTER_EXT.VIEW_ALGORITHMS_NAME;
                algorithmCatalogWidget.title.icon = _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.treeViewIcon;
                app.shell.add(algorithmCatalogWidget, 'main');
                // Add widget to the tracker so it will persist on browser refresh
                algorithmCatalogTracker.save(algorithmCatalogWidget);
                algorithmCatalogTracker.add(algorithmCatalogWidget);
            },
        });
        const category = 'MAAP Extensions';
        // if (launcher) {
        //   launcher.add({
        //     command,
        //     category: category
        //   });
        // }
        console.log('JupyterLab MAAP Algorithms Registration extension is activated!');
    }
};
const algorithm_registration_plugin = {
    id: _constants__WEBPACK_IMPORTED_MODULE_6__.JUPYTER_EXT.REGISTER_ALGORITHM_PLUGIN_ID,
    autoStart: true,
    optional: [_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_0__.ILauncher, _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4__.ICommandPalette, _jupyterlab_application__WEBPACK_IMPORTED_MODULE_5__.ILayoutRestorer],
    activate: (app, launcher, palette, restorer) => {
        const { commands } = app;
        const command = _constants__WEBPACK_IMPORTED_MODULE_6__.JUPYTER_EXT.REGISTER_ALGORITHM_OPEN_COMMAND;
        let registerAlgorithmsWidget = null;
        const registerAlgorithmsTracker = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4__.WidgetTracker({
            namespace: 'register-algorithms-tracker'
        });
        if (restorer) {
            restorer.restore(registerAlgorithmsTracker, {
                command: _constants__WEBPACK_IMPORTED_MODULE_6__.JUPYTER_EXT.REGISTER_ALGORITHM_OPEN_COMMAND,
                name: () => 'register-algorithms-tracker'
            });
        }
        commands.addCommand(command, {
            caption: _constants__WEBPACK_IMPORTED_MODULE_6__.JUPYTER_EXT.REGISTER_ALGORITHM_NAME,
            label: _constants__WEBPACK_IMPORTED_MODULE_6__.JUPYTER_EXT.REGISTER_ALGORITHM_NAME,
            icon: (args) => (args['isPalette'] ? null : _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.treeViewIcon),
            execute: (data) => {
                console.log("Data coming in: ");
                console.log(data);
                const content = new _classes_App__WEBPACK_IMPORTED_MODULE_7__.RegisterAlgorithmsWidget(data);
                registerAlgorithmsWidget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4__.MainAreaWidget({ content });
                registerAlgorithmsWidget.title.label = _constants__WEBPACK_IMPORTED_MODULE_6__.JUPYTER_EXT.REGISTER_ALGORITHM_NAME;
                registerAlgorithmsWidget.title.icon = _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.treeViewIcon;
                app.shell.add(registerAlgorithmsWidget, 'main');
                // Add widget to the tracker so it will persist on browser refresh
                registerAlgorithmsTracker.save(registerAlgorithmsWidget);
                registerAlgorithmsTracker.add(registerAlgorithmsWidget);
            },
        });
        if (launcher) {
            launcher.add({
                command,
                category: "MAAP Extensions"
            });
        }
        const category = 'MAAP Extensions';
        palette.addItem({ command: _constants__WEBPACK_IMPORTED_MODULE_6__.JUPYTER_EXT.REGISTER_ALGORITHM_OPEN_COMMAND, category });
        console.log('JupyterLab register-algorithm plugin is activated!');
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ([algorithms_menu_plugin, algorithm_catalog_plugin, algorithm_registration_plugin]);


/***/ }),

/***/ "./lib/redux/slices/algorithmSlice.js":
/*!********************************************!*\
  !*** ./lib/redux/slices/algorithmSlice.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   algorithmActions: () => (/* binding */ algorithmActions),
/* harmony export */   algorithmSlice: () => (/* binding */ algorithmSlice),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   selectAlgorithm: () => (/* binding */ selectAlgorithm)
/* harmony export */ });
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @reduxjs/toolkit */ "webpack/sharing/consume/default/@reduxjs/toolkit/@reduxjs/toolkit");
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__);

const initialState = {
    positionalData: [],
    configData: [],
    fileData: [],
    repoUrl: "",
    repoBranch: "",
    repoRunCommand: "",
    repoBuildCommand: "",
    algoName: "",
    algoDesc: "",
    algoDiskSpace: "",
    algoResource: "",
    algoContainer: "",
    inputId: 0,
    registrationUrl: ""
};
const algorithmSlice = (0,_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__.createSlice)({
    name: 'Algorithm',
    initialState,
    reducers: {
        resetValue: () => initialState,
        setRegistrationUrl: (state, action) => {
            state.registrationUrl = action.payload;
        },
        incrementInputId: (state) => {
            state.inputId = state.inputId + 1;
        },
        setRepoUrl: (state, action) => {
            state.repoUrl = action.payload;
        },
        setRepoBranch: (state, action) => {
            state.repoBranch = action.payload;
        },
        setRepoRunCommand: (state, action) => {
            state.repoRunCommand = action.payload;
        },
        setRepoBuildCommand: (state, action) => {
            state.repoBuildCommand = action.payload;
        },
        setAlgoName: (state, action) => {
            state.algoName = action.payload;
        },
        setAlgoDesc: (state, action) => {
            state.algoDesc = action.payload;
        },
        setAlgoDiskSpace: (state, action) => {
            state.algoDiskSpace = action.payload;
        },
        setAlgoResource: (state, action) => {
            state.algoResource = action.payload;
        },
        setAlgoContainerURL: (state, action) => {
            state.algoContainer = action.payload;
        },
        addConfigData: (state, action) => {
            state.configData = [...state.configData, action.payload];
        },
        updateConfigData: (state, action) => {
            return {
                ...state,
                configData: state.configData.map(item => item.inputId == action.payload.inputId ? {
                    ...item,
                    [action.payload.inputField]: action.payload.inputValue
                } : item)
            };
        },
        removeConfigData: (state, action) => {
            let nextState = [...state.configData];
            nextState.map((item, index) => {
                if (item.inputId == action.payload.key) {
                    nextState.splice(index, 1);
                }
            });
            return {
                ...state,
                configData: nextState
            };
        },
        addFileData: (state, action) => {
            state.fileData = [...state.fileData, action.payload];
        },
        updateFileData: (state, action) => {
            return {
                ...state,
                fileData: state.fileData.map(item => item.inputId == action.payload.inputId ? {
                    ...item,
                    [action.payload.inputField]: action.payload.inputValue
                } : item)
            };
        },
        removeFileData: (state, action) => {
            let nextState = [...state.fileData];
            nextState.map((item, index) => {
                if (item.inputId == action.payload.key) {
                    nextState.splice(index, 1);
                }
            });
            return {
                ...state,
                fileData: nextState
            };
        },
        addPositionalData: (state, action) => {
            state.positionalData = [...state.positionalData, action.payload];
        },
        updatePositionalData: (state, action) => {
            return {
                ...state,
                positionalData: state.positionalData.map(item => item.inputId == action.payload.inputId ? {
                    ...item,
                    [action.payload.inputField]: action.payload.inputValue
                } : item)
            };
        },
        removePositionalData: (state, action) => {
            let nextState = [...state.positionalData];
            nextState.map((item, index) => {
                if (item.inputId == action.payload.key) {
                    nextState.splice(index, 1);
                }
            });
            return {
                ...state,
                positionalData: nextState
            };
        },
    },
});
// Actions
const algorithmActions = algorithmSlice.actions;
// Selector
const selectAlgorithm = (state) => state.Algorithm;
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (algorithmSlice.reducer);


/***/ }),

/***/ "./lib/redux/slices/registeredAlgorithms.js":
/*!**************************************************!*\
  !*** ./lib/redux/slices/registeredAlgorithms.js ***!
  \**************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   registeredAlgorithmsActions: () => (/* binding */ registeredAlgorithmsActions),
/* harmony export */   registeredAlgorithmsSlice: () => (/* binding */ registeredAlgorithmsSlice),
/* harmony export */   selectRegisteredAlgorithms: () => (/* binding */ selectRegisteredAlgorithms)
/* harmony export */ });
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @reduxjs/toolkit */ "webpack/sharing/consume/default/@reduxjs/toolkit/@reduxjs/toolkit");
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__);

const initialState = {
    algorithmsList: [],
    algorithmsData: [],
    selectedAlgorithm: { id: "", description: "", inputs: [] }
};
const registeredAlgorithmsSlice = (0,_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__.createSlice)({
    name: 'RegisteredAlgorithms',
    initialState,
    reducers: {
        resetValue: () => initialState,
        setAlgorithmsList: (state, action) => {
            state.algorithmsList = action.payload;
        },
        setAlgorithmsData: (state, action) => {
            state.algorithmsData = action.payload;
        },
        setSelectedAlgorithm: (state, action) => {
            state.selectedAlgorithm = action.payload;
            console.log(state.selectedAlgorithm);
        },
    },
});
// Actions
const registeredAlgorithmsActions = registeredAlgorithmsSlice.actions;
// Selector
const selectRegisteredAlgorithms = (state) => state.RegisteredAlgorithms;
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (registeredAlgorithmsSlice.reducer);


/***/ }),

/***/ "./lib/redux/slices/splitPaneSlice.js":
/*!********************************************!*\
  !*** ./lib/redux/slices/splitPaneSlice.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   selectSplitPane: () => (/* binding */ selectSplitPane),
/* harmony export */   splitPaneActions: () => (/* binding */ splitPaneActions),
/* harmony export */   splitPaneSlice: () => (/* binding */ splitPaneSlice)
/* harmony export */ });
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @reduxjs/toolkit */ "webpack/sharing/consume/default/@reduxjs/toolkit/@reduxjs/toolkit");
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__);

const initialState = {
    rowCount: 10
};
const splitPaneSlice = (0,_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__.createSlice)({
    name: 'SplitPane',
    initialState,
    reducers: {
        resetValue: () => initialState,
        updateSize: (state, action) => {
            state.rowCount = action.payload;
        },
    },
});
// Actions
const splitPaneActions = splitPaneSlice.actions;
// Selector
const selectSplitPane = (state) => state.SplitPane;
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (splitPaneSlice.reducer);


/***/ }),

/***/ "./lib/redux/store.js":
/*!****************************!*\
  !*** ./lib/redux/store.js ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   store: () => (/* binding */ store)
/* harmony export */ });
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @reduxjs/toolkit */ "webpack/sharing/consume/default/@reduxjs/toolkit/@reduxjs/toolkit");
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _slices_algorithmSlice__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./slices/algorithmSlice */ "./lib/redux/slices/algorithmSlice.js");
/* harmony import */ var _slices_registeredAlgorithms__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./slices/registeredAlgorithms */ "./lib/redux/slices/registeredAlgorithms.js");
/* harmony import */ var _slices_splitPaneSlice__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./slices/splitPaneSlice */ "./lib/redux/slices/splitPaneSlice.js");




const store = (0,_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__.configureStore)({
    reducer: {
        Algorithm: _slices_algorithmSlice__WEBPACK_IMPORTED_MODULE_1__["default"],
        RegisteredAlgorithms: _slices_registeredAlgorithms__WEBPACK_IMPORTED_MODULE_2__["default"],
        SplitPane: _slices_splitPaneSlice__WEBPACK_IMPORTED_MODULE_3__["default"]
    },
    devTools: true,
});


/***/ }),

/***/ "./lib/templates/algorithm_config.js":
/*!*******************************************!*\
  !*** ./lib/templates/algorithm_config.js ***!
  \*******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   algorithm_config_template: () => (/* binding */ algorithm_config_template)
/* harmony export */ });
const algorithm_config_template = `
  algorithm_name: algorithm-name
  algorithm_version: 0.1.0
  repository_url: https://github.com/
  docker_container_url: url
  algorithm_description: "Description of algorithm."
  run_command: run.sh
  build_command: build.sh
  disk_space: 50GB
  queue: queue
  inputs:
    file:
      - name: benthic_reflectance_dataset
        required: True
      - name: depth_dataset
        required: True
    config:
      - name: crid
        default: "000"
    positional:
      - name: crid
        default: "000"
`;


/***/ }),

/***/ "./lib/utils/algoConfig.js":
/*!*********************************!*\
  !*** ./lib/utils/algoConfig.js ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   registerAlgorithm: () => (/* binding */ registerAlgorithm)
/* harmony export */ });
/* harmony import */ var _redux_store__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../redux/store */ "./lib/redux/store.js");
/* harmony import */ var js_yaml__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! js-yaml */ "webpack/sharing/consume/default/js-yaml/js-yaml");
/* harmony import */ var js_yaml__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(js_yaml__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _templates_algorithm_config__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../templates/algorithm_config */ "./lib/templates/algorithm_config.js");
/* harmony import */ var _api__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./api */ "./lib/utils/api.js");
/* harmony import */ var _redux_slices_algorithmSlice__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../redux/slices/algorithmSlice */ "./lib/redux/slices/algorithmSlice.js");





async function registerAlgorithm() {
    const state = _redux_store__WEBPACK_IMPORTED_MODULE_1__.store.getState();
    const storeData = state.Algorithm;
    // Populate algorithm config yaml template with data pulled from store
    let data = js_yaml__WEBPACK_IMPORTED_MODULE_0___default().load(_templates_algorithm_config__WEBPACK_IMPORTED_MODULE_2__.algorithm_config_template);
    data.algorithm_description = storeData.algoDesc;
    data.algorithm_name = storeData.algoName;
    data.algorithm_version = storeData.repoBranch;
    data.disk_space = storeData.algoDiskSpace + "GB"; // maap-py request expects units in value string
    data.docker_container_url = storeData.algoContainer;
    data.repository_url = storeData.repoUrl;
    data.run_command = storeData.repoRunCommand;
    data.build_command = storeData.repoBuildCommand;
    data.queue = storeData.algoResource.value;
    // Collect the file, config, and positional inputs
    data.inputs.file = _parseInputs(storeData.fileData);
    data.inputs.config = _parseInputs(storeData.configData);
    data.inputs.positional = _parseInputs(storeData.positionalData);
    console.log("Algo config:");
    let algo_data = JSON.stringify(data);
    // Pass the algo config file
    let response = await (0,_api__WEBPACK_IMPORTED_MODULE_3__.registerUsingFile)(data.algorithm_name + ".yml", algo_data);
    console.log(response);
    // update state
    _redux_store__WEBPACK_IMPORTED_MODULE_1__.store.dispatch(_redux_slices_algorithmSlice__WEBPACK_IMPORTED_MODULE_4__.algorithmSlice.actions.setRegistrationUrl(response));
    return true;
}
function _parseInputs(inputType) {
    let tmpArr = [];
    inputType.map((input) => {
        let tmpObj = {};
        tmpObj = { name: input.inputName,
            required: input.isRequired,
            default: input.inputDefault,
            description: input.inputDesc };
        tmpArr.push(tmpObj);
    });
    return tmpArr;
}


/***/ }),

/***/ "./lib/utils/api.js":
/*!**************************!*\
  !*** ./lib/utils/api.js ***!
  \**************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   createFile: () => (/* binding */ createFile),
/* harmony export */   describeAlgorithms: () => (/* binding */ describeAlgorithms),
/* harmony export */   describeAllAlgorithms: () => (/* binding */ describeAllAlgorithms),
/* harmony export */   getAlgorithms: () => (/* binding */ getAlgorithms),
/* harmony export */   getResources: () => (/* binding */ getResources),
/* harmony export */   getWorkspaceContainer: () => (/* binding */ getWorkspaceContainer),
/* harmony export */   register: () => (/* binding */ register),
/* harmony export */   registerUsingFile: () => (/* binding */ registerUsingFile),
/* harmony export */   unregisterAlgorithm: () => (/* binding */ unregisterAlgorithm)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _redux_slices_registeredAlgorithms__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../redux/slices/registeredAlgorithms */ "./lib/redux/slices/registeredAlgorithms.js");
/* harmony import */ var _redux_store__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../redux/store */ "./lib/redux/store.js");
/* harmony import */ var _parsers__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./parsers */ "./lib/utils/parsers.js");




// export const getAlgorithmMetadata = (body: any) => {
//   let algorithmMetadata = {
//     description: '',
//     inputs: {}
//   }
//   //algorithmMetadata.description = _parseAlgoDesc(body)
//   algorithmMetadata.inputs = _parseAlgoInputs(body)
//   return algorithmMetadata
// }
async function registerUsingFile(fileName, algo_data) {
    const response_file = await createFile(fileName, algo_data);
    console.log(response_file);
    if (response_file) {
        console.log("submitting register");
        const response_register = await register(response_file.file, null);
        const d = JSON.parse(response_register.response);
        console.log(d);
        console.log(d.message.job_web_url);
        return d.message.job_web_url;
    }
    // // Create algorithm config file first
    // createFile(fileName, algo_data).then((data) => {
    //   register(data.file, null).then((res) => {
    //     console.log("in register res")
    //     let res_obj = JSON.parse(res.response)
    //     console.log(res_obj)
    //     console.log(res_obj.message.job_web_url)
    //     return res_obj.message.job_web_url
    //   })
    // }).finally((res) => {
    //   console.log(res)
    // })
}
async function createFile(fileName, data) {
    var requestUrl = new URL(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getBaseUrl() + 'jupyter-server-extension/createFile');
    console.log(requestUrl.href);
    requestUrl.searchParams.append("fileName", fileName);
    requestUrl.searchParams.append("data", data);
    try {
        const response = await fetch(requestUrl.href, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error('Request failed');
        }
        console.log("resolved");
        const r_data = await response.json();
        return r_data;
    }
    catch (error) {
        console.log("error in new endpoint");
        console.log(error);
    }
}
async function register(file, data) {
    console.log("registering....");
    if (data == null) {
        console.log("register using file");
        var requestUrl = new URL(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getBaseUrl() + 'jupyter-server-extension/registerUsingFile');
        console.log(requestUrl.href);
        requestUrl.searchParams.append("file", file);
        try {
            const response = await fetch(requestUrl.href, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) {
                throw new Error('Request failed');
            }
            console.log("resolved register request");
            const r_data = await response.json();
            return r_data;
        }
        catch (error) {
            console.log("error in new register endpoint");
            console.log(error);
        }
    }
    else {
        console.log("register with data");
    }
    // if (response.status >= 200 && response.status < 400) {
    //     console.log("request went well")
    //     return true
    //   }else{
    //     //let res = response.json()
    //     console.log("something went wrong with request!!!")
    //     return false
    //     //console.log(response.json())
    //   }
}
const filterOptions = (options, inputValue) => {
    const candidate = inputValue.toLowerCase();
    return options.filter(({ label }) => label.toLowerCase().includes(candidate));
};
async function getResources(inputValue, callback) {
    var resources = [];
    var requestUrl = new URL(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getBaseUrl() + 'jupyter-server-extension/getQueues');
    await fetch(requestUrl.href, {
        headers: {
            'Content-Type': 'application/json'
        }
    }).then((response) => response.json())
        .then((data) => {
        data["response"].forEach((item) => {
            let resource = {};
            resource["value"] = item;
            resource["label"] = item;
            resources.push(resource);
        });
        const filtered = filterOptions(resources, inputValue);
        callback(filtered);
        return resources;
    });
    return resources;
}
async function describeAlgorithms(algo_id) {
    var requestUrl = new URL(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getBaseUrl() + 'jupyter-server-extension/describeAlgorithms');
    var body = {};
    requestUrl.searchParams.append("algo_id", algo_id);
    await fetch(requestUrl.href, {
        headers: { 'Content-Type': 'application/json' }
    }).then((response) => response.json())
        .then((data) => {
        console.log("Data before parsing: ");
        console.log(data);
        body = (0,_parsers__WEBPACK_IMPORTED_MODULE_1__.parseAlgorithmData)(data["response"]);
        console.log(data);
        return body;
    });
    return body;
}
async function getAlgorithms() {
    let algorithms_tmp = [];
    let algorithms_list_tmp = [];
    var requestUrl = new URL(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getBaseUrl() + 'jupyter-server-extension/listAlgorithms');
    requestUrl.searchParams.append("visibility", "all");
    await fetch(requestUrl.href, {
        headers: {
            'Content-Type': 'application/json'
        }
    }).then((response) => response.json())
        .then((data) => {
        data["response"]["algorithms"].forEach((item) => {
            // TODO: add async dropdown formatted options to store
            let algorithm = {};
            // algorithm["value"] = item["type"] + ':' + item["version"]
            // algorithm["label"] = item["type"] + ':' + item["version"]
            algorithms_list_tmp.push(item["type"] + ':' + item["version"]);
            // algorithms_tmp.push(algorithm)
        });
        console.log("list from api: ", algorithms_list_tmp);
        _redux_store__WEBPACK_IMPORTED_MODULE_2__.store.dispatch(_redux_slices_registeredAlgorithms__WEBPACK_IMPORTED_MODULE_3__.registeredAlgorithmsActions.setAlgorithmsList(algorithms_list_tmp));
        return algorithms_tmp;
    });
    return algorithms_tmp;
}
async function _describeAllAlgorithms() {
    const fmtAlgorithmsData = [];
    var requestUrl = new URL(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getBaseUrl() + 'jupyter-server-extension/describeAlgorithms');
    // Get list of all registered algorithms
    const algorithms = _redux_store__WEBPACK_IMPORTED_MODULE_2__.store.getState().RegisteredAlgorithms.algorithmsList;
    // Get algorithm data for each of the registered algorithms
    for (const algorithm of algorithms) {
        let algorithmData = { id: "", description: "", inputs: [] };
        try {
            requestUrl.searchParams.append("algo_id", algorithm);
            const response = await fetch(requestUrl.href, { headers: { 'Content-Type': 'application/json' } });
            const data = await response.json();
            console.log("Data from api return");
            console.log(data);
            algorithmData = (0,_parsers__WEBPACK_IMPORTED_MODULE_1__.parseAlgorithmData)(data["response"]);
            console.log(algorithmData);
            fmtAlgorithmsData.push(algorithmData);
        }
        catch (error) {
            console.error(`Error fetching data: ${error}`);
        }
    }
    return fmtAlgorithmsData;
}
async function describeAllAlgorithms() {
    try {
        const allData = await _describeAllAlgorithms();
        console.log('All responses:', allData);
        _redux_store__WEBPACK_IMPORTED_MODULE_2__.store.dispatch(_redux_slices_registeredAlgorithms__WEBPACK_IMPORTED_MODULE_3__.registeredAlgorithmsActions.setAlgorithmsData(allData));
    }
    catch (error) {
        console.error('Error fetching data:', error);
    }
}
async function unregisterAlgorithm(algo_id) {
    var requestUrl = new URL(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getBaseUrl() + 'jupyter-server-extension/unregisterAlgorithm');
    requestUrl.searchParams.append("algo_id", algo_id);
    console.log("unregister algorithm");
    // const response = await fetch(requestUrl.href, {
    //   headers: { 'Content-Type': 'application/json' }
    // })
    // const data = await response.json();
    // return data
    return "";
}
async function getWorkspaceContainer() {
    var requestUrl = new URL(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getBaseUrl() + 'jupyter-server-extension/getWorkspaceContainer');
    console.log(requestUrl.href);
    try {
        const response = await fetch(requestUrl.href, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error('Request failed');
        }
        console.log("resolved");
        const r_data = await response.json();
        console.log(r_data);
        return r_data;
    }
    catch (error) {
        console.log("error in new endpoint");
        console.log(error);
    }
}


/***/ }),

/***/ "./lib/utils/jupyter.js":
/*!******************************!*\
  !*** ./lib/utils/jupyter.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   openJobs: () => (/* binding */ openJobs),
/* harmony export */   openRegistration: () => (/* binding */ openRegistration)
/* harmony export */ });
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../constants */ "./lib/constants.js");

const openRegistration = (jupyterApp, data) => {
    console.log("in open registration");
    console.log(data);
    if (jupyterApp.commands.hasCommand(_constants__WEBPACK_IMPORTED_MODULE_0__.JUPYTER_EXT.REGISTER_ALGORITHM_OPEN_COMMAND)) {
        console.log("opening registration to edit");
        if (data == null) {
            console.log("in null");
            jupyterApp.commands.execute(_constants__WEBPACK_IMPORTED_MODULE_0__.JUPYTER_EXT.REGISTER_ALGORITHM_OPEN_COMMAND, null);
        }
        else {
            console.log("in data");
            jupyterApp.commands.execute(_constants__WEBPACK_IMPORTED_MODULE_0__.JUPYTER_EXT.REGISTER_ALGORITHM_OPEN_COMMAND, data);
        }
    }
};
const openJobs = (jupyterApp, data) => {
    console.log("in open jobs");
    console.log(jupyterApp.commands);
    if (jupyterApp.commands.hasCommand(_constants__WEBPACK_IMPORTED_MODULE_0__.JUPYTER_EXT.SUBMIT_JOBS_OPEN_COMMAND)) {
        console.log("jobs command exists");
        if (data == null) {
            console.log("in null");
            jupyterApp.commands.execute(_constants__WEBPACK_IMPORTED_MODULE_0__.JUPYTER_EXT.SUBMIT_JOBS_OPEN_COMMAND);
        }
        else {
            console.log("in data");
            jupyterApp.commands.execute(_constants__WEBPACK_IMPORTED_MODULE_0__.JUPYTER_EXT.SUBMIT_JOBS_OPEN_COMMAND);
        }
    }
};


/***/ }),

/***/ "./lib/utils/parsers.js":
/*!******************************!*\
  !*** ./lib/utils/parsers.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   parseAlgorithmData: () => (/* binding */ parseAlgorithmData)
/* harmony export */ });
const _parseAlgorithmInputs = (body) => {
    let inputs = [];
    let tmpInputs = body["wps:ProcessOfferings"]["wps:ProcessOffering"]["wps:Process"]["wps:Input"];
    tmpInputs.forEach(tmpInput => {
        let input = { id: "", title: "", maxOccurs: "", minOccurs: "", dataType: "", required: "", defaultValue: "" };
        input.id = tmpInput["ows:Identifier"];
        input.title = tmpInput["ows:Title"];
        input.required = tmpInput["ns:LiteralData"]["ns:Format"]["@default"];
        input.minOccurs = tmpInput["@minOccurs"];
        input.maxOccurs = tmpInput["@maxOccurs"];
        input.defaultValue = tmpInput["ns:LiteralData"]["LiteralDataDomain"]["ows:AnyValue"];
        try {
            input.dataType = tmpInput["ns:LiteralData"]["LiteralDataDomain"]["ows:DataType"]["@ows:reference"];
        }
        catch {
            input.dataType = "";
        }
        inputs.push(input);
    });
    return inputs;
};
const _parseAlgorithmDescription = (body) => {
    let description = body["wps:ProcessOfferings"]["wps:ProcessOffering"]["wps:Process"]["ows:Title"];
    return description;
};
const _parseAlgorithmID = (body) => {
    let id = body["wps:ProcessOfferings"]["wps:ProcessOffering"]["wps:Process"]["ows:Identifier"];
    return id;
};
const parseAlgorithmData = (body) => {
    let algorithmData = { id: "", description: "", inputs: [] };
    body = JSON.parse(body);
    algorithmData.id = _parseAlgorithmID(body);
    algorithmData.description = _parseAlgorithmDescription(body);
    algorithmData.inputs = _parseAlgorithmInputs(body);
    return algorithmData;
};


/***/ }),

/***/ "./lib/utils/utils.js":
/*!****************************!*\
  !*** ./lib/utils/utils.js ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   checkUrlExists: () => (/* binding */ checkUrlExists)
/* harmony export */ });
async function checkUrlExists(url) {
    try {
        const response = await fetch(url, { method: 'HEAD' });
        if (response.ok) {
            console.log(`URL "${url}" exists.`);
            return true;
        }
        else {
            console.log(`URL "${url}" returned status code ${response.status}.`);
        }
    }
    catch (error) {
        console.error('Error checking URL existence:', error);
        return false;
    }
    return false;
}


/***/ }),

/***/ "./style/actionBar.css":
/*!*****************************!*\
  !*** ./style/actionBar.css ***!
  \*****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/styleDomAPI.js */ "./node_modules/style-loader/dist/runtime/styleDomAPI.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/insertBySelector.js */ "./node_modules/style-loader/dist/runtime/insertBySelector.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js */ "./node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/insertStyleElement.js */ "./node_modules/style-loader/dist/runtime/insertStyleElement.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/styleTagTransform.js */ "./node_modules/style-loader/dist/runtime/styleTagTransform.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_actionBar_css__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js!./actionBar.css */ "./node_modules/css-loader/dist/cjs.js!./style/actionBar.css");

      
      
      
      
      
      
      
      
      

var options = {};

options.styleTagTransform = (_node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5___default());
options.setAttributes = (_node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3___default());

      options.insert = _node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2___default().bind(null, "head");
    
options.domAPI = (_node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1___default());
options.insertStyleElement = (_node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4___default());

var update = _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default()(_node_modules_css_loader_dist_cjs_js_actionBar_css__WEBPACK_IMPORTED_MODULE_6__["default"], options);




       /* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_css_loader_dist_cjs_js_actionBar_css__WEBPACK_IMPORTED_MODULE_6__["default"] && _node_modules_css_loader_dist_cjs_js_actionBar_css__WEBPACK_IMPORTED_MODULE_6__["default"].locals ? _node_modules_css_loader_dist_cjs_js_actionBar_css__WEBPACK_IMPORTED_MODULE_6__["default"].locals : undefined);


/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%27-4 -4 8 8%27%3e%3ccircle r=%272%27 fill=%27%23fff%27/%3e%3c/svg%3e":
/*!******************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%27-4 -4 8 8%27%3e%3ccircle r=%272%27 fill=%27%23fff%27/%3e%3c/svg%3e ***!
  \******************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%27-4 -4 8 8%27%3e%3ccircle r=%272%27 fill=%27%23fff%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%27-4 -4 8 8%27%3e%3ccircle r=%273%27 fill=%27%2386b7fe%27/%3e%3c/svg%3e":
/*!*********************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%27-4 -4 8 8%27%3e%3ccircle r=%273%27 fill=%27%2386b7fe%27/%3e%3c/svg%3e ***!
  \*********************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%27-4 -4 8 8%27%3e%3ccircle r=%273%27 fill=%27%2386b7fe%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%27-4 -4 8 8%27%3e%3ccircle r=%273%27 fill=%27%23fff%27/%3e%3c/svg%3e":
/*!******************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%27-4 -4 8 8%27%3e%3ccircle r=%273%27 fill=%27%23fff%27/%3e%3c/svg%3e ***!
  \******************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%27-4 -4 8 8%27%3e%3ccircle r=%273%27 fill=%27%23fff%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%27-4 -4 8 8%27%3e%3ccircle r=%273%27 fill=%27rgba%280, 0, 0, 0.25%29%27/%3e%3c/svg%3e":
/*!***********************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%27-4 -4 8 8%27%3e%3ccircle r=%273%27 fill=%27rgba%280, 0, 0, 0.25%29%27/%3e%3c/svg%3e ***!
  \***********************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%27-4 -4 8 8%27%3e%3ccircle r=%273%27 fill=%27rgba%280, 0, 0, 0.25%29%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%27-4 -4 8 8%27%3e%3ccircle r=%273%27 fill=%27rgba%28255, 255, 255, 0.25%29%27/%3e%3c/svg%3e":
/*!*****************************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%27-4 -4 8 8%27%3e%3ccircle r=%273%27 fill=%27rgba%28255, 255, 255, 0.25%29%27/%3e%3c/svg%3e ***!
  \*****************************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%27-4 -4 8 8%27%3e%3ccircle r=%273%27 fill=%27rgba%28255, 255, 255, 0.25%29%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 12 12%27 width=%2712%27 height=%2712%27 fill=%27none%27 stroke=%27%23dc3545%27%3e%3ccircle cx=%276%27 cy=%276%27 r=%274.5%27/%3e%3cpath stroke-linejoin=%27round%27 d=%27M5.8 3.6h.4L6 6.5z%27/%3e%3ccircle cx=%276%27 cy=%278.2%27 r=%27.6%27 fill=%27%23dc3545%27 stroke=%27none%27/%3e%3c/svg%3e":
/*!*******************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 12 12%27 width=%2712%27 height=%2712%27 fill=%27none%27 stroke=%27%23dc3545%27%3e%3ccircle cx=%276%27 cy=%276%27 r=%274.5%27/%3e%3cpath stroke-linejoin=%27round%27 d=%27M5.8 3.6h.4L6 6.5z%27/%3e%3ccircle cx=%276%27 cy=%278.2%27 r=%27.6%27 fill=%27%23dc3545%27 stroke=%27none%27/%3e%3c/svg%3e ***!
  \*******************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 12 12%27 width=%2712%27 height=%2712%27 fill=%27none%27 stroke=%27%23dc3545%27%3e%3ccircle cx=%276%27 cy=%276%27 r=%274.5%27/%3e%3cpath stroke-linejoin=%27round%27 d=%27M5.8 3.6h.4L6 6.5z%27/%3e%3ccircle cx=%276%27 cy=%278.2%27 r=%27.6%27 fill=%27%23dc3545%27 stroke=%27none%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27%23000%27%3e%3cpath d=%27M.293.293a1 1 0 0 1 1.414 0L8 6.586 14.293.293a1 1 0 1 1 1.414 1.414L9.414 8l6.293 6.293a1 1 0 0 1-1.414 1.414L8 9.414l-6.293 6.293a1 1 0 0 1-1.414-1.414L6.586 8 .293 1.707a1 1 0 0 1 0-1.414z%27/%3e%3c/svg%3e":
/*!**************************************************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27%23000%27%3e%3cpath d=%27M.293.293a1 1 0 0 1 1.414 0L8 6.586 14.293.293a1 1 0 1 1 1.414 1.414L9.414 8l6.293 6.293a1 1 0 0 1-1.414 1.414L8 9.414l-6.293 6.293a1 1 0 0 1-1.414-1.414L6.586 8 .293 1.707a1 1 0 0 1 0-1.414z%27/%3e%3c/svg%3e ***!
  \**************************************************************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27%23000%27%3e%3cpath d=%27M.293.293a1 1 0 0 1 1.414 0L8 6.586 14.293.293a1 1 0 1 1 1.414 1.414L9.414 8l6.293 6.293a1 1 0 0 1-1.414 1.414L8 9.414l-6.293 6.293a1 1 0 0 1-1.414-1.414L6.586 8 .293 1.707a1 1 0 0 1 0-1.414z%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27%236ea8fe%27%3e%3cpath fill-rule=%27evenodd%27 d=%27M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z%27/%3e%3c/svg%3e":
/*!****************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27%236ea8fe%27%3e%3cpath fill-rule=%27evenodd%27 d=%27M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z%27/%3e%3c/svg%3e ***!
  \****************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27%236ea8fe%27%3e%3cpath fill-rule=%27evenodd%27 d=%27M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27%23fff%27%3e%3cpath d=%27M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z%27/%3e%3c/svg%3e":
/*!************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27%23fff%27%3e%3cpath d=%27M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z%27/%3e%3c/svg%3e ***!
  \************************************************************************************************************************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27%23fff%27%3e%3cpath d=%27M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27%23fff%27%3e%3cpath d=%27M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z%27/%3e%3c/svg%3e":
/*!*************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27%23fff%27%3e%3cpath d=%27M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z%27/%3e%3c/svg%3e ***!
  \*************************************************************************************************************************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27%23fff%27%3e%3cpath d=%27M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27none%27 stroke=%27%23052c65%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3e%3cpath d=%27M2 5L8 11L14 5%27/%3e%3c/svg%3e":
/*!*********************************************************************************************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27none%27 stroke=%27%23052c65%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3e%3cpath d=%27M2 5L8 11L14 5%27/%3e%3c/svg%3e ***!
  \*********************************************************************************************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27none%27 stroke=%27%23052c65%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3e%3cpath d=%27M2 5L8 11L14 5%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27none%27 stroke=%27%23212529%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3e%3cpath d=%27M2 5L8 11L14 5%27/%3e%3c/svg%3e":
/*!*********************************************************************************************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27none%27 stroke=%27%23212529%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3e%3cpath d=%27M2 5L8 11L14 5%27/%3e%3c/svg%3e ***!
  \*********************************************************************************************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27 fill=%27none%27 stroke=%27%23212529%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3e%3cpath d=%27M2 5L8 11L14 5%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27%3e%3cpath fill=%27none%27 stroke=%27%23343a40%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%272%27 d=%27m2 5 6 6 6-6%27/%3e%3c/svg%3e":
/*!****************************************************************************************************************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27%3e%3cpath fill=%27none%27 stroke=%27%23343a40%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%272%27 d=%27m2 5 6 6 6-6%27/%3e%3c/svg%3e ***!
  \****************************************************************************************************************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27%3e%3cpath fill=%27none%27 stroke=%27%23343a40%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%272%27 d=%27m2 5 6 6 6-6%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27%3e%3cpath fill=%27none%27 stroke=%27%23dee2e6%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%272%27 d=%27m2 5 6 6 6-6%27/%3e%3c/svg%3e":
/*!****************************************************************************************************************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27%3e%3cpath fill=%27none%27 stroke=%27%23dee2e6%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%272%27 d=%27m2 5 6 6 6-6%27/%3e%3c/svg%3e ***!
  \****************************************************************************************************************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27%3e%3cpath fill=%27none%27 stroke=%27%23dee2e6%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%272%27 d=%27m2 5 6 6 6-6%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 20 20%27%3e%3cpath fill=%27none%27 stroke=%27%23fff%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%273%27 d=%27M6 10h8%27/%3e%3c/svg%3e":
/*!********************************************************************************************************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 20 20%27%3e%3cpath fill=%27none%27 stroke=%27%23fff%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%273%27 d=%27M6 10h8%27/%3e%3c/svg%3e ***!
  \********************************************************************************************************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 20 20%27%3e%3cpath fill=%27none%27 stroke=%27%23fff%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%273%27 d=%27M6 10h8%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 20 20%27%3e%3cpath fill=%27none%27 stroke=%27%23fff%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%273%27 d=%27m6 10 3 3 6-6%27/%3e%3c/svg%3e":
/*!**************************************************************************************************************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 20 20%27%3e%3cpath fill=%27none%27 stroke=%27%23fff%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%273%27 d=%27m6 10 3 3 6-6%27/%3e%3c/svg%3e ***!
  \**************************************************************************************************************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 20 20%27%3e%3cpath fill=%27none%27 stroke=%27%23fff%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%273%27 d=%27m6 10 3 3 6-6%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 30 30%27%3e%3cpath stroke=%27rgba%28255, 255, 255, 0.55%29%27 stroke-linecap=%27round%27 stroke-miterlimit=%2710%27 stroke-width=%272%27 d=%27M4 7h22M4 15h22M4 23h22%27/%3e%3c/svg%3e":
/*!******************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 30 30%27%3e%3cpath stroke=%27rgba%28255, 255, 255, 0.55%29%27 stroke-linecap=%27round%27 stroke-miterlimit=%2710%27 stroke-width=%272%27 d=%27M4 7h22M4 15h22M4 23h22%27/%3e%3c/svg%3e ***!
  \******************************************************************************************************************************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 30 30%27%3e%3cpath stroke=%27rgba%28255, 255, 255, 0.55%29%27 stroke-linecap=%27round%27 stroke-miterlimit=%2710%27 stroke-width=%272%27 d=%27M4 7h22M4 15h22M4 23h22%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 30 30%27%3e%3cpath stroke=%27rgba%2833, 37, 41, 0.75%29%27 stroke-linecap=%27round%27 stroke-miterlimit=%2710%27 stroke-width=%272%27 d=%27M4 7h22M4 15h22M4 23h22%27/%3e%3c/svg%3e":
/*!***************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 30 30%27%3e%3cpath stroke=%27rgba%2833, 37, 41, 0.75%29%27 stroke-linecap=%27round%27 stroke-miterlimit=%2710%27 stroke-width=%272%27 d=%27M4 7h22M4 15h22M4 23h22%27/%3e%3c/svg%3e ***!
  \***************************************************************************************************************************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 30 30%27%3e%3cpath stroke=%27rgba%2833, 37, 41, 0.75%29%27 stroke-linecap=%27round%27 stroke-miterlimit=%2710%27 stroke-width=%272%27 d=%27M4 7h22M4 15h22M4 23h22%27/%3e%3c/svg%3e";

/***/ }),

/***/ "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 8 8%27%3e%3cpath fill=%27%23198754%27 d=%27M2.3 6.73.6 4.53c-.4-1.04.46-1.4 1.1-.8l1.1 1.4 3.4-3.8c.6-.63 1.6-.27 1.2.7l-4 4.6c-.43.5-.8.4-1.1.1z%27/%3e%3c/svg%3e":
/*!**********************************************************************************************************************************************************************************************************************************************************!*\
  !*** data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 8 8%27%3e%3cpath fill=%27%23198754%27 d=%27M2.3 6.73.6 4.53c-.4-1.04.46-1.4 1.1-.8l1.1 1.4 3.4-3.8c.6-.63 1.6-.27 1.2.7l-4 4.6c-.43.5-.8.4-1.1.1z%27/%3e%3c/svg%3e ***!
  \**********************************************************************************************************************************************************************************************************************************************************/
/***/ ((module) => {

module.exports = "data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 8 8%27%3e%3cpath fill=%27%23198754%27 d=%27M2.3 6.73.6 4.53c-.4-1.04.46-1.4 1.1-.8l1.1 1.4 3.4-3.8c.6-.63 1.6-.27 1.2.7l-4 4.6c-.43.5-.8.4-1.1.1z%27/%3e%3c/svg%3e";

/***/ })

}]);
//# sourceMappingURL=lib_index_js-data_image_svg_xml_3csvg_xmlns_27http_www_w3_org_2000_svg_27_viewBox_27-4_-4_8_8-ab17c1.9827840698d31b19e730.js.map