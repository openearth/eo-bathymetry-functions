.PHONY: build local-deploy deploy get_tf_key

sa_email = $(shell cd terraform && terraform output -raw sa_email)
sa_key_path = $(shell dirname $(shell cd terraform && terraform output -raw sa_key_path))
sa_key_name = $(shell basename $(shell cd terraform && terraform output -raw sa_key_path))

build:
	pack build \
	--builder gcr.io/buildpacks/builder:v1 \
	--env GOOGLE_RUNTIME=python \
	--env GOOGLE_RUNTIME_VERSION=3.8.6 \
	--env GOOGLE_FUNCTION_SIGNATURE_TYPE=http \
	--env GOOGLE_FUNCTION_TARGET=generate_bathymetry \
	sdb-function

local-deploy: build
	gcloud secrets versions access 1 --secret="eo-bathymetry-sa-key" --format='get(payload.data)' | tr '_-' '/+' | base64 -d > dist/$(sa_key_name)
	docker run \
	--rm \
	-p 8080:8080 \
	-e SA_EMAIL=$(sa_email) \
	-e SA_KEY_PATH=$(sa_key_path)/$(sa_key_name) \
	-v $(shell pwd)/dist:$(sa_key_path) \
	-v $(HOME)/.config/gcloud:/home/cnb/.config/gcloud \
	sdb-function

get_tf_key:
	gcloud secrets versions access 1 --secret="terraform-sa-key" --format='get(payload.data)' | tr '_-' '/+' | base64 -d > dist/terraform_sa_key.json

deploy: get_tf_key
	cd terraform && terraform apply -var-file workspaces/default.tfvars
