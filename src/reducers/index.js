import { combineReducers } from 'redux';

import BookmarkReducer from './BookmarkReducer';
import CartReducer from './CartReducer';
import GeneralReducer from './GeneralReducer';

export default combineReducers({
  generalState: GeneralReducer,
  cartState: CartReducer,
  bookmarkState: BookmarkReducer,
});
