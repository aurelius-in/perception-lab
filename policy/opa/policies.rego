package perceptionlab.policies

deny[msg] {
  input.kind == "Rollout"
  endswith(input.spec.template.spec.containers[_].image, ":latest")
  msg := "Disallow :latest tag"
}

deny[msg] {
  input.kind == "Rollout"
  not input.spec.template.spec.containers[_].resources.limits
  msg := "All containers must set resource limits"
}

deny[msg] {
  input.kind == "Rollout"
  not input.spec.template.metadata.labels.app
  msg := "Must set metadata.labels.app"
}

deny[msg] {
  input.kind == "Rollout"
  not input.spec.template.metadata.labels.version
  msg := "Must set metadata.labels.version"
}

