## AnswerRocket Template Code Skills

This repository contains the source code for the template skills used in AnswerRocket. 

These templates serve as a foundation for developing and customizing new skills within the platform.

## Setup

This repository contains a .envrc file for use with [direnv](https://direnv.net/docs/installation.html). With that installed you should have a separate python interpreter that direnv's hook will activate for you when you `cd` into this repository.

Once you have direnv set up and activated inside the repo, run `make` to install the current dependencies.

## Local Development

Make sure to set the `AR_URL`, `AR_TOKEN`, and `DATASET_ID` environment variables when running the skill locally -- these will be used to set up the AnswerRocket Client. 

To run the skill locally, refer to the skill-framework [README](https://github.com/answerrocket/skill-framework/tree/main).

### Dependency Management

Code skills that execute on your machine versus the packaged skill that executes on an environment aren't guaranteed to have the same dependencies. When you upload a code skill and the code executes on the environment, the dependencies of the environment are used. This can potentially cause errors that occur within the environment but not locally if the depedencies they don't match.

To mitigate this, [`nfl/MaxServer/setup/requirements.txt`](https://bitbucket.org/aglabs/nfl/src/main/MaxServer/setup/requirements.txt) is used as a set of constraints, copy + pasted into `platform_constraints.txt`. `requirements.in` specifies the packages to install constrained by `platform_constraints.txt`, which `make` compiles into `requirements.txt` and installs the packages from there.

Tips:
- If you get a constraints error when running `make`, most likely the version of `ar-analytics` package is different between the `platform_constraints.txt` and `requirements.in` files.
- If you want to test a code skill on your local machine against a specific build of Max, checkout `nfl` at that build and copy the `nfl/MaxServer/setup/requirements.txt` and paste into `platform_constraints.txt`, then run `make` to install the dependencies constrained by that max build.