import { IAlgorithmSlice, IRegisteredAlgorithmsSlice, ISplitPaneSlice } from "./slices"

export interface IStore {
  Algorithm: IAlgorithmSlice
  SplitPane: ISplitPaneSlice
  RegisteredAlgorithms: IRegisteredAlgorithmsSlice
}
