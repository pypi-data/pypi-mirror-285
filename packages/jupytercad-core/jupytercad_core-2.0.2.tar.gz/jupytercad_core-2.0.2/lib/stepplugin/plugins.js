import { ICollaborativeDrive } from '@jupyter/docprovider';
import { IJCadWorkerRegistryToken, IJupyterCadDocTracker, IJCadExternalCommandRegistryToken } from '@jupytercad/schema';
import { IThemeManager } from '@jupyterlab/apputils';
import { JupyterCadStepModelFactory } from './modelfactory';
import { JupyterCadWidgetFactory } from '../factory';
import { JupyterCadStepDoc } from './model';
const FACTORY = 'JupyterCAD STEP Viewer';
const activate = (app, tracker, themeManager, workerRegistry, externalCommandRegistry, drive) => {
    const widgetFactory = new JupyterCadWidgetFactory({
        name: FACTORY,
        modelName: 'jupytercad-stepmodel',
        fileTypes: ['step'],
        defaultFor: ['step'],
        tracker,
        commands: app.commands,
        workerRegistry,
        externalCommandRegistry
    });
    // Registering the widget factory
    app.docRegistry.addWidgetFactory(widgetFactory);
    // Creating and registering the model factory for our custom DocumentModel
    const modelFactory = new JupyterCadStepModelFactory();
    app.docRegistry.addModelFactory(modelFactory);
    // register the filetype
    app.docRegistry.addFileType({
        name: 'step',
        displayName: 'STEP',
        mimeTypes: ['text/json'],
        extensions: ['.step', '.STEP'],
        fileFormat: 'text',
        contentType: 'step'
    });
    const stepSharedModelFactory = () => {
        return new JupyterCadStepDoc();
    };
    if (drive) {
        drive.sharedModelFactory.registerDocumentFactory('step', stepSharedModelFactory);
    }
    widgetFactory.widgetCreated.connect((sender, widget) => {
        widget.context.pathChanged.connect(() => {
            tracker.save(widget);
        });
        themeManager.themeChanged.connect((_, changes) => widget.context.model.themeChanged.emit(changes));
        tracker.add(widget);
        app.shell.activateById('jupytercad::leftControlPanel');
        app.shell.activateById('jupytercad::rightControlPanel');
    });
};
const stepPlugin = {
    id: 'jupytercad:stepplugin',
    requires: [
        IJupyterCadDocTracker,
        IThemeManager,
        IJCadWorkerRegistryToken,
        IJCadExternalCommandRegistryToken
    ],
    optional: [ICollaborativeDrive],
    autoStart: true,
    activate
};
export default stepPlugin;
