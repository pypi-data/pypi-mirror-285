function EnvironmentStore() {
  // initial state. same as standard RAMEN.
  this.state = {
    installingEnvironment: null,
    environmentCache: {},
    environments: []
  };

  // BEGIN DATA RELAY HANDLERS. logic within handlers is identical to its counterpart in standard RAMEN. only the binding to store prototype differs.
  EnvironmentStore.prototype.handleUpdateAll = environments => {
    // environments is an array, needs to be an object
    let { environmentCache } = this.state;
    environments.forEach(env => (environmentCache[env._id] = env)); // update cache
    this.setState({ environmentCache, environments });
  };

  EnvironmentStore.prototype.handleRegisterInstalling = environment => {
    this.setState({ installingEnvironment: environment });
  };
  // END DATA RELAY HANDLERS

  // register data relay handlers. same as standard RAMEN, but this block must follow the handler creation + binding to store prototype, or else the handlers cannot be found during the call to bindListeners.
  const { _updateAll, _registerInstalling } =
    this.alt.getActions('EnvironmentActions');
  this.bindListeners({
    handleUpdateAll: _updateAll,
    handleRegisterInstalling: _registerInstalling
  });
}

export default EnvironmentStore;
