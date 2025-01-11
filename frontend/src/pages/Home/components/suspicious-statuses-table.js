import * as React from 'react';
import {useEffect, useRef, useState} from 'react';
import PropTypes from 'prop-types';
import {styled, useTheme} from '@mui/material/styles';
import Box from '@mui/material/Box';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell, {tableCellClasses} from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableFooter from '@mui/material/TableFooter';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import IconButton from '@mui/material/IconButton';
import FirstPageIcon from '@mui/icons-material/FirstPage';
import KeyboardArrowLeft from '@mui/icons-material/KeyboardArrowLeft';
import KeyboardArrowRight from '@mui/icons-material/KeyboardArrowRight';
import LastPageIcon from '@mui/icons-material/LastPage';
import axios from "axios";
import TableHead from "@mui/material/TableHead";
import Button from '@mui/material/Button';
import ReactMarkdown from 'react-markdown';

function TablePaginationActions(props) {
    const theme = useTheme();
    const { count, page, rowsPerPage, onPageChange } = props;

    const handleFirstPageButtonClick = (event) => {
        onPageChange(event, 0);
    };

    const handleBackButtonClick = (event) => {
        onPageChange(event, page - 1);
    };

    const handleNextButtonClick = (event) => {
        onPageChange(event, page + 1);
    };

    const handleLastPageButtonClick = (event) => {
        onPageChange(event, Math.max(0, Math.ceil(count / rowsPerPage) - 1));
    };

    return (
        <Box sx={{ flexShrink: 0, ml: 2.5 }}>
            <IconButton
                onClick={handleFirstPageButtonClick}
                disabled={page === 0}
                aria-label="first page"
            >
                {theme.direction === 'rtl' ? <LastPageIcon/> : <FirstPageIcon/>}
            </IconButton>
            <IconButton
                onClick={handleBackButtonClick}
                disabled={page === 0}
                aria-label="previous page"
            >
                {theme.direction === 'rtl' ? <KeyboardArrowRight/> : <KeyboardArrowLeft/>}
            </IconButton>
            <IconButton
                onClick={handleNextButtonClick}
                disabled={page >= Math.ceil(count / rowsPerPage) - 1}
                aria-label="next page"
            >
                {theme.direction === 'rtl' ? <KeyboardArrowLeft/> : <KeyboardArrowRight/>}
            </IconButton>
            <IconButton
                onClick={handleLastPageButtonClick}
                disabled={page >= Math.ceil(count / rowsPerPage) - 1}
                aria-label="last page"
            >
                {theme.direction === 'rtl' ? <FirstPageIcon/> : <LastPageIcon/>}
            </IconButton>
        </Box>
    );
}

TablePaginationActions.propTypes = {
    count: PropTypes.number.isRequired,
    onPageChange: PropTypes.func.isRequired,
    page: PropTypes.number.isRequired,
    rowsPerPage: PropTypes.number.isRequired,
};

const StyledTableCell = styled(TableCell)(({ theme }) => ({
    [`&.${tableCellClasses.head}`]: {
        backgroundColor: theme.palette.common.black,
        color: theme.palette.common.white,
    },
    [`&.${tableCellClasses.body}`]: {
        fontSize: 14,
    },
}));

