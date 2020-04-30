import Spinner from '../components/spinner'

export default class {

    static namespace = 'home'

    constructor() {
        this.isPending = false;
        this.feed = document.querySelector('.js-feed');
        this.spinner = new Spinner({ el: document.querySelector('.js-spinner') })

        // Events
        window.addEventListener('scroll', this.handleScroll.bind(this));
    }

    handleScroll(e) {
        const bounding = document.body.getBoundingClientRect();
        const _self = this;
        
        if ((bounding.bottom - window.innerHeight) <= 100 && !this.isPending) {
            let xhr = new XMLHttpRequest();
            let cards = document.querySelectorAll('.card')

            _self.isPending = true;
            _self.spinner.show();

            xhr.open('GET', `${APP.API_URL}/feed?offset=${cards.length}`)
            xhr.onloadend = function() {
                const data = JSON.parse(xhr.response);

                _self.isPending = data.length > 0 ? false : true;
                _self.spinner.hide();

                _self.appendFeedItems(data);
            }
            xhr.send();
        }
    }

    appendFeedItems(items) {
        if (items.length > 0) {
            this.feed.insertAdjacentHTML('beforeend', items.map(item => `
                <div style="padding: 10px;">
                    <div class="card" style="margin: 0;">
                        <a href="/post/${ item.image_name }" style="display: block; height:500px;" class="card-image">
                            <img src="/file/${ item.image_name }" style="width: 100%; height: 100%; object-fit: cover;">
                        </a>
                        <div class="card-content">
                            <div class="row" style="margin-bottom: 0;">
                                <span style="cursor: pointer; margin-right: 15px;"><i class="material-icons left" style="margin-right: 5px">favorite_border</i>54</span>
                                <span style="cursor: pointer; margin-right: 15px;"><i class="material-icons left" style="margin-right: 5px">chat_bubble_outline</i>2</span>
                            </div>
                        </div>
                    </div>
                </div>
            `));
        }
    }
}