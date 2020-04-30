export default class {

    static namespace = 'profile'

    constructor() {
        this._followHandler = this.follow.bind(this);
        this._unfollowHandler = this.unfollow.bind(this);

        this.profilePictureManager();
        this.events();
    }

    profilePictureManager() {
        const form = document.getElementById("formProfileImg");
        const input = document.getElementById('profileImgInput');

        input.addEventListener('change', () => form.submit())
    }

    follow(e) {
        let xhr = new XMLHttpRequest();
        let el = e.currentTarget;

        el.removeEventListener('click', this._followHandler);
        el.classList.add('is-loading');

        xhr.open('POST', '/follow');
        xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 400) {
                el.classList.remove('is-loading', 'js-action-follow', 'profile__action--follow');
                el.classList.add('js-action-unfollow', 'profile__action--unfollow')
                el.innerHTML = '<i class="material-icons right">check</i> Ne plus suivre';

                this.events();
            };
        }
        xhr.send(JSON.stringify({ user: e.currentTarget.dataset.user }));
    }

    unfollow(e) {
        let xhr = new XMLHttpRequest();
        let el = e.currentTarget;

        el.removeEventListener('click', this._unfollowHandler);
        el.classList.add('is-loading');

        xhr.open('POST', `/unfollow`);
        xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 400) {
                el.classList.remove('is-loading', 'js-action-unfollow', 'profile__action--unfollow');
                el.classList.add('js-action-follow', 'profile__action--follow')
                el.innerHTML = '<i class="material-icons right">add_circle_outline</i> Suivre';

                this.events();
            };
        }
        xhr.send(JSON.stringify({ user: e.currentTarget.dataset.user }));
    }

    events() {
        const btnFollow = document.querySelector('.js-action-follow');
        const btnUnfollow = document.querySelector('.js-action-unfollow');

        btnFollow?.addEventListener('click', this._followHandler);
        btnUnfollow?.addEventListener('click', this._unfollowHandler);
    }
}