export default function SuspiciousStatusesTable() {
    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(25);
    const [suspiciousStatuses, setSuspiciousStatuses] = useState([]);

    const wsRef = useRef(null);

    const [streamBuffer, setStreamBuffer] = useState({});

    const getSuspiciousStatusesData = async () => {
        try {
            const data = await axios.get(
                "http://0.0.0.0:8000/api/v1/statuses/suspicious?limit=10000"
            );
            console.log(data.data.results)
            setSuspiciousStatuses(data.data.results);
        } catch (e) {
            console.log(e);
        }
    };

    useEffect(() => {
        getSuspiciousStatusesData().then(r => null);
    }, []);

    const emptyRows =
        page > 0 ? Math.max(0, (1 + page) * rowsPerPage - suspiciousStatuses.length) : 0;

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const handleFetchChatGPT = (statusId) => {
        if (wsRef.current) {
            wsRef.current.close();
        }

        wsRef.current = new WebSocket("ws://0.0.0.0:8000/ws");

        let accumulatedResponse = "";

        wsRef.current.onopen = () => {
            wsRef.current.send(statusId.toString());
        };

        wsRef.current.onmessage = (event) => {
            accumulatedResponse  = event.data;

            setStreamBuffer((prev) => ({
                ...prev,
                [statusId]: accumulatedResponse,
            }));
        };

        wsRef.current.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        wsRef.current.onclose = () => {
            console.log("WebSocket closed, finalizing response.");

            setSuspiciousStatuses((prev) =>
                prev.map((item) => {
                    if (item.id === statusId) {
                        return {
                            ...item,
                            chatgpt_response: accumulatedResponse,
                        };
                    }
                    return item;
                })
            );

            setStreamBuffer((prev) => ({
                ...prev,
                [statusId]: accumulatedResponse,
            }));

            wsRef.current = null;
        };
    };


    return (
        <TableContainer component={Paper}>
            <Table sx={{ minWidth: 500 }} aria-label="custom pagination table">
                <TableHead>
                    <TableRow>
                        <StyledTableCell align="left">Created At</StyledTableCell>
                        <StyledTableCell align="left">Language</StyledTableCell>
                        <StyledTableCell align="left">Url</StyledTableCell>
                        <StyledTableCell align="left">Content</StyledTableCell>
                        <StyledTableCell align="left">Checked At</StyledTableCell>
                        <StyledTableCell align="left">Author Followers Count</StyledTableCell>
                        <StyledTableCell align="left">Author Following Count</StyledTableCell>
                        <StyledTableCell align="left">Author Statuses Count</StyledTableCell>
                        <StyledTableCell align="left">Author Created At</StyledTableCell>
                        <StyledTableCell align="left">Analyze</StyledTableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {(suspiciousStatuses.length > 0
                        ? suspiciousStatuses.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                        : suspiciousStatuses
                    ).map((row) => {
                        const partialStream = streamBuffer[row.id] || "";

                        return (
                            <TableRow key={row.id}>
                                <TableCell style={{ width: 160 }} align="left">
                                    {new Date(row.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}{" "}
                                    {new Date(row.created_at).toLocaleDateString('en-CA')}
                                </TableCell>
                                <TableCell style={{ width: 160 }} align="left">
                                    {row.language}
                                </TableCell>
                                <TableCell style={{ width: 160 }} align="left">
                                    <a href={row.url}>{row.url}</a>
                                </TableCell>
                                <TableCell style={{ width: 160 }} align="left">
                                    {row.content}
                                </TableCell>
                                <TableCell style={{ width: 160 }} align="left">
                                    {row.checked_at}
                                </TableCell>
                                <TableCell style={{ width: 160 }} align="left">
                                    {row.author_followers_count}
                                </TableCell>
                                <TableCell style={{ width: 160 }} align="left">
                                    {row.author_following_count}
                                </TableCell>
                                <TableCell style={{ width: 160 }} align="left">
                                    {row.author_statuses_count}
                                </TableCell>
                                <TableCell style={{ width: 160 }} align="right">
                                    {new Date(row.author_created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}{" "}
                                    {new Date(row.author_created_at).toLocaleDateString('en-CA')}
                                </TableCell>
                                <TableCell
                                    style={{ width: 10000000000, verticalAlign: 'top' }}
                                    align="left"
                                >
                                    {row.chatgpt_response ? (
                                        <ReactMarkdown>{row.chatgpt_response}</ReactMarkdown>
                                    ) : (
                                        partialStream ? (
                                            <ReactMarkdown>{partialStream}</ReactMarkdown>
                                        ) : (
                                            <Button
                                                variant="contained"
                                                onClick={() => handleFetchChatGPT(row.id)}
                                            >
                                                Analyze Status
                                            </Button>
                                        )
                                    )}
                                </TableCell>
                            </TableRow>
                        );
                    })}

                    {emptyRows > 0 && (
                        <TableRow style={{ height: 53 * emptyRows }}>
                            <TableCell colSpan={10} />
                        </TableRow>
                    )}
                </TableBody>
                <TableFooter>
                    <TableRow>
                        <TablePagination
                            rowsPerPageOptions={[5, 10, 25, { label: 'All', value: -1 }]}
                            colSpan={10}
                            count={suspiciousStatuses.length}
                            rowsPerPage={rowsPerPage}
                            page={page}
                            SelectProps={{
                                inputProps: {
                                    'aria-label': 'rows per page',
                                },
                                native: true,
                            }}
                            onPageChange={handleChangePage}
                            onRowsPerPageChange={handleChangeRowsPerPage}
                            ActionsComponent={TablePaginationActions}
                        />
                    </TableRow>
                </TableFooter>
            </Table>
        </TableContainer>
    );
}
