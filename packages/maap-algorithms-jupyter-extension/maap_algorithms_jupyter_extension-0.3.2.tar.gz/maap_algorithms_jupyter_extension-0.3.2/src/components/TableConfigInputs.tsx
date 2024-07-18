import React, { useEffect, useState } from 'react';
import { OverlayTrigger, Row, Table, Tooltip } from 'react-bootstrap';
import { BsPlusCircleFill, BsInfoCircle } from 'react-icons/bs';
import { useDispatch, useSelector } from 'react-redux';
import { algorithmActions, selectAlgorithm } from '../redux/slices/algorithmSlice'
import { ALGO_INPUTS, ALGO_INPUTS_DESC, ALGO_INPUT_FIELDS } from '../constants';
import { InputRow } from './InputRow';
import { EmptyRow } from './EmptyRow';
import { Tooltip as ReactTooltip } from "react-tooltip";

export const TableConfigInputs = () => {

    // Redux
    const dispatch = useDispatch()

    const { configData, inputId } = useSelector(selectAlgorithm)
    const { addConfigData, updateConfigData, removeConfigData, incrementInputId } = algorithmActions

    const addRow = () => {
        dispatch(addConfigData({[ALGO_INPUT_FIELDS.INPUT_NAME]: "", 
                                [ALGO_INPUT_FIELDS.INPUT_DEFAULT]: "", 
                                [ALGO_INPUT_FIELDS.INPUT_DESC]: "", 
                                [ALGO_INPUT_FIELDS.IS_REQUIRED]: false, 
                                [ALGO_INPUT_FIELDS.INPUT_ID]: inputId }))
        dispatch(incrementInputId())
    }

    const handleDataChange = e => {
        switch (e.target.type) {
            case "checkbox": {
                dispatch(updateConfigData({inputId: e.target.parentNode.parentNode.parentNode.id, inputField: [e.target.id], inputValue: e.target.checked}))
                break;
            }
            default: dispatch(updateConfigData({inputId: e.target.parentNode.parentNode.id, inputField: [e.target.id], inputValue: e.target.value}))
            break;
        }
    }

    const handleRemoveRow = (inputId) => {
        dispatch(removeConfigData({key: inputId}))
    }

    return (
        <div>
            <div className="input-types">
                <h4>Configuration Inputs</h4>
                <ReactTooltip
                        anchorId="config_input_info"
                        place="right"
                        variant="dark"
                        content={ALGO_INPUTS_DESC.CONFIGURATION_INPUTS}
                />
                <span id="config_input_info"><BsInfoCircle /></span>
            </div>
            <Table className="inputs-table">
                <thead>
                    <tr>
                        <td><BsPlusCircleFill className="success-icon" onClick={addRow} /></td>
                        <td>Name</td>
                        <td>Description</td>
                        <td className="center-align">Required?</td>
                        <td>Default Value</td>
                        <td></td>
                    </tr>
                </thead>
                <tbody>
                {configData.length == 0 ? <EmptyRow text="No inputs specified"/> : Object.entries(configData).map(([key, data]) => {
                    console.log(data)
                    return <InputRow row={data} handleRemoveRow={handleRemoveRow} handleDataChange={handleDataChange} />
                })}
                </tbody>
            </Table>
        </div>
    )
}