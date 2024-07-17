"use strict";
(self["webpackChunkjupyterlab_apibaker"] = self["webpackChunkjupyterlab_apibaker"] || []).push([["lib_index_js"],{

/***/ "./lib/common/copyToClipboard.js":
/*!***************************************!*\
  !*** ./lib/common/copyToClipboard.js ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
const copyToSystem = (clipboardData) => {
    const node = document.body;
    const handler = (event) => {
        const data = event.clipboardData || window.clipboardData;
        data.setData('text', clipboardData);
        event.preventDefault();
        node.removeEventListener('copy', handler);
    };
    node.addEventListener('copy', handler);
    generateEvent(node);
};
/**
 * Generate a clipboard event on a node.
 *
 * @param node - The element on which to generate the event.
 *
 * @param type - The type of event to generate.
 *   `'paste'` events cannot be programmatically generated.
 *
 * #### Notes
 * This can only be called in response to a user input event.
 */
function generateEvent(node, type = 'copy') {
    // http://stackoverflow.com/a/5210367
    // Identify selected text.
    let sel = window.getSelection();
    // Save the current selection.
    const savedRanges = [];
    for (let i = 0, len = (sel === null || sel === void 0 ? void 0 : sel.rangeCount) || 0; i < len; ++i) {
        savedRanges[i] = sel.getRangeAt(i).cloneRange();
    }
    // Select the node content.
    const range = document.createRange();
    range.selectNodeContents(node);
    if (sel) {
        sel.removeAllRanges();
        sel.addRange(range);
    }
    // Execute the command.
    document.execCommand(type);
    // Restore the previous selection.
    sel = window.getSelection();
    if (sel) {
        sel.removeAllRanges();
        for (let i = 0, len = savedRanges.length; i < len; ++i) {
            sel.addRange(savedRanges[i]);
        }
    }
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (copyToSystem);


/***/ }),

/***/ "./lib/common/requestAPI.js":
/*!**********************************!*\
  !*** ./lib/common/requestAPI.js ***!
  \**********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = "", init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, "jupyterlab-apibaker", // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log("Not a JSON response body.", response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/common/utils.js":
/*!*****************************!*\
  !*** ./lib/common/utils.js ***!
  \*****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   extRemoverCorrector: () => (/* binding */ extRemoverCorrector)
/* harmony export */ });
function extRemoverCorrector(stringToBeCorrected) {
    return stringToBeCorrected.replace(/\.[^/.]+$/, "").replace(/[ ._]/g, "-");
}
;


/***/ }),

/***/ "./lib/components/APICardComponent.js":
/*!********************************************!*\
  !*** ./lib/components/APICardComponent.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _EndpointDetailsDialogWithTabsComponent__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./EndpointDetailsDialogWithTabsComponent */ "./lib/components/EndpointDetailsDialogWithTabsComponent.js");
/* harmony import */ var _EndpointCardMore__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./EndpointCardMore */ "./lib/components/EndpointCardMore.js");
/* harmony import */ var _contexts_EndpointContext__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../contexts/EndpointContext */ "./lib/contexts/EndpointContext.js");





const APICardComponent = (props) => {
    const { setCurrentEndpoint } = (0,_contexts_EndpointContext__WEBPACK_IMPORTED_MODULE_2__.useCurrentEndopintContext)();
    const [open, setOpen] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(false);
    const handleClickOpen = () => {
        setCurrentEndpoint(props.endp);
        setOpen(true);
    };
    const handleClose = () => {
        setOpen(false);
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CssBaseline, null),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Card, { key: props.endp.id, variant: "outlined", sx: { width: 450, height: 200 } },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CardHeader, { action: react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_EndpointCardMore__WEBPACK_IMPORTED_MODULE_3__["default"], { endp: props.endp, getEndpoints: props.getEndpoints }), title: props.endp.notebookName, subheader: props.endp.functionName }),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CardContent, null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Stack, { direction: "row", justifyContent: "space-between", alignItems: "center" }),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "body2", color: "text.secondary", noWrap: true, paragraph: true }, props.endp.description)),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CardActions, { disableSpacing: true },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Button, { size: "small", onClick: handleClickOpen }, "Open"),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_EndpointDetailsDialogWithTabsComponent__WEBPACK_IMPORTED_MODULE_4__["default"], { open: open, handleClose: handleClose, endpoint: props.endp, getEndpoints: props.getEndpoints })))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (APICardComponent);


/***/ }),

/***/ "./lib/components/APICatalogComponent.js":
/*!***********************************************!*\
  !*** ./lib/components/APICatalogComponent.js ***!
  \***********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   APICatalogComponent: () => (/* binding */ APICatalogComponent),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material_CssBaseline__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @mui/material/CssBaseline */ "./node_modules/@mui/material/CssBaseline/CssBaseline.js");
/* harmony import */ var _mui_material_Toolbar__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @mui/material/Toolbar */ "./node_modules/@mui/material/Toolbar/Toolbar.js");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mui_material_Grid__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @mui/material/Grid */ "./node_modules/@mui/material/Grid/Grid.js");
/* harmony import */ var _mui_material_Box__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @mui/material/Box */ "./node_modules/@mui/material/Box/Box.js");
/* harmony import */ var _APICardComponent__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./APICardComponent */ "./lib/components/APICardComponent.js");
/* harmony import */ var _contexts_EndpointsContext__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../contexts/EndpointsContext */ "./lib/contexts/EndpointsContext.js");








const APICatalogComponent = () => {
    const { endpoints, getEndpoints } = react__WEBPACK_IMPORTED_MODULE_0___default().useContext(_contexts_EndpointsContext__WEBPACK_IMPORTED_MODULE_2__.EndpointContext);
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_Box__WEBPACK_IMPORTED_MODULE_3__["default"], { display: 'flex', justifyContent: 'center', alignItems: 'flex-start', height: '100%', width: '100%' },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_CssBaseline__WEBPACK_IMPORTED_MODULE_4__["default"], null),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.AppBar, { position: "fixed" },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_Toolbar__WEBPACK_IMPORTED_MODULE_5__["default"], null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "h6", noWrap: true, component: "div" }, "API Collection"))),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_Grid__WEBPACK_IMPORTED_MODULE_6__["default"], { container: true, spacing: 2, sx: {
                paddingLeft: '20px',
                paddingRight: '20px',
                paddingTop: '20px',
                overflow: 'auto',
                maxHeight: '100%',
                marginTop: '50px',
                justifyContent: 'flex-start',
                alignItems: "flex-start"
            } },
            endpoints.length === 0 ? (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_Box__WEBPACK_IMPORTED_MODULE_3__["default"], { width: '100%', display: "flex", flexDirection: 'column', alignItems: "center", alignSelf: 'center', justifyContent: 'center', marginTop: 10 },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: 'h5' }, "There are no endpoints to show"),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: 'body1' }, "You can create one by clicking on the \"Bake API\" button on any of your notebook's toolbar.")))) : '',
            endpoints.map((item) => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_Grid__WEBPACK_IMPORTED_MODULE_6__["default"], { key: item.id, item: true },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_APICardComponent__WEBPACK_IMPORTED_MODULE_7__["default"], { endp: item, getEndpoints: getEndpoints })))))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (APICatalogComponent);


