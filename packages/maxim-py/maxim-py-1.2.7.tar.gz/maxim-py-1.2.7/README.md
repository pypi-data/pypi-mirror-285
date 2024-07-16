# Maxim Python Library

Python SDK to integrate Maxim AI. More info at [Maxim Site](https://getmaxim.ai). Maxim is an enterprise grade evaluation and monitoring platform for your GenAI applications.

## Version changelog

### v1.2.7

- Bug fix where input sent with trace.config was getting overridden with None

### v1.2.6

- Adds `trace.set_input` and `trace.set_output` methods to control what to show in logs dashboard

### v1.2.5

- Removes one no_op command while creating spans
- Minor bug fixes

### v1.2.1

- Fixed MaximLangchainTracer error logging flow.

### v1.2.0

- Adds langchain support
- Adds local parsers to validate payloads on client side

### v1.1.0

- Minor bug fixes around log writer cleanup

### v1.0.0

- Public release
