import React from 'react'
import { Button, CssBaseline, Grid, InputLabel, TextField } from '@mui/material';
import { IEndpoint } from '../common/types';

interface NewAPIKeyProps {
     endp: IEndpoint
     handleSubmit: (event: any) => void
     apiKeyNameError: boolean
     apiKeyDescription: string
     setAPIKeyDescription: (apiKeyDescription: string) => void
     apiKeyName: string
     setAPIKeyName: (apiKeyName: string) => void
     setAPIKeyNameError: (error: boolean) => void
}

const NewAPIKeyComponent: React.FC<NewAPIKeyProps> = (props): JSX.Element => {
     const _handleNameOnChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
          props.setAPIKeyName(event.target.value)
          const regex = /[^A-Za-z0-9_-]/;
          if (props.apiKeyName === '' || regex.test(props.apiKeyName)) {
               props.setAPIKeyNameError(true)
          } else {
               props.setAPIKeyNameError(false)
          }
     }

     return (
          <React.Fragment>
               <CssBaseline />
               <form onSubmit={props.handleSubmit} noValidate>
                    <InputLabel sx={{ whiteSpace: 'wrap' }}>To create a apiKey for the user you want to share the endpoint with, please, insert a name and, optionally, a description:</InputLabel>
                    <Grid
                         container
                         spacing={2}
                         direction='row'
                         justifyContent="left"
                         alignItems={'center'}
                         maxWidth={'1440px'}
                         width={'100%'}
                    >
                         <Grid item xs={12}>
                              <TextField
                                   id="name-input"
                                   name="name"
                                   variant='outlined'
                                   placeholder={"APIKey Name"}
                                   fullWidth
                                   required
                                   onChange={e => _handleNameOnChange(e)}
                                   error={props.apiKeyNameError}
                                   helperText={props.apiKeyNameError ? "Only letters, numbers, - and _ are allowed." : ""}
                                   type={"text"}
                                   value={props.apiKeyName}
                              />
                         </Grid>
                         <Grid item xs={12}>
                              <TextField
                                   id="description-input"
                                   name="description"
                                   variant='outlined'
                                   placeholder={"APIKey Description"}
                                   fullWidth
                                   onChange={e => props.setAPIKeyDescription(e.target.value)}
                                   value={props.apiKeyDescription}
                              />
                         </Grid>
                         <Grid item>
                              <Button variant="contained" color="primary" type="submit">
                                   Create
                              </Button>
                         </Grid>
                    </Grid>
               </form>
          </React.Fragment>
     )
}

export default NewAPIKeyComponent;
