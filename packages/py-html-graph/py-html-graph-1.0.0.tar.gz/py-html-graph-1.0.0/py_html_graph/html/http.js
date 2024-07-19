const MAX_SIZE = 256 * 1024;
const FLUSH_TIMEOUT = 5;

class BatchHttpManager {
    constructor() {
        this.max_size = MAX_SIZE;
        this.flush_timeout = FLUSH_TIMEOUT;
        this.requests = [];
        this.current_size = 0;
        this.oldest_request_time = 0;
        // 每次 flush 之后都设置成 0, 如果 add 的时候是 0, 则设置为当前时间, 否则不动
        setTimeout(() => this._check_auto_flush(), 1);
    }

    add(url, onload, estimated_size) {
        if (this.oldest_request_time === 0) {
            this.oldest_request_time = new Date().getTime();
        }
        this.requests.push([url, onload]);
        this.current_size += estimated_size;
        if (this.current_size >= this.max_size) {
            this.flush();
        }
    }

    _check_auto_flush() {
        if (this.oldest_request_time !== 0 && new Date().getTime() - this.oldest_request_time >= this.flush_timeout) {
            this.flush();
        }
        setTimeout(() => this._check_auto_flush(), 1);
    }

    flush() {
        if (this.oldest_request_time === 0) {
            return;
        }
        var urls = [];
        var onloads = [];
        for (var i = 0; i < this.requests.length; i++) {
            urls.push(this.requests[i][0]);
            onloads.push(this.requests[i][1]);
        }
        var url = BASE_URL + '/batch/' + stringToHex(JSON.stringify(urls));
        var request = new XMLHttpRequest();
        request.open('GET', url, true);
        request.timeout = 500; //just to prevent last too long
        request.responseType = 'arraybuffer';
        request.onload = () => {
            // console.log('batch request success');
            if (request.status !== 200) {
                return;
            }
            var parts_length = request.getResponseHeader('Parts-Length');
            parts_length = JSON.parse(hexToString(parts_length));
            var current_start = 0;
            for (var i = 0; i < urls.length; i++) {
                var part = request.response.slice(current_start, current_start + parts_length[i]);
                onloads[i]({ status: 200, response: part });
                current_start += parts_length[i];
            }
            // console.log('batch request finished');
        }
        request.send();
        this.oldest_request_time = 0;
        this.requests = [];
        this.current_size = 0;
    }
};

var request_manager = new BatchHttpManager();