/***/ }),

/***/ "./lib/components/APIKeyInfoComponent.js":
/*!***********************************************!*\
  !*** ./lib/components/APIKeyInfoComponent.js ***!
  \***********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react_icons_md__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! react-icons/md */ "./node_modules/react-icons/md/index.mjs");
/* harmony import */ var _common_copyToClipboard__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../common/copyToClipboard */ "./lib/common/copyToClipboard.js");
/* harmony import */ var react_icons_io5__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react-icons/io5 */ "./node_modules/react-icons/io5/index.mjs");


// import { CssBaseline, Grid, Card, CardHeader, CardContent, CardActions, IconButton, InputLabel, Typography, TextField, InputAdornment, styled, Tooltip, Snackbar, Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';


// import { IAPIKey } from '../common/types';


const APIKeyInfoComponent = (props) => {
    // const [deleteDialogOpen, setDeleteDialogOpen] = React.useState<boolean>(false)
    const [snackbarOpen, setSnackbarOpen] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(false);
    const [apiKeyToCopy, setAPIKeyToCopy] = react__WEBPACK_IMPORTED_MODULE_0___default().useState('');
    react__WEBPACK_IMPORTED_MODULE_0___default().useEffect(() => {
        setAPIKeyToCopy(apiKeyToCopy);
    }, [apiKeyToCopy]);
    const IconButtonWithTooltip = (0,_mui_material__WEBPACK_IMPORTED_MODULE_1__.styled)(_mui_material__WEBPACK_IMPORTED_MODULE_1__.IconButton)({
        root: {
            '&.Mui-disabled': {
                pointerEvents: 'auto',
            },
        },
    });
    const AlignedInputAdornment = (0,_mui_material__WEBPACK_IMPORTED_MODULE_1__.styled)(_mui_material__WEBPACK_IMPORTED_MODULE_1__.InputAdornment)({
        margin: '0 auto', // fix for vertically unaligned icon
    });
    const handleCopyToClipboard = () => {
        try {
            (0,_common_copyToClipboard__WEBPACK_IMPORTED_MODULE_2__["default"])(apiKeyToCopy);
            setSnackbarOpen(true);
        }
        catch (error) {
            console.log(`Error copying to clipboard => ${JSON.stringify(error, null, 2)}`);
        }
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CssBaseline, null),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { item: true, key: props.apk.id, xs: 12 },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Card, null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CardHeader, { title: props.apk.apiKeyName }),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CardContent, null,
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.InputLabel, null,
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: 'subtitle2' }, "API Key")),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TextField, { disabled: true, variant: 'outlined', value: props.apk.apiKey, sx: { width: '100%' }, InputProps: {
                            endAdornment: (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(AlignedInputAdornment, { position: "end" },
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Tooltip, { title: "Copy API Key" },
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(IconButtonWithTooltip, { role: 'button', onClick: handleCopyToClipboard },
                                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_io5__WEBPACK_IMPORTED_MODULE_3__.IoCopyOutline, null))))),
                        } }),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Snackbar, { open: snackbarOpen, onClose: () => setSnackbarOpen(false), autoHideDuration: 2000, message: "Copied to clipboard" }),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: 'body1', marginTop: 1 },
                        " ",
                        props.apk.description),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: 'body1', marginTop: 1 },
                        "Expires: ",
                        props.apk.expiresAt.toString())),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CardActions, null,
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.IconButton, { onClick: (e) => props.handleRefreshClick(e, props.apk.id) },
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_md__WEBPACK_IMPORTED_MODULE_4__.MdAutorenew, null)),
                    props.apk.apiKeyName === 'Default' ?
                        '' :
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.IconButton, { onClick: (e) => props.handleDeleteClick(e, props.apk.id) },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_md__WEBPACK_IMPORTED_MODULE_4__.MdDeleteOutline, null)))))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (APIKeyInfoComponent);


/***/ }),

/***/ "./lib/components/EndpointAPIKeyComponent.js":
/*!***************************************************!*\
  !*** ./lib/components/EndpointAPIKeyComponent.js ***!
  \***************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _APIKeyInfoComponent__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./APIKeyInfoComponent */ "./lib/components/APIKeyInfoComponent.js");
/* harmony import */ var _NewAPIKeyComponent__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./NewAPIKeyComponent */ "./lib/components/NewAPIKeyComponent.js");
/* harmony import */ var _common_requestAPI__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../common/requestAPI */ "./lib/common/requestAPI.js");
/* harmony import */ var _contexts_CommonContext__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../contexts/CommonContext */ "./lib/contexts/CommonContext.js");
/* harmony import */ var _contexts_EndpointContext__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../contexts/EndpointContext */ "./lib/contexts/EndpointContext.js");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__);








