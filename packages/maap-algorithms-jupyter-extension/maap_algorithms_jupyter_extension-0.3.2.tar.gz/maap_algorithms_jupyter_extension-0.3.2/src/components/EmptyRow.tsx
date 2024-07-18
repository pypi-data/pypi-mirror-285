import React from 'react';
import { COLUMN_SPAN } from '../constants';

export const EmptyRow = ({ text }) => {

    return (
        <tr>
            <td colSpan={COLUMN_SPAN} className="empty-row">{text}</td>
        </tr>
    )
}