function UserStore() {
  // initial state. same as standard RAMEN.
  this.state = {
    user: null,
    config: null,
    isMount: null
  };

  // BEGIN DATA RELAY HANDLERS. logic within handlers is identical to its counterpart in standard RAMEN. only the binding to store prototype differs.
  UserStore.prototype.handleUpdateUser = user => {
    this.setState({
      user: user
    });
  };

  UserStore.prototype.handleUpdateConfig = config => {
    this.setState({
      config: config
    });
  };

  UserStore.prototype.handleUpdateIsMount = isMount => {
    this.setState({
      isMount: isMount
    });
  };
  // END DATA RELAY HANDLERS

  // register data relay handlers. same as standard RAMEN, but this block must follow the handler creation + binding to store prototype, or else the handlers cannot be found during the call to bindListeners.
  const { _updateUser, _updateConfig, _updateIsMount } =
    this.alt.getActions('UserActions');
  this.bindListeners({
    handleUpdateUser: _updateUser,
    handleUpdateConfig: _updateConfig,
    handleUpdateIsMount: _updateIsMount
  });
}

export default UserStore;
