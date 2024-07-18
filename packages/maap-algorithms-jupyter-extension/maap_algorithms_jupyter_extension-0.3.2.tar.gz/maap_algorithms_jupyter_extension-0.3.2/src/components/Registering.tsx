import React, { useState } from 'react';
import { Button } from 'react-bootstrap';


export const Registering = () => {
    
    // Need to ping gitlab to control this
    const [isRegistering, setIsRegistering] = useState(true)

    return (
        <div>
            <span>Registering algorithm...</span>
            <iframe src="google.com"></iframe>
            <Button disabled={isRegistering}>View Summary</Button>
        </div>
    )
}