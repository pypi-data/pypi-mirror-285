import { JupyterFrontEnd, LabShell } from '@jupyterlab/application';
import { Widget } from '@lumino/widgets';
import { qIcon } from '../../components/icons';

const JUPYTER_AI_CHAT_WIDGET_ID = 'jupyter-ai::chat';
const JUPYTER_AI_SETTINGS_BUTTON_SVG_SELECTOR = 'button svg[data-testid="SettingsIcon"]';

export function updateSidebarIconToQ(app: JupyterFrontEnd): void {
  if (app.shell instanceof LabShell) {
    const widgets = Array.from(app.shell.widgets('left'));
    const chatWidget = widgets.find((widget) => widget.id === JUPYTER_AI_CHAT_WIDGET_ID);
    if (chatWidget) {
      chatWidget.title.icon = qIcon;
      removeSettingsButton(chatWidget);
    }
  }
}

export function removeSettingsButton(chatWidget: Widget): void {
  const config = { attributes: true, childList: true, subtree: true };
  const removeButtonIfExists = (observer: MutationObserver) => {
    const settingsButton = chatWidget.node.querySelector(JUPYTER_AI_SETTINGS_BUTTON_SVG_SELECTOR)?.parentElement;
    if (settingsButton) {
      settingsButton.remove();
      observer.disconnect();
    }
  };
  const settingsButtonObserver = new MutationObserver((mutationsList, observer) => {
    removeButtonIfExists(observer);
  });
  settingsButtonObserver.observe(chatWidget.node, config);
  removeButtonIfExists(settingsButtonObserver);
}
