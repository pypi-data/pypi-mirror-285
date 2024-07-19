## vp4jl

### Key Features:

1. **(a) Interactive Visual Programming Editor**:
   - **Rich Built-in Nodes**: Power your designs with our diverse suite of nodes, spanning control flow, mathematical operations, variables, function interactions, reroutes, and annotations.
   - **Smooth User Interaction**: Engage with a user-friendly canvas that allows for effortless zoom, pan, and diverse node operations. Boost your workflow with intuitive menus and a streamlined toolbar. Enhance navigation with a detailed minimap and time-saving shortcut keys.
   - **Smart Auto Layout**: Ensure elegance and clarity with automatic layout adjustments, guaranteeing optimal node alignment and perfect view fitting.
2. **Extensible Node Library with JSON Specifications**:
   - **(d1), (d2) Robust Node Specification**: Introduce new nodes easily with a JSON-based specification, making library extensions a breeze.
   - **(e) Intuitive Node-Library Panel**: Navigate through an advanced panel that showcases all your installed node libraries. Experience streamlined installation, uninstallation, activation, and deactivation processes.
   - **Efficient Backend Library Management**: Handle all your node libraries with a dedicated management backend, ensuring smooth operations.
5. **(f) Seamless Integration within the JupyterLab Interface**: Immerse yourself in integration so smooth it feels native to JupyterLab. Enjoy seamless file operations, efficient code execution, and immediate result displays, all within the familiar JupyterLab environment.
6. **Computational Documents**:
   - **(b) Enhanced Jupyter Notebook**: Revel in the renowned flexibility and power of Jupyter notebooks, now boosted with visual programming capabilities in the notebook.
   - **(c) New Document Format**: Introduce a fresh visual programming-supported document format `vp4jl`, sitting comfortably alongside a traditional computational notebook.
7. **Effortless Visual Programming Integration**: Easily equip your JupyterLab environment with visual programming capabilities using our extension, all without altering your existing setup.

## Requirements

- [jupyterlab](https://github.com/jupyterlab/jupyterlab) >= 4.0.0b0
- python >= 3.10

## Usage

install the `vp4jl` via jupyter lab extension manager.

## Documentation

For in-depth documentation on using `vp4jl`, including basic view and navigation, node operations, JSON-based specification for Node Library, code generation, and so on, please visit [our documentation](doc/Document.md).

## For Developers

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of [yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use `yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Install package in development mode
pip install -e ".[test]"
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
# Server extension must be manually installed in develop mode
jupyter server extension enable vp4jl
# Rebuild extension Typescript source after making changes
jlpm build
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
# Server extension must be manually disabled in develop mode
jupyter server extension disable vp4jl
pip uninstall vp4jl
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop` command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions` folder is located. Then you can remove the symlink named `vp4jl` within that folder.

### Packaging the extension

See [RELEASE](RELEASE.md)

### Troubleshoot

If you are seeing the frontend extension, but it is not working, check
that the server extension is enabled:

```bash
jupyter server extension list
```

If the server extension is installed and enabled, but you are not seeing
the frontend extension, check the frontend extension is installed:

```bash
jupyter labextension list
```

## Support & Contribution

- Issues: For bug reports and feature requests, please open the GitHub issue.
- Contributing: Pull requests are welcome. For major changes, please open an issue first to discuss the proposed change.

## License

This project is licensed under the GNU General Public License v3.0 license.
