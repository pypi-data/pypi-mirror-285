import { JUPYTER_EXT } from "../constants"

export const openRegistration = (jupyterApp, data) => {
    console.log("in open registration")
    console.log(data)
    if (jupyterApp.commands.hasCommand(JUPYTER_EXT.REGISTER_ALGORITHM_OPEN_COMMAND)) {
        console.log("opening registration to edit")
        if (data == null) {
            console.log("in null")
            jupyterApp.commands.execute(JUPYTER_EXT.REGISTER_ALGORITHM_OPEN_COMMAND, null)
        }else {
            console.log("in data")
            jupyterApp.commands.execute(JUPYTER_EXT.REGISTER_ALGORITHM_OPEN_COMMAND, data)
        }
    }
}

export const openJobs = (jupyterApp, data) => {
    console.log("in open jobs")
    console.log(jupyterApp.commands)
    if (jupyterApp.commands.hasCommand(JUPYTER_EXT.SUBMIT_JOBS_OPEN_COMMAND)) {
        console.log("jobs command exists")
        if (data == null) {
            console.log("in null")
            jupyterApp.commands.execute(JUPYTER_EXT.SUBMIT_JOBS_OPEN_COMMAND)
        }else {
            console.log("in data")
            jupyterApp.commands.execute(JUPYTER_EXT.SUBMIT_JOBS_OPEN_COMMAND)
        }
    }
}