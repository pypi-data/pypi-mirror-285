import { DocumentRegistry, ABCWidgetFactory } from '@jupyterlab/docregistry';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { IVPModel } from './model';
import { VPWidget } from './widget';
import { IVPContext } from './context';

export class VPWidgetFactory extends ABCWidgetFactory<VPWidget, IVPModel> {
  // the main widget is main area of the jupyter lab
  private _mainWidget: HTMLElement | null = null;
  private _widgets: VPWidget[] = [];
  private _widgetId = 0;
  private _onMouseDown = this.deactivateWidgetIfMouseDownOut.bind(this);
  private _rendermime: IRenderMimeRegistry;

  constructor(
    options: DocumentRegistry.IWidgetFactoryOptions<VPWidget>,
    rendermime: IRenderMimeRegistry
  ) {
    super(options);
    this._rendermime = rendermime;
  }

  protected createNewWidget(context: IVPContext): VPWidget {
    context.model.setRendermime(this._rendermime);
    const w = new VPWidget(`vp_widget_${++this._widgetId}`, context);
    this.onWidgetCreated(w);
    w.disposed.connect(w => {
      this.onWidgetDisposed(w);
    });
    window.requestAnimationFrame(this._addEventListenerToTab.bind(this));

    return w;
  }

  private deactivateWidgetIfMouseDownOut(event: MouseEvent) {
    for (const w of this._widgets) {
      const rect = w.node.getBoundingClientRect();
      const hidden =
        !rect ||
        (rect.x === 0 && rect.y === 0 && rect.width === 0 && rect.height === 0);
      if (hidden) {
        continue;
      }
      const isInWidget =
        rect.x <= event.clientX &&
        event.clientX <= rect.x + rect.width &&
        rect.y <= event.clientY &&
        event.clientY <= rect.y + rect.height;
      if (!isInWidget) {
        w.content.deactivate();
      } else {
        w.content.activate();
      }
    }
  }

  private onWidgetCreated(w: VPWidget) {
    this._widgets.push(w);
    if (this._mainWidget === null) {
      this._mainWidget = document.getElementById('main');
    }
    if (this._widgets.length === 1) {
      this._mainWidget?.addEventListener('mousedown', this._onMouseDown);
      this._addEventListeners();
    }
  }

  private onWidgetDisposed(widget: VPWidget) {
    this._widgets.splice(this._widgets.indexOf(widget), 1);
    if (this._widgets.length === 0) {
      this._mainWidget?.removeEventListener('mousedown', this._onMouseDown);
      this._removeEventListeners();
    }
  }

  // hack way
  private _addEventListeners() {
    // onPanelContextMenu from vp editor stop propagation
    document.addEventListener('contextmenu', this._onMouseDown);
    const sideBars = document.getElementsByClassName('jp-SideBar');
    for (let i = 0; i < sideBars.length; i++) {
      const sideBar = sideBars[i];
      for (const tab of sideBar.getElementsByClassName('lm-TabBar-tab')) {
        (tab as HTMLElement).addEventListener('click', this._onMouseDown);
      }
    }
    const menuBar = document.getElementById('jp-top-panel');
    const menus = menuBar?.getElementsByClassName('lm-MenuBar-item');
    for (const menu of menus || []) {
      (menu as HTMLElement).addEventListener('click', this._onMouseDown);
    }
  }

  private _addEventListenerToTab() {
    // When click on the other tab of the main area, the currentChanged(index.ts) will be triggered.
    // We only need to add the click event listener to the tab corresponding to the current widget
    const dockPanel = document.getElementById('jp-main-dock-panel');
    (
      dockPanel?.getElementsByClassName('lm-mod-current')[0] as HTMLElement
    ).addEventListener('click', this._onMouseDown);
  }

  private _removeEventListeners() {
    document.removeEventListener('contextmenu', this._onMouseDown);
    const sideBars = document.getElementsByClassName('jp-SideBar');
    for (let i = 0; i < sideBars.length; i++) {
      const sideBar = sideBars[i];
      for (const tab of sideBar.getElementsByClassName('button')) {
        (tab as HTMLElement).removeEventListener('click', this._onMouseDown);
      }
    }
    const menuBar = document.getElementById('jp-top-panel');
    const menus = menuBar?.getElementsByClassName('lm-MenuBar-item');
    for (const menu of menus || []) {
      (menu as HTMLElement).removeEventListener('click', this._onMouseDown);
    }
  }
}
