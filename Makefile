.PHONY: pull-crds

pull-crds:
	crossplane xpkg get-crds manifests/crossplane-providers/ --output-dir crds
