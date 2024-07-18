/*******************************
 * Jupyter Extension
 *******************************/
export const JUPYTER_EXT = {
    EXTENSION_CSS_CLASSNAME : 'jl-ReactAppWidget',

    VIEW_ALGORITHMS_PLUGIN_ID : 'view_algorithms:plugin',
    VIEW_ALGORITHMS_NAME : 'View Algorithms',
    VIEW_ALGORITHMS_OPEN_COMMAND : 'view_algorithms:open',

    REGISTER_ALGORITHM_PLUGIN_ID : 'register_algorithm:plugin',
    REGISTER_ALGORITHM_NAME : 'Register Algorithm',
    REGISTER_ALGORITHM_OPEN_COMMAND : 'register_algorithm:open',

    SUBMIT_JOBS_OPEN_COMMAND : 'jobs_submit:open',
}


/*******************************
 * Algorithms
 *******************************/
export const ALGO_INPUTS = {
    CONFIGURATION_INPUTS : 'configuration_inputs',
    FILE_INPUTS : 'file_inputs',
    POSITIONAL_INPUTS : 'positional_inputs'
}

export const ALGO_INPUTS_DESC = {
    CONFIGURATION_INPUTS : "Inputs defined here will be written to a json file named 'inputs.json' in \
                            the working directory. It is recommended that config inputs be used to \
                            change the behavior of the algorithm the user runs.",

    FILE_INPUTS          : "Inputs defined here will be downloaded and placed in a directory named 'inputs'.",

    POSITIONAL_INPUTS    : "Inputs defined here will be used as inputs to the run command defined as \
                           run_command. The order in which the inputs are defined will be preserved \
                           when building the run_command. It is recommended that positional inputs  \
                           be used when users wish to change the behavior of the run command \
                           and not the behavior of the algorithm e.g. adding a verbose flag."
}

export const ALGO_INPUT_FIELDS = {
    INPUT_NAME: "inputName",
    INPUT_DEFAULT : "inputDefault",
    INPUT_DESC : "inputDesc",
    IS_REQUIRED : "isRequired",
    INPUT_ID : "inputId"
} as const;


/* The colSpan attribute for td elements in React accepts a
   number -- unlike raw td elements where you could specify colspan=100%  */
export const COLUMN_SPAN = 6
