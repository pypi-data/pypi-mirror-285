import { PageConfig } from '@jupyterlab/coreutils';
import { IAlgorithmData } from '../types/slices';
import { registeredAlgorithmsActions } from '../redux/slices/registeredAlgorithms';
import { store } from "../redux/store";
import { parseAlgorithmData } from "./parsers" 


// export const getAlgorithmMetadata = (body: any) => {
//   let algorithmMetadata = {
//     description: '',
//     inputs: {}
//   }

//   //algorithmMetadata.description = _parseAlgoDesc(body)
//   algorithmMetadata.inputs = _parseAlgoInputs(body)

//   return algorithmMetadata
// }

export async function registerUsingFile(fileName: string, algo_data: any) {

  const response_file = await createFile(fileName, algo_data)
  console.log(response_file)

  if (response_file) {
    console.log("submitting register")
    const response_register = await register(response_file.file, null)
    const d = JSON.parse(response_register.response)
    console.log(d)
    console.log(d.message.job_web_url)
    return d.message.job_web_url
  }

  // // Create algorithm config file first
  // createFile(fileName, algo_data).then((data) => {
  //   register(data.file, null).then((res) => {
  //     console.log("in register res")
  //     let res_obj = JSON.parse(res.response)
  //     console.log(res_obj)
  //     console.log(res_obj.message.job_web_url)
  //     return res_obj.message.job_web_url
  //   })
  // }).finally((res) => {
  //   console.log(res)
  // })
}

export async function createFile(fileName: string, data: any) {
  var requestUrl = new URL(PageConfig.getBaseUrl() + 'jupyter-server-extension/createFile');
  console.log(requestUrl.href)

  requestUrl.searchParams.append("fileName", fileName);
  requestUrl.searchParams.append("data", data);

  try {
    const response: any = await fetch(requestUrl.href, {
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error('Request failed');
    }


    console.log("resolved")
    const r_data = await response.json();
    return r_data
  } catch (error) {
    console.log("error in new endpoint")
    console.log(error)
  }
}


export async function register(file: string, data: any) {
  console.log("registering....")

  if (data == null) {
    console.log("register using file")
    var requestUrl = new URL(PageConfig.getBaseUrl() + 'jupyter-server-extension/registerUsingFile');
    console.log(requestUrl.href)

    requestUrl.searchParams.append("file", file);

    try {
      const response: any = await fetch(requestUrl.href, {
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error('Request failed');
      }


      console.log("resolved register request")
      const r_data = await response.json();
      return r_data
    } catch (error) {
      console.log("error in new register endpoint")
      console.log(error)
    }

  } else {
    console.log("register with data")
  }

  // if (response.status >= 200 && response.status < 400) {
  //     console.log("request went well")
  //     return true
  //   }else{
  //     //let res = response.json()
  //     console.log("something went wrong with request!!!")
  //     return false
  //     //console.log(response.json())
  //   }
}


const filterOptions = (options, inputValue) => {
  const candidate = inputValue.toLowerCase();
  return options.filter(({ label }) => label.toLowerCase().includes(candidate));
};

export async function getResources(inputValue, callback) {
  var resources: any[] = []
  var requestUrl = new URL(PageConfig.getBaseUrl() + 'jupyter-server-extension/getQueues');
  await fetch(requestUrl.href, {
    headers: {
      'Content-Type': 'application/json'
    }
  }).then((response) => response.json())
    .then((data) => {

      data["response"].forEach((item: any) => {
        let resource: any = {}
        resource["value"] = item
        resource["label"] = item
        resources.push(resource)
      })
      const filtered = filterOptions(resources, inputValue);
      callback(filtered);
      return resources
    });
  return resources
}


export async function describeAlgorithms(algo_id: string) {
  var requestUrl = new URL(PageConfig.getBaseUrl() + 'jupyter-server-extension/describeAlgorithms');
  var body: any = {}

  requestUrl.searchParams.append("algo_id", algo_id);

  await fetch(requestUrl.href, {
    headers: { 'Content-Type': 'application/json' }
  }).then((response) => response.json())
    .then((data) => {
      console.log("Data before parsing: ")
      console.log(data)
      body = parseAlgorithmData(data["response"])
      console.log(data)
      return body
    })
  return body
}



export async function getAlgorithms() {
  let algorithms_tmp: any[] = []
  let algorithms_list_tmp: any[] = []
  var requestUrl = new URL(PageConfig.getBaseUrl() + 'jupyter-server-extension/listAlgorithms');

  requestUrl.searchParams.append("visibility", "all");

  await fetch(requestUrl.href, {
    headers: {
      'Content-Type': 'application/json'
    }
  }).then((response) => response.json())
    .then((data) => {

      data["response"]["algorithms"].forEach((item: any) => {
        // TODO: add async dropdown formatted options to store
        let algorithm: any = {}

        // algorithm["value"] = item["type"] + ':' + item["version"]
        // algorithm["label"] = item["type"] + ':' + item["version"]
        algorithms_list_tmp.push(item["type"] + ':' + item["version"])
        // algorithms_tmp.push(algorithm)
      })
      console.log("list from api: ", algorithms_list_tmp)
      store.dispatch(registeredAlgorithmsActions.setAlgorithmsList(algorithms_list_tmp))
      return algorithms_tmp
    });
  return algorithms_tmp
}


async function _describeAllAlgorithms() {
  const fmtAlgorithmsData: IAlgorithmData[] = [];
  var requestUrl = new URL(PageConfig.getBaseUrl() + 'jupyter-server-extension/describeAlgorithms');

  // Get list of all registered algorithms
  const algorithms = store.getState().RegisteredAlgorithms.algorithmsList;

  // Get algorithm data for each of the registered algorithms
  for (const algorithm of algorithms) {
    let algorithmData: IAlgorithmData = {id: "", description: "", inputs: []}

    try {
      requestUrl.searchParams.append("algo_id", algorithm);
      const response = await fetch(requestUrl.href, {headers: { 'Content-Type': 'application/json' }})
      const data = await response.json();
      console.log("Data from api return")
      console.log(data)

      algorithmData = parseAlgorithmData(data["response"])
      
      console.log(algorithmData)
      fmtAlgorithmsData.push(algorithmData)

    } catch (error) {
      console.error(`Error fetching data: ${error}`);
    }
  }

  return fmtAlgorithmsData;
}

export async function describeAllAlgorithms() {
  try {
    const allData = await _describeAllAlgorithms();
    console.log('All responses:', allData);
    store.dispatch(registeredAlgorithmsActions.setAlgorithmsData(allData))
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}


export async function unregisterAlgorithm(algo_id: string) {
  var requestUrl = new URL(PageConfig.getBaseUrl() + 'jupyter-server-extension/unregisterAlgorithm');

  requestUrl.searchParams.append("algo_id", algo_id);
  console.log("unregister algorithm")
  // const response = await fetch(requestUrl.href, {
  //   headers: { 'Content-Type': 'application/json' }
  // })
  // const data = await response.json();
  // return data
  return ""
}


export async function getWorkspaceContainer() {
  var requestUrl = new URL(PageConfig.getBaseUrl() + 'jupyter-server-extension/getWorkspaceContainer');
  console.log(requestUrl.href)

  try {
    const response: any = await fetch(requestUrl.href, {
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error('Request failed');
    }

    console.log("resolved")
    const r_data = await response.json();
    console.log(r_data)
    return r_data
  } catch (error) {
    console.log("error in new endpoint")
    console.log(error)
  }
}