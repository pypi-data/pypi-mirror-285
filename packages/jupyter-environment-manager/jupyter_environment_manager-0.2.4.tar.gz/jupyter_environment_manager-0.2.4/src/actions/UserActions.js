function UserActions() {
  this.registerAlt = alt => {
    // hack to provide the alt singleton to function-based action creators
    // (necessitated by ES6 breaking class-based action creators in alt by
    // mandating construction via 'new')
    this.alt = alt;
    this.actions = alt.getActions(this.__proto__.constructor.__proto__.name);
  };

  // BEGIN DATA RELAYS. data relays are a special case of actions creators which
  // are pure functions used by standard action creators to pass data retrieved
  // from api calls etc to stores. stores bind listeners to data relays exclusively.
  // Data relays are always prefixed with an underscore to easily distinguish them
  // from standard action creators.
  this._updateUser = user => user;
  this._updateConfig = config => config;
  this._updateIsMount = isMount => isMount;
  // END DATA RELAYS

  // BEGIN ACTION CREATORS - besides the dispatch line at the start of each handler,
  // all logic and semantics are identical to their equivalen in standard RAMEN.
  this.getUser = () => {
    this.alt.dispatch(this);

    return new Promise((resolve, _reject) => {
      this.alt
        .getActions('ApiActions')
        .query()
        .get('/identity')
        .end((err, res) => {
          if (err) {
            this.actions._updateUser(null);
            resolve(null);
          } else {
            this.actions._updateUser(res.body);
            resolve(res.body);
          }
        });
    });
  };

  this.getLocalConfig = () => {
    // load credentials from ~/.qbraid/qbraidrc if present
    this.alt.dispatch(this);

    return new Promise((resolve, _reject) => {
      this.alt
        .getActions('JupyterApiActions')
        .query('local-config', { method: 'GET' })
        .then(data => {
          if (!data) {
            this.actions._updateConfig(null);
            resolve(null);
          } else {
            this.actions._updateConfig(data);
            resolve(data);
          }
        })
        .catch(err => {
          console.log(err);
          this.actions._updateConfig(null);
          resolve(null);
        });
    });
  };

  this.checkFileMount = () => {
    // check if system is mounted
    this.alt.dispatch(this);

    let getTmpFile = new Promise((resolve, _reject) => {
      this.alt
        .getActions('JupyterApiActions')
        .query('local-config', { method: 'POST' })
        .then(data => resolve(data ? data.filename : null))
        .catch(err => {
          console.log(err);
          resolve(null);
        });
    });

    return new Promise((resolve, _reject) => {
      getTmpFile
        .then(filename => {
          if (!filename) {
            this.actions._updateIsMount(false);
            resolve(false);
          } else {
            this.alt
              .getActions('ApiActions')
              .query()
              .get('/lab/is-mounted/' + filename)
              .end((err, res) => {
                if (err) {
                  console.log(err);
                  this.actions._updateIsMount(false);
                  resolve(false);
                } else {
                  // const isMounted = true;
                  const isMounted = res.body?.isMounted;
                  this.actions._updateIsMount(isMounted);
                  resolve(isMounted);
                }
              });
          }
        })
        .catch(err => {
          console.log(err);
          this.actions._updateIsMount(false);
          resolve(false);
        });
    });
  };

  this.verifyUserSession = () => {
    // Dispatches current context to the alt store
    this.alt.dispatch(this);

    return new Promise((resolve, _reject) => {
      try {
        const { user, config } = this.alt.getStore('UserStore').getState();

        const userEmail = user?.email;
        const configEmail = config?.email;

        // Check if both emails exist and do not match
        if (userEmail && configEmail && userEmail !== configEmail) {
          console.log(
            'WARNING: User Mismatch\n\n' +
              "The logged-in email '" +
              configEmail +
              "' does not match the email '" +
              userEmail +
              "' associated with your current session.\n\n" +
              'Please clear your browser cookies and refresh the page, or use a private browsing window to ensure qBraid Lab functions correctly.'
          );
        }

        resolve({
          status: 'Success',
          message: 'User session verification complete.'
        });
      } catch (error) {
        console.error(error); // For debugging
        resolve(null);
      }
    });
  };
  // END ACTION CREATORS
}

export default UserActions;
