import * as React from 'react';
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
import {useEffect, useState} from "react";
import axios from "axios";
import TableHead from "@mui/material/TableHead";
import {TextField} from "@mui/material";

function TablePaginationActions(props) {
    const theme = useTheme();
    const {count, page, rowsPerPage, onPageChange} = props;

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
        <Box sx={{flexShrink: 0, ml: 2.5}}>
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


const StyledTableCell = styled(TableCell)(({theme}) => ({
    [`&.${tableCellClasses.head}`]: {
        backgroundColor: theme.palette.common.black,
        color: theme.palette.common.white,
    },
    [`&.${tableCellClasses.body}`]: {
        fontSize: 14,
    },
}));

export default function SuspiciousAccountsTable() {
    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(10);
    const [suspiciousAccounts, setSuspiciousAccounts] = useState([]);
    const [search, setSearch] = useState("");

    const getSuspiciousAccountsData = async (limit, instance) => {
        try {
            let parameters = "?limit=" + limit;
            if (instance !== null) {
                parameters += "&instance=" + instance
            }
            const data = await axios.get(
                "http://131.130.125.158/api/v1/accounts" + parameters
            );
            setSuspiciousAccounts(data.data.result);
        } catch (e) {
            console.log(e);
        }
    };

    useEffect(() => {
        getSuspiciousAccountsData(10000, null).then(r => null);
    }, []);

    // Avoid a layout jump when reaching the last page with empty rows.
    const emptyRows =
        page > 0 ? Math.max(0, (1 + page) * rowsPerPage - suspiciousAccounts.length) : 0;

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };


    return (
        <TableContainer component={Paper}>
            <TextField sx={{minWidth: 500}}
                       type="text"
                       placeholder="Filter: Mastodon Instance URL"
                       onChange={(e) => {
                           setSearch(e.target.value);
                       }}
            />
            <Table sx={{minWidth: 500}} aria-label="custom pagination table">
                <TableHead>
                    <TableRow>
                        <StyledTableCell align="left">Account ID</StyledTableCell>
                        <StyledTableCell align="left">Username</StyledTableCell>
                        <StyledTableCell align="left">Display Name</StyledTableCell>
                        <StyledTableCell align="left">Created At</StyledTableCell>
                        <StyledTableCell align="left">URL</StyledTableCell>
                        <StyledTableCell align="left">Instance Url</StyledTableCell>
                        <StyledTableCell align="left">Followers Count</StyledTableCell>
                        <StyledTableCell align="left">Following Count</StyledTableCell>
                        <StyledTableCell align="left">Statuses Count</StyledTableCell>
                        <StyledTableCell align="left">Last Status At</StyledTableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {(suspiciousAccounts.length > 0
                            ? suspiciousAccounts.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                            : suspiciousAccounts
                    ).filter((item) => {
                        if (search === "") {
                            return item;
                        } else if (item.instance_url && item.instance_url.toLowerCase().includes(search.toLowerCase())) {
                            return item;
                        }
                    })
                        .map((row) => (
                            <TableRow key={row.id}>
                                <TableCell style={{width: 160}} align="left">
                                    {row.id}
                                </TableCell>
                                <TableCell style={{width: 160}} align="left">
                                    {row.username}>
                                </TableCell>
                                <TableCell style={{width: 160}} align="left">
                                    {row.display_name}
                                </TableCell>
                                <TableCell style={{width: 160}} align="left">
                                    {row.created_at}
                                </TableCell>
                                <TableCell style={{width: 160}} align="left">
                                    <a href={row.url}>{row.url}</a>
                                </TableCell>
                                <TableCell style={{width: 160}} align="left">
                                    <a href={row.instance_url}>{row.instance_url}</a>
                                </TableCell>
                                <TableCell style={{width: 160}} align="left">
                                    {row.followers_count}
                                </TableCell>
                                <TableCell style={{width: 160}} align="left">
                                    {row.following_count}
                                </TableCell>
                                <TableCell style={{width: 160}} align="left">
                                    {row.statuses_count}
                                </TableCell>
                                <TableCell style={{width: 160}} align="left">
                                    {row.last_status_at}
                                </TableCell>
                            </TableRow>
                        ))}

                    {emptyRows > 0 && (
                        <TableRow style={{height: 53 * emptyRows}}>
                            <TableCell colSpan={6}/>
                        </TableRow>
                    )}
                </TableBody>
                <TableFooter>
                    <TableRow>
                        <TablePagination
                            rowsPerPageOptions={[5, 10, 25, 100, {label: 'All', value: -1}]}
                            colSpan={3}
                            count={suspiciousAccounts.length}
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