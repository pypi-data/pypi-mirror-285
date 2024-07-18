import { configureStore } from '@reduxjs/toolkit'
import algorithmReducer from './slices/algorithmSlice'
import registeredAlgorithms from './slices/registeredAlgorithms'
import splitPaneReducer from './slices/splitPaneSlice'

export const store = configureStore({
  reducer: {
    Algorithm: algorithmReducer,
    RegisteredAlgorithms: registeredAlgorithms,
    SplitPane: splitPaneReducer
  },
  devTools: true,
})