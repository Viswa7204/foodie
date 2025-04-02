import React from 'react';
import { LogBox } from "react-native";
import { Provider } from 'react-redux';
import Navigators from './src/navigators';
import { Store } from './src/Store';

LogBox.ignoreLogs(["Require cycle:"]);
export default () => (
  <Provider store={Store}>
    <Navigators />
  </Provider>
);
