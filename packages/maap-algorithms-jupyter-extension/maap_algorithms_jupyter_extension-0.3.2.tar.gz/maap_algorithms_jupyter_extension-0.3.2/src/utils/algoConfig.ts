import { store } from "../redux/store";
import yaml from 'js-yaml';
import { algorithm_config_template } from "../templates/algorithm_config";
import { IAlgorithmConfig } from "../types/index";
import { IInputParam } from "src/types/slices";
import {registerUsingFile } from "./api";
import { algorithmSlice } from "../redux/slices/algorithmSlice";


export async function registerAlgorithm() {
    const state = store.getState();
    const storeData = state.Algorithm

    // Populate algorithm config yaml template with data pulled from store
    let data: IAlgorithmConfig = yaml.load(algorithm_config_template) as IAlgorithmConfig

    data.algorithm_description = storeData.algoDesc
    data.algorithm_name = storeData.algoName
    data.algorithm_version = storeData.repoBranch
    data.disk_space = storeData.algoDiskSpace + "GB" // maap-py request expects units in value string
    data.docker_container_url = storeData.algoContainer
    data.repository_url = storeData.repoUrl
    data.run_command = storeData.repoRunCommand
    data.build_command = storeData.repoBuildCommand
    data.queue = storeData.algoResource.value

    // Collect the file, config, and positional inputs
    data.inputs.file = _parseInputs(storeData.fileData)
    data.inputs.config = _parseInputs(storeData.configData)
    data.inputs.positional = _parseInputs(storeData.positionalData)


    console.log("Algo config:")
    let algo_data = JSON.stringify(data)

    // Pass the algo config file
    let response = await registerUsingFile(data.algorithm_name + ".yml", algo_data)

    console.log(response)
    // update state
    store.dispatch(algorithmSlice.actions.setRegistrationUrl(response))

    return true
}

function _parseInputs(inputType: IInputParam[]) {
    let tmpArr = []
    inputType.map((input) => {
        let tmpObj = {}
        tmpObj = { name: input.inputName,
                   required: input.isRequired,
                   default: input.inputDefault,
                   description: input.inputDesc}
        tmpArr.push(tmpObj)
    })
    return tmpArr
}