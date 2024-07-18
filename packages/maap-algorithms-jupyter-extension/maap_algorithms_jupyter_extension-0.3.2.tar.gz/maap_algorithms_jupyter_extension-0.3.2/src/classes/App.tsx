import React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { Provider } from 'react-redux';
import { JUPYTER_EXT } from '../constants';
import { store } from '../redux/store';
import 'regenerator-runtime/runtime';
import { AlgorithmsApp } from '../components/AlgorithmsApp';
import { RegistrationForm } from '../components/RegistrationForm';
import { JupyterFrontEnd } from '@jupyterlab/application';

export class AlgorithmCatalogWidget extends ReactWidget {
  jupyterApp: JupyterFrontEnd
  constructor(jupyterApp: JupyterFrontEnd) {
    super()
    this.addClass(JUPYTER_EXT.EXTENSION_CSS_CLASSNAME)
    this.jupyterApp = jupyterApp
  }

  render(): JSX.Element {
    return (
      <Provider store={store}>
        <AlgorithmsApp jupyterApp={this.jupyterApp}/>
      </Provider>
    )
  }
}

export class RegisterAlgorithmsWidget extends ReactWidget {
  data: any
  constructor(data: any) {
    super()
    this.addClass(JUPYTER_EXT.EXTENSION_CSS_CLASSNAME)
    this.data = data
  }

  render(): JSX.Element {
    return (
      <Provider store={store}>
        <RegistrationForm data={this.data} />
        {/* <Registering /> */}
      </Provider>
    )
  }
}