const EndpointAPIKeyComponent = (props) => {
    const { currentUser } = react__WEBPACK_IMPORTED_MODULE_0___default().useContext(_contexts_CommonContext__WEBPACK_IMPORTED_MODULE_3__.CommonContext);
    const [apiKeyName, setAPIKeyName] = react__WEBPACK_IMPORTED_MODULE_0___default().useState('');
    const [apiKeyNameError, setAPIKeyNameError] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(false);
    const [apiKeyDescription, setAPIKeyDescription] = react__WEBPACK_IMPORTED_MODULE_0___default().useState('');
    const [apiKeys, setAPIKeys] = react__WEBPACK_IMPORTED_MODULE_0___default().useState();
    const { endpoint } = (0,_contexts_EndpointContext__WEBPACK_IMPORTED_MODULE_4__.useCurrentEndopintContext)();
    react__WEBPACK_IMPORTED_MODULE_0___default().useEffect(() => {
        getAPIKeys();
    }, []);
    const getAPIKeys = async () => {
        const response = await (0,_common_requestAPI__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('api-keys?id=' + encodeURIComponent(props.id) + "&owner=" + encodeURIComponent(currentUser));
        // console.log(`API Keys => ${JSON.stringify(JSON.parse(response.toString()).data, null, 2)}`)          
        console.log(`API Keys => ${JSON.stringify(JSON.parse(response.toString()).data, null, 2)}`);
        setAPIKeys(JSON.parse(response.toString()).data);
    };
    const _handleSubmit = async (event) => {
        event.preventDefault();
        console.log(`Information to be sent => ${apiKeyName} - ${apiKeyDescription}`);
        const newAPIKey = await (0,_common_requestAPI__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('api-keys', {
            method: 'POST',
            body: JSON.stringify({
                current_user: currentUser,
                endpoint_id: props.id,
                name: apiKeyName,
                description: apiKeyDescription
            })
        });
        console.log(`New APIKey => ${JSON.stringify(newAPIKey, null, 2)}`);
        if (newAPIKey.statusCode >= 400) {
            _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.Notification.error(`There has been an error while creating the new API Key: ${apiKeyName}`);
        }
        else {
            _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.Notification.success(`The new API key ${apiKeyName} has been created successfuly`);
        }
        setAPIKeyName('');
        setAPIKeyDescription('');
        getAPIKeys();
    };
    const _handleRefreshClick = async (event, apiKeyId) => {
        event.preventDefault();
        console.log(`API Key ID to refresh => ${apiKeyId}`);
        // Send request to refresh apiKey
        try {
            let refreshApiKey = await (0,_common_requestAPI__WEBPACK_IMPORTED_MODULE_5__.requestAPI)("api-keys/refresh", {
                method: "PUT",
                body: JSON.stringify({
                    endpoint_id: endpoint === null || endpoint === void 0 ? void 0 : endpoint.id,
                    api_key_id: apiKeyId,
                    current_user: encodeURIComponent(currentUser)
                })
            });
            console.log(`Refresh API Key Result => ${JSON.stringify(refreshApiKey, null, 2)}`);
            getAPIKeys();
        }
        catch (error) {
            console.log(`Error => ${JSON.stringify(error, null, 2)}`);
        }
    };
    const _handleDeleteClick = async (event, apiKeyId) => {
        event.preventDefault();
        console.log(`API Key ID to delete => ${apiKeyId}`);
        console.log(endpoint);
        // Send Reqest to delete apiKey
        try {
            let deleteApiKey = await (0,_common_requestAPI__WEBPACK_IMPORTED_MODULE_5__.requestAPI)("api-keys", {
                method: "DELETE",
                body: JSON.stringify({
                    endpoint_id: endpoint === null || endpoint === void 0 ? void 0 : endpoint.id,
                    api_key_id: apiKeyId,
                    current_user: encodeURIComponent(currentUser)
                })
            });
            console.log(`Delete API Key Result => ${JSON.stringify(deleteApiKey, null, 2)}`);
            getAPIKeys();
        }
        catch (error) {
            console.log(`Error => ${JSON.stringify(error, null, 2)}`);
        }
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CssBaseline, null),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_NewAPIKeyComponent__WEBPACK_IMPORTED_MODULE_6__["default"], { endp: props, handleSubmit: _handleSubmit, apiKeyNameError: apiKeyNameError, apiKeyDescription: apiKeyDescription, setAPIKeyDescription: setAPIKeyDescription, apiKeyName: apiKeyName, setAPIKeyName: setAPIKeyName, setAPIKeyNameError: setAPIKeyNameError }),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { container: true, spacing: 2, direction: 'row', width: '100%', marginTop: 3 },
            apiKeys && apiKeys.length > 0 ? (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: 'h6', marginLeft: 2 }, "Current API Keys:")) : '',
            apiKeys ? (apiKeys.map((apiK, idx) => {
                return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_APIKeyInfoComponent__WEBPACK_IMPORTED_MODULE_7__["default"], { apk: apiK, handleRefreshClick: _handleRefreshClick, handleDeleteClick: _handleDeleteClick }));
            })) : '')));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (EndpointAPIKeyComponent);


/***/ }),

/***/ "./lib/components/EndpointCardMore.js":
/*!********************************************!*\
  !*** ./lib/components/EndpointCardMore.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material_Menu__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @mui/material/Menu */ "./node_modules/@mui/material/Menu/Menu.js");
/* harmony import */ var _mui_material_MenuItem__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @mui/material/MenuItem */ "./node_modules/@mui/material/MenuItem/MenuItem.js");
/* harmony import */ var _mui_material_IconButton__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @mui/material/IconButton */ "./node_modules/@mui/material/IconButton/IconButton.js");
/* harmony import */ var react_icons_fi__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! react-icons/fi */ "./node_modules/react-icons/fi/index.mjs");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react_icons_md__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! react-icons/md */ "./node_modules/react-icons/md/index.mjs");
/* harmony import */ var _common_requestAPI__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../common/requestAPI */ "./lib/common/requestAPI.js");
/* harmony import */ var _EndpointDetailsDialogWithTabsComponent__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./EndpointDetailsDialogWithTabsComponent */ "./lib/components/EndpointDetailsDialogWithTabsComponent.js");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_2__);











const EndpointCardMore = (props) => {
    const [anchorEl, setAnchorEl] = react__WEBPACK_IMPORTED_MODULE_0__.useState(null);
    const [deleteDialogOpen, setDeleteDialogOpen] = react__WEBPACK_IMPORTED_MODULE_0__.useState(false);
    const open = Boolean(anchorEl);
    const [openEndpointDetails, setOpenEndpointDetails] = react__WEBPACK_IMPORTED_MODULE_0__.useState(false);
    const handleEndpointDetailsClickOpen = () => {
        setOpenEndpointDetails(!openEndpointDetails);
        setAnchorEl(null);
    };
    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
        setAnchorEl(null);
    };
    const handleDeleteDialogClick = async () => {
        setDeleteDialogOpen(!deleteDialogOpen);
        setAnchorEl(null);
    };
    const handleDeleteEndpoint = async () => {
        try {
            let deleteEndpoint = await (0,_common_requestAPI__WEBPACK_IMPORTED_MODULE_3__.requestAPI)("endpoint", {
                method: "DELETE",
                body: JSON.stringify({
                    endpoint_id: props.endp.id,
                    owner: _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_2__.PageConfig.getOption('serverRoot').split('/')[2] || ""
                })
            });
            console.log(`Delete Endpoint Result => ${JSON.stringify(deleteEndpoint, null, 2)}`);
            props.getEndpoints();
            setDeleteDialogOpen(false);
        }
        catch (error) {
            console.log(`Error => ${JSON.stringify(error, null, 2)}`);
        }
    };
    console.log(`Endpoint Received in More => ${JSON.stringify(props.endp, null, 2)}`);
    return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(react__WEBPACK_IMPORTED_MODULE_0__.Fragment, null,
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CssBaseline, null),
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_IconButton__WEBPACK_IMPORTED_MODULE_4__["default"], { "aria-label": "settings", id: "basic-button", "aria-controls": open ? 'card-more-action-menu' : undefined, "aria-haspopup": "true", "aria-expanded": open ? 'true' : undefined, onClick: handleClick },
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(react_icons_fi__WEBPACK_IMPORTED_MODULE_5__.FiMoreVertical, null)),
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Menu__WEBPACK_IMPORTED_MODULE_6__["default"], { id: "card-more-actions-menu", anchorEl: anchorEl, open: open, onClose: handleClose, MenuListProps: {
                'aria-labelledby': 'card-more-actions-button',
            } },
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_MenuItem__WEBPACK_IMPORTED_MODULE_7__["default"], { onClick: handleEndpointDetailsClickOpen },
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.ListItemIcon, null,
                    react__WEBPACK_IMPORTED_MODULE_0__.createElement(react_icons_md__WEBPACK_IMPORTED_MODULE_8__.MdEdit, null)),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.ListItemText, null, "Edit")),
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_MenuItem__WEBPACK_IMPORTED_MODULE_7__["default"], { onClick: handleDeleteDialogClick },
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.ListItemIcon, null,
                    react__WEBPACK_IMPORTED_MODULE_0__.createElement(react_icons_md__WEBPACK_IMPORTED_MODULE_8__.MdDeleteOutline, null)),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.ListItemText, null, "Delete"))),
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Dialog, { open: deleteDialogOpen, onClose: handleDeleteDialogClick, "aria-labelledby": "delete-endpoint-dialog", "aria-describedby": "delete-dialog-description" },
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.DialogTitle, { id: "delete-endpoint-dialog" }, "Delete endpoint?"),
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.DialogContent, null,
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.DialogContentText, { id: "delete-dialog-description" },
                    "You are about to delete ",
                    react__WEBPACK_IMPORTED_MODULE_0__.createElement("strong", null, props.endp.notebookName),
                    " endpoint and all its versions. ",
                    react__WEBPACK_IMPORTED_MODULE_0__.createElement("strong", null, "This action can't be undone."),
                    " Do you want to continue?")),
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.DialogActions, null,
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Button, { onClick: handleDeleteDialogClick, autoFocus: true }, "No"),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Button, { onClick: handleDeleteEndpoint, color: 'error' }, "Yes"))),
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_EndpointDetailsDialogWithTabsComponent__WEBPACK_IMPORTED_MODULE_9__["default"], { open: openEndpointDetails, handleClose: handleEndpointDetailsClickOpen, endpoint: props.endp, getEndpoints: props.getEndpoints })));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (EndpointCardMore);


