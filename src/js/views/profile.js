export default class {

    static namespace = 'profile'

    constructor() {
        this.profilePictureManager();
    }

    profilePictureManager() {
        const form = document.getElementById("formProfileImg");
        const input = document.getElementById('profileImgInput');

        input.addEventListener('change', () => form.submit())
    }
}