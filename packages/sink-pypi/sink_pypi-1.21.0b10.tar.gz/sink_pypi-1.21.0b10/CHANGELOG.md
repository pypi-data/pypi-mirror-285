# Changelog

## 1.21.0-beta.10 (2024-07-18)

Full Changelog: [v1.21.0-beta.9...v1.21.0-beta.10](https://github.com/stainless-sdks/sink-python-public/compare/v1.21.0-beta.9...v1.21.0-beta.10)

### Features

* add no_file_param test case with multipart/form-data ([#590](https://github.com/stainless-sdks/sink-python-public/issues/590)) ([b3a1c8d](https://github.com/stainless-sdks/sink-python-public/commit/b3a1c8dc6360df741603c699ab267167d89e6c1d))
* add types ([#605](https://github.com/stainless-sdks/sink-python-public/issues/605)) ([b4afaf5](https://github.com/stainless-sdks/sink-python-public/commit/b4afaf5ede25ad4538181bfa0f2c4fade7e1f092))
* **api:** add webhook unwrap methods ([#593](https://github.com/stainless-sdks/sink-python-public/issues/593)) ([f1c75c6](https://github.com/stainless-sdks/sink-python-public/commit/f1c75c6e430e42a48417b70bce5289f7223a8328))
* demo terraform renaming ([#591](https://github.com/stainless-sdks/sink-python-public/issues/591)) ([f3b5bd1](https://github.com/stainless-sdks/sink-python-public/commit/f3b5bd185d6962313868063450f9d04e4896d1c5))
* **names:** add test for resource with name `clients` ([#587](https://github.com/stainless-sdks/sink-python-public/issues/587)) ([765e233](https://github.com/stainless-sdks/sink-python-public/commit/765e2330445fa59d571d6eb3535511ab394e2b8e))


### Bug Fixes

* **build:** include more files in sdist builds ([#582](https://github.com/stainless-sdks/sink-python-public/issues/582)) ([acc9e3f](https://github.com/stainless-sdks/sink-python-public/commit/acc9e3f100dfe97a07bbde20c2584d39d6e9f884))


### Chores

* bump spec ([#603](https://github.com/stainless-sdks/sink-python-public/issues/603)) ([dec31a3](https://github.com/stainless-sdks/sink-python-public/commit/dec31a3a9f38198b4e2462777a06ffad2845777d))
* **ci:** also run workflows for PRs targeting `next` ([#597](https://github.com/stainless-sdks/sink-python-public/issues/597)) ([c21b191](https://github.com/stainless-sdks/sink-python-public/commit/c21b1910c1091925ab9ffdf2adacaf1c670dd1b4))
* **ci:** limit release doctor target branches ([#607](https://github.com/stainless-sdks/sink-python-public/issues/607)) ([0c7e24f](https://github.com/stainless-sdks/sink-python-public/commit/0c7e24f5c9cdf76135812da100c1df412c7e0fc8))
* **ci:** update rye to v0.35.0 ([#592](https://github.com/stainless-sdks/sink-python-public/issues/592)) ([bab0be4](https://github.com/stainless-sdks/sink-python-public/commit/bab0be4fff24e130c7cc4dac9a9ab0ecde50fe8b))
* **deps:** bump anyio to v4.4.0 ([#583](https://github.com/stainless-sdks/sink-python-public/issues/583)) ([8082c78](https://github.com/stainless-sdks/sink-python-public/commit/8082c78475578b6d72de3ccf61c297a3d95a8ab2))
* **docs:** document how to do per-request http client customization ([#606](https://github.com/stainless-sdks/sink-python-public/issues/606)) ([6121b08](https://github.com/stainless-sdks/sink-python-public/commit/6121b08f502459bb598306a9af4ea652b3d79bfe))
* **docs:** minor update to formatting of API link in README ([#601](https://github.com/stainless-sdks/sink-python-public/issues/601)) ([6cba255](https://github.com/stainless-sdks/sink-python-public/commit/6cba255593dfb38f7947335ebe6b050720bffcb9))
* gitignore test server logs ([#585](https://github.com/stainless-sdks/sink-python-public/issues/585)) ([4df3a79](https://github.com/stainless-sdks/sink-python-public/commit/4df3a79090c6c21f5539feb2b7cc87b636960db3))
* **internal:** add helper function ([#595](https://github.com/stainless-sdks/sink-python-public/issues/595)) ([fa6fc50](https://github.com/stainless-sdks/sink-python-public/commit/fa6fc50625363c71a17a8a22a0c63b324434b7d1))
* **internal:** add helper method for constructing `BaseModel`s ([#589](https://github.com/stainless-sdks/sink-python-public/issues/589)) ([d49fa14](https://github.com/stainless-sdks/sink-python-public/commit/d49fa14fbb84534cf4f85452b8c4a402184c56b8))
* **internal:** add reflection helper function ([#584](https://github.com/stainless-sdks/sink-python-public/issues/584)) ([23cfca9](https://github.com/stainless-sdks/sink-python-public/commit/23cfca90c5166dfa1feebedc06e0992ecc06e815))
* **internal:** add rich as a dev dependency ([#586](https://github.com/stainless-sdks/sink-python-public/issues/586)) ([6723ee5](https://github.com/stainless-sdks/sink-python-public/commit/6723ee50e5d9bc2bbbc465df49201941f7c7a808))
* **internal:** minor import restructuring ([#598](https://github.com/stainless-sdks/sink-python-public/issues/598)) ([62998b2](https://github.com/stainless-sdks/sink-python-public/commit/62998b26130a73a7c479a221efb56ce379bac93f))
* **internal:** minor options / compat functions updates ([#600](https://github.com/stainless-sdks/sink-python-public/issues/600)) ([19434ff](https://github.com/stainless-sdks/sink-python-public/commit/19434ffcd5828c935e7a96d626f1e06c515d8d28))
* **internal:** minor request options handling changes ([#594](https://github.com/stainless-sdks/sink-python-public/issues/594)) ([b6548cb](https://github.com/stainless-sdks/sink-python-public/commit/b6548cb52dfde4117b70f1c4c65a72ae185219b1))
* **internal:** update formatting ([#602](https://github.com/stainless-sdks/sink-python-public/issues/602)) ([f332c7c](https://github.com/stainless-sdks/sink-python-public/commit/f332c7c1924eb81465a956c3f61babeca5cc2d17))
* **internal:** update formatting ([#604](https://github.com/stainless-sdks/sink-python-public/issues/604)) ([f2dfecc](https://github.com/stainless-sdks/sink-python-public/commit/f2dfecc700b67262066a02fa88f36a4d45ef9a37))
* **internal:** update mypy ([#596](https://github.com/stainless-sdks/sink-python-public/issues/596)) ([deb8bf1](https://github.com/stainless-sdks/sink-python-public/commit/deb8bf183b5a6cfff985e02928f328ab390e7be5))


### Documentation

* **examples:** use named params more ([#599](https://github.com/stainless-sdks/sink-python-public/issues/599)) ([43f9ec6](https://github.com/stainless-sdks/sink-python-public/commit/43f9ec69b78eff092ff0ec7222691bde14743208))

## 1.21.0-beta.9 (2024-06-26)

Full Changelog: [v1.21.0-beta.8...v1.21.0-beta.9](https://github.com/stainless-sdks/sink-python-public/compare/v1.21.0-beta.8...v1.21.0-beta.9)

### Features

* chore: test fixed release ([3181232](https://github.com/stainless-sdks/sink-python-public/commit/3181232b898b1707de0c082a89cfe714a2c592ea))

## 1.21.0-beta.8 (2024-06-26)

Full Changelog: [v1.21.0-beta.7...v1.21.0-beta.8](https://github.com/stainless-sdks/sink-python-public/compare/v1.21.0-beta.7...v1.21.0-beta.8)

### Features

* hotfix: try overriding rye's venv ([571e047](https://github.com/stainless-sdks/sink-python-public/commit/571e04758aa0640db8de35d9c4923db0fd19e860))
* Update publish-pypi ([9ddb9e9](https://github.com/stainless-sdks/sink-python-public/commit/9ddb9e92cd2be3e8effa5ffd806119eca3d9c002))

## 1.21.0-beta.7 (2024-06-26)

Full Changelog: [v1.21.0-beta.6...v1.21.0-beta.7](https://github.com/stainless-sdks/sink-python-public/compare/v1.21.0-beta.6...v1.21.0-beta.7)

### Features

* Update publish-pypi ([9fa2fbd](https://github.com/stainless-sdks/sink-python-public/commit/9fa2fbd5cda511aa734822ac629964639b555f7e))
* Update publish-pypi.yml ([44a3114](https://github.com/stainless-sdks/sink-python-public/commit/44a3114516f49e5edf39fd6d61c50c1a876d4650))

## 1.21.0-beta.6 (2024-06-26)

Full Changelog: [v1.21.0-beta.5...v1.21.0-beta.6](https://github.com/stainless-sdks/sink-python-public/compare/v1.21.0-beta.5...v1.21.0-beta.6)

### Features

* Update publish-pypi.yml ([f03f05c](https://github.com/stainless-sdks/sink-python-public/commit/f03f05caaee813aced9932a19e9c775a6aa2c9d9))

## 1.21.0-beta.5 (2024-06-26)

Full Changelog: [v1.21.0-beta.4...v1.21.0-beta.5](https://github.com/stainless-sdks/sink-python-public/compare/v1.21.0-beta.4...v1.21.0-beta.5)

### Features

* Update publish-pypi.yml ([4fb5c45](https://github.com/stainless-sdks/sink-python-public/commit/4fb5c4517ffbc2986763c6c1dcdeba5f85f7002a))

## 1.21.0-beta.4 (2024-06-25)

Full Changelog: [v1.21.0-beta.3...v1.21.0-beta.4](https://github.com/stainless-sdks/sink-python-public/compare/v1.21.0-beta.3...v1.21.0-beta.4)

### Features

* add discriminated union tests ([#546](https://github.com/stainless-sdks/sink-python-public/issues/546)) ([dc9a7f4](https://github.com/stainless-sdks/sink-python-public/commit/dc9a7f4cfcf5f3cf5cf2e1775c9e91c5121f8346))
* add enum body params case ([#574](https://github.com/stainless-sdks/sink-python-public/issues/574)) ([dd7eed1](https://github.com/stainless-sdks/sink-python-public/commit/dd7eed1ae810a83aab47f49e425e2681eecd304a))
* add more headers tests ([#572](https://github.com/stainless-sdks/sink-python-public/issues/572)) ([40bfc22](https://github.com/stainless-sdks/sink-python-public/commit/40bfc22f7503a35244eaaf8f8ed53976e254ce59))
* add query auth method ([#568](https://github.com/stainless-sdks/sink-python-public/issues/568)) ([f73b287](https://github.com/stainless-sdks/sink-python-public/commit/f73b287ae1caf952f4fb3b9784feb9285b62e780))
* add test cases for unknown / null types in params ([#544](https://github.com/stainless-sdks/sink-python-public/issues/544)) ([5a129a1](https://github.com/stainless-sdks/sink-python-public/commit/5a129a14fbd48b52d60c4eef6ff2c0d7f26996fe))
* add tests for offset pagination with no start field ([#573](https://github.com/stainless-sdks/sink-python-public/issues/573)) ([4a2c08e](https://github.com/stainless-sdks/sink-python-public/commit/4a2c08e527153135aa90453279aa0ce4861e75a2))
* **api:** add missing header params ([#570](https://github.com/stainless-sdks/sink-python-public/issues/570)) ([b6136b7](https://github.com/stainless-sdks/sink-python-public/commit/b6136b747f88c6095b7ace0c95162858d70b50bb))
* **api:** add request id property to response classes ([#517](https://github.com/stainless-sdks/sink-python-public/issues/517)) ([1105b72](https://github.com/stainless-sdks/sink-python-public/commit/1105b72009dfb5dbd2614b7da3e48acea6bde8e8))
* **api:** update via SDK Studio ([#516](https://github.com/stainless-sdks/sink-python-public/issues/516)) ([6a4c66b](https://github.com/stainless-sdks/sink-python-public/commit/6a4c66b2b1ea9dbd2cba6e6648b99ac34da398ee))
* **client:** add DefaultHttpxClient and DefaultAsyncHttpxClient ([#506](https://github.com/stainless-sdks/sink-python-public/issues/506)) ([53b29c4](https://github.com/stainless-sdks/sink-python-public/commit/53b29c42c34c6676bbf1a16ee1f860a42c5bb93e))
* **errors:** add request_id property ([#512](https://github.com/stainless-sdks/sink-python-public/issues/512)) ([05e8001](https://github.com/stainless-sdks/sink-python-public/commit/05e800144052b8e410fcb493622611cd75a6869f))
* **models:** add to_dict & to_json helper methods ([#507](https://github.com/stainless-sdks/sink-python-public/issues/507)) ([8776d3a](https://github.com/stainless-sdks/sink-python-public/commit/8776d3a6423ae2f621cda62c3ca5d90d1b15b92b))
* **names:** add tests for clashes with Response ([#571](https://github.com/stainless-sdks/sink-python-public/issues/571)) ([b560c15](https://github.com/stainless-sdks/sink-python-public/commit/b560c15abd41b59cadab7ced80f90fbbd1f27ac2))
* **pagination:** add page number without page response test ([#557](https://github.com/stainless-sdks/sink-python-public/issues/557)) ([7ebc70b](https://github.com/stainless-sdks/sink-python-public/commit/7ebc70b9f34b8044daae22f3bd7d098d8fae4ee3))
* propagate resource description field from stainless config to SDK docs ([#547](https://github.com/stainless-sdks/sink-python-public/issues/547)) ([f4f77bb](https://github.com/stainless-sdks/sink-python-public/commit/f4f77bb700c2d75fd0e59caf6c657c43d083f5b1))


### Bug Fixes

* change casing for openapi ([#511](https://github.com/stainless-sdks/sink-python-public/issues/511)) ([fd1cb85](https://github.com/stainless-sdks/sink-python-public/commit/fd1cb859de74a51740a12bf5111653cb97f5540e))
* **client/async:** avoid blocking io call for platform headers ([#569](https://github.com/stainless-sdks/sink-python-public/issues/569)) ([3f35599](https://github.com/stainless-sdks/sink-python-public/commit/3f3559978e26e89ca07c5eecd0a4d98d415e921a))
* **client:** correct logic for line decoding in streaming ([#505](https://github.com/stainless-sdks/sink-python-public/issues/505)) ([34ebb4c](https://github.com/stainless-sdks/sink-python-public/commit/34ebb4ce8ffceebe1a77c4aa4cb5416692e0162b))
* **docs:** fix link to advanced python httpx docs ([#575](https://github.com/stainless-sdks/sink-python-public/issues/575)) ([fe366ec](https://github.com/stainless-sdks/sink-python-public/commit/fe366ecea027dc6a2d9cac841e5436175420d916))
* **internal:** some changes ([#526](https://github.com/stainless-sdks/sink-python-public/issues/526)) ([189cefe](https://github.com/stainless-sdks/sink-python-public/commit/189cefef91a78d4192b6a9f2c2c067a46f7fba40))
* **project:** use absolute github links on PyPi ([#500](https://github.com/stainless-sdks/sink-python-public/issues/500)) ([dd6b3cf](https://github.com/stainless-sdks/sink-python-public/commit/dd6b3cf0f508faba86b263844cef96797fbc22e3))


### Chores

* add `application/octet-stream` examples ([#567](https://github.com/stainless-sdks/sink-python-public/issues/567)) ([c5fbc61](https://github.com/stainless-sdks/sink-python-public/commit/c5fbc6113dfa19fe20959bb2e32accf993ed81dd))
* add missing __all__ definitions ([#563](https://github.com/stainless-sdks/sink-python-public/issues/563)) ([e52235d](https://github.com/stainless-sdks/sink-python-public/commit/e52235d38c4985718eedaffa49d9b159991f9ea3))
* add unknown model type test ([#545](https://github.com/stainless-sdks/sink-python-public/issues/545)) ([ec3d3f6](https://github.com/stainless-sdks/sink-python-public/commit/ec3d3f6e9c501ebc8dc75e40ca4bf5233a659026))
* **ci:** run examples ([#510](https://github.com/stainless-sdks/sink-python-public/issues/510)) ([7d9514d](https://github.com/stainless-sdks/sink-python-public/commit/7d9514dbb4ef4d72244f2cddb1d783546ad9e853))
* **ci:** update rye install location ([#559](https://github.com/stainless-sdks/sink-python-public/issues/559)) ([cb83676](https://github.com/stainless-sdks/sink-python-public/commit/cb836766a2bdd5d09335c6a3844a8806ffa25650))
* **ci:** update rye install location ([#560](https://github.com/stainless-sdks/sink-python-public/issues/560)) ([0b6d536](https://github.com/stainless-sdks/sink-python-public/commit/0b6d53697813db9f87adcb3cd03031bb504bd71f))
* **client:** log response headers in debug mode ([#538](https://github.com/stainless-sdks/sink-python-public/issues/538)) ([50a17ca](https://github.com/stainless-sdks/sink-python-public/commit/50a17cab68c28b1c4e739484049589a6d6242f6a))
* **client:** validate that max_retries is not None ([#503](https://github.com/stainless-sdks/sink-python-public/issues/503)) ([6499b9a](https://github.com/stainless-sdks/sink-python-public/commit/6499b9ae9c667d3c42400ae7f26b583308b0f082))
* **docs:** add SECURITY.md ([#550](https://github.com/stainless-sdks/sink-python-public/issues/550)) ([ac4644f](https://github.com/stainless-sdks/sink-python-public/commit/ac4644f6708bf5c034929e645f5b37ee6bdd91db))
* **examples:** updated stainless config to generate more complex readme examples ([#565](https://github.com/stainless-sdks/sink-python-public/issues/565)) ([20f98cf](https://github.com/stainless-sdks/sink-python-public/commit/20f98cfbd355ddd799827df154506e990ca95e0e))
* fix typo ([#508](https://github.com/stainless-sdks/sink-python-public/issues/508)) ([b5b0824](https://github.com/stainless-sdks/sink-python-public/commit/b5b0824f10e0904c8933690f7149e75fb2140d26))
* **internal:** add link to openapi spec ([#539](https://github.com/stainless-sdks/sink-python-public/issues/539)) ([d23dbd4](https://github.com/stainless-sdks/sink-python-public/commit/d23dbd42a312ebf93f0d72a7c10be8242b1b458d))
* **internal:** add lru_cache helper function ([#513](https://github.com/stainless-sdks/sink-python-public/issues/513)) ([97ca173](https://github.com/stainless-sdks/sink-python-public/commit/97ca173a3b78e5fd46e4a748eafcb0239e753555))
* **internal:** add scripts/test, scripts/mock and add ci job ([#540](https://github.com/stainless-sdks/sink-python-public/issues/540)) ([04e0bde](https://github.com/stainless-sdks/sink-python-public/commit/04e0bde70a6f1bc7d507f7480e61b7d212453604))
* **internal:** add slightly better logging to scripts ([#553](https://github.com/stainless-sdks/sink-python-public/issues/553)) ([fc47fe3](https://github.com/stainless-sdks/sink-python-public/commit/fc47fe3f0f187ff977c95eab1b836749492c2ad3))
* **internal:** ban usage of lru_cache ([#514](https://github.com/stainless-sdks/sink-python-public/issues/514)) ([4ad3280](https://github.com/stainless-sdks/sink-python-public/commit/4ad328050a512e094f3937f72931ec16c5c4de32))
* **internal:** bump mock server version to ~5.8.0 ([#541](https://github.com/stainless-sdks/sink-python-public/issues/541)) ([d4b7051](https://github.com/stainless-sdks/sink-python-public/commit/d4b7051ddc87117b3ea8c8e76c409c4e65d4b43b))
* **internal:** bump pydantic dependency ([#551](https://github.com/stainless-sdks/sink-python-public/issues/551)) ([e7dbde6](https://github.com/stainless-sdks/sink-python-public/commit/e7dbde6a04a5e64fc754b3812d414ea0be47c744))
* **internal:** bump pyright ([#561](https://github.com/stainless-sdks/sink-python-public/issues/561)) ([8fd20cb](https://github.com/stainless-sdks/sink-python-public/commit/8fd20cbeae156515806b4c43fd258f05785ce197))
* **internal:** bump pyright to 1.1.359 ([#515](https://github.com/stainless-sdks/sink-python-public/issues/515)) ([985938a](https://github.com/stainless-sdks/sink-python-public/commit/985938af8f5ff92d74b2c0633e78ef0bc1cceb9b))
* **internal:** defer model build for import latency ([#504](https://github.com/stainless-sdks/sink-python-public/issues/504)) ([5773224](https://github.com/stainless-sdks/sink-python-public/commit/577322480eefe08884e50cac2db95faaf1197414))
* **internal:** fix package name in README ([#521](https://github.com/stainless-sdks/sink-python-public/issues/521)) ([34408e5](https://github.com/stainless-sdks/sink-python-public/commit/34408e5532c1df4baae006369cea8a6112596883))
* **internal:** fix spec loader ([#509](https://github.com/stainless-sdks/sink-python-public/issues/509)) ([c9629db](https://github.com/stainless-sdks/sink-python-public/commit/c9629db50550574955cb4c1dd44085ac9f420d7e))
* **internal:** minor fixes ([#522](https://github.com/stainless-sdks/sink-python-public/issues/522)) ([ad55b4d](https://github.com/stainless-sdks/sink-python-public/commit/ad55b4df610eaab3bbabb440863225a1122a890d))
* **internal:** minor formatting changes ([#555](https://github.com/stainless-sdks/sink-python-public/issues/555)) ([8be15b5](https://github.com/stainless-sdks/sink-python-public/commit/8be15b5447e4e8096a92597507e4ad14c7653ced))
* **internal:** minor reformatting ([#535](https://github.com/stainless-sdks/sink-python-public/issues/535)) ([c0c3b2b](https://github.com/stainless-sdks/sink-python-public/commit/c0c3b2b1c6ec4c21d80b279f79eba11188d4092d))
* **internal:** reformat imports ([#534](https://github.com/stainless-sdks/sink-python-public/issues/534)) ([c1f09bc](https://github.com/stainless-sdks/sink-python-public/commit/c1f09bcbd75dc63988d6d0c1ee5e03e935d22a8f))
* **internal:** restructure imports ([#527](https://github.com/stainless-sdks/sink-python-public/issues/527)) ([3e496d5](https://github.com/stainless-sdks/sink-python-public/commit/3e496d5e0e10ba1f7a959f7f6b2c5e66f847b0d2))
* **internal:** sync updates ([#530](https://github.com/stainless-sdks/sink-python-public/issues/530)) ([211d694](https://github.com/stainless-sdks/sink-python-public/commit/211d694747de4ca9410bfc4bbd630cb39509cbcf))
* **internal:** update bootstrap script ([#564](https://github.com/stainless-sdks/sink-python-public/issues/564)) ([e7436c3](https://github.com/stainless-sdks/sink-python-public/commit/e7436c3b876e60de2800ea01a81d2f1de2b4ef23))
* **internal:** update test helper function ([#533](https://github.com/stainless-sdks/sink-python-public/issues/533)) ([faf34e4](https://github.com/stainless-sdks/sink-python-public/commit/faf34e44de734b0d332472a5de5f56dd7769ea2e))
* **internal:** updates ([#524](https://github.com/stainless-sdks/sink-python-public/issues/524)) ([c103c9b](https://github.com/stainless-sdks/sink-python-public/commit/c103c9bee531f7623d5168c7eb0685d5eaf1dabe))
* **internal:** updates to repo ([#552](https://github.com/stainless-sdks/sink-python-public/issues/552)) ([96c4232](https://github.com/stainless-sdks/sink-python-public/commit/96c42323fabd93ce235b6f21acbda8282420d2c0))
* **internal:** use actions/checkout@v4 for codeflow ([#532](https://github.com/stainless-sdks/sink-python-public/issues/532)) ([4c895ec](https://github.com/stainless-sdks/sink-python-public/commit/4c895ec550db2da591e32d32987d6b3d7d523b0c))
* modified schema for testing ([#558](https://github.com/stainless-sdks/sink-python-public/issues/558)) ([43c3d5b](https://github.com/stainless-sdks/sink-python-public/commit/43c3d5b3608622cf62402a698fb8e685ecd48a1e))
* rebuild project due to codegen change ([#518](https://github.com/stainless-sdks/sink-python-public/issues/518)) ([921b3ea](https://github.com/stainless-sdks/sink-python-public/commit/921b3eaf40ef0233a66d1e86f3347bd962799104))
* rebuild project due to codegen change ([#519](https://github.com/stainless-sdks/sink-python-public/issues/519)) ([78c14f7](https://github.com/stainless-sdks/sink-python-public/commit/78c14f73306f6d76a145b7d22401b2b975bcfea7))
* rebuild project due to codegen change ([#520](https://github.com/stainless-sdks/sink-python-public/issues/520)) ([e0add45](https://github.com/stainless-sdks/sink-python-public/commit/e0add45972cf126132383dfe26bf097214631380))
* rebuild project due to codegen change ([#523](https://github.com/stainless-sdks/sink-python-public/issues/523)) ([3ba6815](https://github.com/stainless-sdks/sink-python-public/commit/3ba68157ba2122652f3d1deee982beb0eab45e9e))
* rebuild project due to codegen change ([#525](https://github.com/stainless-sdks/sink-python-public/issues/525)) ([3f542d4](https://github.com/stainless-sdks/sink-python-public/commit/3f542d4a0fe6ce1b74cc68a04d4fad209337ad36))
* remove custom code ([#566](https://github.com/stainless-sdks/sink-python-public/issues/566)) ([e07a224](https://github.com/stainless-sdks/sink-python-public/commit/e07a224048f88847b90997b2bcb0c474c2b0d70c))
* rename resource types ([#529](https://github.com/stainless-sdks/sink-python-public/issues/529)) ([63ffa43](https://github.com/stainless-sdks/sink-python-public/commit/63ffa43d9a8cfef66f392128e40bddd1d9018747))
* test change ([#498](https://github.com/stainless-sdks/sink-python-public/issues/498)) ([b022f15](https://github.com/stainless-sdks/sink-python-public/commit/b022f1519606973b6d65fa2667e370d86db92c9b))
* test for request body params mixing known and unknown properties ([#554](https://github.com/stainless-sdks/sink-python-public/issues/554)) ([e62db6a](https://github.com/stainless-sdks/sink-python-public/commit/e62db6a9e82f4e671c7ffe8fefccd778013bf102))
* tests for allOf ([#536](https://github.com/stainless-sdks/sink-python-public/issues/536)) ([e6b7c77](https://github.com/stainless-sdks/sink-python-public/commit/e6b7c7760d9230bc04a5de4c735b464536312527))
* tests for resource documentation propagation ([#549](https://github.com/stainless-sdks/sink-python-public/issues/549)) ([c919282](https://github.com/stainless-sdks/sink-python-public/commit/c9192825d797546803abe869f6ffca72b853600d))
* **tests:** add date-time examples ([#537](https://github.com/stainless-sdks/sink-python-public/issues/537)) ([fafb27e](https://github.com/stainless-sdks/sink-python-public/commit/fafb27e71c703c3cb110b9f3f802e25c5f970271))
* **tests:** fix test client class name ([#542](https://github.com/stainless-sdks/sink-python-public/issues/542)) ([9e5cf64](https://github.com/stainless-sdks/sink-python-public/commit/9e5cf64cd1b1ccba20277b0efd41a2ff2b4bb015))
* **tests:** rename test file ([#531](https://github.com/stainless-sdks/sink-python-public/issues/531)) ([9463e11](https://github.com/stainless-sdks/sink-python-public/commit/9463e114a340693253f8a1715091e6fb024d7fdb))
* **tests:** update some example values ([#556](https://github.com/stainless-sdks/sink-python-public/issues/556)) ([94ec6ba](https://github.com/stainless-sdks/sink-python-public/commit/94ec6ba8a7fd9c3cdcc3a4f7f272fe4db2df5e12))
* update spec URL ([#548](https://github.com/stainless-sdks/sink-python-public/issues/548)) ([6f8d034](https://github.com/stainless-sdks/sink-python-public/commit/6f8d034332bc05f35806ec2eb6c3e4a71fb4fe23))


### Documentation

* **contributing:** update references to rye-up.com ([#562](https://github.com/stainless-sdks/sink-python-public/issues/562)) ([932fe19](https://github.com/stainless-sdks/sink-python-public/commit/932fe1981e86c50192ed9075e3e4a4652d0a08f8))
* **readme:** fix misleading timeout example value ([#543](https://github.com/stainless-sdks/sink-python-public/issues/543)) ([2e1090a](https://github.com/stainless-sdks/sink-python-public/commit/2e1090a020e09a773a767367f0ffe502a87029b9))

## 1.21.0-beta.3 (2024-03-28)

Full Changelog: [v1.21.0-beta.2...v1.21.0-beta.3](https://github.com/stainless-sdks/sink-python-public/compare/v1.21.0-beta.2...v1.21.0-beta.3)

### Features

* **api:** updates ([#489](https://github.com/stainless-sdks/sink-python-public/issues/489)) ([690dec8](https://github.com/stainless-sdks/sink-python-public/commit/690dec80cffb86b7118b661cc612a97c06218368))
* **package:** export default constants ([#497](https://github.com/stainless-sdks/sink-python-public/issues/497)) ([05ee4e3](https://github.com/stainless-sdks/sink-python-public/commit/05ee4e348a7fa8907acd869cbf0541232806f257))


### Bug Fixes

* add support for path params with colon suffix ([#481](https://github.com/stainless-sdks/sink-python-public/issues/481)) ([2a8ee7b](https://github.com/stainless-sdks/sink-python-public/commit/2a8ee7bad64b63dad910c47d7ccd912dbccea61c))
* revert regression with 3.7 support ([#495](https://github.com/stainless-sdks/sink-python-public/issues/495)) ([fc894fc](https://github.com/stainless-sdks/sink-python-public/commit/fc894fcd70cbefcb8e3cf0f207754cb34da4a66c))


### Performance Improvements

* cache TypeAdapters ([#484](https://github.com/stainless-sdks/sink-python-public/issues/484)) ([64a2322](https://github.com/stainless-sdks/sink-python-public/commit/64a23226f8a2fa6d9bd6ccb68e598402bb1e7e7a))


### Chores

* **internal:** formatting change ([#491](https://github.com/stainless-sdks/sink-python-public/issues/491)) ([e3e0bdf](https://github.com/stainless-sdks/sink-python-public/commit/e3e0bdf3a403163f98ef86ab07096dc56781f33f))
* **internal:** loosen input type for util function ([#487](https://github.com/stainless-sdks/sink-python-public/issues/487)) ([df618a9](https://github.com/stainless-sdks/sink-python-public/commit/df618a92804707f6737a944b386cfab62222ec8f))
* **internal:** qualify reference to non-primitive variants ([#483](https://github.com/stainless-sdks/sink-python-public/issues/483)) ([f6da5ab](https://github.com/stainless-sdks/sink-python-public/commit/f6da5ab4a2c1f431607ce50e522c0f928f89603d))
* **internal:** safely rename resource directories using reserved keywords ([#482](https://github.com/stainless-sdks/sink-python-public/issues/482)) ([4ddf239](https://github.com/stainless-sdks/sink-python-public/commit/4ddf239076b67849f5dffad5734ceb48f7f4f543))
* **internal:** update generated pragma comment ([#486](https://github.com/stainless-sdks/sink-python-public/issues/486)) ([9ee469b](https://github.com/stainless-sdks/sink-python-public/commit/9ee469b6d424d366358a91954c8913954ed1b1bd))
* test preview PRs ([#496](https://github.com/stainless-sdks/sink-python-public/issues/496)) ([070cf77](https://github.com/stainless-sdks/sink-python-public/commit/070cf774c4a64a2673d03082e0c46c94a62105ea))
* **types:** include discriminators in unions ([#479](https://github.com/stainless-sdks/sink-python-public/issues/479)) ([06f5291](https://github.com/stainless-sdks/sink-python-public/commit/06f5291f1d172e58ca925ea155f68b326d28bada))
* **types:** move object variants at the end of a union ([#494](https://github.com/stainless-sdks/sink-python-public/issues/494)) ([385e974](https://github.com/stainless-sdks/sink-python-public/commit/385e9748a714365f8c862c70cb6730cee9de2baa))


### Documentation

* **contributing:** fix typo ([#493](https://github.com/stainless-sdks/sink-python-public/issues/493)) ([156d201](https://github.com/stainless-sdks/sink-python-public/commit/156d201e8210fe559f54a19290f0a5cfd97d5f83))
* fix typo in CONTRIBUTING.md ([#485](https://github.com/stainless-sdks/sink-python-public/issues/485)) ([c9a2b88](https://github.com/stainless-sdks/sink-python-public/commit/c9a2b8863ce727fde65eabebc6b1e6e7eb62dbb3))
* **readme:** consistent use of sentence case in headings ([#488](https://github.com/stainless-sdks/sink-python-public/issues/488)) ([1408c2b](https://github.com/stainless-sdks/sink-python-public/commit/1408c2b5f36c961c6b9c53acbfc8664d5e9ea92d))
* **readme:** document how to make undocumented requests ([#490](https://github.com/stainless-sdks/sink-python-public/issues/490)) ([9f017b7](https://github.com/stainless-sdks/sink-python-public/commit/9f017b7d59610b6b367a65c77bbdfed6657fc651))
* **readme:** update package description ([#492](https://github.com/stainless-sdks/sink-python-public/issues/492)) ([0fd4f81](https://github.com/stainless-sdks/sink-python-public/commit/0fd4f81f28c8bbf7a1aabee6bb59f469f6f785b4))

## 1.21.0-beta.2 (2024-03-11)

Full Changelog: [v1.21.0-beta.1...v1.21.0-beta.2](https://github.com/stainless-sdks/sink-python-public/compare/v1.21.0-beta.1...v1.21.0-beta.2)

### Features

* add body param root with extra params ([#456](https://github.com/stainless-sdks/sink-python-public/issues/456)) ([dfe6b67](https://github.com/stainless-sdks/sink-python-public/commit/dfe6b67eff62ebe6f76506c76aa0be3139ee8179))
* add more pagination tests ([#447](https://github.com/stainless-sdks/sink-python-public/issues/447)) ([ccc4467](https://github.com/stainless-sdks/sink-python-public/commit/ccc44679a1e81473dc7aafa8b3def811965da9e8))
* add nested pagination array case ([#458](https://github.com/stainless-sdks/sink-python-public/issues/458)) ([c8a6229](https://github.com/stainless-sdks/sink-python-public/commit/c8a62295069bd7b5c292a852b37edf361ea93982))
* **api:** omit platform headers ([#461](https://github.com/stainless-sdks/sink-python-public/issues/461)) ([76f41a8](https://github.com/stainless-sdks/sink-python-public/commit/76f41a8e91e7907a79ca01dbfa6ee4bc772030c6))
* **api:** reduce unnecessary union ([#474](https://github.com/stainless-sdks/sink-python-public/issues/474)) ([4652b32](https://github.com/stainless-sdks/sink-python-public/commit/4652b3232b40d6c07f57a5f93d0d428d2dec32d5))


### Bug Fixes

* **docs:** better comment escape code handling ([#460](https://github.com/stainless-sdks/sink-python-public/issues/460)) ([bcb0ea8](https://github.com/stainless-sdks/sink-python-public/commit/bcb0ea8534b1501e29f6f3e659d04163a4d8a2e0))
* **types:** loosen most List params types to Iterable ([#446](https://github.com/stainless-sdks/sink-python-public/issues/446)) ([7d2b777](https://github.com/stainless-sdks/sink-python-public/commit/7d2b77797b86cda9851f40c143b0f7f80390c717))
* use qs.stringify for complex query parameters ([#473](https://github.com/stainless-sdks/sink-python-public/issues/473)) ([61b1dce](https://github.com/stainless-sdks/sink-python-public/commit/61b1dcef9677902f2bddca985e43542608178001))


### Chores

* add test for base64 params ([#470](https://github.com/stainless-sdks/sink-python-public/issues/470)) ([d3d49a3](https://github.com/stainless-sdks/sink-python-public/commit/d3d49a34d580657b211cb4e04be6e63796c12004))
* **client:** improve error message for invalid http_client argument ([#471](https://github.com/stainless-sdks/sink-python-public/issues/471)) ([a9e4c82](https://github.com/stainless-sdks/sink-python-public/commit/a9e4c8289993b80aff7213733d5f2273b3d4a116))
* **client:** use correct accept headers for binary data ([#454](https://github.com/stainless-sdks/sink-python-public/issues/454)) ([6d4b21c](https://github.com/stainless-sdks/sink-python-public/commit/6d4b21c87c675644e2e99bf02c5162d9738d9855))
* docs changes ([#451](https://github.com/stainless-sdks/sink-python-public/issues/451)) ([2aa0a8b](https://github.com/stainless-sdks/sink-python-public/commit/2aa0a8b216338b85a1f24a4c3f475f9fcb1c1470))
* **docs:** mention install from git repo ([#465](https://github.com/stainless-sdks/sink-python-public/issues/465)) ([3df7b1a](https://github.com/stainless-sdks/sink-python-public/commit/3df7b1a89cc461ab83584d71f4608282c5a8aeb0))
* export NOT_GIVEN sentinel value ([#477](https://github.com/stainless-sdks/sink-python-public/issues/477)) ([4de7ad4](https://github.com/stainless-sdks/sink-python-public/commit/4de7ad4f7d4ddf9843f96315bd3ca24703369e29))
* **internal:** add lint command ([#445](https://github.com/stainless-sdks/sink-python-public/issues/445)) ([905b43c](https://github.com/stainless-sdks/sink-python-public/commit/905b43c1ff7d9dccceeb930594affa06137a2b70))
* **internal:** bump pyright ([#459](https://github.com/stainless-sdks/sink-python-public/issues/459)) ([0a27fb9](https://github.com/stainless-sdks/sink-python-public/commit/0a27fb997342d576a04d67dccc38c3df9d08a25f))
* **internal:** bump pyright ([#475](https://github.com/stainless-sdks/sink-python-public/issues/475)) ([2618ec4](https://github.com/stainless-sdks/sink-python-public/commit/2618ec43adafe1ed3df23832e90e46fbe7e38216))
* **internal:** bump rye to v0.24.0 ([#455](https://github.com/stainless-sdks/sink-python-public/issues/455)) ([2f03d7c](https://github.com/stainless-sdks/sink-python-public/commit/2f03d7cb110478e3c686c7b4c2f2ada359a5873c))
* **internal:** improve deserialisation of discriminated unions ([#478](https://github.com/stainless-sdks/sink-python-public/issues/478)) ([114208d](https://github.com/stainless-sdks/sink-python-public/commit/114208d2683eca84efc675f1066539d997294d40))
* **internal:** minor core client restructuring ([#462](https://github.com/stainless-sdks/sink-python-public/issues/462)) ([ead517f](https://github.com/stainless-sdks/sink-python-public/commit/ead517f3cccaba81938f2755db270e4f64e617b1))
* **internal:** refactor release environment script ([#452](https://github.com/stainless-sdks/sink-python-public/issues/452)) ([ab423a2](https://github.com/stainless-sdks/sink-python-public/commit/ab423a2ea523422acf4173b2b770efd51a55e485))
* **internal:** split up transforms into sync / async ([#468](https://github.com/stainless-sdks/sink-python-public/issues/468)) ([8fe4b21](https://github.com/stainless-sdks/sink-python-public/commit/8fe4b215a83cf41760e7a0b81ef1efde48996845))
* **internal:** support more input types ([#469](https://github.com/stainless-sdks/sink-python-public/issues/469)) ([27a19e3](https://github.com/stainless-sdks/sink-python-public/commit/27a19e35ef2f02a09b5efb376e94f05325298c6f))
* **internal:** support parsing Annotated types ([#476](https://github.com/stainless-sdks/sink-python-public/issues/476)) ([1b0ac21](https://github.com/stainless-sdks/sink-python-public/commit/1b0ac21fdec3d7afdf8db7f8bb38af343a27ef05))
* **internal:** support serialising iterable types ([#443](https://github.com/stainless-sdks/sink-python-public/issues/443)) ([539ea65](https://github.com/stainless-sdks/sink-python-public/commit/539ea65ffde7f564ef539cd65f5d28105361a025))
* **internal:** update deps ([#457](https://github.com/stainless-sdks/sink-python-public/issues/457)) ([63cb52f](https://github.com/stainless-sdks/sink-python-public/commit/63cb52f0fddd5f5b36a7b0d5f6ee79c39f8e5700))
* move to sink_sdk import for testing config ([#463](https://github.com/stainless-sdks/sink-python-public/issues/463)) ([c20e59a](https://github.com/stainless-sdks/sink-python-public/commit/c20e59a3d72887617395c745842b90d16e00ea97))
* test methods not included in api.md ([#467](https://github.com/stainless-sdks/sink-python-public/issues/467)) ([ceed48c](https://github.com/stainless-sdks/sink-python-public/commit/ceed48cbe5f0679ef160ebb472a7f933c2160ac5))
* test resources not included in api.md ([#466](https://github.com/stainless-sdks/sink-python-public/issues/466)) ([3543f90](https://github.com/stainless-sdks/sink-python-public/commit/3543f906675eca2445eebb6bca3262b1a7a639c4))
* updates ([#449](https://github.com/stainless-sdks/sink-python-public/issues/449)) ([20b76c5](https://github.com/stainless-sdks/sink-python-public/commit/20b76c54e23758f246135d996d16ebf63e76837b))


### Documentation

* add CONTRIBUTING.md ([#448](https://github.com/stainless-sdks/sink-python-public/issues/448)) ([65063e5](https://github.com/stainless-sdks/sink-python-public/commit/65063e5666a5063b15a1417c911501d006dd29f3))
* **contributing:** improve wording ([#464](https://github.com/stainless-sdks/sink-python-public/issues/464)) ([9924c49](https://github.com/stainless-sdks/sink-python-public/commit/9924c49fa88f0dfb60ec75de68f22ed262f4a578))
* **readme:** fix async streaming snippet ([#472](https://github.com/stainless-sdks/sink-python-public/issues/472)) ([0939172](https://github.com/stainless-sdks/sink-python-public/commit/0939172eedbfdfbb0f357866de99424f0179b80a))

## 1.21.0-beta.1 (2024-02-04)

Full Changelog: [v1.20.1-beta.1...v1.21.0-beta.1](https://github.com/stainless-sdks/sink-python-public/compare/v1.20.1-beta.1...v1.21.0-beta.1)

### Features

* **client:** enable follow redirects by default ([#435](https://github.com/stainless-sdks/sink-python-public/issues/435)) ([0467f7e](https://github.com/stainless-sdks/sink-python-public/commit/0467f7e503a10d3a11d35f059e89b355953bcad4))
* **client:** support parsing custom response types ([#438](https://github.com/stainless-sdks/sink-python-public/issues/438)) ([77b7c9b](https://github.com/stainless-sdks/sink-python-public/commit/77b7c9b2d59179feca69a79ab59107238be9fa81))


### Bug Fixes

* prevent crash when platform.architecture() is not allowed ([#442](https://github.com/stainless-sdks/sink-python-public/issues/442)) ([6883a9e](https://github.com/stainless-sdks/sink-python-public/commit/6883a9e769422e534beb23f1010073b842d2b368))


### Chores

* add more test cases for leading _ props ([#432](https://github.com/stainless-sdks/sink-python-public/issues/432)) ([29bf695](https://github.com/stainless-sdks/sink-python-public/commit/29bf6958eb6b10ca42a889b5056fb71380cf971e))
* add test for const enums ([#440](https://github.com/stainless-sdks/sink-python-public/issues/440)) ([5f04391](https://github.com/stainless-sdks/sink-python-public/commit/5f04391fd297cc61fcac4abcaca1551ea9a906fb))
* **internal:** cast type in mocked test ([#439](https://github.com/stainless-sdks/sink-python-public/issues/439)) ([53a178e](https://github.com/stainless-sdks/sink-python-public/commit/53a178e6e16625795cf90a8e14cda643dfc85790))
* **internal:** enable ruff type checking misuse lint rule ([#437](https://github.com/stainless-sdks/sink-python-public/issues/437)) ([8414d33](https://github.com/stainless-sdks/sink-python-public/commit/8414d33b1c47362e99576f02d029a3d32a29c349))
* **internal:** support multipart data with overlapping keys ([#436](https://github.com/stainless-sdks/sink-python-public/issues/436)) ([2ad11aa](https://github.com/stainless-sdks/sink-python-public/commit/2ad11aa13badc1eec2372294a5ec74dbe7c17dec))
* **internal:** support pre-release versioning ([#441](https://github.com/stainless-sdks/sink-python-public/issues/441)) ([dd4841c](https://github.com/stainless-sdks/sink-python-public/commit/dd4841c863752c1869b02e1bc570bce34dc905b0))


### Refactors

* remove unnecessary builtin import ([#434](https://github.com/stainless-sdks/sink-python-public/issues/434)) ([c378c65](https://github.com/stainless-sdks/sink-python-public/commit/c378c65a3a1c0e6da81807ed8cf18feeaa814d53))

## 1.20.1-beta.1 (2024-01-18)

Full Changelog: [v1.20.0-beta.1...v1.20.1-beta.1](https://github.com/stainless-sdks/sink-python-public/compare/v1.20.0-beta.1...v1.20.1-beta.1)

### Bug Fixes

* add test for case when every param in a body is read-only ([#430](https://github.com/stainless-sdks/sink-python-public/issues/430)) ([5c0ac10](https://github.com/stainless-sdks/sink-python-public/commit/5c0ac1013d40e220d78a068c1559a0255204f4b2))

## 1.20.0-beta.1 (2024-01-18)

Full Changelog: [v1.19.0...v1.20.0-beta.1](https://github.com/stainless-sdks/sink-python-public/compare/v1.19.0...v1.20.0-beta.1)

### Features

* add and test `send_as_query_param` and `send_as_path_param` ([#422](https://github.com/stainless-sdks/sink-python-public/issues/422)) ([fcb88e9](https://github.com/stainless-sdks/sink-python-public/commit/fcb88e9461e8f55d7e8da778a553f5983bd7d959))
* add path param enum test ([#423](https://github.com/stainless-sdks/sink-python-public/issues/423)) ([bc8b8e7](https://github.com/stainless-sdks/sink-python-public/commit/bc8b8e7ef702f53a269870d75de6111198701e69))
* add test for resource with only custom methods ([#421](https://github.com/stainless-sdks/sink-python-public/issues/421)) ([261334f](https://github.com/stainless-sdks/sink-python-public/commit/261334f1c47a6944deea5a947f2cc1fe9d9a342c))
* **client:** add support for streaming raw responses ([#420](https://github.com/stainless-sdks/sink-python-public/issues/420)) ([22aa937](https://github.com/stainless-sdks/sink-python-public/commit/22aa937735b242f2fbeb430a5fc61f92602691f6))


### Chores

* **internal:** fix typing util function ([#425](https://github.com/stainless-sdks/sink-python-public/issues/425)) ([f2a332a](https://github.com/stainless-sdks/sink-python-public/commit/f2a332a0d64f8b4d88bc0f9ed3489c969d04adef))
* **internal:** remove redundant client test ([#426](https://github.com/stainless-sdks/sink-python-public/issues/426)) ([1c6389c](https://github.com/stainless-sdks/sink-python-public/commit/1c6389c1b0441a460528fb19e40a716e0a4f5149))
* **internal:** share client instances between all tests ([#429](https://github.com/stainless-sdks/sink-python-public/issues/429)) ([c87da80](https://github.com/stainless-sdks/sink-python-public/commit/c87da806b47de6b7f57a22bf7c031e75eda48a13))
* **internal:** speculative retry-after-ms support ([#427](https://github.com/stainless-sdks/sink-python-public/issues/427)) ([622c5c0](https://github.com/stainless-sdks/sink-python-public/commit/622c5c0fac4aae21ddbe3ecfb22cfdcdda3b3099))
* **internal:** updates to proxy helper ([#424](https://github.com/stainless-sdks/sink-python-public/issues/424)) ([41a41ef](https://github.com/stainless-sdks/sink-python-public/commit/41a41ef5e5cb244183d0087f3f4f565f7d00f939))
* lazy load raw resource class properties ([#428](https://github.com/stainless-sdks/sink-python-public/issues/428)) ([b782293](https://github.com/stainless-sdks/sink-python-public/commit/b782293af7ccd33c4e7bb02ab7334e5e1a60a57e))


### Documentation

* **readme:** improve api reference ([#418](https://github.com/stainless-sdks/sink-python-public/issues/418)) ([7484d19](https://github.com/stainless-sdks/sink-python-public/commit/7484d1934f1a0835e966523f067334bcaceb4a58))

## 1.19.0 (2024-01-10)

Full Changelog: [v1.18.0...v1.19.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.18.0...v1.19.0)

### Features

* **types:** add test for unknown paginated items ([#414](https://github.com/stainless-sdks/sink-python-public/issues/414)) ([afaec95](https://github.com/stainless-sdks/sink-python-public/commit/afaec95169f9a2cf9d0f8badf91bf30afdde05f2))


### Chores

* add .keep files for examples and custom code directories ([#416](https://github.com/stainless-sdks/sink-python-public/issues/416)) ([e675a0c](https://github.com/stainless-sdks/sink-python-public/commit/e675a0c33e4867149b534c741b57fd366a235fbf))
* **client:** improve debug logging for failed requests ([#417](https://github.com/stainless-sdks/sink-python-public/issues/417)) ([690a83d](https://github.com/stainless-sdks/sink-python-public/commit/690a83d3d114b320f21a03aa0af5a6ef31b50cb5))

## 1.18.0 (2024-01-05)

Full Changelog: [v1.17.0...v1.18.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.17.0...v1.18.0)

### Features

* add test case for models using $ref syntax ([#411](https://github.com/stainless-sdks/sink-python-public/issues/411)) ([bf1cb91](https://github.com/stainless-sdks/sink-python-public/commit/bf1cb91997190eac6b3f245e7095aca89aaa11f1))


### Bug Fixes

* escape interface names, fix pagination types ([#413](https://github.com/stainless-sdks/sink-python-public/issues/413)) ([e0ada8d](https://github.com/stainless-sdks/sink-python-public/commit/e0ada8dfb49ba2148e6182423fca5df1c6c047e1))


### Chores

* **internal:** bump license ([#408](https://github.com/stainless-sdks/sink-python-public/issues/408)) ([ef91d8c](https://github.com/stainless-sdks/sink-python-public/commit/ef91d8c29655a009ad7225bcfff4e6a2211e4b98))
* **internal:** replace isort with ruff ([#410](https://github.com/stainless-sdks/sink-python-public/issues/410)) ([0a7cfc7](https://github.com/stainless-sdks/sink-python-public/commit/0a7cfc78468d74262366f5eb284fe8298a8e1ef2))
* use property declarations for resource members ([#412](https://github.com/stainless-sdks/sink-python-public/issues/412)) ([8e4cd34](https://github.com/stainless-sdks/sink-python-public/commit/8e4cd349d5673426b9856150aca4306d84e18a08))

## 1.17.0 (2023-12-28)

Full Changelog: [v1.16.0...v1.17.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.16.0...v1.17.0)

### Features

* add test for fake pages ([#402](https://github.com/stainless-sdks/sink-python-public/issues/402)) ([cb8e7e6](https://github.com/stainless-sdks/sink-python-public/commit/cb8e7e61e41fc6b6f94b156ff8f48ef1500aa86f))


### Bug Fixes

* better typing for parameters when `x-stainless-empty-object: true` ([#403](https://github.com/stainless-sdks/sink-python-public/issues/403)) ([d69eb4a](https://github.com/stainless-sdks/sink-python-public/commit/d69eb4a09cfc2c6bd5bb0f7b716c24befd33ce44))
* **client:** correctly use custom http client auth ([#407](https://github.com/stainless-sdks/sink-python-public/issues/407)) ([adabba5](https://github.com/stainless-sdks/sink-python-public/commit/adabba57b3b1ba6ea8b673b43402e7e40a4a26e0))


### Chores

* **internal:** add bin script ([#404](https://github.com/stainless-sdks/sink-python-public/issues/404)) ([9b4f1c0](https://github.com/stainless-sdks/sink-python-public/commit/9b4f1c09f8da7bbd05c7fa0003ddb073a33aef9d))
* **internal:** bump typing-extensions ([#401](https://github.com/stainless-sdks/sink-python-public/issues/401)) ([6b541d5](https://github.com/stainless-sdks/sink-python-public/commit/6b541d594a1338fdd6dabe115e2e970fffd2a2f7))
* **internal:** fix typos ([#400](https://github.com/stainless-sdks/sink-python-public/issues/400)) ([b2ccc5f](https://github.com/stainless-sdks/sink-python-public/commit/b2ccc5fa7cfa5267d2e3c1b8fc855d9568dff042))
* **internal:** minor utils restructuring ([#399](https://github.com/stainless-sdks/sink-python-public/issues/399)) ([36229d2](https://github.com/stainless-sdks/sink-python-public/commit/36229d27148c45f0ec889fbbbefafd6b2170f7a3))
* **internal:** updates to base client ([#397](https://github.com/stainless-sdks/sink-python-public/issues/397)) ([c849f2e](https://github.com/stainless-sdks/sink-python-public/commit/c849f2e9381977c50d8fcd993ec9d4cb8666d209))
* **internal:** use ruff instead of black for formatting ([#406](https://github.com/stainless-sdks/sink-python-public/issues/406)) ([e3d12c7](https://github.com/stainless-sdks/sink-python-public/commit/e3d12c71c68f1fe94bf30a7fcd16a6a2eff35f31))

## 1.16.0 (2023-12-18)

Full Changelog: [v1.15.2...v1.16.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.15.2...v1.16.0)

### Features

* add test case for reserved params names ([#396](https://github.com/stainless-sdks/sink-python-public/issues/396)) ([63ef425](https://github.com/stainless-sdks/sink-python-public/commit/63ef425e0103cfd98e735b06c758eb7e2e2a778c))
* add test for binary endpoint with a path param ([#395](https://github.com/stainless-sdks/sink-python-public/issues/395)) ([af6c68b](https://github.com/stainless-sdks/sink-python-public/commit/af6c68b9f43bb3588beb6ea83363e69be9c67a2a))


### Bug Fixes

* better typing for parameters when request body is defined as empty ([#394](https://github.com/stainless-sdks/sink-python-public/issues/394)) ([63ee967](https://github.com/stainless-sdks/sink-python-public/commit/63ee967b8a202c4923fcaf8a155b57fddcf20ff9))


### Chores

* uses Stainless GitHub App for codeflow ([#388](https://github.com/stainless-sdks/sink-python-public/issues/388)) ([89718eb](https://github.com/stainless-sdks/sink-python-public/commit/89718eb69cde6486c10b58f003d5869afb68c145))


### Documentation

* improve README timeout comment ([#390](https://github.com/stainless-sdks/sink-python-public/issues/390)) ([d44cb4f](https://github.com/stainless-sdks/sink-python-public/commit/d44cb4f29f5ec9e87ec66a667dde4d40b915342a))


### Refactors

* **client:** simplify cleanup ([#391](https://github.com/stainless-sdks/sink-python-public/issues/391)) ([eee21b2](https://github.com/stainless-sdks/sink-python-public/commit/eee21b2d4cc1f64ea1621dc00a14f9a961122446))
* remove unused model types used in params ([#393](https://github.com/stainless-sdks/sink-python-public/issues/393)) ([2f9d6ab](https://github.com/stainless-sdks/sink-python-public/commit/2f9d6abe303d061767336c40fce6b852958ea59c))
* simplify internal error handling ([#392](https://github.com/stainless-sdks/sink-python-public/issues/392)) ([927e01b](https://github.com/stainless-sdks/sink-python-public/commit/927e01b1c4b6a6dfee084d78723afbd20f1c9af4))

## 1.15.2 (2023-12-08)

Full Changelog: [v1.15.1...v1.15.2](https://github.com/stainless-sdks/sink-python-public/compare/v1.15.1...v1.15.2)

### Bug Fixes

* avoid leaking memory when Client.with_options is used ([#386](https://github.com/stainless-sdks/sink-python-public/issues/386)) ([44bf594](https://github.com/stainless-sdks/sink-python-public/commit/44bf594f4e3b0080d57d36fedacfb041310e7887))

## 1.15.1 (2023-12-08)

Full Changelog: [v1.15.0...v1.15.1](https://github.com/stainless-sdks/sink-python-public/compare/v1.15.0...v1.15.1)

### Bug Fixes

* **errors:** properly assign APIError.body ([#384](https://github.com/stainless-sdks/sink-python-public/issues/384)) ([c239fe9](https://github.com/stainless-sdks/sink-python-public/commit/c239fe9c4658e3b977506868c3b003f0f85b7ff9))

## 1.15.0 (2023-12-07)

Full Changelog: [v1.14.0...v1.15.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.14.0...v1.15.0)

### Features

* add support for pagination refs ([#379](https://github.com/stainless-sdks/sink-python-public/issues/379)) ([7e7d15c](https://github.com/stainless-sdks/sink-python-public/commit/7e7d15cfdfae4bc95d736cb34f836b172b88f8f7))
* **pagination:** add test for cursor_id without previous cursor param ([#377](https://github.com/stainless-sdks/sink-python-public/issues/377)) ([5772bd5](https://github.com/stainless-sdks/sink-python-public/commit/5772bd5d1234e1ec56172f0d5a6c2a0b959b9a59))


### Chores

* **internal:** enable more lint rules ([#383](https://github.com/stainless-sdks/sink-python-public/issues/383)) ([9024110](https://github.com/stainless-sdks/sink-python-public/commit/902411068fcbfddd44c0a46d8e688026cb960f1f))
* **internal:** reformat imports ([#381](https://github.com/stainless-sdks/sink-python-public/issues/381)) ([6a07586](https://github.com/stainless-sdks/sink-python-public/commit/6a075862cd6e4f152534d44a1fdbde5990002f44))
* **internal:** reformat imports ([#382](https://github.com/stainless-sdks/sink-python-public/issues/382)) ([a2205fa](https://github.com/stainless-sdks/sink-python-public/commit/a2205fa95c1f27f0a7df4caea3415d5313b88534))

## 1.14.0 (2023-12-04)

Full Changelog: [v1.13.0...v1.14.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.13.0...v1.14.0)

### Features

* **pagination:** add support for top-level arrays ([#375](https://github.com/stainless-sdks/sink-python-public/issues/375)) ([22ac11b](https://github.com/stainless-sdks/sink-python-public/commit/22ac11b6b3414afcb8dcddff537b306c1acc5c88))
* **pagination:** support response headers ([#371](https://github.com/stainless-sdks/sink-python-public/issues/371)) ([21081ac](https://github.com/stainless-sdks/sink-python-public/commit/21081ac3886ae19d3e49c986bb18db07e07ba397))


### Chores

* **package:** lift anyio v4 restriction ([#373](https://github.com/stainless-sdks/sink-python-public/issues/373)) ([3c62f7c](https://github.com/stainless-sdks/sink-python-public/commit/3c62f7c261f7df43011eb4d4d661846140dd0390))

## 1.13.0 (2023-12-01)

Full Changelog: [v1.12.1...v1.13.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.12.1...v1.13.0)

### Features

* **pagination:** add offset support ([#368](https://github.com/stainless-sdks/sink-python-public/issues/368)) ([b6f3d34](https://github.com/stainless-sdks/sink-python-public/commit/b6f3d340a606b2c439fb6551b3981283c9be6160))
* **pagination:** add support for cursor_url ([#369](https://github.com/stainless-sdks/sink-python-public/issues/369)) ([87f393f](https://github.com/stainless-sdks/sink-python-public/commit/87f393fd0934b2810cc79573ed7ed577f3f34ee4))


### Bug Fixes

* **client:** correct base_url setter implementation ([#370](https://github.com/stainless-sdks/sink-python-public/issues/370)) ([b62c111](https://github.com/stainless-sdks/sink-python-public/commit/b62c1118b64e7b22e6a00e1511d243db3f03795c))


### Chores

* **internal:** replace string concatenation with f-strings ([#366](https://github.com/stainless-sdks/sink-python-public/issues/366)) ([2e80f83](https://github.com/stainless-sdks/sink-python-public/commit/2e80f83191582daa796dcdb8a54c29980b6cbd80))
* remove pagination tests for now ([#367](https://github.com/stainless-sdks/sink-python-public/issues/367)) ([640303c](https://github.com/stainless-sdks/sink-python-public/commit/640303c992784a16b99e5911fda7875c4bebfd23))


### Documentation

* **readme:** update example snippets ([#364](https://github.com/stainless-sdks/sink-python-public/issues/364)) ([5d26ea1](https://github.com/stainless-sdks/sink-python-public/commit/5d26ea12b473bed69f0c177997093a264bca3825))

## 1.12.1 (2023-11-30)

Full Changelog: [v1.12.0...v1.12.1](https://github.com/stainless-sdks/sink-python-public/compare/v1.12.0...v1.12.1)

### Bug Fixes

* **client:** ensure retried requests are closed ([#363](https://github.com/stainless-sdks/sink-python-public/issues/363)) ([4383f52](https://github.com/stainless-sdks/sink-python-public/commit/4383f524f7961b5cc1549ef84cf721bba070bd0e))


### Chores

* **client:** improve copy method ([#354](https://github.com/stainless-sdks/sink-python-public/issues/354)) ([dcee1bd](https://github.com/stainless-sdks/sink-python-public/commit/dcee1bdfeb822ea8346154574db8b454331818fa))
* **deps:** bump mypy to v1.7.1 ([#359](https://github.com/stainless-sdks/sink-python-public/issues/359)) ([c1ada65](https://github.com/stainless-sdks/sink-python-public/commit/c1ada65a9c433cd02c6f7ffd6b6f04b92f86a292))
* **docs:** fix argument names in docstrings ([#352](https://github.com/stainless-sdks/sink-python-public/issues/352)) ([43e86b0](https://github.com/stainless-sdks/sink-python-public/commit/43e86b0c8647c1aba73998da50597757f93b3a0e))
* **internal:** add tests for proxy change ([#362](https://github.com/stainless-sdks/sink-python-public/issues/362)) ([6069582](https://github.com/stainless-sdks/sink-python-public/commit/606958228c32b2bd04b2e24ba0b1bafbdc057511))
* **internal:** options updates ([#356](https://github.com/stainless-sdks/sink-python-public/issues/356)) ([d06046b](https://github.com/stainless-sdks/sink-python-public/commit/d06046beb69b42f391d2e0484fd00e520fd33b24))
* **internal:** revert recent options change ([#357](https://github.com/stainless-sdks/sink-python-public/issues/357)) ([62f9c7e](https://github.com/stainless-sdks/sink-python-public/commit/62f9c7e0adb8f1bf40c30d311c6885001330ebd2))
* **internal:** send more detailed x-stainless headers ([#358](https://github.com/stainless-sdks/sink-python-public/issues/358)) ([2437a93](https://github.com/stainless-sdks/sink-python-public/commit/2437a9342514d67e23ae694635db8d67d332f6b1))
* **internal:** updates to proxy helper ([#361](https://github.com/stainless-sdks/sink-python-public/issues/361)) ([4e4402b](https://github.com/stainless-sdks/sink-python-public/commit/4e4402bb93496bbabb69650e6664609ba44f165f))
* **package:** add license classifier metadata ([#355](https://github.com/stainless-sdks/sink-python-public/issues/355)) ([c18227f](https://github.com/stainless-sdks/sink-python-public/commit/c18227fe388fc802ba3cfc38f4fcf8a5f67d1b9c))

## 1.12.0 (2023-11-21)

Full Changelog: [v1.11.3...v1.12.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.11.3...v1.12.0)

### Features

* add string type test ([#347](https://github.com/stainless-sdks/sink-python-public/issues/347)) ([7b16a91](https://github.com/stainless-sdks/sink-python-public/commit/7b16a919f92288beb517c44b11cbcacdd868de4c))
* add tests for union with unknown variant ([#348](https://github.com/stainless-sdks/sink-python-public/issues/348)) ([c9684b5](https://github.com/stainless-sdks/sink-python-public/commit/c9684b5bd8b47d01f0a63d53dca4a5623194f333))
* **client:** support reading the base url from an env variable ([#343](https://github.com/stainless-sdks/sink-python-public/issues/343)) ([c0b050e](https://github.com/stainless-sdks/sink-python-public/commit/c0b050e4ca7f8ae099ebc8ad01fcf76af36cae8c))
* idk ([#341](https://github.com/stainless-sdks/sink-python-public/issues/341)) ([745ad7e](https://github.com/stainless-sdks/sink-python-public/commit/745ad7e29e6f81b3ac0207ded753e9a51d967887))


### Bug Fixes

* **client:** attempt to parse unknown json content types ([#351](https://github.com/stainless-sdks/sink-python-public/issues/351)) ([227c50d](https://github.com/stainless-sdks/sink-python-public/commit/227c50db49eaf4022e8702a32afe0f1b68d7499d))


### Chores

* **internal:** fix devcontainer interpeter path ([#340](https://github.com/stainless-sdks/sink-python-public/issues/340)) ([83271cf](https://github.com/stainless-sdks/sink-python-public/commit/83271cfe1532d9cb71dd1540599a9c97bae3d714))
* **internal:** fix some docstring argument names ([#349](https://github.com/stainless-sdks/sink-python-public/issues/349)) ([375fa99](https://github.com/stainless-sdks/sink-python-public/commit/375fa993e8dbe4e3f11e476bd5b06884a8b9e9e3))
* **internal:** fix typo in NotGiven docstring ([#338](https://github.com/stainless-sdks/sink-python-public/issues/338)) ([a758078](https://github.com/stainless-sdks/sink-python-public/commit/a758078ea54979f8ef4e4c234b46c2611be678f2))
* **internal:** update stats file ([#345](https://github.com/stainless-sdks/sink-python-public/issues/345)) ([5de6a32](https://github.com/stainless-sdks/sink-python-public/commit/5de6a326b182a697b9265e64457ae3b7be6c5d45))
* **internal:** update type hint for helper function ([#350](https://github.com/stainless-sdks/sink-python-public/issues/350)) ([fb3c127](https://github.com/stainless-sdks/sink-python-public/commit/fb3c127dc32c03967ab1c5eb80af64c73cf07b95))
* update enum tests ([#346](https://github.com/stainless-sdks/sink-python-public/issues/346)) ([0780884](https://github.com/stainless-sdks/sink-python-public/commit/07808844b0b143c7647f63114c39a02d36f0d70b))


### Documentation

* fix code comment typo ([#342](https://github.com/stainless-sdks/sink-python-public/issues/342)) ([2b24c3c](https://github.com/stainless-sdks/sink-python-public/commit/2b24c3c416396cd14c7873e6896ef517ddb13657))
* **readme:** minor updates ([#344](https://github.com/stainless-sdks/sink-python-public/issues/344)) ([9034162](https://github.com/stainless-sdks/sink-python-public/commit/9034162dc3267ebb4d31bb6f0c1f6b951424cb76))

## 1.11.3 (2023-11-13)

Full Changelog: [v1.11.2...v1.11.3](https://github.com/stainless-sdks/sink-python-public/compare/v1.11.2...v1.11.3)

### Bug Fixes

* **client:** retry if SSLWantReadError occurs in the async client ([#336](https://github.com/stainless-sdks/sink-python-public/issues/336)) ([7065e26](https://github.com/stainless-sdks/sink-python-public/commit/7065e26ca8ccce082634f59acf56f7f91768fcc5))

## 1.11.2 (2023-11-10)

Full Changelog: [v1.11.1...v1.11.2](https://github.com/stainless-sdks/sink-python-public/compare/v1.11.1...v1.11.2)

### Bug Fixes

* **client:** serialise pydantic v1 default fields correctly in params ([#334](https://github.com/stainless-sdks/sink-python-public/issues/334)) ([91a5093](https://github.com/stainless-sdks/sink-python-public/commit/91a50931dfc78f16b8eee4cfbf6f948b1af98bae))

## 1.11.1 (2023-11-10)

Full Changelog: [v1.11.0...v1.11.1](https://github.com/stainless-sdks/sink-python-public/compare/v1.11.0...v1.11.1)

### Bug Fixes

* **models:** mark unknown fields as set in pydantic v1 ([#332](https://github.com/stainless-sdks/sink-python-public/issues/332)) ([d82b7d8](https://github.com/stainless-sdks/sink-python-public/commit/d82b7d8ef2085be4b6c1418d2d9d07f4d41401e7))

## 1.11.0 (2023-11-10)

Full Changelog: [v1.10.0...v1.11.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.10.0...v1.11.0)

### Features

* **client:** support passing chunk size for binary responses ([#329](https://github.com/stainless-sdks/sink-python-public/issues/329)) ([21adeb9](https://github.com/stainless-sdks/sink-python-public/commit/21adeb9803b524a046148ef62478c12988562f74))
* **client:** support passing httpx.Timeout to method timeout argument ([#323](https://github.com/stainless-sdks/sink-python-public/issues/323)) ([d798c7f](https://github.com/stainless-sdks/sink-python-public/commit/d798c7fc6cd9ba9262d53a82f0558b2b47d3b54a))


### Bug Fixes

* **client:** correctly flush the stream response body ([#331](https://github.com/stainless-sdks/sink-python-public/issues/331)) ([c5391af](https://github.com/stainless-sdks/sink-python-public/commit/c5391af8f62a72f4074c5e74c92eae494557884e))


### Chores

* **docs:** fix github links ([#326](https://github.com/stainless-sdks/sink-python-public/issues/326)) ([00bcc79](https://github.com/stainless-sdks/sink-python-public/commit/00bcc794a9453f2916e4cb8e446555bd386370ff))
* **internal:** fix some typos ([#325](https://github.com/stainless-sdks/sink-python-public/issues/325)) ([455cda5](https://github.com/stainless-sdks/sink-python-public/commit/455cda58ce6433315e16588a8de23bf855f45a6e))
* **internal:** improve github devcontainer setup ([#328](https://github.com/stainless-sdks/sink-python-public/issues/328)) ([168adf7](https://github.com/stainless-sdks/sink-python-public/commit/168adf799c7214971b892a6ca2c843221dd5fb6e))
* **types:** add more array types tests ([#327](https://github.com/stainless-sdks/sink-python-public/issues/327)) ([6666614](https://github.com/stainless-sdks/sink-python-public/commit/66666143949965164f0a55842e7a5b6a11af513e))


### Documentation

* reword package description ([#330](https://github.com/stainless-sdks/sink-python-public/issues/330)) ([d64aa3d](https://github.com/stainless-sdks/sink-python-public/commit/d64aa3dab4f54c460e2b9a87520a60d24e3e0237))

## 1.10.0 (2023-11-06)

Full Changelog: [v1.9.0...v1.10.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.9.0...v1.10.0)

### Features

* temporarily skip mutual recursion cases ([#319](https://github.com/stainless-sdks/sink-python-public/issues/319)) ([fc0444b](https://github.com/stainless-sdks/sink-python-public/commit/fc0444ba0bed913c50442307753338ae053e8801))


### Bug Fixes

* prevent TypeError in Python 3.8 (ABC is not subscriptable) ([#322](https://github.com/stainless-sdks/sink-python-public/issues/322)) ([64770ff](https://github.com/stainless-sdks/sink-python-public/commit/64770ffe936cc73d7c680de52298cff4b2e2bdb6))


### Chores

* **internal:** remove unused int/float conversion ([#320](https://github.com/stainless-sdks/sink-python-public/issues/320)) ([8489d07](https://github.com/stainless-sdks/sink-python-public/commit/8489d07c9408a3d3f4265d0fcea1131f9b956cfd))


### Documentation

* **api:** improve method signatures for named path params ([#317](https://github.com/stainless-sdks/sink-python-public/issues/317)) ([67d81e9](https://github.com/stainless-sdks/sink-python-public/commit/67d81e98b65edb1a876456984d456c7331a7b70c))
* **readme:** improve example snippets ([#321](https://github.com/stainless-sdks/sink-python-public/issues/321)) ([615ae3d](https://github.com/stainless-sdks/sink-python-public/commit/615ae3d087fbf9a0efd5477ab80e61c1737ec29c))

## 1.9.0 (2023-11-03)

Full Changelog: [v1.8.1...v1.9.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.8.1...v1.9.0)

### Features

* add support for default headers per-resource ([#311](https://github.com/stainless-sdks/sink-python-public/issues/311)) ([83e671c](https://github.com/stainless-sdks/sink-python-public/commit/83e671ccd1c792acad0c78711be48c3732c72c00))
* add union type name tests ([#313](https://github.com/stainless-sdks/sink-python-public/issues/313)) ([9b2ef1d](https://github.com/stainless-sdks/sink-python-public/commit/9b2ef1defbf26615fabd9df910892038844e8c8e))
* **client:** allow binary returns ([#314](https://github.com/stainless-sdks/sink-python-public/issues/314)) ([b3b610e](https://github.com/stainless-sdks/sink-python-public/commit/b3b610e180722d968caed4e38acb0a3997a14ae8))
* **client:** support accessing raw response objects ([#306](https://github.com/stainless-sdks/sink-python-public/issues/306)) ([aa1b0a3](https://github.com/stainless-sdks/sink-python-public/commit/aa1b0a3c82017440b6696905ecce436dde7e9e11))
* **client:** support passing BaseModels to request params at runtime ([#315](https://github.com/stainless-sdks/sink-python-public/issues/315)) ([1512d45](https://github.com/stainless-sdks/sink-python-public/commit/1512d45e35654496d77564d27734b996b7b52f69))
* **github:** include a devcontainer setup ([#312](https://github.com/stainless-sdks/sink-python-public/issues/312)) ([205d58d](https://github.com/stainless-sdks/sink-python-public/commit/205d58d7d2262a4c36b9fde1c09efa5d0d9b5501))
* **package:** add classifiers ([#310](https://github.com/stainless-sdks/sink-python-public/issues/310)) ([cc0502a](https://github.com/stainless-sdks/sink-python-public/commit/cc0502ab4fb789cba4c4ab35e80bf6e8081e2c23))


### Bug Fixes

* **binaries:** don't synchronously block in astream_to_file ([#316](https://github.com/stainless-sdks/sink-python-public/issues/316)) ([b9d2d6b](https://github.com/stainless-sdks/sink-python-public/commit/b9d2d6be0260e23d86f8bbea139a76655c3a0ceb))


### Chores

* **internal:** minor restructuring of base client ([#309](https://github.com/stainless-sdks/sink-python-public/issues/309)) ([8629df3](https://github.com/stainless-sdks/sink-python-public/commit/8629df381102fbfb11dfe232820a82c2ea5345c2))

## 1.8.1 (2023-10-26)

Full Changelog: [v1.8.0...v1.8.1](https://github.com/stainless-sdks/sink-python-public/compare/v1.8.0...v1.8.1)

### Chores

* **internal:** require explicit overrides ([#304](https://github.com/stainless-sdks/sink-python-public/issues/304)) ([9842624](https://github.com/stainless-sdks/sink-python-public/commit/9842624f098b3c9e28612a9f9f1b2cc5d48b2fd1))

## 1.8.0 (2023-10-26)

Full Changelog: [v1.7.0...v1.8.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.7.0...v1.8.0)

### Features

* more unions tests ([#302](https://github.com/stainless-sdks/sink-python-public/issues/302)) ([46d2282](https://github.com/stainless-sdks/sink-python-public/commit/46d228258feab2014edd2ae1e51e1483e24096bf))


### Documentation

* improve to dictionary example ([#300](https://github.com/stainless-sdks/sink-python-public/issues/300)) ([2b3ec08](https://github.com/stainless-sdks/sink-python-public/commit/2b3ec08e431766660ecb80110f4878f5e05bb4ba))

## 1.7.0 (2023-10-24)

Full Changelog: [v1.6.3...v1.7.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.6.3...v1.7.0)

### Features

* **client:** improve file upload types ([#297](https://github.com/stainless-sdks/sink-python-public/issues/297)) ([97ef7fd](https://github.com/stainless-sdks/sink-python-public/commit/97ef7fdd3f6969c194e78e4af6477ffb30fe7cf2))

## 1.6.3 (2023-10-20)

Full Changelog: [v1.6.2...v1.6.3](https://github.com/stainless-sdks/sink-python-public/compare/v1.6.2...v1.6.3)

### Chores

* **internal:** bump mypy ([#295](https://github.com/stainless-sdks/sink-python-public/issues/295)) ([59ad33a](https://github.com/stainless-sdks/sink-python-public/commit/59ad33aedf39efd77b2125338947d51854dd9375))

## 1.6.2 (2023-10-20)

Full Changelog: [v1.6.1...v1.6.2](https://github.com/stainless-sdks/sink-python-public/compare/v1.6.1...v1.6.2)

### Chores

* **internal:** bump pyright ([#293](https://github.com/stainless-sdks/sink-python-public/issues/293)) ([a9c7182](https://github.com/stainless-sdks/sink-python-public/commit/a9c7182112bdb7695000d161d1546e7ca3300353))

## 1.6.1 (2023-10-19)

Full Changelog: [v1.5.2...v1.6.1](https://github.com/stainless-sdks/sink-python-public/compare/v1.5.2...v1.6.1)

### Features

* **client:** support passing httpx.URL instances to base_url ([#288](https://github.com/stainless-sdks/sink-python-public/issues/288)) ([fda1ded](https://github.com/stainless-sdks/sink-python-public/commit/fda1ded935d98301e1da4c41c88779c2318259f6))


### Chores

* **internal:** update gitignore ([#290](https://github.com/stainless-sdks/sink-python-public/issues/290)) ([c71382a](https://github.com/stainless-sdks/sink-python-public/commit/c71382abc6d71b7dba81f9d3e8dcdc1b28f9c5e8))
* **internal:** update gitignore ([#291](https://github.com/stainless-sdks/sink-python-public/issues/291)) ([01f5d89](https://github.com/stainless-sdks/sink-python-public/commit/01f5d89b5e9a4f59fc114a5fa338f80b226f6113))

## 1.5.2 (2023-10-17)

Full Changelog: [v1.5.1...v1.5.2](https://github.com/stainless-sdks/sink-python-public/compare/v1.5.1...v1.5.2)

### Chores

* **internal:** improve publish script ([#286](https://github.com/stainless-sdks/sink-python-public/issues/286)) ([296fe57](https://github.com/stainless-sdks/sink-python-public/commit/296fe577ab42b9756695e89af321d76ce888496d))

## 1.5.1 (2023-10-17)

Full Changelog: [v1.5.0...v1.5.1](https://github.com/stainless-sdks/sink-python-public/compare/v1.5.0...v1.5.1)

### Chores

* **internal:** migrate from Poetry to Rye ([#284](https://github.com/stainless-sdks/sink-python-public/issues/284)) ([ed3b9fb](https://github.com/stainless-sdks/sink-python-public/commit/ed3b9fbed913c2e7c3ccef6a5bd85ac17d7ce563))

## 1.5.0 (2023-10-17)

Full Changelog: [v1.4.1...v1.5.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.4.1...v1.5.0)

### Features

* use Rye instead of Poetry!!! ([acb9d00](https://github.com/stainless-sdks/sink-python-public/commit/acb9d00d65bb3f1cb38f420eb7002454dae0e841))

## 1.4.1 (2023-10-17)

Full Changelog: [v1.4.0...v1.4.1](https://github.com/stainless-sdks/sink-python-public/compare/v1.4.0...v1.4.1)

### Chores

* test change ([e126521](https://github.com/stainless-sdks/sink-python-public/commit/e12652107613089e0340f28135fbc818a8fcf8aa))

## 1.4.0 (2023-10-17)

Full Changelog: [v1.3.1...v1.4.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.3.1...v1.4.0)

### Features

* add case for nullable unions ([#277](https://github.com/stainless-sdks/sink-python-public/issues/277)) ([906363a](https://github.com/stainless-sdks/sink-python-public/commit/906363aef298e245ce80ecba63a67b693acc91e4))
* add tests for date path params ([#281](https://github.com/stainless-sdks/sink-python-public/issues/281)) ([c62fff8](https://github.com/stainless-sdks/sink-python-public/commit/c62fff862d20c432654a3f1eac6507e68a34e041))
* partially add extra_params_and_fields case ([#275](https://github.com/stainless-sdks/sink-python-public/issues/275)) ([0211b94](https://github.com/stainless-sdks/sink-python-public/commit/0211b94b8d0139ce483f03b607be77e5fc369452))


### Bug Fixes

* **client:** accept io.IOBase instances in file params ([#278](https://github.com/stainless-sdks/sink-python-public/issues/278)) ([44ef9eb](https://github.com/stainless-sdks/sink-python-public/commit/44ef9eb9722cd46816b8d529aefaad64800937cd))


### Documentation

* improve error message for invalid file param type ([#280](https://github.com/stainless-sdks/sink-python-public/issues/280)) ([4f8005a](https://github.com/stainless-sdks/sink-python-public/commit/4f8005a0f527c62a54ab5684975f4acec4f51823))
* organisation -&gt; organization (UK to US English) ([#279](https://github.com/stainless-sdks/sink-python-public/issues/279)) ([2773f0e](https://github.com/stainless-sdks/sink-python-public/commit/2773f0ecdf95e455c5de4a016ce73da9dc483a77))

## 1.3.1 (2023-10-16)

Full Changelog: [v1.3.0...v1.3.1](https://github.com/stainless-sdks/sink-python-public/compare/v1.3.0...v1.3.1)

### Chores

* bump ([#273](https://github.com/stainless-sdks/sink-python-public/issues/273)) ([0643508](https://github.com/stainless-sdks/sink-python-public/commit/06435080a22d6b9d0f5ab11055ce77f2e661da73))

## 1.3.0 (2023-10-14)

Full Changelog: [v1.2.5...v1.3.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.2.5...v1.3.0)

### Features

* added Ruby ([#270](https://github.com/stainless-sdks/sink-python-public/issues/270)) ([58e22c9](https://github.com/stainless-sdks/sink-python-public/commit/58e22c9a0d34531a52bebd42732a5415dad360ec))


### Chores

* **internal:** enable lint rule ([#272](https://github.com/stainless-sdks/sink-python-public/issues/272)) ([a88f5ce](https://github.com/stainless-sdks/sink-python-public/commit/a88f5cefcfc331af4fda4c0b101bc6d0f64af964))

## 1.2.5 (2023-10-13)

Full Changelog: [v1.2.4...v1.2.5](https://github.com/stainless-sdks/sink-python-public/compare/v1.2.4...v1.2.5)

### Chores

* **internal:** cleanup some redundant code ([#268](https://github.com/stainless-sdks/sink-python-public/issues/268)) ([e1e921c](https://github.com/stainless-sdks/sink-python-public/commit/e1e921c3890ead873fae9f476e76620b1b0a8dde))

## 1.2.4 (2023-10-13)

Full Changelog: [v1.2.3...v1.2.4](https://github.com/stainless-sdks/sink-python-public/compare/v1.2.3...v1.2.4)

### Bug Fixes

* **streaming:** add additional overload for ambiguous stream param ([#266](https://github.com/stainless-sdks/sink-python-public/issues/266)) ([11ef175](https://github.com/stainless-sdks/sink-python-public/commit/11ef175fb8935fec17c7bcafeeaa427247d5fb63))

## 1.2.3 (2023-10-13)

Full Changelog: [v1.2.2...v1.2.3](https://github.com/stainless-sdks/sink-python-public/compare/v1.2.2...v1.2.3)

### Chores

* update comment ([#264](https://github.com/stainless-sdks/sink-python-public/issues/264)) ([d2abb24](https://github.com/stainless-sdks/sink-python-public/commit/d2abb2420639d9e2af776c4e773e3ac1fbe7db3d))

## 1.2.2 (2023-10-12)

Full Changelog: [v1.2.1...v1.2.2](https://github.com/stainless-sdks/sink-python-public/compare/v1.2.1...v1.2.2)

### Chores

* add case insensitive get header function ([#262](https://github.com/stainless-sdks/sink-python-public/issues/262)) ([506e7ad](https://github.com/stainless-sdks/sink-python-public/commit/506e7ad683f6ff9c53b14647801e5f0030f7bc57))

## 1.2.1 (2023-10-12)

Full Changelog: [v1.2.0...v1.2.1](https://github.com/stainless-sdks/sink-python-public/compare/v1.2.0...v1.2.1)

## 1.2.0 (2023-10-12)

Full Changelog: [v1.1.0...v1.2.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.1.0...v1.2.0)

### Features

* add more streaming tests ([#250](https://github.com/stainless-sdks/sink-python-public/issues/250)) ([5061d3c](https://github.com/stainless-sdks/sink-python-public/commit/5061d3cc8027cd5aa4c7063d793e965d9d0fd7c5))
* add nested request model test case ([#252](https://github.com/stainless-sdks/sink-python-public/issues/252)) ([37ef646](https://github.com/stainless-sdks/sink-python-public/commit/37ef6461babaa916599f75b4945cd6c9b6d1ae8f))
* add tests for property array of objects in params ([#258](https://github.com/stainless-sdks/sink-python-public/issues/258)) ([8715c0d](https://github.com/stainless-sdks/sink-python-public/commit/8715c0dee43f66b261d7fa1e14170f7e67d58e7a))
* **client:** add client argument test ([#259](https://github.com/stainless-sdks/sink-python-public/issues/259)) ([f163e51](https://github.com/stainless-sdks/sink-python-public/commit/f163e512e6477c702a574ee5543179d71f9bef20))
* **client:** add forwards-compatible pydantic methods ([#253](https://github.com/stainless-sdks/sink-python-public/issues/253)) ([3ca03c0](https://github.com/stainless-sdks/sink-python-public/commit/3ca03c0a477168d22727608f6f19ad113b136710))
* **client:** add logging setup ([#257](https://github.com/stainless-sdks/sink-python-public/issues/257)) ([2d03fa5](https://github.com/stainless-sdks/sink-python-public/commit/2d03fa51c35f2fcccd81de0bd6823a5c22c43422))
* **client:** add support for passing in a httpx client ([#254](https://github.com/stainless-sdks/sink-python-public/issues/254)) ([c7c9971](https://github.com/stainless-sdks/sink-python-public/commit/c7c997195870c8fdaba4501c91566a08fdf126e1))


### Chores

* restructuring ([#251](https://github.com/stainless-sdks/sink-python-public/issues/251)) ([d39c0b4](https://github.com/stainless-sdks/sink-python-public/commit/d39c0b46e47405c8cf637558028d319d0158e4c1))
* **tests:** update test examples ([#248](https://github.com/stainless-sdks/sink-python-public/issues/248)) ([788d4ac](https://github.com/stainless-sdks/sink-python-public/commit/788d4ac5eafd9e199183df5a137775217baec3f7))
* update README ([#255](https://github.com/stainless-sdks/sink-python-public/issues/255)) ([2fb6819](https://github.com/stainless-sdks/sink-python-public/commit/2fb68191ac15d7dbe7ec2d02d8f14d2a86d7c134))


### Refactors

* **test:** refactor authentication tests ([#256](https://github.com/stainless-sdks/sink-python-public/issues/256)) ([72349a8](https://github.com/stainless-sdks/sink-python-public/commit/72349a89c79c9a69dddb81e9a41e731d8184f993))

## 1.1.0 (2023-10-03)

Full Changelog: [v1.0.1...v1.1.0](https://github.com/stainless-sdks/sink-python-public/compare/v1.0.1...v1.1.0)

### Features

* add super_mixed_union endpoint ([#245](https://github.com/stainless-sdks/sink-python-public/issues/245)) ([00e3a83](https://github.com/stainless-sdks/sink-python-public/commit/00e3a83828270a6631429cc2e1b6bf47d573aab9))
* **client:** handle retry-after header with a date format ([#243](https://github.com/stainless-sdks/sink-python-public/issues/243)) ([0c2e15d](https://github.com/stainless-sdks/sink-python-public/commit/0c2e15d6291a8bf82c4db02c1e9258d18f982308))
* **types:** add test for primitive 2d arrays ([#246](https://github.com/stainless-sdks/sink-python-public/issues/246)) ([dfca65e](https://github.com/stainless-sdks/sink-python-public/commit/dfca65ead2fe36fe0dfb0868c84aa9172ee12220))

## 1.0.1 (2023-10-02)

Full Changelog: [v1.0.0...v1.0.1](https://github.com/stainless-sdks/sink-python-public/compare/v1.0.0...v1.0.1)

## 1.0.0 (2023-09-27)

Full Changelog: [v0.4.4...v1.0.0](https://github.com/stainless-sdks/sink-python-public/compare/v0.4.4...v1.0.0)

### Chores

* **tests:** improve raw response test ([#239](https://github.com/stainless-sdks/sink-python-public/issues/239)) ([638f543](https://github.com/stainless-sdks/sink-python-public/commit/638f54388e5d567332b263aabb90c05cc7ea2954))

## 0.4.4 (2023-09-26)

Full Changelog: [v0.4.2...v0.4.4](https://github.com/stainless-sdks/sink-python-public/compare/v0.4.2...v0.4.4)

### Features

* **package:** export a root error type ([#237](https://github.com/stainless-sdks/sink-python-public/issues/237)) ([6048b1f](https://github.com/stainless-sdks/sink-python-public/commit/6048b1f36c86983e59d1da17e32d88d25dd59a44))

## 0.4.2 (2023-09-22)

Full Changelog: [v0.4.1...v0.4.2](https://github.com/stainless-sdks/sink-python-public/compare/v0.4.1...v0.4.2)

### Chores

* **internal:** move error classes from _base_exceptions to _exceptions (⚠️ breaking) ([#235](https://github.com/stainless-sdks/sink-python-public/issues/235)) ([4f4413f](https://github.com/stainless-sdks/sink-python-public/commit/4f4413fe81e5507e1c17483ba7daf8d7e95a0ea5))

## 0.4.1 (2023-09-22)

Full Changelog: [v0.4.0...v0.4.1](https://github.com/stainless-sdks/sink-python-public/compare/v0.4.0...v0.4.1)

### Bug Fixes

* **client:** don't error by default for unexpected content types ([#233](https://github.com/stainless-sdks/sink-python-public/issues/233)) ([afacad6](https://github.com/stainless-sdks/sink-python-public/commit/afacad6d27c0a88893af0644e7924acba0c96403))

## 0.4.0 (2023-09-21)

Full Changelog: [v0.3.2...v0.4.0](https://github.com/stainless-sdks/sink-python-public/compare/v0.3.2...v0.4.0)

### ⚠ BREAKING CHANGES

* fix capitalization of `Github` to `GitHub` in some places ([#232](https://github.com/stainless-sdks/sink-python-public/issues/232))

### Features

* **api:** add more reserved word testcases ([#230](https://github.com/stainless-sdks/sink-python-public/issues/230)) ([4ef6f43](https://github.com/stainless-sdks/sink-python-public/commit/4ef6f437606f3d0d221507bbaea202b37f9b0328))


### Refactors

* fix capitalization of `Github` to `GitHub` in some places ([#232](https://github.com/stainless-sdks/sink-python-public/issues/232)) ([c7720a0](https://github.com/stainless-sdks/sink-python-public/commit/c7720a04f64ec343f3ed83092f3eeb6a32f02160))

## 0.3.2 (2023-09-20)

Full Changelog: [v0.3.1...v0.3.2](https://github.com/stainless-sdks/sink-python-public/compare/v0.3.1...v0.3.2)

### Bug Fixes

* allow deprecated method aliases ([#228](https://github.com/stainless-sdks/sink-python-public/issues/228)) ([3e8278d](https://github.com/stainless-sdks/sink-python-public/commit/3e8278de2470521c682be969245f4802fc749122))

## 0.3.1 (2023-09-19)

Full Changelog: [v0.3.0...v0.3.1](https://github.com/stainless-sdks/sink-python-public/compare/v0.3.0...v0.3.1)

### Features

* **types:** improve params type names ([#226](https://github.com/stainless-sdks/sink-python-public/issues/226)) ([bace972](https://github.com/stainless-sdks/sink-python-public/commit/bace97269945710a34a8c00cdd6d13169e749a30))

## 0.3.0 (2023-09-15)

Full Changelog: [v0.2.11...v0.3.0](https://github.com/stainless-sdks/sink-python-public/compare/v0.2.11...v0.3.0)

### ⚠ BREAKING CHANGES

* add an enum value ([#225](https://github.com/stainless-sdks/sink-python-public/issues/225))

### Features

* add an enum value ([#225](https://github.com/stainless-sdks/sink-python-public/issues/225)) ([5b321a5](https://github.com/stainless-sdks/sink-python-public/commit/5b321a5bb7f42b9501a4c04835e92c0d3c8e7bf7))

## 0.2.11 (2023-09-15)

Full Changelog: [v0.2.10...v0.2.11](https://github.com/stainless-sdks/sink-python-public/compare/v0.2.10...v0.2.11)

### Chores

* **internal:** add helpers ([#220](https://github.com/stainless-sdks/sink-python-public/issues/220)) ([2072fbc](https://github.com/stainless-sdks/sink-python-public/commit/2072fbc0aedf9120243a75bf4e3d368fd47f8560))

## 0.2.10 (2023-09-14)

Full Changelog: [v0.2.9...v0.2.10](https://github.com/stainless-sdks/sink-python-public/compare/v0.2.9...v0.2.10)

### Bug Fixes

* **client:** properly configure model set fields ([#219](https://github.com/stainless-sdks/sink-python-public/issues/219)) ([05ffa62](https://github.com/stainless-sdks/sink-python-public/commit/05ffa620986d37e7fd5349c696ee343f1d753e8c))
* **config:** use correct positional params name in tests ([#216](https://github.com/stainless-sdks/sink-python-public/issues/216)) ([da0b2ca](https://github.com/stainless-sdks/sink-python-public/commit/da0b2cafb150bfcd42278d9091a21c89b74aa159))


### Chores

* **internal:** cleaner references to complex union types ([#218](https://github.com/stainless-sdks/sink-python-public/issues/218)) ([ade3a1d](https://github.com/stainless-sdks/sink-python-public/commit/ade3a1dd7b2d22a0fe2dd5a366f2f4c0408443d5))
* **internal:** remove unused aliases ([#214](https://github.com/stainless-sdks/sink-python-public/issues/214)) ([6f17266](https://github.com/stainless-sdks/sink-python-public/commit/6f1726645397cb8460f55ca1d2dea515dff5412e))
* **internal:** update pyright ([#213](https://github.com/stainless-sdks/sink-python-public/issues/213)) ([892b26d](https://github.com/stainless-sdks/sink-python-public/commit/892b26d2a50e5f5c0a62133fcd344f2cee6e63c2))


### Documentation

* add some missing inline documentation ([#215](https://github.com/stainless-sdks/sink-python-public/issues/215)) ([749f51e](https://github.com/stainless-sdks/sink-python-public/commit/749f51e6efac03f2549f92a1efb34b89275beed9))

## 0.2.9 (2023-09-08)

Full Changelog: [v0.2.8...v0.2.9](https://github.com/stainless-sdks/sink-python-public/compare/v0.2.8...v0.2.9)

### Features

* add tests for renaming properties ([#210](https://github.com/stainless-sdks/sink-python-public/issues/210)) ([e278ee6](https://github.com/stainless-sdks/sink-python-public/commit/e278ee60e91acf8e98b389599ed852004a4087fd))


### Chores

* **internal:** cleanup test params ([#209](https://github.com/stainless-sdks/sink-python-public/issues/209)) ([d132678](https://github.com/stainless-sdks/sink-python-public/commit/d1326784a149a4565a22a177cf2fa36dd2116ab1))
* **internal:** minor update ([#204](https://github.com/stainless-sdks/sink-python-public/issues/204)) ([3a733e3](https://github.com/stainless-sdks/sink-python-public/commit/3a733e3ceca1c467f1f58607ce70f6ab6e7c9509))
* **internal:** update lock file ([#208](https://github.com/stainless-sdks/sink-python-public/issues/208)) ([74f501f](https://github.com/stainless-sdks/sink-python-public/commit/74f501f869b44f168cf6cd28acd1354a8d00252a))
* **internal:** updates ([#211](https://github.com/stainless-sdks/sink-python-public/issues/211)) ([8016d0b](https://github.com/stainless-sdks/sink-python-public/commit/8016d0bf5141807f659af292421140cf70c3958e))


### Documentation

* **readme:** add link to api.md ([#206](https://github.com/stainless-sdks/sink-python-public/issues/206)) ([1aa2eeb](https://github.com/stainless-sdks/sink-python-public/commit/1aa2eeba5c9aa8580d60be0a41a34f769d9be643))

## 0.2.8 (2023-09-06)

Full Changelog: [v0.2.7...v0.2.8](https://github.com/stainless-sdks/sink-python-public/compare/v0.2.7...v0.2.8)

### Features

* add `x-stainless-useDefault` testcase ([#197](https://github.com/stainless-sdks/sink-python-public/issues/197)) ([8965e9a](https://github.com/stainless-sdks/sink-python-public/commit/8965e9a7feccb82d0f16f6e8e948c1688763552d))
* add nested pagination property test ([#194](https://github.com/stainless-sdks/sink-python-public/issues/194)) ([c8b7aff](https://github.com/stainless-sdks/sink-python-public/commit/c8b7aff40575382c4f822df780f258abab16a9fb))
* add test for doc escaping ([#199](https://github.com/stainless-sdks/sink-python-public/issues/199)) ([3f962bb](https://github.com/stainless-sdks/sink-python-public/commit/3f962bb63e205f76a4244c1cbb3054d4dab43c5a))
* add test for params model with param in name ([#200](https://github.com/stainless-sdks/sink-python-public/issues/200)) ([27b3ad4](https://github.com/stainless-sdks/sink-python-public/commit/27b3ad4e8f705e4b57e562396824a70793a14061))
* add test for union of numbers ([#196](https://github.com/stainless-sdks/sink-python-public/issues/196)) ([9df50e4](https://github.com/stainless-sdks/sink-python-public/commit/9df50e4da9780ce64c9fe6f944df48d1e9fe3569))
* add tests for child model references ([#188](https://github.com/stainless-sdks/sink-python-public/issues/188)) ([0a124e7](https://github.com/stainless-sdks/sink-python-public/commit/0a124e75fdf231ec760e426d4ff67ece9e8de916))
* add tests for optional file params ([#201](https://github.com/stainless-sdks/sink-python-public/issues/201)) ([7330886](https://github.com/stainless-sdks/sink-python-public/commit/733088659c90a4b38be1a60013df97e21fbc53d1))
* add tests for union items in arrays ([#191](https://github.com/stainless-sdks/sink-python-public/issues/191)) ([2b6b3a2](https://github.com/stainless-sdks/sink-python-public/commit/2b6b3a277abed142434dedd40431926df89e3aee))
* fixes tests where an array has to have unique enum values ([#202](https://github.com/stainless-sdks/sink-python-public/issues/202)) ([c88d621](https://github.com/stainless-sdks/sink-python-public/commit/c88d621ac317dcac885d0895b63b2c56a4264adc))
* more params types tests ([#190](https://github.com/stainless-sdks/sink-python-public/issues/190)) ([631d7ec](https://github.com/stainless-sdks/sink-python-public/commit/631d7ece377fd997196e2645447ecc48e0d57c90))
* **types:** de-duplicate nested streaming params types ([#198](https://github.com/stainless-sdks/sink-python-public/issues/198)) ([8632c46](https://github.com/stainless-sdks/sink-python-public/commit/8632c46d4d297f7e1043ab01581c6e27d72da4c1))
* updates ([#192](https://github.com/stainless-sdks/sink-python-public/issues/192)) ([d52fdf1](https://github.com/stainless-sdks/sink-python-public/commit/d52fdf1ca2fe5d0055d76b0d461c54c5e6b6b9fa))


### Chores

* **internal:** minor formatting changes ([#195](https://github.com/stainless-sdks/sink-python-public/issues/195)) ([08998fc](https://github.com/stainless-sdks/sink-python-public/commit/08998fcacffed9cc4e4fb18f4fccbceaba6b18a3))
* **internal:** update base client ([#203](https://github.com/stainless-sdks/sink-python-public/issues/203)) ([b87ac5e](https://github.com/stainless-sdks/sink-python-public/commit/b87ac5ed2a9abf41d19787fa4e9c3444de582518))


### Documentation

* **readme:** reference pydantic helpers ([#193](https://github.com/stainless-sdks/sink-python-public/issues/193)) ([78ae5e5](https://github.com/stainless-sdks/sink-python-public/commit/78ae5e5934e8786bf878da45e61758459239072f))

## 0.2.7 (2023-08-31)

Full Changelog: [v0.2.6...v0.2.7](https://github.com/stainless-sdks/sink-python-public/compare/v0.2.6...v0.2.7)

### Features

* add test case for null property ([#184](https://github.com/stainless-sdks/sink-python-public/issues/184)) ([e439f7a](https://github.com/stainless-sdks/sink-python-public/commit/e439f7a64611ba0d9510ddf9467b80db5f5c4678))
* add test for method named get ([#185](https://github.com/stainless-sdks/sink-python-public/issues/185)) ([075b177](https://github.com/stainless-sdks/sink-python-public/commit/075b1774f0d3c07350057acd525663fffcec00be))
* add tests for complex union types in params ([#182](https://github.com/stainless-sdks/sink-python-public/issues/182)) ([8bf1b33](https://github.com/stainless-sdks/sink-python-public/commit/8bf1b33d1b00b5b236a0f0a109f88dc945e52ed6))
* sync ([#180](https://github.com/stainless-sdks/sink-python-public/issues/180)) ([a4fc313](https://github.com/stainless-sdks/sink-python-public/commit/a4fc313a98573edb3d5be500532160b61c4dc5df))


### Chores

* **internal:** add `pydantic.generics` import for compatibility ([#186](https://github.com/stainless-sdks/sink-python-public/issues/186)) ([c7c7b27](https://github.com/stainless-sdks/sink-python-public/commit/c7c7b277bdee6ba86a91760cff1449660960cd4c))
* **internal:** update lock file ([#183](https://github.com/stainless-sdks/sink-python-public/issues/183)) ([bf3fb96](https://github.com/stainless-sdks/sink-python-public/commit/bf3fb96b7a2afdc3b018e1875ced44d9580e9cd8))

## 0.2.6 (2023-08-28)

Full Changelog: [v0.2.5...v0.2.6](https://github.com/stainless-sdks/sink-python-public/compare/v0.2.5...v0.2.6)

### Features

* add ambiguous schemas and transforms on them ([#80](https://github.com/stainless-sdks/sink-python-public/issues/80)) ([ac8c921](https://github.com/stainless-sdks/sink-python-public/commit/ac8c92171d30db9891f38cadba59e267067b58b2))
* add test cases for duplicate param names ([#175](https://github.com/stainless-sdks/sink-python-public/issues/175)) ([2bda4c7](https://github.com/stainless-sdks/sink-python-public/commit/2bda4c774b1023e3368f14b6d6a63ee9c2f0753b))
* add tests for envelope unwrapping arrays ([#164](https://github.com/stainless-sdks/sink-python-public/issues/164)) ([ce16297](https://github.com/stainless-sdks/sink-python-public/commit/ce1629758591a47f7301fc18eee5f6f24146f1cb))
* add tests for model import clashing ([#176](https://github.com/stainless-sdks/sink-python-public/issues/176)) ([26e8375](https://github.com/stainless-sdks/sink-python-public/commit/26e83751d5a628ee8bda8ce9e98a709020dd8d89))
* add tests for reserved names ([#174](https://github.com/stainless-sdks/sink-python-public/issues/174)) ([e2753ea](https://github.com/stainless-sdks/sink-python-public/commit/e2753eab62dcf33a0736d56551a669d9a6c236e4))
* tests for skipping object properties ([#169](https://github.com/stainless-sdks/sink-python-public/issues/169)) ([6516103](https://github.com/stainless-sdks/sink-python-public/commit/6516103c97ceedad53d94e25d2602dae14d3cd77))


### Bug Fixes

* **ci:** correct branch check ([#172](https://github.com/stainless-sdks/sink-python-public/issues/172)) ([3ac5309](https://github.com/stainless-sdks/sink-python-public/commit/3ac5309041e055e341ab090424b12ece621b8a16))
* **internal:** fixes internal naming issue ([#177](https://github.com/stainless-sdks/sink-python-public/issues/177)) ([13d6b14](https://github.com/stainless-sdks/sink-python-public/commit/13d6b14d1d89c245256854c48a75771e41e5af03))


### Chores

* **ci:** setup workflows to create releases and release PRs ([#178](https://github.com/stainless-sdks/sink-python-public/issues/178)) ([e30edb6](https://github.com/stainless-sdks/sink-python-public/commit/e30edb6f7c77314d4b7b3f7dabd982dc3ec3fb3d))
* **deps:** bump lock file ([#171](https://github.com/stainless-sdks/sink-python-public/issues/171)) ([873349d](https://github.com/stainless-sdks/sink-python-public/commit/873349dd1fa654319b1c5cf1785e005be4cf51c7))
* **deps:** update lock file ([#170](https://github.com/stainless-sdks/sink-python-public/issues/170)) ([cbac2d2](https://github.com/stainless-sdks/sink-python-public/commit/cbac2d236818fe5587c69bc03554a130228b0812))
* **internal:** improve support for streaming responses ([#85](https://github.com/stainless-sdks/sink-python-public/issues/85)) ([658ae3a](https://github.com/stainless-sdks/sink-python-public/commit/658ae3a250f691ab0d295d926c3521a9e7d43f15))
* **internal:** minor reformatting ([#78](https://github.com/stainless-sdks/sink-python-public/issues/78)) ([e8b14d6](https://github.com/stainless-sdks/sink-python-public/commit/e8b14d6d689f52e2c41364840832b17508a1c4cd))
* **internal:** run Release Doctor in Next PR too ([#83](https://github.com/stainless-sdks/sink-python-public/issues/83)) ([5de7a23](https://github.com/stainless-sdks/sink-python-public/commit/5de7a2339fdf6633bb47073cd5d916597cc70936))
* **internal:** update anyio ([#167](https://github.com/stainless-sdks/sink-python-public/issues/167)) ([dc848dc](https://github.com/stainless-sdks/sink-python-public/commit/dc848dcbd19576f673d1387adeecc6893cabb6fb))
* **internal:** use different release PR header ([#82](https://github.com/stainless-sdks/sink-python-public/issues/82)) ([ac4e5a0](https://github.com/stainless-sdks/sink-python-public/commit/ac4e5a0e660a0a4b10c4ec0508903566982765af))
* test change ([#163](https://github.com/stainless-sdks/sink-python-public/issues/163)) ([5c4eb1e](https://github.com/stainless-sdks/sink-python-public/commit/5c4eb1e38c9580f5f6392564babe5904df28c820))
* test change 2 ([#165](https://github.com/stainless-sdks/sink-python-public/issues/165)) ([8fb1636](https://github.com/stainless-sdks/sink-python-public/commit/8fb163647393d1cea563026ecdcec8d50d6c1327))

## [0.2.5](https://github.com/stainless-sdks/sink-python-public/compare/v0.2.4...v0.2.5) (2023-04-27)


### Features

* add tests for concrete page types ([#73](https://github.com/stainless-sdks/sink-python-public/issues/73)) ([4d69fe5](https://github.com/stainless-sdks/sink-python-public/commit/4d69fe5aadee8bfce34af16608a14ddb1e2efb34))


### Bug Fixes

* **ci:** correct version for release-please action ([#75](https://github.com/stainless-sdks/sink-python-public/issues/75)) ([8ee5a27](https://github.com/stainless-sdks/sink-python-public/commit/8ee5a2714f59e4eb9f1359af40d08d27d3366854))

## [0.2.4](https://github.com/stainless-sdks/sink-python-public/compare/v0.2.3...v0.2.4) (2023-04-26)


### Features

* add test cases for allOf ([#68](https://github.com/stainless-sdks/sink-python-public/issues/68)) ([a20eacc](https://github.com/stainless-sdks/sink-python-public/commit/a20eacc0cd6bf57a89aa1ad987cf469342f430e3))
* header params tests ([#66](https://github.com/stainless-sdks/sink-python-public/issues/66)) ([8ac2279](https://github.com/stainless-sdks/sink-python-public/commit/8ac22790db4331e73943a3918c766e8ddb3d704d))

## [0.2.3](https://github.com/stainless-sdks/sink-python-public/compare/v0.2.2...v0.2.3) (2023-04-18)


### Features

* **ci:** add workflow for running PyPI publishing manually ([#63](https://github.com/stainless-sdks/sink-python-public/issues/63)) ([be7a1c6](https://github.com/stainless-sdks/sink-python-public/commit/be7a1c6a9a1ae96b2119ed0bd645af54dffe472c))

## [0.2.2](https://github.com/stainless-sdks/sink-python-public/compare/v0.2.1...v0.2.2) (2023-04-18)


### Features

* **api:** update docs ([#60](https://github.com/stainless-sdks/sink-python-public/issues/60)) ([d0ea156](https://github.com/stainless-sdks/sink-python-public/commit/d0ea156140b36a9d0fe705d4ad0b07799d7fe20f))

## [0.2.1](https://github.com/stainless-sdks/sink-python-public/compare/v0.2.0...v0.2.1) (2023-04-18)


### Features

* add timeout option to methods ([#29](https://github.com/stainless-sdks/sink-python-public/issues/29)) ([3d68204](https://github.com/stainless-sdks/sink-python-public/commit/3d68204c945d33492d6dda459fb4e4b09276c2af))
* **ci:** add script to publish to PyPi ([#49](https://github.com/stainless-sdks/sink-python-public/issues/49)) ([518cd7e](https://github.com/stainless-sdks/sink-python-public/commit/518cd7e8238f36737a4df3943e5c2e530169d6c0))
* test change ([#42](https://github.com/stainless-sdks/sink-python-public/issues/42)) ([7b653da](https://github.com/stainless-sdks/sink-python-public/commit/7b653da06aba2b85fcf3f2b60fa5f63fec4566d2))
* use foo ([#44](https://github.com/stainless-sdks/sink-python-public/issues/44)) ([020d77d](https://github.com/stainless-sdks/sink-python-public/commit/020d77d73c9c56aeba7af615be35cb2cb4a4c70f))
* use foo ([#45](https://github.com/stainless-sdks/sink-python-public/issues/45)) ([4b08a66](https://github.com/stainless-sdks/sink-python-public/commit/4b08a66da9f200db63d2183a14db8002988b9228))


### Bug Fixes

* **ci:** release doctor workflow + improvements ([#53](https://github.com/stainless-sdks/sink-python-public/issues/53)) ([6b506a9](https://github.com/stainless-sdks/sink-python-public/commit/6b506a993bee182e3cddbb0307ff778192d47550))
* **ci:** release file options syntax ([#47](https://github.com/stainless-sdks/sink-python-public/issues/47)) ([793bb08](https://github.com/stainless-sdks/sink-python-public/commit/793bb08d8a54caf76f3e40f3d62a84be1fd43180))
