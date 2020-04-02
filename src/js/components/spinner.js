export default class Spinner {
    /**
     * @param {Object} options
     * @param {HTMLElement} options.el
     */
    constructor(options) {
        this.options = options
        this.spinner = options.el;
    }

    show() {
        this.spinner.classList.add('is-visible')
    }

    hide() {
        this.spinner.classList.remove('is-visible')
    }
}