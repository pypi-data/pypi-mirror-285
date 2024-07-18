import { ALGO_INPUT_FIELDS } from "../constants"

export interface IRegisteredAlgorithmsSlice {
  algorithmsList: any[],
  algorithmsData: IAlgorithmData[],
  selectedAlgorithm: IAlgorithmData
}

export interface IAlgorithmSlice {
    configData: IInputParam[],
    fileData: IInputParam[],
    positionalData: IInputParam[],
    repoUrl: "",
    repoBranch: "",
    repoRunCommand: "",
    repoBuildCommand: "",
    algoName: "",
    algoDesc: "",
    algoDiskSpace: "",
    algoResource: any,
    algoContainer: "",
    inputId: number,
    registrationUrl: ""
  }

export interface ISplitPaneSlice {
  rowCount: number
}

export interface IInputParam {
  [ALGO_INPUT_FIELDS.INPUT_NAME] : string,
  [ALGO_INPUT_FIELDS.INPUT_DEFAULT]: string,
  [ALGO_INPUT_FIELDS.INPUT_DESC]: string,
  [ALGO_INPUT_FIELDS.IS_REQUIRED]: boolean,
  [ALGO_INPUT_FIELDS.INPUT_ID]: number
}


export interface IAlgorithmInput {
  id: String,
  title: String,
  maxOccurs: any,
  minOccurs: any,
  dataType: any,
  required: any,
  defaultValue: any
}


export interface IAlgorithmData {
  id: String,
  description: String,
  inputs: IAlgorithmInput[]
}