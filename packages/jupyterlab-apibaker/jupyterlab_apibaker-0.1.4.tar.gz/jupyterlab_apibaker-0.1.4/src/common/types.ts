import { PartialJSONValue } from "@lumino/coreutils";

export interface IError {
     code?: number;
     message?: string;
}

export interface INBFunction {
     functionName: string;
     functionCode: string;
}

export interface INotebookInfo {
     nbpythonVersion: string;
     nbfunctions: INBFunction[];
}

export interface IParsedNBResponse {
     statusCode: number;
     error?: IError;
     data: INotebookInfo;
}

export interface INotebookContentAndMetadata {
     nbName: string;
     nbRawName: string;
     nbRaw: PartialJSONValue;
     pathToNotebook: string;
}

export interface IEndpoint {
     id: number;
     functionName: string;
     description: string;
     notebookName: string;
     owner: string;
     filesPath: string;
     versions: IEndpointVersion[]
     apiKeys: IAPIKey[]
}

export interface IEndpointVersion {
     id: string;
     versionName: string;
     description: string;
     isActive: boolean;
     shortHash: string;
     status: string;
     jobs?: IImageCreationJob[];
     parameters?: IEndpointVersionParameter[];
}

export interface IImageCreationJob {
     id: number;
     jobId: string;
     stage: string;
     status: string;
     reason: string;
     trace: string;
}

export interface IEndpointVersionParameter {
     id: number;
     name: string;
     description: string;
}

export interface IAPIKey {
     id: number;
     apiKeyName: string;
     description: string;
     apiKey: string;
     createdAt: Date;
     updatedAt: Date;
     expiresAt: Date
     isAdmin: boolean;
     refreshCount: number;
}

export interface IAPIKeys extends Array<IAPIKey> { }
export interface IEndpoints extends Array<IEndpoint> { }

interface RequestResponse {
     statusCode: number;
     error?: IError;
}

export interface IEndpointResponse extends RequestResponse {
     data: IEndpoint;
}

export interface IEndpointListResponse extends RequestResponse {
     data: IEndpoint[];
}

export interface IImageUpdate extends RequestResponse {
     data: IEndpointVersion
}

export interface IAPIKeyResponse extends RequestResponse {
     data: IAPIKey
}

export interface IAPIKeyListResponse extends RequestResponse {
     data: IAPIKey[]
}