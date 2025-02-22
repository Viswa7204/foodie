import { applyMiddleware, legacy_createStore as createStore } from 'redux';
import Reducers from './reducers';

const {thunk} = require("redux-thunk");

const Store = createStore(Reducers, applyMiddleware(thunk));

const getToken = () => Store?.getState()?.generalState?.token;

export { getToken, Store };

