import { ServerConnection } from '@jupyterlab/services';

interface ITokens {
  authenticated: boolean;
  Authorization: null | string;
  'X-XSRFToken': null | string;
}

function getCookie(name: string): string | undefined {
  // From http://www.tornadoweb.org/en/stable/guide/security.html
  const matches = document.cookie.match('\\b' + name + '=([^;]*)\\b');
  return matches?.[1];
}

export function requestToken(): ITokens {
  const token: ITokens = {
    authenticated: false,
    Authorization: null,
    'X-XSRFToken': null
  };
  const settings = ServerConnection.makeSettings();
  if (settings.token) {
    token.authenticated = true;
    token['Authorization'] = `token ${settings.token}`;
  }
  if (typeof document !== 'undefined' && document?.cookie) {
    const xsrfToken = getCookie('_xsrf');
    if (xsrfToken !== undefined) {
      token.authenticated = true;
      token['X-XSRFToken'] = xsrfToken;
    }
  }
  return token;
}
