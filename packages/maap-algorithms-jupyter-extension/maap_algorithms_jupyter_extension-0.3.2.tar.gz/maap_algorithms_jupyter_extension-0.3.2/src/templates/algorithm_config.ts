export const algorithm_config_template = `
  algorithm_name: algorithm-name
  algorithm_version: 0.1.0
  repository_url: https://github.com/
  docker_container_url: url
  algorithm_description: "Description of algorithm."
  run_command: run.sh
  build_command: build.sh
  disk_space: 50GB
  queue: queue
  inputs:
    file:
      - name: benthic_reflectance_dataset
        required: True
      - name: depth_dataset
        required: True
    config:
      - name: crid
        default: "000"
    positional:
      - name: crid
        default: "000"
`
