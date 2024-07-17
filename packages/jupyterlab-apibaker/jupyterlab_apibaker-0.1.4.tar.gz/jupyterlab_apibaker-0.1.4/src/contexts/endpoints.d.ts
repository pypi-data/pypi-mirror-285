import { IEndpoint } from "../common/types";

type EndpointsContextType = {
     endpoints: IEndpoint[];
     getEndpoints: () => Promise<any>;
};

