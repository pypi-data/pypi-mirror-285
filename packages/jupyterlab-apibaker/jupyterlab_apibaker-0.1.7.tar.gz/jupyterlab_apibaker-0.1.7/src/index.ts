import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ILauncher } from "@jupyterlab/launcher"
import { IMainMenu } from '@jupyterlab/mainmenu';
import { INotebookModel, NotebookPanel } from '@jupyterlab/notebook';
import { PageConfig } from '@jupyterlab/coreutils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { IDisposable, DisposableDelegate } from '@lumino/disposable';
import { InputDialog, ToolbarButton, Notification, MainAreaWidget } from '@jupyterlab/apputils';
import { Menu } from '@lumino/widgets';
import { APICatalogWidget } from './widgets/APICatalogWidget';

import isEmpty from 'lodash.isempty';
import isUndefined from 'lodash.isundefined';

// Types
import { IEndpointResponse, IImageCreationJob, IImageUpdate, INBFunction, INotebookContentAndMetadata, IParsedNBResponse } from './common/types';

// Commons
import { requestAPI } from './common/requestAPI';
import { extRemoverCorrector } from './common/utils';

const plugin: JupyterFrontEndPlugin<void> = {
     id: 'jupyterlab-apibaker:plugin',
     description: 'Create a secured API based on a function in your notebook in a few clicks.',
     autoStart: true,
     optional: [ISettingRegistry, ILauncher, IMainMenu],
     activate
};

export class BakeAPINotebookToolbarButton implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel> {
     createNew(panel: NotebookPanel, _: DocumentRegistry.IContext<INotebookModel>): IDisposable {
          const bakeAPI = async () => {
               const currentUserOwner = PageConfig.getOption('serverRoot').split('/')[2] || ""
               let currentNotebookRaw = this.getNBContentAndMetadata(panel)
               let nbPath = `${PageConfig.getOption('serverRoot')}/${panel.context.contentsModel?.path}`

               if (isUndefined(currentNotebookRaw)) {
                    console.log("There has been an error parsing the current notebook. Please, contact the administrator.")
                    return;
               };

               const extractedNBFunctions = await this.getNBFunctions(currentNotebookRaw)

               if (isUndefined(extractedNBFunctions)) {
                    console.log("No functions found in the notebook.")
                    return;
               };

               const userSelectedFunction = await this.promptUserToSelectFunctionFromNB(extractedNBFunctions.data.nbfunctions);

               if (isUndefined(userSelectedFunction)) {
                    return;
               };

               const userSelectedFunctionAndCode: INBFunction = extractedNBFunctions.data.nbfunctions.filter((el: INBFunction) => el.functionName === userSelectedFunction)[0];

               const apiDescription = await InputDialog.getText({
                    title: "Bake a New API",
                    label: "Provide a short description for your API:",
                    placeholder: "Please, insert a short description.",
                    okLabel: "Create",
                    cancelLabel: "Cancel",
               });

               if (!apiDescription.button.accept) {
                    return;
               }

               if (isEmpty(apiDescription.value)) {
                    Notification.warning(`Please, insert a short description.`, { autoClose: 3000 });
                    return;
               }

               const createEndpoint = await requestAPI<IEndpointResponse>("endpoint", {
                    method: "POST",
                    body: JSON.stringify({
                         functionName: userSelectedFunctionAndCode.functionName,
                         functionCode: userSelectedFunctionAndCode.functionCode,
                         description: apiDescription.value,
                         notebookName: currentNotebookRaw.nbName,
                         owner: currentUserOwner,
                         nbPath
                    })
               });

               console.log(`Create Endpoint Response => ${JSON.stringify(createEndpoint, null, 2)}`)

               let getEndpointUpdate: IImageUpdate
               let i = 1
               let imageCreationStatus: string = ''
               let prepareStage: IImageCreationJob = { id: 0, jobId: '', reason: '', stage: '', status: '', trace: '' }
               let buildAndPushStage: IImageCreationJob = { id: 0, jobId: '', reason: '', stage: '', status: '', trace: '' }
               let retry = true
               let notif = Notification.manager.notify("Baking API...", 'in-progress', {})

               do {
                    getEndpointUpdate = await requestAPI<IImageUpdate>("get-endpoint-updates", {
                         method: "POST",
                         body: JSON.stringify({
                              id: createEndpoint.data.id,
                              version: createEndpoint.data.versions[0].id,
                              owner: currentUserOwner,
                              action: 'image'
                         })
                    })
                    const delayMs = 500 * 2 ** i
                    console.log(`Delay => ${delayMs}`)

                    if (getEndpointUpdate&& getEndpointUpdate.data.jobs && getEndpointUpdate.data.jobs.length > 0) {
                         imageCreationStatus = getEndpointUpdate.data.status
                         prepareStage = getEndpointUpdate.data.jobs.filter((item: any) => item.stage === 'prepare')[0]
                         buildAndPushStage = getEndpointUpdate.data.jobs.filter((item: any) => item.stage === 'build_and_push')[0]
                    }
                    console.log(`Prepare Stage Info => ${JSON.stringify(prepareStage)}`)
                    console.log(`Build and Push Stage Info => ${JSON.stringify(buildAndPushStage)}`)

                    if (['created', 'running', 'pending', ''].includes(prepareStage.status) || ['created', 'running', 'pending', ''].includes(buildAndPushStage.status)) {
                         Notification.manager.update({
                              id: notif,
                              message: `Creation Jobs -> Prepare: ${prepareStage.status} | Build and Push: ${buildAndPushStage.status}`,
                              type: 'in-progress'
                         })
                         await new Promise((resolve) => setTimeout(resolve, delayMs))
                         if (delayMs >= 20000) {
                              i = 0
                         }
                         i++
                    } else if (prepareStage.status === 'failed' || buildAndPushStage.status === 'failed') {
                         Notification.manager.update({
                              id: notif,
                              message: `Creation Jobs Error -> Prepare: ${prepareStage.status} | Build and Push: ${buildAndPushStage.status}`,
                              type: 'error'
                         })
                         retry = false
                    } else if (prepareStage.status === 'success' && buildAndPushStage.status === 'success') {
                         Notification.manager.update({
                              id: notif,
                              message: `Creation Jobs Success -> Prepare: ${prepareStage.status} | Build and Push: ${buildAndPushStage.status}`,
                              type: 'success'
                         })
                         retry = false
                    } else {
                         Notification.manager.update({
                              id: notif,
                              message: `Creation Jobs Info: ${imageCreationStatus}`,
                              type: 'info'
                         })
                         retry = false
                    }
               } while (retry)
          };

          const button = new ToolbarButton({
               className: "apiBaker",
               label: "Bake API",
               onClick: bakeAPI,
               tooltip: "Create an API endpoint based on a selected function from this notebook.",
          });

          panel.toolbar.insertItem(10, "bake-api", button);
          return new DisposableDelegate(() => {
               button.dispose();
          });

     };

