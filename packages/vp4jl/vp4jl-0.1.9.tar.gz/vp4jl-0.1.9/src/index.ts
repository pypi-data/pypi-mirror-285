import {
  ILabShell,
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import {
  IFileBrowserFactory,
  IDefaultFileBrowser
} from '@jupyterlab/filebrowser';
import { ILauncher } from '@jupyterlab/launcher';
import { IMainMenu } from '@jupyterlab/mainmenu';
import {
  copyIcon,
  pasteIcon,
  cutIcon,
  deleteIcon,
  duplicateIcon,
  clearIcon,
  fastForwardIcon,
  refreshIcon,
  stopIcon,
  runIcon
} from '@jupyterlab/ui-components';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { ICommandPalette, ISessionContextDialogs } from '@jupyterlab/apputils';
import { ReadonlyPartialJSONObject } from '@lumino/coreutils';
import { VPWidget } from './widget';
import {
  vp4jlIDs as gVP4jlIDs,
  vp4jlCommandIDs as gVp4jlCommandIDs
} from './namepace';
import { requestAPI } from './request';
import { NodeExtensionToken, NodeExtension } from './node-extension';
import { VPModelFactory } from './model-factory';
import { VPWidgetFactory } from './widget-factory';
import { getToolbarFactory } from './toolbar-factory';
import { IVPTracker, VPTracker, IVPTrackerToken } from './tracker';
import { LoadPackageToRegistry } from 'chaldene_vpe';
import visualCodePlugins from './visual-code-cell';
import { IDocumentWidget } from '@jupyterlab/docregistry';

const vp4jl: JupyterFrontEndPlugin<IVPTracker> = {
  id: 'vp4jl:plugin',
  autoStart: true,
  requires: [IRenderMimeRegistry],
  provides: IVPTrackerToken,
  activate: activateVp4jl
};

const vp4jlCommands: JupyterFrontEndPlugin<void> = {
  id: 'vp4jl:Commands',
  autoStart: true,
  requires: [
    ILabShell,
    IVPTrackerToken,
    ISessionContextDialogs,
    IFileBrowserFactory,
    NodeExtensionToken
  ],
  optional: [IDefaultFileBrowser],
  activate: activateVp4jlCommands
};

const vp4jlAttachCommandsToGui: JupyterFrontEndPlugin<void> = {
  id: 'vp4jl:AttachCommandsToGui',
  autoStart: true,
  requires: [IMainMenu, IVPTrackerToken],
  optional: [ILauncher, ICommandPalette],
  activate: activateVp4jlAttachCommandsToGui
};

const vp4jlRestorer: JupyterFrontEndPlugin<void> = {
  id: 'vp4jl:Restorer',
  autoStart: true,
  optional: [ILayoutRestorer, IVPTrackerToken],
  activate: activateVp4jlRestorer
};

const vp4jlNodeExtension: JupyterFrontEndPlugin<NodeExtension> = {
  id: 'vp4jl:NodeExtension',
  autoStart: true,
  optional: [ILayoutRestorer],
  provides: NodeExtensionToken,
  activate: activateVp4jlNodeExtension
};

const vp4jlFixContextMenuClose: JupyterFrontEndPlugin<void> = {
  id: 'vp4jl:FixContextMenuClose',
  autoStart: true,
  requires: [ILabShell],
  activate: activateVp4jlFixContextMenuClose
};

const plugins: JupyterFrontEndPlugin<any>[] = [
  vp4jl,
  vp4jlCommands,
  vp4jlAttachCommandsToGui,
  vp4jlRestorer,
  vp4jlNodeExtension,
  vp4jlFixContextMenuClose,
  ...visualCodePlugins
];
export default plugins;

function activateVp4jl(
  app: JupyterFrontEnd,
  rendermime: IRenderMimeRegistry
): IVPTracker {
  const vp4jlIDs = gVP4jlIDs;

  const tracker = new VPTracker({
    namespace: vp4jlIDs.trackerNamespace
  });

  const widgetFactory = new VPWidgetFactory(
    {
      name: vp4jlIDs.widgetFactory,
      modelName: vp4jlIDs.modelFactory,
      fileTypes: [vp4jlIDs.fileType],
      defaultFor: [vp4jlIDs.fileType],
      toolbarFactory: getToolbarFactory(app.commands, vp4jlIDs.widgetFactory)
    },
    rendermime
  );
  widgetFactory.widgetCreated.connect((sender, widget) => {
    widget.context.pathChanged.connect(() => {
      tracker.save(widget);
    });
    tracker.add(widget);
  });

  app.docRegistry.addWidgetFactory(widgetFactory);
  app.docRegistry.addModelFactory(new VPModelFactory());
  app.docRegistry.addFileType({
    name: vp4jlIDs.fileType,
    displayName: 'VP File',
    mimeTypes: ['text/json', 'application/json'],
    extensions: [vp4jlIDs.fileExtension],
    fileFormat: 'text',
    contentType: 'file'
  });
  return tracker;
}

function activateVp4jlCommands(
  app: JupyterFrontEnd,
  labShell: ILabShell,
  tracker: IVPTracker,
  sessionDialogs: ISessionContextDialogs,
  browserFactory: IFileBrowserFactory,
  nodeExtension: NodeExtension,
  defaultFileBrowser: IDefaultFileBrowser | null
) {
  const vp4jlIDs = gVP4jlIDs;
  const cmdIds = gVp4jlCommandIDs;
  const { shell } = app;
  const isEnabled = (): boolean => {
    return isFocusVPWidget(shell, tracker);
  };

  const isEnabledDependOnSelected = (args: any): boolean => {
    if (!isEnabled()) {
      return false;
    }
    const current = getCurrent(tracker, shell, { ...args, activate: false });
    return !!current?.model.vpActions?.getSelectedCounts().nodesCount;
  };

  app.commands.addCommand(cmdIds.createNew, {
    label: args =>
      args['isPalette']
        ? vp4jlIDs.createNewLabelInPalette
        : args['isContextMenu']
        ? vp4jlIDs.createNewLabelInContextMenu
        : vp4jlIDs.createNewLabelInFileMenu,
    caption: vp4jlIDs.caption,
    execute: async args => {
      const cwd =
        args['cwd'] ||
        browserFactory.tracker.currentWidget?.model.path ||
        defaultFileBrowser?.model.path ||
        '';
      const model = await app.commands.execute('docmanager:new-untitled', {
        path: cwd,
        contentType: 'file',
        fileFormat: 'text',
        ext: vp4jlIDs.fileExtension,
        type: 'file'
      });
      if (model !== undefined) {
        const widget = (await app.commands.execute('docmanager:open', {
          path: model.path,
          factory: vp4jlIDs.widgetFactory
        })) as unknown as IDocumentWidget;
        widget.isUntitled = true;
        return widget;
      }
    }
  });

  app.commands.addCommand(cmdIds.run, {
    label: 'Run Visual Programming File',
    caption: 'Run the visual programming file',
    execute: args => {
      const current = getCurrent(tracker, shell, args);
      current?.execute();
    },
    icon: args => (args.toolbar ? runIcon : undefined),
    isEnabled
  });

  app.commands.addCommand(cmdIds.copy, {
    label: args => {
      const current = getCurrent(tracker, shell, { ...args, activate: false });
      return !args.toolbar
        ? 'Copy'
        : !current?.model.vpActions?.getSelectedCounts().nodesCount
        ? 'Copy Node'
        : 'Copy Nodes';
    },
    caption: args => {
      const current = getCurrent(tracker, shell, { ...args, activate: false });
      return !current?.model.vpActions?.getSelectedCounts().nodesCount
        ? 'Copy this node'
        : 'Copy theses nodes';
    },
    execute: args => {
      const current = getCurrent(tracker, shell, args);
      if (current) {
        current.model.vpActions?.copySelectedNodeToClipboard();
      }
    },
    icon: args => (args.toolbar ? copyIcon : undefined),
    isEnabled: args => {
      return isEnabledDependOnSelected(args);
    }
  });

  app.commands.addCommand(cmdIds.paste, {
    label: 'Paste',
    caption: 'Paste from the clipboard',
    execute: args => {
      const current = getCurrent(tracker, shell, args);
      if (current) {
        current.model.vpActions?.pasteFromClipboard();
      }
    },
    icon: args => (args.toolbar ? pasteIcon : undefined),
    isEnabled: args => {
      return isEnabledDependOnSelected(args);
    }
  });

  app.commands.addCommand(cmdIds.del, {
    label: 'Delete',
    caption: 'Delete the selected node',
    execute: args => {
      const current = getCurrent(tracker, shell, args);
      if (current) {
        current.model.vpActions?.deleteSelectedElements();
      }
    },
    icon: args => (args.toolbar ? deleteIcon : undefined),
    isEnabled: args => {
      return isEnabledDependOnSelected(args);
    }
  });

  app.commands.addCommand(cmdIds.cut, {
    label: 'Cut',
    caption: 'Cut the selected node',
    execute: args => {
      const current = getCurrent(tracker, shell, args);
      if (current) {
        current.model.vpActions?.cutSelectedNodesToClipboard();
      }
    },
    icon: args => (args.toolbar ? cutIcon : undefined),
    isEnabled: args => {
      return isEnabledDependOnSelected(args);
    }
  });

  app.commands.addCommand(cmdIds.duplicate, {
    label: 'Duplicate',
    caption: 'Duplicate the selected node',
    execute: args => {
      const current = getCurrent(tracker, shell, args);
      if (current) {
        current.model.vpActions?.duplicateSelectedNodes();
      }
    },
    icon: args => (args.toolbar ? duplicateIcon : undefined),
    isEnabled: args => {
      return isEnabledDependOnSelected(args);
    }
  });

  app.commands.addCommand(cmdIds.deleteAll, {
    label: 'Delete All',
    caption: 'Delete all nodes and edges',
    execute: args => {
      const current = getCurrent(tracker, shell, args);
      if (current) {
        current.model.vpActions?.clear();
      }
    },
    icon: args => (args.toolbar ? clearIcon : undefined),
    isEnabled
  });

  app.commands.addCommand(cmdIds.interruptKernel, {
    label: 'Interrupt Kernel',
    caption: 'Interrupt the kernel',
    execute: args => {
      const current = getCurrent(tracker, shell, args);
      if (!current) {
        return;
      }
      const kernel = current.sessionContext.session?.kernel;
      if (kernel) {
        return kernel.interrupt();
      }
    },
    icon: args => (args.toolbar ? stopIcon : undefined),
    isEnabled
  });

  app.commands.addCommand(cmdIds.restartKernel, {
    label: 'Restart Kernel',
    caption: 'Restart the kernel',
    execute: args => {
      const current = getCurrent(tracker, shell, args);
      if (current) {
        return sessionDialogs.restart(current.sessionContext);
      }
    },
    icon: args => (args.toolbar ? refreshIcon : undefined),
    isEnabled
  });

  app.commands.addCommand(cmdIds.clearOutput, {
    label: 'Clear Output',
    caption: 'Clear the output',
    execute: args => {
      console.log('clear output');
    },
    isEnabled
  });

  app.commands.addCommand(cmdIds.reconnectKernel, {
    label: 'Reconnect to Kernel',
    caption: 'Reconnect to the kernel',
    execute: args => {
      const current = getCurrent(tracker, shell, args);
      if (!current) {
        return;
      }
      const kernel = current.context.sessionContext.session?.kernel;

      if (kernel) {
        return kernel.reconnect();
      }
    },
    isEnabled
  });

  app.commands.addCommand(cmdIds.restartKernelAndRun, {
    label: 'Restart Kernel and Run',
    caption: 'Restart the kernel and re-run the whole file',
    execute: async args => {
      const restarted: boolean = await app.commands.execute(
        cmdIds.restartKernel,
        {
          activate: false
        }
      );
      if (restarted) {
        await app.commands.execute(cmdIds.run);
      }
    },
    icon: fastForwardIcon,
    isEnabled
  });

  app.commands.addCommand(cmdIds.shutdownKernel, {
    label: 'Shut Down Kernel',
    caption: 'Shutdown the kernel',
    execute: args => {
      const current = getCurrent(tracker, shell, args);
      if (current) {
        return current.context.sessionContext.shutdown();
      }
    },
    isEnabled
  });
  app.commands.addCommand(cmdIds.changeKernel, {
    label: 'Change Kernel…',
    execute: args => {
      const current = getCurrent(tracker, shell, args);

      if (current) {
        return sessionDialogs.selectKernel(current.context.sessionContext);
      }
    },
    isEnabled
  });

  app.commands.addCommand(cmdIds.showNodeExtension, {
    label: 'Show Node Packages Manager',
    execute: () => {
      labShell.activateById(vp4jlIDs.nodeExtension);
    }
  });

  app.commands.addCommand(cmdIds.hideNodeExtension, {
    label: 'Hide Node Extension',
    execute: () => {
      labShell.collapseLeft();
    }
  });

  app.commands.addCommand(cmdIds.toggleNodeExtension, {
    label: 'Node Packages Manager',
    execute: () => {
      if (nodeExtension.isHidden) {
        return app.commands.execute(cmdIds.showNodeExtension, void 0);
      }
      return app.commands.execute(cmdIds.hideNodeExtension, void 0);
    }
  });

  app.commands.addCommand(cmdIds.toggleOutput, {
    label: 'Output Area',
    execute: args => {
      const current = getCurrent(tracker, shell, args);
      if (current) {
        current.toggleOutput();
      }
    },
    isEnabled
  });
}

function isFocusVPWidget(
  shell: JupyterFrontEnd.IShell,
  tracker: IVPTracker
): boolean {
  return (
    tracker.currentWidget !== null &&
    tracker.currentWidget === shell.currentWidget
  );
}

function getCurrent(
  tracker: IVPTracker,
  shell: JupyterFrontEnd.IShell,
  args: ReadonlyPartialJSONObject
): VPWidget | null {
  const widget = tracker.currentWidget;
  const activate = args['activate'] !== false;

  if (activate && widget) {
    shell.activateById(widget.id);
  }

  return widget;
}

function activateVp4jlAttachCommandsToGui(
  app: JupyterFrontEnd,
  mainMenu: IMainMenu,
  tracker: IVPTracker,
  launcher: ILauncher | null,
  palette: ICommandPalette | null
) {
  const cmdIds = gVp4jlCommandIDs;
  const isEnabled = (): boolean => {
    return isFocusVPWidget(app.shell, tracker);
  };
  mainMenu.fileMenu.newMenu.addItem({ command: cmdIds.createNew, rank: 30 });
  mainMenu.editMenu.addGroup(
    [
      { command: cmdIds.copy },
      { command: cmdIds.paste },
      { command: cmdIds.duplicate },
      { command: cmdIds.cut },
      { command: cmdIds.del },
      { command: cmdIds.deleteAll }
    ],
    4
  );
  mainMenu.runMenu.codeRunners.run.add({
    id: cmdIds.run,
    isEnabled
  });
  mainMenu.kernelMenu.kernelUsers.interruptKernel.add({
    id: cmdIds.interruptKernel,
    isEnabled
  });
  mainMenu.kernelMenu.kernelUsers.restartKernel.add({
    id: cmdIds.restartKernel,
    isEnabled
  });
  mainMenu.kernelMenu.kernelUsers.reconnectToKernel.add({
    id: cmdIds.reconnectKernel,
    isEnabled
  });
  mainMenu.runMenu.codeRunners.restart.add({
    id: cmdIds.restartKernelAndRun,
    isEnabled
  });
  mainMenu.kernelMenu.kernelUsers.shutdownKernel.add({
    id: cmdIds.shutdownKernel,
    isEnabled
  });
  mainMenu.kernelMenu.kernelUsers.changeKernel.add({
    id: cmdIds.changeKernel,
    isEnabled
  });

  mainMenu.kernelMenu.kernelUsers.clearWidget.add({
    id: cmdIds.clearOutput,
    isEnabled
  });

  mainMenu.editMenu.clearers.clearCurrent.add({
    id: cmdIds.clearOutput,
    isEnabled
  });

  mainMenu.viewMenu.addItem({
    command: cmdIds.toggleNodeExtension,
    rank: 9
  });

  mainMenu.viewMenu.addItem({
    command: cmdIds.toggleOutput,
    rank: 9
  });

  launcher?.add({
    command: cmdIds.createNew,
    category: cmdIds.commandCategory,
    rank: 0
  });

  palette?.addItem({
    command: cmdIds.createNew,
    category: cmdIds.commandCategory,
    args: { isPalette: true }
  });

  app.contextMenu.addItem({
    command: cmdIds.createNew,
    selector: '.jp-DirListing-content',
    rank: 53,
    args: {
      isContextMenu: true
    }
  });
}

function activateVp4jlRestorer(
  app: JupyterFrontEnd,
  restorer: ILayoutRestorer | null,
  tracker: IVPTracker | null
) {
  const vp4jlIDs = gVP4jlIDs;
  if (restorer && tracker) {
    restorer.restore(tracker, {
      command: 'docmanager:open',
      args: widget => ({
        path: widget.context.path,
        factory: vp4jlIDs.widgetFactory
      }),
      name: widget => widget.context.path
    });
  }
}

function activateVp4jlNodeExtension(
  app: JupyterFrontEnd,
  restorer: ILayoutRestorer | null
): NodeExtension {
  const nodeExtension = new NodeExtension();
  app.shell.add(nodeExtension, 'left');

  if (restorer) {
    restorer.add(nodeExtension, 'vp4jlNodeExtension');
  }
  fetchNodeExtensions();
  return nodeExtension;
}

function fetchNodeExtensions() {
  requestAPI<any>('node_extension_manager')
    .then(data => {
      Object.entries(data.packages).forEach(([key, value]) => {
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        LoadPackageToRegistry(key, value!);
      });
    })
    .catch(reason => {
      console.error(`The vp4jl server error:\n${reason}`);
      console.error(`The vp4jl server error:\n${reason}`);
    });
}

function activateVp4jlFixContextMenuClose(
  app: JupyterFrontEnd,
  labShell: ILabShell
) {
  // close the context menu when switch the tab
  labShell.currentChanged.connect((_, args) => {
    if (args.oldValue instanceof VPWidget) {
      args.oldValue.content.deactivate();
    }
    closeDefaultContextMenu();
  });

  function closeDefaultContextMenu() {
    if (app.contextMenu.menu.isAttached) {
      app.contextMenu.menu.close();
    }
  }

  // close the context menu when click the tab
  function addClickEventToSideBar() {
    const sideBars = document.getElementsByClassName('jp-SideBar');
    if (!sideBars.length) {
      window.requestAnimationFrame(() => {
        addClickEventToSideBar();
      });
      return;
    }
    for (const sideBar of sideBars) {
      for (const tab of sideBar.getElementsByClassName('lm-TabBar-tab')) {
        (tab as HTMLElement).addEventListener('click', closeDefaultContextMenu);
      }
    }
  }

  window.requestAnimationFrame(() => {
    addClickEventToSideBar();
  });
}
