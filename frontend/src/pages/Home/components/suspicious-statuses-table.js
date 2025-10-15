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
import ButtonGroup from '@mui/material/ButtonGroup';
import ReactMarkdown from 'react-markdown';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Tooltip from '@mui/material/Tooltip';
import {green, red, grey, blue, purple, orange} from '@mui/material/colors';

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

const LLM_MODELS = {
    OPENAI: 'openai',
    CLAUDE: 'claude',
    GEMINI: 'gemini',
    LLAMA: 'llama'
};

const MODEL_CONFIGS = {
    [LLM_MODELS.OPENAI]: {
        label: 'GPT-4',
        color: green[600],
        icon: '🤖'
    },
    [LLM_MODELS.CLAUDE]: {
        label: 'Claude',
        color: purple[600],
        icon: '🧠'
    },
    [LLM_MODELS.GEMINI]: {
        label: 'Gemini',
        color: blue[600],
        icon: '✨'
    },
    [LLM_MODELS.LLAMA]: {
        label: 'Llama',
        color: orange[600],
        icon: '🦙'
    }
};

export default function SuspiciousStatusesTable() {
    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(5);
    const [suspiciousStatuses, setSuspiciousStatuses] = useState([]);

    const wsRef = useRef(null);

    const [streamBuffer, setStreamBuffer] = useState({});
    const [loadingStates, setLoadingStates] = useState({});

    const getSuspiciousStatusesData = async () => {
        try {
            const {data} = await axios.get(
                "http://0.0.0.0:8000/api/v1/statuses/suspicious?limit=10000"
            );
            setSuspiciousStatuses(data.results);
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        getSuspiciousStatusesData();
    }, []);

    useEffect(() => {
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    const handleFetchLLM = (statusId, model) => {
        const key = `${statusId}-${model}`;

        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.close();
            wsRef.current = null;
        }

        const ws = new WebSocket("ws://0.0.0.0:8000/ws");
        wsRef.current = ws;

        let accumulatedResponse = "";

        setLoadingStates(prev => ({
            ...prev,
            [key]: true
        }));

        ws.onopen = () => {
            console.log('WebSocket connected');
            ws.send(JSON.stringify({
                status_id: statusId.toString(),
                model: model
            }));
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.error) {
                    console.error("WebSocket error:", data.error);
                    setLoadingStates(prev => ({
                        ...prev,
                        [key]: false
                    }));
                    return;
                }

                if (data.type === 'start') {
                    console.log(`Starting analysis with ${data.model}...`);
                    accumulatedResponse = "";
                } else if (data.type === 'stream') {
                    accumulatedResponse = data.content;
                    setStreamBuffer((prev) => ({
                        ...prev,
                        [key]: accumulatedResponse,
                    }));
                } else if (data.type === 'complete') {
                    console.log(`Analysis complete! Confidence: ${data.confidence}, Is Suspicious: ${data.is_suspicious}`);

                    setSuspiciousStatuses((prev) =>
                        prev.map((item) => {
                            if (item.id === statusId) {
                                return {
                                    ...item,
                                    [`${model}_response`]: accumulatedResponse,
                                    [`${model}_confidence`]: data.confidence,
                                    [`${model}_is_suspicious`]: data.is_suspicious
                                };
                            }
                            return item;
                        })
                    );

                    setStreamBuffer((prev) => ({
                        ...prev,
                        [key]: accumulatedResponse,
                    }));

                    setLoadingStates(prev => ({
                        ...prev,
                        [key]: false
                    }));

                    if (ws.readyState === WebSocket.OPEN) {
                        ws.close();
                    }
                }
            } catch (e) {
                console.error('Parse error:', e);
                accumulatedResponse = event.data;
                setStreamBuffer((prev) => ({
                    ...prev,
                    [key]: accumulatedResponse,
                }));
            }
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
            setLoadingStates(prev => ({
                ...prev,
                [key]: false
            }));
        };

        ws.onclose = () => {
            console.log("WebSocket closed");
            setLoadingStates(prev => ({
                ...prev,
                [key]: false
            }));
            if (wsRef.current === ws) {
                wsRef.current = null;
            }
        };
    };

    const renderAnalysisCell = (row, model) => {
        const key = `${row.id}-${model}`;
        const response = row[`${model}_response`];
        const confidence = row[`${model}_confidence`];
        const isSuspicious = row[`${model}_is_suspicious`];
        const partialStream = streamBuffer[key] || "";
        const isLoading = loadingStates[key];
        const config = MODEL_CONFIGS[model];

        return (
            <TableCell
                style={{
                    minWidth: 300,
                    maxWidth: 400,
                    verticalAlign: "top"
                }}
                align="left"
            >
                <Box sx={{mb: 1}}>
                    {response ? (
                        <Box>
                            <Box sx={{display: 'flex', gap: 0.5, mb: 1, alignItems: 'center', flexWrap: 'wrap'}}>
                                <Chip
                                    label={`${config.icon} ${config.label}`}
                                    size="small"
                                    sx={{
                                        backgroundColor: config.color,
                                        color: 'white',
                                        fontSize: '0.7rem',
                                        height: '22px'
                                    }}
                                />
                                {confidence !== null && confidence !== undefined && (
                                    <Tooltip title="Confidence Level">
                                        <Chip
                                            label={`${(confidence * 100).toFixed(0)}%`}
                                            size="small"
                                            color={confidence > 0.7 ? "success" : confidence > 0.5 ? "warning" : "default"}
                                            sx={{fontSize: '0.7rem', height: '22px'}}
                                        />
                                    </Tooltip>
                                )}
                                {isSuspicious !== null && isSuspicious !== undefined && (
                                    <Chip
                                        label={isSuspicious ? "Suspicious" : "Legit"}
                                        size="small"
                                        color={isSuspicious ? "error" : "success"}
                                        sx={{fontSize: '0.7rem', height: '22px'}}
                                    />
                                )}
                            </Box>
                            <Box sx={{
                                maxHeight: 250,
                                overflow: 'auto',
                                p: 1,
                                border: '1px solid #e0e0e0',
                                borderRadius: 1,
                                backgroundColor: '#f9f9f9',
                                fontSize: '0.8rem',
                                wordBreak: 'break-word',
                                whiteSpace: 'pre-wrap'
                            }}>
                                <ReactMarkdown>{response}</ReactMarkdown>
                            </Box>
                        </Box>
                    ) : partialStream ? (
                        <Box>
                            <Box sx={{display: 'flex', gap: 0.5, mb: 1, alignItems: 'center', flexWrap: 'wrap'}}>
                                <Chip
                                    label={`${config.icon} ${config.label}`}
                                    size="small"
                                    sx={{
                                        backgroundColor: config.color,
                                        color: 'white',
                                        fontSize: '0.7rem',
                                        height: '22px'
                                    }}
                                />
                                <CircularProgress size={14}/>
                            </Box>
                            <Box sx={{
                                maxHeight: 250,
                                overflow: 'auto',
                                p: 1,
                                border: '1px solid #e0e0e0',
                                borderRadius: 1,
                                backgroundColor: '#f9f9f9',
                                fontSize: '0.8rem',
                                wordBreak: 'break-word',
                                whiteSpace: 'pre-wrap'
                            }}>
                                <ReactMarkdown>{partialStream}</ReactMarkdown>
                            </Box>
                        </Box>
                    ) : (
                        <Button
                            variant="outlined"
                            size="small"
                            onClick={() => handleFetchLLM(row.id, model)}
                            disabled={isLoading}
                            startIcon={isLoading ? <CircularProgress size={14}/> : null}
                            sx={{
                                borderColor: config.color,
                                color: config.color,
                                fontSize: '0.7rem',
                                '&:hover': {
                                    borderColor: config.color,
                                    backgroundColor: `${config.color}10`
                                }
                            }}
                        >
                            {isLoading ? 'Analyzing...' : `${config.icon} Analyze`}
                        </Button>
                    )}
                </Box>
            </TableCell>
        );
    };

    const emptyRows =
        page > 0
            ? Math.max(0, (1 + page) * rowsPerPage - suspiciousStatuses.length)
            : 0;

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    return (
        <>
            <Box sx={{display: 'flex', justifyContent: 'space-between', mb: 2, alignItems: 'center'}}>
                <Box sx={{display: 'flex', gap: 1}}>
                    {Object.entries(MODEL_CONFIGS).map(([key, config]) => (
                        <Chip
                            key={key}
                            label={`${config.icon} ${config.label}`}
                            sx={{backgroundColor: config.color, color: 'white'}}
                        />
                    ))}
                </Box>
                <Button variant="contained" onClick={getSuspiciousStatusesData}>
                    Refresh
                </Button>
            </Box>

            <TableContainer component={Paper} sx={{maxHeight: 'calc(100vh - 200px)'}}>
                <Table stickyHeader sx={{minWidth: 500}} aria-label="custom pagination table">
                    <TableHead>
                        <TableRow>
                            <StyledTableCell align="left" sx={{minWidth: 140}}>Created At</StyledTableCell>
                            <StyledTableCell align="left" sx={{width: 60}}>Lang</StyledTableCell>
                            <StyledTableCell align="left" sx={{minWidth: 100}}>Link</StyledTableCell>
                            <StyledTableCell align="left" sx={{minWidth: 250, maxWidth: 300}}>Content</StyledTableCell>
                            <StyledTableCell align="left" sx={{minWidth: 150}}>Author Info</StyledTableCell>
                            <StyledTableCell align="left" sx={{minWidth: 300}}>🤖 GPT-4</StyledTableCell>
                            <StyledTableCell align="left" sx={{minWidth: 300}}>🧠 Claude</StyledTableCell>
                            <StyledTableCell align="left" sx={{minWidth: 300}}>✨ Gemini</StyledTableCell>
                            <StyledTableCell align="left" sx={{minWidth: 300}}>🦙 Llama</StyledTableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {(suspiciousStatuses.length > 0
                                ? suspiciousStatuses.slice(
                                    page * rowsPerPage,
                                    page * rowsPerPage + rowsPerPage
                                )
                                : suspiciousStatuses
                        ).map((row) => {
                            return (
                                <TableRow key={row.id}>
                                    <TableCell align="left">
                                        <Box sx={{fontSize: '0.75rem', whiteSpace: 'nowrap'}}>
                                            <div>{new Date(row.created_at).toLocaleTimeString([], {
                                                hour: '2-digit',
                                                minute: '2-digit',
                                            })}</div>
                                            <div>{new Date(row.created_at).toLocaleDateString("en-CA")}</div>
                                        </Box>
                                    </TableCell>
                                    <TableCell align="left">
                                        <Box sx={{fontSize: '0.75rem'}}>
                                            {row.language}
                                        </Box>
                                    </TableCell>
                                    <TableCell align="left">
                                        <a
                                            href={row.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            style={{fontSize: '0.75rem'}}
                                        >
                                            View
                                        </a>
                                    </TableCell>
                                    <TableCell align="left">
                                        <Box sx={{
                                            maxHeight: 100,
                                            overflow: 'auto',
                                            fontSize: '0.75rem',
                                            wordBreak: 'break-word',
                                            whiteSpace: 'pre-wrap'
                                        }}>
                                            {row.content}
                                        </Box>
                                    </TableCell>
                                    <TableCell align="left">
                                        <Box sx={{fontSize: '0.7rem'}}>
                                            <div><strong>👥</strong> {row.author_followers_count}</div>
                                            <div><strong>➡️</strong> {row.author_following_count}</div>
                                            <div><strong>📝</strong> {row.author_statuses_count}</div>
                                            <div><strong>📅</strong> {new Date(row.author_created_at).toLocaleDateString("en-CA")}</div>
                                        </Box>
                                    </TableCell>
                                    {renderAnalysisCell(row, LLM_MODELS.OPENAI)}
                                    {renderAnalysisCell(row, LLM_MODELS.CLAUDE)}
                                    {renderAnalysisCell(row, LLM_MODELS.GEMINI)}
                                    {renderAnalysisCell(row, LLM_MODELS.LLAMA)}
                                </TableRow>
                            );
                        })}
                        {emptyRows > 0 && (
                            <TableRow style={{height: 53 * emptyRows}}>
                                <TableCell colSpan={9}/>
                            </TableRow>
                        )}
                    </TableBody>
                    <TableFooter>
                        <TableRow>
                            <TablePagination
                                rowsPerPageOptions={[5, 10, 25, {label: "All", value: -1}]}
                                colSpan={9}
                                count={suspiciousStatuses.length}
                                rowsPerPage={rowsPerPage}
                                page={page}
                                SelectProps={{
                                    inputProps: {
                                        "aria-label": "rows per page",
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
        </>
    );
}