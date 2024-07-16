# Purpose

Wouldn't be nice to script your GCP infrastructure without having to learn a new language ?

# Description

This package simplifies the deployment of GCP services through the gcloud command line.

# Installation

`pip install pygcloud`

# Features

* Leverage `gcloud` command line tool
* Be as transparent to `gcloud` as possible
* Capability to group deployment of services together
* Capability to describe relationships between services
* Capability to perform trial run

# Enabling Features 

* Infrastructure governance
* Diagramming

The above features are supported by employing the `after_*` methods of the `GCPService` class.

# Categories of Services

1. SingletonImmutable e.g. Firestore indexes
2. RevisionBased e.g. Cloud Run service with revisions
3. Updatable e.g. GCS bucket

For the "SingletonImmutable" category, we ignore exceptions arising from the service already being created. The "describe" facility might be or not available.

For the "RevisionBased", we skip the "update" step. The "create" method will be called. The "describe" facility might be or not available.

For the "Updatable", we do the complete steps i.e. describe, create or update.

# Example Usage

```
from pygcloud.models import Param, EnvParam
from pygcloud.gcp.services.storage import StorageBucket
from pygcloud.deployer import Deployer

# Retrieve parameter from environment variables
# Useful in the context of using Cloud Build
project_id = EnvParam("--project", "_PROJECT_ID")

# The 'common_params' will be added at the end of the gcloud command
# The Deployer can be reused for multiple services
deployer = Deployer(common_params=[project_id])

# The first parameter is the name. Most services require a unique name.
# The second parameter is a list of parameters added to the gcloud command.
bucket = StorageBucket("my-bucket", ["--public-access-prevention"])

# Deploy the service
# For Storage Buckets, an existence check is done using the `describe` gcloud command
# before creating or updating the bucket.
deployer.deploy(bucket)
```

Additional usage tips can be found in the `tests/gcp.services` folder.

# Use relationships

pygcloud supports specifying relationships between services. These are captured in the service instance labels.

The relation type `use` is defined directionally i.e. from one service to another. It is envisaged to be pertinent in the context of an application running on a compute related service (e.g. Cloud Run) utilizing another service (e.g. GCS).

# About GCP Labels

Labels optionally carry the "use" relationships between service instances.

We work with the limitations (i.e. 64 entries, unique key names, value length limited to 63 characters) of GCP's labeling capability in the following manner:

1. Each relationship takes 1 label
2. Each label key is composed like so:  *`pygcloud-use-$index`*
3. The corresponding label value:  *`$ns--$name`*

The field `$name` is sometimes encoded since the value contains characters not supported by GCP. Encoding strategy in these cases is always the same (bas64 with custom alphabet, padding `=` removed).


# About Python 3.9

The gcloud command line is currently built for Python 3.9. The accompanied Docker image provided by Google is built for Python 3.9. To simplify usage of pygcloud, I opted to follow this gcloud constraint.

# TODO

* File bug report about GCS not supporting --clear-labels along with --update-labels (as in Cloud Run as example)


# Links

* [Repository](https://github.com/jldupont/pygcloud)
* [Pypi](https://pypi.org/project/pygcloud/)
* [GCP Labels](https://cloud.google.com/compute/docs/labeling-resources)
