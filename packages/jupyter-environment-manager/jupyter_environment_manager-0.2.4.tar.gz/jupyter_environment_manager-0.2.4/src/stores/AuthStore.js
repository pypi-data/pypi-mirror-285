function AuthStore() {
  // initial state. same as standard RAMEN.
  this.state = {
    isAuthenticated: false,
    user: null
  };

  // BEGIN DATA RELAY HANDLERS. logic within handlers is identical to its counterpart in standard RAMEN. only the binding to store prototype differs.
  AuthStore.prototype.handleUpdateUser = user => {
    this.setState({
      isAuthenticated: true,
      user: user
    });
  };

  AuthStore.prototype.handleSignOut = () => {
    this.setState({
      isAuthenticated: false,
      user: null
    });
  };
  // END DATA RELAY HANDLERS

  // register data relay handlers. same as standard RAMEN, but this block must follow the handler creation + binding to store prototype, or else the handlers cannot be found during the call to bindListeners.
  const { _updateUser, _signOut } = this.alt.getActions('AuthActions');
  this.bindListeners({
    handleUpdateUser: _updateUser,
    handleSignOut: _signOut
  });
}

export default AuthStore;
