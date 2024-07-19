import { Token } from '@lumino/coreutils';
import { WidgetTracker } from '@jupyterlab/apputils';
import { VPWidget } from './widget';

export type IVPTracker = WidgetTracker<VPWidget>;

export const IVPTrackerToken = new Token<IVPTracker>(
  '@jupyterlab/vp4jl:IVPTracker',
  `A widget tracker for visual programming files.
  Use this if you want to be able to iterate over and interact with file editors
  created by the application.`
);

export class VPTracker extends WidgetTracker<VPWidget> implements IVPTracker {}
