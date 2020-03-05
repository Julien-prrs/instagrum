export default class {

    static namespace = 'search'

    constructor() {
        this.input = document.querySelector('.js-search-input');
        this.resultsContainer = document.querySelector('.js-search-results');

        this.initSearch();
    }

    initSearch() {
        this.input.addEventListener('input', () => {
            const value = this.input.value;
            (value.length >= 3) ? this.findUser(value) : this.resultsContainer.innerHTML = '';
        })
    }

    findUser(value) {
        let xhr = new XMLHttpRequest();

        this.resultsContainer.innerHTML = "";
        this.resultsContainer.classList.add('is-loading');

        xhr.open('GET', `${window.location.href}?q=${value}`)
        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 400) {
                const data = JSON.parse(xhr.response);
                let html = data.map(user => `
                    <a href="/user/${user.username}" class="card-user">
                        <div class="card-user__pp">
                            <img src="/file/${user.profile_image}">
                        </div>
                        <div class="card-user__meta">
                            <h5>${user.firstname} ${user.lastname}</h5>
                            <span>${user.username}</span>
                        </div>
                    </a>
                `);

                if (html.length < 1) {
                    html = '<p class="no-result">Aucun résultat</p>'
                }

                this.resultsContainer.classList.remove('is-loading');
                this.resultsContainer.innerHTML = html;
            }
        }
        xhr.send();
    }
}