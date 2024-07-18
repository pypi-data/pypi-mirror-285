import React, { useEffect, useState } from 'react';
import { OverlayTrigger, Row, Table, Tooltip } from 'react-bootstrap';
import { BsPlusCircleFill, BsInfoCircle, BsFillInfoCircleFill } from 'react-icons/bs';
import { useDispatch, useSelector } from 'react-redux';
import { algorithmActions, selectAlgorithm } from '../redux/slices/algorithmSlice'
import { ALGO_INPUTS, ALGO_INPUTS_DESC, ALGO_INPUT_FIELDS } from '../constants';
import { InputRow } from './InputRow';
import { EmptyRow } from './EmptyRow';
import { Tooltip as ReactTooltip } from "react-tooltip";

export const TablePositionalInputs = () => {

    // Redux
    const dispatch = useDispatch()

    const { positionalData, inputId } = useSelector(selectAlgorithm)
    const { addPositionalData, updatePositionalData, removePositionalData, incrementInputId } = algorithmActions

    const addRow = () => {
        dispatch(addPositionalData({[ALGO_INPUT_FIELDS.INPUT_NAME]: "", 
                                    [ALGO_INPUT_FIELDS.INPUT_DEFAULT]: "", 
                                    [ALGO_INPUT_FIELDS.INPUT_DESC]: "", 
                                    [ALGO_INPUT_FIELDS.IS_REQUIRED]: false, 
                                    [ALGO_INPUT_FIELDS.INPUT_ID]: inputId }))
        dispatch(incrementInputId())
    }

    const handleDataChange = e => {
        switch (e.target.type) {
            case "checkbox": {
                dispatch(updatePositionalData({inputId: e.target.parentNode.parentNode.parentNode.id, inputField: [e.target.id], inputValue: e.target.checked}))
                break;
            }
            default: dispatch(updatePositionalData({inputId: e.target.parentNode.parentNode.id, inputField: [e.target.id], inputValue: e.target.value}))
            break;
        }
    }

    const handleRemoveRow = (inputId) => {
        dispatch(removePositionalData({key: inputId}))
    }

    return (
        <div>
            <div className="input-types">
                <h4>Positional Inputs</h4>
                <ReactTooltip
                    anchorId="positional_input_info"
                    place="right"
                    variant="dark"
                    content={ALGO_INPUTS_DESC.POSITIONAL_INPUTS}
                />
                <span id="positional_input_info"><BsInfoCircle /></span>
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
                    {positionalData.length == 0 ? <EmptyRow text="No inputs specified"/> : Object.entries(positionalData).map(([key, data]) => {
                    return <InputRow row={data} handleRemoveRow={handleRemoveRow} handleDataChange={handleDataChange} />
                })}
                </tbody>
            </Table>
        </div>
    )
}