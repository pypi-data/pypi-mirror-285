import { JupyterFrontEnd } from '@jupyterlab/application';
import { SAGEMAKER_AUTH_DETAILS_ENDPOINT, SAGEMAKER_CONTEXT_ENDPOINT } from '../constants';
import { updateSidebarIconToQ } from '../plugins/QDeveloperPlugin/q-developer';
import { AccessToken, AppEnvironment, AuthDetailsOutput, QDevProfile, UserMetaData } from '../types/usermetadata';
import { OPTIONS_TYPE, fetchApiResponse } from './fetchapi';

const ENDPOINT = 'api/contents';
const PLUGIN_LOADED_MESSAGE = 'JL_COMMON_PLUGIN_LOADED';
const AWS_DIRECTORY = '.aws';
const SSO_DIRECTORY = AWS_DIRECTORY + '/sso';
const Q_PROFILE_DIRECTORY = AWS_DIRECTORY + '/amazon_q';

const SM_INTERVAL_TIME = 5 * 60 * 1000; // 5 minutes

class UserMetaDataService {
  private region: string | undefined;

  private smInterval: NodeJS.Timeout | undefined;

  constructor(private app: JupyterFrontEnd) {}

  public async initialize() {
    const details = await this.postAuthDetails();
    if (details?.environment === AppEnvironment.SMStudio || details?.environment === AppEnvironment.SMStudioSSO) {
      if (details.isQDeveloperEnabled) {
        updateSidebarIconToQ(this.app);
        this.initializeSMInterval();
      }
    } else {
      updateSidebarIconToQ(this.app);
      this.initializeTwoWayIframeCommunication();
    }
  }

  private async initializeSMInterval(): Promise<void> {
    if (!this.smInterval) {
      this.smInterval = setInterval(async () => {
        await this.postAuthDetails();
      }, SM_INTERVAL_TIME);
    }
  }

  private async updateMetadata(metadata: UserMetaData) {
    await this.createDirectoryIfDoesNotExist(AWS_DIRECTORY, '.aws');
    await this.createDirectoryIfDoesNotExist(SSO_DIRECTORY, 'sso');
    await this.createDirectoryIfDoesNotExist(Q_PROFILE_DIRECTORY, 'amazon_q');

    await this.putMetadataFile(SSO_DIRECTORY, 'idc_access_token', 'json', { idc_access_token: metadata.accessToken });

    await this.putMetadataFile(Q_PROFILE_DIRECTORY, 'q_dev_profile', 'json', {
      q_dev_profile_arn: metadata.profileArn ?? '',
    });
  }

  private async postAuthDetails(): Promise<AuthDetailsOutput | undefined> {
    try {
      const response = await fetchApiResponse(SAGEMAKER_AUTH_DETAILS_ENDPOINT, OPTIONS_TYPE.POST);
      return (await response.json()) as AuthDetailsOutput;
    } catch {
      return undefined;
    }
  }

  private async getDirectory(path: string, returnContent?: boolean): Promise<Response | undefined> {
    try {
      return await fetchApiResponse(`${ENDPOINT}/${path}?content=${returnContent ? 1 : 0}`, OPTIONS_TYPE.GET);
    } catch {
      return undefined;
    }
  }

  private putDirectory = async (path: string, name: string): Promise<Response> =>
    await fetchApiResponse(
      `${ENDPOINT}/${path}`,
      OPTIONS_TYPE.PUT,
      JSON.stringify({ type: 'directory', format: 'text', name }),
    );

  private getAllowedDomains = async () => {
    if (!this.region) {
      try {
        const getStudioContextResponse = await fetchApiResponse(SAGEMAKER_CONTEXT_ENDPOINT, OPTIONS_TYPE.GET);
        const response = await getStudioContextResponse.json();
        this.region = response.region;
      } catch (err) {
        // couldnt't fetch context
      }
    }
    const region = this.region;

    return [
      `.v2.${region}.beta.app.iceland.aws.dev`,
      `.v2.niceland-gamma.${region}.on.aws`,
      `.datazone.${region}.on.aws`,
    ];
  };

  private isMessageOriginValid = (event: MessageEvent, allowedDomains: string[]) =>
    this.isLocalhost()
      ? event.origin === 'http://localhost:5173'
      : allowedDomains.some((domain) => event.origin.endsWith(domain));

  private putMetadataFile = async (
    path: string,
    name: string,
    ext: string,
    content: AccessToken | QDevProfile,
  ): Promise<Response> =>
    await fetchApiResponse(
      `${ENDPOINT}/${path ? `${path}/${name}.${ext}` : `/${name}.${ext}`}`,
      OPTIONS_TYPE.PUT,
      JSON.stringify({
        content: JSON.stringify(content),
        format: 'text',
        name: `${name}.${ext}`,
        type: 'file',
      }),
    );

  /**
   * Send a message to the parent window when the plugin is ready to receive user metadata.
   * NOTE: since this message is sent using an unrestricted domain origin, do not pass any sensitive
   * information using this method. This is strictly for handshaking.
   */
  private sendMessageWhenReadyToReceiveUserMetadata(): void {
    window.top?.postMessage(PLUGIN_LOADED_MESSAGE, '*');
  }

  private messageListener = async (event: MessageEvent): Promise<void> => {
    const allowedDomains = await this.getAllowedDomains();

    if (!this.isMessageOriginValid(event, allowedDomains)) return;

    try {
      const metadata = JSON.parse(event.data) as UserMetaData;

      if (!('accessToken' in metadata)) throw new Error('IAM Identity Center access token not found.');

      this.updateMetadata(metadata);
    } catch (err) {
      // create notification service to post error notification in UI.
    }
  };

  private async createDirectoryIfDoesNotExist(path: string, name: string) {
    const exists = await this.getDirectory(path, false);
    if (!exists) {
      await this.putDirectory(path, name);
    }
  }

  private isLocalhost() {
    return ['localhost', '127.0.0.1'].some((condition) => document.location.href.includes(condition));
  }

  /**
   * This method adds an event listener for listening to messages from the parent window
   * and sends a message to the parent window when the message listener has been added.
   * This prevents messages from the parent window from being sent before the plugin has been loaded.
   */
  private initializeTwoWayIframeCommunication(): void {
    window.addEventListener('message', this.messageListener);
    this.sendMessageWhenReadyToReceiveUserMetadata();
  }
}

export { UserMetaDataService };
