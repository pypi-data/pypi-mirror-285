import React from 'react';
import { CssBaseline, Grid, Card, CardHeader, CardContent, CardActions, IconButton, InputLabel, Typography, TextField, InputAdornment, styled, Tooltip, Snackbar } from '@mui/material';
// import { CssBaseline, Grid, Card, CardHeader, CardContent, CardActions, IconButton, InputLabel, Typography, TextField, InputAdornment, styled, Tooltip, Snackbar, Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';
import { MdAutorenew } from "react-icons/md";
import { MdDeleteOutline } from "react-icons/md";
// import { IAPIKey } from '../common/types';
import copyToSystem from '../common/copyToClipboard';
import { IoCopyOutline } from 'react-icons/io5';
import { IAPIKey } from '../common/types';

interface APICardProps {
     apk: IAPIKey
     handleRefreshClick: (event: React.MouseEvent<HTMLElement>, apiKeyId: number) => void
     handleDeleteClick: (event: React.MouseEvent<HTMLElement>, apiKeyId: number) => void
}

const APIKeyInfoComponent: React.FC<APICardProps> = (props): JSX.Element => {

     // const [deleteDialogOpen, setDeleteDialogOpen] = React.useState<boolean>(false)
     const [snackbarOpen, setSnackbarOpen] = React.useState<boolean>(false);
     const [apiKeyToCopy, setAPIKeyToCopy] = React.useState('');

     React.useEffect(() => {
          setAPIKeyToCopy(apiKeyToCopy)
     }, [apiKeyToCopy])

     const IconButtonWithTooltip = styled(IconButton)({
          root: {
               '&.Mui-disabled': {
                    pointerEvents: 'auto',
               },
          },
     })

     const AlignedInputAdornment = styled(InputAdornment)({
          margin: '0 auto', // fix for vertically unaligned icon
     });

     const handleCopyToClipboard = () => {
          try {
               copyToSystem(apiKeyToCopy as string)
               setSnackbarOpen(true)
          } catch (error) {
               console.log(`Error copying to clipboard => ${JSON.stringify(error, null, 2)}`)
          }
     }

     return (
          <React.Fragment>
               <CssBaseline />
               <Grid item key={props.apk.id} xs={12}>
                    <Card>
                         <CardHeader
                              title={props.apk.apiKeyName}>
                         </CardHeader>
                         <CardContent>
                              <InputLabel>
                                   <Typography variant='subtitle2'>
                                        API Key
                                   </Typography>
                              </InputLabel>
                              <TextField
                                   disabled
                                   variant='outlined'
                                   value={props.apk.apiKey}
                                   sx={{ width: '100%' }}
                                   InputProps={{
                                        endAdornment: (
                                             <AlignedInputAdornment position="end">
                                                  <Tooltip title="Copy API Key">
                                                       <IconButtonWithTooltip role={'button'} onClick={handleCopyToClipboard}>
                                                            <IoCopyOutline />
                                                       </IconButtonWithTooltip>
                                                  </Tooltip>
                                             </AlignedInputAdornment>
                                        ),
                                   }}
                              />
                              <Snackbar
                                   open={snackbarOpen}
                                   onClose={() => setSnackbarOpen(false)}
                                   autoHideDuration={2000}
                                   message="Copied to clipboard"
                              />
                              <Typography variant='body1' marginTop={1}> {props.apk.description}</Typography>
                              <Typography variant='body1' marginTop={1}>Expires: {props.apk.expiresAt.toString()}</Typography>
                         </CardContent>
                         <CardActions>
                              <IconButton onClick={(e) => props.handleRefreshClick(e, props.apk.id)}>
                                   <MdAutorenew />
                              </IconButton>
                              {
                                   props.apk.apiKeyName === 'Default' ?
                                        '' :
                                        <IconButton onClick={(e) => props.handleDeleteClick(e, props.apk.id)}>
                                             <MdDeleteOutline />
                                        </IconButton>
                              }
                         </CardActions>
                    </Card>
                    {/* <Dialog
                         open={deleteDialogOpen}
                         onClose={handleDeleteDialogClick}
                         aria-labelledby="delete-endpoint-dialog"
                         aria-describedby="delete-dialog-description"
                    >
                         <DialogTitle id="delete-endpoint-dialog">
                              {"Delete endpoint?"}
                         </DialogTitle>
                         <DialogContent>
                              <DialogContentText id="delete-dialog-description">
                                   You are about to delete <strong>{props.notebookName}</strong> endpoint and all its versions. <strong>This action can't be undone.</strong> Do you want to continue?
                              </DialogContentText>
                         </DialogContent>
                         <DialogActions>
                              <Button onClick={handleDeleteDialogClick} autoFocus>No</Button>
                              <Button onClick={handleDeleteEndpoint} color='error'>Yes</Button>
                         </DialogActions>
                    </Dialog> */}
               </Grid>
          </React.Fragment >
     )
}

export default APIKeyInfoComponent;
