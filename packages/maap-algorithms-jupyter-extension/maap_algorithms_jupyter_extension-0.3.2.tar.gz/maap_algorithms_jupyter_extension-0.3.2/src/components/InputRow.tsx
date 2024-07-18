import React from 'react';
import { Form } from 'react-bootstrap';
import { ALGO_INPUT_FIELDS } from '../constants';
import { BsFillXCircleFill } from 'react-icons/bs';

export const InputRow = ({row, handleRemoveRow, handleDataChange }) => {
    return (
        <tr className="input-row" id={row.inputId.toString()}>
            {/* <td>{row.inputId}</td> */}
            <td></td>
            <td><Form.Control id={ALGO_INPUT_FIELDS.INPUT_NAME} type="text" placeholder="What is the input name?" onChange={handleDataChange} value={row.inputName}/></td>
            <td><Form.Control id={ALGO_INPUT_FIELDS.INPUT_DESC} type="text" placeholder="Describe the input parameter" onChange={handleDataChange} value={row.inputDesc} /></td>
            <td><Form.Switch id={ALGO_INPUT_FIELDS.IS_REQUIRED} className="center-align" aria-label="required_input" onChange={handleDataChange} checked={row.isRequired} /></td>
            <td><Form.Control id={ALGO_INPUT_FIELDS.INPUT_DEFAULT} type="text" placeholder="Default value" onChange={handleDataChange} value={row.inputDefault} /></td>
            <td style={{verticalAlign: "middle"}}><span><BsFillXCircleFill className="danger-icon" id={row.inputId.toString()} onClick={() => handleRemoveRow(row.inputId.toString())}/></span></td>
        </tr>
    )
}