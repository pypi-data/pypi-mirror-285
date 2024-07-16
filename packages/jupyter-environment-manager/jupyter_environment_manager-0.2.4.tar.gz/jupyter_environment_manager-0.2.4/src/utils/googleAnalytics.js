/* eslint-disable @typescript-eslint/explicit-module-boundary-types */
import Cookies from 'universal-cookie';

const cookies = new Cookies();

const sendRGAEvent = (label, action) => {
  const gtagId = cookies.get('GTAGID');
  const actionSnakeCase = action.toLowerCase().replace(' ', '_');
  const data = {
    event: actionSnakeCase, // Adhere to snake_case convention
    category: 'lab',
    action: action,
    label: label,
    nonInteraction: true
  };
  if (gtagId) {
    data.userId = gtagId;
  }
  window.dataLayer.push(data);
};

export default sendRGAEvent;