/***/ }),

/***/ "./lib/components/EndpointDetailsDialogWithTabsComponent.js":
/*!******************************************************************!*\
  !*** ./lib/components/EndpointDetailsDialogWithTabsComponent.js ***!
  \******************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mui_lab__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/lab */ "webpack/sharing/consume/default/@mui/lab/@mui/lab");
/* harmony import */ var _mui_lab__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_mui_lab__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _EndpointSummaryComponent__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./EndpointSummaryComponent */ "./lib/components/EndpointSummaryComponent.js");
/* harmony import */ var _EndpointAPIKeyComponent__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./EndpointAPIKeyComponent */ "./lib/components/EndpointAPIKeyComponent.js");
/* harmony import */ var _EndpointLogsComponent__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./EndpointLogsComponent */ "./lib/components/EndpointLogsComponent.js");
/* harmony import */ var _common_requestAPI__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../common/requestAPI */ "./lib/common/requestAPI.js");







const EndpointDetailsDialogWithTabs = (props) => {
    const [value, setValue] = react__WEBPACK_IMPORTED_MODULE_0___default().useState('1');
    const [apiBakerDomain, setApiBakerDomain] = react__WEBPACK_IMPORTED_MODULE_0___default().useState('');
    const handleChange = (event, newValue) => {
        setValue(newValue);
    };
    const getSysEnv = async () => {
        const response = await (0,_common_requestAPI__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('env');
        console.log(`API_BAKER_DOMAIN => ${response.data}`);
        setApiBakerDomain(response.data);
        console.log(apiBakerDomain);
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CssBaseline, null),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Dialog, { sx: { '& .MuiDialog-paper': { maxHeight: '70%' } }, onClose: props.handleClose, open: props.open, fullWidth: true, maxWidth: 'lg' },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.DialogTitle, null, "Endpoint Details"),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.DialogContent, { sx: { height: '100vh' } },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Box, { sx: { width: '100%', typography: 'body1' } },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_lab__WEBPACK_IMPORTED_MODULE_2__.TabContext, { value: value },
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Box, { sx: { borderBottom: 1, borderColor: 'divider' } },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_lab__WEBPACK_IMPORTED_MODULE_2__.TabList, { onChange: handleChange, "aria-label": "lab API tabs example", variant: 'fullWidth' },
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Tab, { label: "Summary", value: "1" }),
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Tab, { label: "API Keys", value: "2" }),
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Tab, { label: "Logs", value: "3" }),
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Tab, { label: "Analytics", value: "4" }))),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_lab__WEBPACK_IMPORTED_MODULE_2__.TabPanel, { value: "1" },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_EndpointSummaryComponent__WEBPACK_IMPORTED_MODULE_4__["default"], { endpoint: props.endpoint, getSysEnv: getSysEnv, apiBakerDomain: apiBakerDomain, getEndpoints: props.getEndpoints })),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_lab__WEBPACK_IMPORTED_MODULE_2__.TabPanel, { value: "2" },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_EndpointAPIKeyComponent__WEBPACK_IMPORTED_MODULE_5__["default"], { ...props.endpoint })),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_lab__WEBPACK_IMPORTED_MODULE_2__.TabPanel, { value: "3" },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_EndpointLogsComponent__WEBPACK_IMPORTED_MODULE_6__["default"], { endpoint: props.endpoint }))))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.DialogActions, null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Box, { sx: {
                        display: 'flex',
                        flexDirection: 'row',
                        justifyContent: 'flex-end',
                        alignItems: 'center',
                        alignContent: 'center',
                        width: '100%'
                    } },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Button, { variant: 'text', sx: { mr: 1 } }, "Open notebook"),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Button, { variant: 'text', onClick: props.handleClose }, "Close"))))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (EndpointDetailsDialogWithTabs);


/***/ }),

/***/ "./lib/components/EndpointLogsComponent.js":
/*!*************************************************!*\
  !*** ./lib/components/EndpointLogsComponent.js ***!
  \*************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react_icons_io5__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react-icons/io5 */ "./node_modules/react-icons/io5/index.mjs");
/* harmony import */ var _common_requestAPI__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../common/requestAPI */ "./lib/common/requestAPI.js");


// import { TbLogs } from 'react-icons/tb';


