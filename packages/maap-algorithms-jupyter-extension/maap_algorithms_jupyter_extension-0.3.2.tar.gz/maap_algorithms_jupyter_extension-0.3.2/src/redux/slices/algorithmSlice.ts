import { createSlice } from '@reduxjs/toolkit'
import { IAlgorithmSlice } from '../../types/slices'
import { IStore } from '../../types/store'

const initialState: IAlgorithmSlice = {
  positionalData: [],
  configData: [],
  fileData: [],
  repoUrl: "",
  repoBranch: "",
  repoRunCommand: "",
  repoBuildCommand: "",
  algoName: "",
  algoDesc: "",
  algoDiskSpace: "",
  algoResource: "",
  algoContainer: "",
  inputId: 0,
  registrationUrl: ""
}

export const algorithmSlice = createSlice({
  name: 'Algorithm',
  initialState,
  reducers: {
    resetValue: () => initialState,

    setRegistrationUrl: (state, action): any => {
      state.registrationUrl = action.payload
    },

    incrementInputId: (state): any => {
      state.inputId = state.inputId + 1
    },

    setRepoUrl: (state, action): any => {
      state.repoUrl = action.payload
    },

    setRepoBranch: (state, action): any => {
      state.repoBranch = action.payload
    },

    setRepoRunCommand: (state, action): any => {
      state.repoRunCommand = action.payload
    },

    setRepoBuildCommand: (state, action): any => {
      state.repoBuildCommand = action.payload
    },

    setAlgoName: (state, action): any => {
      state.algoName = action.payload
    },

    setAlgoDesc: (state, action): any => {
      state.algoDesc = action.payload
    },

    setAlgoDiskSpace: (state, action): any => {
      state.algoDiskSpace = action.payload
    },

    setAlgoResource: (state, action): any => {
      state.algoResource = action.payload
    },

    setAlgoContainerURL: (state, action): any => {
      state.algoContainer = action.payload
    },

    addConfigData: (state, action): any => {
      state.configData = [...state.configData, action.payload]
    },

    updateConfigData: (state, action): any => {
      return  {
        ...state,
        configData: state.configData.map(item => item.inputId == action.payload.inputId ? {
            ...item,
            [action.payload.inputField]: action.payload.inputValue
          } : item)
      }
    },

    removeConfigData: (state, action): any => {
      let nextState = [...state.configData]
      nextState.map((item, index) => {
        if (item.inputId == action.payload.key) {
          nextState.splice(index, 1)
        }
      })

      return {
        ...state,
        configData: nextState
      }
    },

    addFileData: (state, action): any => {
      state.fileData = [...state.fileData, action.payload]
    },

    updateFileData: (state, action): any => {
      return  {
        ...state,
        fileData: state.fileData.map(item => item.inputId == action.payload.inputId ? {
            ...item,
            [action.payload.inputField]: action.payload.inputValue
          } : item)
      }
    },

    removeFileData: (state, action): any => {
      let nextState = [...state.fileData]
      nextState.map((item, index) => {
        if (item.inputId == action.payload.key) {
          nextState.splice(index, 1)
        }
      })

      return {
        ...state,
        fileData: nextState
      }
    },

    addPositionalData: (state, action): any => {
      state.positionalData = [...state.positionalData, action.payload]
    },

    updatePositionalData: (state, action): any => {
      return  {
        ...state,
        positionalData: state.positionalData.map(item => item.inputId == action.payload.inputId ? {
            ...item,
            [action.payload.inputField]: action.payload.inputValue
          } : item)
      }
    },

    removePositionalData: (state, action): any => {
      let nextState = [...state.positionalData]
      nextState.map((item, index) => {
        if (item.inputId == action.payload.key) {
          nextState.splice(index, 1)
        }
      })

      return {
        ...state,
        positionalData: nextState
      }
    },
  },
})

// Actions
export const algorithmActions = algorithmSlice.actions

// Selector
export const selectAlgorithm = (state: IStore): IAlgorithmSlice => state.Algorithm

export default algorithmSlice.reducer
