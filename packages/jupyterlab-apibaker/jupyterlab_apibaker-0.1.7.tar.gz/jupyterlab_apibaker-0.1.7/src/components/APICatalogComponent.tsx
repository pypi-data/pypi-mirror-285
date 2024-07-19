import React from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';
import { AppBar, Typography } from '@mui/material';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import APICardComponent from './APICardComponent';
import { EndpointContext } from '../contexts/EndpointsContext';
import { EndpointsContextType } from '../contexts/endpoints';

export const APICatalogComponent: React.FC = () => {
     const { endpoints, getEndpoints } = React.useContext(EndpointContext) as EndpointsContextType
     return (
          <Box
               display='flex'
               justifyContent='center'
               alignItems='flex-start'
               height={'100%'}
               width={'100%'}
          >
               <CssBaseline />
               <AppBar
                    position="fixed"
               >
                    <Toolbar>
                         <Typography variant="h6" noWrap component="div">
                              API Collection
                         </Typography>
                    </Toolbar>
               </AppBar>
               <Grid
                    container
                    spacing={2}
                    sx={{
                         paddingLeft: '20px',
                         paddingRight: '20px',
                         paddingTop: '20px',
                         overflow: 'auto',
                         maxHeight: '100%',
                         marginTop: '50px',
                         justifyContent: 'flex-start',
                         alignItems: "flex-start"
                    }}
               >
                    {endpoints.length === 0 ? (
                         <>
                              <Box
                                   width={'100%'}
                                   display="flex"
                                   flexDirection={'column'}
                                   alignItems="center"
                                   alignSelf={'center'}
                                   justifyContent={'center'}
                                   marginTop={10}
                              >
                                   <Typography variant='h5'>There are no endpoints to show</Typography>
                                   <Typography variant='body1'>You can create one by clicking on the "Bake API" button on any of your notebook's toolbar.</Typography>
                              </Box>
                         </>) : ''}
                    {endpoints.map((item) => (
                         <Grid key={item.id} item>
                              <APICardComponent endp={item} getEndpoints={getEndpoints} />
                         </Grid>
                    ))}
               </Grid>
          </Box >
     );
}
export default APICatalogComponent