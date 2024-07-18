import React from 'react';
import { Button } from 'react-bootstrap';
import '../../style/actionBar.css';
import { openRegistration } from '../utils/jupyter'


export const ActionBar = ({jupyterApp}) => {
    
    return (
        <div className="action-bar">
            <Button variant="primary" onClick={() => openRegistration(jupyterApp, null)}>+ New Algorithm</Button>
        </div>
    )
}