const Transition = react__WEBPACK_IMPORTED_MODULE_0___default().forwardRef(function Transition(props, ref) {
    return react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Slide, { direction: "up", ref: ref, ...props });
});
const EndpointLogs = (props) => {
    const [logs, setLogs] = react__WEBPACK_IMPORTED_MODULE_0___default().useState([]);
    const [open, setOpen] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(false);
    const [contentLog, setContentLog] = react__WEBPACK_IMPORTED_MODULE_0___default().useState('');
    const [workflowName, setWorkflowName] = react__WEBPACK_IMPORTED_MODULE_0___default().useState('');
    const [scroll, setScroll] = react__WEBPACK_IMPORTED_MODULE_0___default().useState('paper');
    const [version, setVersion] = react__WEBPACK_IMPORTED_MODULE_0___default().useState('');
    react__WEBPACK_IMPORTED_MODULE_0___default().useEffect(() => {
        setVersion(`${props.endpoint.versions.length > 0 ? props.endpoint.versions[0].id : ''}`);
        console.log(props.endpoint.versions);
        console.log(version);
        getWorkflows(`${props.endpoint.versions.length > 0 ? props.endpoint.versions[0].id : ''}`);
    }, []);
    const handleVersionChange = (event) => {
        event.preventDefault();
        setVersion(event.target.value);
        getWorkflows(event.target.value);
    };
    const handleClickOpen = (scrollType, workflowName) => () => {
        console.log(`Workflow Name => ${workflowName}`);
        setOpen(true);
        setScroll(scrollType);
        getWorkflowLog(workflowName);
    };
    const handleClose = () => {
        setOpen(false);
    };
    const descriptionElementRef = react__WEBPACK_IMPORTED_MODULE_0___default().useRef(null);
    react__WEBPACK_IMPORTED_MODULE_0___default().useEffect(() => {
        if (open) {
            const { current: descriptionElement } = descriptionElementRef;
            if (descriptionElement !== null) {
                descriptionElement.focus();
            }
        }
    }, [open]);
    const getWorkflows = async (version) => {
        try {
            console.log(props.endpoint);
            // TODO: Add Data type for Workflows and Logs
            let workflows = await (0,_common_requestAPI__WEBPACK_IMPORTED_MODULE_2__.requestAPI)("endpoint/workflows?owner=" + props.endpoint.owner + "&endpointId=" + props.endpoint.id + "&versionId=" + version, {
                method: "GET",
            });
            console.log(`Endpoint Workflows Result => ${JSON.stringify(workflows, null, 2)}`);
            setLogs(workflows);
        }
        catch (error) {
            console.log(`Error => ${JSON.stringify(error, null, 2)}`);
        }
    };
    const getWorkflowLog = async (workflowName) => {
        try {
            console.log('From GetWokrflowLog');
            console.log(`URL => ${"endpoint/workflows/log?owner=" + props.endpoint.owner + "&endpointId=" + props.endpoint.id + "&versionId=" + version + "&workflowName=" + workflowName}`);
            let response = await (0,_common_requestAPI__WEBPACK_IMPORTED_MODULE_2__.requestAPI)("endpoint/workflows/log?owner=" + props.endpoint.owner + "&endpointId=" + props.endpoint.id + "&versionId=" + version + "&workflowName=" + workflowName, {
                method: "GET",
            });
            console.log(`Endpoint Workflow log Result => ${response}`);
            setContentLog(response);
            setWorkflowName(workflowName);
        }
        catch (error) {
            console.log(`Error => ${JSON.stringify(error, null, 2)}`);
        }
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CssBaseline, null),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableContainer, null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Table, { sx: {
                    maxWidth: '100vw', [`& .${_mui_material__WEBPACK_IMPORTED_MODULE_1__.tableCellClasses.root}`]: {
                        borderBottom: "none"
                    }
                }, "aria-label": "endpoint-info" },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableBody, null,
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableRow, null,
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableCell, { align: 'left' },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.InputLabel, { id: "version-select-label" },
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: 'body1', noWrap: true, sx: { fontSize: '20px' } }, "Version:")),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Select, { labelId: "version-select-label", id: "version-select", value: version, onChange: handleVersionChange, sx: { width: 150 } }, (props.endpoint.versions.length > 0) ? (props.endpoint.versions.map((version) => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.MenuItem, { key: version.id, value: version.id }, version.versionName)))) : (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.MenuItem, { key: 0, value: 0 }, "No version")))))))),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CssBaseline, null),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { item: true, key: props.endpoint.id, xs: 12 }, logs.length ? (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.List, { sx: { width: '100%', maxWidth: 360, bgcolor: 'background.paper' } }, logs.map((log, index) => {
            return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.ListItemButton, { key: index, alignItems: "flex-start", onClick: handleClickOpen('paper', log.name) },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.ListItemText, { primary: log.name, secondary: react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { sx: { display: 'inline' }, component: "span", variant: "body2", color: "text.primary" },
                                log.phase,
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("br", null)),
                            "created at: ",
                            log.createdAt,
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("br", null),
                            "started at: ",
                            log.startedAt,
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("br", null),
                            "finished at: ",
                            log.finishedAt) })),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Divider, { variant: "inset", component: "li" })));
        })))
            : react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "subtitle1", gutterBottom: true }, "No logs were found.")),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Dialog, { fullScreen: true, open: open, onClose: handleClose, TransitionComponent: Transition },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.AppBar, { sx: { position: 'relative' } },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Toolbar, null,
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.IconButton, { edge: "start", color: "inherit", onClick: handleClose, "aria-label": "close" },
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_io5__WEBPACK_IMPORTED_MODULE_3__.IoClose, null)),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { sx: { ml: 2, flex: 1 }, variant: "h6", component: "div" }, "LOGS"))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.DialogTitle, { id: "scroll-dialog-title" }, workflowName),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.DialogContent, { dividers: scroll === 'paper' },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.DialogContentText, { id: "scroll-dialog-description", ref: descriptionElementRef, tabIndex: -1 },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "caption", display: "block", gutterBottom: true, style: { whiteSpace: 'pre-wrap', fontFamily: 'monospace' } }, contentLog))))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (EndpointLogs);


/***/ }),

/***/ "./lib/components/EndpointSummaryComponent.js":
/*!****************************************************!*\
  !*** ./lib/components/EndpointSummaryComponent.js ***!
  \****************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react_icons_io5__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! react-icons/io5 */ "./node_modules/react-icons/io5/index.mjs");
/* harmony import */ var _common_copyToClipboard__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../common/copyToClipboard */ "./lib/common/copyToClipboard.js");
/* harmony import */ var react_icons_md__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! react-icons/md */ "./node_modules/react-icons/md/index.mjs");
/* harmony import */ var _common_requestAPI__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../common/requestAPI */ "./lib/common/requestAPI.js");
/* harmony import */ var _contexts_CommonContext__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../contexts/CommonContext */ "./lib/contexts/CommonContext.js");







