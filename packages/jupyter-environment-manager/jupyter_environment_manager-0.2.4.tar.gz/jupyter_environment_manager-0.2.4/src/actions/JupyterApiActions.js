import { URLExt } from '@jupyterlab/coreutils';

import { ServerConnection } from '@jupyterlab/services';

export default function () {
  this.registerAlt = alt => {
    // hack to provide the alt singleton to function-based action creators
    // (necessitated by ES6 breaking class-based action creators in alt by
    // mandating construction via 'new')
    this.alt = alt;
  };

  this.query = (endpoint, query) =>
    new Promise(async (resolve, reject) => {
      const settings = ServerConnection.makeSettings();
      const requestUrl = URLExt.join(
        settings.baseUrl,
        'jupyter-environment-manager',
        endpoint
      );

      let response;
      try {
        response = await ServerConnection.makeRequest(
          requestUrl,
          query,
          settings
        );
      } catch (err) {
        console.log(err);
        reject(err);
      }

      const data = await response.json();

      if (!response.ok) {
        reject({ response, data });
      }

      resolve(data);
    });
}