     getNBContentAndMetadata(panel: NotebookPanel): INotebookContentAndMetadata | undefined {
          if (!panel.model || !panel.context.isReady) {
               return;
          }

          return {
               nbName: extRemoverCorrector(panel.title.label),
               nbRawName: panel.title.label,
               nbRaw: panel.model.toJSON(),
               pathToNotebook: `${PageConfig.getOption('serverRoot')} / ${panel.context.contentsModel?.path}`
          };
     };

     async getNBFunctions(nbContentAndMetadata: INotebookContentAndMetadata): Promise<IParsedNBResponse | undefined> {
          const nbInfo: IParsedNBResponse = await requestAPI<any>("parse-model", {
               method: "POST",
               body: JSON.stringify(nbContentAndMetadata.nbRaw)
          });

          console.log(`Functions List => ${JSON.stringify(nbInfo, null, 2)}`)

          if (isEmpty(nbInfo.data.nbfunctions)) {
               return
          };

          return nbInfo;
     };

     async promptUserToSelectFunctionFromNB(functionsInNotebook: INBFunction[]): Promise<string | void> {
          let functionsToSelect = functionsInNotebook.map((el: INBFunction) => el.functionName);
          const functionSelector = await InputDialog.getItem({
               title: "Bake a New API",
               label: "Select Function:",
               items: functionsToSelect,
               okLabel: "Next",
               cancelLabel: "Cancel",
          });

          if (!functionSelector.button.accept) {
               return;
          }

          if (isUndefined(functionSelector.value)) {
               return undefined;
          }

          return functionSelector.value!;
     }
};

function activate(app: JupyterFrontEnd, settingRegistry: ISettingRegistry | null, launcher: ILauncher, mainMenu: IMainMenu, panel: NotebookPanel): void {
     console.log('API Baker Extension Activated!');
     app.docRegistry.addWidgetExtension("Notebook", new BakeAPINotebookToolbarButton())
     Promise.all([app.restored]).then(() => {
          // a state perhaps https://github.com/jupyterlab/extension-examples/tree/3.x/state
          // Get state variables and jobs queue?
          // update jobs panel?
          // update notifications?
     });
     const { commands } = app;
     const command = "jlab-apibaker:command";
     commands.addCommand(command, {
          caption: "Show API Collection",
          label: "API Collection",
          execute: async () => {
               const currentUserOwner = PageConfig.getOption('serverRoot').split('/')[2] || ""
               console.log(`Owner => ${currentUserOwner}`)
               const content = new APICatalogWidget();
               const widget = new MainAreaWidget<APICatalogWidget>({ content });
               widget.title.label = "API Collection";
               app.shell.add(widget, "main");
          },
     });

     const menu = new Menu({ commands: app.commands });
     menu.title.label = "API Baker";
     menu.addItem({ command });

     mainMenu.addMenu(menu, true, { rank: 900 });
}

export default plugin;
