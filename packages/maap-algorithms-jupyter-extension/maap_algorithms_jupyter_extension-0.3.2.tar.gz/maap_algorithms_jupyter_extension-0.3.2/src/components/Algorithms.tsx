import React, { useMemo, useState, useEffect } from 'react';
import { IAlgorithm } from '../types/index';
import {
    useTable,
    useGlobalFilter,
    usePagination,
    useFilters,
    Column
} from 'react-table';
import {
    Button,
    Modal,
    Pagination,
    Spinner,
    Table
} from 'react-bootstrap';
import { ActionBar } from './ActionBar';
import { BsFillPencilFill, BsFillPlayFill, BsFillTrash3Fill, BsExclamationTriangleFill } from 'react-icons/bs';
import { selectSplitPane } from '../redux/slices/splitPaneSlice';
import { useDispatch, useSelector } from 'react-redux';
import { openJobs, openRegistration } from '../utils/jupyter'
import { registeredAlgorithmsActions, selectRegisteredAlgorithms } from '../redux/slices/registeredAlgorithms';
import { describeAllAlgorithms, unregisterAlgorithm } from '../utils/api';
import { IAlgorithmData } from '../types/slices';

function DefaultColumnFilter({
    column: { filterValue, preFilteredRows, setFilter, columns },
}) {

    return (
        <input
            value={filterValue || ''}
            onChange={e => {
                setFilter(e.target.value || undefined) 
            }}
            placeholder={`Search...`}
        />
    )
}


function ReactTable({ columns, data, jupyterApp }) {

    // Redux
    const dispatch = useDispatch()
    const { setSelectedAlgorithm } = registeredAlgorithmsActions
    const { rowCount } = useSelector(selectSplitPane)
    const { algorithmsList } = useSelector(selectRegisteredAlgorithms)

    // Local
    const [hoveredRowIndex, setHoveredRowIndex] = useState(null);
    const [show, setShow] = useState(false);
    const [unregisterAlgoID, setUnregisterAlgoID] = useState("");
    const [showSpinner, setShowSpinner] = useState(false)
    

    const handleRowHover = rowIndex => {
        setHoveredRowIndex(rowIndex);
    };

    const handleRowClick = row => {
        const algorithm: IAlgorithmData = row.original
        console.log("Data: ", algorithm)
        dispatch(setSelectedAlgorithm(algorithm))
    };

    const handleUnregisterModal = row => {
        setUnregisterAlgoID(row.values.id)
        setShow(true);
    }

    const handleUnregistration = algoID => {
        unregisterAlgorithm(algoID).finally(() => {
            console.log("unregistered return")
        })
    }

    

    const handleClose = () => setShow(false);

    const defaultColumn = React.useMemo<any>(
        () => ({
            Filter: DefaultColumnFilter,
        }),
        []
    )


    useEffect(() => {
        setPageSize(rowCount)
    }, [rowCount]);


    // useEffect(() => {
    //     console.log("Algorithms")
    //     console.log(algorithmsData)
    // }, [algorithmsData]);

    useEffect(() => {
        setShowSpinner(true)
        describeAllAlgorithms().finally(() => setShowSpinner(false))
      }, [algorithmsList]);

    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        rows,
        canPreviousPage,
        canNextPage,
        prepareRow,
        pageOptions,
        pageCount,
        gotoPage,
        nextPage,
        previousPage,
        setPageSize,
        state: { pageIndex, pageSize }
    } = useTable({
        defaultColumn,
        columns,
        data,
        initialState: { pageIndex: 0, pageSize: rowCount }
    }, useFilters, usePagination)

    return (<>
        <Table {...getTableProps()} className='hover'>
            <thead>
                {headerGroups.map(headerGroup => (
                    <tr {...headerGroup.getHeaderGroupProps()}>
                        {headerGroup.headers.map(column => (
                            <th {...column.getHeaderProps()}>{column.render('Header')}<div>{column.canFilter ? column.render('Filter') : null}</div></th>
                        ))}
                    </tr>
                ))}
            </thead>
            <tbody {...getTableBodyProps()}>
                {showSpinner ? <tr><td colSpan={columns.length} style={{ textAlign: "center" }}><Spinner animation="border" variant="primary" /></td></tr>:
                rows.map((row, i) => {
                    prepareRow(row)
                    const isRowHovered = i === hoveredRowIndex;
                    return (
                        <tr {...row.getRowProps()} onClick={() => handleRowClick(row)} onMouseEnter={() => handleRowHover(i)} onMouseLeave={() => handleRowHover(null)} className={isRowHovered ? 'hovered' : ''}>
                            {row.cells.map(cell => {
                                return <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                            })}
                            {isRowHovered ? (
                                <td className="row-actions">
                                    
                                    {/* TODO: MAAP API does not return all the data used to register an algorithm, so we can't prepopulate the registration form
                                        with a registered algorithm's data. dps-jupyter-extension
                                    <BsFillPencilFill color='blue' size={16} title="Edit" onClick={() => openRegistration(jupyterApp, row.original)} /> */}
                                    <BsFillPlayFill color='green' size={18} title="Run" onClick={() => openJobs(jupyterApp, row)} />
                                    <BsFillTrash3Fill color='red' size={16} title="Unregister" onClick={() => handleUnregisterModal(row)}/>
                                </td>
                            ): <td/>}
                        </tr>
                    )
                })}
            </tbody>
        </Table>

        <div className='pagination-footer'>
            <span>Showing {pageOptions.length === 0 ? 0 : pageIndex + 1} of {pageOptions.length}</span>
            <Pagination>
                <Pagination.First onClick={() => gotoPage(0)} disabled={!canPreviousPage} />
                <Pagination.Prev onClick={() => previousPage()} disabled={!canPreviousPage} />
                <Pagination.Next onClick={() => nextPage()} disabled={!canNextPage} />
                <Pagination.Last onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage} />
            </Pagination>
        </div>

        <Modal show={show} onHide={handleClose} centered>
        <Modal.Header closeButton>
        <BsExclamationTriangleFill color='red' size={30} className="margin-right-1" />
        </Modal.Header>
        <Modal.Body>Are you sure you want to unregister <i>{unregisterAlgoID}</i> ?</Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Cancel
          </Button>
          <Button variant="danger" onClick={() => handleUnregistration(unregisterAlgoID)}>
            Unregister
          </Button>
        </Modal.Footer>
      </Modal>
    </>
    )
}

export const Algorithms = ({ jupyterApp }) => {

    const { algorithmsData } = useSelector(selectRegisteredAlgorithms)

    const data = useMemo(() => algorithmsData, [algorithmsData])
    const columns = useMemo(
        () => [
            {
                Header: 'Algorithm ID',
                accessor: 'id' as const,
            }
            // {
            //     Header: 'Creator',
            //     accessor: 'creator' as const,
            //     width: 50
            // },
            // {
            //     Header: 'Description',
            //     accessor: 'description' as const,
            // },
            // {
            //     Header: 'Last Updated',
            //     accessor: 'time_last_update' as const,
            //     width: 100
            // }
        ],

        []
    )

    return (
        <div >
            <ActionBar jupyterApp={jupyterApp}/>
            <ReactTable columns={columns} data={data} jupyterApp={jupyterApp} />
        </div>
    )
}

