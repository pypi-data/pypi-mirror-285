import { createSlice } from '@reduxjs/toolkit'
import { ISplitPaneSlice } from '../../types/slices'
import { IStore } from '../../types/store'

const initialState: ISplitPaneSlice = {
  rowCount: 10
}

export const splitPaneSlice = createSlice({
  name: 'SplitPane',
  initialState,
  reducers: {
    resetValue: () => initialState,

    updateSize: (state, action) => {
        state.rowCount = action.payload
      },

  },
})

// Actions
export const splitPaneActions = splitPaneSlice.actions

// Selector
export const selectSplitPane = (state: IStore): ISplitPaneSlice => state.SplitPane

export default splitPaneSlice.reducer
