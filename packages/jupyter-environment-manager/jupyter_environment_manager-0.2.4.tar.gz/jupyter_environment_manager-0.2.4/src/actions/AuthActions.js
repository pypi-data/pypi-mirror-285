import Auth from '@aws-amplify/auth';

Auth.configure({
  region: 'us-east-1',
  userPoolId: 'us-east-1_7hq9OmpnT',
  userPoolWebClientId: '70fo00fpob1sd133m98k7b0jan',
  authenticationFlowType: 'USER_SRP_AUTH'
});

function AuthActions() {
  this.registerAlt = alt => {
    // hack to provide the alt singleton to function-based action creators
    // (necessitated by ES6 breaking class-based action creators in alt by
    // mandating construction via 'new')
    this.alt = alt;
    this.actions = alt.getActions(this.__proto__.constructor.__proto__.name);
  };

  // BEGIN DATA RELAYS. Data relays are a special case of actions creators which
  // are pure functions used by standard action creators to pass data retrieved
  // from api calls etc to stores. stores bind listeners to data relays exclusively.
  // Data relays are always prefixed with an underscore to easily distinguish them
  // from standard action creators.
  this._updateUser = user => user;

  this._signOut = () => {};
  // END DATA RELAYS

  // BEGIN ACTION CREATORS - besides the dispatch line at the start of each handler,
  // all logic and semantics are identical to their equivalen in standard RAMEN.
  this.getUser = refresh => {
    this.alt.dispatch(this, refresh);

    return new Promise((resolve, _reject) => {
      Auth.currentAuthenticatedUser({ bypassCache: refresh })
        .then(user => {
          this.actions._updateUser(user);
          resolve(user);
        })
        .catch(_err => {
          this.actions._signOut(); // ensure signed-out status propagates
          resolve();
        });
    });
  };
  // END ACTION CREATORS
}

export default AuthActions;
