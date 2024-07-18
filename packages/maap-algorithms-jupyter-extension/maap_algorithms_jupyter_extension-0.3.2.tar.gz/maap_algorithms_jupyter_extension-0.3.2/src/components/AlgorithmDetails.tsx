import React from 'react'
import { Nav, Tab, Table } from 'react-bootstrap'
import { useSelector } from 'react-redux'
import { selectRegisteredAlgorithms } from '../redux/slices/registeredAlgorithms'

export const AlgorithmDetails = (): JSX.Element => {

    // Redux
    const { selectedAlgorithm } = useSelector(selectRegisteredAlgorithms)

    return (
        <div className="job-details-container">
            <h2>Algorithm Details</h2>
            <Tab.Container id="left-tabs-example" defaultActiveKey="general">
                <Nav variant="pills" className="nav-menu">
                    <Nav.Item>
                        <Nav.Link eventKey="general">General</Nav.Link>
                    </Nav.Item>
                    <Nav.Item>
                        <Nav.Link eventKey="inputs">Inputs</Nav.Link>
                    </Nav.Item>
                </Nav>
                <Tab.Content className="content-padding">
                    <Tab.Pane eventKey="general">
                        
                        {/* {selectedAlgorithm} */}
                        {/* {selectedJob ? <GeneralJobInfoTable /> : <div className='subtext'>No algorithm selected</div>} */}
                    </Tab.Pane>
                    <Tab.Pane eventKey="inputs">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Data Type</th>
                                    <th>Default Value</th>
                                    <th>Required?</th>
                                </tr>
                            </thead>
                            <tbody>
                                {selectedAlgorithm ?
                                selectedAlgorithm.inputs.map((input) => {
                                    console.log("iterating over inputs")
                                    console.log(input)
                                    return <tr>
                                        <td>{input.id}</td>
                                        <td>{input.dataType}</td>
                                        <td>{input.defaultValue}</td>
                                        <td>{input.required}</td>
                                    </tr>
                                }) : <i>"No algorithm selected"</i>}
                            </tbody>
                        </table>
                    </Tab.Pane>
                </Tab.Content>
            </Tab.Container>
        </div>
    )
}