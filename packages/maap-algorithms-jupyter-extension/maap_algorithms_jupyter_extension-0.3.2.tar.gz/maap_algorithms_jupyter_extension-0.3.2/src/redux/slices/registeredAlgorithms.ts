import { createSlice } from '@reduxjs/toolkit'
import { IRegisteredAlgorithmsSlice } from '../../types/slices'
import { IStore } from '../../types/store'

const initialState: IRegisteredAlgorithmsSlice = {
  algorithmsList: [],
  algorithmsData: [],
  selectedAlgorithm: {id: "", description: "", inputs: []}
}

export const registeredAlgorithmsSlice = createSlice({
  name: 'RegisteredAlgorithms',
  initialState,
  reducers: {
    resetValue: () => initialState,

    setAlgorithmsList: (state, action): any => {
      state.algorithmsList = action.payload
    },

    setAlgorithmsData: (state, action): any => {
      state.algorithmsData = action.payload
    },

    setSelectedAlgorithm: (state, action): any => {
      state.selectedAlgorithm = action.payload
      console.log(state.selectedAlgorithm)
    },

  },
})

// Actions
export const registeredAlgorithmsActions = registeredAlgorithmsSlice.actions

// Selector
export const selectRegisteredAlgorithms = (state: IStore): IRegisteredAlgorithmsSlice => state.RegisteredAlgorithms

export default registeredAlgorithmsSlice.reducer
