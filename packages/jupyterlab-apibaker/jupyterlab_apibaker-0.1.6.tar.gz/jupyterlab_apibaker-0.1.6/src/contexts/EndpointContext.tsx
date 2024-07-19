import React, { useState } from 'react';
import { IEndpoint } from '../common/types';
import { EndpointContextType } from './endpoint';

export const CurrentEndpointContext = React.createContext<EndpointContextType | null>(null);

const CurrentEndpointProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
     const [endpoint, setEndpoint] = useState<IEndpoint>()

     const setCurrentEndpoint = (currentEndpoint: IEndpoint): void => {
          setEndpoint(currentEndpoint)
     }

     return (
          <CurrentEndpointContext.Provider value={{ endpoint, setCurrentEndpoint }} >
               {children}
          </CurrentEndpointContext.Provider>
     );
}

export function useCurrentEndopintContext() {
     const context = React.useContext(CurrentEndpointContext)
     if (!context) {
          throw new Error("useEndpointsContext must be used within a EndpointProvider")
     }
     return context
}

export default CurrentEndpointProvider;