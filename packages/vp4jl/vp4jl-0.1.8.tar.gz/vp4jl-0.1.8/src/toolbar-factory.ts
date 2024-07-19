import { Widget } from '@lumino/widgets';
import { CommandRegistry } from '@lumino/commands';
import { ExecutionIndicator } from '@jupyterlab/notebook';
import { Toolbar } from '@jupyterlab/apputils/lib/toolbar';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { ToolbarRegistry, createDefaultFactory } from '@jupyterlab/apputils';
import { ToolbarItems as DocToolbarItems } from '@jupyterlab/docmanager-extension';
import { vp4jlCommandIDs } from './namepace';
import { VPWidget } from './widget';

interface IToolbarItemWithFactoryConfig {
  name: string;
  factory: (widget: VPWidget) => Widget;
}

type IToolbarItemConfig =
  | IToolbarItemWithFactoryConfig
  | ToolbarRegistry.IWidget;

type IDefaultToolbarFactory = (
  widgetFactory: string,
  widget: Widget,
  toolbarItem: ToolbarRegistry.IWidget
) => Widget;

function getToolbarItems(commands: CommandRegistry): IToolbarItemConfig[] {
  return [
    {
      name: 'save',
      factory: (widget: VPWidget) =>
        DocToolbarItems.createSaveButton(commands, widget.context.fileChanged)
    },
    { name: 'cut', command: vp4jlCommandIDs.cut },
    { name: 'copy', command: vp4jlCommandIDs.copy },
    { name: 'paste', command: vp4jlCommandIDs.paste },
    { name: 'duplicate', command: vp4jlCommandIDs.duplicate },
    { name: 'delete', command: vp4jlCommandIDs.del },
    { name: 'deleteAll', command: vp4jlCommandIDs.deleteAll },
    { name: 'run', command: vp4jlCommandIDs.run },
    { name: 'interrupt', command: vp4jlCommandIDs.interruptKernel },
    { name: 'restart', command: vp4jlCommandIDs.restartKernel },
    {
      name: 'restart-and-run',
      command: vp4jlCommandIDs.restartKernelAndRun
    },
    { name: 'spacer', type: 'spacer' },
    {
      name: 'kernelName',
      factory: (widget: VPWidget) =>
        Toolbar.createKernelNameItem(widget.sessionContext)
    },
    {
      name: 'executionProgress',
      factory: (widget: VPWidget) =>
        ExecutionIndicator.createExecutionIndicatorItem(
          // @ts-ignore
          widget,
          undefined,
          undefined
        )
    }
  ];
}

function createWidget(
  widget: VPWidget,
  widgetFactory: string | undefined,
  item: IToolbarItemConfig,
  defaultFactory: IDefaultToolbarFactory
): Widget {
  return item.factory
    ? (item as IToolbarItemWithFactoryConfig).factory(widget)
    : defaultFactory(
        widgetFactory ?? '',
        widget,
        item as ToolbarRegistry.IWidget
      );
}

export function getToolbarFactory(
  commands: CommandRegistry,
  widgetFactory?: string
): (widget: VPWidget) => DocumentRegistry.IToolbarItem[] {
  const toolbarItems = getToolbarItems(commands);
  const defaultFactory = createDefaultFactory(commands);

  return (widget: VPWidget): DocumentRegistry.IToolbarItem[] => {
    const toolbar = toolbarItems.map(item => ({
      name: item.name,
      widget: createWidget(widget, widgetFactory, item, defaultFactory)
    }));
    widget.model?.setToolbarItems(toolbar);
    return toolbar;
  };
}
