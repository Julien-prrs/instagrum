export default class {

    static namespace = 'profile'

    constructor() {
        this.input = document.getElementById("profileImgInput")
        this.submitForm()
    }

    submitForm() {
        this.input.addEventListener('change', () => {
            document.getElementById("formProfileImg").submit();
        })
    }

}