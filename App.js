import React from 'react';
import { Provider } from 'react-redux';
import Navigators from './src/navigators';
import { Store } from './src/Store';

export default () => (
  <Provider store={Store}>
    <Navigators />
  </Provider>
);
