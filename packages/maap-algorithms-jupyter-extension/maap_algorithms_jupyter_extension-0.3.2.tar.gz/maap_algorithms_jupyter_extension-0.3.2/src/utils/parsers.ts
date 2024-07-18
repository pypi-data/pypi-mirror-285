import { IAlgorithmData, IAlgorithmInput } from "../types/slices"


const _parseAlgorithmInputs = (body: any) => {
    let inputs: IAlgorithmInput[] = []

    let tmpInputs = body["wps:ProcessOfferings"]["wps:ProcessOffering"]["wps:Process"]["wps:Input"]
    tmpInputs.forEach(tmpInput => {
        let input: IAlgorithmInput = {id: "", title: "", maxOccurs: "", minOccurs: "", dataType: "", required: "", defaultValue: ""}
        input.id = tmpInput["ows:Identifier"]
        input.title = tmpInput["ows:Title"]
        input.required = tmpInput["ns:LiteralData"]["ns:Format"]["@default"]
        input.minOccurs = tmpInput["@minOccurs"]
        input.maxOccurs = tmpInput["@maxOccurs"]
        input.defaultValue = tmpInput["ns:LiteralData"]["LiteralDataDomain"]["ows:AnyValue"]

        try {
            input.dataType = tmpInput["ns:LiteralData"]["LiteralDataDomain"]["ows:DataType"]["@ows:reference"]
        } catch {
            input.dataType = ""
        }

        inputs.push(input)
    });
    return inputs
}
  
  
const _parseAlgorithmDescription = (body: any) => {
    let description: String = body["wps:ProcessOfferings"]["wps:ProcessOffering"]["wps:Process"]["ows:Title"]
    return description
}


const _parseAlgorithmID = (body: any) => {
    let id: String = body["wps:ProcessOfferings"]["wps:ProcessOffering"]["wps:Process"]["ows:Identifier"]
    return id
}


export const parseAlgorithmData = (body: any) => {
    let algorithmData: IAlgorithmData = {id: "", description: "", inputs: []}
    body = JSON.parse(body)

    algorithmData.id = _parseAlgorithmID(body)
    algorithmData.description = _parseAlgorithmDescription(body)
    algorithmData.inputs = _parseAlgorithmInputs(body)

    return algorithmData
}