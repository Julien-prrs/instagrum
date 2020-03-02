import views from './views'

export default class Instagrum {
    constructor(namespace) {
        this.namespace = namespace

        this.initView()
        this.ready()
    }

    initView() {
        document.body.classList.add(`is--${this.namespace}`)
        views.map(view => view.namespace === this.namespace ? new view() : null)
    }

    ready() {

        // Global code here ...

    }
}