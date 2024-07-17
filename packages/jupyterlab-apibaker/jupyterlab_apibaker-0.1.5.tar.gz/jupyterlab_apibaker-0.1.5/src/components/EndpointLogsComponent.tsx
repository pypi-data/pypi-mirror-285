import React from 'react';
import {
     CssBaseline,
     Typography,
     Grid,
     List,
     ListItemButton,
     ListItemText,
     Divider,
     IconButton,
     Dialog,
     AppBar,
     Toolbar,
     Slide,
     Select,
     SelectChangeEvent,
     DialogProps,
     DialogTitle,
     DialogContent,
     DialogContentText,
     MenuItem,
     TableContainer,
     Table,
     TableBody,
     TableRow,
     TableCell,
     tableCellClasses,
     InputLabel
} from '@mui/material';
// import { TbLogs } from 'react-icons/tb';
import { IoClose } from 'react-icons/io5';
import { TransitionProps } from '@mui/material/transitions';
import { IEndpoint } from '../common/types';
import { requestAPI } from '../common/requestAPI';

type EndpointInfoProps = {
     endpoint: IEndpoint
}

const Transition = React.forwardRef(function Transition(
     props: TransitionProps & {
          children: React.ReactElement;
     },
     ref: React.Ref<unknown>,
) {
     return <Slide direction="up" ref={ref} {...props} />;
});


