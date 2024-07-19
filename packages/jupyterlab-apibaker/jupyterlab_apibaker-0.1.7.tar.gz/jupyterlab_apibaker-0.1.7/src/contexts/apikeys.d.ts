import { IEndpoint } from "../common/types";

type APIKeysContextType = {
     apiKeys?: IEndpoint;
     getAPIKeys: () => Promise<void>;
};

