import { IEndpoint } from "../common/types";

type EndpointContextType = {
     endpoint?: IEndpoint;
     setCurrentEndpoint: (setCurrentEndpoint: IEndpoint) => void;
};

