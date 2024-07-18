import { ILauncher } from '@jupyterlab/launcher';
import { treeViewIcon } from '@jupyterlab/ui-components';
import { JUPYTER_EXT } from './constants';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { Menu } from '@lumino/widgets';
import { 
  AlgorithmCatalogWidget, 
  RegisterAlgorithmsWidget } from './classes/App';
import { 
  ICommandPalette, 
  MainAreaWidget,
  WidgetTracker } from '@jupyterlab/apputils';
import {
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin } from '@jupyterlab/application';


  // Add 'View Algorithms' and 'Register Algorithms' plugins to the jupyter lab 'Algorithms' menu
const algorithms_menu_plugin: JupyterFrontEndPlugin<void> = {
  id: 'algorithms-menu',
  autoStart: true,
  requires: [IMainMenu],
  activate: (app: JupyterFrontEnd, mainMenu: IMainMenu) => {
    const { commands } = app;
    let algorithmsMenu = new Menu({ commands });
    algorithmsMenu.id = 'algorithms-menu';
    algorithmsMenu.title.label = 'Algorithms';
    [
      // JUPYTER_EXT.VIEW_ALGORITHMS_OPEN_COMMAND,
      JUPYTER_EXT.REGISTER_ALGORITHM_OPEN_COMMAND
    ].forEach(command => {
      algorithmsMenu.addItem({ command });
    });
    mainMenu.addMenu(algorithmsMenu)
  }
};

const algorithm_catalog_plugin: JupyterFrontEndPlugin<void> = {
  id: JUPYTER_EXT.VIEW_ALGORITHMS_PLUGIN_ID,
  autoStart: true,
  optional: [ILauncher, ICommandPalette, ILayoutRestorer],
  activate: (app: JupyterFrontEnd, 
             launcher: ILauncher, 
             palette: ICommandPalette,
             restorer: ILayoutRestorer) => {

    const { commands } = app;
    const command = JUPYTER_EXT.VIEW_ALGORITHMS_OPEN_COMMAND;

    let algorithmCatalogWidget: MainAreaWidget<AlgorithmCatalogWidget> | null = null;

    const algorithmCatalogTracker = new WidgetTracker<MainAreaWidget<AlgorithmCatalogWidget>>({
      namespace: 'view-algorithms-tracker'
    });

    if (restorer) {
      restorer.restore(algorithmCatalogTracker, {
        command: JUPYTER_EXT.VIEW_ALGORITHMS_OPEN_COMMAND,
        name: () => 'view-algorithms-tracker'
      });
    }

    commands.addCommand(command, {
      caption: JUPYTER_EXT.VIEW_ALGORITHMS_NAME,
      label: JUPYTER_EXT.VIEW_ALGORITHMS_NAME,
      icon: (args) => (args['isPalette'] ? null : treeViewIcon),
      execute: () => {
        const content = new AlgorithmCatalogWidget(app);
        algorithmCatalogWidget = new MainAreaWidget<AlgorithmCatalogWidget>({ content });
        algorithmCatalogWidget.title.label = JUPYTER_EXT.VIEW_ALGORITHMS_NAME;
        algorithmCatalogWidget.title.icon = treeViewIcon;
        app.shell.add(algorithmCatalogWidget, 'main');

        // Add widget to the tracker so it will persist on browser refresh
        algorithmCatalogTracker.save(algorithmCatalogWidget)
        algorithmCatalogTracker.add(algorithmCatalogWidget)
      },
    });

    const category = 'MAAP Extensions'

    // if (launcher) {
    //   launcher.add({
    //     command,
    //     category: category
    //   });
    // }

    console.log('JupyterLab MAAP Algorithms Registration extension is activated!');
  }
};


const algorithm_registration_plugin: JupyterFrontEndPlugin<void> = {
  id: JUPYTER_EXT.REGISTER_ALGORITHM_PLUGIN_ID,
  autoStart: true,
  optional: [ILauncher, ICommandPalette, ILayoutRestorer],
  activate: (app: JupyterFrontEnd, 
             launcher: ILauncher, 
             palette: ICommandPalette,
             restorer: ILayoutRestorer) => {

    const { commands } = app;
    const command = JUPYTER_EXT.REGISTER_ALGORITHM_OPEN_COMMAND;

    let registerAlgorithmsWidget: MainAreaWidget<RegisterAlgorithmsWidget> | null = null;

    const registerAlgorithmsTracker = new WidgetTracker<MainAreaWidget<RegisterAlgorithmsWidget>>({
      namespace: 'register-algorithms-tracker'
    });

    if (restorer) {
      restorer.restore(registerAlgorithmsTracker, {
        command: JUPYTER_EXT.REGISTER_ALGORITHM_OPEN_COMMAND,
        name: () => 'register-algorithms-tracker'
      });
    }

    commands.addCommand(command, {
      caption: JUPYTER_EXT.REGISTER_ALGORITHM_NAME,
      label: JUPYTER_EXT.REGISTER_ALGORITHM_NAME,
      icon: (args) => (args['isPalette'] ? null : treeViewIcon),
      execute: (data) => {
        console.log("Data coming in: ")
        console.log(data)
        const content = new RegisterAlgorithmsWidget(data);
        registerAlgorithmsWidget = new MainAreaWidget<RegisterAlgorithmsWidget>({ content });
        registerAlgorithmsWidget.title.label = JUPYTER_EXT.REGISTER_ALGORITHM_NAME;
        registerAlgorithmsWidget.title.icon = treeViewIcon;
        app.shell.add(registerAlgorithmsWidget, 'main');

        // Add widget to the tracker so it will persist on browser refresh
        registerAlgorithmsTracker.save(registerAlgorithmsWidget)
        registerAlgorithmsTracker.add(registerAlgorithmsWidget)
      },
    });

    if (launcher) {
      launcher.add({
        command,
        category: "MAAP Extensions"
      });
    }

    const category = 'MAAP Extensions'

    palette.addItem({ command: JUPYTER_EXT.REGISTER_ALGORITHM_OPEN_COMMAND, category });

    console.log('JupyterLab register-algorithm plugin is activated!');
  }
};

export default [algorithms_menu_plugin, algorithm_catalog_plugin, algorithm_registration_plugin];
