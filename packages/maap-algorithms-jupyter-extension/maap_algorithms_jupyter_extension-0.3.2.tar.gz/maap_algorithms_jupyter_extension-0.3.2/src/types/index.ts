export type IAlgorithm = {
    algorithmID: string
}

export type IAlgorithmConfig = {
    algorithm_name: string,
    algorithm_version: string,
    repository_url: string,
    docker_container_url: string,
    algorithm_description: string,
    run_command: string,
    build_command: string,
    queue: string,
    disk_space: string,
    inputs: {
        file: any[]
        config: any[]
        positional: any[]
    }
}