const EndpointSummary = (props) => {
    const { currentUser } = react__WEBPACK_IMPORTED_MODULE_0___default().useContext(_contexts_CommonContext__WEBPACK_IMPORTED_MODULE_2__.CommonContext);
    const [version, setVersion] = react__WEBPACK_IMPORTED_MODULE_0___default().useState('');
    const [snackbarOpen, setSnackbarOpen] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(false);
    const [endpointURLToCopy, setEndpointURLToCopy] = react__WEBPACK_IMPORTED_MODULE_0___default().useState('');
    const [versionDescription, setVersionDescription] = react__WEBPACK_IMPORTED_MODULE_0___default().useState('');
    const [versions, setVersions] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(props.endpoint.versions);
    // const enpointdVersions = props.endpoint.versions || []
    react__WEBPACK_IMPORTED_MODULE_0___default().useEffect(() => {
        setVersion(`${versions.length > 0 ? versions[0].id : ''}`);
        setVersionDescription(`${versions.length > 0
            ? versions[0].description
            : ''}`);
    }, [props.endpoint.versions]);
    react__WEBPACK_IMPORTED_MODULE_0___default().useEffect(() => {
        props.getSysEnv();
        setEndpointURLToCopy(`${props.apiBakerDomain}/endpoints/${props.endpoint.id}/versions/${version}/submit`);
    }, [props.endpoint.id, version, props.apiBakerDomain]);
    const handleVersionChange = (event) => {
        var _a, _b;
        event.preventDefault();
        console.log(event.target.value);
        setVersion(event.target.value);
        setVersionDescription((_b = (_a = versions.find((v) => v.id === event.target.value)) === null || _a === void 0 ? void 0 : _a.description) !== null && _b !== void 0 ? _b : "");
    };
    const handleCopyToClipboard = () => {
        try {
            (0,_common_copyToClipboard__WEBPACK_IMPORTED_MODULE_3__["default"])(endpointURLToCopy);
            setSnackbarOpen(true);
        }
        catch (error) {
            console.log(`Error copying to clipboard => ${JSON.stringify(error, null, 2)}`);
        }
    };
    const handleDelete = async (event) => {
        try {
            event.stopPropagation();
            const versionId = event.currentTarget.id;
            await (0,_common_requestAPI__WEBPACK_IMPORTED_MODULE_4__.requestAPI)("version", {
                method: "DELETE",
                body: JSON.stringify({
                    current_user: currentUser,
                    endpoint_id: props.endpoint.id,
                    version_id: versionId,
                })
            });
            props.getEndpoints();
            const response = await (0,_common_requestAPI__WEBPACK_IMPORTED_MODULE_4__.requestAPI)("endpoint?owner=" + props.endpoint.owner, {
                method: "GET",
            });
            const responseObj = JSON.parse(response.toString());
            const endpoints = responseObj.data;
            const endpoint = endpoints.find((endpoint) => endpoint.id === props.endpoint.id);
            setVersions(endpoint ? endpoint.versions : []);
        }
        catch (error) {
            console.log(`Error copying to clipboard => ${JSON.stringify(error, null, 2)}`);
        }
    };
    function DeleteButton({ isSelected, versionId }) {
        if (isSelected) {
            return react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_md__WEBPACK_IMPORTED_MODULE_5__.MdDeleteOutline, { id: versionId, fontSize: "large", onClick: handleDelete });
        }
        return null;
    }
    const IconButtonWithTooltip = (0,_mui_material__WEBPACK_IMPORTED_MODULE_1__.styled)(_mui_material__WEBPACK_IMPORTED_MODULE_1__.IconButton)({
        root: {
            '&.Mui-disabled': {
                pointerEvents: 'auto',
            },
        },
    });
    const AlignedInputAdornment = (0,_mui_material__WEBPACK_IMPORTED_MODULE_1__.styled)(_mui_material__WEBPACK_IMPORTED_MODULE_1__.InputAdornment)({
        margin: '0 auto', // fix for vertically unaligned icon
    });
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CssBaseline, null),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableContainer, null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Table, { sx: {
                    maxWidth: '100vw', [`& .${_mui_material__WEBPACK_IMPORTED_MODULE_1__.tableCellClasses.root}`]: {
                        borderBottom: "none"
                    }
                }, "aria-label": "endpoint-info" },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableBody, null,
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableRow, null,
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableCell, { align: "left" },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "body1", noWrap: true, sx: {
                                    fontSize: '20px'
                                } }, "Notebook name:")),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableCell, { align: "right", colSpan: 2 },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "body2", noWrap: true, sx: { fontSize: '17px' } }, props.endpoint.notebookName))),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableRow, { sx: { '&:last-child td, &:last-child th': { border: 0 } } },
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableCell, { align: "left" },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "body1", noWrap: true, sx: { fontSize: '20px' } }, "Function name:")),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableCell, { align: "right", colSpan: 2 },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "body2", noWrap: true, sx: { fontSize: '17px' } }, props.endpoint.functionName))),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableRow, { sx: { '&:last-child td, &:last-child th': { border: 0 } } },
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableCell, { align: "left", colSpan: 2 },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.InputLabel, null,
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: 'body1', noWrap: true, sx: { fontSize: '20px' } }, "Description of the endpoint:")),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TextField, { fullWidth: true, variant: "outlined", defaultValue: props.endpoint.description, sx: { width: '100%' } }))),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableRow, null,
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableCell, { align: 'left' },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.InputLabel, { id: "version-select-label" },
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: 'body1', noWrap: true, sx: { fontSize: '20px' } }, "Version:")),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Select, { labelId: "version-select-label", id: "version-select", value: version, onChange: handleVersionChange, sx: { width: 150 } }, (versions.length > 0) ? (versions.map((ver) => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.MenuItem, { key: ver.id, value: ver.id },
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { container: true, direction: "row", justifyContent: "space-between", alignItems: "center" },
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { item: true }, ver.versionName),
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { item: true },
                                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(DeleteButton, { isSelected: version !== ver.id, versionId: ver.id }))))))) : (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.MenuItem, { key: 0, value: 0 }, "No version")))),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableCell, { sx: { width: '100%' } },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.InputLabel, null,
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: 'body1', noWrap: true, sx: { fontSize: '20px' } }, "Description:")),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TextField, { disabled: true, fullWidth: true, variant: "standard", InputProps: {
                                    disableUnderline: true,
                                }, multiline: true, maxRows: 2, minRows: 2, value: versionDescription, sx: { width: '100%' } }))),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableRow, null,
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TableCell, { colSpan: 2 },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.InputLabel, null,
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: 'body1', noWrap: true, sx: { fontSize: '20px' } }, "URL:")),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TextField, { disabled: true, variant: 'outlined', value: endpointURLToCopy, sx: { width: '100%' }, InputProps: {
                                    endAdornment: (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(AlignedInputAdornment, { position: "end" },
                                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Tooltip, { title: "Copy Endpoint URL" },
                                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(IconButtonWithTooltip, { role: 'button', onClick: handleCopyToClipboard },
                                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_icons_io5__WEBPACK_IMPORTED_MODULE_6__.IoCopyOutline, null))))),
                                } }),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Snackbar, { open: snackbarOpen, onClose: () => setSnackbarOpen(false), autoHideDuration: 2000, message: "Copied to clipboard" }))))))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (EndpointSummary);


/***/ }),

/***/ "./lib/components/NewAPIKeyComponent.js":
/*!**********************************************!*\
  !*** ./lib/components/NewAPIKeyComponent.js ***!
  \**********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);


const NewAPIKeyComponent = (props) => {
    const _handleNameOnChange = (event) => {
        props.setAPIKeyName(event.target.value);
        const regex = /[^A-Za-z0-9_-]/;
        if (props.apiKeyName === '' || regex.test(props.apiKeyName)) {
            props.setAPIKeyNameError(true);
        }
        else {
            props.setAPIKeyNameError(false);
        }
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CssBaseline, null),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("form", { onSubmit: props.handleSubmit, noValidate: true },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.InputLabel, { sx: { whiteSpace: 'wrap' } }, "To create a apiKey for the user you want to share the endpoint with, please, insert a name and, optionally, a description:"),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { container: true, spacing: 2, direction: 'row', justifyContent: "left", alignItems: 'center', maxWidth: '1440px', width: '100%' },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { item: true, xs: 12 },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TextField, { id: "name-input", name: "name", variant: 'outlined', placeholder: "APIKey Name", fullWidth: true, required: true, onChange: e => _handleNameOnChange(e), error: props.apiKeyNameError, helperText: props.apiKeyNameError ? "Only letters, numbers, - and _ are allowed." : "", type: "text", value: props.apiKeyName })),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { item: true, xs: 12 },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TextField, { id: "description-input", name: "description", variant: 'outlined', placeholder: "APIKey Description", fullWidth: true, onChange: e => props.setAPIKeyDescription(e.target.value), value: props.apiKeyDescription })),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { item: true },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Button, { variant: "contained", color: "primary", type: "submit" }, "Create"))))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (NewAPIKeyComponent);


/***/ }),

/***/ "./lib/contexts/CommonContext.js":
/*!***************************************!*\
  !*** ./lib/contexts/CommonContext.js ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   CommonContext: () => (/* binding */ CommonContext),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__);


