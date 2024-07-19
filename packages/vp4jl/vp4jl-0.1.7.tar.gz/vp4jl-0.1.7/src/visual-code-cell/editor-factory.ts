import { CodeEditor } from '@jupyterlab/codeeditor';
import { VisualCodeEditor } from './editor';
export const VisualCodeEditorFactory = (options: CodeEditor.IOptions): any => {
  options.host.dataset.type = 'inline';
  return new VisualCodeEditor(options);
};
