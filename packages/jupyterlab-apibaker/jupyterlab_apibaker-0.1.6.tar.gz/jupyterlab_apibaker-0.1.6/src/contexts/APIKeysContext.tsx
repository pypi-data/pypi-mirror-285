import React, { useEffect, useState } from 'react';
import { requestAPI } from '../common/requestAPI'
import { IEndpoint, IEndpointResponse } from '../common/types';
import { APIKeysContextType } from './apikeys';

export const APIKeyContext = React.createContext<APIKeysContextType | null>(null);

const APIKeyProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
     const [apiKeys, setAPIKeys] = useState<IEndpoint>()

     useEffect(() => {
          getAPIKeys()
     }, []);

     const getAPIKeys = async (): Promise<void> => {
          const response = await requestAPI<IEndpointResponse>('api-keys?id=');
          setAPIKeys(response.data)
     }

     return (
          <APIKeyContext.Provider value={{ apiKeys, getAPIKeys }} >
               {children}
          </APIKeyContext.Provider>
     );
}

export default APIKeyProvider;