const CommonContext = react__WEBPACK_IMPORTED_MODULE_0___default().createContext(null);
const CommonProvider = ({ children }) => {
    const currentUserOwner = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.PageConfig.getOption('serverRoot').split('/')[2] || "";
    const [currentUser, setCurrentUser] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(currentUserOwner);
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        setCurrentUser(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.PageConfig.getOption('serverRoot').split('/')[2] || "");
    }, []);
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(CommonContext.Provider, { value: { currentUser } }, children));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (CommonProvider);


/***/ }),

/***/ "./lib/contexts/EndpointContext.js":
/*!*****************************************!*\
  !*** ./lib/contexts/EndpointContext.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   CurrentEndpointContext: () => (/* binding */ CurrentEndpointContext),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   useCurrentEndopintContext: () => (/* binding */ useCurrentEndopintContext)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);

const CurrentEndpointContext = react__WEBPACK_IMPORTED_MODULE_0___default().createContext(null);
const CurrentEndpointProvider = ({ children }) => {
    const [endpoint, setEndpoint] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)();
    const setCurrentEndpoint = (currentEndpoint) => {
        setEndpoint(currentEndpoint);
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(CurrentEndpointContext.Provider, { value: { endpoint, setCurrentEndpoint } }, children));
};
function useCurrentEndopintContext() {
    const context = react__WEBPACK_IMPORTED_MODULE_0___default().useContext(CurrentEndpointContext);
    if (!context) {
        throw new Error("useEndpointsContext must be used within a EndpointProvider");
    }
    return context;
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (CurrentEndpointProvider);


/***/ }),

/***/ "./lib/contexts/EndpointsContext.js":
/*!******************************************!*\
  !*** ./lib/contexts/EndpointsContext.js ***!
  \******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   EndpointContext: () => (/* binding */ EndpointContext),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   useEndopintsContext: () => (/* binding */ useEndopintsContext)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _common_requestAPI__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../common/requestAPI */ "./lib/common/requestAPI.js");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__);



const EndpointContext = react__WEBPACK_IMPORTED_MODULE_0___default().createContext(null);
const EndpointProvider = ({ children }) => {
    const [endpoints, setEndpoints] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)([]);
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        getEndpoints();
    }, []);
    const getEndpoints = async () => {
        const currentUserOwner = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.PageConfig.getOption('serverRoot').split('/')[2] || "";
        const ownedEndpointsList = await (0,_common_requestAPI__WEBPACK_IMPORTED_MODULE_2__.requestAPI)("endpoint?owner=" + encodeURIComponent(currentUserOwner));
        console.log(`Owned Endpoints => ${JSON.stringify(ownedEndpointsList, null, 2)}`);
        const parsedOwnedEndpointsList = JSON.parse(ownedEndpointsList);
        setEndpoints(parsedOwnedEndpointsList.data);
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(EndpointContext.Provider, { value: { endpoints, getEndpoints } }, children));
};
function useEndopintsContext() {
    const context = react__WEBPACK_IMPORTED_MODULE_0___default().useContext(EndpointContext);
    if (!context) {
        throw new Error("useEndpointsContext must be used within a EndpointProvider");
    }
    return context;
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (EndpointProvider);


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   BakeAPINotebookToolbarButton: () => (/* binding */ BakeAPINotebookToolbarButton),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/launcher */ "webpack/sharing/consume/default/@jupyterlab/launcher");
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _widgets_APICatalogWidget__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./widgets/APICatalogWidget */ "./lib/widgets/APICatalogWidget.js");
/* harmony import */ var lodash_isempty__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! lodash.isempty */ "webpack/sharing/consume/default/lodash.isempty/lodash.isempty");
/* harmony import */ var lodash_isempty__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(lodash_isempty__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var lodash_isundefined__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! lodash.isundefined */ "webpack/sharing/consume/default/lodash.isundefined/lodash.isundefined");
/* harmony import */ var lodash_isundefined__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(lodash_isundefined__WEBPACK_IMPORTED_MODULE_8__);
/* harmony import */ var _common_requestAPI__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./common/requestAPI */ "./lib/common/requestAPI.js");
/* harmony import */ var _common_utils__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./common/utils */ "./lib/common/utils.js");










// Commons


