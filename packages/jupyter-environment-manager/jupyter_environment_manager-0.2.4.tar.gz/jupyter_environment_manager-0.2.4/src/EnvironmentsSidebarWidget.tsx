import React from 'react';

import { ReactWidget } from '@jupyterlab/apputils';

import EnvironmentsSidebar from './components/EnvironmentsSidebar';
import { JupyterFrontEnd } from '@jupyterlab/application';

// TODO: Argument 'flux' should be typed with a non-any type
export class EnvironmentsSidebarWidget extends ReactWidget {
  flux: any;
  app: JupyterFrontEnd;

  constructor(flux: any, app: JupyterFrontEnd) {
    super();
    this.flux = flux;
    this.app = app;
  }

  render(): JSX.Element | null {
    return <EnvironmentsSidebar flux={this.flux} app={this.app} />;
  }
}