const EndpointLogs: React.FC<EndpointInfoProps> = (props): JSX.Element => {
     const [logs, setLogs] = React.useState<any[]>([])
     const [open, setOpen] = React.useState(false);
     const [contentLog, setContentLog] = React.useState('');
     const [workflowName, setWorkflowName] = React.useState('');
     const [scroll, setScroll] = React.useState<DialogProps['scroll']>('paper');
     const [version, setVersion] = React.useState<string>('');

     React.useEffect(() => {
          setVersion(
               `${props.endpoint.versions.length > 0 ? props.endpoint.versions[0].id : ''
               }`
          );
          console.log(props.endpoint.versions)
          console.log(version)
          getWorkflows(`${props.endpoint.versions.length > 0 ? props.endpoint.versions[0].id : ''}`)
     }, []);

     const handleVersionChange = (event: SelectChangeEvent) => {
          event.preventDefault();
          setVersion(event.target.value as string);
          getWorkflows(event.target.value as string)
     };

     const handleClickOpen = (scrollType: DialogProps['scroll'], workflowName: string) => () => {
          console.log(`Workflow Name => ${workflowName}`)
          setOpen(true);
          setScroll(scrollType);
          getWorkflowLog(workflowName)
     };

     const handleClose = () => {
          setOpen(false);
     };

     const descriptionElementRef = React.useRef<HTMLElement>(null);
     React.useEffect(() => {
          if (open) {
               const { current: descriptionElement } = descriptionElementRef;
               if (descriptionElement !== null) {
                    descriptionElement.focus();
               }
          }
     }, [open]);

     const getWorkflows = async (version: string) => {
          try {
               console.log(props.endpoint)
               // TODO: Add Data type for Workflows and Logs
               let workflows = await requestAPI<any>("endpoint/workflows?owner=" + props.endpoint.owner + "&endpointId=" + props.endpoint.id + "&versionId=" + version, {
                    method: "GET",
               })
               console.log(`Endpoint Workflows Result => ${JSON.stringify(workflows, null, 2)}`)
               setLogs(workflows)
          } catch (error) {
               console.log(`Error => ${JSON.stringify(error, null, 2)}`)
          }

     }

     const getWorkflowLog = async (workflowName: string) => {
          try {
               console.log('From GetWokrflowLog')
               console.log(`URL => ${"endpoint/workflows/log?owner=" + props.endpoint.owner + "&endpointId=" + props.endpoint.id + "&versionId=" + version + "&workflowName=" + workflowName}`)
               let response = await requestAPI<any>("endpoint/workflows/log?owner=" + props.endpoint.owner + "&endpointId=" + props.endpoint.id + "&versionId=" + version + "&workflowName=" + workflowName, {
                    method: "GET",
               })
               console.log(`Endpoint Workflow log Result => ${response}`)
               setContentLog(response)
               setWorkflowName(workflowName)

          } catch (error) {
               console.log(`Error => ${JSON.stringify(error, null, 2)}`)
          }

     }
     return (
          <React.Fragment>
               <CssBaseline />
               <TableContainer >
                    <Table sx={{
                         maxWidth: '100vw', [`& .${tableCellClasses.root}`]: {
                              borderBottom: "none"
                         }
                    }} aria-label="endpoint-info">
                         <TableBody>
                              <TableRow>
                                   <TableCell align='left'>
                                        <InputLabel id="version-select-label">
                                             <Typography variant='body1' noWrap sx={{ fontSize: '20px' }}>
                                                  Version:
                                             </Typography>
                                        </InputLabel>
                                        <Select
                                             labelId="version-select-label"
                                             id="version-select"
                                             value={version}
                                             onChange={handleVersionChange}
                                             sx={{ width: 150 }}
                                        >
                                             {(props.endpoint.versions.length > 0) ? (
                                                  props.endpoint.versions.map((version) => (
                                                       <MenuItem key={version.id} value={version.id}>{version.versionName}</MenuItem>
                                                  ))) : (
                                                  <MenuItem key={0} value={0}>No version</MenuItem>
                                             )}
                                        </Select>
                                   </TableCell>
                              </TableRow>
                         </TableBody>
                    </Table>
               </TableContainer>
               <CssBaseline />
               <Grid item key={props.endpoint.id} xs={12}>
                    {
                         logs.length ? (
                              <List sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}>
                                   {
                                        logs.map((log, index) => {
                                             return (
                                                  <>
                                                       <ListItemButton key={index} alignItems="flex-start" onClick={handleClickOpen('paper', log.name)}>
                                                            <ListItemText
                                                                 primary={log.name}
                                                                 secondary={
                                                                      <React.Fragment>
                                                                           <Typography
                                                                                sx={{ display: 'inline' }}
                                                                                component="span"
                                                                                variant="body2"
                                                                                color="text.primary"
                                                                           >
                                                                                {log.phase}<br />
                                                                           </Typography>
                                                                           created at: {log.createdAt}<br />
                                                                           started at: {log.startedAt}<br />
                                                                           finished at: {log.finishedAt}
                                                                      </React.Fragment>
                                                                 }
                                                            />
                                                       </ListItemButton>
                                                       <Divider variant="inset" component="li" />
                                                  </>
                                             )
                                        })
                                   }
                              </List>)
                              : <Typography variant="subtitle1" gutterBottom>No logs were found.</Typography>
                    }
               </Grid>
               <Dialog
                    fullScreen
                    open={open}
                    onClose={handleClose}
                    TransitionComponent={Transition}
               >
                    <AppBar sx={{ position: 'relative' }}>
                         <Toolbar>
                              <IconButton
                                   edge="start"
                                   color="inherit"
                                   onClick={handleClose}
                                   aria-label="close"
                              >
                                   <IoClose />
                              </IconButton>
                              <Typography sx={{ ml: 2, flex: 1 }} variant="h6" component="div">
                                   LOGS
                              </Typography>
                         </Toolbar>
                    </AppBar>
                    <DialogTitle id="scroll-dialog-title">{workflowName}</DialogTitle>
                    <DialogContent dividers={scroll === 'paper'}>
                         <DialogContentText
                              id="scroll-dialog-description"
                              ref={descriptionElementRef}
                              tabIndex={-1}
                         >
                              <Typography variant="caption" display="block" gutterBottom style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                                   {contentLog}
                              </Typography>

                         </DialogContentText>
                    </DialogContent>
               </Dialog>
          </React.Fragment >
     )
};

export default EndpointLogs;
