import React, { useEffect, useState } from 'react';
import { requestAPI } from '../common/requestAPI'
import { IEndpoint, IEndpointListResponse } from '../common/types';
import { EndpointsContextType } from './endpoints';
import { PageConfig } from '@jupyterlab/coreutils';

export const EndpointContext = React.createContext<EndpointsContextType | null>(null);

const EndpointProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
     const [endpoints, setEndpoints] = useState<IEndpoint[]>([])

     useEffect(() => {
          getEndpoints()
     }, []);

     const getEndpoints = async (): Promise<void> => {
          const currentUserOwner = PageConfig.getOption('serverRoot').split('/')[2] || ""
          const ownedEndpointsList = await requestAPI<any>("endpoint?owner=" + encodeURIComponent(currentUserOwner));
          console.log(`Owned Endpoints => ${JSON.stringify(ownedEndpointsList, null, 2)}`)
          const parsedOwnedEndpointsList: IEndpointListResponse = JSON.parse(ownedEndpointsList)
          setEndpoints(parsedOwnedEndpointsList.data)
     }

     return (
          <EndpointContext.Provider value={{ endpoints, getEndpoints }} >
               {children}
          </EndpointContext.Provider>
     );
}

export function useEndopintsContext() {
     const context = React.useContext(EndpointContext)
     if (!context) {
          throw new Error("useEndpointsContext must be used within a EndpointProvider")
     }
     return context
}

export default EndpointProvider;