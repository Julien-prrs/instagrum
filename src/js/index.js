import "../scss/main.scss";
import Instagrum from './app.js';

const view = document.querySelector('.view');

document.addEventListener('DOMContentLoaded', () => new Instagrum(view.dataset.namespace));