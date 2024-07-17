import React, { useEffect, useState } from 'react';
import { PageConfig } from '@jupyterlab/coreutils';

export const CommonContext = React.createContext<CommonContextType | null>(null);

const CommonProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
     const currentUserOwner = PageConfig.getOption('serverRoot').split('/')[2] || ""
     const [currentUser, setCurrentUser] = useState<string>(currentUserOwner)

     useEffect(() => {
          setCurrentUser(PageConfig.getOption('serverRoot').split('/')[2] || "")
     }, []);

     return (
          <CommonContext.Provider value={{ currentUser }} >
               {children}
          </CommonContext.Provider>
     );
}

export default CommonProvider;