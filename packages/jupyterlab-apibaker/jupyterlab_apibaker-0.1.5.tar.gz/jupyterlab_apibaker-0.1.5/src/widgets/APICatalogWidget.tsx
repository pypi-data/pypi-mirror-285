import { ReactWidget } from "@jupyterlab/apputils";
import React from 'react';
import { APICatalogComponent } from "../components/APICatalogComponent";
import EndpointProvider from "../contexts/EndpointsContext";
import CurrentEndpointProvider from "../contexts/EndpointContext";
import CommonProvider from "../contexts/CommonContext";

export class APICatalogWidget extends ReactWidget {
  constructor() {
    super()
  }

  render(): JSX.Element {
    return (
      <EndpointProvider>
        <CurrentEndpointProvider>
          <CommonProvider>
            <APICatalogComponent />
          </CommonProvider>
        </CurrentEndpointProvider>
      </EndpointProvider>
    )
  }
}