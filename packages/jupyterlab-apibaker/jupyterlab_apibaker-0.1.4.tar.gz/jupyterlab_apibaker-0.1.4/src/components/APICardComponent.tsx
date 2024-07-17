import React from 'react';
import { Button, CardActions, Card, CardContent, Typography, CssBaseline, Stack, CardHeader } from '@mui/material';
import EndpointDetails from './EndpointDetailsDialogWithTabsComponent';
import EndpointCardMore from './EndpointCardMore';
import { useCurrentEndopintContext } from '../contexts/EndpointContext';
import { IEndpoint } from '../common/types';

interface APICardProps {
     endp: IEndpoint
     getEndpoints: () => void
}

const APICardComponent: React.FC<APICardProps> = (props): JSX.Element => {
     const { setCurrentEndpoint } = useCurrentEndopintContext()

     const [open, setOpen] = React.useState(false);

     const handleClickOpen = () => {
          setCurrentEndpoint(props.endp)
          setOpen(true);
     };

     const handleClose = () => {
          setOpen(false);
     };
     return (
          <React.Fragment>
               <CssBaseline />
               <Card key={props.endp.id} variant="outlined" sx={{ width: 450, height: 200 }}>
                    <CardHeader
                         action={
                              <EndpointCardMore endp={props.endp} getEndpoints={props.getEndpoints} />
                         }
                         title={props.endp.notebookName}
                         subheader={props.endp.functionName}
                    />
                    <CardContent>
                         <Stack
                              direction="row"
                              justifyContent="space-between"
                              alignItems="center"
                         >
                         </Stack>
                         <Typography variant="body2" color="text.secondary" noWrap paragraph>
                              {props.endp.description}
                         </Typography>
                    </CardContent>
                    <CardActions disableSpacing>
                         <Button size="small" onClick={handleClickOpen}>Open</Button>
                         <EndpointDetails open={open} handleClose={handleClose} endpoint={props.endp} getEndpoints={props.getEndpoints}/>
                    </CardActions>
               </Card>
          </React.Fragment>
     )
};

export default APICardComponent;