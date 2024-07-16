import Alt from 'alt';

import ApiActions from './actions/ApiActions';
import AuthActions from './actions/AuthActions';
import EnvironmentActions from './actions/EnvironmentActions';
import JupyterApiActions from './actions/JupyterApiActions';
import UserActions from './actions/UserActions';

import AuthStore from './stores/AuthStore';
import EnvironmentStore from './stores/EnvironmentStore';
import UserStore from './stores/UserStore';

class Flux extends Alt {
  constructor(options) {
    super();

    this.apiBaseUrl = options.apiBaseUrl;
    this.jupyterlab = options.jupyterlab;

    // register action creators
    this.addActions('ApiActions', ApiActions);
    this.addActions('AuthActions', AuthActions);
    this.addActions('EnvironmentActions', EnvironmentActions);
    this.addActions('JupyterApiActions', JupyterApiActions);
    this.addActions('UserActions', UserActions);

    // register the alt singleton with action creators
    this.registerAltWithActions();

    // register stores
    this.addStore('AuthStore', AuthStore);
    this.addStore('EnvironmentStore', EnvironmentStore);
    this.addStore('UserStore', UserStore);
  }

  registerAltWithActions = () => {
    // hack to provide the alt singleton to function-based action creators (necessitated by ES6 breaking class-based action creators in alt by mandating construction via 'new')
    for (const namespace in this.actions) {
      // namespace is the string provided as the first param of calls to this.addActions(...) above
      if (namespace !== 'global') {
        // this namespace is used internally by alt, so we leave it alone
        this.actions[namespace].registerAlt(this);
      }
    }
  };
}

export default Flux;
