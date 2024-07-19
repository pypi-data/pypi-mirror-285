interface UserMetaData {
  accessToken: string;
  profileArn?: string;
}

interface AccessToken {
  idc_access_token: string;
}

interface QDevProfile {
  q_dev_profile_arn: string;
}

export enum AppEnvironment {
  SMStudio = 'SageMaker Studio',
  SMStudioSSO = 'SageMaker Studio SSO',
  MD = 'MD',
}

export interface AuthDetailsOutput {
  isQDeveloperEnabled: boolean;
  environment: AppEnvironment;
}

export { UserMetaData, AccessToken, QDevProfile };
