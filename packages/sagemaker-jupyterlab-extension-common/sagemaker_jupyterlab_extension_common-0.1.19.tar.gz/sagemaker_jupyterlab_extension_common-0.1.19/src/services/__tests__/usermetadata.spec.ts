import { JupyterFrontEnd } from '@jupyterlab/application';
import { UserMetaDataService } from '../usermetadata';
import * as utils from '../../plugins/QDeveloperPlugin/q-developer';
import { AppEnvironment } from '../../types';

let userMetadataService: UserMetaDataService;

jest.spyOn(utils, 'updateSidebarIconToQ').mockImplementation();

describe('userMetadataService sm', () => {
  beforeEach(async () => {
    userMetadataService = new UserMetaDataService({} as JupyterFrontEnd);
    userMetadataService['region'] = 'us-west-2';
    jest
      .spyOn(userMetadataService as any, 'postAuthDetails')
      .mockResolvedValue({ isQDeveloperEnabled: true, environment: AppEnvironment.SMStudio });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should not initialize event listener if in sagemaker app environment', async () => {
    jest.spyOn(userMetadataService as any, 'updateMetadata').mockImplementation();

    const addEventListenerSpy = jest.spyOn(window, 'addEventListener');
    userMetadataService.initialize();
    const response = await userMetadataService['postAuthDetails']();
    expect(response?.isQDeveloperEnabled).toBeTruthy();
    expect(addEventListenerSpy).not.toHaveBeenCalled();
  });

  it('app environment is sm if we have accesstoken', async () => {
    const response = await userMetadataService['postAuthDetails']();
    expect(response?.isQDeveloperEnabled).toBeTruthy();
  });
});

describe('userMetadataService non sm', () => {
  beforeEach(async () => {
    userMetadataService = new UserMetaDataService({} as JupyterFrontEnd);
    userMetadataService['region'] = 'us-west-2';
    jest
      .spyOn(userMetadataService as any, 'postAuthDetails')
      .mockResolvedValue({ isQDeveloperEnabled: false, environment: AppEnvironment.MD });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should be defined', () => {
    expect(userMetadataService).toBeDefined();
    expect(userMetadataService.initialize).toBeDefined();
  });

  it('should add an event listener', async () => {
    const addEventListenerSpy = jest.spyOn(window, 'addEventListener');
    userMetadataService.initialize();
    await userMetadataService['postAuthDetails']();
    expect(addEventListenerSpy).toHaveBeenCalled();
  });

  it("app environment is not sm if we don't have accesstoken", async () => {
    const response = await userMetadataService['postAuthDetails']();
    expect(response?.isQDeveloperEnabled).toBeFalsy();
  });

  it('should post a message to the parent window that contains JL_COMMON_PLUGIN_LOADED when event listener is added.', async () => {
    const postMessageSpy = jest.spyOn(window, 'postMessage');
    userMetadataService.initialize();
    await userMetadataService['postAuthDetails']();
    expect(postMessageSpy).toHaveBeenCalledWith('JL_COMMON_PLUGIN_LOADED', '*');
  });

  it('getAllowedDomains should return valid domain origins based on the current region', async () => {
    expect(await userMetadataService['getAllowedDomains']()).toEqual([
      '.v2.us-west-2.beta.app.iceland.aws.dev',
      '.v2.niceland-gamma.us-west-2.on.aws',
      '.datazone.us-west-2.on.aws',
    ]);
  });

  it('isMessageOriginValid should return true if current origin is included in allowed domains (localhost dev example)', async () => {
    expect(
      userMetadataService['isMessageOriginValid'](
        new MessageEvent('message', { data: 'test', origin: 'http://localhost:5173' }),
        await userMetadataService['getAllowedDomains'](),
      ),
    ).toEqual(true);
  });

  it('isMessageOriginValid should return false if current origin is not included in allowed domains', async () => {
    expect(
      userMetadataService['isMessageOriginValid'](
        new MessageEvent('message', { data: 'test', origin: 'http://google.com' }),
        await userMetadataService['getAllowedDomains'](),
      ),
    ).toEqual(false);
  });

  it('isMessageOriginValid should return false if current origin is not included in allowed domains - inject subdomain', async () => {
    expect(
      userMetadataService['isMessageOriginValid'](
        new MessageEvent('message', { data: 'test', origin: 'http://hacker.datazone.us-west-2.on.aws.google.com' }),
        await userMetadataService['getAllowedDomains'](),
      ),
    ).toEqual(false);
  });

  it('isMessageOriginValid should return true if current origin is included in allowed domains', async () => {
    jest.spyOn(userMetadataService as any, 'isLocalhost').mockReturnValue(false);

    const originUrl = 'https://dzd_5tmhoefz7b8g87.v2.us-west-2.beta.app.iceland.aws.dev';

    expect(
      userMetadataService['isMessageOriginValid'](
        new MessageEvent('message', { data: 'test', origin: originUrl }),
        await userMetadataService['getAllowedDomains'](),
      ),
    ).toEqual(true);
  });
});