const plugin = {
    id: 'jupyterlab-apibaker:plugin',
    description: 'Create a secured API based on a function in your notebook in a few clicks.',
    autoStart: true,
    optional: [_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_0__.ISettingRegistry, _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_1__.ILauncher, _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2__.IMainMenu],
    activate
};
class BakeAPINotebookToolbarButton {
    createNew(panel, _) {
        const bakeAPI = async () => {
            var _a;
            const currentUserOwner = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__.PageConfig.getOption('serverRoot').split('/')[2] || "";
            let currentNotebookRaw = this.getNBContentAndMetadata(panel);
            let nbPath = `${_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__.PageConfig.getOption('serverRoot')}/${(_a = panel.context.contentsModel) === null || _a === void 0 ? void 0 : _a.path}`;
            if (lodash_isundefined__WEBPACK_IMPORTED_MODULE_8___default()(currentNotebookRaw)) {
                console.log("There has been an error parsing the current notebook. Please, contact the administrator.");
                return;
            }
            ;
            const extractedNBFunctions = await this.getNBFunctions(currentNotebookRaw);
            if (lodash_isundefined__WEBPACK_IMPORTED_MODULE_8___default()(extractedNBFunctions)) {
                console.log("No functions found in the notebook.");
                return;
            }
            ;
            const userSelectedFunction = await this.promptUserToSelectFunctionFromNB(extractedNBFunctions.data.nbfunctions);
            if (lodash_isundefined__WEBPACK_IMPORTED_MODULE_8___default()(userSelectedFunction)) {
                return;
            }
            ;
            const userSelectedFunctionAndCode = extractedNBFunctions.data.nbfunctions.filter((el) => el.functionName === userSelectedFunction)[0];
            const apiDescription = await _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.InputDialog.getText({
                title: "Bake a New API",
                label: "Provide a short description for your API:",
                placeholder: "Please, insert a short description.",
                okLabel: "Create",
                cancelLabel: "Cancel",
            });
            if (!apiDescription.button.accept) {
                return;
            }
            if (lodash_isempty__WEBPACK_IMPORTED_MODULE_7___default()(apiDescription.value)) {
                _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Notification.warning(`Please, insert a short description.`, { autoClose: 3000 });
                return;
            }
            const createEndpoint = await (0,_common_requestAPI__WEBPACK_IMPORTED_MODULE_9__.requestAPI)("endpoint", {
                method: "POST",
                body: JSON.stringify({
                    functionName: userSelectedFunctionAndCode.functionName,
                    functionCode: userSelectedFunctionAndCode.functionCode,
                    description: apiDescription.value,
                    notebookName: currentNotebookRaw.nbName,
                    owner: currentUserOwner,
                    nbPath
                })
            });
            console.log(`Create Endpoint Response => ${JSON.stringify(createEndpoint, null, 2)}`);
            let getEndpointUpdate;
            let i = 1;
            let imageCreationStatus = '';
            let prepareStage = { id: 0, jobId: '', reason: '', stage: '', status: '', trace: '' };
            let buildAndPushStage = { id: 0, jobId: '', reason: '', stage: '', status: '', trace: '' };
            let retry = true;
            let notif = _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Notification.manager.notify("Baking API...", 'in-progress', {});
            do {
                getEndpointUpdate = await (0,_common_requestAPI__WEBPACK_IMPORTED_MODULE_9__.requestAPI)("get-endpoint-updates", {
                    method: "POST",
                    body: JSON.stringify({
                        id: createEndpoint.data.id,
                        version: createEndpoint.data.versions[0].id,
                        owner: currentUserOwner,
                        action: 'image'
                    })
                });
                const delayMs = 500 * 2 ** i;
                console.log(`Delay => ${delayMs}`);
                if (getEndpointUpdate && getEndpointUpdate.data.jobs && getEndpointUpdate.data.jobs.length > 0) {
                    imageCreationStatus = getEndpointUpdate.data.status;
                    prepareStage = getEndpointUpdate.data.jobs.filter((item) => item.stage === 'prepare')[0];
                    buildAndPushStage = getEndpointUpdate.data.jobs.filter((item) => item.stage === 'build_and_push')[0];
                }
                console.log(`Prepare Stage Info => ${JSON.stringify(prepareStage)}`);
                console.log(`Build and Push Stage Info => ${JSON.stringify(buildAndPushStage)}`);
                if (['created', 'running', 'pending', ''].includes(prepareStage.status) || ['created', 'running', 'pending', ''].includes(buildAndPushStage.status)) {
                    _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Notification.manager.update({
                        id: notif,
                        message: `Creation Jobs -> Prepare: ${prepareStage.status} | Build and Push: ${buildAndPushStage.status}`,
                        type: 'in-progress'
                    });
                    await new Promise((resolve) => setTimeout(resolve, delayMs));
                    if (delayMs >= 20000) {
                        i = 0;
                    }
                    i++;
                }
                else if (prepareStage.status === 'failed' || buildAndPushStage.status === 'failed') {
                    _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Notification.manager.update({
                        id: notif,
                        message: `Creation Jobs Error -> Prepare: ${prepareStage.status} | Build and Push: ${buildAndPushStage.status}`,
                        type: 'error'
                    });
                    retry = false;
                }
                else if (prepareStage.status === 'success' && buildAndPushStage.status === 'success') {
                    _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Notification.manager.update({
                        id: notif,
                        message: `Creation Jobs Success -> Prepare: ${prepareStage.status} | Build and Push: ${buildAndPushStage.status}`,
                        type: 'success'
                    });
                    retry = false;
                }
                else {
                    _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Notification.manager.update({
                        id: notif,
                        message: `Creation Jobs Info: ${imageCreationStatus}`,
                        type: 'info'
                    });
                    retry = false;
                }
            } while (retry);
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ToolbarButton({
            className: "apiBaker",
            label: "Bake API",
            onClick: bakeAPI,
            tooltip: "Create an API endpoint based on a selected function from this notebook.",
        });
        panel.toolbar.insertItem(10, "bake-api", button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__.DisposableDelegate(() => {
            button.dispose();
        });
    }
    ;
    getNBContentAndMetadata(panel) {
        var _a;
        if (!panel.model || !panel.context.isReady) {
            return;
        }
        return {
            nbName: (0,_common_utils__WEBPACK_IMPORTED_MODULE_10__.extRemoverCorrector)(panel.title.label),
            nbRawName: panel.title.label,
            nbRaw: panel.model.toJSON(),
            pathToNotebook: `${_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__.PageConfig.getOption('serverRoot')} / ${(_a = panel.context.contentsModel) === null || _a === void 0 ? void 0 : _a.path}`
        };
    }
    ;
    async getNBFunctions(nbContentAndMetadata) {
        const nbInfo = await (0,_common_requestAPI__WEBPACK_IMPORTED_MODULE_9__.requestAPI)("parse-model", {
            method: "POST",
            body: JSON.stringify(nbContentAndMetadata.nbRaw)
        });
        console.log(`Functions List => ${JSON.stringify(nbInfo, null, 2)}`);
        if (lodash_isempty__WEBPACK_IMPORTED_MODULE_7___default()(nbInfo.data.nbfunctions)) {
            return;
        }
        ;
        return nbInfo;
    }
    ;
    async promptUserToSelectFunctionFromNB(functionsInNotebook) {
        let functionsToSelect = functionsInNotebook.map((el) => el.functionName);
        const functionSelector = await _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.InputDialog.getItem({
            title: "Bake a New API",
            label: "Select Function:",
            items: functionsToSelect,
            okLabel: "Next",
            cancelLabel: "Cancel",
        });
        if (!functionSelector.button.accept) {
            return;
        }
        if (lodash_isundefined__WEBPACK_IMPORTED_MODULE_8___default()(functionSelector.value)) {
            return undefined;
        }
        return functionSelector.value;
    }
}
;
function activate(app, settingRegistry, launcher, mainMenu, panel) {
    console.log('API Baker Extension Activated!');
    app.docRegistry.addWidgetExtension("Notebook", new BakeAPINotebookToolbarButton());
    Promise.all([app.restored]).then(() => {
        // a state perhaps https://github.com/jupyterlab/extension-examples/tree/3.x/state
        // Get state variables and jobs queue?
        // update jobs panel?
        // update notifications?
    });
    const { commands } = app;
    const command = "jlab-apibaker:command";
    commands.addCommand(command, {
        caption: "Show API Collection",
        label: "API Collection",
        execute: async () => {
            const currentUserOwner = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__.PageConfig.getOption('serverRoot').split('/')[2] || "";
            console.log(`Owner => ${currentUserOwner}`);
            const content = new _widgets_APICatalogWidget__WEBPACK_IMPORTED_MODULE_11__.APICatalogWidget();
            const widget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.MainAreaWidget({ content });
            widget.title.label = "API Collection";
            app.shell.add(widget, "main");
        },
    });
    const menu = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_6__.Menu({ commands: app.commands });
    menu.title.label = "API Baker";
    menu.addItem({ command });
    mainMenu.addMenu(menu, { rank: 900 });
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/widgets/APICatalogWidget.js":
/*!*****************************************!*\
  !*** ./lib/widgets/APICatalogWidget.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   APICatalogWidget: () => (/* binding */ APICatalogWidget)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components_APICatalogComponent__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../components/APICatalogComponent */ "./lib/components/APICatalogComponent.js");
/* harmony import */ var _contexts_EndpointsContext__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../contexts/EndpointsContext */ "./lib/contexts/EndpointsContext.js");
/* harmony import */ var _contexts_EndpointContext__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../contexts/EndpointContext */ "./lib/contexts/EndpointContext.js");
/* harmony import */ var _contexts_CommonContext__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../contexts/CommonContext */ "./lib/contexts/CommonContext.js");






class APICatalogWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    constructor() {
        super();
    }
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_contexts_EndpointsContext__WEBPACK_IMPORTED_MODULE_2__["default"], null,
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_contexts_EndpointContext__WEBPACK_IMPORTED_MODULE_3__["default"], null,
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_contexts_CommonContext__WEBPACK_IMPORTED_MODULE_4__["default"], null,
                    react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_components_APICatalogComponent__WEBPACK_IMPORTED_MODULE_5__.APICatalogComponent, null)))));
    }
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.487dd87c45cd3b3d57a2.js.map