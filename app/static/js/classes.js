class files {
    constructor() {
        this.filesData = {};
        this.files_size = 0;
        this.files_length = 0;
    }
    length() {
        return this.files_length;
    }
    size() {
        return this.files_size;
    }
    getall() {
        return this.filesData;
    }
    get(filename) {
        return this.filesData[filename];
    }
    add(filename, data) {
        this.filesData[filename] = data;
        this.files_size += data.size;
        this.files_length += 1;
    }
    remove(filename) {
        this.files_size -= this.filesData[filename].size;
        this.files_length -= 1;
        delete this.filesData[filename];
    }
    empty() {
        return this.files_length == 0;
    }
    clear() {
        this.filesData = {};
        this.files_size = 0;
        this.files_length = 0;
    }
}