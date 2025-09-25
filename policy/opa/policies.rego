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

