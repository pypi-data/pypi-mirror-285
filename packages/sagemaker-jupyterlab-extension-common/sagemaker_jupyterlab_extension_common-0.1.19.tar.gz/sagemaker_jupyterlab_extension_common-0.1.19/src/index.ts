import { DeepLinkingPlugin, PanoramaPlugin, QDeveloperPlugin } from './plugins';
import { ILogger, logSchemas, LoggerPlugin, SchemaDefinition } from './plugins';

export { ILogger, logSchemas, SchemaDefinition };
export default [PanoramaPlugin, LoggerPlugin, DeepLinkingPlugin, QDeveloperPlugin];
