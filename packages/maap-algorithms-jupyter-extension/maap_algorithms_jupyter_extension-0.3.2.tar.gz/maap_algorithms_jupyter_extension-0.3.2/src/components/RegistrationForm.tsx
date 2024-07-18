import React, { useState, useEffect } from 'react';
import { Alert, Button, Form, Modal, Table } from 'react-bootstrap';
import { BsArrowRightShort, BsInfoCircleFill } from "react-icons/bs";
import { BsFillCheckCircleFill, BsFillXCircleFill } from 'react-icons/bs';
import { ALGO_INPUTS } from '../constants';
import { useDispatch, useSelector } from 'react-redux';
import { algorithmActions, selectAlgorithm } from '../redux/slices/algorithmSlice'
import { TableConfigInputs } from './TableConfigInputs';
import { TableFileInputs } from './TableFileInputs';
import { TablePositionalInputs } from './TablePositionalInputs';
import { registerAlgorithm } from '../utils/algoConfig';
import AsyncSelect from 'react-select/async';
import { getResources, getWorkspaceContainer } from "../utils/api";
import { Spinner } from 'react-bootstrap';
import { checkUrlExists } from '../utils/utils';
import { Notification } from "@jupyterlab/apputils";

export const RegistrationForm = ({ data }) => {

    // Local state variables
    const [firstStep, setFirstStep] = useState(true)
    // const [validRepo, setValidRepo] = useState(false)
    const [validRepo, setValidRepo] = useState(true)
    const [repoBranches, setRepoBranches] = useState([])
    const [firstRepoCheck, setFirstRepoCheck] = useState(true)
    const [show, setShow] = useState(false);
    const [showSpinner, setShowSpinner] = useState(false)
    const [showNotification, setShowNotification] = useState(false);

    // Redux
    const dispatch = useDispatch()
    const { registrationUrl, repoRunCommand, algoResource, algoContainer } = useSelector(selectAlgorithm)
    const { setAlgoDesc,
            setAlgoDiskSpace,
            setAlgoName,
            setAlgoResource,
            setAlgoContainerURL,
            setRepoBranch,
            setRepoRunCommand,
            setRepoBuildCommand,
            setRepoUrl } = algorithmActions

    

    const validateRepo = (e) => {
        checkUrlExists(e.target.value) ? setValidRepo(true) : setValidRepo(false)
        setFirstRepoCheck(false)
    }

    const handleKeyPress = (e) => {
        if (e.keyCode === 13){
          e.target.blur()
        }
    }

    const handleAlgoNameChange = e => {
        dispatch(setAlgoName(e.target.value))
    }

    const handleRepoUrlChange = e => {
        dispatch(setRepoUrl(e.target.value))
    }

    const handleBranchChange = e => {
        dispatch(setRepoBranch(e.target.value))
    }

    const handleRunCmdChange = e => {
        dispatch(setRepoRunCommand(e.target.value))
    }

    const handleBuildCmdChange = e => {
        dispatch(setRepoBuildCommand(e.target.value))
    }

    const handleAlgoDescChange = e => {
        dispatch(setAlgoDesc(e.target.value))
    }

    const handleDiskSpaceChange = e => {
        dispatch(setAlgoDiskSpace(e.target.value))
    }

    const handleResourceChange = value => {
        dispatch(setAlgoResource(value))
    }

    const handleContainerURLChange = e => {
        dispatch(setAlgoContainerURL(e.target.value))
    }

    const handleModalClose = () => setShow(false);
    const handleModalShow = () => setShow(true);

    async function submitHandler(e) { // = (e) => {
        e.preventDefault()
        // setShowSpinner(true)
        let res = await registerAlgorithm()
        if (res) {
            // setShowSpinner(false)
            handleModalShow()
            setShowNotification(true)
        }
    }

    useEffect(() => {
        // The container from which the workspace is running will be the default container for algorithm registration.
        getWorkspaceContainer().then((param) => {
            let container = param["DOCKERIMAGE_PATH"]
            if (container != null) { dispatch(setAlgoContainerURL(container)) }
        })
    }, []);

    useEffect(() => {
        if (showNotification) {
            Notification.success("The algorithm was successfully submitted.", {
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

    return (
        <>
        <Form onSubmit={submitHandler}>
            <div className='section-padding'>
                <h2>Register Algorithm</h2>
                <Alert variant="primary" className="alert-box">To register an algorithm to the MAAP, your code must be committed to a public code repository.<br/><br/>Need more tips and tricks? Documentation may be found <a href="">here</a>.</Alert>
                <h3>Repository Information</h3>
                <Table className="form-table">
                    <tbody>
                        <tr>
                            <td>Repository URL</td>
                            <td className='flex'>
                                <div>
                                    <div className='flex'>
                                        <Form.Control onChange={handleRepoUrlChange} onKeyDown={handleKeyPress} onBlur={validateRepo} type="text" placeholder="Enter repository URL" />
                                        <div className={firstRepoCheck ? 'hide' : 'show'}>
                                            {validRepo ? <BsFillCheckCircleFill className='success-icon' /> : <BsFillXCircleFill className='danger-icon' />}
                                        </div>
                                    </div>
                                    <div className={firstStep ? firstRepoCheck ? 'hide' : 'show' : 'hide'}>
                                        {/* {validRepo ? <span className='success-icon'>Confirmed repository exists and is public.</span> : <span className='danger-icon'>Failed to confirm repository exists and is public.</span>} */}
                                    </div>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td>Repository Branch</td>
                            <td>
                                <Form.Control type="text" placeholder="Enter repository branch" onChange={handleBranchChange} />
                            </td>
                        </tr>
                        <tr>
                            <td>Run Command</td>
                            <td>
                                <Form.Control type="text" placeholder="Enter run command" onChange={handleRunCmdChange} />
                            </td>
                        </tr>
                        <tr>
                            <td>Build Command</td>
                            <td>
                                <Form.Control type="text" placeholder="Enter build command" onChange={handleBuildCmdChange} />
                            </td>
                        </tr>
                    </tbody>
                </Table>
            </div>

            <div className='section-padding'>
                <h3>General Information</h3>
                <Table className="form-table">
                    <tbody>
                        <tr>
                            <td>Algorithm Name</td>
                            <td>
                                <Form.Control type="text" placeholder="Enter algorithm name" onChange={handleAlgoNameChange}/>
                            </td>
                        </tr>
                        <tr>
                            <td>Algorithm Description</td>
                            <td>
                                <Form.Control type="textarea" placeholder="Enter algorithm description" onChange={handleAlgoDescChange} />
                            </td>
                        </tr>
                        <tr>
                            <td>Disk Space (GB)</td>
                            <td>
                                <Form.Control type="text" placeholder="Enter disk space" onChange={handleDiskSpaceChange} />
                            </td>
                        </tr>
                        <tr>
                            <td>Resource Allocation</td>
                            <td>
                                <Form.Group className="mb-3 algorithm-input">
                                    <AsyncSelect
                                        cacheOptions
                                        defaultOptions
                                        value={algoResource}
                                        loadOptions={getResources}
                                        onChange={handleResourceChange}
                                        placeholder="Select resource"
                                    />
                                </Form.Group>
                                {/* <Form.Control type="text" placeholder="Enter resource allocation" onChange={handleResourceChange} /> */}
                            </td>
                        </tr>
                        <tr>
                            <td>Container URL</td>
                            <td>
                                <Form.Control type="text" defaultValue={algoContainer} placeholder="Enter container URL" onChange={handleContainerURLChange} />
                            </td>
                        </tr>
                    </tbody>
                </Table>

                <div className='section-padding'>
                    <h3>Inputs</h3>
                    {/* <TableConfigInputs /> */}
                    <TableFileInputs />
                    <TablePositionalInputs />
                </div>

                <Button variant="primary" type="submit">
                    Register Algorithm 
                    {/* <BsArrowRightShort size={20} /> */}
                </Button>
            </div>
        </Form>
        <div>
        {/* {showSpinner ? <Spinner animation="border" variant="primary" /> : */}
        <Modal show={show} aria-labelledby="contained-modal-title-vcenter" onHide={handleModalClose}>
            <Modal.Header closeButton>
                <Modal.Title>Algorithm submitted for registration</Modal.Title>
            </Modal.Header>
            <Modal.Body>Your algorithm was submitted for registration. You can view the progress here: <a href={registrationUrl} target="_blank">{registrationUrl}</a></Modal.Body>
            <Modal.Footer>
                <Button variant="primary" onClick={handleModalClose}>
                    Close
                </Button>
            </Modal.Footer>
        </Modal>
        </div>
        </>
    )
}