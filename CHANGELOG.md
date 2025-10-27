# [](https://github.com/flamingquaks/promptrek/compare/v0.4.0...v) (2025-10-27)


### Features

* add dynamic variables with built-in and command-based support ([#100](https://github.com/flamingquaks/promptrek/issues/100)) ([d5b70d4](https://github.com/flamingquaks/promptrek/commit/d5b70d43154e9698b84f713a9c6ffe5f3bafd7c3))



# [0.4.0](https://github.com/flamingquaks/promptrek/compare/v0.3.1...v0.4.0) (2025-10-26)


### Bug Fixes

* add SAFETY_API_KEY environment variable for Safety scans and improve handling of missing key ([cfd41e4](https://github.com/flamingquaks/promptrek/commit/cfd41e42ce8e57582f8f7d2b3023067395dd0251))
* Claude missing project agents ([#91](https://github.com/flamingquaks/promptrek/issues/91)) ([95f2a74](https://github.com/flamingquaks/promptrek/commit/95f2a7478c2075c9ca156f13f75a44c56605f7c5))
* Cursor adapter and UPF models with metadata support ([#84](https://github.com/flamingquaks/promptrek/issues/84)) ([60e5372](https://github.com/flamingquaks/promptrek/commit/60e5372ee5b90ca25dd6bef063a9680c2aac5d18))
* improve all adapters to be more inline with their editors ([703836e](https://github.com/flamingquaks/promptrek/commit/703836e4ca47550db130555a8f66ae7c24f96fd2))
* improve Continue IDE file generation and docs ([#86](https://github.com/flamingquaks/promptrek/issues/86)) ([3f1a03b](https://github.com/flamingquaks/promptrek/commit/3f1a03bf8f56f3c8939c3e56c62ad349ef5d1f59))
* Improve layout and responsiveness for benefits and CTA sections ([b6bdefa](https://github.com/flamingquaks/promptrek/commit/b6bdefa0b05ff0451d062b22d59cbac3fa3e2cd1))
* improve safety scan output handling and error management ([aef4bad](https://github.com/flamingquaks/promptrek/commit/aef4baddc45d7088c253234a75d80558302e7a78))
* update default Python version to 3.12 in security workflow ([8c76ab9](https://github.com/flamingquaks/promptrek/commit/8c76ab9e9d68927d9ee80bff78c16aff40b93504))
* yaml schemas updated to include major, minor AND patch in URL. ([#85](https://github.com/flamingquaks/promptrek/issues/85)) ([17d9894](https://github.com/flamingquaks/promptrek/commit/17d98943623138c82f58f4405ebded09f4bd021c))


### Features

* Add automatic PR labeling based on changed files ([#94](https://github.com/flamingquaks/promptrek/issues/94)) ([7ca9266](https://github.com/flamingquaks/promptrek/commit/7ca9266b6909394763d5551fc6fed5277a93c2ea))
* Add Claude-specific patterns to .gitignore and corresponding tests ([#87](https://github.com/flamingquaks/promptrek/issues/87)) ([cda170b](https://github.com/flamingquaks/promptrek/commit/cda170b1492680d6afb0fd650b75ae3c7ed8116a))
* Add new logo assets and update site configuration ([b333388](https://github.com/flamingquaks/promptrek/commit/b33338825c549705d52fca6bdf2e6c99fa824d61))
* Cline MCP improvements and variable refactoring ([#90](https://github.com/flamingquaks/promptrek/issues/90)) ([47637c4](https://github.com/flamingquaks/promptrek/commit/47637c4d2bf811a5230748a7087510d62e105466))
* **docs:** Publish JSON Schema files for UPF v2.0, v2.1, and v3.0 ([#79](https://github.com/flamingquaks/promptrek/issues/79)) ([50eb6fa](https://github.com/flamingquaks/promptrek/commit/50eb6faeab00ce255f4b8c7954d9a331e8983bd0))
* Update Cline adapter to support VSCode integration and enhance documentation ([#75](https://github.com/flamingquaks/promptrek/issues/75)) ([33f2c0b](https://github.com/flamingquaks/promptrek/commit/33f2c0b3f286f15e40bc5b0abb3dd573a89ad276))
* Update Continue Adapter to support modular configuration and enhance sync functionality ([#92](https://github.com/flamingquaks/promptrek/issues/92)) ([8793730](https://github.com/flamingquaks/promptrek/commit/87937303cee765a24158398f7d0cfaa4a3770324))
* Update Universal Prompt Format schemas to enhance content handling and descriptions ([be37516](https://github.com/flamingquaks/promptrek/commit/be375161d0cf0bff042ebfc96a0d4b42f534169b))



# [](https://github.com/flamingquaks/promptrek/compare/v0.3.1...v) (2025-10-26)


### Features

* **variables:** Add dynamic variables with built-in date/time/git variables and command execution support ([#TBD](https://github.com/flamingquaks/promptrek/issues/TBD))
  - Add built-in dynamic variables: CURRENT_DATE, CURRENT_TIME, CURRENT_DATETIME, CURRENT_YEAR, CURRENT_MONTH, CURRENT_DAY, PROJECT_NAME, PROJECT_ROOT, GIT_BRANCH, GIT_COMMIT_SHORT
  - Add support for user-defined command-based dynamic variables in .promptrek/variables.promptrek.yaml
  - Add `allow_commands` field to UniversalPromptV3 for security control
  - Add variable caching mechanism for command-based variables
  - Add `promptrek refresh` command to regenerate files with updated dynamic variables
  - Add generation metadata (.promptrek/last-generation.yaml) to support refresh workflow
  - Update .gitignore and pre-commit hooks to prevent committing metadata files


### Bug Fixes

* add SAFETY_API_KEY environment variable for Safety scans and improve handling of missing key ([cfd41e4](https://github.com/flamingquaks/promptrek/commit/cfd41e42ce8e57582f8f7d2b3023067395dd0251))
* Claude missing project agents ([#91](https://github.com/flamingquaks/promptrek/issues/91)) ([95f2a74](https://github.com/flamingquaks/promptrek/commit/95f2a7478c2075c9ca156f13f75a44c56605f7c5))
* Cursor adapter and UPF models with metadata support ([#84](https://github.com/flamingquaks/promptrek/issues/84)) ([60e5372](https://github.com/flamingquaks/promptrek/commit/60e5372ee5b90ca25dd6bef063a9680c2aac5d18))
* improve all adapters to be more inline with their editors ([703836e](https://github.com/flamingquaks/promptrek/commit/703836e4ca47550db130555a8f66ae7c24f96fd2))
* improve Continue IDE file generation and docs ([#86](https://github.com/flamingquaks/promptrek/issues/86)) ([3f1a03b](https://github.com/flamingquaks/promptrek/commit/3f1a03bf8f56f3c8939c3e56c62ad349ef5d1f59))
* Improve layout and responsiveness for benefits and CTA sections ([b6bdefa](https://github.com/flamingquaks/promptrek/commit/b6bdefa0b05ff0451d062b22d59cbac3fa3e2cd1))
* improve safety scan output handling and error management ([aef4bad](https://github.com/flamingquaks/promptrek/commit/aef4baddc45d7088c253234a75d80558302e7a78))
* update default Python version to 3.12 in security workflow ([8c76ab9](https://github.com/flamingquaks/promptrek/commit/8c76ab9e9d68927d9ee80bff78c16aff40b93504))
* yaml schemas updated to include major, minor AND patch in URL. ([#85](https://github.com/flamingquaks/promptrek/issues/85)) ([17d9894](https://github.com/flamingquaks/promptrek/commit/17d98943623138c82f58f4405ebded09f4bd021c))


### Features

* Add automatic PR labeling based on changed files ([#94](https://github.com/flamingquaks/promptrek/issues/94)) ([7ca9266](https://github.com/flamingquaks/promptrek/commit/7ca9266b6909394763d5551fc6fed5277a93c2ea))
* Add Claude-specific patterns to .gitignore and corresponding tests ([#87](https://github.com/flamingquaks/promptrek/issues/87)) ([cda170b](https://github.com/flamingquaks/promptrek/commit/cda170b1492680d6afb0fd650b75ae3c7ed8116a))
* Add new logo assets and update site configuration ([b333388](https://github.com/flamingquaks/promptrek/commit/b33338825c549705d52fca6bdf2e6c99fa824d61))
* Cline MCP improvements and variable refactoring ([#90](https://github.com/flamingquaks/promptrek/issues/90)) ([47637c4](https://github.com/flamingquaks/promptrek/commit/47637c4d2bf811a5230748a7087510d62e105466))
* **docs:** Publish JSON Schema files for UPF v2.0, v2.1, and v3.0 ([#79](https://github.com/flamingquaks/promptrek/issues/79)) ([50eb6fa](https://github.com/flamingquaks/promptrek/commit/50eb6faeab00ce255f4b8c7954d9a331e8983bd0))
* Update Cline adapter to support VSCode integration and enhance documentation ([#75](https://github.com/flamingquaks/promptrek/issues/75)) ([33f2c0b](https://github.com/flamingquaks/promptrek/commit/33f2c0b3f286f15e40bc5b0abb3dd573a89ad276))
* Update Continue Adapter to support modular configuration and enhance sync functionality ([#92](https://github.com/flamingquaks/promptrek/issues/92)) ([8793730](https://github.com/flamingquaks/promptrek/commit/87937303cee765a24158398f7d0cfaa4a3770324))
* Update Universal Prompt Format schemas to enhance content handling and descriptions ([be37516](https://github.com/flamingquaks/promptrek/commit/be375161d0cf0bff042ebfc96a0d4b42f534169b))



## [0.3.1](https://github.com/flamingquaks/promptrek/compare/v0.3.0...v0.3.1) (2025-10-17)


### Features

* Update documentation and configuration for v3.0.0 schema, including new .gitignore entries and migration instructions ([52a7157](https://github.com/flamingquaks/promptrek/commit/52a71572b062d12238a0a4af45bdef8115a1417f))
* Upgrade adapters and sync command to support UniversalPromptV3 schema ([#73](https://github.com/flamingquaks/promptrek/issues/73)) ([5a70d22](https://github.com/flamingquaks/promptrek/commit/5a70d221fa4e5055f069417b0de84ecba3708258))



# [](https://github.com/flamingquaks/promptrek/compare/v0.3.0...v) (2025-10-17)


### Features

* Update documentation and configuration for v3.0.0 schema, including new .gitignore entries and migration instructions ([52a7157](https://github.com/flamingquaks/promptrek/commit/52a71572b062d12238a0a4af45bdef8115a1417f))
* Upgrade adapters and sync command to support UniversalPromptV3 schema ([#73](https://github.com/flamingquaks/promptrek/issues/73)) ([5a70d22](https://github.com/flamingquaks/promptrek/commit/5a70d221fa4e5055f069417b0de84ecba3708258))



# [0.3.0](https://github.com/flamingquaks/promptrek/compare/v0.2.0...v0.3.0) (2025-10-16)


### Features

* Add .gitignore configuration for editor-specific files ([#72](https://github.com/flamingquaks/promptrek/issues/72)) ([e1b2f04](https://github.com/flamingquaks/promptrek/commit/e1b2f046e183a005121ec62705a27f9fc329d3f3))
* Add support for UniversalPromptV3 and enhance migration functionality ([#70](https://github.com/flamingquaks/promptrek/issues/70)) ([e3e4319](https://github.com/flamingquaks/promptrek/commit/e3e431924982c65822eb3f662ff8de80d308e9c6))
* Update documentation for v3.0.0 schema, including migration guide and deprecation warnings ([bb393d4](https://github.com/flamingquaks/promptrek/commit/bb393d4f6b0f278e005163ebf0f042005cff927c))
* Upgrade Project's promptrek config - schema version to 3.0.0 ([c53c2a5](https://github.com/flamingquaks/promptrek/commit/c53c2a5d80b1d21bb2c408b4b1fdfac7c4d3b4cd))



# [](https://github.com/flamingquaks/promptrek/compare/v0.2.0...v) (2025-10-16)


### Features

* Add .gitignore configuration for editor-specific files ([#72](https://github.com/flamingquaks/promptrek/issues/72)) ([e1b2f04](https://github.com/flamingquaks/promptrek/commit/e1b2f046e183a005121ec62705a27f9fc329d3f3))
* Add support for UniversalPromptV3 and enhance migration functionality ([#70](https://github.com/flamingquaks/promptrek/issues/70)) ([e3e4319](https://github.com/flamingquaks/promptrek/commit/e3e431924982c65822eb3f662ff8de80d308e9c6))
* Update documentation for v3.0.0 schema, including migration guide and deprecation warnings ([bb393d4](https://github.com/flamingquaks/promptrek/commit/bb393d4f6b0f278e005163ebf0f042005cff927c))
* Upgrade Project's promptrek config - schema version to 3.0.0 ([c53c2a5](https://github.com/flamingquaks/promptrek/commit/c53c2a5d80b1d21bb2c408b4b1fdfac7c4d3b4cd))



# [0.2.0](https://github.com/flamingquaks/promptrek/compare/v0.1.1...v0.2.0) (2025-10-15)


### Bug Fixes

* Downgrade PyYAML dependency version to 5.4 in configuration files ([8199b08](https://github.com/flamingquaks/promptrek/commit/8199b08022eee738cfc9c35ab85a9dd65ec737d8))
* Update keywords and remove unnecessary dependencies in configuration files ([5da5d6c](https://github.com/flamingquaks/promptrek/commit/5da5d6cc395ff1801241105a9622bcb10ab89820))


### Features

* Add v2.1 plugin support and enhance configurations ([#69](https://github.com/flamingquaks/promptrek/issues/69)) ([ceb3d51](https://github.com/flamingquaks/promptrek/commit/ceb3d5150790a4353ddd6e42912c0205246e9e7c))



# [](https://github.com/flamingquaks/promptrek/compare/v0.1.1...v) (2025-10-15)


### Bug Fixes

* Downgrade PyYAML dependency version to 5.4 in configuration files ([8199b08](https://github.com/flamingquaks/promptrek/commit/8199b08022eee738cfc9c35ab85a9dd65ec737d8))
* Update keywords and remove unnecessary dependencies in configuration files ([5da5d6c](https://github.com/flamingquaks/promptrek/commit/5da5d6cc395ff1801241105a9622bcb10ab89820))


### Features

* Add v2.1 plugin support and enhance configurations ([#69](https://github.com/flamingquaks/promptrek/issues/69)) ([ceb3d51](https://github.com/flamingquaks/promptrek/commit/ceb3d5150790a4353ddd6e42912c0205246e9e7c))



## [0.1.1](https://github.com/flamingquaks/promptrek/compare/v0.0.7...v0.1.1) (2025-10-13)


### Bug Fixes

* Correct changelog sections and reorder entries for clarity ([14436e3](https://github.com/flamingquaks/promptrek/commit/14436e37b0be48bce44dc310c19d73f461d9fabb))
* update hook stages to pre-commit for validation and prevention checks ([#65](https://github.com/flamingquaks/promptrek/issues/65)) ([f3273b4](https://github.com/flamingquaks/promptrek/commit/f3273b41adbf44b1820e285abe265a1b6ae87678))


### Features

* Enhance changelog generation with last stable version detection ([cc0f395](https://github.com/flamingquaks/promptrek/commit/cc0f3953da4fbadadf132addb8be5498f73e55c3))



# [](https://github.com/flamingquaks/promptrek/compare/v0.0.7...v) (2025-10-13)


### Bug Fixes

* Correct changelog sections and reorder entries for clarity ([14436e3](https://github.com/flamingquaks/promptrek/commit/14436e37b0be48bce44dc310c19d73f461d9fabb))
* update hook stages to pre-commit for validation and prevention checks ([#65](https://github.com/flamingquaks/promptrek/issues/65)) ([f3273b4](https://github.com/flamingquaks/promptrek/commit/f3273b41adbf44b1820e285abe265a1b6ae87678))


### Features

* Enhance changelog generation with last stable version detection ([cc0f395](https://github.com/flamingquaks/promptrek/commit/cc0f3953da4fbadadf132addb8be5498f73e55c3))



## [0.0.7](https://github.com/flamingquaks/promptrek/compare/v0.0.6...v0.0.7) (2025-10-08)


### Bug Fixes

* sync support across editos ([#61](https://github.com/flamingquaks/promptrek/issues/61)) ([46a202e](https://github.com/flamingquaks/promptrek/commit/46a202e1ad47d2a7853751a1b35674cda4f6b0e2))
* update file name from .cline_rules.md to .clinerules/context.md ([f93004d](https://github.com/flamingquaks/promptrek/commit/f93004d8340c80618175ec4f920cbb8524c55e82))


### Features

* add support for local variables file and prevent accidental commits ([#59](https://github.com/flamingquaks/promptrek/issues/59)) ([32d4001](https://github.com/flamingquaks/promptrek/commit/32d400195d96f6526bebe13e006bd4ad557edea3))



# [](https://github.com/flamingquaks/promptrek/compare/v0.0.7...v) (2025-10-13)


### Bug Fixes

* update hook stages to pre-commit for validation and prevention checks ([#65](https://github.com/flamingquaks/promptrek/issues/65)) ([f3273b4](https://github.com/flamingquaks/promptrek/commit/f3273b41adbf44b1820e285abe265a1b6ae87678))


### Features

* Enhance changelog generation with last stable version detection ([cc0f395](https://github.com/flamingquaks/promptrek/commit/cc0f3953da4fbadadf132addb8be5498f73e55c3))



## [0.0.7](https://github.com/flamingquaks/promptrek/compare/v0.0.6...v0.0.7) (2025-10-08)


### Bug Fixes

* sync support across editos ([#61](https://github.com/flamingquaks/promptrek/issues/61)) ([46a202e](https://github.com/flamingquaks/promptrek/commit/46a202e1ad47d2a7853751a1b35674cda4f6b0e2))
* update file name from .cline_rules.md to .clinerules/context.md ([f93004d](https://github.com/flamingquaks/promptrek/commit/f93004d8340c80618175ec4f920cbb8524c55e82))


### Features

* add support for local variables file and prevent accidental commits ([#59](https://github.com/flamingquaks/promptrek/issues/59)) ([32d4001](https://github.com/flamingquaks/promptrek/commit/32d400195d96f6526bebe13e006bd4ad557edea3))



## [0.0.6](https://github.com/flamingquaks/promptrek/compare/v0.0.5...v0.0.6) (2025-10-01)


### Bug Fixes

* update pre-commit hook args and remove Windsurf references from documentation ([#55](https://github.com/flamingquaks/promptrek/issues/55)) ([5e19094](https://github.com/flamingquaks/promptrek/commit/5e19094f83241729f5d62c3ef75402426dc59e70))



## [0.0.5](https://github.com/flamingquaks/promptrek/compare/v0.0.4...v0.0.5) (2025-10-01)



## [0.0.4](https://github.com/flamingquaks/promptrek/compare/v0.0.3...v0.0.4) (2025-10-01)



## [0.0.3](https://github.com/flamingquaks/promptrek/compare/v0.0.2...v0.0.3) (2025-10-01)


### Bug Fixes

* improve release notes generation with fallback mechanism ([798e380](https://github.com/flamingquaks/promptrek/commit/798e380a45a9c793e2a734698d043d690e1baa4a))
* remove duplicate permissions declaration in CI workflow ([4ebf193](https://github.com/flamingquaks/promptrek/commit/4ebf19370eaaef2f9663e23312dbda81f8187e68))


### Features

* Add pre-commit hooks integration and commands ([#54](https://github.com/flamingquaks/promptrek/issues/54)) ([5b66746](https://github.com/flamingquaks/promptrek/commit/5b66746a86dbf0707ec0615afec32a3937a65c53))
* Add preview command to CLI for generating output previews ([#53](https://github.com/flamingquaks/promptrek/issues/53)) ([f6f4933](https://github.com/flamingquaks/promptrek/commit/f6f4933fe575736b208399ae156e388150626599))



## [0.0.2](https://github.com/flamingquaks/promptrek/compare/v0.0.1...v0.0.2) (2025-09-29)



## [0.0.1](https://github.com/flamingquaks/promptrek/compare/v0.0.0-rc.6...v0.0.1) (2025-09-29)


### Bug Fixes

* code scanning alert no. 11: Workflow does not contain permissions ([#51](https://github.com/flamingquaks/promptrek/issues/51)) ([27847a7](https://github.com/flamingquaks/promptrek/commit/27847a7dc8765e55b692cb3f6850e25d8e8a0a9c))
* code scanning alert no. 14: Workflow does not contain permissions ([#50](https://github.com/flamingquaks/promptrek/issues/50)) ([1475d3a](https://github.com/flamingquaks/promptrek/commit/1475d3ad09b49790784ac80a43607ad9e43fdb24))
* code scanning alert no. 22: Workflow does not contain permissions ([#49](https://github.com/flamingquaks/promptrek/issues/49)) ([ac71f93](https://github.com/flamingquaks/promptrek/commit/ac71f93e1733c697d5318ab9edd7c6bf263aae8d))
* code scanning alert no. 28: Workflow does not contain permissions ([#48](https://github.com/flamingquaks/promptrek/issues/48)) ([5166260](https://github.com/flamingquaks/promptrek/commit/5166260dfc22ad783df49fc6a229538ff9d2e83c))
* code scanning alert no. 4: Workflow does not contain permissions ([#52](https://github.com/flamingquaks/promptrek/issues/52)) ([711c166](https://github.com/flamingquaks/promptrek/commit/711c166a7efef5a5b73a040d7ac965614a7e0917))
* code scanning alert no. 40: Workflow does not contain permissions ([#47](https://github.com/flamingquaks/promptrek/issues/47)) ([65fa0ee](https://github.com/flamingquaks/promptrek/commit/65fa0eec0f8f697e91330e859e878c7c5361524a))
* code scanning alert no. 41: Workflow does not contain permissions ([#46](https://github.com/flamingquaks/promptrek/issues/46)) ([4e66515](https://github.com/flamingquaks/promptrek/commit/4e6651515a090c2ba86067d273e784022a7dd446))
* code scanning alert no. 42: Workflow does not contain permissions ([#45](https://github.com/flamingquaks/promptrek/issues/45)) ([fe84748](https://github.com/flamingquaks/promptrek/commit/fe847483a2557125b68ad31aa933ac12ce7ce1dd))
* code scanning alert no. 44: Workflow does not contain permissions ([#44](https://github.com/flamingquaks/promptrek/issues/44)) ([ba3d4d9](https://github.com/flamingquaks/promptrek/commit/ba3d4d946413192b6f15cf16455a86b7337f9ad2))
* code scanning alert no. 45: Workflow does not contain permissions ([#43](https://github.com/flamingquaks/promptrek/issues/43)) ([e09bcea](https://github.com/flamingquaks/promptrek/commit/e09bcea384fbbe3f5baa8b58d5a8cdc59d6cc0c2))
* code scanning alert no. 46: Workflow does not contain permissions ([#42](https://github.com/flamingquaks/promptrek/issues/42)) ([6297aba](https://github.com/flamingquaks/promptrek/commit/6297aba3605afe0cc7d249aa14c0afdf7179265c))
* code scanning alert no. 48: Workflow does not contain permissions ([#40](https://github.com/flamingquaks/promptrek/issues/40)) ([d11d4ca](https://github.com/flamingquaks/promptrek/commit/d11d4ca1da074d7756e1ab5fab4bf2c60ea5278c))
* Update Safety scan condition to exclude '-rc' tags ([#41](https://github.com/flamingquaks/promptrek/issues/41)) ([f8121d5](https://github.com/flamingquaks/promptrek/commit/f8121d5e085a94c48cb5f35a133242abc7ac0594))


### Features

* Enhance ClineAdapter to support modular rule file generation and improve validation ([d754348](https://github.com/flamingquaks/promptrek/commit/d754348e41237e38f3534489cbd667d13f65048c))



# [0.0.0-rc.6](https://github.com/flamingquaks/promptrek/compare/v0.0.0-rc.5...v0.0.0-rc.6) (2025-09-29)



# [0.0.0-rc.5](https://github.com/flamingquaks/promptrek/compare/v0.0.0-rc.4...v0.0.0-rc.5) (2025-09-29)


### Bug Fixes

* copilot file generation ([#37](https://github.com/flamingquaks/promptrek/issues/37)) ([e9b35b9](https://github.com/flamingquaks/promptrek/commit/e9b35b9d08ae9959aee596eabf94d3ab7db5ccdb))



# [0.0.0-rc.4](https://github.com/flamingquaks/promptrek/compare/v0.0.0-rc.3...v0.0.0-rc.4) (2025-09-29)


### Features

* Update release workflow to set version from tag for pre-releases and improve RC version handling ([6fb1c7f](https://github.com/flamingquaks/promptrek/commit/6fb1c7fcd7ce1c901c4b253bc0c8343c344ea7b2))



# [0.0.0-rc.3](https://github.com/flamingquaks/promptrek/compare/v0.0.0-rc.2...v0.0.0-rc.3) (2025-09-29)



# [0.0.0-rc.2](https://github.com/flamingquaks/promptrek/compare/v0.0.0-rc.1...v0.0.0-rc.2) (2025-09-29)


### Features

* Add skip-existing option to prevent re-publishing existing versions to Test PyPI ([40c42a7](https://github.com/flamingquaks/promptrek/commit/40c42a754bf1c285dc87cda9b3e6a29ca554b083))



# [0.0.0-rc.1](https://github.com/flamingquaks/promptrek/compare/0126fef9fe576d8076248c238831d37adda08674...v0.0.0-rc.1) (2025-09-29)


* feat!: drop Python 3.8 support, require Python 3.9+ ([fb66cd0](https://github.com/flamingquaks/promptrek/commit/fb66cd0c5a58491f60f80c8c91b7dd66e80efc5e))


### Bug Fixes

* Claude files, CI build issues ([#32](https://github.com/flamingquaks/promptrek/issues/32)) ([b43e6e1](https://github.com/flamingquaks/promptrek/commit/b43e6e121363886d103407b10d7908b3b5c5c732))
* Correct api-key to api_key in Safety CLI step and ensure environment is set for security scan ([e2e8ea4](https://github.com/flamingquaks/promptrek/commit/e2e8ea4e846122f8e7dfe193e526fa7a21a72881))
* Ensure security scans continue on error for RC tags and regular CI/PRs (temp patch) ([b9aa475](https://github.com/flamingquaks/promptrek/commit/b9aa475160e3aeba77857129d1fa88f8e80adcb1))
* GitHub Pages CSS loading by adding missing Jekyll includes and correcting domain configuration ([#25](https://github.com/flamingquaks/promptrek/issues/25)) ([fd74a31](https://github.com/flamingquaks/promptrek/commit/fd74a31526cae84b0ec8b8de65775b387ab6b5ba))
* refactor/replace bad outputs ([bf57499](https://github.com/flamingquaks/promptrek/commit/bf574996c2d2ea1bc61dda1ac7b8015652349e28))
* resolve failing tests and validations ([#17](https://github.com/flamingquaks/promptrek/issues/17)) ([7794825](https://github.com/flamingquaks/promptrek/commit/7794825ec017761090da5112409d122cd9a632d0))
* resolved issues with tests ([9029aa7](https://github.com/flamingquaks/promptrek/commit/9029aa7b7b2231191aaba2a3b703d5bc148c611d))
* test-matrix workflow failures: CLI args, YAML syntax, and conditional processing ([#6](https://github.com/flamingquaks/promptrek/issues/6)) ([eb972e3](https://github.com/flamingquaks/promptrek/commit/eb972e316b1b04354eb234fb1d51f4e60e400b48))
* typo in release pipeline. ([c99f7c1](https://github.com/flamingquaks/promptrek/commit/c99f7c1b39d335311735f0c4411fe178b81b358f))
* use Tuple instead of tuple for Python <3.9 compatibility ([ae9c20b](https://github.com/flamingquaks/promptrek/commit/ae9c20bd4e1b4ad0754a4d02c76f8f1ae6cde650))
* uv build issues ([#29](https://github.com/flamingquaks/promptrek/issues/29)) ([b1baafb](https://github.com/flamingquaks/promptrek/commit/b1baafbafc5f600843452bfc795b1960f15cb8a3))
* uv run build ([#28](https://github.com/flamingquaks/promptrek/issues/28)) ([2a5c4b6](https://github.com/flamingquaks/promptrek/commit/2a5c4b6ec08808645d607e6700767cd6eadeaa3a))


### Features

* Add 'agents' command for persistent agent instruction files ([#21](https://github.com/flamingquaks/promptrek/issues/21)) ([3880848](https://github.com/flamingquaks/promptrek/commit/388084848dbce6cf364ed08b7e743eb109a3fd0f))
* Add bidirectional sync feature: create/update PrompTrek configuration from AI editor files ([#19](https://github.com/flamingquaks/promptrek/issues/19)) ([cf67e8e](https://github.com/flamingquaks/promptrek/commit/cf67e8e06e3070bd0c071439e4ac3a679fec936b))
* Add comprehensive GitHub Actions workflows for automated testing and CI/CD ([#5](https://github.com/flamingquaks/promptrek/issues/5)) ([8151d87](https://github.com/flamingquaks/promptrek/commit/8151d87a7672dbb08fc5c527b6b58def3a5bb41a))
* Add release and release candidate scripts for managing versioning and tagging ([ac3ee2d](https://github.com/flamingquaks/promptrek/commit/ac3ee2d5f25ec01f1924cbf09009ef4091488470))
* Add reusable security workflow for RC tags and regular CI/PRs ([13e7272](https://github.com/flamingquaks/promptrek/commit/13e72723a528f6b55ef03ac96adc0d86b6aa9dcc))
* Add reusable security workflow for RC tags and regular CI/PRs ([2aaa886](https://github.com/flamingquaks/promptrek/commit/2aaa8867c7c471aea38bd2426df14bcd7f614879))
* Add support for multiple prompt files with intelligent content merging and separate file generation ([#9](https://github.com/flamingquaks/promptrek/issues/9)) ([c789bfc](https://github.com/flamingquaks/promptrek/commit/c789bfc8ef7813559a96b34012d3716a4a32d36d))
* **changelog:** integrate conventional commits for automated changelog generation ([#14](https://github.com/flamingquaks/promptrek/issues/14)) ([837a15a](https://github.com/flamingquaks/promptrek/commit/837a15a2466be4edec8ac815eb34e6574926a0ee))
* Complete adapter implementations and add advanced template features ([#4](https://github.com/flamingquaks/promptrek/issues/4)) ([0be5865](https://github.com/flamingquaks/promptrek/commit/0be5865c6dd735fc5abe88dd1ecbf808dabc6f68))
* Enhance Kiro adapter with hooks and prompts systems ([#36](https://github.com/flamingquaks/promptrek/issues/36)) ([940a16d](https://github.com/flamingquaks/promptrek/commit/940a16d000f38833bd326be000e4b6707bc6ad15))
* Enhance release workflow to differentiate between regular and pre-release publishing to PyPI ([15e881b](https://github.com/flamingquaks/promptrek/commit/15e881b577eab9bd3d0deadffb103f58e6e66510))
* Implement adapter architecture, variable substitution, and expand editor support to 6 adapters ([#3](https://github.com/flamingquaks/promptrek/issues/3)) ([7307201](https://github.com/flamingquaks/promptrek/commit/7307201888ab21c99e8c43e729f298969aba3b91))
* Implement core Agent Prompt Mapper functionality - Phase 1-3 complete ([#2](https://github.com/flamingquaks/promptrek/issues/2)) ([0126fef](https://github.com/flamingquaks/promptrek/commit/0126fef9fe576d8076248c238831d37adda08674))
* Integrate with pre-commit framework to validate promptrek files and prevent generated file commits ([#18](https://github.com/flamingquaks/promptrek/issues/18)) ([03f29a0](https://github.com/flamingquaks/promptrek/commit/03f29a0940b2327500e40aca9a94695b5af972c1))
* **pages:** Improve UI ([#31](https://github.com/flamingquaks/promptrek/issues/31)) ([2ac478d](https://github.com/flamingquaks/promptrek/commit/2ac478d1edda44f6a307fe2e802244e8fa8cad34))


### BREAKING CHANGES

* Python 3.8 is no longer supported, minimum version is now 3.9



