# Changelog

## [Unreleased] - TBA

## [v0.1.52] - 2024-07-19

- Use logging in middleware

## [v0.1.51] - 2024-07-18

- Adds `@actor.task` and removes `@actor`
- Adds `@actor.dynamic`
- Adds `UNION_API_KEY` as environment variable for the API key.

## [v0.1.50] - 2024-07-17

- Small fix for workspaces with GPUs

## [v0.1.49] - 2024-07-17

- Use `--host` for login to be consistent with uctl.
- Improve workspaces to make it easier to authenticate.

## [v0.1.48] - 2024-07-12

- Give `ttl_seconds` a non-zero value of 100

## [v0.1.47] - 2024-07-11

- Use cr.union.ai hostname for serverless images
- Adds `UNION_CONFIG` and `UNION_SERVERLESS_API_KEY`.
- Migrate to `UNION_SERVERLESS_ENDPOINT` and `UNION_ENABLE_REGISTER_IMAGE_BUILDER` for development.
- Simplify `union create login`
- Update all other `UNION_` environment variables.
- Adds `union create login --host`

## [v0.1.46] - 2024-07-05

- Only add `union` in image builder if it is not specified already

## [v0.1.45] - 2024-07-03

- First release of `union` SDK.

## [v0.1.44] - 2024-07-03

- Updates Actor definition

## [v0.1.43] - 2024-07-01

- Fixes MetadataFS for Artifacts

## [v0.1.42] - 2024-06-28

- Use home directory when installing code-sever manually

## [v0.1.41] - 2024-06-28

- Support `~` in `workspace_root`

## [v0.1.40] - 2024-06-27

- Enable binary file secrets

## [v0.1.39] - 2024-06-26

- Enable artifact triggers that bind to queries

## [v0.1.38] - 2024-06-25

- Add accelerator to `ActorEnvironment`.

## [v0.1.37] - 2024-06-25

- Use unionai version that is installed during registration in image builder

## [v0.1.36] - 2024-06-25

- Revert back to `~/.unionai/config.yaml` for standard configuration.

## [v0.1.35] - 2024-06-25

- `pyflyte` defaults to localhost for `byoc` to match with OSS.
- Improve image builder with flyte labels
- Update docstrings for classes and methods in `unionai`
- Adds `UNIONAI_ENABLE_REGISTER_IMAGE_BUILDER` to offline debugging.

## [v0.1.34] - 2024-06-24

- Send errors from flytekit.clients to sentry
- Image builder now ignores files from `.gitignore` and `.dockerignore`

## [v0.1.33] - 2024-06-21

- Fixes image builder execution id bug

## [v0.1.32] - 2024-06-20

- Fixes bug with CLI in workspaces.

## [v0.1.31] - 2024-06-18

- Makes the workspace root configurable.

## [v0.1.30] - 2024-06-18

- Change config directory to `~/.config/unionai/config.yaml`

## [v0.1.29] - 2024-06-18

- Make sure image build can recover from UI termination
- Error when the config is empty when using `~/.unionai/config`.
- Gives `UNIONAI_SERVERLESS_ENDPOINT` a high precedence than `~/.unionai/config`

## [v0.1.28] - 2024-06-13

- Ship with actors
- Use `UNIONAI_SDK_LOGGING_LEVEL` for controlling logging level.

## [v0.1.27] - 2024-06-11

- Fixes issue with `unionai[byoc]`

## [v0.1.26] - 2024-06-11

- Improves support for large dataframes
- Adds `pip install unionai[byoc]`
- Image builder skips building if the image is already built.
- Gives `UNIONAI_SERVERLESS_ENDPOINT` a high precedence than `~/.unionai/config`

## [v0.1.25] - 2024-06-05

- pin flytekit version >= 1.12.2

## [v0.1.24] - 2024-06-04

- pin flytekit version >= 1.12.1rc1
- Update to use vanity URLs when dumping console link

## [v0.1.23] - 2024-05-31

- Support `ImageSpec` in actors

## [v0.1.22] - 2024-05-29

- Update workspace idle time to 20 minutes.

## [v0.1.21] - 2024-05-28

- Fixes bug with workspaces

## [v0.1.20] - 2024-05-28

- Fixes project bug from CLI.

## [v0.1.19] - 2024-05-28

- Adds workspaces alpha feature.

## [v0.1.18] - 2024-05-21

- Disable fsspec caching to remove stderr from grpc.

## [v0.1.17] - 2024-05-14

- Allows FlyteDeck to appear without `flytekitplugins-deck-standard`

## [v0.1.16] - 2024-05-09

- Injects org into Artifact grpc calls.
- Update set_org to recurse maps as well.
- Ignore .git folder in image builder.

## [v0.1.15] - 2024-05-07

- Only show client_id when running `unionai get app`.
- Raises an error if `python_version` is not `"3.11"` in Image Builder.
- Add initial implementation for the actor decorator. Currently only works on functions

## [v0.1.14] - 2024-04-10

- Fixes FlyteDeck regression from fsspec
- Improve error message when image build fails
- Fixes regression in unionfs

## [v0.1.12] - 2024-04-04

- Adds support for `flytekit`'s StructuredDatasets
- Update to `serverless-1.us-east-2.s.union.ai` tenant
- Update HTML callback page.

## [v0.1.11] - 2024-03-29

- Changes image builder name to `unionai`.
- Fixes issue with multiple callbacks when authenticating.

## [v0.1.10] - 2024-03-26

- Fixes project issue when switching between `pyflyte` and `unionai`.

## [v0.1.9] - 2024-03-26

- Adds `verbose` and `x-request-id` for debugging.

## [v0.1.8] - 2024-03-25

- Install `unionai` by default in the image builder.

## [v0.1.7] - 2024-03-25

* Adds Image Build related mapping of Union serverless FQDN to Google Artifact registry base URLs.
- Adds `unionai create login device-flow` and `unionai delete login` to enable device flow authentication.
- `unionai` ignores `FLYTECTL_CONFIG`. Please use `UNIONAI_CONFIG` instead.
- Only require auth when running `unionai run --remote`.
- Make sure `project` is set to `"default"` for serverless.

## [v0.1.6] - 2024-03-13

- Updates Artifacts with `OnTrigger` and sync up with `flytekit`
- Adds Time Granularity
- Add model/data cards

## [v0.1.5] - 2024-02-29

- Fixes bug with `FlyteDirectory` such that multiple files can be downloaded

## [v0.1.4] - 2024-02-27

- Fixes circular reference issue when importing `UnionRemote`

## [v0.1.3] - 2024-02-27

- Adds support for `FlyteDirectory`

## [v0.1.2] - 2024-02-27

- Runs Image builder in the system project
- Adds `is_container()` to ImageSpec

## [v0.1.1] - 2024-02-16

- Fixes default images when passing `--config` in CLI
- Redesigned OAuth success HTML page: Requires `flytekit>=1.10.8`

## [v0.1.0] - 2024-02-15

- Adds UnionAI's ImageBuilder plugin for `ImageSpec`
- Adds Secrets CLI
- Adds Application management CLI
- Adds `--org` to configure the organization in every grpc request
- Adds Artifacts and Triggers (`unionai.artifacts`)
- Adds PersistentDirectory for on-node persistent storage (`unionai.persist`)
