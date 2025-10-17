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
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Tooltip from '@mui/material/Tooltip';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
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
        padding: '8px 6px',
        fontSize: '0.75rem',
    },
    [`&.${tableCellClasses.body}`]: {
        fontSize: 12,
        padding: '6px 4px',
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
    const [dialogOpen, setDialogOpen] = useState(false);
    const [dialogContent, setDialogContent] = useState({ text: '', model: '', confidence: null, isSuspicious: null });
    const [contentDialogOpen, setContentDialogOpen] = useState(false);
    const [selectedContent, setSelectedContent] = useState({ text: '', author: '', date: '', url: '' });

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

    const handleOpenDialog = (text, model, confidence, isSuspicious) => {
        setDialogContent({
            text,
            model: MODEL_CONFIGS[model]?.label || model,
            confidence,
            isSuspicious
        });
        setDialogOpen(true);
    };

    const handleCloseDialog = () => {
        setDialogOpen(false);
    };

    const handleOpenContentDialog = (content, author, date, url) => {
        setSelectedContent({
            text: content,
            author: author,
            date: date,
            url: url
        });
        setContentDialogOpen(true);
    };

    const handleCloseContentDialog = () => {
        setContentDialogOpen(false);
    };

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

        const previewText = response ? response.substring(0, 100) + (response.length > 100 ? '...' : '') : '';
        const streamPreview = partialStream ? partialStream.substring(0, 100) + (partialStream.length > 100 ? '...' : '') : '';

        return (
            <TableCell
                style={{
                    minWidth: 180,
                    maxWidth: 220,
                    verticalAlign: "top",
                    padding: '6px 4px'
                }}
                align="left"
            >
                <Box>
                    {response ? (
                        <Box>
                            <Box sx={{display: 'flex', gap: 0.3, mb: 0.5, alignItems: 'center', flexWrap: 'wrap'}}>
                                <Tooltip title={config.label}>
                                    <Chip
                                        label={config.icon}
                                        size="small"
                                        sx={{
                                            backgroundColor: config.color,
                                            color: 'white',
                                            fontSize: '0.65rem',
                                            height: '18px',
                                            minWidth: '24px',
                                            '& .MuiChip-label': {
                                                padding: '0 4px'
                                            }
                                        }}
                                    />
                                </Tooltip>
                                {confidence !== null && confidence !== undefined && (
                                    <Tooltip title="Confidence">
                                        <Chip
                                            label={`${(confidence * 100).toFixed(0)}%`}
                                            size="small"
                                            color={confidence > 0.7 ? "success" : confidence > 0.5 ? "warning" : "default"}
                                            sx={{
                                                fontSize: '0.65rem',
                                                height: '18px',
                                                '& .MuiChip-label': {
                                                    padding: '0 4px'
                                                }
                                            }}
                                        />
                                    </Tooltip>
                                )}
                                {isSuspicious !== null && isSuspicious !== undefined && (
                                    <Chip
                                        label={isSuspicious ? "⚠️" : "✓"}
                                        size="small"
                                        color={isSuspicious ? "error" : "success"}
                                        sx={{
                                            fontSize: '0.65rem',
                                            height: '18px',
                                            minWidth: '24px',
                                            '& .MuiChip-label': {
                                                padding: '0 4px'
                                            }
                                        }}
                                    />
                                )}
                            </Box>
                            <Box
                                onClick={() => handleOpenDialog(response, model, confidence, isSuspicious)}
                                sx={{
                                    maxHeight: 80,
                                    overflow: 'hidden',
                                    p: 0.5,
                                    border: '1px solid #e0e0e0',
                                    borderRadius: 0.5,
                                    backgroundColor: '#f9f9f9',
                                    fontSize: '0.7rem',
                                    wordBreak: 'break-word',
                                    cursor: 'pointer',
                                    '&:hover': {
                                        backgroundColor: '#f0f0f0',
                                        borderColor: config.color
                                    },
                                    '& p': {margin: '2px 0'},
                                    '& ul, & ol': {margin: '2px 0', paddingLeft: '16px'},
                                    '& li': {margin: '1px 0'}
                                }}
                            >
                                <ReactMarkdown>{previewText}</ReactMarkdown>
                                {response.length > 100 && (
                                    <Box sx={{
                                        color: config.color,
                                        fontSize: '0.6rem',
                                        fontWeight: 'bold',
                                        mt: 0.5,
                                        textAlign: 'center'
                                    }}>
                                        Click to view full response
                                    </Box>
                                )}
                            </Box>
                        </Box>
                    ) : partialStream ? (
                        <Box>
                            <Box sx={{display: 'flex', gap: 0.3, mb: 0.5, alignItems: 'center'}}>
                                <Chip
                                    label={config.icon}
                                    size="small"
                                    sx={{
                                        backgroundColor: config.color,
                                        color: 'white',
                                        fontSize: '0.65rem',
                                        height: '18px',
                                        minWidth: '24px',
                                        '& .MuiChip-label': {
                                            padding: '0 4px'
                                        }
                                    }}
                                />
                                <CircularProgress size={12}/>
                            </Box>
                            <Box sx={{
                                maxHeight: 80,
                                overflow: 'hidden',
                                p: 0.5,
                                border: '1px solid #e0e0e0',
                                borderRadius: 0.5,
                                backgroundColor: '#f9f9f9',
                                fontSize: '0.7rem',
                                wordBreak: 'break-word',
                                '& p': {margin: '2px 0'},
                                '& ul, & ol': {margin: '2px 0', paddingLeft: '16px'},
                                '& li': {margin: '1px 0'}
                            }}>
                                <ReactMarkdown>{streamPreview}</ReactMarkdown>
                            </Box>
                        </Box>
                    ) : (
                        <Button
                            variant="outlined"
                            size="small"
                            onClick={() => handleFetchLLM(row.id, model)}
                            disabled={isLoading}
                            startIcon={isLoading ? <CircularProgress size={10}/> : null}
                            sx={{
                                borderColor: config.color,
                                color: config.color,
                                fontSize: '0.65rem',
                                padding: '2px 6px',
                                minWidth: '70px',
                                '&:hover': {
                                    borderColor: config.color,
                                    backgroundColor: `${config.color}10`
                                }
                            }}
                        >
                            {isLoading ? 'Loading' : `${config.icon}`}
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
                <Box sx={{display: 'flex', gap: 0.5}}>
                    {Object.entries(MODEL_CONFIGS).map(([key, config]) => (
                        <Chip
                            key={key}
                            label={`${config.icon} ${config.label}`}
                            size="small"
                            sx={{
                                backgroundColor: config.color,
                                color: 'white',
                                fontSize: '0.7rem',
                                height: '24px'
                            }}
                        />
                    ))}
                </Box>
                <Button
                    variant="contained"
                    size="small"
                    onClick={getSuspiciousStatusesData}
                    sx={{fontSize: '0.75rem'}}
                >
                    Refresh
                </Button>
            </Box>

            <TableContainer component={Paper} sx={{maxHeight: 'calc(100vh - 200px)'}}>
                <Table stickyHeader sx={{minWidth: 500}} aria-label="custom pagination table">
                    <TableHead>
                        <TableRow>
                            <StyledTableCell align="left" sx={{width: 80}}>Date</StyledTableCell>
                            <StyledTableCell align="left" sx={{width: 40}}>Lang</StyledTableCell>
                            <StyledTableCell align="left" sx={{width: 50}}>Link</StyledTableCell>
                            <StyledTableCell align="left" sx={{minWidth: 150, maxWidth: 200}}>Content</StyledTableCell>
                            <StyledTableCell align="left" sx={{width: 100}}>Author</StyledTableCell>
                            <StyledTableCell align="left" sx={{minWidth: 180, maxWidth: 220}}>🤖 GPT</StyledTableCell>
                            <StyledTableCell align="left" sx={{minWidth: 180, maxWidth: 220}}>🧠 Claude</StyledTableCell>
                            <StyledTableCell align="left" sx={{minWidth: 180, maxWidth: 220}}>✨ Gemini</StyledTableCell>
                            <StyledTableCell align="left" sx={{minWidth: 180, maxWidth: 220}}>🦙 Llama</StyledTableCell>
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
                                        <Box sx={{fontSize: '0.65rem', whiteSpace: 'nowrap'}}>
                                            <div>{new Date(row.created_at).toLocaleTimeString([], {
                                                hour: '2-digit',
                                                minute: '2-digit',
                                            })}</div>
                                            <div>{new Date(row.created_at).toLocaleDateString("en-CA").slice(5)}</div>
                                        </Box>
                                    </TableCell>
                                    <TableCell align="left">
                                        <Box sx={{fontSize: '0.65rem'}}>
                                            {row.language}
                                        </Box>
                                    </TableCell>
                                    <TableCell align="left">
                                        <a
                                            href={row.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            style={{fontSize: '0.65rem'}}
                                        >
                                            View
                                        </a>
                                    </TableCell>
                                    <TableCell align="left">
                                        <Box
                                            onClick={() => handleOpenContentDialog(
                                                row.content,
                                                `👥 ${row.author_followers_count} | ➡️ ${row.author_following_count} | 📝 ${row.author_statuses_count}`,
                                                row.created_at,
                                                row.url
                                            )}
                                            sx={{
                                            maxHeight: 80,
                                            overflow: 'hidden',
                                            fontSize: '0.65rem',
                                            wordBreak: 'break-word',
                                            whiteSpace: 'pre-wrap',
                                            cursor: 'pointer',
                                            padding: '4px',
                                            borderRadius: '4px',
                                            '&:hover': {
                                                backgroundColor: '#f0f0f0',
                                                border: '1px solid #1976d2'
                                            }
                                        }}>
                                            {row.content}
                                        </Box>
                                    </TableCell>
                                    <TableCell align="left">
                                        <Box sx={{fontSize: '0.6rem', lineHeight: 1.3}}>
                                            <div>👥 {row.author_followers_count}</div>
                                            <div>➡️ {row.author_following_count}</div>
                                            <div>📝 {row.author_statuses_count}</div>
                                            <div>📅 {new Date(row.author_created_at).toLocaleDateString("en-CA").slice(2)}</div>
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

            {/* Dialog для полного просмотра ответа LLM */}
            <Dialog
                open={dialogOpen}
                onClose={handleCloseDialog}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    backgroundColor: '#f5f5f5'
                }}>
                    <span>LLM Analysis - {dialogContent.model}</span>
                    {dialogContent.confidence !== null && dialogContent.confidence !== undefined && (
                        <Chip
                            label={`Confidence: ${(dialogContent.confidence * 100).toFixed(0)}%`}
                            size="small"
                            color={dialogContent.confidence > 0.7 ? "success" : dialogContent.confidence > 0.5 ? "warning" : "default"}
                        />
                    )}
                    {dialogContent.isSuspicious !== null && dialogContent.isSuspicious !== undefined && (
                        <Chip
                            label={dialogContent.isSuspicious ? "Suspicious ⚠️" : "Not Suspicious ✓"}
                            size="small"
                            color={dialogContent.isSuspicious ? "error" : "success"}
                        />
                    )}
                </DialogTitle>
                <DialogContent dividers sx={{
                    '& p': { marginBottom: 2 },
                    '& ul, & ol': { marginLeft: 2, marginBottom: 2 },
                    '& li': { marginBottom: 1 },
                    '& h1, & h2, & h3': { marginTop: 2, marginBottom: 1 }
                }}>
                    <ReactMarkdown>{dialogContent.text}</ReactMarkdown>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog} variant="contained">
                        Close
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Dialog для просмотра полного контента */}
            <Dialog
                open={contentDialogOpen}
                onClose={handleCloseContentDialog}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 1,
                    backgroundColor: '#f5f5f5'
                }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span>Status Content</span>
                        <a
                            href={selectedContent.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ fontSize: '0.85rem', textDecoration: 'none' }}
                        >
                            View Original 🔗
                        </a>
                    </Box>
                    <Box sx={{ fontSize: '0.75rem', color: '#666' }}>
                        <div>{selectedContent.author}</div>
                        <div>{selectedContent.date ? new Date(selectedContent.date).toLocaleString() : ''}</div>
                    </Box>
                </DialogTitle>
                <DialogContent dividers sx={{
                    fontSize: '0.9rem',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    lineHeight: 1.5
                }}>
                    {selectedContent.text}
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseContentDialog} variant="contained">
                        Close
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
}