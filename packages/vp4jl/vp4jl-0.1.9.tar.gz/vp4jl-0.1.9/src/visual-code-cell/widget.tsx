import React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { Widget } from '@lumino/widgets';
import { CodeEditor } from '@jupyterlab/codeeditor';
import {
  VPEditor,
  ISceneActions,
  SerializedGraph,
  GenResult
} from 'chaldene_vpe';

type ISharedText = any;

function isSerializedGraph(object: any): boolean {
  return (
    object &&
    typeof object === 'object' &&
    Array.isArray(object.nodes) &&
    Array.isArray(object.edges)
  );
}

export class VPWidget extends ReactWidget {
  constructor(id: string, model: CodeEditor.IModel) {
    super();
    this.id = id;
    this.node.style.width = '100%';
    this.node.style.height = '100%';
    this.node.addEventListener('contextmenu', e => {
      e.preventDefault();
      e.stopPropagation();
    });

    this.node.addEventListener('focusout', function (e) {
      e.preventDefault();
      const nextFocusedElement = e.relatedTarget as HTMLElement;
      const isElementChild = this.contains(nextFocusedElement);
      const isMenu = nextFocusedElement?.classList[0].includes('Mui');
      if (nextFocusedElement && (isElementChild || isMenu)) {
        e.stopPropagation();
      }
    });
    this._model = model;
  }

  get sharedModel(): ISharedText {
    return this._model.sharedModel;
  }

  setSceneActions(actions: ISceneActions | null): void {
    this._sceneActions = actions;
  }

  closeMenu(): void {
    this._sceneActions?.closeMenu();
  }

  get hasFocus(): boolean {
    return this._editor_activated;
  }

  focus(): void {
    if (!this._editor_activated) {
      this._editor_activated = true;

      this.update();
    }
  }

  blur(): void {
    if (this._editor_activated) {
      this._editor_activated = false;
      this.update();
    }
  }

  get content(): SerializedGraph {
    let source = undefined;
    try {
      source = JSON.parse(this.sharedModel.getSource());
    } catch (e) {
      source = undefined;
    }

    return isSerializedGraph(source) ? source : null;
  }

  setContent(newContent: string) {
    if (this.sharedModel.getSource() !== newContent) {
      this.sharedModel.setSource(newContent);
    }
  }

  getCode(): GenResult {
    return this._sceneActions?.sourceCode();
  }

  render(): JSX.Element {
    return (
      <VPEditor
        id={this.id}
        content={this.content}
        onContentChange={this.setContent.bind(this)}
        activated={this._editor_activated}
        onSceneActionsInit={this.setSceneActions.bind(this)}
        option={{
          minimap: {
            collapsed: true
          }
        }}
      />
    );
  }

  private _model: CodeEditor.IModel;
  private _editor_activated = false;
  private _sceneActions: any | null = null;
}

export function createVPWidget(id: string, model: any, host: HTMLElement): any {
  const editor = new VPWidget(id, model);
  host.style.height = '300px';
  host.style.overflow = 'auto';
  host.style.resize = 'vertical';

  window.requestAnimationFrame(() => {
    if (host.isConnected) {
      Widget.attach(editor, host);
    }
  });
  return editor;
}
