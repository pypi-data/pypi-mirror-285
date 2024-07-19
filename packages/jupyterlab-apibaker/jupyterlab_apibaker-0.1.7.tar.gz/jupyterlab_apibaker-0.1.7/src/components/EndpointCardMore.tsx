import * as React from 'react';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import IconButton from '@mui/material/IconButton';
import { FiMoreVertical } from "react-icons/fi";
import { Button, CssBaseline, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, ListItemIcon, ListItemText } from '@mui/material';
import { MdEdit } from "react-icons/md";
import { MdDeleteOutline } from "react-icons/md";
import { requestAPI } from '../common/requestAPI';
import EndpointDetails from './EndpointDetailsDialogWithTabsComponent';
import { PageConfig } from '@jupyterlab/coreutils';
import { IEndpoint } from '../common/types';

interface EndpointCardMoreProps {
     endp: IEndpoint
     getEndpoints: () => void
}

const EndpointCardMore: React.FC<EndpointCardMoreProps> = (props): JSX.Element => {
     const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
     const [deleteDialogOpen, setDeleteDialogOpen] = React.useState<boolean>(false)
     const open = Boolean(anchorEl);
     const [openEndpointDetails, setOpenEndpointDetails] = React.useState(false);

     const handleEndpointDetailsClickOpen = () => {
          setOpenEndpointDetails(!openEndpointDetails);
          setAnchorEl(null)
     };

     const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
          setAnchorEl(event.currentTarget);
     };
     const handleClose = () => {
          setAnchorEl(null);
     };

     const handleDeleteDialogClick = async () => {
          setDeleteDialogOpen(!deleteDialogOpen);
          setAnchorEl(null)
     };

     const handleDeleteEndpoint = async () => {
          try {
               let deleteEndpoint = await requestAPI<any>("endpoint", {
                    method: "DELETE",
                    body: JSON.stringify({
                         endpoint_id: props.endp.id,
                         owner: PageConfig.getOption('serverRoot').split('/')[2] || ""
                    })
               })
               console.log(`Delete Endpoint Result => ${JSON.stringify(deleteEndpoint, null, 2)}`)
               props.getEndpoints()

               setDeleteDialogOpen(false)
          } catch (error) {
               console.log(`Error => ${JSON.stringify(error, null, 2)}`)
          }
     };

     console.log(`Endpoint Received in More => ${JSON.stringify(props.endp, null, 2)}`)
     return (
          <React.Fragment>
               <CssBaseline />
               <IconButton
                    aria-label="settings"
                    id="basic-button"
                    aria-controls={open ? 'card-more-action-menu' : undefined}
                    aria-haspopup="true"
                    aria-expanded={open ? 'true' : undefined}
                    onClick={handleClick}
               >
                    <FiMoreVertical />
               </IconButton>
               <Menu
                    id="card-more-actions-menu"
                    anchorEl={anchorEl}
                    open={open}
                    onClose={handleClose}
                    MenuListProps={{
                         'aria-labelledby': 'card-more-actions-button',
                    }}
               >
                    <MenuItem onClick={handleEndpointDetailsClickOpen}>
                         <ListItemIcon>
                              <MdEdit />
                         </ListItemIcon>
                         <ListItemText>Edit</ListItemText>
                    </MenuItem>
                    <MenuItem onClick={handleDeleteDialogClick}>
                         <ListItemIcon>
                              <MdDeleteOutline />
                         </ListItemIcon>
                         <ListItemText>Delete</ListItemText>
                    </MenuItem>
               </Menu>
               <Dialog
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
                              You are about to delete <strong>{props.endp.notebookName}</strong> endpoint and all its versions. <strong>This action can't be undone.</strong> Do you want to continue?
                         </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                         <Button onClick={handleDeleteDialogClick} autoFocus>No</Button>
                         <Button onClick={handleDeleteEndpoint} color='error'>Yes</Button>
                    </DialogActions>
               </Dialog>
               <EndpointDetails open={openEndpointDetails} handleClose={handleEndpointDetailsClickOpen} endpoint={props.endp} getEndpoints={props.getEndpoints}/>
          </React.Fragment>
     );
}

export default EndpointCardMore;
