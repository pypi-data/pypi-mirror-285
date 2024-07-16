const path = window.location.href;

let accountURL, apiURL;
let apiUserPool = 'qbraid'; // distinguish cognito user pool in server

switch (true) {
  case path.includes('lab.qbraid'):
    accountURL = 'https://account.qbraid.com';
    apiURL = 'https://api.qbraid.com/api';
    apiUserPool = 'qbraid';
    break;
  case path.includes('lab-staging.qbraid'):
  case path.includes('lab-testing.qbraid'):
    accountURL = 'https://account-staging.qbraid.com';
    apiURL = 'https://api-staging-1.qbraid.com/api';
    apiUserPool = 'qbraid';
    break;
  case path.includes('lab.qusteam'):
    accountURL = 'http://account.qusteam.org';
    apiURL = 'https://api.qbraid.com/api';
    apiUserPool = 'qusteam';
    break;
  case path.includes('lab.xanadu.qbraid'):
    accountURL = 'https://account.qbraid.com/auth/login/partner/xanadu';
    apiURL = 'https://api.qbraid.com/api';
    apiUserPool = 'xanadu';
    break;
  default:
    // For local testing, uncomment desired apiURL.
    // Before release, switch back to production URL.
    accountURL = 'https://account.qbraid.com';
    apiURL = 'https://api.qbraid.com/api';
    // apiURL = 'https://api-staging-1.qbraid.com/api';
    // apiURL = 'http://localhost:3001/api';
    apiUserPool = 'qbraid';
    break;
}

export const ACCOUNT_URL = accountURL;
export const API_URL = apiURL;

export const buildHeaders = alt => {
  const headers = { domain: apiUserPool };

  const user = alt.getStore('AuthStore').getState().user;
  const config = alt.getStore('UserStore').getState().config;

  if (config?.email && config?.refreshToken) {
    headers['email'] = config.email;
    headers['refresh-token'] = config.refreshToken;
  } else if (config?.apiKey) {
    headers['api-key'] = config.apiKey;
  } else if (user?.signInUserSession) {
    headers['id-token'] = user.signInUserSession.idToken.jwtToken;
  } else {
    const cookies = Object.fromEntries(
      document.cookie
        .split(';')
        .map(cookie => cookie.split('=').map(c => c.trim()))
    );
    const { EMAIL: email, REFRESH: refreshToken } = cookies;

    if (email && refreshToken) {
      headers['email'] = email;
      headers['refresh-token'] = refreshToken;
    }
  }

  return headers;
};

export default function () {
  this.registerAlt = alt => {
    this.alt = alt;
  };

  this.query = () => {
    if (!this.agent) {
      this.agent = require('superagent-use')(require('superagent'));

      this.agent.use(req => {
        if (req.url[0] === '/') {
          req.url = `${this.alt.apiBaseUrl}${req.url}`;
        }

        const headers = buildHeaders(this.alt);
        Object.assign(req.header, headers);
        return req;
      });
    }

    return this.agent;
  };
}
