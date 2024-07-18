import React from 'react';
import { Tooltip } from 'react-bootstrap';

export const SimpleTooltip = ({ text }) => {

    return (
        <Tooltip id="tooltip">
            <strong>Holy guacamole!</strong> Check this info.
        </Tooltip>
    )
}

// const tooltip = (
//     <Tooltip id="tooltip">
//       <strong>Holy guacamole!</strong> Check this info.
//     </Tooltip>
//   );