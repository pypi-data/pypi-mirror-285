import { DocumentRegistry, TextModelFactory } from '@jupyterlab/docregistry';
import { ISharedFile } from '@jupyter/ydoc';
import { IVPModel, VPModel } from './model';
import { vp4jlIDs } from './namepace';

export type IVPModelFactory = DocumentRegistry.IModelFactory<IVPModel>;

export class VPModelFactory
  extends TextModelFactory
  implements IVPModelFactory
{
  get name(): string {
    return vp4jlIDs.modelFactory;
  }

  createNew(
    options: DocumentRegistry.IModelOptions<ISharedFile> = {}
  ): IVPModel {
    const collaborative = options.collaborationEnabled && this.collaborative;
    return new VPModel({
      ...options,
      collaborationEnabled: collaborative
    });
  }
}
